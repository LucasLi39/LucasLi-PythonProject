import re
from pykakasi import kakasi
from common_kanji import is_uncommon

# Initialize pykakasi converter
_kakasi = kakasi()
_kakasi.setMode("J", "H")  # Kanji to Hiragana
_kakasi.setMode("H", "H")  # Hiragana to Hiragana (passthrough)
_kakasi.setMode("K", "H")  # Katakana to Hiragana
_converter = _kakasi.getConverter()

# Regex to match CJK kanji characters
KANJI_PATTERN = re.compile(r'[一-鿿㐀-䶿]')

# Regex to match explicit furigana patterns like 漢字（かんじ）or 漢字(かんじ)
# Matches: one or more kanji + full-width or half-width parens containing hiragana/katakana
EXPLICIT_FURIGANA_PATTERN = re.compile(
    r'([一-鿿㐀-䶿]+)\s*[(（]([ぁ-ゔァ-ヶー]+)[)）]'
)


def _extract_explicit_furigana(text: str) -> str:
    """Convert 漢字（かんじ） patterns to <ruby> tags.

    Replaces explicit furigana annotations with HTML ruby tags.
    Uses the furigana provided in the text rather than guessing with pykakasi.
    """
    def replace_match(match: re.Match) -> str:
        kanji = match.group(1)
        furigana = match.group(2)
        return f'<ruby>{kanji}<rt>{furigana}</rt></ruby>'

    return EXPLICIT_FURIGANA_PATTERN.sub(replace_match, text)


def annotate_text(text: str) -> str:
    """Annotate uncommon kanji with furigana using ruby HTML tags.

    First extracts explicit furigana from parentheses (e.g. 漢字（かんじ）),
    then uses pykakasi for remaining kanji.

    Returns HTML string where uncommon kanji are wrapped in <ruby>漢字<rt>かんじ</rt></ruby>.
    Common kanji and non-kanji text pass through unchanged.
    """
    # Step 1: Extract explicit furigana from parentheses
    text = _extract_explicit_furigana(text)

    # Step 2: Process remaining text, skipping already-annotated <ruby> blocks
    result = []
    i = 0

    while i < len(text):
        # Check if we're at the start of an existing <ruby> tag
        if text[i:i+6] == '<ruby>':
            # Find the end of this ruby tag
            end_tag = text.find('</ruby>', i)
            if end_tag != -1:
                result.append(text[i:end_tag + 7])
                i = end_tag + 7
                continue

        char = text[i]

        if KANJI_PATTERN.match(char):
            # Found a kanji — try to get a multi-character kanji word
            word, reading = _extract_kanji_word(text, i)

            if is_uncommon_word(word):
                result.append(f'<ruby>{word}<rt>{reading}</rt></ruby>')
            else:
                result.append(word)

            i += len(word)
        else:
            result.append(char)
            i += 1

    return ''.join(result)


def _extract_kanji_word(text: str, start: int) -> tuple[str, str]:
    """Extract a kanji word starting at position start and get its reading.

    Tries to grab consecutive kanji characters to form a word,
    then uses pykakasi to get the reading.
    """
    # Find the end of consecutive kanji characters
    end = start
    while end < len(text) and KANJI_PATTERN.match(text[end]):
        end += 1

    word = text[start:end]

    if len(word) == 1:
        # Single kanji — use pykakasi directly
        converted = _converter.do(word)
        reading = _extract_hiragana(converted)
        return word, reading

    # Multi-character kanji word — convert the whole word
    converted = _converter.do(word)
    reading = _extract_hiragana(converted)
    return word, reading


def _extract_hiragana(converted: str) -> str:
    """Extract only hiragana characters from pykakasi output."""
    return ''.join(c for c in converted if '぀' <= c <= 'ゟ')


def is_uncommon_word(word: str) -> bool:
    """Return True if any character in the word is uncommon kanji."""
    for char in word:
        if KANJI_PATTERN.match(char) and is_uncommon(char):
            return True
    return False
