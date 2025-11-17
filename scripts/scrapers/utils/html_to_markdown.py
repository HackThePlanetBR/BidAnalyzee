"""
HTML to Markdown Converter

Robust HTML to Markdown conversion with proper formatting for:
- Headings (h1-h6)
- Paragraphs
- Lists (ordered and unordered, nested)
- Tables
- Code blocks
- Blockquotes
- Links and images
"""

import re
from typing import Set, Optional
from bs4 import BeautifulSoup, Tag, NavigableString
import logging

logger = logging.getLogger(__name__)


class HTMLToMarkdownConverter:
    """
    Converts HTML content to clean Markdown format.

    Features:
    - Preserves document structure
    - Handles nested lists
    - Converts tables to markdown format
    - Cleans unwanted elements (scripts, styles, nav)
    - Avoids duplicate processing
    - Preserves code blocks with language detection
    """

    # Elements to remove completely
    UNWANTED_TAGS = ['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'noscript']

    # Block-level elements that should be processed
    BLOCK_ELEMENTS = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'blockquote', 'table', 'pre', 'div']

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize converter.

        Args:
            base_url: Base URL for converting relative links to absolute
        """
        self.base_url = base_url
        self.processed_elements: Set[int] = set()

    def convert(self, html_content: str, title: Optional[str] = None) -> str:
        """
        Convert HTML to Markdown.

        Args:
            html_content: HTML content as string or BeautifulSoup element
            title: Optional document title to include as h1

        Returns:
            Markdown formatted string

        Example:
            >>> converter = HTMLToMarkdownConverter()
            >>> html = "<h2>Title</h2><p>Content here</p>"
            >>> markdown = converter.convert(html)
        """
        # Parse HTML if string
        if isinstance(html_content, str):
            soup = BeautifulSoup(html_content, 'html.parser')
        else:
            soup = html_content

        # Clean unwanted elements
        self._clean_unwanted_elements(soup)

        markdown = ""

        # Add title if provided
        if title:
            markdown += f"# {title}\n\n"

        # Reset processed elements tracker
        self.processed_elements.clear()

        # Process all block-level elements in order
        for element in soup.find_all(self.BLOCK_ELEMENTS):
            # Skip if already processed (nested elements)
            if id(element) in self.processed_elements:
                continue

            # Convert element to markdown
            element_md = self._process_element(element)

            if element_md:
                markdown += element_md

        # Clean up excessive newlines
        markdown = self._cleanup_markdown(markdown)

        return markdown

    def _clean_unwanted_elements(self, soup: BeautifulSoup) -> None:
        """Remove unwanted HTML elements."""
        for tag_name in self.UNWANTED_TAGS:
            for element in soup.find_all(tag_name):
                element.decompose()

    def _process_element(self, element: Tag) -> str:
        """
        Process a single HTML element and convert to markdown.

        Args:
            element: BeautifulSoup Tag element

        Returns:
            Markdown string for this element
        """
        tag_name = element.name

        # Mark as processed
        self.processed_elements.add(id(element))

        # Get clean text
        text = element.get_text().strip()

        # Skip empty elements
        if not text or len(text) < 3:
            return ""

        # Convert based on tag type
        if tag_name == 'h1':
            return f"# {text}\n\n"
        elif tag_name == 'h2':
            return f"## {text}\n\n"
        elif tag_name == 'h3':
            return f"### {text}\n\n"
        elif tag_name == 'h4':
            return f"#### {text}\n\n"
        elif tag_name == 'h5':
            return f"##### {text}\n\n"
        elif tag_name == 'h6':
            return f"###### {text}\n\n"
        elif tag_name == 'p':
            # Process inline elements within paragraph
            processed_text = self._process_inline_elements(element)
            if len(processed_text) > 10:
                return f"{processed_text}\n\n"
        elif tag_name == 'blockquote':
            # Process blockquote content
            content = self._process_inline_elements(element)
            lines = content.split('\n')
            quoted = '\n'.join(f"> {line}" for line in lines if line.strip())
            return f"{quoted}\n\n"
        elif tag_name in ['ul', 'ol']:
            return self._process_list(element)
        elif tag_name == 'table':
            return self._process_table(element)
        elif tag_name == 'pre':
            return self._process_code_block(element)
        elif tag_name == 'div':
            # Only process divs if they contain substantial text
            if len(text) > 50:
                processed_text = self._process_inline_elements(element)
                return f"{processed_text}\n\n"

        return ""

    def _process_inline_elements(self, element: Tag) -> str:
        """
        Process inline elements like <a>, <strong>, <em>, <code>.

        Args:
            element: Parent element containing inline elements

        Returns:
            Processed text with markdown inline formatting
        """
        # Get all contents (text and tags)
        result = ""

        for content in element.contents:
            if isinstance(content, NavigableString):
                # Plain text
                text = str(content).strip()
                if text:
                    result += text + " "
            elif isinstance(content, Tag):
                tag_name = content.name

                if tag_name == 'a':
                    # Link
                    link_text = content.get_text().strip()
                    link_href = content.get('href', '')

                    # Convert relative to absolute if base_url provided
                    if self.base_url and link_href and not link_href.startswith(('http://', 'https://', '#')):
                        from urllib.parse import urljoin
                        link_href = urljoin(self.base_url, link_href)

                    if link_text and link_href:
                        result += f"[{link_text}]({link_href}) "
                    elif link_text:
                        result += f"{link_text} "

                elif tag_name == 'strong' or tag_name == 'b':
                    # Bold
                    bold_text = content.get_text().strip()
                    if bold_text:
                        result += f"**{bold_text}** "

                elif tag_name == 'em' or tag_name == 'i':
                    # Italic
                    italic_text = content.get_text().strip()
                    if italic_text:
                        result += f"*{italic_text}* "

                elif tag_name == 'code':
                    # Inline code
                    code_text = content.get_text().strip()
                    if code_text:
                        result += f"`{code_text}` "

                elif tag_name == 'br':
                    # Line break
                    result += "\n"

                else:
                    # Other tags - just get text
                    text = content.get_text().strip()
                    if text:
                        result += text + " "

        return result.strip()

    def _process_list(self, list_element: Tag) -> str:
        """
        Process ordered or unordered list.

        Args:
            list_element: <ul> or <ol> element

        Returns:
            Markdown formatted list
        """
        markdown = ""
        is_ordered = (list_element.name == 'ol')

        # Get direct <li> children only (not nested)
        list_items = list_element.find_all('li', recursive=False)

        if not list_items:
            return ""

        for i, li in enumerate(list_items, start=1):
            # Mark as processed
            self.processed_elements.add(id(li))

            # Get text (excluding nested lists)
            li_text = ""

            for content in li.contents:
                if isinstance(content, NavigableString):
                    li_text += str(content).strip() + " "
                elif isinstance(content, Tag):
                    if content.name not in ['ul', 'ol']:
                        # Not a nested list, include text
                        li_text += content.get_text().strip() + " "

            li_text = li_text.strip()

            # Clean up extra whitespace
            li_text = re.sub(r'\s+', ' ', li_text)

            if li_text and len(li_text) > 2:
                # Add list item
                if is_ordered:
                    markdown += f"{i}. {li_text}\n"
                else:
                    markdown += f"- {li_text}\n"

            # Process nested lists
            nested_lists = li.find_all(['ul', 'ol'], recursive=False)
            for nested_list in nested_lists:
                nested_md = self._process_list(nested_list)
                # Indent nested list
                indented = '\n'.join(f"  {line}" for line in nested_md.split('\n') if line.strip())
                markdown += indented + "\n"

        markdown += "\n"
        return markdown

    def _process_table(self, table_element: Tag) -> str:
        """
        Process HTML table to markdown table.

        Args:
            table_element: <table> element

        Returns:
            Markdown formatted table
        """
        markdown = "\n"

        rows = table_element.find_all('tr')
        if not rows:
            return ""

        for i, row in enumerate(rows):
            # Mark as processed
            self.processed_elements.add(id(row))

            # Get cells (th or td)
            cells = row.find_all(['td', 'th'])

            if not cells:
                continue

            # Extract cell texts
            cell_texts = []
            for cell in cells:
                self.processed_elements.add(id(cell))
                cell_text = cell.get_text().strip()
                # Clean whitespace
                cell_text = re.sub(r'\s+', ' ', cell_text)
                cell_texts.append(cell_text)

            if cell_texts:
                # Create table row
                row_text = " | ".join(cell_texts)
                markdown += f"| {row_text} |\n"

                # Add separator after header row
                if i == 0:
                    separators = " | ".join(["---" for _ in cell_texts])
                    markdown += f"| {separators} |\n"

        markdown += "\n"
        return markdown

    def _process_code_block(self, pre_element: Tag) -> str:
        """
        Process <pre> code block.

        Args:
            pre_element: <pre> element

        Returns:
            Markdown code block
        """
        # Get code element if exists
        code_element = pre_element.find('code')

        if code_element:
            code_text = code_element.get_text()
            # Try to detect language from class
            classes = code_element.get('class', [])
            language = ""

            for cls in classes:
                if cls.startswith('language-'):
                    language = cls.replace('language-', '')
                    break
                elif cls in ['python', 'javascript', 'java', 'cpp', 'bash', 'sql', 'json', 'xml']:
                    language = cls
                    break

            return f"```{language}\n{code_text}\n```\n\n"
        else:
            # Just pre without code
            code_text = pre_element.get_text()
            return f"```\n{code_text}\n```\n\n"

    def _cleanup_markdown(self, markdown: str) -> str:
        """
        Clean up excessive whitespace and newlines in markdown.

        Args:
            markdown: Raw markdown string

        Returns:
            Cleaned markdown
        """
        # Remove excessive newlines (more than 2 consecutive)
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)

        # Remove trailing whitespace on each line
        lines = markdown.split('\n')
        lines = [line.rstrip() for line in lines]
        markdown = '\n'.join(lines)

        # Ensure file ends with single newline
        markdown = markdown.strip() + '\n'

        return markdown


def html_to_markdown(
    html_content: str,
    title: Optional[str] = None,
    base_url: Optional[str] = None
) -> str:
    """
    Convenience function to convert HTML to Markdown.

    Args:
        html_content: HTML string or BeautifulSoup element
        title: Optional document title
        base_url: Base URL for resolving relative links

    Returns:
        Markdown string

    Example:
        >>> html = "<h2>Title</h2><p>Content</p>"
        >>> markdown = html_to_markdown(html, title="Document")
    """
    converter = HTMLToMarkdownConverter(base_url=base_url)
    return converter.convert(html_content, title=title)
