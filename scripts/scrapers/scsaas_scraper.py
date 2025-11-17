"""
Security Center SaaS Help Scraper

Scrapes documentation from https://help.securitycentersaas.genetec.cloud/en/
using the official sitemap.xml for comprehensive URL discovery.

Category: SCSaaS (static)
"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import time

from .base_scraper import BaseScraper


class SCSaaSScraper(BaseScraper):
    """
    Scraper for Security Center SaaS Help documentation.

    Features:
    - Uses official sitemap.xml for URL discovery
    - Filters for English-only content (/en/ path)
    - Static category: "SCSaaS"
    - Source: "Security Center SaaS Help"
    """

    SITEMAP_URL = "https://help.securitycentersaas.genetec.cloud/en/sitemap.xml"

    def __init__(
        self,
        output_dir: str = "data/knowledge_base/genetec/scsaas",
        delay_between_requests: float = 1.5
    ):
        """
        Initialize SCSaaS scraper.

        Args:
            output_dir: Directory to save markdown files
            delay_between_requests: Delay in seconds between requests
        """
        super().__init__(
            base_url="https://help.securitycentersaas.genetec.cloud/en/",
            source_name="Security Center SaaS Help",
            output_dir=output_dir,
            language="en",
            min_confidence=0.7,
            delay_between_requests=delay_between_requests
        )

        # HTTP session for efficient connections
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def discover_urls(self) -> List[str]:
        """
        Discover URLs from sitemap.xml.

        Returns:
            List of .html URLs from sitemap
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

                if url:
                    # Filter for English content and HTML pages
                    if '/en/' in url and url.endswith('.html'):
                        urls.append(url)

            # Remove duplicates and sort
            urls = sorted(list(set(urls)))

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

            # Return data
            return {
                'title': title,
                'content_html': content_element,
                'metadata': {}
            }

        except requests.exceptions.RequestException as e:
            self.logger.error(f"HTTP error for {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error extracting {url}: {e}", exc_info=True)
            return None

    def _extract_title(self, soup: BeautifulSoup, url: str) -> str:
        """
        Extract page title using multiple strategies.

        Args:
            soup: BeautifulSoup object
            url: Page URL (fallback)

        Returns:
            Page title
        """
        # Strategy 1: <article> <h1>
        article_h1 = soup.select_one('article h1')
        if article_h1:
            return article_h1.get_text().strip()

        # Strategy 2: First <h1>
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()

        # Strategy 3: <title> tag
        title_tag = soup.find('title')
        if title_tag:
            title_text = title_tag.get_text().strip()
            # Remove site suffix if present
            title_text = title_text.replace(' - Genetec', '').replace(' - Security Center SaaS', '')
            return title_text.strip()

        # Strategy 4: Extract from URL
        from urllib.parse import urlparse
        path = urlparse(url).path
        # Remove .html and /en/ prefix
        path = path.replace('/en/', '').replace('.html', '')
        # Convert path to title
        title = path.replace('/', ' - ').replace('_', ' ').replace('-', ' ').title()
        return title if title else "Untitled Document"

    def _find_main_content(self, soup: BeautifulSoup):
        """
        Find main content element.

        Args:
            soup: BeautifulSoup object

        Returns:
            Main content element or None
        """
        # Strategy 1: <article> tag
        article = soup.find('article')
        if article:
            return article

        # Strategy 2: <main> tag
        main = soup.find('main')
        if main:
            return main

        # Strategy 3: Common content classes/IDs
        for selector in ['.content', '#content', '.main-content', '.article-content', '.page-content']:
            element = soup.select_one(selector)
            if element:
                return element

        # Strategy 4: <body> as last resort
        return soup.find('body')

    def get_category(self, url: str, content: Optional[Dict[str, Any]] = None) -> str:
        """
        Get category for SCSaaS documentation.

        Args:
            url: Source URL
            content: Optional content data (unused)

        Returns:
            Always returns "SCSaaS"
        """
        return "SCSaaS"


def main():
    """
    Run SCSaaS scraper standalone.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Security Center SaaS Help Scraper")
    parser.add_argument(
        '--output',
        '-o',
        default="data/knowledge_base/genetec/scsaas",
        help="Output directory (default: data/knowledge_base/genetec/scsaas)"
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

    args = parser.parse_args()

    print("=" * 70)
    print("Security Center SaaS Help Scraper")
    print("=" * 70)
    print(f"Output directory: {args.output}")
    print(f"Delay: {args.delay}s")
    if args.limit:
        print(f"Limit: {args.limit} URLs")
    print()

    # Create scraper
    scraper = SCSaaSScraper(
        output_dir=args.output,
        delay_between_requests=args.delay
    )

    # Override discover_urls if limit specified
    if args.limit:
        original_discover = scraper.discover_urls

        def limited_discover():
            urls = original_discover()
            return urls[:args.limit]

        scraper.discover_urls = limited_discover

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
    print("=" * 70)


if __name__ == '__main__':
    main()
