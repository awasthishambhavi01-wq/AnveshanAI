import logging
import time

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.services import llm, memory
from app.services.prompt_builder import NOT_FOUND_MESSAGE, build_messages
from app.services.retriever import retrieve

logger = logging.getLogger(__name__)

SNIPPET_LEN = 300


def _answer(search_query: str, doc_ids: list[str] | None) -> dict:
    s = get_settings()

    t0 = time.perf_counter()
    chunks = retrieve(search_query, s.top_k, doc_ids, min_score=s.score_threshold)
    retrieve_ms = (time.perf_counter() - t0) * 1000

    # Anti-hallucination guard: nothing relevant -> do not call the LLM
    if not chunks:
        logger.info("No chunks above threshold %.2f (retrieve %.0f ms)", s.score_threshold, retrieve_ms)
        return {"answer": NOT_FOUND_MESSAGE, "sources": []}

    t1 = time.perf_counter()
    answer = llm.generate(build_messages(search_query, chunks))
    generate_ms = (time.perf_counter() - t1) * 1000
    logger.info("retrieve %.0f ms | generate %.0f ms | %d chunks", retrieve_ms, generate_ms, len(chunks))

    # Model refused: don't attach sources to a "not found" answer
    if NOT_FOUND_MESSAGE.lower() in answer.lower():
        return {"answer": NOT_FOUND_MESSAGE, "sources": []}

    sources = [
        {
            "id": i,
            "filename": c["filename"],
            "page": c["page"],
            "snippet": c["text"][:SNIPPET_LEN],
            "score": c["score"],
        }
        for i, c in enumerate(chunks, start=1)
    ]
    return {"answer": answer, "sources": sources}


def ask(
    db: Session,
    question: str,
    doc_ids: list[str] | None = None,
    session_id: str | None = None,
) -> dict:
    # 1. Load history BEFORE saving this question
    history = memory.load_history(db, session_id) if session_id else []

    # 2. Rewrite follow-ups into standalone questions (skipped when no history)
    search_query = memory.rewrite_question(question, history)

    # 3. Retrieve with the rewritten query, answer from the context
    result = _answer(search_query, doc_ids)
    result["rewritten_question"] = search_query

    # 4. Save both messages only after a successful answer
    if session_id:
        memory.save_exchange(db, session_id, question, result)

    return result