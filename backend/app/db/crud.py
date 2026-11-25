import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ChatSession, Document, Message


# ---------- documents ----------

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


# ---------- sessions and messages ----------

def create_session(db: Session) -> ChatSession:
    s = ChatSession()
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def get_session(db: Session, session_id: str) -> ChatSession | None:
    return db.get(ChatSession, session_id)


def list_messages(db: Session, session_id: str) -> list[Message]:
    return list(
        db.scalars(
            select(Message).where(Message.session_id == session_id).order_by(Message.id)
        )
    )


def get_recent_messages(db: Session, session_id: str, limit: int) -> list[Message]:
    rows = db.scalars(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.id.desc())
        .limit(limit)
    ).all()
    return list(reversed(rows))  # oldest first


def add_message(
    db: Session,
    session_id: str,
    role: str,
    content: str,
    sources: list[dict] | None = None,
) -> Message:
    msg = Message(
        session_id=session_id,
        role=role,
        content=content,
        sources_json=json.dumps(sources) if sources else None,
    )
    db.add(msg)
    db.commit()
    return msg