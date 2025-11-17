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
        output_dir: str = "data/knowledge_base/genetec/techdocs",
        delay_between_requests: float = 1.5
    ):
        """
        Initialize TechDocs scraper.

        Args:
            output_dir: Directory to save markdown files
            delay_between_requests: Delay in seconds between requests
        """
        super().__init__(
            base_url="https://techdocs.genetec.com",
            source_name="Genetec Technical Documentation",
            output_dir=output_dir,
            language="en",
            min_confidence=0.7,
            delay_between_requests=delay_between_requests
        )

        # HTTP session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Track discovered products
        self.discovered_products: Dict[str, str] = {}

    def discover_urls(self) -> List[str]:
        """
        Discover URLs from sitemap.xml.

        Returns:
            List of documentation URLs
        """
        self.logger.info(f"Fetching sitemap: {self.SITEMAP_URL}")

        try:
            response = self.session.get(self.SITEMAP_URL, timeout=30)
            response.raise_for_status()

            # Parse XML
            root = ET.fromstring(response.content)

            # XML namespace
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

            # Extract all <loc> elements
            urls = []

            for url_element in root.findall('.//ns:loc', namespace):
                url = url_element.text

                if url and self._is_valid_doc_url(url):
                    urls.append(url)

            # Remove duplicates and sort
            urls = sorted(list(set(urls)))

            # Log discovered products
            self._analyze_discovered_products(urls)

            self.stats['urls_discovered'] = len(urls)
            self.logger.info(f"Discovered {len(urls)} URLs from sitemap")

            return urls

        except ET.ParseError as e:
            self.logger.error(f"Failed to parse sitemap XML: {e}")
            return []
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch sitemap: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error discovering URLs: {e}", exc_info=True)
            return []

    def _is_valid_doc_url(self, url: str) -> bool:
        """
        Check if URL is a valid documentation page.

        Args:
            url: URL to check

        Returns:
            True if valid documentation URL
        """
        # Filter out non-English content
        # TechDocs doesn't use /en/ path, but may have language in different format
        # For now, accept all since we'll filter by content language later

        # Skip index pages, search pages, etc.
        skip_patterns = [
            '/search',
            '/genindex',
            '/index.html',
            '/404.html'
        ]

        for pattern in skip_patterns:
            if pattern in url.lower():
                return False

        # Must be .html page
        if not url.endswith('.html'):
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
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')

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

        except requests.exceptions.RequestException as e:
            self.logger.error(f"HTTP error for {url}: {e}")
            return None
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
        Extract product name and version from URL.

        URL pattern: https://techdocs.genetec.com/{product}/{version}/...

        Args:
            url: Documentation URL

        Returns:
            Tuple of (product_name, version) or (None, None)

        Example:
            >>> _extract_product_and_version("https://techdocs.genetec.com/securitycenter/5.11/admin/...")
            ("Security Center", "5.11")
        """
        parsed = urlparse(url)
        path_parts = [p for p in parsed.path.split('/') if p]

        if len(path_parts) < 2:
            return None, None

        # First part is typically the product slug
        product_slug = path_parts[0].lower()

        # Second part might be version
        potential_version = path_parts[1] if len(path_parts) > 1 else None

        # Check if it looks like a version number
        version = None
        if potential_version and re.match(r'^\d+\.\d+', potential_version):
            version = potential_version

        # Map product slug to friendly name
        product_name = self.PRODUCT_MAPPINGS.get(product_slug)

        if not product_name:
            # Try to create friendly name from slug
            product_name = product_slug.replace('-', ' ').replace('_', ' ').title()

            # Log unknown product
            if product_slug not in self.discovered_products:
                self.logger.warning(
                    f"Unknown product slug: '{product_slug}' → using '{product_name}'"
                )
                self.discovered_products[product_slug] = product_name

        return product_name, version

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
    print()

    # Create scraper
    scraper = TechDocsScraper(
        output_dir=args.output,
        delay_between_requests=args.delay
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
