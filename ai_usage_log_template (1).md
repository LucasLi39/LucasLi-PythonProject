# AI Usage Log

## Entry 1

### Date
2026-05-25

### AI Tool Used
Claude Code (Anthropic)

### What I Asked AI
Help me define the scope of my Japanese reading app (KanjiLens) and fill out the Final Project PRD template.

### Why I Asked
I had a rough idea — a reading app that annotates Japanese kanji with furigana — but I needed to narrow it down to a realistic v1 MVP. I was unsure about the technical stack, file formats, and which features to include vs. cut.

### What AI Gave Me
A series of "grilling" questions that forced me to make concrete decisions:
- Python backend (FastAPI) + vanilla JS frontend
- EPUB and TXT support only
- Japanese only (v1)
- Free offline library (pykakasi) instead of paid API
- Only annotate uncommon kanji (JLPT N5/N4 as common baseline)
- No user accounts for v1
- A complete filled-out PRD document

### What I Used
All of it. The PRD became the blueprint for the entire project.

### What I Changed or Rejected
- Initially wanted "Apple Books-like pages" — AI pushed me to accept a simpler scrollable text for v1
- Initially wanted to annotate *every* kanji — AI suggested annotating only uncommon ones to avoid visual clutter

### What I Still Do Not Fully Understand
How the pagination logic in the frontend (measuring DOM height dynamically) works under the hood. I understand what it does but not the exact browser rendering timing.

### My Next Step
Start implementing the codebase based on the PRD.

---

## Entry 2

### Date
2026-05-26

### AI Tool Used
Claude Code (Anthropic)

### What I Asked AI
Build the entire KanjiLens web application for me.

### Why I Asked
I needed a working prototype fast for my class presentation. While I understand Python basics, I had never built a full-stack web app with FastAPI, and I was unfamiliar with Japanese text processing libraries.

### What AI Gave Me
A complete working codebase:
- `main.py` — FastAPI server with file upload endpoint
- `annotator.py` — pykakasi-based furigana engine with explicit parenthesis parsing
- `parser.py` — EPUB/TXT file parsing (ebooklib)
- `common_kanji.py` — JLPT N5/N4 kanji filter set
- `static/index.html` — Upload page + reader UI
- `static/style.css` — Book-like styling with ruby text
- `static/app.js` — Upload handling, pagination, furigana toggle
- Installed all dependencies and tested end-to-end

### What I Used
All of the code. I ran the server locally and verified it works with test files.

### What I Changed or Rejected
- Later asked AI to add a feature: if a kanji already has furigana in parentheses in the text (e.g. 吾輩（わがはい）), extract that instead of using pykakasi. AI added this to `annotator.py`.
- Did not deploy to the cloud — kept it local for the presentation.

### What I Still Do Not Fully Understand
- Regular expressions in `annotator.py` — I know they match patterns but I don't fully understand the Unicode ranges (e.g. `[一-鿿㐀-䶿]`)
- How pykakasi's internal dictionary lookup works — it's a black box to me
- The exact mechanics of FastAPI's `UploadFile` and how it handles file streaming

### My Next Step
Prepare presentation materials and test the demo.

---

## Entry 3

### Date
2026-05-27

### AI Tool Used
Claude Code (Anthropic)

### What I Asked AI
Read the Final Product Presentation template PPTX and fill it with KanjiLens content.

### Why I Asked
The teacher requires a presentation for the final project, and I needed to structure my talking points clearly. I also cannot directly edit PPTX files programmatically.

### What AI Gave Me
A filled PPTX file (`KanjiLens-Presentation.pptx`) with all 7 slides completed:
- Slide 1: Title slide with project name and my name
- Slide 2: Problem description, target user, why it matters
- Slide 3: One-sentence solution + how it works in plain English
- Slide 4: 3 key features (smart annotation, EPUB/TXT support, paginated reader)
- Slide 5: Technical details (data structures, libraries, architecture, code snippet)
- Slide 6: Demo instructions (kept template tips)
- Slide 7: Reflection (challenges, learnings, next steps)

### What I Used
The entire presentation file. I will open it in Keynote/PowerPoint to present.

### What I Changed or Rejected
Nothing yet — may adjust formatting or add screenshots during the demo.

### What I Still Do Not Fully Understand
N/A — this was a straightforward content generation task.

### My Next Step
Present the project in class. Run the live demo showing file upload and furigana annotation.

---

## Summary

| Tool | Purpose | Code Written By AI? |
|------|---------|---------------------|
| Claude Code | PRD scoping, architecture decisions | No (decisions only) |
| Claude Code | Full-stack app implementation | Yes (100% of code) |
| Claude Code | Explicit furigana feature addition | Yes |
| Claude Code | PPTX presentation content | Yes (content only) |

**My honest assessment:** I designed the concept and made all product decisions (with AI's prompting questions). However, 100% of the actual code — backend, frontend, parsing, annotation logic, styling — was written by AI. I understand the high-level flow and can explain each file's purpose, but I could not reproduce the regex patterns, the DOM pagination logic, or the EPUB parsing from memory without reference. The explicit furigana feature was my idea, but AI implemented it.
