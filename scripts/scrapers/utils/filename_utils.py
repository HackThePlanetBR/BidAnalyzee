"""
Filename Utilities

Creates filesystem-safe, unique filenames for scraped documents.
"""

import re
import hashlib
from typing import Optional
from pathlib import Path
import unicodedata


def create_safe_filename(
    title: str,
    url: str,
    max_length: int = 100,
    add_hash: bool = True,
    extension: str = '.md'
) -> str:
    """
    Create a filesystem-safe, unique filename from title and URL.

    Strategy:
    1. Sanitize title (remove special chars, normalize unicode)
    2. Convert to lowercase, replace spaces with hyphens
    3. Limit length to max_length
    4. Add short hash of URL for uniqueness (optional)
    5. Add extension

    Args:
        title: Document title
        url: Source URL (used for hash uniqueness)
        max_length: Maximum filename length (excluding extension)
        add_hash: Whether to add URL hash for uniqueness
        extension: File extension (default: '.md')

    Returns:
        Safe filename string

    Example:
        >>> filename = create_safe_filename(
        ...     "API Authentication Guide",
        ...     "https://help.genetec.cloud/en/api/auth.html"
        ... )
        >>> print(filename)
        api-authentication-guide-a3f2d1.md
    """
    # Normalize unicode characters
    title_normalized = unicodedata.normalize('NFKD', title)
    title_ascii = title_normalized.encode('ascii', 'ignore').decode('ascii')

    # Convert to lowercase
    safe_title = title_ascii.lower()

    # Remove special characters (keep only alphanumeric, spaces, and hyphens)
    safe_title = re.sub(r'[^\w\s-]', '', safe_title)

    # Replace multiple spaces/underscores with single hyphen
    safe_title = re.sub(r'[\s_]+', '-', safe_title)

    # Replace multiple hyphens with single hyphen
    safe_title = re.sub(r'-+', '-', safe_title)

    # Remove leading/trailing hyphens
    safe_title = safe_title.strip('-')

    # If title is empty after sanitization, use fallback
    if not safe_title:
        safe_title = 'document'

    # Add hash for uniqueness
    if add_hash:
        # Create short hash from URL
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()[:6]
        hash_suffix = f"-{url_hash}"
    else:
        hash_suffix = ""

    # Calculate available length for title (accounting for hash and extension)
    hash_length = len(hash_suffix)
    ext_length = len(extension)
    available_length = max_length - hash_length - ext_length

    # Truncate title if needed
    if len(safe_title) > available_length:
        safe_title = safe_title[:available_length].rstrip('-')

    # Combine parts
    filename = f"{safe_title}{hash_suffix}{extension}"

    return filename


def sanitize_filename(filename: str, replacement: str = '-') -> str:
    """
    Sanitize a filename by removing/replacing unsafe characters.

    Args:
        filename: Original filename
        replacement: Character to replace unsafe chars with

    Returns:
        Sanitized filename

    Example:
        >>> sanitize_filename("my/file:name.txt")
        'my-file-name.txt'
    """
    # Characters not allowed in filenames (Windows + Unix)
    unsafe_chars = r'[<>:"/\\|?*\x00-\x1f]'

    # Replace unsafe characters
    safe = re.sub(unsafe_chars, replacement, filename)

    # Remove leading/trailing dots and spaces (Windows)
    safe = safe.strip('. ')

    # Replace multiple replacement chars with single
    if replacement:
        pattern = re.escape(replacement) + '+'
        safe = re.sub(pattern, replacement, safe)

    return safe


def ensure_unique_filename(
    filepath: Path,
    max_attempts: int = 1000
) -> Path:
    """
    Ensure filename is unique by adding counter if file exists.

    Args:
        filepath: Desired file path
        max_attempts: Maximum number of attempts to find unique name

    Returns:
        Unique file path

    Raises:
        ValueError: If unable to find unique name after max_attempts

    Example:
        >>> path = Path("output/document.md")
        >>> unique = ensure_unique_filename(path)
        >>> # If document.md exists, returns document_1.md
    """
    if not filepath.exists():
        return filepath

    # Split into parts
    directory = filepath.parent
    stem = filepath.stem
    suffix = filepath.suffix

    # Try adding counter
    for i in range(1, max_attempts + 1):
        new_filename = f"{stem}_{i}{suffix}"
        new_filepath = directory / new_filename

        if not new_filepath.exists():
            return new_filepath

    raise ValueError(f"Unable to find unique filename after {max_attempts} attempts")


def create_filename_from_url(
    url: str,
    max_length: int = 100,
    extension: str = '.md'
) -> str:
    """
    Create filename directly from URL when title is not available.

    Args:
        url: Source URL
        max_length: Maximum filename length
        extension: File extension

    Returns:
        Filename based on URL

    Example:
        >>> filename = create_filename_from_url(
        ...     "https://help.genetec.cloud/en/api/authentication.html"
        ... )
        >>> print(filename)
        api-authentication-e8f4a2.md
    """
    from urllib.parse import urlparse

    # Parse URL
    parsed = urlparse(url)

    # Get path without extension
    path = parsed.path.strip('/')

    # Remove file extension if present
    path = re.sub(r'\.(html|htm|php|aspx?)$', '', path)

    # Replace slashes with hyphens
    safe_path = path.replace('/', '-')

    # Use standard sanitization
    return create_safe_filename(
        title=safe_path if safe_path else 'page',
        url=url,
        max_length=max_length,
        add_hash=True,
        extension=extension
    )


def validate_filename(filename: str) -> tuple[bool, str]:
    """
    Validate that filename is safe for filesystem.

    Args:
        filename: Filename to validate

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> is_valid, error = validate_filename("my-file.md")
        >>> if not is_valid:
        ...     print(f"Invalid: {error}")
    """
    # Check for empty filename
    if not filename or filename.strip() == '':
        return False, "Filename is empty"

    # Check for reserved names (Windows)
    reserved_names = [
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]

    name_without_ext = Path(filename).stem.upper()
    if name_without_ext in reserved_names:
        return False, f"Filename uses reserved name: {name_without_ext}"

    # Check for unsafe characters
    unsafe_pattern = r'[<>:"/\\|?*\x00-\x1f]'
    if re.search(unsafe_pattern, filename):
        return False, "Filename contains unsafe characters"

    # Check for leading/trailing dots or spaces
    if filename.startswith('.') or filename.endswith('.'):
        return False, "Filename starts or ends with dot"

    if filename.startswith(' ') or filename.endswith(' '):
        return False, "Filename starts or ends with space"

    # Check length (common limit is 255 bytes)
    if len(filename.encode('utf-8')) > 255:
        return False, "Filename is too long (>255 bytes)"

    return True, ""


def get_file_stem_and_hash(filename: str) -> tuple[str, str]:
    """
    Extract the stem and hash from a filename created by create_safe_filename.

    Args:
        filename: Filename with potential hash suffix

    Returns:
        Tuple of (stem_without_hash, hash_or_empty)

    Example:
        >>> stem, hash_val = get_file_stem_and_hash("api-auth-guide-a3f2d1.md")
        >>> print(stem)  # "api-auth-guide"
        >>> print(hash_val)  # "a3f2d1"
    """
    # Remove extension
    path = Path(filename)
    stem = path.stem

    # Check if ends with hash pattern (6 hex chars)
    match = re.search(r'-([0-9a-f]{6})$', stem)

    if match:
        hash_value = match.group(1)
        stem_without_hash = stem[:match.start()]
        return stem_without_hash, hash_value
    else:
        return stem, ""
