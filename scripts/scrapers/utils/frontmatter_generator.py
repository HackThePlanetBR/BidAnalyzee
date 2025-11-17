"""
YAML Frontmatter Generator

Generates properly formatted YAML frontmatter for markdown documents
to integrate with the RAG system.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import yaml


def generate_frontmatter(
    title: str,
    url: str,
    source: str,
    category: str,
    language: str = "en",
    product: Optional[str] = None,
    version: Optional[str] = None,
    tags: Optional[List[str]] = None,
    extra_fields: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate YAML frontmatter for markdown files.

    Args:
        title: Document title (required)
        url: Source URL - must be absolute (required)
        source: Source website name (required)
        category: Content category (required)
        language: Language code (default: "en")
        product: Product name (optional)
        version: Product version (optional)
        tags: List of tags (optional)
        extra_fields: Additional custom fields (optional)

    Returns:
        Formatted YAML frontmatter string with --- delimiters

    Raises:
        ValueError: If required fields are missing or invalid

    Example:
        >>> frontmatter = generate_frontmatter(
        ...     title="API Authentication Guide",
        ...     url="https://help.scsaas.genetec.cloud/en/api/auth.html",
        ...     source="Security Center SaaS Help",
        ...     category="SCSaaS"
        ... )
        >>> print(frontmatter)
        ---
        title: API Authentication Guide
        url: https://help.scsaas.genetec.cloud/en/api/auth.html
        source: Security Center SaaS Help
        category: SCSaaS
        date: 2025-11-17
        language: en
        ---
    """
    # Validate required fields
    if not title:
        raise ValueError("Title is required")
    if not url:
        raise ValueError("URL is required")
    if not source:
        raise ValueError("Source is required")
    if not category:
        raise ValueError("Category is required")

    # Validate URL format
    if not url.startswith(('http://', 'https://')):
        raise ValueError(f"URL must be absolute (start with http:// or https://): {url}")

    # Validate language (enforce English-only)
    if language != 'en':
        raise ValueError(f"Only English content allowed (language must be 'en', got '{language}')")

    # Build metadata dictionary with required fields
    metadata = {
        'title': title,
        'url': url,
        'source': source,
        'category': category,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'language': language
    }

    # Add optional fields if provided
    if product:
        metadata['product'] = product
    if version:
        metadata['version'] = version
    if tags:
        metadata['tags'] = tags

    # Add extra custom fields if provided
    if extra_fields:
        metadata.update(extra_fields)

    # Generate YAML with proper formatting
    yaml_content = yaml.dump(
        metadata,
        default_flow_style=False,  # Use block style (multi-line)
        allow_unicode=True,         # Support unicode characters
        sort_keys=False,            # Preserve field order
        width=1000                  # Prevent line wrapping for long URLs
    )

    # Return frontmatter with delimiters
    return f"---\n{yaml_content}---\n"


def validate_frontmatter(frontmatter_dict: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate that frontmatter dictionary contains all required fields.

    Args:
        frontmatter_dict: Dictionary of frontmatter fields

    Returns:
        Tuple of (is_valid, list_of_errors)

    Example:
        >>> metadata = {'title': 'Test', 'url': 'http://test.com', ...}
        >>> is_valid, errors = validate_frontmatter(metadata)
        >>> if not is_valid:
        ...     print(f"Errors: {errors}")
    """
    errors = []

    # Required fields
    required_fields = ['title', 'url', 'source', 'category', 'date', 'language']

    for field in required_fields:
        if field not in frontmatter_dict:
            errors.append(f"Missing required field: {field}")
        elif not frontmatter_dict[field]:
            errors.append(f"Empty required field: {field}")

    # Validate URL format if present
    if 'url' in frontmatter_dict:
        url = frontmatter_dict['url']
        if not url.startswith(('http://', 'https://')):
            errors.append(f"Invalid URL format (must be absolute): {url}")

    # Validate language if present
    if 'language' in frontmatter_dict:
        if frontmatter_dict['language'] != 'en':
            errors.append(f"Invalid language (must be 'en'): {frontmatter_dict['language']}")

    # Validate date format if present
    if 'date' in frontmatter_dict:
        try:
            datetime.strptime(frontmatter_dict['date'], '%Y-%m-%d')
        except ValueError:
            errors.append(f"Invalid date format (must be YYYY-MM-DD): {frontmatter_dict['date']}")

    return len(errors) == 0, errors


def extract_frontmatter_from_markdown(markdown_content: str) -> Optional[Dict[str, Any]]:
    """
    Extract and parse frontmatter from a markdown file.

    Args:
        markdown_content: Full markdown file content

    Returns:
        Dictionary of frontmatter fields, or None if no frontmatter found

    Example:
        >>> with open('doc.md', 'r') as f:
        ...     content = f.read()
        >>> metadata = extract_frontmatter_from_markdown(content)
        >>> print(metadata['title'])
    """
    import re

    # Match frontmatter pattern
    pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(pattern, markdown_content, re.DOTALL)

    if not match:
        return None

    try:
        # Parse YAML
        frontmatter_yaml = match.group(1)
        metadata = yaml.safe_load(frontmatter_yaml)
        return metadata
    except yaml.YAMLError:
        return None
