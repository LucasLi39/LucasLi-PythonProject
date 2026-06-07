"""Tests for annotator.py — furigana annotation engine."""

import unittest
from annotator import (
    annotate_text,
    _extract_explicit_furigana,
    is_uncommon_word,
    KANJI_PATTERN,
)


class TestExplicitFurigana(unittest.TestCase):
    """Test extraction of parenthesized furigana: 漢字（かんじ）."""

    def test_fullwidth_parens(self):
        """Full-width parentheses should be recognized."""
        text = "漢字（かんじ）"
        result = _extract_explicit_furigana(text)
        self.assertEqual(result, "<ruby>漢字<rt>かんじ</rt></ruby>")

    def test_halfwidth_parens(self):
        """Half-width parentheses should also be recognized."""
        text = "漢字(かんじ)"
        result = _extract_explicit_furigana(text)
        self.assertEqual(result, "<ruby>漢字<rt>かんじ</rt></ruby>")

    def test_multiple_explicit(self):
        """Multiple explicit annotations in one string."""
        text = "名前（なまえ）は猫（ねこ）である"
        result = _extract_explicit_furigana(text)
        self.assertIn("<ruby>名前<rt>なまえ</rt></ruby>", result)
        self.assertIn("<ruby>猫<rt>ねこ</rt></ruby>", result)
        self.assertNotIn("（", result)
        self.assertNotIn("）", result)

    def test_no_explicit_furigana(self):
        """Text without parentheses should pass through unchanged."""
        text = "吾輩は猫である"
        result = _extract_explicit_furigana(text)
        self.assertEqual(result, text)


class TestIsUncommonWord(unittest.TestCase):
    """Test the uncommon-word detector."""

    def test_common_word(self):
        """Words made entirely of common kanji are not uncommon."""
        self.assertFalse(is_uncommon_word("日本"))   # Both common
        self.assertFalse(is_uncommon_word("学校"))   # Both common
        self.assertFalse(is_uncommon_word("人口"))   # Both common

    def test_uncommon_word(self):
        """Words containing any uncommon kanji are flagged."""
        self.assertTrue(is_uncommon_word("吾輩"))    # Both uncommon
        self.assertTrue(is_uncommon_word("誕生"))    # 誕 is uncommon

    def test_mixed_word(self):
        """Words with a mix of common and uncommon kanji are flagged."""
        # Even if one kanji is common, the presence of an uncommon one flags it
        self.assertTrue(is_uncommon_word("輩目"))    # 輩 uncommon, 目 common


class TestAnnotateText(unittest.TestCase):
    """Test the full annotation pipeline."""

    def test_common_kanji_not_annotated(self):
        """Common kanji should NOT get ruby tags."""
        text = "日本の学校"
        result = annotate_text(text)
        self.assertNotIn("<ruby>", result)

    def test_uncommon_kanji_gets_annotated(self):
        """Uncommon kanji should get ruby tags with furigana."""
        text = "吾輩"
        result = annotate_text(text)
        self.assertIn("<ruby>吾輩<rt>わがはい</rt></ruby>", result)

    def test_hiragana_passes_through(self):
        """Hiragana should not be modified."""
        text = "わがはい"
        result = annotate_text(text)
        self.assertEqual(result, text)

    def test_katakana_passes_through(self):
        """Katakana should not be modified."""
        text = "テレビ"
        result = annotate_text(text)
        self.assertEqual(result, text)

    def test_explicit_furigana_priority(self):
        """Explicit furigana in parentheses takes priority over pykakasi."""
        text = "薄暗（うすぐら）い"
        result = annotate_text(text)
        # Should use the explicit reading うすぐら, not pykakasi's はくあん
        self.assertIn("<ruby>薄暗<rt>うすぐら</rt></ruby>", result)
        self.assertNotIn("はくあん", result)

    def test_mixed_text(self):
        """Mixed text: hiragana + kanji should handle correctly."""
        text = "吾輩が好きです"
        result = annotate_text(text)
        # 吾輩 are uncommon and should be annotated
        self.assertIn("<ruby>吾輩<rt>わがはい</rt></ruby>", result)
        # Hiragana should pass through
        self.assertIn("が", result)
        self.assertIn("です", result)

    def test_single_kanji_annotation(self):
        """Single uncommon kanji should be annotated."""
        text = "輩"
        result = annotate_text(text)
        # pykakasi returns やから for 輩 when standalone
        self.assertIn("<ruby>輩<rt>", result)
        self.assertIn("</rt></ruby>", result)

    def test_punctuation_preserved(self):
        """Punctuation should be preserved."""
        text = "吾輩は猫である。"
        result = annotate_text(text)
        self.assertIn("。", result)
        self.assertIn("、", annotate_text("吾輩、猫。"))

    def test_no_duplicate_annotation(self):
        """Already-annotated ruby blocks should not be double-annotated."""
        text = "<ruby>漢字<rt>かんじ</rt></ruby>"
        result = annotate_text(text)
        # Should contain the ruby tag exactly once, not nested
        count = result.count("<ruby>")
        self.assertEqual(count, 1)


class TestKanjiPattern(unittest.TestCase):
    """Test the KANJI_PATTERN regex."""

    def test_matches_kanji(self):
        self.assertIsNotNone(KANJI_PATTERN.match("漢"))
        self.assertIsNotNone(KANJI_PATTERN.match("字"))

    def test_no_match_hiragana(self):
        self.assertIsNone(KANJI_PATTERN.match("あ"))

    def test_no_match_katakana(self):
        self.assertIsNone(KANJI_PATTERN.match("ア"))

    def test_no_match_ascii(self):
        self.assertIsNone(KANJI_PATTERN.match("A"))
        self.assertIsNone(KANJI_PATTERN.match("1"))


if __name__ == "__main__":
    unittest.main()
