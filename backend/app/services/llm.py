import logging

import httpx

from app.core.config import get_settings
from app.core.exceptions import LLMError

logger = logging.getLogger(__name__)


def generate(messages: list[dict], temperature: float = 0.1, max_tokens: int = 300) -> str:
    """Call Ollama /api/chat (non-streaming) and return the reply text."""
    s = get_settings()
    payload = {
        "model": s.llm_model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens},
    }
    

    try:
        # Long read timeout: the first call after startup loads the model into memory
        with httpx.Client(timeout=httpx.Timeout(180.0, connect=5.0)) as client:
            resp = client.post(f"{s.ollama_url}/api/chat", json=payload)
            resp.raise_for_status()
            return resp.json()["message"]["content"].strip()
    except httpx.ConnectError:
        raise LLMError("Cannot reach Ollama. Is it running? (ollama serve)")
    except httpx.TimeoutException:
        raise LLMError("Ollama took too long to respond")
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise LLMError(f"Model '{s.llm_model}' not found. Run: ollama pull {s.llm_model}")
        raise LLMError(f"Ollama error: {exc.response.status_code}")
    except (KeyError, ValueError):
        raise LLMError("Unexpected response format from Ollama")