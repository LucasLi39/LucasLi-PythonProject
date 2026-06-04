# Final Project PRD

## Project Title

**KanjiLens** — A Japanese Reading App with Furigana Annotations

## One Sentence Pitch

My project is a web app that lets users upload Japanese books (EPUB/TXT) and automatically annotates uncommon kanji with furigana (pronunciation guides) so learners can read without constantly looking up readings.

## Target User

This project is for Japanese language learners (beginner to intermediate) who can read hiragana/katakana and some basic kanji, but struggle with less common kanji when reading real Japanese books.

## Purpose

This is useful because reading native Japanese content is one of the best ways to improve, but learners hit a wall when they encounter unfamiliar kanji. Existing solutions either annotate everything (visual clutter) or require manual lookups (slow). KanjiLens smartly annotates only uncommon kanji and lets users toggle annotations on/off, keeping the reading experience clean.

## MVP

The smallest working version will:
- Let a user upload an EPUB or TXT file containing Japanese text
- Parse the file and detect kanji
- Use pykakasi to generate furigana readings for uncommon kanji
- Display the text in a clean, scrollable reader with ruby annotations over uncommon kanji
- Allow the user to toggle all furigana annotations on/off
- Auto-paginate the content into readable chunks

## Must Have Features

1. **File upload** — Accept EPUB and TXT files via a web interface
2. **EPUB parsing** — Extract text content from EPUB files (preserving structure/styling, skipping images)
3. **Kanji detection & furigana annotation** — Use pykakasi to identify kanji and generate hiragana readings; annotate only uncommon kanji (e.g., outside JLPT N5–N4 level or below a frequency threshold)
4. **Reading view** — Scrollable text display with HTML ruby annotations (`<ruby>` tags)
5. **Furigana toggle** — Button to show/hide all furigana annotations
6. **Auto-pagination** — Split content into page-sized chunks

## Nice To Have Features

1. **Chapter navigation** — Sidebar or dropdown to jump between EPUB chapters
2. **Reading progress indicator** — Show which page/chapter the user is on

## Stretch Feature

1. **Click-to-annotate** — Click any kanji (even common ones) to see its reading on demand, without cluttering the full page

## Python Skills I Might Use

### Functions
- Parsing functions for EPUB structure extraction
- Text processing pipeline (raw text → kanji detection → furigana injection)

### Lists
- Ordered list of chapters from EPUB spine
- Paginated chunks of text

### Dictionaries
- Kanji-to-reading mappings from pykakasi output
- Kanji frequency/commonality lookup table
- Book metadata (title, author) from EPUB

### APIs
- FastAPI endpoints: upload file, get chapter content, get paginated pages

### File I/O
- Reading uploaded EPUB/TXT files from disk
- Writing processed/annotated HTML output

### OOP
- Book class (metadata, chapters, pages)
- Chapter class (content, page splits)
- Annotation/Word class (original text, reading, is_uncommon flag)

### Error Handling
- Invalid file format rejection
- Empty/corrupt EPUB handling
- pykakasi parse failures (graceful fallback to unannotated text)

## Data Plan

**What data does my project need?**
- Uploaded book files (EPUB or TXT)
- Kanji frequency/commonality data (to determine which kanji are "uncommon")
- pykakasi dictionary (bundled with the library)

**Where will the data come from?**
- User uploads (book files)
- pykakasi's built-in IPAdic dictionary for readings
- A kanji frequency list (e.g., from Wikipedia frequency data or JLPT level lists) to classify common vs. uncommon

**How will I store or organize the data?**
- Uploaded files stored temporarily in a local `uploads/` directory, deleted after session ends
- No database — stateless for v1 (upload → read → done)
- Processed book content held in memory during the reading session

## First Tiny Step

The first thing I need to build is: a minimal FastAPI app that accepts a TXT file upload, runs pykakasi on it to detect kanji and generate furigana, and returns the annotated text as HTML with `<ruby>` tags.

## Possible Risk

The hardest parts might be:
- **EPUB parsing complexity** — EPUBs vary wildly in structure; some use complex CSS or non-standard markup that breaks naive parsing
- **pykakasi accuracy** — It uses dictionary-based lookup, so it may pick wrong readings for kanji with multiple possible readings in context (e.g., 生). For v1, we accept "most common reading" as good enough
- **Performance** — Large books (500+ pages) could be slow to process if we annotate everything upfront; may need to process per-chapter on demand
