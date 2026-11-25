import logging
from abc import ABC, abstractmethod
from functools import lru_cache

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class VectorStore(ABC):
    @abstractmethod
    def add_chunks(self, chunks: list[dict], embeddings: list[list[float]]) -> None: ...

    @abstractmethod
    def search(
        self, query_embedding: list[float], top_k: int, doc_ids: list[str] | None = None
    ) -> list[dict]: ...

    @abstractmethod
    def delete_by_doc(self, doc_id: str) -> None: ...


class ChromaVectorStore(VectorStore):
    def __init__(self, path: str, collection_name: str = "chunks"):
        self.client = chromadb.PersistentClient(
            path=path,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(self, chunks: list[dict], embeddings: list[list[float]]) -> None:
        if not chunks:
            return
        self.collection.upsert(
            ids=[c["id"] for c in chunks],
            documents=[c["text"] for c in chunks],
            embeddings=embeddings,
            metadatas=[c["metadata"] for c in chunks],
        )

    def search(
        self, query_embedding: list[float], top_k: int, doc_ids: list[str] | None = None
    ) -> list[dict]:
        where = None
        if doc_ids:
            where = (
                {"doc_id": doc_ids[0]}
                if len(doc_ids) == 1
                else {"doc_id": {"$in": doc_ids}}
            )

        res = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        results = []
        for text, meta, dist in zip(
            res["documents"][0], res["metadatas"][0], res["distances"][0]
        ):
            results.append(
                {
                    "text": text,
                    "score": round(1 - dist, 4),  # cosine distance -> similarity
                    "doc_id": meta["doc_id"],
                    "filename": meta["filename"],
                    "page": meta["page"],
                }
            )
        return results

    def delete_by_doc(self, doc_id: str) -> None:
        self.collection.delete(where={"doc_id": doc_id})


@lru_cache
def get_vector_store() -> VectorStore:
    return ChromaVectorStore(path=str(get_settings().chroma_dir))