#!/usr/bin/env python3
"""
OCR Handler for Document Structurer

Provides OCR capabilities for scanned/image-based PDF documents.
Uses Tesseract OCR with Portuguese language optimization.

Author: BidAnalyzee Team
Date: 2025-11-06
Version: 1.0.0
"""

import os
import subprocess
import shutil
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
from pathlib import Path
import tempfile

if TYPE_CHECKING:
    from PIL import Image

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None  # Fallback

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False


class OCRHandler:
    """
    Handles OCR processing for scanned PDF documents.

    Features:
    - Automatic scanned PDF detection
    - Portuguese language optimization
    - Image preprocessing (deskew, denoise, enhance)
    - Confidence scoring
    - Graceful degradation when OCR unavailable
    """

    def __init__(self, language: str = "por"):
        """
        Initialize OCR handler.

        Args:
            language: Tesseract language code (default: "por" for Portuguese)
        """
        self.language = language
        self.min_text_length = 100  # Threshold for scanned PDF detection
        self.confidence_threshold = 70.0  # Minimum OCR confidence

        # Check dependencies
        self.tesseract_available = self._check_tesseract()
        self.pil_available = PIL_AVAILABLE
        self.pytesseract_available = PYTESSERACT_AVAILABLE

        if self.tesseract_available and self.pytesseract_available:
            # Configure pytesseract
            tesseract_cmd = shutil.which("tesseract")
            if tesseract_cmd:
                pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def _check_tesseract(self) -> bool:
        """
        Check if Tesseract OCR is installed and available.

        Returns:
            True if tesseract is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["tesseract", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def is_available(self) -> bool:
        """
        Check if OCR functionality is fully available.

        Returns:
            True if all dependencies are installed
        """
        return (
            self.tesseract_available and
            self.pil_available and
            self.pytesseract_available
        )

    def get_missing_dependencies(self) -> List[str]:
        """
        Get list of missing dependencies.

        Returns:
            List of missing dependency names
        """
        missing = []

        if not self.tesseract_available:
            missing.append("tesseract-ocr (system package)")

        if not self.pil_available:
            missing.append("Pillow (pip install Pillow)")

        if not self.pytesseract_available:
            missing.append("pytesseract (pip install pytesseract)")

        return missing

    def is_scanned_pdf(self, extracted_text: str) -> bool:
        """
        Detect if a PDF is likely scanned (image-based) based on extracted text.

        A PDF is considered scanned if:
        - Extracted text length < min_text_length (default 100 chars)
        - OR text is mostly whitespace/garbage

        Args:
            extracted_text: Text extracted from PDF using standard methods

        Returns:
            True if PDF appears to be scanned, False otherwise
        """
        if not extracted_text:
            return True

        # Remove whitespace and check length
        clean_text = extracted_text.strip()

        if len(clean_text) < self.min_text_length:
            return True

        # Check if text is mostly non-alphanumeric (garbage from image encoding)
        alphanumeric_count = sum(c.isalnum() for c in clean_text)
        if len(clean_text) > 0 and (alphanumeric_count / len(clean_text)) < 0.3:
            return True

        return False

    def extract_text_from_image(
        self,
        image_path: str,
        preprocess: bool = True
    ) -> Tuple[str, float]:
        """
        Extract text from an image file using OCR.

        Args:
            image_path: Path to image file
            preprocess: Whether to preprocess image before OCR

        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        if not self.is_available():
            raise RuntimeError(
                f"OCR not available. Missing dependencies: {', '.join(self.get_missing_dependencies())}"
            )

        try:
            # Open image
            image = Image.open(image_path)

            # Preprocess if requested
            if preprocess:
                image = self._preprocess_image(image)

            # Configure OCR
            config = f'--oem 3 --psm 6 -l {self.language}'

            # Extract text
            text = pytesseract.image_to_string(image, config=config)

            # Get confidence data
            confidence = self._calculate_confidence(image, config)

            return text.strip(), confidence

        except Exception as e:
            raise RuntimeError(f"OCR extraction failed: {str(e)}")

    def _preprocess_image(self, image: "Image.Image") -> "Image.Image":
        """
        Preprocess image to improve OCR accuracy.

        Steps:
        - Convert to grayscale
        - Increase contrast
        - Denoise (if needed)

        Args:
            image: PIL Image object

        Returns:
            Preprocessed PIL Image
        """
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')

        # Increase contrast using point transformation
        # Enhance contrast by mapping values
        from PIL import ImageEnhance

        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)  # 50% more contrast

        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.3)

        return image

    def _calculate_confidence(self, image: "Image.Image", config: str) -> float:
        """
        Calculate OCR confidence score.

        Uses Tesseract's confidence data for each word and averages them.

        Args:
            image: PIL Image object
            config: Tesseract config string

        Returns:
            Average confidence score (0.0-100.0)
        """
        try:
            # Get detailed OCR data
            data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)

            # Extract confidence scores (excluding -1 which means no text)
            confidences = [
                float(conf) for conf in data['conf']
                if conf != -1
            ]

            if not confidences:
                return 0.0

            return sum(confidences) / len(confidences)

        except Exception:
            # If confidence calculation fails, return 0
            return 0.0

    def extract_text_from_pdf_page(
        self,
        pdf_path: str,
        page_number: int
    ) -> Tuple[str, float]:
        """
        Extract text from a specific PDF page using OCR.

        This method:
        1. Converts PDF page to image
        2. Applies OCR to extract text
        3. Returns text and confidence

        Args:
            pdf_path: Path to PDF file
            page_number: Page number (0-indexed)

        Returns:
            Tuple of (extracted_text, confidence_score)

        Note:
            Requires pdf2image library (not included by default)
        """
        try:
            from pdf2image import convert_from_path
        except ImportError:
            raise RuntimeError(
                "pdf2image library required for PDF OCR. "
                "Install with: pip install pdf2image"
            )

        if not self.is_available():
            raise RuntimeError(
                f"OCR not available. Missing dependencies: {', '.join(self.get_missing_dependencies())}"
            )

        with tempfile.TemporaryDirectory() as temp_dir:
            # Convert specific page to image
            images = convert_from_path(
                pdf_path,
                first_page=page_number + 1,
                last_page=page_number + 1,
                dpi=300  # High DPI for better OCR
            )

            if not images:
                return "", 0.0

            # Save to temp file
            image = images[0]
            temp_image_path = Path(temp_dir) / f"page_{page_number}.png"
            image.save(temp_image_path, "PNG")

            # Extract text
            return self.extract_text_from_image(str(temp_image_path))

    def extract_text_from_pdf(
        self,
        pdf_path: str,
        max_pages: Optional[int] = None
    ) -> Dict[str, any]:
        """
        Extract text from entire PDF using OCR.

        Args:
            pdf_path: Path to PDF file
            max_pages: Maximum number of pages to process (None = all)

        Returns:
            Dictionary with:
            - text: Combined text from all pages
            - pages: List of dicts with page-level data
            - average_confidence: Average confidence across all pages
            - total_pages: Total pages processed
        """
        try:
            from pdf2image import convert_from_path
        except ImportError:
            raise RuntimeError(
                "pdf2image library required for PDF OCR. "
                "Install with: pip install pdf2image"
            )

        if not self.is_available():
            raise RuntimeError(
                f"OCR not available. Missing dependencies: {', '.join(self.get_missing_dependencies())}"
            )

        with tempfile.TemporaryDirectory() as temp_dir:
            # Convert PDF to images
            if max_pages:
                images = convert_from_path(pdf_path, dpi=300, last_page=max_pages)
            else:
                images = convert_from_path(pdf_path, dpi=300)

            all_text = []
            page_data = []
            confidences = []

            for i, image in enumerate(images):
                # Save to temp file
                temp_image_path = Path(temp_dir) / f"page_{i}.png"
                image.save(temp_image_path, "PNG")

                # Extract text
                text, confidence = self.extract_text_from_image(str(temp_image_path))

                all_text.append(text)
                confidences.append(confidence)

                page_data.append({
                    "page": i + 1,
                    "text": text,
                    "confidence": confidence,
                    "char_count": len(text)
                })

            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            return {
                "text": "\n\n".join(all_text),
                "pages": page_data,
                "average_confidence": avg_confidence,
                "total_pages": len(images)
            }


# Convenience functions

def is_ocr_available() -> bool:
    """
    Check if OCR functionality is available.

    Returns:
        True if OCR can be used
    """
    handler = OCRHandler()
    return handler.is_available()


def get_ocr_status() -> Dict[str, any]:
    """
    Get detailed OCR availability status.

    Returns:
        Dictionary with status information
    """
    handler = OCRHandler()

    return {
        "available": handler.is_available(),
        "tesseract_installed": handler.tesseract_available,
        "pil_installed": handler.pil_available,
        "pytesseract_installed": handler.pytesseract_available,
        "missing_dependencies": handler.get_missing_dependencies()
    }


def extract_text_with_ocr(pdf_path: str, max_pages: Optional[int] = None) -> Dict[str, any]:
    """
    Convenience function to extract text from PDF using OCR.

    Args:
        pdf_path: Path to PDF file
        max_pages: Maximum pages to process

    Returns:
        Dictionary with extracted text and metadata
    """
    handler = OCRHandler()
    return handler.extract_text_from_pdf(pdf_path, max_pages)


if __name__ == "__main__":
    # Example usage and status check
    print("=" * 60)
    print("OCR Handler - Status Check")
    print("=" * 60)

    status = get_ocr_status()

    print(f"\nOCR Available: {'✅ YES' if status['available'] else '❌ NO'}")
    print(f"\nDependency Status:")
    print(f"  Tesseract: {'✅' if status['tesseract_installed'] else '❌'}")
    print(f"  Pillow (PIL): {'✅' if status['pil_installed'] else '❌'}")
    print(f"  pytesseract: {'✅' if status['pytesseract_installed'] else '❌'}")

    if status['missing_dependencies']:
        print(f"\n⚠️ Missing Dependencies:")
        for dep in status['missing_dependencies']:
            print(f"  - {dep}")

        print("\nInstallation Instructions:")
        print("  System packages:")
        print("    sudo apt-get install tesseract-ocr tesseract-ocr-por")
        print("\n  Python packages:")
        print("    pip install Pillow pytesseract pdf2image")
    else:
        print("\n✅ All dependencies installed - OCR ready!")

    print("=" * 60)
