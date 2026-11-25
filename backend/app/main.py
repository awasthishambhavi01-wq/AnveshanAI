
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import chat, documents, health, search
from app.core.exceptions import LLMError


from app.api.routes import documents, health
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db import models  # noqa: F401 (registers tables on Base)
from app.db.database import Base, engine
from app.api.routes import documents, health, search
from app.services.embedder import get_embedder
from app.services.vector_store import get_vector_store


settings = get_settings()
setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    settings.chroma_dir.mkdir(parents=True, exist_ok=True)

    Base.metadata.create_all(bind=engine)
    get_embedder()       # load the model once at startup
    get_vector_store()   # open Chroma once

    logger.info(
        "%s started. Data dir: %s",
        settings.app_name,
        settings.data_dir,
    )

    yield

    logger.info("%s shutting down", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(chat.router)


@app.exception_handler(LLMError)
async def llm_error_handler(request: Request, exc: LLMError):
    return JSONResponse(status_code=503, content={"detail": str(exc)})

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health.router)
app.include_router(documents.router)
app.include_router(search.router)