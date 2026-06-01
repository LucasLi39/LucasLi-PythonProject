import os
import shutil
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from parser import parse_file
from annotator import annotate_text

app = FastAPI()

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Serve static files
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


@app.get("/")
async def root():
    """Serve the main HTML page."""
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a book file (EPUB or TXT), parse and annotate it."""
    # Validate file extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ('.epub', '.txt'):
        raise HTTPException(status_code=400, detail="Only .epub and .txt files are supported")

    # Save uploaded file temporarily
    upload_path = UPLOAD_DIR / file.filename
    try:
        with open(upload_path, 'wb') as f:
            shutil.copyfileobj(file.file, f)

        # Parse the file
        book_data = parse_file(str(upload_path))

        # Annotate each chapter with furigana
        annotated_chapters = []
        for chapter in book_data["chapters"]:
            annotated = annotate_text(chapter["content"])
            # Wrap text in paragraphs for pagination
            paragraphs = annotated.split('\n')
            html_paragraphs = ''.join(
                f'<p>{p.strip()}</p>' if p.strip() else ''
                for p in paragraphs
            )
            annotated_chapters.append({
                "title": chapter["title"],
                "content": html_paragraphs
            })

        return {
            "title": book_data["title"],
            "chapters": annotated_chapters
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up uploaded file
        if upload_path.exists():
            upload_path.unlink()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
