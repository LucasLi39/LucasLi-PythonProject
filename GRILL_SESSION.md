# /grill-me Session — KanjiLens PRD v2

**Date:** 2026-06-07
**Project:** KanjiLens
**Type:** Web app (FastAPI backend + vanilla JS frontend)

---

## Section 1: Project Identity

**AI:** Let's start with Project Identity. What's your project called and what does it do in one sentence?

**Student:** It's called KanjiLens. It's a web app that lets users upload Japanese books and automatically annotates uncommon kanji with furigana.

**AI:** That's clear, but "users" is vague. Who exactly is your user? A high school student? A college student? Someone studying for JLPT? Someone reading for fun?

**Student:** A self-learner who is reading Japanese light novels. Not a student in a formal class — someone who bought a Japanese light novel and wants to read it without stopping every sentence to look up kanji.

**AI:** Better. Now — name one existing solution your user might already use. What does KanjiLens do better?

**Student:** Apple Books. You can import EPUBs into Apple Books, but it doesn't understand furigana in TXT files at all. And if the EPUB has embedded furigana, Apple Books might have import errors. KanjiLens supports both EPUB and TXT, and automatically identifies and marks all uncommon kanji regardless of the source format.

**AI:** Why did YOU pick this project? What's personal about it?

**Student:** I'm learning Japanese myself. I tried reading native content but got stuck on kanji constantly. Existing apps either annotate everything (cluttered) or nothing (frustrating). I wanted something that annotates just enough to keep me reading.

---

## Section 2: Feature Scope

**AI:** You need exactly 3-5 core features. List them.

**Student:**
1. File Upload & Parse — upload EPUB or TXT
2. Smart Furigana Annotation — two-step: explicit furigana from parentheses, then pykakasi for the rest
3. Paginated Reader — book-like pages with chapter navigation
4. Vocabulary Bookmark — click any annotated kanji to save it
5. In-Book Search — search for kanji/reading within the current page

**AI:** Good, 5 features. Let's grill Feature 1: File Upload. Walk me through the exact user flow, step by step.

**Student:**
1. User opens browser → sees KanjiLens homepage with a large upload button
2. User clicks upload → file picker opens, they select an EPUB or TXT file
3. User clicks "Upload & Read" → loading spinner shows "Analyzing kanji..."
4. Server processes the file, returns annotated chapters
5. Reader view appears with the first page of the book

**AI:** Edge case 1: User uploads a PDF. What happens?

**Student:** The server validates the file extension. If it's not .epub or .txt, it returns a 400 error with message "Only .epub and .txt files are supported." The frontend shows an alert.

**AI:** Edge case 2: User uploads a 100MB EPUB.

**Student:** We haven't implemented a file size limit yet. Right now it would try to process it, which might be slow or run out of memory. For V2, we should add a 50MB limit.

**AI:** Be honest — that's a gap. Write it down as a known limitation.

**Student:** Noted.

**AI:** Feature 3: Smart Furigana Annotation. How does the user know WHY a particular kanji got annotated or didn't?

**Student:** They don't — not explicitly. Common kanji (JLPT N5/N4) have no annotation. Uncommon kanji get `<ruby>` tags with furigana. The user can infer "this one has furigana because it's uncommon," but there's no tooltip explaining the JLPT level.

**AI:** So if a kanji has NO furigana, it could mean two things: (1) it's common, or (2) pykakasi failed to generate a reading. The user can't tell the difference. Is that a problem?

**Student:** For V1, it's acceptable. pykakasi handles most single kanji correctly. For V2, we could add a "debug mode" or hover tooltip.

**AI:** Feature 4: Vocabulary Bookmark. What happens when the user clicks a kanji?

**Student:** The kanji + its reading is saved to a vocabulary list stored in localStorage. A green flash appears on the kanji as visual feedback. The vocab count in the header updates. The user can open a sidebar to see all saved words and delete any.

**AI:** What if the user clicks the SAME kanji twice?

**Student:** It's a no-op. The code checks for duplicates before adding.

**AI:** What if the user refreshes the page? Do they lose their vocab list?

**Student:** No — localStorage persists across refreshes. But if they upload a different book, the vocab list stays (it might contain words from the previous book). That's a design choice — vocab is global, not per-book.

**AI:** Feature 5: In-Book Search. What exactly can the user search for?

**Student:** They can search for kanji characters or hiragana readings. The search scans all annotated `<ruby>` tags on the current page. Matches are highlighted in yellow. The user can navigate between matches with up/down arrows.

**AI:** What if the user searches for something that's not on the current page?

**Student:** The search only scans the current page. If there are no matches, it shows "No matches." The user would need to flip pages manually. Searching across all chapters would require loading all content into memory, which we don't do for performance reasons.

---

## Section 3: Data Architecture

**AI:** Show me the EXACT JSON your `/upload` endpoint returns.

**Student:**
```json
{
    "title": "吾輩は猫である",
    "chapters": [
        {
            "title": "第一章",
            "content": "<p><ruby>吾輩<rt>わがはい</rt></ruby>は猫である。</p><p>名前はまだ無い。</p>"
        },
        {
            "title": "第二章",
            "content": "<p>どこで生れたかとんと見当がつかぬ。</p>"
        }
    ]
}
```

**AI:** Where is this data stored while the user is reading?

**Student:** In JavaScript memory (the `chapters` array). When the user refreshes the page, it's lost. There's no database. The app is stateless: upload → read → done.

**AI:** So refreshing loses everything — the book, the current page, everything. Is that acceptable?

**Student:** For V1, yes. The user can re-upload the file in seconds. For V2, we could save the reading progress to localStorage.

---

## Section 4: Function Specifications

**AI:** Name 5 key functions in your codebase and their specs.

**Student:**

**Function 1: `parse_file(file_path: str) -> dict`**
- Parses EPUB or TXT file and returns structured book data
- Edge case: Unsupported format → raises `ValueError`
- Edge case: Corrupt EPUB → `ebooklib` may raise exception, caught in `app.py` and returned as 500 error

**Function 2: `annotate_text(text: str) -> str`**
- Annotates uncommon kanji with furigana using HTML `<ruby>` tags
- Two-step: explicit furigana from parentheses first, then pykakasi for remaining
- Edge case: Text with no kanji → returns unchanged
- Edge case: Already-annotated `<ruby>` blocks → skipped to prevent double-annotation

**Function 3: `_extract_explicit_furigana(text: str) -> str`**
- Converts `漢字（かんじ）` patterns to `<ruby>` tags
- Edge case: Half-width parens `漢字(かんじ)` → also matched
- Edge case: Nested/malformed parentheses → regex won't match, falls through to pykakasi

**Function 4: `is_uncommon(kanji_char: str) -> bool`**
- Returns True if kanji is outside JLPT N5/N4 sets
- Edge case: Non-kanji character (hiragana, ASCII) → returns True (but caller filters by kanji pattern first)

**Function 5: `_html_to_text(html_content: str) -> str`**
- Strips HTML tags and converts block elements to newlines
- Edge case: Script/style tags → completely removed
- Edge case: HTML entities (`&amp;`, `&lt;`) → decoded to actual characters

---

## Section 5: UI / Interaction Design

**AI:** Show me the opening screen.

**Student:**
```
┌─────────────────────────────────────┐
│                                     │
│           KanjiLens                 │
│   日本語の本を読もう                │
│                                     │
│   ┌─────────────────────────┐      │
│   │  📚 Choose an EPUB      │      │
│   │      or TXT file        │      │
│   └─────────────────────────┘      │
│                                     │
│   [Upload & Read] (disabled)       │
│                                     │
│   Supports .epub and .txt          │
│                                     │
└─────────────────────────────────────┘
```

**AI:** Show me the reader screen.

**Student:**
```
┌──────────────────────────────────────────────────────────┐
│ ← Back  |  Book Title  |  🔍 Search  |  あ Furigana    │
│                          |  📖 Vocab (3) |  [Chapter ▼] │
├──────────────────────────────────────────────────────────┤
│                                                          │
│   吾輩は猫である。名前はまだ無い。                        │
│                                                          │
│   どこで生れたかとんと見当がつかぬ。                      │
│                                                          │
├──────────────────────────────────────────────────────────┤
│              [← Prev]  Page 1 of 5  [Next →]            │
└──────────────────────────────────────────────────────────┘
```

**AI:** What happens when the user clicks "📖 Vocab (3)"?

**Student:** A sidebar slides in from the right showing the 3 saved words, each with delete button. If empty, shows "Click any annotated kanji to save it here."

---

## Section 6: Error Handling

**AI:** List 5 error scenarios.

**Student:**

| # | Error Scenario | App Response |
|---|---------------|-------------|
| 1 | User uploads PDF or other unsupported format | Alert: "Only .epub and .txt files are supported" |
| 2 | User uploads corrupt/unreadable EPUB | Alert: "Error: [exception message]" (HTTP 500) |
| 3 | pykakasi gives wrong reading for compound word | Mitigated by explicit furigana extraction; if neither works, kanji passes through unannotated |
| 4 | User searches for term with no matches | Search bar shows "No matches" |
| 5 | Page refresh mid-reading | Book content lost; user must re-upload (acceptable for V1) |

---

## Section 7: Testing Plan

**AI:** What are your 3 most important tests?

**Student:**

**Test 1: Explicit furigana priority**
- Input: `薄暗（うすぐら）い`
- Expected: Uses `うすぐら`, NOT pykakasi's `はくあん`
- Why it matters: This proves our two-step pipeline correctly prioritizes explicit annotations

**Test 2: Common kanji filtering**
- Input: `日本の学校`
- Expected: No `<ruby>` tags (all common kanji)
- Why it matters: Proves we don't over-annotate and clutter the reading experience

**Test 3: HTML stripping**
- Input: `<script>alert('x')</script><p>Text</p>`
- Expected: `Text` (no script tags)
- Why it matters: Security — malicious or malformed EPUBs can't inject scripts

---

## Summary of Gaps Found During Grilling

1. **File size limit** — No max file size check. 100MB+ EPUBs could crash the server.
2. **State loss on refresh** — All reading progress lost on page refresh. localStorage could save this.
3. **Search scope** — Only searches current page, not all chapters.
4. **No visual distinction** between "common kanji" and "pykakasi failed" — both show no furigana.
5. **Global vocabulary** — Vocab list is not per-book. Reading Book A then Book B mixes vocabulary.

These gaps are documented as known limitations for V1, with clear paths for V2 improvement.
