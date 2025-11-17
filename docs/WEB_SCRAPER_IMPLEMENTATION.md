# Web Scraper Implementation - Genetec Knowledge Base

**Project:** BidAnalyzee RAG Knowledge Base Population
**Created:** 2025-11-17
**Status:** Planning Phase
**Agent:** Claude (Session: claude/web-scraper-markdown-01FByWrSRHDQxiUAxKYu6RY9)

---

## 🎯 Objective

Create a robust web scraping system to extract English-only technical documentation from 3 Genetec websites in Markdown format, with proper metadata for RAG system integration.

---

## 📊 Target Websites

| # | URL | Sitemap Available | Category Logic | Script Status |
|---|-----|-------------------|----------------|---------------|
| 1 | https://help.securitycentersaas.genetec.cloud/en/ | ✅ Yes (sitemap.xml) | Static: `SCSaaS` | ✅ Exists (script1) |
| 2 | https://compliance.genetec.com/ | ❌ No | Static: `Security/Compliance` | ✅ Exists (script2) |
| 3 | https://techdocs.genetec.com/ | ✅ Yes (sitemap.xml) | 🔄 Dynamic: Extract from product name | ❌ Needs Creation |

---

## 🔍 Analysis of Existing Scripts

### Script 1: SCSaaS Documentation Extractor

**File:** `genetec_saas_extractor.py` (script1)
**Target:** https://help.securitycentersaas.genetec.cloud/en/

#### ✅ Strengths:
- Uses official sitemap.xml for comprehensive URL discovery
- Clean HTML-to-Markdown conversion with proper structure
- Handles headings, lists, tables, blockquotes
- Progress tracking with tqdm
- Comprehensive logging system
- Statistics export (JSON)
- Creates organized index file (README.md)
- Category auto-detection from URL patterns
- Robust error handling with retries

#### ⚠️ Issues Identified:
1. **No YAML Frontmatter**: Doesn't generate metadata header required by RAG system
2. **No Language Filtering**: Doesn't check if content is in English
3. **Category Logic Incomplete**: Categories are generic, not aligned with RAG requirements
4. **No URL Metadata**: Doesn't embed source URL in document frontmatter
5. **File Naming**: May create conflicts with sanitized titles
6. **Duplicate Prevention**: Basic filename conflict resolution
7. **No Source Field**: Missing `source` metadata field

#### 🔧 Required Optimizations:
- Add YAML frontmatter generation with all required fields
- Implement language detection (English-only filter)
- Fix category to static `SCSaaS`
- Embed source URL in metadata
- Improve filename generation (use URL slug + hash for uniqueness)
- Add `source: "Security Center SaaS Help"` metadata

---

### Script 2: Compliance Portal Extractor

**File:** `genetec_compliance_extractor.py` (script2)
**Target:** https://compliance.genetec.com/

#### ✅ Strengths:
- Uses Undetected ChromeDriver to bypass Cloudflare
- Smart welcome text filtering (removes repetitive portal intro)
- Robust navigation retry logic
- Section-based extraction with dynamic discovery
- Fallback extraction when structured parsing fails
- Organized article grouping
- Progress tracking

#### ⚠️ Issues Identified:
1. **No YAML Frontmatter**: Missing metadata header
2. **No Language Filtering**: Doesn't validate English content
3. **Section-based Files**: Creates one file per section (may need consolidation)
4. **No URL Embedding**: Doesn't store source URL in metadata
5. **Heavy Dependencies**: Requires Selenium + ChromeDriver (resource intensive)
6. **Headless Mode**: Default is GUI mode (slow for batch processing)
7. **Category Not Set**: Doesn't use `Security/Compliance` category

#### 🔧 Required Optimizations:
- Add YAML frontmatter with `category: Security/Compliance`
- Enable headless mode by default
- Embed section URLs in metadata
- Add language validation
- Improve article-level file generation (one file per article vs. per section)
- Add `source: "Genetec Compliance Portal"` metadata
- Consider rate limiting to avoid triggering Cloudflare

---

### Script 3: TechDocs Extractor (To Be Created)

**File:** `genetec_techdocs_extractor.py` (script3)
**Target:** https://techdocs.genetec.com/

#### 📋 Requirements:
1. Use sitemap.xml for URL discovery
2. **Dynamic Category Extraction**: Parse product name from document/URL
   - Example: "Security Center" → Category: `Security Center`
   - Example: "Synergis" → Category: `Synergis`
   - Example: "AutoVu" → Category: `AutoVu`
3. Filter English-only content
4. Generate YAML frontmatter
5. Handle version-specific documentation
6. Source metadata: `"Genetec Technical Documentation"`

#### 🎯 Category Extraction Strategy:
```python
# URL pattern examples:
# https://techdocs.genetec.com/securitycenter/5.11/admin/... → Category: "Security Center"
# https://techdocs.genetec.com/synergis/2.12/guide/... → Category: "Synergis"
# https://techdocs.genetec.com/autovu/9.2/... → Category: "AutoVu"

def extract_category_from_url(url):
    """
    Extract product name from techdocs URL structure
    Pattern: /product-name/version/...
    """
    # Parse URL path
    # Extract second segment (product name)
    # Normalize to title case
    # Map common patterns:
    #   - securitycenter → Security Center
    #   - synergis → Synergis
    #   - autovu → AutoVu
    #   - clearid → Genetec ClearID
```

---

## 🏗️ Implementation Architecture

### Directory Structure

```
BidAnalyzee/
├── scripts/
│   └── scrapers/
│       ├── __init__.py
│       ├── base_scraper.py              # Abstract base class
│       ├── scsaas_scraper.py            # Script1 refactored
│       ├── compliance_scraper.py        # Script2 refactored
│       ├── techdocs_scraper.py          # Script3 new
│       ├── scraper_orchestrator.py      # Unified runner
│       └── utils/
│           ├── __init__.py
│           ├── html_to_markdown.py      # Shared conversion logic
│           ├── frontmatter_generator.py # YAML metadata
│           ├── language_detector.py     # English-only filter
│           └── filename_utils.py        # Safe naming
├── data/
│   └── knowledge_base/
│       └── genetec/                     # Output directory
│           ├── scsaas/
│           ├── compliance/
│           └── techdocs/
└── docs/
    ├── WEB_SCRAPER_IMPLEMENTATION.md    # This file
    └── WEB_SCRAPER_STATUS.md            # Progress tracking
```

---

## 📝 Required Markdown Output Format

All scrapers must generate markdown files with this structure:

```markdown
---
title: "API Authentication Guide"
url: "https://help.securitycentersaas.genetec.cloud/en/api/authentication.html"
source: "Security Center SaaS Help"
category: "SCSaaS"
date: "2025-11-17"
language: "en"
product: "Security Center SaaS"
version: "latest"
---

# API Authentication Guide

This guide explains how to authenticate API requests...

## Prerequisites

- Valid API credentials
- Network access to SaaS instance

...
```

### Required Frontmatter Fields

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `title` | string | ✅ Yes | Document title | "API Authentication Guide" |
| `url` | string | ✅ Yes | Source URL | "https://help.scsaas.genetec.cloud/..." |
| `source` | string | ✅ Yes | Website name | "Security Center SaaS Help" |
| `category` | string | ✅ Yes | Content category | "SCSaaS" or "Security/Compliance" or product name |
| `date` | string | ✅ Yes | Extraction date (ISO) | "2025-11-17" |
| `language` | string | ✅ Yes | Content language | "en" |
| `product` | string | ⚠️ Optional | Product name | "Security Center" |
| `version` | string | ⚠️ Optional | Product version | "5.11" or "latest" |

---

## 🔧 Common Utilities to Implement

### 1. Language Detector (`language_detector.py`)

```python
def is_english_content(text: str, threshold: float = 0.8) -> bool:
    """
    Detect if text is primarily English.

    Uses:
    - Common English stop words frequency
    - Character set validation (ASCII heavy)
    - Language detection library (langdetect)

    Args:
        text: Content to analyze
        threshold: Minimum confidence (0.0-1.0)

    Returns:
        True if English content detected
    """
```

**Implementation Strategy:**
- Use `langdetect` library for probabilistic detection
- Fallback: Check for English stop words (the, and, is, of, to, etc.)
- Check URL for language indicators (`/en/`, `/pt/`, `/fr/`)
- Minimum text length: 100 chars for reliable detection

### 2. Frontmatter Generator (`frontmatter_generator.py`)

```python
def generate_frontmatter(
    title: str,
    url: str,
    source: str,
    category: str,
    language: str = "en",
    product: str = None,
    version: str = None,
    extra_fields: dict = None
) -> str:
    """
    Generate YAML frontmatter for markdown files.

    Returns formatted YAML header with metadata.
    """
```

### 3. HTML to Markdown Converter (`html_to_markdown.py`)

Consolidate conversion logic from script1/script2:
- Use `html2text` library as base
- Custom handlers for:
  - Tables (preserve formatting)
  - Code blocks (detect language)
  - Lists (nested support)
  - Blockquotes
  - Images (with alt text)
  - Links (preserve absolute URLs)

### 4. Filename Utilities (`filename_utils.py`)

```python
def create_safe_filename(
    title: str,
    url: str,
    max_length: int = 100,
    add_hash: bool = True
) -> str:
    """
    Create filesystem-safe filename from title and URL.

    Strategy:
    - Sanitize title (remove special chars)
    - Limit length
    - Add short hash of URL for uniqueness
    - Ensure .md extension

    Returns:
        Safe filename like: "api-authentication-guide-a3f2d1.md"
    """
```

---

## 🎯 Implementation Plan

### Phase 1: Setup Base Infrastructure ⏳

**Tasks:**
1. Create `scripts/scrapers/` directory structure
2. Implement `base_scraper.py` abstract class
3. Implement shared utilities:
   - `language_detector.py`
   - `frontmatter_generator.py`
   - `html_to_markdown.py`
   - `filename_utils.py`
4. Create output directories in `data/knowledge_base/genetec/`

**Deliverables:**
- Base scraper interface with common methods
- Reusable utility functions
- Unit tests for utilities

---

### Phase 2: Refactor Script 1 (SCSaaS) ⏳

**Tasks:**
1. Migrate script1 code to `scsaas_scraper.py`
2. Inherit from `BaseScraper`
3. Add language detection filter
4. Implement frontmatter generation
5. Fix category to `SCSaaS`
6. Improve filename generation
7. Update metadata fields

**Key Changes:**
```python
# BEFORE (script1)
def save_document(self, doc_data, output_dir="genetec_docs"):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(doc_data['content'])

# AFTER (refactored)
def save_document(self, doc_data, output_dir="data/knowledge_base/genetec/scsaas"):
    # Generate frontmatter
    frontmatter = generate_frontmatter(
        title=doc_data['title'],
        url=doc_data['url'],
        source="Security Center SaaS Help",
        category="SCSaaS",
        language="en"
    )

    # Combine frontmatter + content
    full_content = f"{frontmatter}\n{doc_data['content']}"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_content)
```

**Deliverables:**
- `scsaas_scraper.py` with all optimizations
- Updated output format with frontmatter
- Language filtering enabled

---

### Phase 3: Refactor Script 2 (Compliance) ⏳

**Tasks:**
1. Migrate script2 code to `compliance_scraper.py`
2. Inherit from `BaseScraper`
3. Add language detection
4. Implement frontmatter generation
5. Set category to `Security/Compliance`
6. Enable headless mode by default
7. Improve article-level extraction
8. Embed section URLs in metadata

**Key Changes:**
```python
# Add to each article
frontmatter = generate_frontmatter(
    title=article['title'],
    url=f"{self.base_url}?itemName={section_name}#{article_slug}",
    source="Genetec Compliance Portal",
    category="Security/Compliance",
    language="en"
)
```

**Deliverables:**
- `compliance_scraper.py` with optimizations
- Headless mode enabled
- Proper metadata in all outputs

---

### Phase 4: Create Script 3 (TechDocs) ⏳

**Tasks:**
1. Create `techdocs_scraper.py` from scratch
2. Implement sitemap.xml parsing (similar to script1)
3. Implement dynamic category extraction logic
4. Create product name mapping:
   ```python
   PRODUCT_MAPPINGS = {
       'securitycenter': 'Security Center',
       'synergis': 'Synergis',
       'autovu': 'AutoVu',
       'clearid': 'Genetec ClearID',
       'streamvault': 'Genetec StreamVault',
       # ... add more as discovered
   }
   ```
5. Extract version information from URLs
6. Add language filtering
7. Implement frontmatter generation

**URL Parsing Logic:**
```python
def extract_category_from_url(self, url: str) -> tuple[str, str]:
    """
    Extract product category and version from techdocs URL.

    Example:
        Input: "https://techdocs.genetec.com/securitycenter/5.11/admin/..."
        Output: ("Security Center", "5.11")

    Returns:
        (category, version)
    """
    # Parse: /product/version/...
    # Map product slug to friendly name
    # Return both category and version
```

**Deliverables:**
- Complete `techdocs_scraper.py`
- Dynamic category extraction working
- Version tracking in metadata

---

### Phase 5: Create Unified Orchestrator ⏳

**Tasks:**
1. Create `scraper_orchestrator.py`
2. Implement sequential/parallel scraper execution
3. Add CLI interface with argparse:
   ```bash
   python scraper_orchestrator.py --sites scsaas,compliance,techdocs
   python scraper_orchestrator.py --sites all
   python scraper_orchestrator.py --sites techdocs --headless
   ```
4. Implement progress tracking
5. Generate consolidated statistics
6. Create master index file

**Features:**
- Site selection (individual or all)
- Headless mode toggle
- Rate limiting configuration
- Output directory configuration
- Statistics export (JSON + CSV)

**Deliverables:**
- Unified CLI tool
- Documentation on usage
- Example commands

---

### Phase 6: Testing & Validation ⏳

**Tasks:**
1. Run each scraper individually
2. Validate output format:
   - Frontmatter present and valid YAML
   - All required fields populated
   - Content is English-only
   - Markdown syntax valid
3. Check RAG compatibility:
   - Test with `scripts/index_knowledge_base.py`
   - Verify metadata extraction
   - Test search queries
4. Performance testing:
   - Measure extraction speed
   - Check memory usage
   - Validate error handling

**Validation Checklist:**
- [ ] All files have valid YAML frontmatter
- [ ] `title` field matches document title
- [ ] `url` field is absolute and accessible
- [ ] `source` field is correct for each site
- [ ] `category` follows requirements:
  - SCSaaS → `SCSaaS`
  - Compliance → `Security/Compliance`
  - TechDocs → Product name (dynamic)
- [ ] `date` is ISO format (YYYY-MM-DD)
- [ ] `language` is always `en`
- [ ] Content is valid Markdown
- [ ] No non-English content leaked through
- [ ] Filenames are unique and safe

**Deliverables:**
- Test report with validation results
- Sample output files for review
- Performance metrics

---

### Phase 7: Integration with RAG System ⏳

**Tasks:**
1. Configure knowledge base path in `.env`:
   ```bash
   RAG_KNOWLEDGE_BASE_PATH=data/knowledge_base/genetec
   ```
2. Run indexing:
   ```bash
   python scripts/index_knowledge_base.py \
     --kb-path data/knowledge_base/genetec \
     --force \
     --verify
   ```
3. Test RAG search with Genetec queries
4. Validate category usage in analysis CSV
5. Update documentation

**Test Queries:**
```bash
# Test SCSaaS category
python scripts/rag_search.py --requirement "API authentication in SCSaaS" --top-k 5

# Test Compliance category
python scripts/rag_search.py --requirement "Security certifications" --top-k 5

# Test TechDocs categories
python scripts/rag_search.py --requirement "Security Center camera setup" --top-k 5
```

**Deliverables:**
- Indexed vector store with Genetec knowledge
- Search validation results
- Updated RAG configuration

---

## 📊 Expected Output Statistics

### Target Metrics (Estimated)

| Site | Estimated Pages | Expected Categories | Avg Size/Page |
|------|----------------|---------------------|---------------|
| SCSaaS Help | ~500-800 | SCSaaS | 2-5 KB |
| Compliance Portal | ~50-100 | Security/Compliance | 3-10 KB |
| TechDocs | ~2000-5000 | 10-15 products | 5-15 KB |
| **TOTAL** | **~2550-5900** | **12-17 categories** | **~20-30 MB** |

---

## 🔒 Scraping Best Practices

### Ethical Scraping Guidelines

1. **Rate Limiting:**
   - Delay between requests: 1.5-3 seconds
   - Respect `robots.txt` directives
   - Use sitemaps when available

2. **User-Agent:**
   - Identify as legitimate bot
   - Include contact info if possible
   - Example: `"BidAnalyzee-RAG-Bot/1.0 (Educational Purpose)"`

3. **Cloudflare Handling:**
   - Use undetected-chromedriver only when necessary
   - Minimize headless detection
   - Retry with exponential backoff

4. **Error Handling:**
   - Log all errors
   - Retry failed requests (max 3 attempts)
   - Continue on error (don't crash entire process)

5. **Resource Usage:**
   - Use headless mode for production
   - Clean up browser sessions
   - Limit concurrent requests

---

## 🐛 Known Issues & Mitigation

### Issue 1: Cloudflare Protection (compliance.genetec.com)
**Impact:** May block automated scraping
**Mitigation:**
- Use undetected-chromedriver
- Implement retry logic
- Add random delays
- Consider manual CAPTCHA solving if automated fails

### Issue 2: Language Detection Accuracy
**Impact:** May include non-English content or exclude valid English
**Mitigation:**
- Check URL patterns first (`/en/`, `/pt/`, etc.)
- Use multiple detection methods
- Set conservative thresholds
- Manual review of sample outputs

### Issue 3: Dynamic Category Extraction (techdocs)
**Impact:** May misclassify products
**Mitigation:**
- Maintain product mapping dictionary
- Log unknown products for manual review
- Use URL pattern as fallback
- Validate against known product list

### Issue 4: Duplicate Content
**Impact:** Same content under different URLs
**Mitigation:**
- Use content hashing to detect duplicates
- Prefer canonical URLs
- Check for URL parameters (utm_*, etc.)

### Issue 5: Large Volume Processing
**Impact:** Thousands of pages to process
**Mitigation:**
- Implement checkpointing (resume capability)
- Process in batches
- Monitor memory usage
- Parallel processing (with rate limiting)

---

## 📦 Dependencies

### Required Python Packages

```txt
# Existing dependencies (from current project)
beautifulsoup4>=4.12.0
requests>=2.31.0
tqdm>=4.66.0
lxml>=4.9.0

# New dependencies for scrapers
selenium>=4.15.0
undetected-chromedriver>=3.5.0
langdetect>=1.0.9
html2text>=2020.1.16
pyyaml>=6.0.1
```

### Installation Command
```bash
pip install beautifulsoup4 requests tqdm lxml selenium undetected-chromedriver langdetect html2text pyyaml
```

---

## 🔄 Maintenance & Updates

### Periodic Tasks

**Weekly:**
- Check for sitemap updates
- Monitor for new products (techdocs)
- Validate language detection accuracy

**Monthly:**
- Full re-scrape of all sites
- Update product mappings
- Review error logs

**Quarterly:**
- Update ChromeDriver version
- Audit category classifications
- Performance optimization review

---

## 📚 References

### RAG System Integration
- See: `docs/WEB_SCRAPER_GUIDE.md` - Original scraper template
- See: `agents/technical_analyst/ingestion_pipeline.py` - Document processing
- See: `.env.example` - Configuration options

### Knowledge Base Format
- Location: `data/knowledge_base/`
- Example: `data/knowledge_base/mock/exemplo_com_url.md`
- Frontmatter spec: YAML with required fields

### Analysis Pipeline
- See: `agents/technical_analyst/query_processor.py` - Category usage
- Output: CSV with `Categoria`, `Fonte_Titulo`, `Fonte_URL` columns

---

## 🎯 Success Criteria

**The implementation is complete when:**

✅ All 3 scrapers are operational
✅ All output files have valid YAML frontmatter
✅ Language filtering excludes non-English content
✅ Categories are correctly assigned:
  - SCSaaS: Static `SCSaaS`
  - Compliance: Static `Security/Compliance`
  - TechDocs: Dynamic extraction from product name
✅ Markdown conversion is clean and readable
✅ Filenames are unique and filesystem-safe
✅ RAG system can index and search the knowledge base
✅ CSV analysis includes correct category metadata
✅ Orchestrator can run all scrapers in sequence
✅ Documentation is complete and accurate

---

## 👥 Handoff Notes for Next Agent

### What's Done
- ✅ Planning and documentation
- ✅ Analysis of existing scripts
- ✅ Architecture design
- ✅ Output format specification

### What's Next
1. Start with Phase 1 (base infrastructure)
2. Create utility functions first
3. Test each utility independently
4. Then proceed to Phase 2-7 in order

### Key Files to Create
```
scripts/scrapers/base_scraper.py          # Start here
scripts/scrapers/utils/language_detector.py
scripts/scrapers/utils/frontmatter_generator.py
scripts/scrapers/utils/html_to_markdown.py
scripts/scrapers/utils/filename_utils.py
scripts/scrapers/scsaas_scraper.py
scripts/scrapers/compliance_scraper.py
scripts/scrapers/techdocs_scraper.py
scripts/scrapers/scraper_orchestrator.py
```

### Testing Strategy
- Test utilities with sample HTML/text
- Test each scraper on 5-10 sample URLs first
- Validate frontmatter YAML syntax
- Check RAG integration before full scrape

### Important Notes
- Always use headless mode for final scraping
- Respect rate limits (1.5-3s delay)
- Log everything for debugging
- Save progress checkpoints for large scrapes

---

**End of Implementation Plan**
**Status:** Documentation Complete - Ready for Implementation
**Next Step:** Commit this documentation and proceed to Phase 1
