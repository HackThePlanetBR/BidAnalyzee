# OCR Installation Guide

**Purpose:** Step-by-step guide to install Tesseract OCR and dependencies for the Document Structurer agent.

**Target Systems:** Ubuntu/Debian Linux

---

## 📋 Overview

The Document Structurer uses Tesseract OCR to automatically extract text from scanned/image-based PDF documents. This guide covers installation for all required dependencies.

**Dependencies:**
- Tesseract OCR (system package)
- Portuguese language data (system package)
- Python packages (Pillow, pytesseract, pdf2image)
- Poppler utilities (optional, for PDF rendering)

---

## 🚀 Quick Installation

### Ubuntu / Debian

```bash
# Update package list
sudo apt-get update

# Install Tesseract OCR and Portuguese language pack
sudo apt-get install -y tesseract-ocr tesseract-ocr-por poppler-utils

# Install Python packages
pip install Pillow pytesseract pdf2image
```

### Verify Installation

```bash
# Check Tesseract version
tesseract --version

# Check if Portuguese is available
tesseract --list-langs | grep por

# Test OCR handler
python agents/document_structurer/extractors/ocr_handler.py
```

**Expected Output:**
```
============================================================
OCR Handler - Status Check
============================================================

OCR Available: ✅ YES

Dependency Status:
  Tesseract: ✅
  Pillow (PIL): ✅
  pytesseract: ✅

✅ All dependencies installed - OCR ready!
============================================================
```

---

## 📦 Detailed Installation

### Step 1: System Packages

#### Install Tesseract OCR

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr
```

**Verify:**
```bash
tesseract --version
# Should output: tesseract 4.x.x or 5.x.x
```

---

#### Install Portuguese Language Data

```bash
sudo apt-get install -y tesseract-ocr-por
```

**Verify:**
```bash
tesseract --list-langs
# Should include: por (Portuguese)
```

---

#### Install Poppler Utils (for PDF→Image conversion)

```bash
sudo apt-get install -y poppler-utils
```

**Verify:**
```bash
pdftoppm -v
# Should output: pdftoppm version X.X.X
```

---

### Step 2: Python Packages

#### Install via pip

```bash
pip install Pillow pytesseract pdf2image
```

**Verify:**
```bash
python -c "import PIL; print(f'Pillow {PIL.__version__}')"
python -c "import pytesseract; print('pytesseract OK')"
python -c "import pdf2image; print('pdf2image OK')"
```

---

### Step 3: Verify Complete Installation

```bash
cd /path/to/BidAnalyzee
python agents/document_structurer/extractors/ocr_handler.py
```

**Success Output:**
```
OCR Available: ✅ YES
✅ All dependencies installed - OCR ready!
```

**Failure Output:**
```
OCR Available: ❌ NO
⚠️ Missing Dependencies:
  - tesseract-ocr (system package)
```

---

## 🐳 Docker Installation

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-por \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir \
    Pillow \
    pytesseract \
    pdf2image

# Copy application
WORKDIR /app
COPY . /app

# Verify OCR installation
RUN python agents/document_structurer/extractors/ocr_handler.py
```

### Build and Run

```bash
docker build -t bidanalyzee .
docker run -it bidanalyzee python agents/document_structurer/extractors/ocr_handler.py
```

---

## 🔧 Alternative Installation Methods

### Using Conda

```bash
conda create -n bidanalyzee python=3.11
conda activate bidanalyzee

# Install tesseract via conda
conda install -c conda-forge tesseract

# Install Python packages
pip install Pillow pytesseract pdf2image
```

### Using Homebrew (macOS)

```bash
# Install tesseract
brew install tesseract tesseract-lang

# Install Python packages
pip install Pillow pytesseract pdf2image
```

---

## 🌍 Additional Languages

### Install Additional Language Packs

```bash
# Spanish
sudo apt-get install tesseract-ocr-spa

# English (usually pre-installed)
sudo apt-get install tesseract-ocr-eng

# List all available languages
apt-cache search tesseract-ocr-
```

### Use Multiple Languages

```python
from agents.document_structurer.extractors.ocr_handler import OCRHandler

# Portuguese + English combined
handler = OCRHandler(language="por+eng")

# Spanish only
handler_es = OCRHandler(language="spa")
```

---

## 🚨 Troubleshooting

### Issue: `tesseract: command not found`

**Cause:** Tesseract not installed or not in PATH

**Solution:**
```bash
# Check if installed
which tesseract

# If not found, install
sudo apt-get install tesseract-ocr

# Add to PATH if needed
export PATH=$PATH:/usr/bin
```

---

### Issue: `Error opening data file por.traineddata`

**Cause:** Portuguese language pack not installed

**Solution:**
```bash
# Install Portuguese language pack
sudo apt-get install tesseract-ocr-por

# Verify installation
ls /usr/share/tesseract-ocr/4.00/tessdata/ | grep por
# Should show: por.traineddata
```

---

### Issue: `ModuleNotFoundError: No module named 'PIL'`

**Cause:** Pillow not installed

**Solution:**
```bash
pip install Pillow

# If using system Python, may need
sudo apt-get install python3-pil
```

---

### Issue: `pdf2image.exceptions.PDFInfoNotInstalledError`

**Cause:** poppler-utils not installed

**Solution:**
```bash
sudo apt-get install poppler-utils

# Verify
which pdftoppm
```

---

### Issue: Low OCR accuracy for Portuguese text

**Solutions:**

1. **Verify correct language pack:**
   ```bash
   tesseract --list-langs | grep por
   ```

2. **Increase DPI for PDF conversion:**
   ```python
   # In code, if needed
   from pdf2image import convert_from_path
   images = convert_from_path(pdf_path, dpi=400)  # Higher DPI
   ```

3. **Use language combinations:**
   ```python
   handler = OCRHandler(language="por+eng")
   ```

---

## ✅ Post-Installation Checklist

After installation, verify:

- [ ] Tesseract version 4.0+ installed
  ```bash
  tesseract --version
  ```

- [ ] Portuguese language pack available
  ```bash
  tesseract --list-langs | grep por
  ```

- [ ] Poppler utils installed
  ```bash
  pdftoppm -v
  ```

- [ ] Python packages installed
  ```bash
  pip list | grep -E "(Pillow|pytesseract|pdf2image)"
  ```

- [ ] OCR handler reports "available"
  ```bash
  python agents/document_structurer/extractors/ocr_handler.py
  ```

- [ ] Unit tests pass
  ```bash
  python tests/unit/test_ocr_handler.py
  ```

---

## 📊 System Requirements

### Minimum

- **OS:** Ubuntu 18.04+ / Debian 10+
- **Python:** 3.8+
- **RAM:** 2 GB
- **Disk:** 500 MB (for tesseract + language data)

### Recommended

- **OS:** Ubuntu 22.04+ / Debian 12+
- **Python:** 3.11+
- **RAM:** 4 GB (for processing large PDFs)
- **Disk:** 1 GB

---

## 🔗 Additional Resources

- **Tesseract Official Docs:** https://tesseract-ocr.github.io/
- **pytesseract GitHub:** https://github.com/madmaze/pytesseract
- **pdf2image GitHub:** https://github.com/Belval/pdf2image
- **Language Data Downloads:** https://github.com/tesseract-ocr/tessdata

---

## 💡 Tips

1. **Use virtual environments** to avoid conflicts:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install Pillow pytesseract pdf2image
   ```

2. **Cache OCR results** for repeated processing of same documents

3. **Limit max_pages** for large PDFs to improve performance:
   ```python
   result = handler.extract_text_from_pdf(pdf_path, max_pages=50)
   ```

4. **Monitor OCR confidence** and flag low-confidence extractions for review

---

**Created:** 2025-11-06
**Version:** 1.0.0
**Status:** ✅ Complete
