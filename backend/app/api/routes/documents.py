from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db import crud
from app.db.database import get_db
from app.schemas.document import DocumentOut, UploadResponse
from app.services.ingestion import ingest_pdf

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=UploadResponse)
def upload_document(file: UploadFile, db: Session = Depends(get_db)):
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    data = file.file.read()
    if not data.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="File is not a valid PDF")

    doc, duplicate = ingest_pdf(db, file.filename, data)
    return UploadResponse(
        id=doc.id, filename=doc.filename, status=doc.status, duplicate=duplicate
    )


@router.get("", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db)):
    return crud.list_documents(db)


@router.delete("/{doc_id}")
def delete_document(doc_id: str, db: Session = Depends(get_db)):
    doc = crud.get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    pdf_path = get_settings().uploads_dir / f"{doc.id}.pdf"
    pdf_path.unlink(missing_ok=True)
    # TODO (next stage): also delete this document's vectors from Chroma
    crud.delete_document(db, doc)
    return {"deleted": True}