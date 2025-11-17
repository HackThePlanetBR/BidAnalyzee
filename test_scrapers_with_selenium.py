#!/usr/bin/env python3
"""
Test script for web scrapers with Selenium using Playwright's Chromium
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Path to Playwright's Chromium
CHROME_PATH = "/root/.cache/ms-playwright/chromium-1194/chrome-linux/chrome"
CHROMEDRIVER_PATH = "/tmp/chromedriver-linux64/chromedriver"

def test_selenium_setup():
    """Test if Selenium works with Playwright's Chromium"""
    print("=" * 70)
    print("Testing Selenium Setup with Playwright Chromium")
    print("=" * 70)

    try:
        options = Options()
        options.binary_location = CHROME_PATH
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--no-proxy-server')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-background-networking')
        options.add_argument('--dns-prefetch-disable')

        service = Service(executable_path=CHROMEDRIVER_PATH)

        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)

        # Test with a local HTML page
        test_html = '''
        <html>
        <head><title>Selenium Test</title></head>
        <body><h1>Selenium is working!</h1></body>
        </html>
        '''

        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(test_html)
            test_file = f.name

        driver.get(f"file://{test_file}")
        title = driver.title

        driver.quit()

        import os
        os.unlink(test_file)

        print(f"✅ Selenium working! Test page title: {title}")
        return True

    except Exception as e:
        print(f"❌ Selenium setup failed: {e}")
        return False

def test_compliance_scraper():
    """Test Compliance scraper with Selenium"""
    print("\n" + "=" * 70)
    print("Testing Compliance Scraper with Selenium")
    print("=" * 70)

    try:
        from scripts.scrapers.compliance_scraper import ComplianceScraper

        # Monkey-patch the scraper to use our Chrome
        original_setup = ComplianceScraper._setup_selenium

        def patched_setup(self):
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service

            options = Options()
            options.binary_location = CHROME_PATH
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--headless=new')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--no-proxy-server')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-background-networking')
            options.add_argument('--dns-prefetch-disable')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            service = Service(executable_path=CHROMEDRIVER_PATH)

            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(30)
            self.logger.info("Selenium ready (Playwright Chromium)")

        ComplianceScraper._setup_selenium = patched_setup

        # Create scraper and test with limited sections
        scraper = ComplianceScraper(
            output_dir="/tmp/test_compliance",
            use_selenium=True,
            delay_between_requests=2.0
        )

        # Override discover to limit sections
        original_discover = scraper.discover_urls
        def limited_discover():
            urls = original_discover()
            return urls[:3]  # Only test first 3 sections
        scraper.discover_urls = limited_discover

        # Run scraper
        stats = scraper.run()

        # Check results
        success = stats['extracted'] > 0

        print(f"\n📊 Results:")
        print(f"  URLs discovered: {stats['discovered']}")
        print(f"  Processed: {stats['processed']}")
        print(f"  Extracted: {stats['extracted']}")
        print(f"  Failed: {stats['failed']}")
        print(f"  Success rate: {stats['extracted']/stats['processed']*100:.1f}%")

        if success:
            print(f"✅ Compliance scraper WORKING with Selenium!")

            # Show sample file
            output_dir = Path("/tmp/test_compliance")
            if output_dir.exists():
                files = list(output_dir.glob("*.md"))
                if files:
                    print(f"\n📄 Sample file: {files[0].name}")
                    content = files[0].read_text()[:500]
                    print(content + "...")
        else:
            print(f"❌ Compliance scraper failed to extract content")

        return success

    except Exception as e:
        print(f"❌ Compliance scraper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_techdocs_scraper():
    """Test TechDocs scraper with Selenium"""
    print("\n" + "=" * 70)
    print("Testing TechDocs Scraper with Selenium")
    print("=" * 70)

    try:
        from scripts.scrapers.techdocs_scraper import TechDocsScraper

        # Monkey-patch the scraper to use our Chrome
        original_setup = TechDocsScraper._setup_selenium

        def patched_setup(self):
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service

            options = Options()
            options.binary_location = CHROME_PATH
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--headless=new')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--no-proxy-server')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-background-networking')
            options.add_argument('--dns-prefetch-disable')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            service = Service(executable_path=CHROMEDRIVER_PATH)

            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(30)
            self.logger.info("Selenium ready (Playwright Chromium)")

        TechDocsScraper._setup_selenium = patched_setup

        # Create scraper
        scraper = TechDocsScraper(
            output_dir="/tmp/test_techdocs",
            use_selenium=True,
            delay_between_requests=2.0
        )

        # Override discover to limit URLs
        original_discover = scraper.discover_urls
        def limited_discover():
            urls = original_discover()
            return urls[:3]  # Only test first 3 URLs
        scraper.discover_urls = limited_discover

        # Run scraper
        stats = scraper.run()

        # Check results
        success = stats['extracted'] > 0

        print(f"\n📊 Results:")
        print(f"  URLs discovered: {stats['discovered']}")
        print(f"  Processed: {stats['processed']}")
        print(f"  Extracted: {stats['extracted']}")
        print(f"  Failed: {stats['failed']}")
        print(f"  Success rate: {stats['extracted']/stats['processed']*100:.1f}%")

        if success:
            print(f"✅ TechDocs scraper WORKING with Selenium!")

            # Show sample file and check if content is present
            output_dir = Path("/tmp/test_techdocs")
            if output_dir.exists():
                files = list(output_dir.glob("*.md"))
                if files:
                    print(f"\n📄 Sample file: {files[0].name}")
                    content = files[0].read_text()

                    # Check if there's actual content beyond frontmatter
                    parts = content.split('---')
                    if len(parts) >= 3:
                        actual_content = parts[2].strip()
                        if len(actual_content) > 100:
                            print(f"✅ Content extracted! ({len(actual_content)} chars)")
                            print(actual_content[:300] + "...")
                        else:
                            print(f"⚠️ Content is too short ({len(actual_content)} chars)")
                            success = False
        else:
            print(f"❌ TechDocs scraper failed to extract content")

        return success

    except Exception as e:
        print(f"❌ TechDocs scraper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "🧪 " * 20)
    print("WEB SCRAPER SELENIUM TESTING SUITE")
    print("🧪 " * 20 + "\n")

    results = {}

    # Test 1: Selenium setup
    results['selenium_setup'] = test_selenium_setup()

    if not results['selenium_setup']:
        print("\n❌ Selenium setup failed. Cannot proceed with scraper tests.")
        return

    # Test 2: Compliance scraper
    results['compliance'] = test_compliance_scraper()

    # Test 3: TechDocs scraper
    results['techdocs'] = test_techdocs_scraper()

    # Final report
    print("\n" + "=" * 70)
    print("FINAL TEST REPORT")
    print("=" * 70)

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    print(f"\n📊 Overall Results: {passed}/{total} tests passed")
    print(f"\nDetailed Results:")
    print(f"  Selenium Setup: {'✅ PASS' if results['selenium_setup'] else '❌ FAIL'}")
    print(f"  Compliance Scraper: {'✅ PASS' if results['compliance'] else '❌ FAIL'}")
    print(f"  TechDocs Scraper: {'✅ PASS' if results['techdocs'] else '❌ FAIL'}")

    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED! All scrapers working with Selenium!")
    else:
        print(f"\n⚠️ Some tests failed. Review output above for details.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
