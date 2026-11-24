from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]  # .../backend


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )

    app_name: str = "AnveshanAI"

    # LLM + embeddings
    ollama_url: str = "http://localhost:11434"
    llm_model: str = "qwen2.5:3b"
    embed_model: str = "BAAI/bge-small-en-v1.5"

    # RAG tuning
    chunk_size: int = 800
    chunk_overlap: int = 100
    top_k: int = 5
    score_threshold: float = 0.35
    max_history: int = 6

    # CORS
    frontend_origin: str = "http://localhost:5173"

    # Paths (computed, not read from .env)
    @property
    def data_dir(self) -> Path:
        return BASE_DIR / "data"

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def chroma_dir(self) -> Path:
        return self.data_dir / "chroma"

    @property
    def database_url(self) -> str:
        return f"sqlite:///{(self.data_dir / 'app.db').as_posix()}"


@lru_cache
def get_settings() -> Settings:
    return Settings()