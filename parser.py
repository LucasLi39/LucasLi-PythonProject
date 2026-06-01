import re
from pathlib import Path
from ebooklib import epub
from lxml import etree


def parse_txt(file_path: str) -> dict:
    """Parse a TXT file and return structured book data."""
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Split into chapters by double newlines or page breaks
    chapters = _split_txt_chapters(text)

    return {
        "title": Path(file_path).stem,
        "chapters": chapters
    }


def parse_epub(file_path: str) -> dict:
    """Parse an EPUB file and return structured book data."""
    book = epub.read_epub(file_path, options={"ignore_ncx": True})

    # Get title from metadata
    title = book.get_metadata('DC', 'title')
    title = title[0][0] if title else Path(file_path).stem

    chapters = []
    for item in book.get_items_of_type(9):  # ITEM_DOCUMENT
        content = item.get_content().decode('utf-8', errors='replace')
        html_text = _html_to_text(content)

        if html_text.strip():
            chapters.append({
                "title": _extract_title(content) or f"Chapter {len(chapters) + 1}",
                "content": html_text
            })

    return {
        "title": title,
        "chapters": chapters
    }


def _html_to_text(html_content: str) -> str:
    """Convert HTML content to clean text, preserving structure.

    Strips images and scripts but keeps text flow.
    """
    # Remove script and style tags
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)

    # Remove img tags
    html_content = re.sub(r'<img[^>]*/?>', '', html_content)

    # Remove SVG tags
    html_content = re.sub(r'<svg[^>]*>.*?</svg>', '', html_content, flags=re.DOTALL)

    # Convert block elements to newlines
    html_content = re.sub(r'<(p|div|br|h[1-6])[^>]*/?>', '\n', html_content)
    html_content = re.sub(r'</(p|div|h[1-6])>', '\n', html_content)

    # Remove remaining HTML tags
    html_content = re.sub(r'<[^>]+>', '', html_content)

    # Decode HTML entities
    html_content = html_content.replace('&amp;', '&')
    html_content = html_content.replace('&lt;', '<')
    html_content = html_content.replace('&gt;', '>')
    html_content = html_content.replace('&quot;', '"')
    html_content = html_content.replace('&#39;', "'")
    html_content = html_content.replace('&nbsp;', ' ')

    # Clean up whitespace
    html_content = re.sub(r'\n{3,}', '\n\n', html_content)
    html_content = html_content.strip()

    return html_content


def _extract_title(html_content: str) -> str:
    """Extract title from first h1/h2 tag in HTML content."""
    match = re.search(r'<h[12][^>]*>(.*?)</h[12]>', html_content, re.DOTALL)
    if match:
        title = re.sub(r'<[^>]+>', '', match.group(1))
        return title.strip()
    return ""


def _split_txt_chapters(text: str) -> list[dict]:
    """Split TXT content into chapters.

    Attempts to split by form feed characters, chapter markers,
    or large blank line gaps.
    """
    # Try splitting by form feed first
    if '\f' in text:
        parts = text.split('\f')
        return [{"title": f"Part {i + 1}", "content": part.strip()}
                for i, part in enumerate(parts) if part.strip()]

    # Try splitting by chapter markers (e.g., "第1章", "Chapter 1", "CHAPTER 1")
    chapter_pattern = re.compile(
        r'\n\s*(?:第[一二三四五六七八九十百千\d]+章|'
        r'[Cc]hapter\s+\d+|'
        r'CHAPTER\s+\d+)',
        re.MULTILINE
    )
    splits = list(chapter_pattern.finditer(text))

    if len(splits) >= 2:
        chapters = []
        for i, match in enumerate(splits):
            start = match.start()
            end = splits[i + 1].start() if i + 1 < len(splits) else len(text)
            content = text[start:end].strip()
            if content:
                chapters.append({
                    "title": match.group().strip(),
                    "content": content
                })
        return chapters

    # Fallback: return as single chapter
    return [{"title": "全文", "content": text}]


def parse_file(file_path: str) -> dict:
    """Parse a file (EPUB or TXT) and return structured book data."""
    ext = Path(file_path).suffix.lower()

    if ext == '.epub':
        return parse_epub(file_path)
    elif ext == '.txt':
        return parse_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
