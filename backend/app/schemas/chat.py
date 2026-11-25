from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    session_id: str | None = None  # used from the memory stage onward
    doc_ids: list[str] | None = None


class Source(BaseModel):
    id: int  # matches the [1], [2] markers in the answer
    filename: str
    page: int
    snippet: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]