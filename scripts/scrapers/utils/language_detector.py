"""
Language Detection Utility

Detects if content is in English using multiple strategies:
1. URL pattern analysis (/en/, /pt/, etc.)
2. Probabilistic language detection (langdetect)
3. English stop words frequency analysis (fallback)
"""

import re
from typing import Optional, Tuple
from urllib.parse import urlparse
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Common English stop words for fallback detection
ENGLISH_STOP_WORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
    'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me'
}

# Language codes in URLs
LANGUAGE_URL_PATTERNS = {
    'en': ['en', 'en-us', 'en-gb', 'english'],
    'pt': ['pt', 'pt-br', 'pt-pt', 'portugues', 'portuguese'],
    'es': ['es', 'es-es', 'es-mx', 'espanol', 'spanish'],
    'fr': ['fr', 'fr-fr', 'francais', 'french'],
    'de': ['de', 'de-de', 'deutsch', 'german'],
    'it': ['it', 'it-it', 'italiano', 'italian'],
    'ja': ['ja', 'jp', 'japanese'],
    'zh': ['zh', 'cn', 'zh-cn', 'chinese']
}


def detect_language_from_url(url: str) -> Optional[str]:
    """
    Detect language from URL patterns.

    Looks for language indicators in URL path segments:
    - /en/, /pt/, /fr/, etc.
    - /en-us/, /pt-br/, etc.
    - Language subdomains

    Args:
        url: URL to analyze

    Returns:
        Language code ('en', 'pt', etc.) or None if not detected

    Example:
        >>> detect_language_from_url("https://help.genetec.cloud/en/docs")
        'en'
        >>> detect_language_from_url("https://help.genetec.cloud/pt-br/docs")
        'pt'
    """
    url_lower = url.lower()

    # Parse URL
    parsed = urlparse(url_lower)
    path = parsed.path
    hostname = parsed.hostname or ''

    # Check path segments
    path_segments = [seg for seg in path.split('/') if seg]

    # Look for language codes in path
    for lang_code, patterns in LANGUAGE_URL_PATTERNS.items():
        for pattern in patterns:
            # Check if any path segment matches
            if any(segment == pattern for segment in path_segments):
                return lang_code
            # Check if subdomain matches
            if hostname.startswith(f"{pattern}."):
                return lang_code

    return None


def is_english_content(
    text: str,
    threshold: float = 0.7,
    min_length: int = 100,
    use_url: Optional[str] = None
) -> Tuple[bool, float, str]:
    """
    Detect if text is primarily English using multiple strategies.

    Detection strategies (in order):
    1. URL pattern check (if URL provided)
    2. Probabilistic detection using langdetect library
    3. Fallback: English stop words frequency analysis

    Args:
        text: Content to analyze
        threshold: Minimum confidence (0.0-1.0) for probabilistic detection
        min_length: Minimum text length for reliable detection
        use_url: Optional URL to check for language indicators

    Returns:
        Tuple of (is_english, confidence, detection_method)

    Example:
        >>> text = "This is an example of English text."
        >>> is_en, conf, method = is_english_content(text)
        >>> print(f"English: {is_en}, Confidence: {conf:.2f}, Method: {method}")
        English: True, Confidence: 0.95, Method: langdetect
    """
    # Strategy 1: Check URL if provided
    if use_url:
        url_lang = detect_language_from_url(use_url)
        if url_lang:
            is_en = (url_lang == 'en')
            logger.debug(f"Language detected from URL: {url_lang}")
            return is_en, 1.0, 'url_pattern'

    # Check minimum length
    if len(text) < min_length:
        logger.warning(f"Text too short for reliable detection ({len(text)} < {min_length} chars)")
        # Still try, but with lower confidence
        return _detect_with_stopwords(text, threshold * 0.5)

    # Strategy 2: Use langdetect library
    try:
        import langdetect
        from langdetect import DetectorFactory

        # Set seed for reproducible results
        DetectorFactory.seed = 0

        # Detect language with confidence
        detected_lang = langdetect.detect(text)

        # Get confidence scores for all languages
        lang_probs = langdetect.detect_langs(text)

        # Find English probability
        en_confidence = 0.0
        for lang_prob in lang_probs:
            if lang_prob.lang == 'en':
                en_confidence = lang_prob.prob
                break

        is_en = (detected_lang == 'en' and en_confidence >= threshold)

        logger.debug(f"Langdetect result: {detected_lang}, EN confidence: {en_confidence:.2f}")

        return is_en, en_confidence, 'langdetect'

    except ImportError:
        logger.warning("langdetect library not available, using fallback method")
        return _detect_with_stopwords(text, threshold)
    except Exception as e:
        logger.warning(f"Langdetect failed: {e}, using fallback method")
        return _detect_with_stopwords(text, threshold)


def _detect_with_stopwords(text: str, threshold: float) -> Tuple[bool, float, str]:
    """
    Fallback method: Detect English by counting stop words frequency.

    Args:
        text: Text to analyze
        threshold: Minimum ratio of English stop words

    Returns:
        Tuple of (is_english, confidence, method)
    """
    # Normalize text
    text_lower = text.lower()

    # Remove punctuation and split into words
    words = re.findall(r'\b[a-z]+\b', text_lower)

    if not words:
        return False, 0.0, 'stopwords_fallback'

    # Count English stop words
    en_stopwords_count = sum(1 for word in words if word in ENGLISH_STOP_WORDS)

    # Calculate ratio
    total_words = len(words)
    en_ratio = en_stopwords_count / total_words if total_words > 0 else 0.0

    is_en = en_ratio >= threshold

    logger.debug(f"Stop words analysis: {en_stopwords_count}/{total_words} = {en_ratio:.2f}")

    return is_en, en_ratio, 'stopwords_fallback'


def validate_english_content(
    text: str,
    url: Optional[str] = None,
    min_confidence: float = 0.7,
    min_length: int = 100
) -> Tuple[bool, str]:
    """
    Validate that content is in English with detailed reason.

    Args:
        text: Content to validate
        url: Optional URL for language detection
        min_confidence: Minimum confidence threshold
        min_length: Minimum text length

    Returns:
        Tuple of (is_valid, reason_message)

    Example:
        >>> is_valid, reason = validate_english_content(text, url)
        >>> if not is_valid:
        ...     print(f"Content rejected: {reason}")
    """
    if not text or len(text.strip()) < 10:
        return False, "Content is empty or too short"

    is_en, confidence, method = is_english_content(
        text,
        threshold=min_confidence,
        min_length=min_length,
        use_url=url
    )

    if is_en:
        return True, f"English detected (confidence: {confidence:.2f}, method: {method})"
    else:
        return False, f"Non-English content detected (confidence: {confidence:.2f}, method: {method})"


def get_content_language(
    text: str,
    url: Optional[str] = None
) -> Tuple[str, float, str]:
    """
    Get the detected language of content.

    Args:
        text: Content to analyze
        url: Optional URL for language detection

    Returns:
        Tuple of (language_code, confidence, detection_method)

    Example:
        >>> lang, conf, method = get_content_language(text)
        >>> print(f"Language: {lang}")
    """
    # Check URL first
    if url:
        url_lang = detect_language_from_url(url)
        if url_lang:
            return url_lang, 1.0, 'url_pattern'

    # Use langdetect
    try:
        import langdetect
        from langdetect import DetectorFactory

        DetectorFactory.seed = 0
        detected_lang = langdetect.detect(text)

        # Get confidence
        lang_probs = langdetect.detect_langs(text)
        confidence = 0.0

        for lang_prob in lang_probs:
            if lang_prob.lang == detected_lang:
                confidence = lang_prob.prob
                break

        return detected_lang, confidence, 'langdetect'

    except Exception as e:
        logger.warning(f"Language detection failed: {e}")
        return 'unknown', 0.0, 'error'
