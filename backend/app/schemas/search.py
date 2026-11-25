from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    doc_ids: list[str] | None = None


class SearchResult(BaseModel):
    text: str
    score: float
    filename: str
    page: int
    doc_id: str