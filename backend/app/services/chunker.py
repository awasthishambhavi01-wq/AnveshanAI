from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import get_settings


def chunk_pages(pages: list[dict], doc_id: str, filename: str) -> list[dict]:
    """Chunk page by page so every chunk keeps its page number."""
    s = get_settings()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=s.chunk_size,
        chunk_overlap=s.chunk_overlap,
    )
    chunks = []
    for p in pages:
        if not p["text"]:
            continue
        for idx, text in enumerate(splitter.split_text(p["text"])):
            chunks.append(
                {
                    "id": f"{doc_id}_p{p['page']}_c{idx}",
                    "text": text,
                    "metadata": {
                        "doc_id": doc_id,
                        "filename": filename,
                        "page": p["page"],
                        "chunk_index": idx,
                    },
                }
            )
    return chunks