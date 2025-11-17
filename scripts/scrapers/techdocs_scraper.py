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

        # Setup Selenium if requested (for content extraction)
        if self.use_selenium:
            self._setup_selenium()

        # Track discovered products
        self.discovered_products: Dict[str, str] = {}

    def _setup_selenium(self):
        """Setup Selenium with ChromeDriver for JavaScript rendering."""
        try:
            # Try undetected-chromedriver first (better for bot detection)
            try:
                import undetected_chromedriver as uc
                self.logger.info("Setting up Selenium with undetected ChromeDriver...")

                options = uc.ChromeOptions()
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')

                # Headless mode from config
                if self.config.headless:
                    options.add_argument('--headless=new')

                options.add_argument('--window-size=1920,1080')

                # Chrome binary path from config
                if self.config.chrome_binary_path:
                    options.binary_location = self.config.chrome_binary_path

                # Proxy from config
                proxy_url = self.config.get_proxy_config()
                if proxy_url:
                    options.add_argument(f'--proxy-server={proxy_url}')
                    self.logger.info(f"Using proxy: {proxy_url[:50]}...")

                # ChromeDriver path from config
                driver_kwargs = {'options': options}
                if self.config.chromedriver_path:
                    driver_kwargs['driver_executable_path'] = self.config.chromedriver_path

                self.driver = uc.Chrome(**driver_kwargs)
                self.driver.set_page_load_timeout(30)

                self.logger.info("Selenium ready (undetected-chromedriver)")
                return

            except ImportError:
                self.logger.warning("undetected-chromedriver not available, using regular Selenium")

            # Fallback to regular Selenium
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service

            self.logger.info("Setting up regular Selenium ChromeDriver...")

            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

            # Headless mode from config
            if self.config.headless:
                options.add_argument('--headless=new')

            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            # Chrome binary path from config
            if self.config.chrome_binary_path:
                options.binary_location = self.config.chrome_binary_path

            # Proxy from config
            proxy_url = self.config.get_proxy_config()
            if proxy_url:
                options.add_argument(f'--proxy-server={proxy_url}')
                self.logger.info(f"Using proxy: {proxy_url[:50]}...")

            # ChromeDriver service
            service_kwargs = {}
            if self.config.chromedriver_path:
                service_kwargs['executable_path'] = self.config.chromedriver_path

            service = Service(**service_kwargs) if service_kwargs else None

            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(30)

            self.logger.info("Selenium ready (regular ChromeDriver)")

        except Exception as e:
            self.logger.error(f"Failed to setup Selenium: {e}")
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

        # Log stats
        self._analyze_discovered_products(all_urls)
        self.stats['urls_discovered'] = len(all_urls)
        self.logger.info(f"Discovered {len(all_urls)} total URLs from sitemap index")

        return all_urls

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
        Fetch page HTML using requests or Selenium.

        Args:
            url: URL to fetch

        Returns:
            HTML content or None
        """
        try:
            if self.use_selenium:
                self.driver.get(url)

                # Wait for JavaScript to render content
                # TechDocs is a SPA, so we need to wait for the main content to load
                import time
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC

                try:
                    # Wait up to 10 seconds for main content area to be present
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "article"))
                    )
                    # Additional wait for content to fully render
                    time.sleep(2)
                except:
                    # If no article tag, just wait and hope for the best
                    time.sleep(5)

                return self.driver.page_source
            else:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response.text

        except Exception as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            return None

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
        """Cleanup Selenium driver if used."""
        if self.driver:
            try:
                self.driver.quit()
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

    # Override discover_urls if filters specified
    if args.limit or args.product:
        original_discover = scraper.discover_urls

        def filtered_discover():
            urls = original_discover()

            # Filter by product
            if args.product:
                urls = [u for u in urls if f"/{args.product}/" in u.lower()]
                print(f"Filtered to {len(urls)} URLs for product '{args.product}'")

            # Limit
            if args.limit:
                urls = urls[:args.limit]

            return urls

        scraper.discover_urls = filtered_discover

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
