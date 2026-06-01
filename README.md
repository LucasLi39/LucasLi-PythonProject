# KanjiLens

A web app that automatically annotates uncommon kanji with furigana (pronunciation guides) in Japanese books, helping learners read native content without constant dictionary lookups.

## Features

- **Smart Furigana Annotation** — Only annotates uncommon kanji (outside JLPT N5/N4 level). Supports both explicit furigana from text (e.g. `漢字（かんじ）`) and automatic readings via pykakasi.
- **EPUB & TXT Support** — Upload `.epub` or `.txt` files containing Japanese text.
- **Toggle Furigana** — One-click show/hide all annotations.
- **Paginated Reader** — Book-like reading interface with chapter navigation and keyboard shortcuts.

## Tech Stack

- **Backend**: Python, FastAPI
- **Frontend**: Vanilla HTML/CSS/JS
- **Libraries**: pykakasi (kanji→hiragana), ebooklib (EPUB parsing), lxml

## How to Run

```bash
pip install -r requirements.txt
python3 -m uvicorn main:app --reload
```

Open browser at `http://localhost:8000`.

## Project Files

| File | Purpose |
|---|---|
| `main.py` | FastAPI server, upload endpoint |
| `annotator.py` | Furigana engine (explicit + pykakasi) |
| `parser.py` | EPUB/TXT file parsing |
| `common_kanji.py` | JLPT N5/N4 kanji filter |
| `static/index.html` | Upload page + reader UI |
| `static/style.css` | Reader styling |
| `static/app.js` | Upload, pagination, toggle logic |

## Presentation

See `KanjiLens-Presentation.pptx` for the final project presentation.
