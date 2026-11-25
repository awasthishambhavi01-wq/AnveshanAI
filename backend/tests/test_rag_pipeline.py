from app.services.prompt_builder import NOT_FOUND_MESSAGE


def test_answerable_question_returns_answer_and_sources(
    client, upload, hbka_pdf, fake_llm
):
    upload("hbka.pdf", hbka_pdf)

    body = client.post("/chat", json={"question": "What is HBKA?"}).json()

    assert body["answer"] == fake_llm.answer
    assert body["sources"][0]["filename"] == "hbka.pdf"
    assert body["sources"][0]["page"] == 1
    assert body["sources"][0]["id"] == 1
    assert fake_llm.answer_calls == 1


def test_not_found_path_skips_the_llm(client, upload, hbka_pdf, fake_llm):
    upload("hbka.pdf", hbka_pdf)

    body = client.post("/chat", json={"question": "best pizza recipe"}).json()

    assert body["answer"] == NOT_FOUND_MESSAGE
    assert body["sources"] == []
    assert fake_llm.calls == []  # the threshold guard stopped it before the LLM


def test_no_documents_at_all_is_not_found(client, fake_llm):
    body = client.post("/chat", json={"question": "What is HBKA?"}).json()

    assert body["answer"] == NOT_FOUND_MESSAGE
    assert fake_llm.calls == []


def test_model_refusal_returns_no_sources(client, upload, hbka_pdf, fake_llm):
    upload("hbka.pdf", hbka_pdf)
    fake_llm.answer = NOT_FOUND_MESSAGE

    body = client.post("/chat", json={"question": "What is HBKA?"}).json()

    assert body["answer"] == NOT_FOUND_MESSAGE
    assert body["sources"] == []


def test_doc_ids_filter_limits_what_can_be_answered(
    client, upload, hbka_pdf, plant_pdf, fake_llm
):
    upload("hbka.pdf", hbka_pdf)
    plant_id = upload("plant.pdf", plant_pdf).json()["id"]

    body = client.post(
        "/chat", json={"question": "What is HBKA?", "doc_ids": [plant_id]}
    ).json()

    assert body["answer"] == NOT_FOUND_MESSAGE
    assert fake_llm.calls == []


def test_ollama_down_returns_503(client, upload, hbka_pdf, fake_llm):
    upload("hbka.pdf", hbka_pdf)
    fake_llm.fail = True

    r = client.post("/chat", json={"question": "What is HBKA?"})

    assert r.status_code == 503
    assert "Ollama" in r.json()["detail"]


def test_empty_question_is_422(client):
    assert client.post("/chat", json={"question": ""}).status_code == 422