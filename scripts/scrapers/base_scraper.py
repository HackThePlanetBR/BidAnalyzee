"""
Base Scraper

Abstract base class for all web scrapers.
Provides common functionality and defines interface for concrete scrapers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
import json
from datetime import datetime
import time

from .utils import (
    generate_frontmatter,
    is_english_content,
    detect_language_from_url,
    HTMLToMarkdownConverter,
    create_safe_filename
)


class BaseScraper(ABC):
    """
    Abstract base class for documentation scrapers.

    Concrete scrapers must implement:
    - discover_urls(): Find all URLs to scrape
    - extract_content(url): Extract content from a single URL
    - get_category(url): Determine category for a URL
    """

    def __init__(
        self,
        base_url: str,
        source_name: str,
        output_dir: str,
        language: str = "en",
        min_confidence: float = 0.7,
        delay_between_requests: float = 1.5
    ):
        """
        Initialize scraper.

        Args:
            base_url: Base URL of the website
            source_name: Name of the documentation source
            output_dir: Directory to save markdown files
            language: Target language code (default: "en")
            min_confidence: Minimum confidence for language detection
            delay_between_requests: Delay in seconds between HTTP requests
        """
        self.base_url = base_url.rstrip('/')
        self.source_name = source_name
        self.output_dir = Path(output_dir)
        self.language = language
        self.min_confidence = min_confidence
        self.delay_between_requests = delay_between_requests

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Configure logging
        self.logger = self._setup_logging()

        # Statistics
        self.stats = {
            'urls_discovered': 0,
            'urls_processed': 0,
            'docs_extracted': 0,
            'docs_skipped_language': 0,
            'docs_skipped_error': 0,
            'start_time': None,
            'end_time': None
        }

        # HTML to Markdown converter
        self.html_converter = HTMLToMarkdownConverter(base_url=self.base_url)

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for scraper."""
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)

        # File handler
        log_file = self.output_dir / f"{self.__class__.__name__.lower()}.log"
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

        return logger

    @abstractmethod
    def discover_urls(self) -> List[str]:
        """
        Discover all URLs to scrape.

        Returns:
            List of URLs to process

        Note:
            Concrete implementations should:
            - Use sitemap.xml when available
            - Filter for relevant content (e.g., .html files)
            - Remove duplicates
            - Update self.stats['urls_discovered']
        """
        pass

    @abstractmethod
    def extract_content(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract content from a single URL.

        Args:
            url: URL to extract content from

        Returns:
            Dictionary with extracted data:
            {
                'title': str,
                'content_html': str or BeautifulSoup,
                'metadata': dict (optional additional fields)
            }
            Or None if extraction failed

        Note:
            Concrete implementations should:
            - Handle HTTP errors gracefully
            - Extract title from <h1>, <title>, or URL
            - Extract main content (article, main, .content, etc.)
            - Return None on failure
        """
        pass

    @abstractmethod
    def get_category(self, url: str, content: Optional[Dict[str, Any]] = None) -> str:
        """
        Determine category for a URL/content.

        Args:
            url: Source URL
            content: Optional extracted content dictionary

        Returns:
            Category string

        Note:
            Concrete implementations define categorization logic:
            - Static category (e.g., "SCSaaS", "Security/Compliance")
            - Dynamic from URL pattern (e.g., product name in path)
            - From content analysis
        """
        pass

    def validate_language(self, text: str, url: str) -> bool:
        """
        Validate that content is in target language.

        Args:
            text: Content text to validate
            url: Source URL (used for URL pattern detection)

        Returns:
            True if content matches target language
        """
        # Check URL first for language indicators
        url_lang = detect_language_from_url(url)
        if url_lang:
            is_valid = (url_lang == self.language)
            if not is_valid:
                self.logger.debug(f"URL language {url_lang} != target {self.language}")
            return is_valid

        # Check content
        is_english, confidence, method = is_english_content(
            text,
            threshold=self.min_confidence,
            use_url=url
        )

        if self.language == 'en':
            if not is_english:
                self.logger.debug(
                    f"Non-English content detected (confidence: {confidence:.2f}, method: {method})"
                )
            return is_english
        else:
            # For non-English targets, would need additional logic
            self.logger.warning(f"Language validation for '{self.language}' not fully implemented")
            return True

    def convert_to_markdown(
        self,
        content_data: Dict[str, Any],
        url: str
    ) -> Optional[str]:
        """
        Convert extracted content to markdown with frontmatter.

        Args:
            content_data: Dictionary from extract_content()
            url: Source URL

        Returns:
            Complete markdown string with frontmatter, or None on failure
        """
        try:
            title = content_data.get('title', 'Untitled')
            content_html = content_data.get('content_html')
            metadata = content_data.get('metadata', {})

            if not content_html:
                self.logger.error(f"No content_html in content_data for {url}")
                return None

            # Convert HTML to Markdown
            markdown_body = self.html_converter.convert(content_html, title=None)

            # Validate language
            if not self.validate_language(markdown_body, url):
                self.logger.info(f"Skipping non-{self.language} content: {url}")
                self.stats['docs_skipped_language'] += 1
                return None

            # Get category
            category = self.get_category(url, content_data)

            # Generate frontmatter
            frontmatter = generate_frontmatter(
                title=title,
                url=url,
                source=self.source_name,
                category=category,
                language=self.language,
                product=metadata.get('product'),
                version=metadata.get('version'),
                tags=metadata.get('tags')
            )

            # Combine frontmatter and content
            full_markdown = frontmatter + "\n" + markdown_body

            return full_markdown

        except Exception as e:
            self.logger.error(f"Error converting to markdown for {url}: {e}", exc_info=True)
            return None

    def save_document(
        self,
        content_data: Dict[str, Any],
        url: str,
        markdown_content: str
    ) -> Optional[Path]:
        """
        Save markdown document to file.

        Args:
            content_data: Extracted content dictionary
            url: Source URL
            markdown_content: Complete markdown with frontmatter

        Returns:
            Path to saved file, or None on failure
        """
        try:
            title = content_data.get('title', 'Untitled')

            # Create filename
            filename = create_safe_filename(
                title=title,
                url=url,
                max_length=100,
                add_hash=True,
                extension='.md'
            )

            # Full path
            filepath = self.output_dir / filename

            # Ensure unique (shouldn't be necessary with hash, but just in case)
            counter = 1
            original_filepath = filepath
            while filepath.exists():
                stem = original_filepath.stem
                filepath = self.output_dir / f"{stem}_{counter}.md"
                counter += 1

            # Write file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            self.logger.info(f"Saved: {filepath.name}")
            return filepath

        except Exception as e:
            self.logger.error(f"Error saving document for {url}: {e}", exc_info=True)
            return None

    def process_url(self, url: str) -> bool:
        """
        Process a single URL: extract, convert, validate, save.

        Args:
            url: URL to process

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.debug(f"Processing: {url}")

            # Extract content
            content_data = self.extract_content(url)

            if not content_data:
                self.logger.warning(f"Failed to extract content from: {url}")
                self.stats['docs_skipped_error'] += 1
                return False

            # Convert to markdown
            markdown_content = self.convert_to_markdown(content_data, url)

            if not markdown_content:
                # Language validation failed or conversion error
                return False

            # Save document
            filepath = self.save_document(content_data, url, markdown_content)

            if filepath:
                self.stats['docs_extracted'] += 1
                return True
            else:
                self.stats['docs_skipped_error'] += 1
                return False

        except Exception as e:
            self.logger.error(f"Error processing {url}: {e}", exc_info=True)
            self.stats['docs_skipped_error'] += 1
            return False

    def run(self) -> Dict[str, Any]:
        """
        Run the complete scraping process.

        Returns:
            Statistics dictionary

        Process:
        1. Discover URLs
        2. Process each URL (with delay)
        3. Generate statistics
        4. Save statistics to JSON
        """
        self.logger.info(f"Starting {self.__class__.__name__}")
        self.logger.info(f"Base URL: {self.base_url}")
        self.logger.info(f"Output directory: {self.output_dir}")

        self.stats['start_time'] = datetime.now()

        # Discover URLs
        self.logger.info("Phase 1: Discovering URLs...")
        urls = self.discover_urls()

        if not urls:
            self.logger.error("No URLs discovered. Aborting.")
            return self.stats

        self.logger.info(f"Discovered {len(urls)} URLs")

        # Process URLs
        self.logger.info("Phase 2: Processing URLs...")

        for i, url in enumerate(urls, start=1):
            self.logger.info(f"[{i}/{len(urls)}] Processing: {url[:80]}...")

            success = self.process_url(url)

            self.stats['urls_processed'] += 1

            # Progress update
            if i % 10 == 0:
                self._log_progress()

            # Delay between requests (except last one)
            if i < len(urls):
                time.sleep(self.delay_between_requests)

        # Finalize
        self.stats['end_time'] = datetime.now()
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()

        # Save statistics
        self._save_statistics()

        # Final report
        self.logger.info("=" * 60)
        self.logger.info("SCRAPING COMPLETE")
        self.logger.info("=" * 60)
        self.logger.info(f"URLs discovered: {self.stats['urls_discovered']}")
        self.logger.info(f"URLs processed: {self.stats['urls_processed']}")
        self.logger.info(f"Documents extracted: {self.stats['docs_extracted']}")
        self.logger.info(f"Skipped (language): {self.stats['docs_skipped_language']}")
        self.logger.info(f"Skipped (errors): {self.stats['docs_skipped_error']}")
        self.logger.info(f"Duration: {duration:.1f}s")
        self.logger.info(f"Output: {self.output_dir}")

        return self.stats

    def _log_progress(self):
        """Log current progress."""
        self.logger.info(
            f"Progress: {self.stats['docs_extracted']} extracted, "
            f"{self.stats['docs_skipped_language']} skipped (language), "
            f"{self.stats['docs_skipped_error']} errors"
        )

    def _save_statistics(self):
        """Save statistics to JSON file."""
        stats_file = self.output_dir / 'scraping_stats.json'

        # Convert datetimes to strings
        stats_json = {}
        for key, value in self.stats.items():
            if isinstance(value, datetime):
                stats_json[key] = value.isoformat()
            else:
                stats_json[key] = value

        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats_json, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Statistics saved to: {stats_file}")
