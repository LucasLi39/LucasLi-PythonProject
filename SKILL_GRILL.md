# Skill-Grill Reflection — KanjiLens V2

This document records the Skill-Grill process applied to KanjiLens after receiving teacher feedback. The goal was not to "fix bugs" but to pressure-test the project architecture, identify structural weaknesses, and guide a second iteration.

---

## The Feedback (Starting Point)

My teacher's feedback was specific and actionable:

1. Push actual working source code
2. Organize the project folder
3. Make the main file visible
4. Add setup instructions
5. Provide a deployed or runnable version

But the regrill requirement went deeper: **use the Skill-Grill process to pressure-test the next version**, not just patch surface issues.

---

## Skill-Grill Questions Applied

### Q1: Is the entry point obvious to someone who has never seen this code?

**Finding:** No. `main.py` is a generic name. A teacher or peer reviewer should immediately know which file to run.

**Change:** Renamed `main.py` → `app.py`. This is the standard convention for FastAPI/Flask applications. Anyone familiar with Python web frameworks knows `app.py` is the entry point.

---

### Q2: Can someone else run this project without asking me questions?

**Finding:** No. There was no README with setup steps. Dependencies were not documented clearly.

**Change:** Rewrote `README.md` with a clear Prerequisites → Clone → Install → Run → Test flow. Each step includes the exact command. Listed all required packages with explanations of what each does (`fastapi`, `pykakasi`, `ebooklib`, etc.).

---

### Q3: Is the code organized into logical modules with single responsibilities?

**Finding:** Partially. The backend had separation (parser, annotator, common_kanji), but `app.py` mixed HTTP handling, file I/O, and HTML formatting in one function.

**Assessment:** For a V1 MVP, the module split is reasonable:
- `parser.py` — file parsing only
- `annotator.py` — furigana logic only
- `common_kanji.py` — data/lookup only
- `app.py` — HTTP layer only (though it does wrap text in `<p>` tags)

**Decision:** Keep the current structure but document it clearly. For V3, `app.py`'s paragraph-wrapping logic could move to a `formatter.py` module, but that would be premature abstraction at this stage.

---

### Q4: Is there any way to verify the code works without manually uploading a file?

**Finding:** No. There were no automated tests. Every verification required running the full server and uploading a file through the browser.

**Change:** Added 45 unit tests across three test modules:

| Test File | Coverage | Key Tests |
|-----------|----------|-----------|
| `test_common_kanji.py` | Kanji filtering | Common kanji skipped, uncommon kanji flagged, set size sanity check |
| `test_annotator.py` | Furigana engine | Explicit furigana extraction, pykakasi fallback, hiragana passthrough, no double-annotation |
| `test_parser.py` | File parsing | HTML stripping, title extraction, chapter splitting, encoding preservation |

**Why unittest:** Chose Python's built-in `unittest` over `pytest` to avoid adding another dependency. The tests run with `python3 -m unittest discover -v tests/`.

---

### Q5: What happens when the "happy path" assumptions break?

**Finding:** Several edge cases were not handled:

1. **pykakasi accuracy:** Compound kanji words like 薄暗 are read incorrectly (はくあん instead of うすぐら) because pykakasi does dictionary lookup without context.
   - **Solution:** Added explicit furigana extraction from parentheses. If the text already contains `漢字（かんじ）`, use that reading instead of guessing.

2. **EPUB HTML complexity:** Real EPUBs contain scripts, images, SVGs, and complex CSS that break text extraction.
   - **Solution:** `parser.py` strips `<script>`, `<style>`, `<img>`, and `<svg>` tags before extracting text. Block elements are converted to newlines to preserve paragraph structure.

3. **Already-annotated text:** If explicit furigana is extracted first, the remaining text should not re-annotate those ruby blocks.
   - **Solution:** `annotator.py` skips over existing `<ruby>...</ruby>` blocks during the second pass.

---

### Q6: Is the tech stack defensible?

**Finding:** Yes, with tradeoffs.

| Choice | Rationale | Tradeoff |
|--------|-----------|----------|
| **FastAPI** | Lightweight, async-native, great for file upload APIs | Requires understanding of ASGI/uvicorn |
| **pykakasi** | Free, offline, no API keys | ~85% accuracy on compound words; mitigated by explicit furigana feature |
| **ebooklib** | Mature EPUB parsing library | Complex EPUBs may have edge cases; we strip non-text elements |
| **Vanilla JS frontend** | No build step, no dependencies | Limited to basic UI; acceptable for V1 |
| **CSS `<ruby>` tags** | Native browser support, no JS rendering | Older browsers may not render perfectly |

**Defensible position:** For a student MVP with a "Python only" requirement, these are the right choices. A commercial product might use a cloud NLP API (Google Cloud, AWS) for better accuracy, but that violates the offline/free constraint.

---

### Q7: How was AI used, and what decisions were mine?

**AI usage breakdown:**

| Task | AI Role | My Decision |
|------|---------|-------------|
| PRD scoping | AI asked clarifying questions | I chose the feature set (EPUB/TXT, toggle, pagination) |
| Full code implementation | AI wrote all code | I chose the tech stack (FastAPI, pykakasi, ebooklib) |
| Explicit furigana feature | AI implemented the regex | I identified the problem (pykakasi accuracy) and proposed the solution |
| Project reorganization | AI reorganized files | I chose the naming conventions and structure |
| Unit tests | AI wrote all tests | I reviewed and approved the coverage areas |
| README/Documentation | AI wrote the content | I specified the target audience (a teacher grading the project) |

**Key insight:** AI was a code-generation tool, but all product, architecture, and quality decisions were mine. The Skill-Grill process helped me articulate *why* each choice was made.

---

## Summary of Changes (V1 → V2)

| Area | V1 State | V2 Improvement |
|------|----------|----------------|
| Entry point | `main.py` (ambiguous) | `app.py` (standard FastAPI convention) |
| Project structure | Flat, messy filenames | Clean names, `tests/` directory |
| Setup instructions | None | Full README with step-by-step commands |
| Tests | None | 45 unit tests covering all core modules |
| AI tracking | Template file | Completed `AI_USAGE_LOG.md` |
| Documentation | Minimal | `README.md` + `PRD.md` + `AI_USAGE_LOG.md` + this file |
| Error handling | Basic try/except | Preserved; no new failure modes introduced |

---

## What Skill-Grill Helped Me See

1. **Naming matters for readability.** `app.py` vs `main.py` is a small change with outsized impact on discoverability.

2. **Tests are not optional for maintainability.** Without tests, every change risks breaking something. The 45 tests now act as a safety net.

3. **The "good enough" threshold.** Not every module needs further splitting. `app.py` wrapping text in `<p>` tags is acceptable for V1. Over-engineering is as bad as under-engineering.

4. **Defensible tradeoffs.** pykakasi is not perfect, but the explicit furigana feature mitigates its weakness. This is a better answer than "I used a perfect library" (which doesn't exist).

---

*Completed for regrade submission. Sunday night deadline.*
