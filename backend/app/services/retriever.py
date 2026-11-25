from app.services.embedder import get_embedder
from app.services.vector_store import get_vector_store


def retrieve(
    query: str,
    top_k: int,
    doc_ids: list[str] | None = None,
    min_score: float | None = None,
) -> list[dict]:
    """Embed the query, search Chroma, optionally drop weak matches."""
    query_vec = get_embedder().embed_query(query)
    results = get_vector_store().search(query_vec, top_k, doc_ids)
    if min_score is not None:
        results = [r for r in results if r["score"] >= min_score]
    return results