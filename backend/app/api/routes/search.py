from fastapi import APIRouter, HTTPException

from app.schemas.search import SearchRequest, SearchResult
from app.services.retriever import retrieve

router = APIRouter(tags=["search"])


@router.post("/search", response_model=list[SearchResult])
def search(req: SearchRequest):
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    return retrieve(query, req.top_k, req.doc_ids)