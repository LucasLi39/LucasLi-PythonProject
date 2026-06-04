# KanjiLens

A web app that automatically annotates uncommon kanji with furigana (pronunciation guides) in Japanese books, helping learners read native content without constant dictionary lookups.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136+-green)

## What It Does

Upload a Japanese `.epub` or `.txt` file → KanjiLens analyzes the text → Uncommon kanji get furigana annotations → Read in a clean, paginated viewer.

### Key Features

| Feature | Description |
|---------|-------------|
| **Smart Furigana** | Only annotates uncommon kanji (outside JLPT N5/N4). Common kanji like 人, 日, 月 are left clean. |
| **Two Annotation Sources** | 1) Explicit furigana from text: `漢字（かんじ）` → `<ruby>漢字<rt>かんじ</rt></ruby>`. 2) Automatic via pykakasi for remaining kanji. |
| **Toggle On/Off** | One button to show/hide all furigana annotations. |
| **EPUB & TXT Support** | Upload `.epub` (preserves chapters) or `.txt` (plain text) files. |
| **Paginated Reader** | Book-like reading interface with chapter navigation, page controls, and keyboard shortcuts. |

## How to Run Locally

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone https://github.com/LucasLi39/LucasLi-PythonProject.git
cd LucasLi-PythonProject
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `fastapi` — Web framework
- `uvicorn` — ASGI server
- `python-multipart` — File upload handling
- `ebooklib` — EPUB parsing
- `pykakasi` — Kanji to hiragana conversion
- `lxml` — HTML processing

### Step 3: Run the Server

```bash
python3 app.py
```

You should see output like:
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 4: Open in Browser

Go to [http://localhost:8000](http://localhost:8000)

Upload a Japanese `.txt` or `.epub` file and start reading!

### Step 5: Test It

Two sample files are included in `tests/`:

- `tests/test_sample.txt` — Excerpt from *Wagahai wa Neko de Aru* (吾輩は猫である)
- `tests/test_explicit.txt` — Same text with explicit furigana in parentheses

Upload either file to see furigana annotations in action.

## Project Structure

```
LucasLi-PythonProject/
├── app.py                  # Main entry point — FastAPI server
├── annotator.py            # Furigana engine — detects kanji, generates readings
├── parser.py               # File parser — handles EPUB and TXT formats
├── common_kanji.py         # JLPT N5/N4 kanji filter set
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── PRD.md                  # Project Requirements Document
├── AI_USAGE_LOG.md         # AI usage tracking log
├── static/                 # Frontend files
│   ├── index.html          # Upload page + reader UI
│   ├── style.css           # Book-like styling
│   └── app.js              # Upload handling, pagination, toggle
└── tests/                  # Sample files for testing
    ├── test_explicit.txt
    └── test_sample.txt
```

## How It Works

```
User uploads file (.epub or .txt)
        |
        v
   parser.py extracts text
        |
        v
   annotator.py processes text
   ├── Step 1: Extract explicit furigana
   │   "漢字（かんじ）" → <ruby>漢字<rt>かんじ</rt></ruby>
   │
   └── Step 2: pykakasi for remaining kanji
       "吾輩" → <ruby>吾輩<rt>わがはい</rt></ruby>
       "猫" → 猫 (common kanji, skip)
        |
        v
   JSON response to frontend
        |
        v
   Browser renders paginated reader
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python, FastAPI |
| **Frontend** | HTML, CSS, JavaScript (vanilla) |
| **Kanji Processing** | pykakasi (kanji → hiragana) |
| **EPUB Parsing** | ebooklib |

## License

For educational use.
