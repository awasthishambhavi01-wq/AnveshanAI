from app.core.config import get_settings
from app.db import crud
from app.services import memory


def _start(client, upload, hbka_pdf) -> str:
    upload("hbka.pdf", hbka_pdf)
    return client.post("/sessions").json()["session_id"]


def test_first_question_is_not_rewritten(client, upload, hbka_pdf, fake_llm):
    sid = _start(client, upload, hbka_pdf)

    body = client.post(
        "/chat", json={"session_id": sid, "question": "What is HBKA?"}
    ).json()

    assert body["rewritten_question"] == "What is HBKA?"
    assert fake_llm.rewrite_calls == 0  # no history, so no extra LLM call
    assert fake_llm.answer_calls == 1


def test_followup_is_rewritten_and_used_for_retrieval(
    client, upload, hbka_pdf, fake_llm
):
    sid = _start(client, upload, hbka_pdf)
    client.post("/chat", json={"session_id": sid, "question": "What is HBKA?"})

    body = client.post(
        "/chat",
        json={"session_id": sid, "question": "What does it use to establish a key?"},
    ).json()

    assert body["rewritten_question"] == fake_llm.rewrite
    assert fake_llm.rewrite_calls == 1
    # The final prompt must contain the rewritten question, not the vague one
    final_prompt = fake_llm.calls[-1][-1]["content"]
    assert fake_llm.rewrite in final_prompt
    assert body["sources"]


def test_messages_are_saved_with_sources(client, upload, hbka_pdf, fake_llm):
    sid = _start(client, upload, hbka_pdf)
    client.post("/chat", json={"session_id": sid, "question": "What is HBKA?"})

    msgs = client.get(f"/sessions/{sid}/messages").json()

    assert [m["role"] for m in msgs] == ["user", "assistant"]
    assert msgs[0]["sources"] is None
    assert msgs[1]["sources"][0]["filename"] == "hbka.pdf"


def test_failed_llm_call_is_not_saved(client, upload, hbka_pdf, fake_llm):
    sid = _start(client, upload, hbka_pdf)
    fake_llm.fail = True

    r = client.post("/chat", json={"session_id": sid, "question": "What is HBKA?"})

    assert r.status_code == 503
    assert client.get(f"/sessions/{sid}/messages").json() == []


def test_unknown_session_is_404(client, fake_llm):
    r = client.post("/chat", json={"session_id": "nope", "question": "hi"})
    assert r.status_code == 404
    assert client.get("/sessions/nope/messages").status_code == 404


def test_chat_still_works_without_a_session(client, upload, hbka_pdf, fake_llm):
    upload("hbka.pdf", hbka_pdf)

    r = client.post("/chat", json={"question": "What is HBKA?"})

    assert r.status_code == 200


def test_sliding_window_returns_last_n_messages_oldest_first(db):
    session = crud.create_session(db)
    for i in range(10):
        crud.add_message(db, session.id, "user" if i % 2 == 0 else "assistant", f"m{i}")

    history = memory.load_history(db, session.id)

    n = get_settings().max_history
    assert [m["content"] for m in history] == [f"m{i}" for i in range(10 - n, 10)]