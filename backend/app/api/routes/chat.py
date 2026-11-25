from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import crud
from app.db.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_pipeline import ask

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    if req.session_id and not crud.get_session(db, req.session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return ask(db, question, req.doc_ids, req.session_id)