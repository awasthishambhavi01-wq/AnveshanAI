from app.core.config import get_settings
from app.services.chunker import chunk_pages


def test_chunks_keep_page_metadata_and_skip_empty_pages():
    pages = [
        {"page": 1, "text": "alpha " * 300},
        {"page": 2, "text": ""},
        {"page": 3, "text": "beta " * 50},
    ]

    chunks = chunk_pages(pages, "doc1", "f.pdf")

    assert {c["metadata"]["page"] for c in chunks} == {1, 3}
    assert all(c["metadata"]["doc_id"] == "doc1" for c in chunks)
    assert all(c["metadata"]["filename"] == "f.pdf" for c in chunks)
    assert len({c["id"] for c in chunks}) == len(chunks)  # ids are unique
    assert max(len(c["text"]) for c in chunks) <= get_settings().chunk_size