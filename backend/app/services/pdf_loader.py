from pathlib import Path

import fitz  # PyMuPDF

from app.utils.text_cleaning import clean_text


def extract_pages(path: Path) -> list[dict]:
    """Return [{"page": 1, "text": "..."}, ...] (1-based page numbers)."""
    with fitz.open(path) as doc:
        return [
            {"page": i + 1, "text": clean_text(page.get_text())}
            for i, page in enumerate(doc)
        ]