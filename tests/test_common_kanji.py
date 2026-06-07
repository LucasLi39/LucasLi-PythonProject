"""Tests for common_kanji.py — kanji filtering logic."""

import unittest
from common_kanji import is_uncommon, COMMON_KANJI


class TestCommonKanji(unittest.TestCase):
    """Test the JLPT-based kanji filtering."""

    def test_common_n5_kanji(self):
        """N5 kanji like 人, 日, 月 should NOT be flagged as uncommon."""
        self.assertFalse(is_uncommon("人"))
        self.assertFalse(is_uncommon("日"))
        self.assertFalse(is_uncommon("月"))
        self.assertFalse(is_uncommon("山"))
        self.assertFalse(is_uncommon("水"))

    def test_common_n4_kanji(self):
        """N4 kanji like 会, 社, 駅 should NOT be flagged as uncommon."""
        self.assertFalse(is_uncommon("会"))
        self.assertFalse(is_uncommon("社"))
        self.assertFalse(is_uncommon("駅"))
        self.assertFalse(is_uncommon("食"))
        self.assertFalse(is_uncommon("飲"))

    def test_uncommon_kanji(self):
        """Kanji outside N5/N4 SHOULD be flagged as uncommon."""
        self.assertTrue(is_uncommon("輩"))   # Uncommon
        self.assertTrue(is_uncommon("薄"))   # Uncommon
        self.assertTrue(is_uncommon("诞"))   # Rare kanji
        self.assertTrue(is_uncommon("吾"))   # Uncommon
        self.assertTrue(is_uncommon("墓"))   # Uncommon

    def test_non_kanji_characters(self):
        """Hiragana, katakana, and ASCII should be considered uncommon
        (they are not in COMMON_KANJI, but callers filter by kanji pattern first)."""
        self.assertTrue(is_uncommon("あ"))
        self.assertTrue(is_uncommon("A"))
        self.assertTrue(is_uncommon("1"))

    def test_common_kanji_set_size(self):
        """The common kanji set should contain a reasonable number of characters."""
        self.assertGreater(len(COMMON_KANJI), 100)
        self.assertLess(len(COMMON_KANJI), 500)


if __name__ == "__main__":
    unittest.main()
