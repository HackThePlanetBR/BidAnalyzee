# Web Scraper Tests

Test scripts for the Genetec documentation web scrapers.

## Test Files

### test_scrapers_with_selenium.py

Comprehensive test suite for all web scrapers using Selenium with Playwright's Chromium.

**Tests:**
- Selenium setup and configuration
- Compliance scraper with Cloudflare bypass
- TechDocs scraper with JavaScript rendering

**Usage:**
```bash
# From project root
python tests/scrapers/test_scrapers_with_selenium.py
```

**Requirements:**
- Selenium installed
- Chrome/Chromium available (uses Playwright's Chromium by default)
- ChromeDriver compatible with browser version

**What it tests:**
- ✅ Selenium WebDriver initialization
- ✅ Proxy configuration (if HTTP_PROXY set)
- ✅ Compliance scraper URL discovery and extraction
- ✅ TechDocs scraper URL discovery and content extraction
- ✅ Markdown file generation with frontmatter
- ✅ Content validation

### test_quick.py

Quick smoke test for proxy configuration with Selenium.

**Usage:**
```bash
# From project root
python tests/scrapers/test_quick.py
```

**What it tests:**
- ✅ Selenium setup with proxy
- ✅ Basic page loading
- ✅ JavaScript rendering detection

## Configuration

Both test scripts use hardcoded paths to Playwright's Chromium:

```python
CHROME_PATH = "/root/.cache/ms-playwright/chromium-1194/chrome-linux/chrome"
CHROMEDRIVER_PATH = "/tmp/chromedriver-linux64/chromedriver"
```

**To use different Chrome/ChromeDriver:**
Edit the paths in the test files before running.

## Running Tests

### From Project Root

```bash
# Full test suite
python tests/scrapers/test_scrapers_with_selenium.py

# Quick test
python tests/scrapers/test_quick.py
```

### With Proxy

```bash
# Set proxy environment variable
export HTTP_PROXY=http://proxy.example.com:8080

# Run tests
python tests/scrapers/test_scrapers_with_selenium.py
```

## Expected Output

### test_scrapers_with_selenium.py

```
🧪 WEB SCRAPER SELENIUM TESTING SUITE
======================================================================
Testing Selenium Setup with Playwright Chromium
======================================================================
✅ Selenium working! Test page title: Selenium Test

======================================================================
Testing Compliance Scraper with Selenium
======================================================================
📊 Results:
  URLs discovered: 3
  Processed: 3
  Extracted: 3
  Failed: 0
  Success rate: 100.0%
✅ Compliance scraper WORKING with Selenium!

======================================================================
Testing TechDocs Scraper with Selenium
======================================================================
📊 Results:
  URLs discovered: 3
  Processed: 3
  Extracted: 3
  Failed: 0
  Success rate: 100.0%
✅ TechDocs scraper WORKING with Selenium!

======================================================================
FINAL TEST REPORT
======================================================================
📊 Overall Results: 3/3 tests passed

Detailed Results:
  Selenium Setup: ✅ PASS
  Compliance Scraper: ✅ PASS
  TechDocs Scraper: ✅ PASS

🎉 ALL TESTS PASSED! All scrapers working with Selenium!
```

## Troubleshooting

### Chrome/ChromeDriver not found

Update paths in test scripts:
```python
CHROME_PATH = "/path/to/your/chrome"
CHROMEDRIVER_PATH = "/path/to/your/chromedriver"
```

### Import errors

Make sure you're running from project root:
```bash
cd /path/to/BidAnalyzee
python tests/scrapers/test_scrapers_with_selenium.py
```

### Proxy issues

Check HTTP_PROXY variable:
```bash
echo $HTTP_PROXY
```

Unset if causing problems:
```bash
unset HTTP_PROXY
```

## See Also

- [Web Scraper Documentation](../../docs/scrapers/)
- [Scraper Implementation](../../scripts/scrapers/)
- [Test Reports](../../docs/test-results/)
