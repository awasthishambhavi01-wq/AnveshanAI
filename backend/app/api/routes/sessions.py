import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import crud
from app.db.database import get_db
from app.schemas.chat import MessageOut, SessionOut

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionOut)
def create_session(db: Session = Depends(get_db)):
    return SessionOut(session_id=crud.create_session(db).id)


@router.get("/{session_id}/messages", response_model=list[MessageOut])
def get_messages(session_id: str, db: Session = Depends(get_db)):
    if not crud.get_session(db, session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return [
        MessageOut(
            role=m.role,
            content=m.content,
            sources=json.loads(m.sources_json) if m.sources_json else None,
        )
        for m in crud.list_messages(db, session_id)
    ]