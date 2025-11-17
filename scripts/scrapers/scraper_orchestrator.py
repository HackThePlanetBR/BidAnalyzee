"""
Scraper Orchestrator

Unified CLI to run one or more Genetec documentation scrapers.

Usage:
    python -m scripts.scrapers.scraper_orchestrator --sites all
    python -m scripts.scrapers.scraper_orchestrator --sites scsaas,compliance
    python -m scripts.scrapers.scraper_orchestrator --sites techdocs --limit 50
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import json

from .scsaas_scraper import SCSaaSScraper
from .compliance_scraper import ComplianceScraper
from .techdocs_scraper import TechDocsScraper


class ScraperOrchestrator:
    """
    Orchestrates multiple scrapers for Genetec documentation.
    """

    AVAILABLE_SCRAPERS = {
        'scsaas': {
            'class': SCSaaSScraper,
            'name': 'Security Center SaaS Help',
            'url': 'https://help.securitycentersaas.genetec.cloud/en/'
        },
        'compliance': {
            'class': ComplianceScraper,
            'name': 'Genetec Compliance Portal',
            'url': 'https://compliance.genetec.com/'
        },
        'techdocs': {
            'class': TechDocsScraper,
            'name': 'Genetec Technical Documentation',
            'url': 'https://techdocs.genetec.com/'
        }
    }

    def __init__(
        self,
        sites: List[str],
        output_base_dir: str = "data/knowledge_base/genetec",
        delay: float = 1.5,
        use_selenium: bool = False,
        limit: int = None
    ):
        """
        Initialize orchestrator.

        Args:
            sites: List of site keys to scrape ('scsaas', 'compliance', 'techdocs', or 'all')
            output_base_dir: Base directory for output
            delay: Delay between requests
            use_selenium: Whether to use Selenium (for compliance)
            limit: Limit URLs per scraper (for testing)
        """
        self.sites = self._expand_sites(sites)
        self.output_base_dir = Path(output_base_dir)
        self.delay = delay
        self.use_selenium = use_selenium
        self.limit = limit

        self.overall_stats = {
            'start_time': None,
            'end_time': None,
            'scrapers_run': 0,
            'total_urls': 0,
            'total_extracted': 0,
            'total_skipped_language': 0,
            'total_skipped_errors': 0,
            'scraper_results': {}
        }

    def _expand_sites(self, sites: List[str]) -> List[str]:
        """
        Expand 'all' to all available scrapers.

        Args:
            sites: List of site keys or ['all']

        Returns:
            Expanded list of site keys
        """
        if 'all' in sites:
            return list(self.AVAILABLE_SCRAPERS.keys())

        # Validate site keys
        invalid = [s for s in sites if s not in self.AVAILABLE_SCRAPERS]
        if invalid:
            raise ValueError(f"Invalid site(s): {invalid}. Available: {list(self.AVAILABLE_SCRAPERS.keys())}")

        return sites

    def run(self):
        """
        Run all selected scrapers.
        """
        self.overall_stats['start_time'] = datetime.now()

        print("=" * 80)
        print("GENETEC DOCUMENTATION SCRAPER ORCHESTRATOR")
        print("=" * 80)
        print(f"Sites to scrape: {', '.join(self.sites)}")
        print(f"Output directory: {self.output_base_dir}")
        print(f"Delay: {self.delay}s")
        if self.limit:
            print(f"Limit: {self.limit} URLs per scraper")
        if self.use_selenium:
            print("Selenium: ENABLED (for Compliance)")
        print("=" * 80)
        print()

        # Run each scraper
        for site_key in self.sites:
            self._run_scraper(site_key)

        # Finalize
        self.overall_stats['end_time'] = datetime.now()

        # Save consolidated statistics
        self._save_overall_stats()

        # Print final report
        self._print_final_report()

    def _run_scraper(self, site_key: str):
        """
        Run a single scraper.

        Args:
            site_key: Site key ('scsaas', 'compliance', 'techdocs')
        """
        scraper_info = self.AVAILABLE_SCRAPERS[site_key]

        print("\n" + "=" * 80)
        print(f"SCRAPER: {scraper_info['name']}")
        print(f"URL: {scraper_info['url']}")
        print("=" * 80)
        print()

        try:
            # Create scraper
            scraper_class = scraper_info['class']
            output_dir = self.output_base_dir / site_key

            # Initialize with appropriate parameters
            if site_key in ['compliance', 'techdocs']:
                # Compliance and TechDocs support Selenium
                scraper = scraper_class(
                    output_dir=str(output_dir),
                    delay_between_requests=self.delay,
                    use_selenium=self.use_selenium
                )
            else:
                # SCSaaS doesn't need Selenium
                scraper = scraper_class(
                    output_dir=str(output_dir),
                    delay_between_requests=self.delay
                )

            # Apply limit if specified
            if self.limit:
                original_discover = scraper.discover_urls

                def limited_discover():
                    urls = original_discover()
                    return urls[:self.limit]

                scraper.discover_urls = limited_discover

            # Run scraper
            stats = scraper.run()

            # Record results
            self.overall_stats['scrapers_run'] += 1
            self.overall_stats['total_urls'] += stats.get('urls_discovered', 0)
            self.overall_stats['total_extracted'] += stats.get('docs_extracted', 0)
            self.overall_stats['total_skipped_language'] += stats.get('docs_skipped_language', 0)
            self.overall_stats['total_skipped_errors'] += stats.get('docs_skipped_error', 0)

            # Store individual results
            self.overall_stats['scraper_results'][site_key] = {
                'name': scraper_info['name'],
                'url': scraper_info['url'],
                'urls_discovered': stats.get('urls_discovered', 0),
                'docs_extracted': stats.get('docs_extracted', 0),
                'docs_skipped_language': stats.get('docs_skipped_language', 0),
                'docs_skipped_errors': stats.get('docs_skipped_error', 0),
                'start_time': stats.get('start_time').isoformat() if stats.get('start_time') else None,
                'end_time': stats.get('end_time').isoformat() if stats.get('end_time') else None
            }

            print(f"\n✓ {scraper_info['name']} completed successfully")

        except Exception as e:
            print(f"\n✗ {scraper_info['name']} failed: {e}")
            import traceback
            traceback.print_exc()

            # Record failure
            self.overall_stats['scraper_results'][site_key] = {
                'name': scraper_info['name'],
                'url': scraper_info['url'],
                'error': str(e)
            }

    def _save_overall_stats(self):
        """Save overall statistics to JSON."""
        stats_file = self.output_base_dir / 'overall_scraping_stats.json'

        # Convert datetimes to strings
        stats_json = {}
        for key, value in self.overall_stats.items():
            if isinstance(value, datetime):
                stats_json[key] = value.isoformat()
            else:
                stats_json[key] = value

        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats_json, f, indent=2, ensure_ascii=False)

        print(f"\n Overall statistics saved to: {stats_file}")

    def _print_final_report(self):
        """Print final consolidated report."""
        duration = (self.overall_stats['end_time'] - self.overall_stats['start_time']).total_seconds()

        print("\n" + "=" * 80)
        print("OVERALL SCRAPING REPORT")
        print("=" * 80)
        print(f"Scrapers run: {self.overall_stats['scrapers_run']}/{len(self.sites)}")
        print(f"Total URLs discovered: {self.overall_stats['total_urls']}")
        print(f"Total documents extracted: {self.overall_stats['total_extracted']}")
        print(f"Total skipped (language): {self.overall_stats['total_skipped_language']}")
        print(f"Total skipped (errors): {self.overall_stats['total_skipped_errors']}")
        print(f"Total duration: {duration:.1f}s ({duration/60:.1f} minutes)")
        print()

        # Success rate
        if self.overall_stats['total_urls'] > 0:
            success_rate = (self.overall_stats['total_extracted'] / self.overall_stats['total_urls']) * 100
            print(f"Success rate: {success_rate:.1f}%")

        print()
        print("Results by scraper:")
        print("-" * 80)

        for site_key, result in self.overall_stats['scraper_results'].items():
            if 'error' in result:
                print(f"  ✗ {result['name']}: FAILED - {result['error']}")
            else:
                print(f"  ✓ {result['name']}: {result['docs_extracted']} documents")

        print()
        print(f"Output directory: {self.output_base_dir}")
        print("=" * 80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Genetec Documentation Scraper Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape all sites
  python -m scripts.scrapers.scraper_orchestrator --sites all

  # Scrape specific sites
  python -m scripts.scrapers.scraper_orchestrator --sites scsaas,techdocs

  # Test with limited URLs
  python -m scripts.scrapers.scraper_orchestrator --sites scsaas --limit 10

  # Use Selenium for Compliance (Cloudflare bypass)
  python -m scripts.scrapers.scraper_orchestrator --sites compliance --selenium
        """
    )

    parser.add_argument(
        '--sites',
        '-s',
        required=True,
        help="Sites to scrape (comma-separated: scsaas,compliance,techdocs or 'all')"
    )
    parser.add_argument(
        '--output',
        '-o',
        default="data/knowledge_base/genetec",
        help="Base output directory (default: data/knowledge_base/genetec)"
    )
    parser.add_argument(
        '--delay',
        '-d',
        type=float,
        default=1.5,
        help="Delay between requests in seconds (default: 1.5)"
    )
    parser.add_argument(
        '--selenium',
        action='store_true',
        help="Use Selenium for Compliance (Cloudflare bypass) and TechDocs (JavaScript rendering)"
    )
    parser.add_argument(
        '--limit',
        '-l',
        type=int,
        default=None,
        help="Limit URLs per scraper (for testing)"
    )

    args = parser.parse_args()

    # Parse sites
    sites = [s.strip() for s in args.sites.split(',')]

    try:
        # Create orchestrator
        orchestrator = ScraperOrchestrator(
            sites=sites,
            output_base_dir=args.output,
            delay=args.delay,
            use_selenium=args.selenium,
            limit=args.limit
        )

        # Run
        orchestrator.run()

        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
