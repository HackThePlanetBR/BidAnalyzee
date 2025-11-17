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
        output_dir: str = "data/knowledge_base/genetec/compliance",
        delay_between_requests: float = 2.0,
        use_selenium: bool = False
    ):
        """
        Initialize Compliance scraper.

        Args:
            output_dir: Directory to save markdown files
            delay_between_requests: Delay in seconds between requests
            use_selenium: Whether to use Selenium (for Cloudflare bypass)
        """
        super().__init__(
            base_url="https://compliance.genetec.com",
            source_name="Genetec Compliance Portal",
            output_dir=output_dir,
            language="en",
            min_confidence=0.7,
            delay_between_requests=delay_between_requests
        )

        self.use_selenium = use_selenium
        self.driver = None

        if use_selenium:
            self._setup_selenium()
        else:
            # HTTP session for requests
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })

    def _setup_selenium(self):
        """Setup Selenium with ChromeDriver (tries undetected first, falls back to regular)."""
        try:
            # Try undetected-chromedriver first (better for Cloudflare)
            try:
                import undetected_chromedriver as uc
                self.logger.info("Setting up Selenium with undetected ChromeDriver...")

                options = uc.ChromeOptions()
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--headless=new')
                options.add_argument('--window-size=1920,1080')

                self.driver = uc.Chrome(options=options)
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
            options.add_argument('--headless=new')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            # Configure proxy if HTTP_PROXY environment variable is set
            import os
            proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
            if proxy:
                options.add_argument(f'--proxy-server={proxy}')
                self.logger.info(f"Using proxy: {proxy[:50]}...")

            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(30)

            self.logger.info("Selenium ready (regular ChromeDriver)")

        except Exception as e:
            self.logger.error(f"Failed to setup Selenium: {e}")
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
        Fetch page HTML using requests or Selenium.

        Args:
            url: URL to fetch

        Returns:
            HTML content or None
        """
        try:
            if self.use_selenium:
                self.driver.get(url)
                # Wait for content to load
                import time
                time.sleep(3)
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
                    'section': section_name
                }
            }

        except Exception as e:
            self.logger.error(f"Error extracting {url}: {e}", exc_info=True)
            return None

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

            # Skip welcome/navigation text
            if self._is_navigation_or_welcome_text(text):
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
                    if li_text and not self._is_navigation_or_welcome_text(li_text):
                        list_items.append(f"- {li_text}")

                if list_items:
                    current_content.extend(list_items)

        # Save last article
        if current_title and current_content:
            articles.append({
                'title': current_title,
                'content': '\n\n'.join(current_content)
            })

        # If no structured articles found, try to extract substantial paragraphs
        if not articles:
            substantial_content = []

            for p in soup.find_all('p'):
                text = p.get_text().strip()
                if len(text) > 50 and not self._is_navigation_or_welcome_text(text):
                    substantial_content.append(text)

            if substantial_content:
                articles.append({
                    'title': 'Content',
                    'content': '\n\n'.join(substantial_content[:10])  # Limit to 10 paragraphs
                })

        return articles

    def _is_navigation_or_welcome_text(self, text: str) -> bool:
        """
        Check if text is navigation or welcome text that should be filtered.

        Args:
            text: Text to check

        Returns:
            True if text should be filtered out
        """
        if not text or len(text.strip()) < 3:
            return True

        # Check for welcome text indicators
        for indicator in self.WELCOME_TEXT_INDICATORS:
            if indicator in text:
                return True

        # Navigation keywords
        nav_keywords = [
            'overview', 'compliance', 'documents', 'product security',
            'reports', 'self-assessments', 'data security', 'app security',
            'esg', 'legal', 'data privacy', 'access control', 'infrastructure',
            'endpoint security', 'network security', 'corporate security', 'policies',
            'get access', 'bulk download', 'view more', 'close', 'share compliance portal',
            'subscribe to updates', 'report issue', 'built on', 'all', 'public', 'private'
        ]

        text_lower = text.lower().strip()

        # Exact match with nav keywords
        if text_lower in nav_keywords:
            return True

        # Very short text that's likely navigation
        if len(text_lower) < 20 and any(keyword in text_lower for keyword in nav_keywords):
            return True

        return False

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
        """Cleanup Selenium driver if used."""
        if self.driver:
            try:
                self.driver.quit()
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
