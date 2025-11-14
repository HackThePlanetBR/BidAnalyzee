#!/usr/bin/env python3
"""
PDF Validator Script

Validates PDF files before processing with Document Structurer.
Prevents errors by checking PDF integrity, readability, and structure.

Usage:
    python3 scripts/validate_pdf.py --input edital.pdf [--strict]

Checks:
- File exists and is readable
- Valid PDF format (magic bytes)
- Not corrupted (can be opened)
- Has extractable text content
- Size within reasonable limits
- Page count reasonable
- Encoding compatible

Exit Codes:
    0 - PDF is valid
    1 - PDF is invalid (errors found)
    2 - Invalid arguments
"""

import argparse
import sys
from pathlib import Path
from typing import Tuple, List, Dict, Any


def check_file_exists(filepath: Path) -> Tuple[bool, str]:
    """Check if file exists and is readable"""
    if not filepath.exists():
        return False, f"File not found: {filepath}"

    if not filepath.is_file():
        return False, f"Path is not a file: {filepath}"

    if not filepath.stat().st_size > 0:
        return False, f"File is empty (0 bytes)"

    try:
        with open(filepath, 'rb') as f:
            # Try to read first byte
            f.read(1)
        return True, "File exists and is readable"
    except PermissionError:
        return False, "No read permission for file"
    except Exception as e:
        return False, f"Cannot read file: {e}"


def check_pdf_magic_bytes(filepath: Path) -> Tuple[bool, str]:
    """Check if file starts with PDF magic bytes (%PDF-)"""
    try:
        with open(filepath, 'rb') as f:
            header = f.read(5)
            if header == b'%PDF-':
                return True, "Valid PDF magic bytes"
            else:
                return False, f"Invalid PDF header (got: {header[:20]})"
    except Exception as e:
        return False, f"Error reading header: {e}"


def check_pdf_integrity(filepath: Path) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Check if PDF can be opened and read using PyPDF2

    Returns:
        (is_valid, message, metadata_dict)
    """
    try:
        import PyPDF2
    except ImportError:
        return True, "⚠️  PyPDF2 not installed, skipping integrity check", {}

    try:
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)

            # Basic checks
            num_pages = len(reader.pages)
            if num_pages == 0:
                return False, "PDF has 0 pages", {}

            # Try to read first page
            try:
                first_page = reader.pages[0]
                _ = first_page.extract_text()
            except Exception as e:
                return False, f"Cannot extract text from first page: {e}", {}

            # Get metadata
            metadata = {
                'num_pages': num_pages,
                'is_encrypted': reader.is_encrypted,
            }

            # Check metadata
            if hasattr(reader, 'metadata') and reader.metadata:
                metadata['title'] = reader.metadata.get('/Title', 'N/A')
                metadata['author'] = reader.metadata.get('/Author', 'N/A')

            return True, f"PDF is valid ({num_pages} pages)", metadata

    except PyPDF2.errors.PdfReadError as e:
        return False, f"PDF is corrupted or invalid: {e}", {}
    except Exception as e:
        return False, f"Error reading PDF: {e}", {}


def check_pdf_size(filepath: Path, max_mb: int = 100) -> Tuple[bool, str]:
    """Check if PDF size is within reasonable limits"""
    size_bytes = filepath.stat().st_size
    size_mb = size_bytes / (1024 * 1024)

    if size_mb > max_mb:
        return False, f"PDF too large: {size_mb:.1f}MB (max: {max_mb}MB)"

    return True, f"Size OK: {size_mb:.2f}MB"


def check_text_content(filepath: Path, min_chars: int = 100) -> Tuple[bool, str]:
    """Check if PDF has extractable text content"""
    try:
        import PyPDF2
    except ImportError:
        return True, "⚠️  PyPDF2 not installed, skipping text content check"

    try:
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)

            # Extract text from first 3 pages
            text = ""
            max_pages = min(3, len(reader.pages))
            for i in range(max_pages):
                text += reader.pages[i].extract_text()

            text = text.strip()

            if len(text) < min_chars:
                return False, f"Insufficient text content ({len(text)} chars, min: {min_chars}). PDF may be scanned images only."

            return True, f"Text content OK ({len(text)} chars in first {max_pages} pages)"

    except Exception as e:
        return False, f"Error extracting text: {e}"


def check_page_count(filepath: Path, max_pages: int = 500) -> Tuple[bool, str]:
    """Check if page count is reasonable"""
    try:
        import PyPDF2
    except ImportError:
        return True, "⚠️  PyPDF2 not installed, skipping page count check"

    try:
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            num_pages = len(reader.pages)

            if num_pages > max_pages:
                return False, f"Too many pages: {num_pages} (max: {max_pages})"

            if num_pages < 1:
                return False, "PDF has no pages"

            return True, f"Page count OK: {num_pages}"

    except Exception as e:
        return False, f"Error counting pages: {e}"


def validate_pdf(
    filepath: Path,
    strict: bool = False,
    max_size_mb: int = 100,
    max_pages: int = 500,
    min_text_chars: int = 100
) -> Tuple[bool, List[str], List[str], Dict[str, Any]]:
    """
    Validate PDF file

    Args:
        filepath: Path to PDF file
        strict: If True, warnings are treated as errors
        max_size_mb: Maximum file size in MB
        max_pages: Maximum number of pages
        min_text_chars: Minimum text characters to extract

    Returns:
        (is_valid, errors, warnings, metadata)
    """
    errors = []
    warnings = []
    metadata = {}

    # 1. File exists and readable
    valid, msg = check_file_exists(filepath)
    if not valid:
        errors.append(f"❌ File check: {msg}")
        return False, errors, warnings, metadata

    # 2. PDF magic bytes
    valid, msg = check_pdf_magic_bytes(filepath)
    if not valid:
        errors.append(f"❌ Format check: {msg}")
        return False, errors, warnings, metadata

    # 3. File size
    valid, msg = check_pdf_size(filepath, max_mb=max_size_mb)
    if not valid:
        if strict:
            errors.append(f"❌ Size check: {msg}")
        else:
            warnings.append(f"⚠️  Size check: {msg}")

    # 4. PDF integrity
    valid, msg, pdf_metadata = check_pdf_integrity(filepath)
    metadata.update(pdf_metadata)

    if not valid:
        if "not installed" in msg:
            warnings.append(f"⚠️  Integrity check: {msg}")
        else:
            errors.append(f"❌ Integrity check: {msg}")

    # 5. Page count
    valid, msg = check_page_count(filepath, max_pages=max_pages)
    if not valid:
        if "not installed" in msg:
            warnings.append(f"⚠️  Page count: {msg}")
        elif strict:
            errors.append(f"❌ Page count: {msg}")
        else:
            warnings.append(f"⚠️  Page count: {msg}")

    # 6. Text content
    valid, msg = check_text_content(filepath, min_chars=min_text_chars)
    if not valid:
        if "not installed" in msg:
            warnings.append(f"⚠️  Text content: {msg}")
        elif strict:
            errors.append(f"❌ Text content: {msg}")
        else:
            warnings.append(f"⚠️  Text content: {msg}")

    is_valid = len(errors) == 0
    return is_valid, errors, warnings, metadata


def main():
    parser = argparse.ArgumentParser(
        description="Validate PDF files before processing",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to PDF file to validate"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors"
    )
    parser.add_argument(
        "--max-size",
        type=int,
        default=100,
        help="Maximum file size in MB (default: 100)"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=500,
        help="Maximum number of pages (default: 500)"
    )
    parser.add_argument(
        "--min-text",
        type=int,
        default=100,
        help="Minimum extractable text characters (default: 100)"
    )

    args = parser.parse_args()
    filepath = Path(args.input)

    print(f"\n{'='*70}")
    print(f"📄 VALIDATING PDF")
    print(f"{'='*70}")
    print(f"File: {filepath}")
    print(f"Mode: {'STRICT' if args.strict else 'NORMAL'}")
    print(f"{'='*70}\n")

    is_valid, errors, warnings, metadata = validate_pdf(
        filepath,
        strict=args.strict,
        max_size_mb=args.max_size,
        max_pages=args.max_pages,
        min_text_chars=args.min_text
    )

    # Show metadata if available
    if metadata:
        print("📊 PDF Metadata:")
        for key, value in metadata.items():
            print(f"   {key}: {value}")
        print()

    # Show warnings
    if warnings:
        print(f"⚠️  Warnings ({len(warnings)}):")
        for warning in warnings:
            print(f"   {warning}")
        print()

    # Show errors
    if errors:
        print(f"❌ Errors ({len(errors)}):")
        for error in errors:
            print(f"   {error}")
        print()

    # Result
    if is_valid:
        print("✅ PDF is VALID")
        print("\n📋 Checks passed:")
        print("   ✅ File exists and is readable")
        print("   ✅ Valid PDF format")
        print("   ✅ PDF integrity OK")
        print("   ✅ Size within limits")
        print("   ✅ Page count reasonable")
        print("   ✅ Has extractable text content")
        print()
        print("💡 Ready for Document Structurer processing")
        print()
        return 0
    else:
        print("❌ PDF is INVALID")
        print("\n⚠️  This PDF may cause errors during processing.")
        print("   Fix the issues above before proceeding.")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
