"""
Genetec Technical Documentation Scraper

Scrapes documentation from https://techdocs.genetec.com/
using the official sitemap.xml for comprehensive URL discovery.

Category: Dynamic (extracted from product name in URL)
"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re
import time

from .base_scraper import BaseScraper
from .config import ScrapersConfig


class TechDocsScraper(BaseScraper):
    """
    Scraper for Genetec Technical Documentation.

    Features:
    - Uses official sitemap.xml for URL discovery
    - Dynamic category extraction from product name in URL
    - Version tracking from URL
    - Filters for English-only content
    - Source: "Genetec Technical Documentation"
    """

    SITEMAP_URL = "https://techdocs.genetec.com/sitemap.xml"

    # Product name mappings (URL slug → friendly name)
    PRODUCT_MAPPINGS = {
        'securitycenter': 'Security Center',
        'synergis': 'Synergis',
        'autovu': 'AutoVu',
        'clearid': 'Genetec ClearID',
        'streamvault': 'Genetec StreamVault',
        'sipdesk': 'Genetec SIP Desk',
        'missioncontrol': 'Genetec Mission Control',
        'kiwivision': 'KiwiVision',
        'plan manager': 'Plan Manager',
        'stratocast': 'Stratocast',
        'genetec-server': 'Genetec Server',
        'omnicast': 'Omnicast',
        'synergis-cloud-link': 'Synergis Cloud Link'
    }

    def __init__(
        self,
        output_dir: Optional[str] = None,
        delay_between_requests: Optional[float] = None,
        use_selenium: Optional[bool] = None,
        config: Optional[ScrapersConfig] = None
    ):
        """
        Initialize TechDocs scraper.

        Args:
            output_dir: Directory to save markdown files (overrides config)
            delay_between_requests: Delay in seconds between requests (overrides config)
            use_selenium: Whether to use Selenium (overrides config)
            config: ScrapersConfig instance (if None, loads from environment)
        """
        # Load config if not provided
        if config is None:
            from .config import get_config
            config = get_config()

        self.config = config

        # Use provided values or fall back to config
        _output_dir = output_dir or config.output_dir
        _delay = delay_between_requests if delay_between_requests is not None else config.delay_between_requests
        _use_selenium = use_selenium if use_selenium is not None else config.use_selenium

        super().__init__(
            base_url="https://techdocs.genetec.com",
            source_name="Genetec Technical Documentation",
            output_dir=_output_dir,
            language="en",
            min_confidence=0.7,
            delay_between_requests=_delay
        )

        self.use_selenium = _use_selenium
        self.driver = None

        # HTTP session always needed for sitemap discovery
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Setup browser automation if requested (for content extraction)
        self.browser = None
        self.playwright = None
        if self.use_selenium:
            self._setup_playwright()

        # Track discovered products
        self.discovered_products: Dict[str, str] = {}

    def _setup_playwright(self):
        """Setup Playwright for JavaScript rendering with anti-bot detection bypass."""
        try:
            from playwright.sync_api import sync_playwright

            self.logger.info("Setting up Playwright browser...")

            # Start Playwright
            self.playwright = sync_playwright().start()

            # Launch browser with anti-detection configurations
            # Use chromium as it has best anti-bot bypass capabilities
            launch_kwargs = {
                'headless': self.config.headless,
                'args': [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                ]
            }

            # Chrome binary path from config
            if self.config.chrome_binary_path:
                launch_kwargs['executable_path'] = self.config.chrome_binary_path

            # Proxy from config
            proxy_url = self.config.get_proxy_config()
            if proxy_url:
                # Parse proxy URL for Playwright format
                from urllib.parse import urlparse
                parsed_proxy = urlparse(proxy_url)
                launch_kwargs['proxy'] = {
                    'server': f'{parsed_proxy.scheme}://{parsed_proxy.hostname}:{parsed_proxy.port}'
                }
                if parsed_proxy.username:
                    launch_kwargs['proxy']['username'] = parsed_proxy.username
                if parsed_proxy.password:
                    launch_kwargs['proxy']['password'] = parsed_proxy.password
                self.logger.info(f"Using proxy: {proxy_url[:50]}...")

            self.browser = self.playwright.chromium.launch(**launch_kwargs)

            # Create a new context with realistic viewport and user agent
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            # Create a new page
            self.page = self.context.new_page()

            self.logger.info("Playwright ready (Chromium with anti-bot bypass)")

        except ImportError as e:
            self.logger.error("Playwright not installed. Install with: pip install playwright && playwright install chromium")
            raise
        except Exception as e:
            self.logger.error(f"Failed to setup Playwright: {e}")
            raise

    def discover_urls(self) -> List[str]:
        """
        Discover URLs from sitemap.xml (handles sitemap index).

        Returns:
            List of English documentation URLs
        """
        self.logger.info(f"Fetching sitemap: {self.SITEMAP_URL}")

        try:
            response = self.session.get(self.SITEMAP_URL, timeout=30)
            response.raise_for_status()

            # Parse XML
            root = ET.fromstring(response.content)

            # XML namespace
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

            # Check if this is a sitemap index
            if root.tag.endswith('sitemapindex'):
                self.logger.info("Detected sitemap index, fetching sub-sitemaps...")
                return self._discover_from_sitemap_index(root, namespace)
            else:
                # Direct sitemap with URLs
                return self._extract_urls_from_sitemap(root, namespace)

        except ET.ParseError as e:
            self.logger.error(f"Failed to parse sitemap XML: {e}")
            return []
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch sitemap: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error discovering URLs: {e}", exc_info=True)
            return []

    def _discover_from_sitemap_index(self, root: ET.Element, namespace: dict) -> List[str]:
        """
        Discover URLs from a sitemap index (sitemap of sitemaps).

        Args:
            root: XML root element
            namespace: XML namespace dict

        Returns:
            List of URLs from all sub-sitemaps
        """
        all_urls = []

        # Get all sub-sitemap URLs
        sitemap_urls = []
        for sitemap_element in root.findall('.//ns:sitemap/ns:loc', namespace):
            sitemap_url = sitemap_element.text
            if sitemap_url:
                sitemap_urls.append(sitemap_url)

        self.logger.info(f"Found {len(sitemap_urls)} sub-sitemaps")

        # Fetch each sub-sitemap (focus on structured content)
        for sitemap_url in sitemap_urls:
            # Prioritize structured content
            if 'structured' in sitemap_url or 'pages' in sitemap_url:
                self.logger.info(f"Fetching sub-sitemap: {sitemap_url}")

                try:
                    response = self.session.get(sitemap_url, timeout=30)
                    response.raise_for_status()

                    sub_root = ET.fromstring(response.content)
                    urls = self._extract_urls_from_sitemap(sub_root, namespace)
                    all_urls.extend(urls)

                except Exception as e:
                    self.logger.warning(f"Failed to fetch sub-sitemap {sitemap_url}: {e}")

        # Remove duplicates and sort
        all_urls = sorted(list(set(all_urls)))

        # Filter to keep only latest versions
        all_urls = self._filter_latest_versions(all_urls)

        # Store base URLs for TOC expansion later (when Playwright is ready)
        self.base_urls = all_urls.copy()

        # Log stats
        self._analyze_discovered_products(all_urls)
        self.logger.info(f"Discovered {len(all_urls)} base guide URLs (latest versions only)")

        # If Selenium is enabled, automatically expand to include all sub-pages
        if self.use_selenium and hasattr(self, 'page'):
            self.logger.info("\nAutomatically expanding base guides to include all sub-pages...")
            expanded_urls = self.expand_to_subpages(all_urls)
            self.stats['urls_discovered'] = len(expanded_urls)
            return expanded_urls
        else:
            self.stats['urls_discovered'] = len(all_urls)
            self.logger.info("Note: Selenium not enabled - returning base URLs only (without sub-pages)")
            return all_urls

    def expand_to_subpages(self, base_urls: List[str] = None, limit: int = None) -> List[str]:
        """
        Expand base guide URLs to include all sub-pages from Table of Contents.

        This should be called AFTER Playwright is ready (after _setup_playwright).

        Args:
            base_urls: List of base URLs to expand (defaults to self.base_urls)
            limit: Optional limit on number of guides to expand

        Returns:
            Expanded list of ALL URLs (base + all sub-pages)
        """
        if base_urls is None:
            base_urls = getattr(self, 'base_urls', [])

        if not base_urls:
            self.logger.warning("No base URLs to expand")
            return []

        if not self.use_selenium or not hasattr(self, 'page'):
            self.logger.error("Playwright not initialized - cannot expand TOC links")
            return base_urls

        if limit:
            base_urls = base_urls[:limit]

        self.logger.info(f"\n{'='*70}")
        self.logger.info(f"EXPANDING {len(base_urls)} BASE GUIDES TO SUBPAGES")
        self.logger.info(f"{'='*70}\n")

        all_expanded_urls = []
        total_subpages = 0

        for i, base_url in enumerate(base_urls, 1):
            try:
                self.logger.info(f"[{i}/{len(base_urls)}] Expanding: {base_url}")

                # Navigate to base URL
                self.page.goto(base_url, wait_until='domcontentloaded', timeout=60000)

                # Handle cookie consent on EVERY page (modal appears on all pages, not just first)
                import time
                time.sleep(2)
                try:
                    button = self.page.wait_for_selector("button:has-text('Accept all')", timeout=3000, state='visible')
                    if button:
                        button.click()
                        self.logger.info("Clicked cookie consent")
                        time.sleep(2)
                except:
                    pass  # Cookie modal not present or already accepted

                # Extract TOC links
                toc_links = self._extract_toc_links(base_url)

                # Add all links (base + subpages)
                all_expanded_urls.extend(toc_links)
                total_subpages += len(toc_links)

                self.logger.info(f"  → Added {len(toc_links)} URLs")

            except Exception as e:
                self.logger.error(f"Failed to expand {base_url}: {e}")
                # Add base URL anyway
                all_expanded_urls.append(base_url)

        # Remove duplicates
        all_expanded_urls = sorted(list(set(all_expanded_urls)))

        self.logger.info(f"\n{'='*70}")
        self.logger.info(f"EXPANSION COMPLETE")
        self.logger.info(f"{'='*70}")
        self.logger.info(f"Base guides: {len(base_urls)}")
        self.logger.info(f"Total URLs (after expansion): {len(all_expanded_urls)}")
        self.logger.info(f"Average subpages per guide: {total_subpages / len(base_urls):.1f}")
        self.logger.info(f"{'='*70}\n")

        return all_expanded_urls

    def _extract_urls_from_sitemap(self, root: ET.Element, namespace: dict) -> List[str]:
        """
        Extract URLs from a single sitemap.

        Args:
            root: XML root element
            namespace: XML namespace dict

        Returns:
            List of valid documentation URLs
        """
        urls = []

        for url_element in root.findall('.//ns:url/ns:loc', namespace):
            url = url_element.text

            if url and self._is_valid_doc_url(url):
                urls.append(url)

        return urls

    def _is_valid_doc_url(self, url: str) -> bool:
        """
        Check if URL is a valid English documentation page.

        Args:
            url: URL to check

        Returns:
            True if valid English documentation URL
        """
        # IMPORTANT: Filter only English content
        # TechDocs URL format: /r/en-US/Document-Title or /r/LANG/...
        if '/r/en-US/' not in url:
            return False

        # Skip non-documentation pages
        skip_patterns = [
            '/search',
            '/genindex',
            '/index.html',
            '/404.html',
            '/p/'  # Product pages, not documentation
        ]

        for pattern in skip_patterns:
            if pattern in url.lower():
                return False

        return True

    def _filter_latest_versions(self, urls: List[str]) -> List[str]:
        """
        Filter URLs to keep only the latest version of each product/guide.

        Example:
            AMAG-Symmetry-Plugin-Guide-3.1 → Skip (older)
            AMAG-Symmetry-Plugin-Guide-3.3.0 → Keep (newer)

        Args:
            urls: List of all discovered URLs

        Returns:
            Filtered list with only latest versions
        """
        from packaging import version

        # Group URLs by product base (without version)
        product_groups: Dict[str, List[tuple]] = {}

        for url in urls:
            product, ver = self._extract_product_and_version(url)

            if not product:
                # No version found, keep URL as-is
                if None not in product_groups:
                    product_groups[None] = []
                product_groups[None].append((url, None))
                continue

            # Store URL with parsed version for comparison
            if product not in product_groups:
                product_groups[product] = []

            product_groups[product].append((url, ver))

        # Keep only latest version from each group
        filtered_urls = []
        skipped_count = 0

        for product, url_list in product_groups.items():
            if product is None:
                # URLs without versions - keep all
                filtered_urls.extend([url for url, _ in url_list])
                continue

            if len(url_list) == 1:
                # Only one version - keep it
                filtered_urls.append(url_list[0][0])
                continue

            # Multiple versions - find the latest
            latest_url = None
            latest_version = None

            for url, ver in url_list:
                if ver is None:
                    # No version string, keep URL
                    filtered_urls.append(url)
                    continue

                try:
                    parsed_ver = version.parse(ver)

                    if latest_version is None or parsed_ver > latest_version:
                        if latest_url:
                            skipped_count += 1
                        latest_version = parsed_ver
                        latest_url = url
                    else:
                        skipped_count += 1

                except Exception as e:
                    # Can't parse version - keep URL to be safe
                    self.logger.debug(f"Can't parse version '{ver}' for {url}: {e}")
                    filtered_urls.append(url)

            if latest_url:
                filtered_urls.append(latest_url)

        self.logger.info(f"Version filtering: {len(urls)} URLs → {len(filtered_urls)} URLs (skipped {skipped_count} older versions)")

        return sorted(filtered_urls)

    def _analyze_discovered_products(self, urls: List[str]):
        """
        Analyze URLs to discover products and their counts.

        Args:
            urls: List of URLs to analyze
        """
        product_counts: Dict[str, int] = {}

        for url in urls:
            product, version = self._extract_product_and_version(url)

            if product:
                if product not in product_counts:
                    product_counts[product] = 0
                product_counts[product] += 1

        # Log discovered products
        self.logger.info(f"Discovered {len(product_counts)} products:")
        for product, count in sorted(product_counts.items(), key=lambda x: x[1], reverse=True):
            self.logger.info(f"  - {product}: {count} pages")

    def _fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch page HTML using requests or Playwright.

        Args:
            url: URL to fetch

        Returns:
            HTML content or None
        """
        try:
            if self.use_selenium and self.page:
                # Navigate to URL
                self.page.goto(url, wait_until='domcontentloaded', timeout=60000)

                # Wait for initial page load
                time.sleep(2)

                # Handle cookie consent modal (if present)
                try:
                    # Try multiple possible button selectors for "Accept All"
                    accept_button_selectors = [
                        "button:has-text('Accept all')",
                        "button:has-text('Allow all')",
                        "button:has-text('Accept')",
                        "a:has-text('Accept all')",
                        "#onetrust-accept-btn-handler",
                        "button.accept-all",
                        "button.accept",
                    ]

                    cookie_accepted = False
                    for selector in accept_button_selectors:
                        try:
                            button = self.page.wait_for_selector(selector, timeout=3000, state='visible')
                            if button:
                                button.click()
                                self.logger.info(f"Clicked cookie consent: {selector}")

                                # Wait for cookie modal to disappear completely
                                try:
                                    # Wait for OneTrust banner to be hidden
                                    self.page.wait_for_selector('#onetrust-banner-sdk', state='hidden', timeout=5000)
                                    self.logger.info("Cookie modal disappeared")
                                except:
                                    # If banner selector doesn't exist, just wait
                                    time.sleep(3)
                                    self.logger.debug("Cookie modal wait timeout - proceeding")

                                cookie_accepted = True
                                break
                        except:
                            continue

                    if not cookie_accepted:
                        self.logger.debug("No cookie modal found (may have been accepted previously)")

                except Exception as e:
                    self.logger.debug(f"Cookie modal handling: {str(e)[:100]}")

                # TechDocs is a SPA - content loads dynamically after initial page load
                # Wait for network to be idle (content finished loading)
                try:
                    self.page.wait_for_load_state('networkidle', timeout=15000)
                    self.logger.debug("Network idle - content loaded")
                except:
                    self.logger.debug("Network idle timeout - proceeding anyway")

                # Additional wait for JavaScript to render
                time.sleep(3)

                # Scroll to trigger lazy-loaded content
                try:
                    self.page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
                    time.sleep(1)
                    self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(1)
                    self.page.evaluate("window.scrollTo(0, 0)")
                    time.sleep(1)
                except:
                    pass

                # Wait for content indicators (multiple headings = document loaded)
                try:
                    self.page.wait_for_function(
                        "document.querySelectorAll('h1, h2, h3').length > 1",
                        timeout=10000
                    )
                    self.logger.debug("Dynamic content loaded (multiple headings found)")
                except:
                    self.logger.debug("Timeout waiting for headings - TechDocs may use shadow DOM")

                # CRITICAL: TechDocs content is NOT in standard DOM, shadow DOM, or CDP HTML
                # Content is only accessible via the Playwright Accessibility API
                # Wait for page to fully render first
                self.logger.info("Waiting 15 seconds for TechDocs SPA to fully render...")
                time.sleep(15)

                # TechDocs uses a special rendering mechanism where content is exposed via accessibility tree
                # Extract content using Playwright's accessibility snapshot API
                try:
                    self.logger.info("Extracting content using Playwright Accessibility API...")

                    # Get accessibility snapshot (contains all rendered text)
                    snapshot = self.page.accessibility.snapshot()

                    if snapshot:
                        # Convert accessibility tree to HTML-like structure for compatibility
                        html_content = self._accessibility_to_html(snapshot)

                        # Always use accessibility content, even if small (some pages are legitimately short)
                        if len(html_content) > 0:
                            self.logger.info(f"Successfully extracted {len(html_content)} chars from accessibility tree")
                            # Wrap in <div> (for proper text flow) and <main> tag (for _find_main_content())
                            return f"<html><head><title>TechDocs</title></head><body><main><div>{html_content}</div></main></body></html>"
                        else:
                            self.logger.warning("Accessibility extraction returned empty content")
                            return None

                except Exception as e:
                    self.logger.error(f"Accessibility extraction failed: {e}")
                    return None
            else:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response.text

        except Exception as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            return None

    def _extract_toc_links(self, base_url: str) -> List[str]:
        """
        Extract all Table of Contents links from a guide page.

        TechDocs guides have a sidebar with links to all sub-pages.
        This extracts those links so we can scrape each page individually.

        Args:
            base_url: Guide base URL (e.g., /AMAG-Symmetry-Plugin-Guide-3.1)

        Returns:
            List of full URLs to sub-pages
        """
        if not self.use_selenium:
            return []

        try:
            # Get accessibility snapshot
            snapshot = self.page.accessibility.snapshot()
            if not snapshot:
                return []

            # Find all links in the accessibility tree
            links = []

            def find_links(node):
                if isinstance(node, dict):
                    role = node.get('role', '')
                    name = node.get('name', '')

                    # Look for link nodes in TOC area
                    if role == 'link' and name:
                        # Skip navigation/footer links
                        skip_patterns = [
                            'Home', 'Search', 'Sign In', 'Downloads',
                            'Privacy', 'Terms', 'Partners', 'About Us',
                            'Contact', 'Facebook', 'Twitter', 'LinkedIn'
                        ]

                        if not any(pattern in name for pattern in skip_patterns):
                            links.append(name)

                    # Recurse into children
                    for child in node.get('children', []):
                        find_links(child)

            find_links(snapshot)

            # Convert link text to URLs (approximate based on URL patterns)
            # TechDocs uses URL format: /r/en-US/Guide-Name/Topic-Name
            # We need to find actual href values, not just text

            # Better approach: extract from page HTML
            all_links = self.page.query_selector_all('a[href*="/r/en-US/"]')
            toc_urls = set()

            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    if href and base_url.split('/')[-1] in href:
                        # Link belongs to current guide
                        full_url = urljoin(base_url, href)

                        # Skip SSO/login URLs
                        if '/authentication/' in full_url or '/sso/' in full_url:
                            continue

                        toc_urls.add(full_url)
                except:
                    continue

            result = sorted(list(toc_urls))
            self.logger.info(f"Found {len(result)} TOC links for {base_url}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to extract TOC links from {base_url}: {e}")
            return []

    def _should_expand_toc(self, url: str) -> bool:
        """
        Check if this URL is a base guide that should be expanded via TOC.

        Args:
            url: URL to check

        Returns:
            True if this is a base guide URL (not a sub-page)
        """
        # Base URLs don't have a topic path after the version
        # Base: /r/en-US/Guide-Name-3.1
        # Sub:  /r/en-US/Guide-Name-3.1/Topic-Name
        parts = url.rstrip('/').split('/')

        # If URL has more than 5 parts, it's likely a sub-page
        # Format: https://techdocs.genetec.com/r/en-US/Guide-Name-3.1[/Topic]
        return len(parts) == 5

    def extract_content(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract content from a single URL.

        Args:
            url: URL to extract

        Returns:
            Dictionary with title, content_html, metadata
        """
        try:
            # Fetch page
            html = self._fetch_page(url)
            if not html:
                return None

            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')

            # Extract title
            title = self._extract_title(soup, url)

            # Extract main content
            content_element = self._find_main_content(soup)

            if not content_element:
                self.logger.warning(f"No main content found for: {url}")
                return None

            # Extract product and version
            product, version = self._extract_product_and_version(url)

            # Return data
            return {
                'title': title,
                'content_html': content_element,
                'metadata': {
                    'product': product,
                    'version': version
                }
            }

        except Exception as e:
            self.logger.error(f"Error extracting {url}: {e}", exc_info=True)
            return None

    def _accessibility_to_html(self, node: dict, depth: int = 0) -> str:
        """
        Convert Playwright accessibility tree to HTML-like format.

        TechDocs documentation content is only accessible via accessibility API.
        This method reconstructs HTML from the accessibility tree nodes.

        Args:
            node: Accessibility tree node
            depth: Current depth (for filtering)

        Returns:
            HTML string reconstructed from accessibility tree
        """
        html_parts = []

        role = node.get('role', '')
        name = node.get('name', '')
        children = node.get('children', [])

        # Skip unwanted UI elements but still process their children
        skip_roles = {
            'button', 'searchbox', 'navigation', 'link', 'WebArea',
            'banner', 'contentinfo', 'complementary', 'form'
        }

        # Skip UI text patterns (navigation, footers, UI elements)
        skip_text_patterns = [
            'Rate this content', 'Search in document', 'Copy link', 'Print this topic',
            'Sign In', 'Downloads', 'Table of contents', 'Expand', 'Collapse',
            'Language:', 'Home', 'Search site', 'Solutions', 'Resources',
            'Was this topic helpful?', 'Not rated', 'Sign in to get the most out',
            'Connect with us', '© 20', 'Genetec Inc.', 'All rights reserved',
            'Privacy Policy', 'Terms of Use', 'Cookie', 'Partners', 'About Us'
        ]

        # Check if this node should be extracted
        should_extract = False
        if depth > 0:  # Skip root level
            if role == 'heading':
                should_extract = True
            elif role == 'text' and name.strip():
                # Extract text if it's not a UI label
                if not any(pattern in name for pattern in skip_text_patterns):
                    should_extract = True
            elif role == 'paragraph' and name.strip():
                should_extract = True
            elif role == 'listitem' and name.strip():
                should_extract = True

        # Add this node's content if appropriate
        if should_extract:
            if role == 'heading':
                level = node.get('level', 2)
                html_parts.append(f"<h{level}>{name}</h{level}>")
            elif role == 'text':
                # Output text directly - it will be grouped into paragraphs naturally
                if name.strip():
                    html_parts.append(name + " ")
            elif role == 'paragraph':
                html_parts.append(f"<p>{name}</p>")
            elif role == 'listitem':
                html_parts.append(f"<li>{name}</li>")

        # Recursively process children (ALWAYS, even if parent was skipped)
        # This is crucial because documentation text nodes are often nested inside
        # UI elements like 'link', 'button', 'WebArea' that we want to skip
        for child in children:
            child_html = self._accessibility_to_html(child, depth + 1)
            if child_html:
                html_parts.append(child_html)

        result = ''.join(html_parts)

        # Clean up at root level
        if depth == 0 and result:
            import re
            # Remove excessive whitespace
            result = re.sub(r'\n{3,}', '\n\n', result)
            # Remove double spaces
            result = re.sub(r' {2,}', ' ', result)
            # Remove stray year at end (footer artifact)
            result = re.sub(r'\s+20\d{2}\s*$', '', result)
            result = result.strip()

        return result

    def _extract_title(self, soup: BeautifulSoup, url: str) -> str:
        """
        Extract page title.

        Args:
            soup: BeautifulSoup object
            url: Page URL (fallback)

        Returns:
            Page title
        """
        # Strategy 1: Main content <h1>
        main_h1 = soup.select_one('main h1, article h1, .content h1')
        if main_h1:
            return main_h1.get_text().strip()

        # Strategy 2: First <h1>
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()

        # Strategy 3: <title> tag
        title_tag = soup.find('title')
        if title_tag:
            title_text = title_tag.get_text().strip()
            # Remove common suffixes
            title_text = re.sub(r'\s*[-–—]\s*Genetec.*$', '', title_text)
            return title_text.strip()

        # Strategy 4: Extract from URL
        from urllib.parse import urlparse
        path = urlparse(url).path
        # Get last part of path
        parts = [p for p in path.split('/') if p and p != '.html']
        if parts:
            title = parts[-1].replace('.html', '').replace('_', ' ').replace('-', ' ').title()
            return title

        return "Untitled Document"

    def _find_main_content(self, soup: BeautifulSoup):
        """
        Find main content element.

        Args:
            soup: BeautifulSoup object

        Returns:
            Main content element or None
        """
        # Strategy 1: <main> tag
        main = soup.find('main')
        if main:
            return main

        # Strategy 2: <article> tag
        article = soup.find('article')
        if article:
            return article

        # Strategy 3: Common content classes
        for selector in ['.content', '#content', '.main-content', '.document', '.rst-content']:
            element = soup.select_one(selector)
            if element:
                return element

        # Strategy 4: Find div with role="main"
        role_main = soup.find('div', attrs={'role': 'main'})
        if role_main:
            return role_main

        # Strategy 5: <body> as last resort
        return soup.find('body')

    def _extract_product_and_version(self, url: str) -> Tuple[str, Optional[str]]:
        """
        Extract product name and version from URL/document title.

        TechDocs URL format: https://techdocs.genetec.com/r/en-US/Security-Center-Release-Notes-5.12.2.10

        Args:
            url: Documentation URL

        Returns:
            Tuple of (product_name, version) or (None, None)

        Example:
            >>> _extract_product_and_version("https://techdocs.genetec.com/r/en-US/Security-Center-Admin-Guide-5.12")
            ("Security Center", "5.12")
        """
        # Extract document slug from URL
        # Format: /r/en-US/Document-Title-With-Version
        parsed = urlparse(url)
        path_parts = [p for p in parsed.path.split('/') if p]

        if len(path_parts) < 3:
            return None, None

        # Document title is the last part
        doc_title = path_parts[-1]

        # Extract version from title (usually at the end)
        # Pattern: ...version-X.Y.Z or ...X.Y.Z
        version = None
        version_match = re.search(r'(\d+\.\d+(?:\.\d+)?(?:\.\d+)?)$', doc_title)
        if version_match:
            version = version_match.group(1)
            # Remove version from title for product extraction
            doc_title = doc_title[:version_match.start()].rstrip('-')

        # Extract product name from title
        # Common patterns:
        # - Security-Center-...
        # - SynergisTM-...
        # - AutoVuTM-...
        product_name = None

        # Check known products
        for slug, friendly_name in self.PRODUCT_MAPPINGS.items():
            slug_pattern = slug.replace(' ', '-').replace('_', '-').lower()
            if doc_title.lower().startswith(slug_pattern):
                product_name = friendly_name
                break

        # If not found, try to extract first few words as product
        if not product_name:
            # Remove TM suffix if present
            doc_title_clean = doc_title.replace('TM', '').replace('Tm', '')

            # Get first 1-3 words as product name
            words = doc_title_clean.split('-')
            if words:
                # Try 2-word product names first (e.g., "Security Center")
                if len(words) >= 2:
                    potential_product = ' '.join(words[:2])
                    # Check if it's a known product
                    for friendly_name in self.PRODUCT_MAPPINGS.values():
                        if friendly_name.lower() == potential_product.lower():
                            product_name = friendly_name
                            break

                # Fallback to single word
                if not product_name and words:
                    product_name = words[0].replace('-', ' ').title()

            # Log unknown product
            if product_name and product_name not in self.PRODUCT_MAPPINGS.values():
                slug = doc_title.split('-')[0].lower() if '-' in doc_title else doc_title.lower()
                if slug not in self.discovered_products:
                    self.logger.info(
                        f"Discovered product: '{product_name}' from document: {doc_title}"
                    )
                    self.discovered_products[slug] = product_name

        return product_name if product_name else "General", version

    def get_category(self, url: str, content: Optional[Dict[str, Any]] = None) -> str:
        """
        Get category for TechDocs documentation (dynamic from product name).

        Args:
            url: Source URL
            content: Optional content data (contains product in metadata)

        Returns:
            Product name as category
        """
        # Try to get from content metadata first
        if content and 'metadata' in content:
            product = content['metadata'].get('product')
            if product:
                return product

        # Fallback: extract from URL
        product, _ = self._extract_product_and_version(url)

        return product if product else "General"

    def __del__(self):
        """Cleanup Playwright browser if used."""
        try:
            if hasattr(self, 'page') and self.page:
                self.page.close()
            if hasattr(self, 'context') and self.context:
                self.context.close()
            if hasattr(self, 'browser') and self.browser:
                self.browser.close()
            if hasattr(self, 'playwright') and self.playwright:
                self.playwright.stop()
        except:
            pass


def main():
    """
    Run TechDocs scraper standalone.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Genetec Technical Documentation Scraper")
    parser.add_argument(
        '--output',
        '-o',
        default="data/knowledge_base/genetec/techdocs",
        help="Output directory (default: data/knowledge_base/genetec/techdocs)"
    )
    parser.add_argument(
        '--delay',
        '-d',
        type=float,
        default=1.5,
        help="Delay between requests in seconds (default: 1.5)"
    )
    parser.add_argument(
        '--limit',
        '-l',
        type=int,
        default=None,
        help="Limit number of URLs to process (for testing)"
    )
    parser.add_argument(
        '--product',
        '-p',
        default=None,
        help="Filter for specific product (e.g., 'securitycenter', 'autovu')"
    )
    parser.add_argument(
        '--selenium',
        action='store_true',
        help="Use Selenium for JavaScript rendering (required for SPA content)"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Genetec Technical Documentation Scraper")
    print("=" * 70)
    print(f"Output directory: {args.output}")
    print(f"Delay: {args.delay}s")
    if args.limit:
        print(f"Limit: {args.limit} URLs")
    if args.product:
        print(f"Filter product: {args.product}")
    if args.selenium:
        print("Using Selenium: YES (JavaScript rendering enabled)")
    print()

    # Create scraper
    scraper = TechDocsScraper(
        output_dir=args.output,
        delay_between_requests=args.delay,
        use_selenium=args.selenium
    )

    # Override discover_urls to include TOC expansion
    original_discover = scraper.discover_urls

    def discover_and_expand():
        # Get base URLs (with version filtering already applied)
        base_urls = original_discover()

        # Filter by product if specified
        if args.product:
            base_urls = [u for u in base_urls if f"/{args.product}/" in u.lower()]
            print(f"Filtered to {len(base_urls)} base guides for product '{args.product}'")

        # Limit base guides if specified
        if args.limit:
            base_urls = base_urls[:args.limit]
            print(f"Limited to {args.limit} base guides")

        # Expand to include all subpages
        if args.selenium and scraper.use_selenium:
            print("\nExpanding guides to include all sub-pages...")
            expanded_urls = scraper.expand_to_subpages(base_urls)
            return expanded_urls
        else:
            print("Warning: Selenium not enabled - cannot expand TOC links")
            return base_urls

    scraper.discover_urls = discover_and_expand

    # Run scraper
    stats = scraper.run()

    # Print summary
    print()
    print("=" * 70)
    print("SCRAPING SUMMARY")
    print("=" * 70)
    print(f"Total URLs: {stats['urls_discovered']}")
    print(f"Processed: {stats['urls_processed']}")
    print(f"Extracted: {stats['docs_extracted']}")
    print(f"Skipped (language): {stats['docs_skipped_language']}")
    print(f"Skipped (errors): {stats['docs_skipped_error']}")

    if stats['start_time'] and stats['end_time']:
        duration = (stats['end_time'] - stats['start_time']).total_seconds()
        print(f"Duration: {duration:.1f}s")

        if stats['docs_extracted'] > 0:
            avg_time = duration / stats['docs_extracted']
            print(f"Avg time per doc: {avg_time:.2f}s")

    print()
    print(f"Output directory: {args.output}")

    # Print discovered products
    if scraper.discovered_products:
        print("\nUnknown products discovered:")
        for slug, name in scraper.discovered_products.items():
            print(f"  - {slug} → {name}")

    print("=" * 70)


if __name__ == '__main__':
    main()
