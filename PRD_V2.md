# PRD v2 — KanjiLens

**Project Type:** Web app (FastAPI backend + vanilla JavaScript frontend)
**Version:** 2.0 (second iteration based on Skill-Grill process)
**Date:** 2026-06-07

---

## Part 1: Project Identity

**KanjiLens** is a web app that helps Japanese self-learners read native content (light novels, web fiction, short stories) by automatically annotating uncommon kanji with furigana (pronunciation guides). Users upload EPUB or TXT files and read in a clean, paginated viewer where only unfamiliar kanji get annotated — keeping the experience immersive, not cluttered.

**Target user:** A self-learner (age 16-30) who has mastered hiragana/katakana and basic kanji (JLPT N5-N4 level) but gets stuck when reading native Japanese books. They want to read real content, not textbook passages, without stopping every other sentence to look up readings.

**Why this project:** I am this user. I tried importing Japanese light novels into Apple Books, but it either failed to import EPUBs or showed no furigana at all for TXT files. Existing solutions annotate every kanji (visual overload) or require manual lookup (breaks reading flow). KanjiLens finds the balance: annotate only what's needed, let the user toggle, and make it feel like reading a real book.

---

## Part 2: Feature Scope — The "Must-Have" List

### Feature 1: File Upload & Parse

**What it does:** Accepts EPUB or TXT files via a web upload form, validates the format, parses the content into structured chapters, and returns annotated HTML.

**Why it matters:** This is the entry point. Without it, the app has no content to display.

**User flow:**
1. User opens browser at `http://localhost:8000` → sees KanjiLens homepage
2. User clicks "Choose an EPUB or TXT file" → file picker opens
3. User selects a file → filename appears below the upload area
4. User clicks "Upload & Read" → loading spinner shows "Analyzing kanji..."
5. Server parses the file, annotates kanji, returns JSON with chapters
6. Reader view appears with the first page of Chapter 1

**Edge cases:**
- User uploads PDF or unsupported format → Alert: "Only .epub and .txt files are supported"
- User uploads corrupt EPUB → Alert: "Error: [exception message]" (HTTP 500, generic message for security)
- User uploads very large file (>>50MB) → Should reject with size limit message (not yet implemented in V1, planned for V2)

---

### Feature 2: Smart Furigana Annotation

**What it does:** Two-step annotation pipeline. Step 1 extracts explicit furigana already present in the text (e.g., `漢字（かんじ）`). Step 2 uses pykakasi to auto-generate readings for remaining uncommon kanji. Common kanji (JLPT N5/N4) are left unannotated.

**Why it matters:** This is the core value. Without smart filtering, the page would be covered in ruby text. Without explicit extraction, pykakasi would misread compound words like 薄暗 as はくあん instead of うすぐら.

**User flow:**
1. User uploads a file (no direct user action — happens automatically)
2. Server runs the annotation pipeline on each chapter
3. Reader displays text with `<ruby>漢字<rt>かんじ</rt></ruby>` tags over uncommon kanji
4. User reads naturally; unfamiliar kanji have small readings above them

**Edge cases:**
- Text contains no kanji at all (all hiragana) → Returns unchanged, no annotations
- pykakasi fails to generate a reading → Kanji passes through unannotated (graceful degradation)
- Already-annotated `<ruby>` blocks from explicit extraction → Skipped by Step 2 to prevent double-annotation

---

### Feature 3: Paginated Reader with Chapter Navigation

**What it does:** Displays annotated text in book-like pages that fit the viewport. Users can navigate forward/backward and jump between chapters via a dropdown.

**Why it matters:** Raw HTML dumped on one screen is overwhelming. Pagination creates a natural reading rhythm.

**User flow:**
1. Book loads → first page of Chapter 1 is displayed
2. User clicks "Next →" or presses Space/→ → advances to next page
3. User clicks "← Prev" or presses ← → goes back
4. User selects a chapter from the dropdown → jumps to that chapter's first page
5. Page counter shows "Page X of Y" at the bottom

**Edge cases:**
- User presses Next on the last page → Button disabled, key press ignored
- Chapter has very little content → Displayed as a single short page (acceptable)
- Window is resized → Content is re-paginated automatically after 250ms debounce

---

### Feature 4: Vocabulary Bookmark

**What it does:** Users can click any annotated kanji to save it to a personal vocabulary list. The list persists in localStorage and can be viewed in a sidebar.

**Why it matters:** Reading is only half of learning. Saving unknown words for later review turns passive reading into active vocabulary building.

**User flow:**
1. User encounters an unfamiliar annotated kanji while reading
2. User clicks the kanji → brief green flash appears as feedback
3. Header button updates from "📖 Vocab (0)" to "📖 Vocab (1)"
4. User clicks "📖 Vocab (n)" → sidebar slides in from the right
5. Sidebar shows saved entries: kanji + reading, with a delete button each
6. User clicks ✕ to remove a word

**Edge cases:**
- User clicks same kanji twice → No duplicate added; no error
- User refreshes the page → Vocab list persists (localStorage)
- User opens vocab sidebar with no saved words → Shows "Click any annotated kanji to save it here."
- Vocab list grows very long → Sidebar is scrollable

---

### Feature 5: In-Book Search

**What it does:** Users can search for kanji characters or hiragana readings within the current page. Matches are highlighted, and users can navigate between them.

**Why it matters:** In a long book, finding a specific word or character you remember seeing is tedious without search.

**User flow:**
1. User types a search term in the header search box (e.g., "わがはい" or "薄暗")
2. User presses Enter or clicks 🔍 → search bar appears below header
3. Matching `<ruby>` tags are highlighted with yellow background
4. Search bar shows "1 / 3" → user clicks ↑ or ↓ to navigate matches
5. User clicks ✕ or presses Escape → search cleared, highlights removed

**Edge cases:**
- Search term has no matches → "No matches" displayed
- User searches while on a page with no matches → "No matches"; user must navigate to another page manually
- User flips pages while search is active → Search re-runs on the new page automatically

---

## Part 3: Data Architecture

### 3a: Data Structure

**API Response from `/upload` endpoint:**

```json
{
    "title": "吾輩は猫である",
    "chapters": [
        {
            "title": "第一章",
            "content": "<p><ruby>吾輩<rt>わがはい</rt></ruby>は猫である。</p>"
        },
        {
            "title": "第二章",
            "content": "<p>どこで生れたかとんと<ruby>見当<rt>けんとう</rt></ruby>がつかぬ。</p>"
        }
    ]
}
```

**Frontend State (JavaScript memory):**

```javascript
{
    chapters: [
        { title: "第一章", content: "<p>...</p>" },
        { title: "第二章", content: "<p>...</p>" }
    ],
    currentChapter: 0,
    currentPage: 0,
    pages: ["<p>...</p>", "<p>...</p>"], // paginated HTML chunks
    furiganaVisible: true
}
```

**Vocabulary (localStorage):**

```json
[
    { "kanji": "吾輩", "reading": "わがはい", "added": "2026-06-07T14:30:00Z" },
    { "kanji": "薄暗", "reading": "うすぐら", "added": "2026-06-07T14:31:00Z" }
]
```

### 3b: Data Flow

```
User selects file (browser)
    ↓
Browser sends multipart/form-data POST to /upload (FastAPI)
    ↓
Server saves file temporarily → parses → annotates → returns JSON
    ↓
Browser receives JSON → stores in JS memory → paginates → renders
    ↓
User reads, clicks kanji → saved to localStorage
    ↓
User searches → scans current page DOM → highlights matches
```

**Storage decisions:**
- Book content: In-memory only (refreshes lost). No database for V1 to keep architecture simple.
- Vocabulary: localStorage (persists across sessions, per-browser).
- Uploaded files: Temporary disk storage, deleted immediately after processing.

---

## Part 4: Function Specifications

### Function 1: `parse_file(file_path: str) -> dict`

```python
def parse_file(file_path: str) -> dict:
    """
    Parse an EPUB or TXT file and return structured book data.

    Dispatches to parse_epub() or parse_txt() based on file extension.

    Args:
        file_path: Absolute path to the uploaded file.

    Returns:
        Dict with keys: "title" (str), "chapters" (list of dicts).
        Each chapter dict has: "title" (str), "content" (str).

    Example:
        >>> parse_file("/tmp/book.epub")
        {"title": "吾輩は猫である", "chapters": [{"title": "第一章", "content": "..."}]}

    Edge cases handled:
        - Unsupported file format → raises ValueError with message
        - Corrupt EPUB → exception propagates to caller (handled in app.py as 500)
    """
```

### Function 2: `annotate_text(text: str) -> str`

```python
def annotate_text(text: str) -> str:
    """
    Annotate uncommon kanji in text with furigana using HTML <ruby> tags.

    Two-step pipeline:
    1. Extract explicit furigana from parentheses (e.g., 漢字（かんじ）)
    2. Use pykakasi for remaining kanji, skipping JLPT N5/N4 common kanji

    Args:
        text: Raw Japanese text string.

    Returns:
        HTML string with <ruby> tags around uncommon kanji.

    Example:
        >>> annotate_text("吾輩は猫である")
        "<ruby>吾輩<rt>わがはい</rt></ruby>は猫である"

    Edge cases handled:
        - Text with no kanji → returns unchanged
        - Already-annotated <ruby> blocks → skipped to prevent double-wrapping
        - pykakasi returns empty reading → kanji passes through unannotated
    """
```

### Function 3: `_extract_explicit_furigana(text: str) -> str`

```python
def _extract_explicit_furigana(text: str) -> str:
    """
    Convert parenthesized furigana patterns to HTML <ruby> tags.

    Matches patterns like 漢字（かんじ）or 漢字(かんじ).

    Args:
        text: Japanese text that may contain explicit furigana.

    Returns:
        Text with matched patterns replaced by <ruby> tags.

    Example:
        >>> _extract_explicit_furigana("薄暗（うすぐら）い")
        "<ruby>薄暗<rt>うすぐら</rt></ruby>い"

    Edge cases handled:
        - Half-width parentheses → matched by regex
        - No explicit furigana in text → returns unchanged
        - Malformed parentheses → regex won't match, falls through silently
    """
```

### Function 4: `is_uncommon(kanji_char: str) -> bool`

```python
def is_uncommon(kanji_char: str) -> bool:
    """
    Return True if a kanji character is uncommon (outside JLPT N5/N4).

    Args:
        kanji_char: A single CJK kanji character.

    Returns:
        True if the kanji is not in the common kanji set.

    Example:
        >>> is_uncommon("輩")
        True
        >>> is_uncommon("日")
        False

    Edge cases handled:
        - Non-kanji character → returns True (caller filters by kanji pattern first)
        - Empty string → returns True
    """
```

### Function 5: `_html_to_text(html_content: str) -> str`

```python
def _html_to_text(html_content: str) -> str:
    """
    Convert EPUB HTML content to clean plain text, preserving structure.

    Strips scripts, styles, images, and SVGs. Converts block elements to newlines.
    Decodes HTML entities.

    Args:
        html_content: Raw HTML string from EPUB document.

    Returns:
        Clean text with paragraphs separated by blank lines.

    Example:
        >>> _html_to_text("<p>Hello</p><script>alert('x')</script>")
        "Hello"

    Edge cases handled:
        - Script/style tags → completely removed (security)
        - HTML entities → decoded (&amp; → &, &lt; → <)
        - Excessive whitespace → collapsed to max 2 newlines
    """
```

---

## Part 5: User Interface & Interaction Design

### 5a: Homepage / Upload Screen

```
┌────────────────────────────────────────────┐
│                                            │
│              KanjiLens                     │
│   日本語の本を読もう — Read Japanese        │
│      books with furigana                   │
│                                            │
│   ┌─────────────────────────────────┐     │
│   │         📚                      │     │
│   │   Choose an EPUB or TXT file    │     │
│   └─────────────────────────────────┘     │
│                                            │
│   test_explicit.txt                        │
│                                            │
│   [Upload & Read]                         │
│                                            │
│   Supports .epub and .txt files           │
│   with Japanese text                       │
│                                            │
└────────────────────────────────────────────┘
```

### 5b: Reader Screen

```
┌──────────────────────────────────────────────────────────────┐
│ ← Back    Book Title      [Search...] [🔍] [あ Furigana]   │
│                           [📖 Vocab (0)] [Chapter ▼]        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   吾輩は猫である。名前はまだ無い。                            │
│                                                              │
│   どこで生れたかとんと見当がつかぬ。                          │
│   何でも薄暗いじめじめした所で                                │
│   ニャーニャー泣いていた事だけは                              │
│   記憶している。                                              │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│           [← Prev]        Page 1 of 5        [Next →]       │
└──────────────────────────────────────────────────────────────┘
```

### 5c: Vocabulary Sidebar (open state)

```
┌──────────────────────────────────────────────────┐
│ Book Title...              ┌────────────────────┐│
│                            │ 📖 Vocabulary    ✕ ││
│                            ├────────────────────┤│
│   (content dimmed)         │ 吾輩    わがはい  ✕││
│                            │ 見当    けんとう  ✕││
│                            │ 薄暗    うすぐら  ✕││
│                            │ 所      ところ    ✕││
│                            │ 事      こと      ✕││
│                            │ 記憶    きおく    ✕││
│                            │                    ││
│                            └────────────────────┘│
└──────────────────────────────────────────────────┘
```

### 5d: Search Active State

```
┌──────────────────────────────────────────────────────────────┐
│ ← Back    Book Title      [わがはい] [🔍] [あ Furigana]    │
│                           [📖 Vocab (0)] [Chapter ▼]        │
├──────────────────────────────────────────────────────────────┤
│ 1 / 3                               ↑  ↓  ✕                 │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   [highlighted]吾輩[/]は猫である。名前はまだ無い。           │
│                                                              │
│   どこで生れたかとんと見当がつかぬ。                          │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│           [← Prev]        Page 1 of 5        [Next →]       │
└──────────────────────────────────────────────────────────────┘
```

### 5e: Error Alert

```
┌─────────────────────────────┐
│  Error: Only .epub and .txt │
│  files are supported        │
│            [OK]             │
└─────────────────────────────┘
```

---

## Part 6: Error Handling & Edge Cases

| # | Error Scenario | App Response | Where Handled |
|---|---------------|-------------|---------------|
| 1 | User uploads unsupported file format (PDF, DOCX, etc.) | Alert dialog: "Error: Only .epub and .txt files are supported" | Backend: `app.py` validates extension; Frontend: catches 400 error |
| 2 | User uploads corrupt or unreadable EPUB | Alert dialog: "Error: [generic message]" | Backend: `parse_file()` raises → `app.py` catches → 500 response |
| 3 | pykakasi gives incorrect reading for compound word (e.g., 薄暗 → はくあん) | User sees no annotation OR incorrect annotation; mitigated by explicit furigana extraction | Backend: two-step pipeline prioritizes explicit furigana |
| 4 | User searches for term with no matches on current page | Search bar shows "No matches"; no highlight | Frontend: search logic checks match count |
| 5 | User refreshes page mid-reading | Book content and reading position lost; user must re-upload | Architectural decision: stateless V1; localStorage could save progress in V2 |
| 6 | User clicks same kanji twice for vocab | No duplicate added; green flash still shows | Frontend: `addToVocab()` checks for existing entry |
| 7 | HTML in EPUB contains `<script>` tags | Tags are stripped during parsing; no script execution | Backend: `_html_to_text()` removes script/style tags |

---

## Part 7: Testing Plan

### Test 1: Explicit Furigana Priority

**What it tests:** The two-step annotation pipeline correctly prioritizes explicit furigana over pykakasi guesses.

**Setup:** Input text: `薄暗（うすぐら）い`

**Expected result:** `<ruby>薄暗<rt>うすぐら</rt></ruby>い` (NOT pykakasi's incorrect はくあん)

**Why it matters:** This is the primary defense against pykakasi's dictionary-lookup limitations.

### Test 2: Common Kanji Filtering

**What it tests:** Kanji in the JLPT N5/N4 set are NOT annotated.

**Setup:** Input text: `日本の学校`

**Expected result:** No `<ruby>` tags — all kanji (日, 本, 学, 校) are common.

**Why it matters:** Prevents visual clutter; keeps the reading experience clean.

### Test 3: HTML Security Stripping

**What it tests:** Malicious or malformed EPUB content cannot inject scripts.

**Setup:** Input HTML: `<script>alert('x')</script><p>Safe text</p>`

**Expected result:** `Safe text` — script tag completely removed.

**Why it matters:** Security. Users upload arbitrary files; we must not execute their content.

### Test 4: Duplicate Vocabulary Prevention

**What it tests:** Clicking the same kanji twice does not create duplicate entries.

**Setup:** User clicks "吾輩" twice.

**Expected result:** Vocab list contains one entry for 吾輩, not two.

**Why it matters:** Data integrity and user experience.

### Test 5: Chapter Splitting for TXT Files

**What it tests:** TXT files with chapter markers are correctly split into chapters.

**Setup:** TXT content with `第一章` and `第二章` markers.

**Expected result:** Two chapters returned, each with correct title and content.

**Why it matters:** Users expect chapter navigation for long books.

---

## Part 8: Stretch Goals (V2 and Beyond)

- [ ] **Reading progress persistence** — Save current chapter/page to localStorage so refresh doesn't lose position
- [ ] **Per-book vocabulary** — Associate saved words with specific books instead of global list
- [ ] **Search across all chapters** — Load and search all chapters, not just current page
- [ ] **JLPT level customization** — Let user choose which JLPT levels to consider "common" (e.g., include N3)
- [ ] **Export annotated text** — Download the annotated HTML as a self-contained file
- [ ] **Word frequency analysis** — Show which kanji appear most often in the book
- [ ] **Dark mode** — Toggle between light and dark reading themes

---

## What Changed from PRD v1 to PRD v2

| Area | PRD v1 | PRD v2 |
|---|---|---|
| Features | 6 must-have, vague descriptions | 5 core features, each with full user flow + 2+ edge cases |
| Data Architecture | Mentioned but no structure shown | Exact JSON with realistic example data + data flow diagram |
| Functions | Named but no specs | 5 functions with full docstrings, args, returns, edge cases |
| UI Design | Described in words | Every screen shown with ASCII mockup of exact text/layout |
| Error Handling | 3 generic cases | 7 specific cases with exact app responses |
| Testing | Not included | 5 test cases with setup, expected result, and rationale |
| New Features | Search and vocab mentioned as "nice to have" | Implemented and fully specified as core features |
