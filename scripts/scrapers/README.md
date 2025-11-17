# Genetec Documentation Scrapers

Automated web scrapers for extracting Genetec technical documentation in Markdown format with proper metadata for RAG system integration.

## Overview

This package contains scrapers for three Genetec documentation websites:

1. **SCSaaS Scraper** (`scsaas_scraper.py`)
   - Site: https://help.securitycentersaas.genetec.cloud/en/
   - Category: `SCSaaS` (static)
   - Method: Sitemap.xml discovery

2. **Compliance Scraper** (`compliance_scraper.py`)
   - Site: https://compliance.genetec.com/
   - Category: `Security/Compliance` (static)
   - Method: Section-based navigation
   - Features: Cloudflare bypass support (Selenium required)

3. **TechDocs Scraper** (`techdocs_scraper.py`)
   - Site: https://techdocs.genetec.com/
   - Category: Dynamic (extracted from product name)
   - Method: Sitemap.xml discovery
   - Features: JavaScript rendering support (Selenium required for content extraction)

## Features

All scrapers provide:

- **English-only filtering**: Automatically detects and skips non-English content
- **YAML frontmatter**: Generates proper metadata for RAG integration
- **Markdown conversion**: Clean HTML-to-Markdown transformation
- **Rate limiting**: Configurable delays between requests
- **Progress tracking**: Real-time statistics and logging
- **Error handling**: Robust retry logic and error recovery

## Installation

### Required Dependencies

```bash
pip install beautifulsoup4 lxml requests pyyaml tqdm
```

### Configuration (.env)

**NEW:** All settings are now configurable via environment variables!

Add to your `.env` file:

```bash
# ============================================
# WEB SCRAPERS CONFIGURATION
# ============================================
# Selenium Configuration
SCRAPERS_USE_SELENIUM=true                # Enable Selenium for Compliance and TechDocs
SCRAPERS_HEADLESS=true                    # Run browser in headless mode

# Proxy Configuration
SCRAPERS_USE_PROXY=false                  # Enable proxy for Selenium
SCRAPERS_PROXY_URL=                       # Proxy URL (e.g., http://proxy.example.com:8080)
# If empty and USE_PROXY=true, will auto-detect from HTTP_PROXY environment variable

# Rate Limiting
SCRAPERS_DELAY_BETWEEN_REQUESTS=1.5       # Seconds between requests (be polite!)

# Output Configuration
SCRAPERS_OUTPUT_DIR=data/knowledge_base/genetec

# Browser Configuration (optional - auto-detect if empty)
SCRAPERS_CHROME_BINARY_PATH=              # Path to Chrome/Chromium
SCRAPERS_CHROMEDRIVER_PATH=               # Path to ChromeDriver
```

**View Current Configuration:**
```bash
python -m scripts.scrapers.scraper_orchestrator --print-config
```

**CLI Overrides:** You can override .env settings via command-line flags:
```bash
# Use proxy (override .env)
python -m scripts.scrapers.scraper_orchestrator --sites all --use-proxy --proxy-url http://proxy:8080

# Disable headless mode (see browser)
python -m scripts.scrapers.scraper_orchestrator --sites techdocs --selenium --no-headless

# Enable headless mode
python -m scripts.scrapers.scraper_orchestrator --sites all --selenium --headless
```

### Selenium Dependencies (Required for Compliance and TechDocs)

**Required for:**
- **Compliance scraper:** Cloudflare bypass (site blocks basic HTTP requests)
- **TechDocs scraper:** JavaScript rendering (SPA site, content not available without JS)

**Installation:**
```bash
pip install selenium                    # Required
pip install undetected-chromedriver    # Optional but recommended (better Cloudflare bypass)
```

**System Requirements:**
- Chrome or Chromium browser must be installed
- ChromeDriver is managed automatically by Selenium

**Notes:**
- SCSaaS scraper works perfectly without Selenium (requests-based)
- Compliance and TechDocs scrapers will use regular Selenium if undetected-chromedriver is unavailable
- Both scrapers include graceful fallback mechanisms

## Quick Start

### Run All Scrapers

```bash
# From project root (with Selenium for full coverage)
python -m scripts.scrapers.scraper_orchestrator --sites all --selenium

# Without Selenium (only SCSaaS will work properly)
python -m scripts.scrapers.scraper_orchestrator --sites all
```

### Run Individual Scrapers

```bash
# SCSaaS Help (no Selenium needed)
python -m scripts.scrapers.scsaas_scraper

# Compliance Portal (REQUIRES Selenium)
python -m scripts.scrapers.compliance_scraper --selenium

# Technical Documentation (REQUIRES Selenium for content)
python -m scripts.scrapers.techdocs_scraper --selenium
```

## Usage Examples

### Orchestrator (Recommended)

The orchestrator runs multiple scrapers in sequence:

```bash
# Scrape all sites (RECOMMENDED: with Selenium for full coverage)
python -m scripts.scrapers.scraper_orchestrator --sites all --selenium

# Scrape specific sites
python -m scripts.scrapers.scraper_orchestrator --sites scsaas,techdocs --selenium

# Custom output directory
python -m scripts.scrapers.scraper_orchestrator --sites all --selenium --output /path/to/output

# Adjust rate limiting (slower = more polite)
python -m scripts.scrapers.scraper_orchestrator --sites all --selenium --delay 3.0

# Test with limited URLs (useful before full run)
python -m scripts.scrapers.scraper_orchestrator --sites all --selenium --limit 10
```

### Individual Scrapers

Each scraper can be run standalone:

#### SCSaaS Scraper

```bash
python -m scripts.scrapers.scsaas_scraper \
  --output data/knowledge_base/genetec/scsaas \
  --delay 1.5
```

#### Compliance Scraper

```bash
# Without Selenium (may fail if Cloudflare is active)
python -m scripts.scrapers.compliance_scraper \
  --output data/knowledge_base/genetec/compliance

# With Selenium (recommended)
python -m scripts.scrapers.compliance_scraper \
  --output data/knowledge_base/genetec/compliance \
  --selenium
```

#### TechDocs Scraper

```bash
# Scrape all products (REQUIRES Selenium for content extraction)
python -m scripts.scrapers.techdocs_scraper \
  --selenium \
  --output data/knowledge_base/genetec/techdocs

# Filter by product (with Selenium)
python -m scripts.scrapers.techdocs_scraper \
  --selenium \
  --product securitycenter \
  --limit 50

# Without Selenium (will only get metadata, NO content)
python -m scripts.scrapers.techdocs_scraper \
  --output data/knowledge_base/genetec/techdocs
```

## Output Format

All scrapers generate markdown files with YAML frontmatter:

```markdown
---
title: "API Authentication Guide"
url: "https://help.securitycentersaas.genetec.cloud/en/api/auth.html"
source: "Security Center SaaS Help"
category: "SCSaaS"
date: "2025-11-17"
language: "en"
---

# API Authentication Guide

This guide explains how to authenticate...
```

### Metadata Fields

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `title` | Yes | Document title | "API Authentication Guide" |
| `url` | Yes | Source URL | "https://..." |
| `source` | Yes | Website name | "Security Center SaaS Help" |
| `category` | Yes | Content category | "SCSaaS" or "Security Center" |
| `date` | Yes | Extraction date | "2025-11-17" |
| `language` | Yes | Content language | "en" |
| `product` | No | Product name | "Security Center" |
| `version` | No | Product version | "5.11" |

## Output Directories

Default output structure:

```
data/knowledge_base/genetec/
├── scsaas/
│   ├── document-1-abc123.md
│   ├── document-2-def456.md
│   └── scraping_stats.json
├── compliance/
│   ├── certifications-789ghi.md
│   └── scraping_stats.json
├── techdocs/
│   ├── camera-setup-jkl012.md
│   └── scraping_stats.json
└── overall_scraping_stats.json
```

## Statistics

Each scraper generates a `scraping_stats.json` file:

```json
{
  "urls_discovered": 500,
  "urls_processed": 500,
  "docs_extracted": 475,
  "docs_skipped_language": 10,
  "docs_skipped_error": 15,
  "start_time": "2025-11-17T10:00:00",
  "end_time": "2025-11-17T12:30:00"
}
```

The orchestrator also generates `overall_scraping_stats.json` with consolidated results.

## Category Assignment

### SCSaaS: Static Category

All documents from SCSaaS Help are assigned:
- **Category:** `SCSaaS`
- **Source:** `Security Center SaaS Help`

### Compliance: Static Category

All documents from Compliance Portal are assigned:
- **Category:** `Security/Compliance`
- **Source:** `Genetec Compliance Portal`

### TechDocs: Dynamic Categories

TechDocs extracts the product name from the URL and uses it as the category:

| URL Pattern | Product Slug | Category |
|-------------|--------------|----------|
| `/securitycenter/...` | securitycenter | Security Center |
| `/synergis/...` | synergis | Synergis |
| `/autovu/...` | autovu | AutoVu |
| `/clearid/...` | clearid | Genetec ClearID |

Unknown products are automatically mapped using title case conversion.

## Language Filtering

All scrapers enforce English-only content using multiple detection strategies:

1. **URL Pattern Detection**: Checks for `/en/`, `/pt/`, etc. in URL
2. **Content Analysis**: Uses language detection library or stop words analysis
3. **Confidence Threshold**: Minimum 70% confidence required

Non-English content is automatically skipped and logged.

## Troubleshooting

### Issue: Compliance scraper returns 503 errors

**Problem:** Cloudflare bot protection blocks requests-based scraping

**Solution:** Use Selenium mode:
```bash
python -m scripts.scrapers.compliance_scraper --selenium
```

Ensure Selenium is installed:
```bash
pip install selenium
pip install undetected-chromedriver  # Optional but recommended
```

Make sure Chrome/Chromium is installed on your system.

### Issue: TechDocs scraper returns empty content

**Problem:** TechDocs is a Single Page Application (SPA) that requires JavaScript execution

**Solution:** Use Selenium mode:
```bash
python -m scripts.scrapers.techdocs_scraper --selenium
```

Without Selenium, you'll get valid frontmatter metadata but no actual content.

### Issue: Chrome/ChromeDriver not found

**Problem:** Selenium can't find Chrome browser or ChromeDriver

**Solution:**
- Install Chrome or Chromium browser on your system
- ChromeDriver is managed automatically by Selenium 4.x
- If issues persist, try: `pip install --upgrade selenium`

### Issue: Rate limiting / 429 errors

**Solution:** Increase delay between requests:
```bash
python -m scripts.scrapers.scraper_orchestrator --sites all --delay 3.0
```

### Issue: Too many URLs to process

**Solution:** Use the `--limit` flag for testing:
```bash
python -m scripts.scrapers.techdocs_scraper --limit 50
```

Or filter by product:
```bash
python -m scripts.scrapers.techdocs_scraper --product securitycenter
```

### Issue: Non-English content getting through

**Solution:** Content is validated during processing. Check the logs for language detection details. Adjust confidence threshold if needed (edit source code).

## Integration with RAG System

After scraping, index the documents:

```bash
# Index knowledge base
python scripts/index_knowledge_base.py \
  --kb-path data/knowledge_base/genetec \
  --force \
  --verify
```

Test RAG search:

```bash
# Search for content
python scripts/rag_search.py \
  --requirement "API authentication in SaaS" \
  --top-k 5
```

The metadata flows through to CSV analysis:
- `category` → CSV `Categoria` column
- `title` → CSV `Fonte_Titulo` column
- `url` → CSV `Fonte_URL` column

## Architecture

### Base Infrastructure

- **base_scraper.py**: Abstract base class with common workflow
- **utils/frontmatter_generator.py**: YAML metadata generation
- **utils/language_detector.py**: Multi-strategy language detection
- **utils/html_to_markdown.py**: HTML to Markdown conversion
- **utils/filename_utils.py**: Safe filename generation

### Concrete Scrapers

Each scraper inherits from `BaseScraper` and implements:
- `discover_urls()`: Find URLs to scrape
- `extract_content(url)`: Extract HTML and title
- `get_category(url)`: Determine category

### Orchestrator

Coordinates multiple scrapers and provides:
- Unified CLI interface
- Consolidated statistics
- Error handling and reporting

## Development

### Adding a New Scraper

1. Create new file: `scripts/scrapers/mysite_scraper.py`
2. Inherit from `BaseScraper`
3. Implement required abstract methods
4. Register in orchestrator's `AVAILABLE_SCRAPERS`

Example:

```python
from .base_scraper import BaseScraper

class MySiteScraper(BaseScraper):
    def __init__(self, output_dir="data/knowledge_base/mysite"):
        super().__init__(
            base_url="https://mysite.com",
            source_name="My Documentation Site",
            output_dir=output_dir
        )

    def discover_urls(self) -> List[str]:
        # Implement URL discovery
        pass

    def extract_content(self, url: str) -> Optional[Dict[str, Any]]:
        # Implement content extraction
        pass

    def get_category(self, url: str, content=None) -> str:
        # Implement category logic
        return "MyCategory"
```

## Best Practices

1. **Rate Limiting**: Always use appropriate delays (1.5-3s) between requests
2. **Error Handling**: Check logs for errors and retry failed URLs
3. **Language Validation**: Review language detection stats to ensure quality
4. **Testing**: Use `--limit` flag to test on small batches first
5. **Monitoring**: Check `scraping_stats.json` for success rates

## License

Part of the BidAnalyzee project.

## Support

For issues or questions:
- Check logs in output directory
- Review `scraping_stats.json` for details
- Consult `docs/WEB_SCRAPER_IMPLEMENTATION.md` for architecture details
