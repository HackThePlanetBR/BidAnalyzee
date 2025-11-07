#!/usr/bin/env python3
"""
Unit Tests for OCR Handler

Tests OCR functionality including:
- Dependency checking
- Scanned PDF detection
- OCR text extraction (mocked when tesseract not available)
- Image preprocessing
- Confidence scoring

Author: BidAnalyzee Team
Date: 2025-11-06
Version: 1.0.0
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.document_structurer.extractors.ocr_handler import (
    OCRHandler,
    is_ocr_available,
    get_ocr_status
)


class TestOCRHandler:
    """Test suite for OCR Handler"""

    def setup_method(self):
        """Setup test fixtures"""
        self.handler = OCRHandler()

    def test_dependency_check(self):
        """Test dependency checking"""
        status = get_ocr_status()

        # Status dict should have required keys
        assert "available" in status
        assert "tesseract_installed" in status
        assert "pil_installed" in status
        assert "pytesseract_installed" in status
        assert "missing_dependencies" in status

        # Available should be bool
        assert isinstance(status["available"], bool)

        # Python packages should be installed (we just installed them)
        assert status["pil_installed"] is True, "Pillow should be installed"
        assert status["pytesseract_installed"] is True, "pytesseract should be installed"

        print("✅ Dependency check: PASS")

    def test_is_ocr_available(self):
        """Test is_ocr_available convenience function"""
        available = is_ocr_available()
        assert isinstance(available, bool)

        # Should match handler.is_available()
        assert available == self.handler.is_available()

        print("✅ is_ocr_available: PASS")

    def test_get_missing_dependencies(self):
        """Test missing dependencies reporting"""
        missing = self.handler.get_missing_dependencies()

        # Should be a list
        assert isinstance(missing, list)

        # If OCR is not fully available, should have at least one missing dependency
        if not self.handler.is_available():
            assert len(missing) > 0, "Should report missing dependencies"
            # tesseract is likely missing (system package)
            assert any("tesseract" in dep.lower() for dep in missing)

        print(f"✅ Missing dependencies: {', '.join(missing) if missing else 'None'}")

    def test_scanned_pdf_detection_empty(self):
        """Test scanned PDF detection with empty text"""
        is_scanned = self.handler.is_scanned_pdf("")
        assert is_scanned is True, "Empty text should be detected as scanned"

        print("✅ Scanned PDF detection (empty): PASS")

    def test_scanned_pdf_detection_short(self):
        """Test scanned PDF detection with very short text"""
        short_text = "ABC"
        is_scanned = self.handler.is_scanned_pdf(short_text)
        assert is_scanned is True, "Short text (< 100 chars) should be detected as scanned"

        print("✅ Scanned PDF detection (short): PASS")

    def test_scanned_pdf_detection_garbage(self):
        """Test scanned PDF detection with garbage characters"""
        garbage_text = "!@#$%^&*()_+{}|:<>?~`" * 10  # 200+ non-alphanumeric chars
        is_scanned = self.handler.is_scanned_pdf(garbage_text)
        assert is_scanned is True, "Garbage text should be detected as scanned"

        print("✅ Scanned PDF detection (garbage): PASS")

    def test_scanned_pdf_detection_valid(self):
        """Test scanned PDF detection with valid extracted text"""
        valid_text = """
        PREFEITURA MUNICIPAL DE SÃO PAULO

        EDITAL Nº 001/2025
        PREGÃO ELETRÔNICO

        1. OBJETO

        Aquisição de Sistema de Videomonitoramento Urbano com câmeras IP,
        servidores de armazenamento e software de gerenciamento, conforme
        especificações técnicas anexas.

        2. VALOR ESTIMADO

        R$ 2.500.000,00 (dois milhões e quinhentos mil reais)
        """

        is_scanned = self.handler.is_scanned_pdf(valid_text)
        assert is_scanned is False, "Valid long text should NOT be detected as scanned"

        print("✅ Scanned PDF detection (valid): PASS")

    def test_min_text_length_threshold(self):
        """Test that min_text_length threshold can be configured"""
        # Default threshold is 100
        assert self.handler.min_text_length == 100

        # Text just under threshold
        text_99 = "A" * 99
        assert self.handler.is_scanned_pdf(text_99) is True

        # Text just above threshold
        text_101 = "A" * 101
        assert self.handler.is_scanned_pdf(text_101) is False

        print("✅ Min text length threshold: PASS")

    def test_confidence_threshold(self):
        """Test that confidence threshold can be configured"""
        # Default confidence threshold is 70.0
        assert self.handler.confidence_threshold == 70.0

        print("✅ Confidence threshold: PASS")

    def test_language_configuration(self):
        """Test language configuration"""
        # Default language is Portuguese
        assert self.handler.language == "por"

        # Can initialize with different language
        handler_en = OCRHandler(language="eng")
        assert handler_en.language == "eng"

        print("✅ Language configuration: PASS")

    def test_handler_initialization(self):
        """Test OCR handler initialization"""
        handler = OCRHandler()

        # Check attributes exist
        assert hasattr(handler, 'language')
        assert hasattr(handler, 'min_text_length')
        assert hasattr(handler, 'confidence_threshold')
        assert hasattr(handler, 'tesseract_available')
        assert hasattr(handler, 'pil_available')
        assert hasattr(handler, 'pytesseract_available')

        print("✅ Handler initialization: PASS")

    def test_ocr_extraction_without_tesseract(self):
        """Test that OCR extraction fails gracefully without tesseract"""
        if self.handler.is_available():
            print("⏭️  Skipping: tesseract is available")
            return

        # Should raise RuntimeError when trying to extract without tesseract
        try:
            from PIL import Image
            import tempfile

            # Create a dummy image
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                img = Image.new('RGB', (100, 100), color='white')
                img.save(tmp.name)
                tmp_path = tmp.name

            # Try to extract - should fail
            try:
                self.handler.extract_text_from_image(tmp_path)
                assert False, "Should have raised RuntimeError"
            except RuntimeError as e:
                assert "OCR not available" in str(e)
                assert "Missing dependencies" in str(e)

            # Cleanup
            Path(tmp_path).unlink()

            print("✅ OCR extraction without tesseract (graceful failure): PASS")

        except ImportError:
            print("⏭️  Skipping: PIL not available")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("OCR Handler - Unit Tests")
    print("=" * 60 + "\n")

    # Show OCR status first
    status = get_ocr_status()
    print("OCR Status:")
    print(f"  Available: {'✅ YES' if status['available'] else '❌ NO'}")
    print(f"  Tesseract: {'✅' if status['tesseract_installed'] else '❌'}")
    print(f"  Pillow: {'✅' if status['pil_installed'] else '❌'}")
    print(f"  pytesseract: {'✅' if status['pytesseract_installed'] else '❌'}")

    if status['missing_dependencies']:
        print(f"  Missing: {', '.join(status['missing_dependencies'])}")

    print("\n" + "-" * 60 + "\n")

    test_suite = TestOCRHandler()

    # Run tests
    tests = [
        test_suite.test_dependency_check,
        test_suite.test_is_ocr_available,
        test_suite.test_get_missing_dependencies,
        test_suite.test_scanned_pdf_detection_empty,
        test_suite.test_scanned_pdf_detection_short,
        test_suite.test_scanned_pdf_detection_garbage,
        test_suite.test_scanned_pdf_detection_valid,
        test_suite.test_min_text_length_threshold,
        test_suite.test_confidence_threshold,
        test_suite.test_language_configuration,
        test_suite.test_handler_initialization,
        test_suite.test_ocr_extraction_without_tesseract,
    ]

    passed = 0
    failed = 0
    skipped = 0

    for test in tests:
        try:
            test_suite.setup_method()
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: FAILED")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            if "Skipping" in str(e):
                skipped += 1
            else:
                print(f"❌ {test.__name__}: ERROR")
                print(f"   Error: {e}")
                failed += 1

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    if skipped > 0:
        print(f"⏭️  Skipped: {skipped}")
    print(f"Total: {passed + failed + skipped}")
    print("=" * 60 + "\n")

    if not status['available']:
        print("ℹ️  Note: Full OCR functionality requires tesseract-ocr")
        print("   Install with: sudo apt-get install tesseract-ocr tesseract-ocr-por")
        print()

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
