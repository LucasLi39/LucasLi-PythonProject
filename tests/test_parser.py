"""Tests for parser.py — file parsing logic."""

import os
import unittest
import tempfile
from pathlib import Path

from parser import (
    parse_txt,
    parse_file,
    _html_to_text,
    _extract_title,
    _split_txt_chapters,
)


class TestHtmlToText(unittest.TestCase):
    """Test HTML stripping and text extraction."""

    def test_remove_script_tags(self):
        """Script tags should be completely removed."""
        html = '<p>Hello</p><script>alert("x")</script><p>World</p>'
        result = _html_to_text(html)
        self.assertNotIn("script", result)
        self.assertNotIn("alert", result)
        self.assertIn("Hello", result)
        self.assertIn("World", result)

    def test_remove_style_tags(self):
        """Style tags should be completely removed."""
        html = '<style>body{color:red}</style><p>Text</p>'
        result = _html_to_text(html)
        self.assertNotIn("style", result)
        self.assertNotIn("color", result)
        self.assertIn("Text", result)

    def test_remove_img_tags(self):
        """Image tags should be removed."""
        html = '<p>Start</p><img src="pic.jpg"/><p>End</p>'
        result = _html_to_text(html)
        self.assertNotIn("img", result)
        self.assertNotIn("pic.jpg", result)
        self.assertIn("Start", result)
        self.assertIn("End", result)

    def test_remove_svg_tags(self):
        """SVG tags should be removed."""
        html = '<p>Text</p><svg><circle/></svg><p>More</p>'
        result = _html_to_text(html)
        self.assertNotIn("svg", result)
        self.assertNotIn("circle", result)

    def test_block_elements_to_newlines(self):
        """Block elements should become newlines."""
        html = '<p>Paragraph 1</p><p>Paragraph 2</p>'
        result = _html_to_text(html)
        self.assertIn("Paragraph 1", result)
        self.assertIn("Paragraph 2", result)

    def test_html_entities_decoded(self):
        """HTML entities should be decoded."""
        html = '<p>A &amp; B &lt; C</p>'
        result = _html_to_text(html)
        self.assertIn("A & B", result)
        self.assertIn("< C", result)
        self.assertNotIn("&amp;", result)

    def test_whitespace_cleanup(self):
        """Excessive newlines should be collapsed."""
        html = '<p>A</p>\n\n\n\n\n<p>B</p>'
        result = _html_to_text(html)
        # Should not have 4+ consecutive newlines
        self.assertNotIn("\n\n\n\n", result)


class TestExtractTitle(unittest.TestCase):
    """Test title extraction from HTML."""

    def test_h1_title(self):
        """h1 tags should be extracted as title."""
        html = '<html><body><h1>Chapter One</h1><p>Text</p></body></html>'
        self.assertEqual(_extract_title(html), "Chapter One")

    def test_h2_title(self):
        """h2 tags should also be extracted."""
        html = '<h2>Section A</h2><p>Text</p>'
        self.assertEqual(_extract_title(html), "Section A")

    def test_no_title(self):
        """HTML without h1/h2 returns empty string."""
        html = '<p>Just some text</p>'
        self.assertEqual(_extract_title(html), "")

    def test_title_with_nested_tags(self):
        """Nested tags inside title should be stripped."""
        html = '<h1><em>Italic</em> Title</h1>'
        self.assertEqual(_extract_title(html), "Italic Title")


class TestSplitTxtChapters(unittest.TestCase):
    """Test TXT chapter splitting logic."""

    def test_form_feed_split(self):
        """Form feed characters should split chapters."""
        text = "Part one content\fPart two content"
        chapters = _split_txt_chapters(text)
        self.assertEqual(len(chapters), 2)
        self.assertEqual(chapters[0]["title"], "Part 1")
        self.assertEqual(chapters[1]["title"], "Part 2")

    def test_chinese_chapter_markers(self):
        """Chinese-style chapter markers should split chapters."""
        text = "前置文本\n\n第一章\n这是第一章内容\n\n第二章\n这是第二章内容"
        chapters = _split_txt_chapters(text)
        self.assertGreaterEqual(len(chapters), 2)
        self.assertIn("第一章", chapters[0]["title"])

    def test_english_chapter_markers(self):
        """English chapter markers should split chapters."""
        text = "Intro\n\nChapter 1\nContent one\n\nChapter 2\nContent two"
        chapters = _split_txt_chapters(text)
        self.assertGreaterEqual(len(chapters), 2)

    def test_no_markers_single_chapter(self):
        """Text without chapter markers becomes a single chapter."""
        text = "Just some plain text without any chapters"
        chapters = _split_txt_chapters(text)
        self.assertEqual(len(chapters), 1)
        self.assertEqual(chapters[0]["title"], "全文")
        self.assertIn("plain text", chapters[0]["content"])

    def test_empty_text(self):
        """Empty text should return a single chapter."""
        chapters = _split_txt_chapters("")
        self.assertEqual(len(chapters), 1)


class TestParseTxt(unittest.TestCase):
    """Test TXT file parsing."""

    def setUp(self):
        """Create a temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        for f in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, f))
        os.rmdir(self.temp_dir)

    def test_parse_simple_txt(self):
        """A simple TXT file should parse correctly."""
        filepath = os.path.join(self.temp_dir, "test_book.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("吾輩は猫である。\n\n名前はまだ無い。")

        result = parse_txt(filepath)
        self.assertEqual(result["title"], "test_book")
        self.assertIsInstance(result["chapters"], list)
        self.assertGreater(len(result["chapters"]), 0)

    def test_parse_japanese_txt(self):
        """Japanese text should be preserved with correct encoding."""
        filepath = os.path.join(self.temp_dir, "japanese.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("第一章\n\n吾輩は猫である。\n\n第二章\n\n続きの物語。")

        result = parse_txt(filepath)
        # Should have chapters
        self.assertGreaterEqual(len(result["chapters"]), 1)
        # Content should contain Japanese text
        content = result["chapters"][0]["content"]
        self.assertIn("吾輩", content)


class TestParseFile(unittest.TestCase):
    """Test the unified parse_file dispatcher."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        for f in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, f))
        os.rmdir(self.temp_dir)

    def test_unsupported_format(self):
        """Unsupported file formats should raise ValueError."""
        filepath = os.path.join(self.temp_dir, "test.pdf")
        with open(filepath, "w") as f:
            f.write("dummy")

        with self.assertRaises(ValueError) as context:
            parse_file(filepath)
        self.assertIn("Unsupported", str(context.exception))

    def test_txt_format(self):
        """TXT files should be parsed via parse_txt."""
        filepath = os.path.join(self.temp_dir, "test.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("Hello world")

        result = parse_file(filepath)
        self.assertEqual(result["title"], "test")
        self.assertEqual(len(result["chapters"]), 1)


if __name__ == "__main__":
    unittest.main()
