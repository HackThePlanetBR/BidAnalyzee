# OCR Handler - Document Structurer

**Module:** `ocr_handler.py`
**Version:** 1.0.0
**Purpose:** Automatic OCR processing for scanned/image-based PDF documents

---

## 📋 Overview

The OCR Handler enables the Document Structurer to automatically extract text from scanned PDFs using Optical Character Recognition (OCR). This eliminates the need for manual intervention when processing image-based documents.

**Key Features:**
- ✅ Automatic scanned PDF detection
- ✅ Portuguese language optimization (default)
- ✅ Image preprocessing for better accuracy
- ✅ Confidence scoring per extraction
- ✅ Graceful degradation when OCR unavailable
- ✅ Supports multi-page PDF processing

---

## 🚀 Quick Start

### Installation

**1. Install System Dependencies (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-por
```

**2. Install Python Packages:**
```bash
pip install Pillow pytesseract pdf2image
```

### Usage

```python
from agents.document_structurer.extractors.ocr_handler import OCRHandler

# Initialize handler
handler = OCRHandler(language="por")  # Portuguese

# Check if OCR is available
if handler.is_available():
    # Extract text from scanned PDF
    result = handler.extract_text_from_pdf("edital_scanned.pdf")

    print(f"Extracted {result['total_pages']} pages")
    print(f"Average confidence: {result['average_confidence']:.1f}%")
    print(f"Text: {result['text'][:500]}...")
else:
    print(f"OCR not available. Missing: {handler.get_missing_dependencies()}")
```

---

## 📦 Dependencies

### Required

| Dependency | Type | Purpose | Install Command |
|------------|------|---------|-----------------|
| **tesseract-ocr** | System | OCR engine | `sudo apt-get install tesseract-ocr` |
| **tesseract-ocr-por** | System | Portuguese language data | `sudo apt-get install tesseract-ocr-por` |
| **Pillow (PIL)** | Python | Image processing | `pip install Pillow` |
| **pytesseract** | Python | Python wrapper for tesseract | `pip install pytesseract` |
| **pdf2image** | Python | PDF to image conversion | `pip install pdf2image` |

### Optional

| Dependency | Purpose | Install Command |
|------------|---------|-----------------|
| **poppler-utils** | PDF rendering (for pdf2image) | `sudo apt-get install poppler-utils` |

---

## 🔍 Features

### 1. Scanned PDF Detection

Automatically detects if a PDF is scanned based on extracted text:

```python
handler = OCRHandler()

# Attempt to extract text with standard PDF tools
extracted_text = extract_text_from_pdf_standard(pdf_path)

# Check if it's scanned
if handler.is_scanned_pdf(extracted_text):
    print("⚠️  Scanned PDF detected - using OCR")
    result = handler.extract_text_from_pdf(pdf_path)
else:
    print("✅ Text-based PDF - using standard extraction")
```

**Detection Logic:**
- Text length < 100 characters → Scanned
- Text is mostly non-alphanumeric (> 70%) → Scanned
- Otherwise → Text-based PDF

### 2. Portuguese Optimization

OCR is optimized for Brazilian Portuguese documents:

```python
# Default: Portuguese
handler = OCRHandler(language="por")

# Can also use English or other languages
handler_en = OCRHandler(language="eng")
handler_pt_br = OCRHandler(language="por+eng")  # Combined
```

### 3. Image Preprocessing

Automatic image enhancement for better OCR accuracy:

- **Grayscale conversion:** Reduces noise
- **Contrast enhancement:** 50% increase
- **Sharpness enhancement:** 30% increase

```python
# Preprocessing is enabled by default
text, confidence = handler.extract_text_from_image(
    "page.png",
    preprocess=True  # Default
)
```

### 4. Confidence Scoring

Each OCR extraction includes a confidence score:

```python
result = handler.extract_text_from_pdf("edital.pdf")

# Overall confidence
print(f"Average confidence: {result['average_confidence']:.1f}%")

# Per-page confidence
for page in result['pages']:
    print(f"Page {page['page']}: {page['confidence']:.1f}%")
```

**Confidence Scale:**
- **90-100%:** Excellent quality
- **70-89%:** Good quality (recommended minimum)
- **50-69%:** Fair quality (may need review)
- **< 50%:** Poor quality (manual review required)

### 5. Graceful Degradation

The handler checks for dependencies and fails gracefully:

```python
from agents.document_structurer.extractors.ocr_handler import get_ocr_status

status = get_ocr_status()

if not status['available']:
    print(f"OCR unavailable. Missing:")
    for dep in status['missing_dependencies']:
        print(f"  - {dep}")
```

---

## 📖 API Reference

### OCRHandler Class

#### `__init__(language: str = "por")`

Initialize OCR handler.

**Parameters:**
- `language` (str): Tesseract language code. Default: "por" (Portuguese)

**Example:**
```python
handler = OCRHandler(language="por")
```

---

#### `is_available() -> bool`

Check if OCR functionality is fully available.

**Returns:**
- `True` if all dependencies installed, `False` otherwise

**Example:**
```python
if handler.is_available():
    # Use OCR
else:
    # Fallback to manual processing
```

---

#### `get_missing_dependencies() -> List[str]`

Get list of missing dependencies.

**Returns:**
- List of dependency names (empty if all installed)

**Example:**
```python
missing = handler.get_missing_dependencies()
if missing:
    print(f"Please install: {', '.join(missing)}")
```

---

#### `is_scanned_pdf(extracted_text: str) -> bool`

Detect if a PDF is likely scanned based on extracted text.

**Parameters:**
- `extracted_text` (str): Text extracted using standard PDF tools

**Returns:**
- `True` if PDF appears scanned, `False` if text-based

**Example:**
```python
text = extract_text_standard(pdf_path)
if handler.is_scanned_pdf(text):
    # Use OCR
```

---

#### `extract_text_from_image(image_path: str, preprocess: bool = True) -> Tuple[str, float]`

Extract text from an image file.

**Parameters:**
- `image_path` (str): Path to image file (PNG, JPG, etc.)
- `preprocess` (bool): Apply preprocessing (default: True)

**Returns:**
- Tuple of `(extracted_text, confidence_score)`

**Example:**
```python
text, conf = handler.extract_text_from_image("page1.png")
print(f"Extracted {len(text)} chars with {conf:.1f}% confidence")
```

---

#### `extract_text_from_pdf(pdf_path: str, max_pages: Optional[int] = None) -> Dict`

Extract text from entire PDF using OCR.

**Parameters:**
- `pdf_path` (str): Path to PDF file
- `max_pages` (int, optional): Limit processing to N pages

**Returns:**
- Dictionary with keys:
  - `text` (str): Combined text from all pages
  - `pages` (List[Dict]): Per-page data (text, confidence, char_count)
  - `average_confidence` (float): Average confidence across pages
  - `total_pages` (int): Number of pages processed

**Example:**
```python
# Process entire PDF
result = handler.extract_text_from_pdf("edital.pdf")

# Process first 10 pages only
result = handler.extract_text_from_pdf("edital.pdf", max_pages=10)
```

---

### Convenience Functions

#### `is_ocr_available() -> bool`

Quick check if OCR is available.

```python
from agents.document_structurer.extractors.ocr_handler import is_ocr_available

if is_ocr_available():
    # Use OCR features
```

---

#### `get_ocr_status() -> Dict`

Get detailed OCR status.

```python
from agents.document_structurer.extractors.ocr_handler import get_ocr_status

status = get_ocr_status()
# {
#     "available": False,
#     "tesseract_installed": False,
#     "pil_installed": True,
#     "pytesseract_installed": True,
#     "missing_dependencies": ["tesseract-ocr (system package)"]
# }
```

---

## 🧪 Testing

### Unit Tests

```bash
python tests/unit/test_ocr_handler.py
```

**Test Coverage:**
- Dependency checking
- Scanned PDF detection (empty, short, garbage, valid text)
- Language configuration
- Confidence thresholds
- Graceful failure without tesseract
- Handler initialization

**Expected Output:**
```
============================================================
OCR Handler - Unit Tests
============================================================

OCR Status:
  Available: ✅ YES / ❌ NO
  Tesseract: ✅ / ❌
  Pillow: ✅ / ❌
  pytesseract: ✅ / ❌

...

============================================================
TEST SUMMARY
============================================================
✅ Passed: 12
❌ Failed: 0
Total: 12
============================================================
```

---

## 🔧 Integration with Document Structurer

### Step 1: Detect Scanned PDF

In the Document Structurer's EXECUTE phase:

```python
from agents.document_structurer.extractors.ocr_handler import OCRHandler

# Extract text with standard tools
text = pdf_processor.extract_text(pdf_path)

# Check if scanned
handler = OCRHandler()
if handler.is_scanned_pdf(text):
    if handler.is_available():
        # Use OCR
        result = handler.extract_text_from_pdf(pdf_path, max_pages=50)
        text = result['text']

        # Log OCR usage
        metadata['ocr_used'] = True
        metadata['ocr_confidence'] = result['average_confidence']
    else:
        # HALT: OCR required but not available
        return {
            "status": "HALT",
            "reason": "Scanned PDF detected but OCR not available",
            "missing_dependencies": handler.get_missing_dependencies()
        }
```

### Step 2: Update HALT Behavior

Replace manual HALT for scanned PDFs with automatic OCR attempt:

**Before (História 2.6):**
```python
if len(text) < 100:
    return HALT("Scanned PDF detected - OCR required")
```

**After (História 2.7):**
```python
if len(text) < 100:
    handler = OCRHandler()
    if handler.is_available():
        result = handler.extract_text_from_pdf(pdf_path)
        text = result['text']
        # Continue processing
    else:
        return HALT(f"OCR required but not available: {handler.get_missing_dependencies()}")
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# Optional: Set custom tesseract path
export TESSERACT_CMD=/usr/local/bin/tesseract

# Optional: Set default language
export OCR_LANGUAGE=por
```

### Custom Configuration

```python
handler = OCRHandler()

# Adjust detection threshold
handler.min_text_length = 50  # Default: 100

# Adjust confidence threshold
handler.confidence_threshold = 80.0  # Default: 70.0
```

---

## 🚨 Troubleshooting

### Issue: "OCR not available"

**Cause:** Missing dependencies

**Solution:**
```bash
# Check status
python -c "from agents.document_structurer.extractors.ocr_handler import get_ocr_status; print(get_ocr_status())"

# Install missing dependencies
sudo apt-get install tesseract-ocr tesseract-ocr-por
pip install Pillow pytesseract pdf2image
```

---

### Issue: "tesseract is not installed"

**Cause:** Tesseract not in PATH

**Solution:**
```bash
# Find tesseract
which tesseract

# If not found, install
sudo apt-get install tesseract-ocr

# Or set custom path
export TESSERACT_CMD=/custom/path/to/tesseract
```

---

### Issue: Low OCR confidence (< 50%)

**Causes:**
- Poor scan quality
- Low resolution
- Skewed/rotated pages
- Complex layouts

**Solutions:**
1. Increase scan DPI (minimum 300 DPI)
2. Pre-process images manually
3. Use higher quality scans
4. Enable preprocessing:
   ```python
   text, conf = handler.extract_text_from_image(path, preprocess=True)
   ```

---

## 📊 Performance

### Processing Speed

| PDF Size | Pages | Resolution | Time | Notes |
|----------|-------|------------|------|-------|
| Small | 1-10 | 300 DPI | ~5-15s | Fast |
| Medium | 11-50 | 300 DPI | ~30-120s | Moderate |
| Large | 51-100 | 300 DPI | ~2-4 min | Slow |
| Very Large | 100+ | 300 DPI | ~5+ min | Use max_pages limit |

**Tip:** For large PDFs, process first N pages only:
```python
result = handler.extract_text_from_pdf(pdf_path, max_pages=50)
```

### Memory Usage

- ~50-100 MB per page at 300 DPI
- Temporary files cleaned automatically
- Processes one page at a time (no bulk memory load)

---

## 🔮 Future Enhancements

- [ ] Multi-language detection (auto-detect document language)
- [ ] Parallel page processing (faster for large PDFs)
- [ ] Advanced preprocessing (deskew, rotation correction)
- [ ] Table detection and extraction
- [ ] Confidence-based re-processing (retry low-confidence pages with different settings)
- [ ] GPU acceleration (if available)

---

## 📚 References

- **Tesseract OCR:** https://github.com/tesseract-ocr/tesseract
- **pytesseract:** https://pypi.org/project/pytesseract/
- **Pillow (PIL):** https://pillow.readthedocs.io/
- **pdf2image:** https://pypi.org/project/pdf2image/
- **Main Agent:** `agents/document_structurer/README.md`

---

**Created:** 2025-11-06
**Version:** 1.0.0
**Status:** ✅ Production Ready (with tesseract installed)
