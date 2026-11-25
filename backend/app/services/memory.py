import logging

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import LLMError
from app.db import crud
from app.services import llm

logger = logging.getLogger(__name__)

REWRITE_SYSTEM = (
    "You rewrite follow-up questions. Given a conversation and a follow-up question, "
    "rewrite the follow-up as one standalone question that makes sense without the "
    "conversation, replacing pronouns and vague references with the specific topic. "
    "If it is already standalone, return it unchanged. "
    "Output ONLY the question, nothing else."
)


def load_history(db: Session, session_id: str) -> list[dict]:
    """Sliding window: the last MAX_HISTORY messages, oldest first."""
    rows = crud.get_recent_messages(db, session_id, get_settings().max_history)
    return [{"role": m.role, "content": m.content} for m in rows]


def rewrite_question(question: str, history: list[dict]) -> str:
    if not history:
        return question  # first question: no extra LLM call

    # Truncate long answers so the rewrite prompt stays small and fast
    convo = "\n".join(f"{m['role'].capitalize()}: {m['content'][:300]}" for m in history)
    messages = [
        {"role": "system", "content": REWRITE_SYSTEM},
        {
            "role": "user",
            "content": f"Conversation:\n{convo}\n\nFollow-up question: {question}\n\nStandalone question:",
        },
    ]
    try:
        out = llm.generate(messages, temperature=0.0, max_tokens=80)
    except LLMError:
        return question  # fall back to the raw question; the answer call will report real errors

    out = out.strip().split("\n")[0].strip().strip('"')
    if not out or len(out) > len(question) * 3 + 200:
        return question  # model rambled; don't trust it
    logger.info("Rewrote %r -> %r", question, out)
    return out


def save_exchange(db: Session, session_id: str, question: str, result: dict) -> None:
    crud.add_message(db, session_id, "user", question)
    crud.add_message(db, session_id, "assistant", result["answer"], result["sources"])