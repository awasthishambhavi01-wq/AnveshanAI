import math
import re
import zlib

import pymupdf
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core import config
from app.core.exceptions import LLMError
from app.db.database import Base, get_db
from app.main import app
from app.services.vector_store import VectorStore

DIM = 512


def _vec(text: str) -> list[float]:
    """Bag-of-words hashing: texts that share words get similar vectors."""
    v = [0.0] * DIM
    for w in re.findall(r"[a-z0-9]+", text.lower()):
        v[zlib.crc32(w.encode()) % DIM] += 1.0
    norm = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / norm for x in v]


class FakeEmbedder:
    def embed_documents(self, texts):
        return [_vec(t) for t in texts]

    def embed_query(self, text):
        return _vec(text)


class FakeVectorStore(VectorStore):
    def __init__(self):
        self.items: list[dict] = []

    def add_chunks(self, chunks, embeddings):
        for c, e in zip(chunks, embeddings):
            self.items = [i for i in self.items if i["id"] != c["id"]]
            self.items.append({**c, "embedding": e})

    def search(self, query_embedding, top_k, doc_ids=None):
        pool = [
            i for i in self.items
            if not doc_ids or i["metadata"]["doc_id"] in doc_ids
        ]
        results = [
            {
                "text": i["text"],
                "score": round(sum(a * b for a, b in zip(query_embedding, i["embedding"])), 4),
                "doc_id": i["metadata"]["doc_id"],
                "filename": i["metadata"]["filename"],
                "page": i["metadata"]["page"],
            }
            for i in pool
        ]
        results.sort(key=lambda r: r["score"], reverse=True)
        return results[:top_k]

    def delete_by_doc(self, doc_id):
        self.items = [i for i in self.items if i["metadata"]["doc_id"] != doc_id]


class FakeLLM:
    REWRITE_MARKER = "You rewrite follow-up"

    def __init__(self):
        self.answer = "HBKA is Hash-Based Key Agreement [1]."
        self.rewrite = "What does HBKA use to establish a shared secret key?"
        self.fail = False
        self.calls: list[list[dict]] = []

    def __call__(self, messages, temperature=0.1, max_tokens=300):
        self.calls.append(messages)
        if self.fail:
            raise LLMError("Cannot reach Ollama (test)")
        if messages[0]["content"].startswith(self.REWRITE_MARKER):
            return self.rewrite
        return self.answer

    @property
    def rewrite_calls(self) -> int:
        return sum(1 for c in self.calls if c[0]["content"].startswith(self.REWRITE_MARKER))

    @property
    def answer_calls(self) -> int:
        return len(self.calls) - self.rewrite_calls


@pytest.fixture
def store():
    return FakeVectorStore()


@pytest.fixture
def fake_llm(monkeypatch):
    fake = FakeLLM()
    monkeypatch.setattr("app.services.llm.generate", fake)
    return fake


@pytest.fixture
def testing_session(tmp_path):
    engine = create_engine(
        f"sqlite:///{(tmp_path / 'test.db').as_posix()}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture
def db(testing_session):
    session = testing_session()
    yield session
    session.close()


@pytest.fixture
def client(tmp_path, monkeypatch, store, testing_session):
    # Temp uploads folder: Settings computes paths from BASE_DIR at call time
    (tmp_path / "data" / "uploads").mkdir(parents=True)
    monkeypatch.setattr(config, "BASE_DIR", tmp_path)

    settings = config.get_settings()
    monkeypatch.setattr(settings, "score_threshold", 0.15)
    monkeypatch.setattr(settings, "top_k", 3)

    # Replace the heavy services where they are imported
    embedder = FakeEmbedder()
    for mod in ("app.services.ingestion", "app.services.retriever"):
        monkeypatch.setattr(f"{mod}.get_embedder", lambda: embedder)
    for mod in (
        "app.services.ingestion",
        "app.services.retriever",
        "app.api.routes.documents",
    ):
        monkeypatch.setattr(f"{mod}.get_vector_store", lambda: store)

    def override_get_db():
        session = testing_session()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    # No "with": skips the lifespan, so no model is loaded
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def upload(client):
    def _upload(name: str, data: bytes):
        return client.post("/documents", files={"file": (name, data, "application/pdf")})

    return _upload


@pytest.fixture
def make_pdf():
    def _make(pages: list[str]) -> bytes:
        doc = pymupdf.open()
        for text in pages:
            page = doc.new_page()
            page.insert_textbox(pymupdf.Rect(72, 72, 523, 770), text, fontsize=11)
        data = doc.tobytes()
        doc.close()
        return data

    return _make


@pytest.fixture
def hbka_pdf(make_pdf):
    return make_pdf([
        "HBKA is Hash-Based Key Agreement. It uses hash functions and Merkle "
        "trees to establish a shared secret key."
    ])


@pytest.fixture
def plant_pdf(make_pdf):
    return make_pdf([
        "Photosynthesis converts sunlight into chemical energy inside plant chloroplasts."
    ])