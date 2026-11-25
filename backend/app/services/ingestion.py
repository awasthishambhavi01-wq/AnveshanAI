import logging

from sqlalchemy.orm import Session
from app.services.embedder import get_embedder
from app.services.vector_store import get_vector_store
from app.core.config import get_settings
from app.db import crud
from app.db.models import Document
from app.services.chunker import chunk_pages
from app.services.pdf_loader import extract_pages
from app.utils.file_hash import sha256_bytes

logger = logging.getLogger(__name__)


def ingest_pdf(db: Session, filename: str, data: bytes) -> tuple[Document, bool]:
    """Returns (document, is_duplicate)."""
    settings = get_settings()

    file_hash = sha256_bytes(data)
    existing = crud.get_document_by_hash(db, file_hash)
    if existing:
        return existing, True

    doc = crud.create_document(db, filename, file_hash)
    path = settings.uploads_dir / f"{doc.id}.pdf"
    path.write_bytes(data)

    try:
        pages = extract_pages(path)
        chunks = chunk_pages(pages, doc.id, filename)
        if not chunks:
            raise ValueError("No extractable text (scanned PDF?)")

        # Embed the text and store it in the vector store
        embeddings = get_embedder().embed_documents([c["text"] for c in chunks])
        get_vector_store().add_chunks(chunks, embeddings)

        doc = crud.update_document(
            db, doc, status="ready", pages=len(pages), num_chunks=len(chunks)
        )
        logger.info("Ingested %s: %d pages, %d chunks", filename, len(pages), len(chunks))
    except Exception as exc:
        logger.exception("Ingestion failed for %s", filename)
        get_vector_store().delete_by_doc(doc.id)  # no half-indexed documents
        doc = crud.update_document(db, doc, status="failed", error=str(exc))

    return doc, False