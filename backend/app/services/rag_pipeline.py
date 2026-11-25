import logging
import time

from app.core.config import get_settings
from app.services import llm
from app.services.prompt_builder import NOT_FOUND_MESSAGE, build_messages
from app.services.retriever import retrieve

logger = logging.getLogger(__name__)

SNIPPET_LEN = 300


def ask(question: str, doc_ids: list[str] | None = None) -> dict:
    s = get_settings()

    t0 = time.perf_counter()
    chunks = retrieve(question, s.top_k, doc_ids, min_score=s.score_threshold)
    retrieve_ms = (time.perf_counter() - t0) * 1000

    # Anti-hallucination guard: nothing relevant -> do not call the LLM at all
    if not chunks:
        logger.info("No chunks above threshold %.2f (retrieve %.0f ms)", s.score_threshold, retrieve_ms)
        return {"answer": NOT_FOUND_MESSAGE, "sources": []}

    t1 = time.perf_counter()
    answer = llm.generate(build_messages(question, chunks))
    generate_ms = (time.perf_counter() - t1) * 1000
    logger.info("retrieve %.0f ms | generate %.0f ms | %d chunks", retrieve_ms, generate_ms, len(chunks))
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