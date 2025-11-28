"""
Genetec Compliance Portal Scraper

Scrapes documentation from https://compliance.genetec.com/

Category: Security/Compliance (static)

Note: This site may use Cloudflare protection. If using requests fails,
consider using Selenium with undetected-chromedriver.
"""

import requests
from typing import List, Dict, Any, Optional, Set
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup, Tag
import re

from .base_scraper import BaseScraper
from .config import ScrapersConfig


class ComplianceScraper(BaseScraper):
    """
    Scraper for Genetec Compliance Portal documentation.

    Features:
    - Section-based navigation discovery
    - Filters repetitive welcome text
    - Static category: "Security/Compliance"
    - Source: "Genetec Compliance Portal"
    - Optional Selenium support for Cloudflare bypass
    """

    # Known sections from compliance portal
    KNOWN_SECTIONS = [
        'overview', 'certifications', 'product_features', 'reports',
        'questionnaires', 'data_security', 'application_security',
        'environment_social_governance', 'legal', 'data_privacy',
        'access_control', 'infrastructure', 'endpoint_security',
        'network_security', 'internal_practices', 'policies'
    ]

    # Welcome text patterns to filter out
    WELCOME_TEXT_INDICATORS = [
        "Welcome to the Genetec Compliance Portal",
        "Our commitment to data privacy and security is embedded",
        "We take security seriously and have a dedicated internal security team",
        "This Compliance Portal outlines high-level details",
        "This portal can be used to learn about our information security",
        "If you have any additional questions not answered by this portal",
        "reach out to your sales representative"
    ]

    def __init__(
        self,
        output_dir: Optional[str] = None,
        delay_between_requests: Optional[float] = None,
        use_selenium: Optional[bool] = None,
        config: Optional[ScrapersConfig] = None
    ):
        """
        Initialize Compliance scraper.

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
            base_url="https://compliance.genetec.com",
            source_name="Genetec Compliance Portal",
            output_dir=_output_dir,
            language="en",
            min_confidence=0.7,
            delay_between_requests=_delay
        )

        self.use_selenium = _use_selenium
        self.browser = None
        self.playwright = None

        if self.use_selenium:
            self._setup_playwright()
        else:
            # HTTP session for requests
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })

    def _setup_playwright(self):
        """Setup Playwright for JavaScript rendering with anti-bot detection bypass."""
        try:
            from playwright.sync_api import sync_playwright
            import time

            self.logger.info("Setting up Playwright browser...")

            # Start Playwright
            self.playwright = sync_playwright().start()

            # Launch browser with anti-detection configurations
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
                launch_kwargs['proxy'] = {
                    'server': proxy_url
                }
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
        Discover URLs by building section URLs.

        Returns:
            List of section URLs to scrape
        """
        self.logger.info("Building section URLs...")

        # Try to discover sections dynamically
        discovered_sections = self._discover_sections_dynamically()

        if discovered_sections:
            self.logger.info(f"Discovered {len(discovered_sections)} sections dynamically")
            sections = discovered_sections
        else:
            self.logger.info(f"Using {len(self.KNOWN_SECTIONS)} known sections")
            sections = self.KNOWN_SECTIONS

        # Build URLs for each section
        urls = []
        for section in sections:
            url = f"{self.base_url}/?itemName={section}"
            urls.append(url)

        self.stats['urls_discovered'] = len(urls)
        return urls

    def _discover_sections_dynamically(self) -> List[str]:
        """
        Try to discover sections by scraping the main page.

        Returns:
            List of section names, or empty list if failed
        """
        try:
            html = self._fetch_page(self.base_url)
            if not html:
                return []

            soup = BeautifulSoup(html, 'html.parser')

            # Find all links with ?itemName= parameter
            sections = set()

            for link in soup.find_all('a', href=True):
                href = link['href']

                if '?itemName=' in href:
                    # Parse URL
                    parsed = urlparse(href)
                    params = parse_qs(parsed.query)

                    if 'itemName' in params:
                        section_name = params['itemName'][0]
                        sections.add(section_name)

            return sorted(list(sections))

        except Exception as e:
            self.logger.warning(f"Failed to discover sections dynamically: {e}")
            return []

    def _fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch page HTML using requests or Playwright with Accessibility API.

        Args:
            url: URL to fetch

        Returns:
            HTML content or None
        """
        try:
            if self.use_selenium and hasattr(self, 'page'):
                import time

                # Navigate to URL
                self.page.goto(url, wait_until='domcontentloaded', timeout=60000)

                # Wait for Cloudflare challenge to complete
                self.logger.info("Waiting for Cloudflare challenge...")
                time.sleep(8)  # Increased wait time for challenge

                # Check if still on challenge page
                page_text = self.page.content()
                if 'cloudflare' in page_text.lower() or 'verify you are human' in page_text.lower():
                    self.logger.warning("Cloudflare challenge still active, waiting longer...")
                    time.sleep(10)  # Additional wait

                # Extract content using Playwright Accessibility API
                try:
                    self.logger.info("Extracting content using Playwright Accessibility API...")

                    # Get accessibility snapshot (contains all rendered text)
                    snapshot = self.page.accessibility.snapshot()

                    if snapshot:
                        # Convert accessibility tree to HTML-like structure
                        html_content = self._accessibility_to_html(snapshot)

                        if len(html_content) > 0:
                            self.logger.info(f"Successfully extracted {len(html_content)} chars from accessibility tree")
                            # Wrap in HTML structure for BeautifulSoup parsing
                            return f"<html><head><title>Compliance</title></head><body><main><div>{html_content}</div></main></body></html>"
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

    def _accessibility_to_html(self, node: dict, depth: int = 0) -> str:
        """
        Convert Playwright accessibility tree to HTML-like format.

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

        # Skip UI text patterns
        skip_text_patterns = [
            'Confirme que você é humano', 'Confirm that you are human',
            'Rate this content', 'Search in document', 'Copy link',
            'Sign In', 'Downloads', 'Table of contents',
            'Was this topic helpful?', 'Connect with us',
            '© 20', 'Genetec Inc.', 'All rights reserved',
            'Privacy', 'Terms', 'Cookies'
        ]

        # If node has text content, extract it
        if name and role not in skip_roles:
            # Check if text should be skipped
            should_skip = False
            for pattern in skip_text_patterns:
                if pattern in name:
                    should_skip = True
                    break

            if not should_skip and len(name.strip()) > 10:
                # Map roles to HTML tags
                if role == 'heading':
                    # Guess heading level (h1-h6) based on depth
                    level = min(depth + 1, 6)
                    html_parts.append(f"<h{level}>{name}</h{level}>\n")
                elif role == 'paragraph':
                    html_parts.append(f"<p>{name}</p>\n")
                elif role in ['listitem', 'list']:
                    html_parts.append(f"<li>{name}</li>\n")
                elif role == 'text':
                    # Plain text - wrap in paragraph
                    html_parts.append(f"<p>{name}</p>\n")
                else:
                    # Generic content
                    html_parts.append(f"<p>{name}</p>\n")

        # Recurse into children
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
            result = result.strip()

        return result

    def extract_content(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract content from a section URL.

        Args:
            url: Section URL to extract

        Returns:
            Dictionary with title, content_html, metadata
        """
        try:
            # Fetch page
            html = self._fetch_page(url)
            if not html:
                return None

            # Parse
            soup = BeautifulSoup(html, 'html.parser')

            # Extract section name from URL
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            section_name = params.get('itemName', ['unknown'])[0]

            # Title from section name
            title = section_name.replace('_', ' ').title()

            # Extract articles from section
            articles = self._extract_section_articles(soup)

            # Find internal links to follow (for sections like "legal" that are mostly links)
            internal_links = self._find_internal_links(soup, url)

            if internal_links:
                self.logger.info(f"Found {len(internal_links)} internal links to follow in {section_name}")

                # Follow each link and extract content
                for link_url, link_text in internal_links[:5]:  # Limit to 5 links max per section
                    self.logger.info(f"  Following link: {link_text} -> {link_url}")

                    try:
                        link_html = self._fetch_page(link_url)
                        if link_html:
                            link_soup = BeautifulSoup(link_html, 'html.parser')
                            link_articles = self._extract_section_articles(link_soup)

                            if link_articles:
                                # Add link articles to main articles list
                                for art in link_articles:
                                    art['title'] = f"{link_text}: {art['title']}"
                                articles.extend(link_articles)
                                self.logger.info(f"    ✓ Extracted {len(link_articles)} articles from link")
                            else:
                                self.logger.debug(f"    No articles found in linked page")
                    except Exception as e:
                        self.logger.warning(f"  Failed to extract from link {link_url}: {e}")
                        continue

            if not articles:
                self.logger.warning(f"No articles found in section: {section_name}")
                return None

            # Combine articles into single content
            # We'll create one document per section with multiple articles
            combined_html = self._combine_articles_html(articles, title)

            return {
                'title': title,
                'content_html': combined_html,
                'metadata': {
                    'section': section_name,
                    'internal_links_followed': len(internal_links) if internal_links else 0
                }
            }

        except Exception as e:
            self.logger.error(f"Error extracting {url}: {e}", exc_info=True)
            return None

    def _find_internal_links(self, soup: BeautifulSoup, current_url: str) -> List[tuple]:
        """
        Find internal links within a section to follow for more content.

        Useful for sections like "legal" and "questionnaires" that are mostly link lists.

        Args:
            soup: BeautifulSoup object of current page (IGNORED - using Playwright DOM instead)
            current_url: Current page URL

        Returns:
            List of (url, link_text) tuples
        """
        internal_links = []

        # If using Playwright, extract links directly from DOM via JavaScript
        if self.use_selenium and hasattr(self, 'page'):
            try:
                # Use JavaScript to get all links with href and text
                links_data = self.page.evaluate("""
                    () => {
                        const links = Array.from(document.querySelectorAll('a[href]'));
                        return links.map(link => ({
                            href: link.href,
                            text: link.textContent.trim()
                        }));
                    }
                """)

                for link_data in links_data:
                    href = link_data['href']
                    text = link_data['text']

                    # Skip empty or very short text
                    if not text or len(text) < 3:
                        continue

                    # Skip obvious navigation links
                    nav_patterns = ['close', 'view more', 'back', 'home', 'share', 'subscribe']
                    if any(nav in text.lower() for nav in nav_patterns):
                        continue

                    # Build full URL
                    full_url = urljoin(self.base_url, href)

                    # Only follow links to same domain
                    if not full_url.startswith(self.base_url):
                        continue

                    # Skip PDFs and external files
                    if full_url.lower().endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip')):
                        self.logger.debug(f"Skipping external file: {text} ({full_url})")
                        continue

                    # Skip if it's the same URL as current
                    if full_url == current_url:
                        continue

                    # Check if this is a compliance.genetec.com internal link with actual content
                    # (not just navigation or modal triggers)
                    if '?itemName=' in full_url or '/documents/' in full_url or '/legal/' in full_url:
                        internal_links.append((full_url, text))
                        self.logger.debug(f"Found internal link: {text} -> {full_url}")

            except Exception as e:
                self.logger.warning(f"Failed to extract links via JavaScript: {e}")
                # Fallback to BeautifulSoup (won't work with accessibility tree, but keep for compatibility)
                pass

        return internal_links

    def _extract_section_articles(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """
        Extract articles from a section page.

        Args:
            soup: BeautifulSoup object

        Returns:
            List of article dictionaries with title and content
        """
        articles = []
        processed_elements: Set[int] = set()

        # Find all heading and paragraph elements
        elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'blockquote'])

        current_title = None
        current_content = []

        for element in elements:
            # Skip if already processed
            if id(element) in processed_elements:
                continue

            text = element.get_text().strip()

            # Skip empty or very short text
            if not text or len(text) < 3:
                continue

            # Skip navigation text (but NOT welcome text - that's real content!)
            if self._is_navigation_text_only(text):
                continue

            processed_elements.add(id(element))

            # If it's a heading, save previous article and start new
            if element.name in ['h1', 'h2', 'h3', 'h4'] and len(text) < 100:
                # Save previous article
                if current_title and current_content:
                    articles.append({
                        'title': current_title,
                        'content': '\n\n'.join(current_content)
                    })

                # Start new article
                current_title = text
                current_content = []

            # If it's content
            elif element.name in ['p', 'blockquote'] and len(text) > 20:
                current_content.append(text)

            # If it's a list
            elif element.name in ['ul', 'ol']:
                list_items = []
                for li in element.find_all('li'):
                    li_text = li.get_text().strip()
                    if li_text and not self._is_navigation_text_only(li_text):
                        list_items.append(f"- {li_text}")

                if list_items:
                    current_content.extend(list_items)

        # Save last article
        if current_title and current_content:
            articles.append({
                'title': current_title,
                'content': '\n\n'.join(current_content)
            })

        # If no structured articles found, extract ALL substantial paragraphs
        # (don't filter out welcome text at this stage - it's real content!)
        if not articles:
            substantial_content = []

            for p in soup.find_all('p'):
                text = p.get_text().strip()
                # Lower threshold to 10 chars (some sections have short but valuable content)
                if len(text) > 10 and not self._is_pure_navigation(text):
                    substantial_content.append(text)

            if substantial_content:
                articles.append({
                    'title': 'Content',
                    'content': '\n\n'.join(substantial_content)  # Keep all paragraphs
                })

        return articles

    def _is_navigation_text_only(self, text: str) -> bool:
        """
        Check if text is ONLY navigation (not content).

        This is stricter than before - only filters pure navigation elements,
        NOT welcome/intro text which is real content.

        Args:
            text: Text to check

        Returns:
            True if text should be filtered out
        """
        if not text or len(text.strip()) < 3:
            return True

        # Navigation keywords (short, single-word commands)
        nav_keywords = [
            'close', 'view more', 'bulk download', 'get access',
            'share compliance portal', 'subscribe to updates',
            'report issue', 'built on', 'all', 'public', 'private'
        ]

        text_lower = text.lower().strip()

        # Exact match with nav keywords
        if text_lower in nav_keywords:
            return True

        # Very short text that's likely navigation (< 15 chars)
        if len(text_lower) < 15 and any(keyword in text_lower for keyword in nav_keywords):
            return True

        return False

    def _is_pure_navigation(self, text: str) -> bool:
        """
        Check if text is pure navigation element (most permissive - almost nothing filtered).

        Only filters obvious UI elements like buttons and links.

        Args:
            text: Text to check

        Returns:
            True if text should be filtered out
        """
        if not text or len(text.strip()) < 10:
            return True

        # Only filter very obvious UI elements
        ui_elements = [
            'close', 'click here', 'learn more', 'read more',
            'view all', 'see more', 'expand', 'collapse'
        ]

        text_lower = text.lower().strip()

        # Exact match only
        return text_lower in ui_elements

    def _is_navigation_or_welcome_text(self, text: str) -> bool:
        """
        DEPRECATED: Use _is_navigation_text_only instead.

        Kept for backwards compatibility but now just calls the new method.
        """
        return self._is_navigation_text_only(text)

    def _combine_articles_html(self, articles: List[Dict[str, str]], section_title: str) -> str:
        """
        Combine multiple articles into a single HTML structure.

        Args:
            articles: List of article dictionaries
            section_title: Section title

        Returns:
            Combined HTML string
        """
        html_parts = [f"<h1>{section_title}</h1>"]

        for article in articles:
            html_parts.append(f"<h2>{article['title']}</h2>")

            # Convert content to HTML paragraphs
            paragraphs = article['content'].split('\n\n')
            for para in paragraphs:
                if para.strip():
                    # Check if it's a list item
                    if para.strip().startswith('-'):
                        # It's a list
                        items = [item.strip('- ').strip() for item in para.split('\n') if item.strip().startswith('-')]
                        html_parts.append("<ul>")
                        for item in items:
                            html_parts.append(f"<li>{item}</li>")
                        html_parts.append("</ul>")
                    else:
                        html_parts.append(f"<p>{para}</p>")

        return '\n'.join(html_parts)

    def get_category(self, url: str, content: Optional[Dict[str, Any]] = None) -> str:
        """
        Get category for Compliance documentation.

        Args:
            url: Source URL
            content: Optional content data

        Returns:
            Always returns "Security/Compliance"
        """
        return "Security/Compliance"

    def __del__(self):
        """Cleanup Playwright browser if used."""
        try:
            if hasattr(self, 'browser') and self.browser:
                self.browser.close()
            if hasattr(self, 'playwright') and self.playwright:
                self.playwright.stop()
        except:
            pass


def main():
    """
    Run Compliance scraper standalone.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Genetec Compliance Portal Scraper")
    parser.add_argument(
        '--output',
        '-o',
        default="data/knowledge_base/genetec/compliance",
        help="Output directory (default: data/knowledge_base/genetec/compliance)"
    )
    parser.add_argument(
        '--delay',
        '-d',
        type=float,
        default=2.0,
        help="Delay between requests in seconds (default: 2.0)"
    )
    parser.add_argument(
        '--selenium',
        action='store_true',
        help="Use Selenium for Cloudflare bypass"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Genetec Compliance Portal Scraper")
    print("=" * 70)
    print(f"Output directory: {args.output}")
    print(f"Delay: {args.delay}s")
    print(f"Using Selenium: {args.selenium}")
    print()

    # Create scraper
    try:
        scraper = ComplianceScraper(
            output_dir=args.output,
            delay_between_requests=args.delay,
            use_selenium=args.selenium
        )

        # Run scraper
        stats = scraper.run()

        # Print summary
        print()
        print("=" * 70)
        print("SCRAPING SUMMARY")
        print("=" * 70)
        print(f"Total sections: {stats['urls_discovered']}")
        print(f"Processed: {stats['urls_processed']}")
        print(f"Extracted: {stats['docs_extracted']}")
        print(f"Skipped (language): {stats['docs_skipped_language']}")
        print(f"Skipped (errors): {stats['docs_skipped_error']}")

        if stats['start_time'] and stats['end_time']:
            duration = (stats['end_time'] - stats['start_time']).total_seconds()
            print(f"Duration: {duration:.1f}s")

        print()
        print(f"Output directory: {args.output}")
        print("=" * 70)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
