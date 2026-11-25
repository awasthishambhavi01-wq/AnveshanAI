from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Document


def get_document(db: Session, doc_id: str) -> Document | None:
    return db.get(Document, doc_id)


def get_document_by_hash(db: Session, file_hash: str) -> Document | None:
    return db.scalar(select(Document).where(Document.file_hash == file_hash))


def list_documents(db: Session) -> list[Document]:
    return list(db.scalars(select(Document).order_by(Document.created_at.desc())))


def create_document(db: Session, filename: str, file_hash: str) -> Document:
    doc = Document(filename=filename, file_hash=file_hash, status="processing")
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def update_document(db: Session, doc: Document, **fields) -> Document:
    for key, value in fields.items():
        setattr(doc, key, value)
    db.commit()
    db.refresh(doc)
    return doc


def delete_document(db: Session, doc: Document) -> None:
    db.delete(doc)
    db.commit()