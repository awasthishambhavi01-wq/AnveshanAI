from app.services.retriever import retrieve

HBKA_QUERY = "What does HBKA use to establish a shared secret key?"


def test_search_ranks_relevant_document_first(client, upload, hbka_pdf, plant_pdf):
    upload("hbka.pdf", hbka_pdf)
    upload("plant.pdf", plant_pdf)

    results = client.post("/search", json={"query": HBKA_QUERY, "top_k": 5}).json()

    assert results[0]["filename"] == "hbka.pdf"
    assert results[0]["score"] > results[-1]["score"]


def test_search_filters_by_doc_ids(client, upload, hbka_pdf, plant_pdf):
    upload("hbka.pdf", hbka_pdf)
    plant_id = upload("plant.pdf", plant_pdf).json()["id"]

    results = client.post(
        "/search", json={"query": HBKA_QUERY, "top_k": 5, "doc_ids": [plant_id]}
    ).json()

    assert results
    assert all(r["doc_id"] == plant_id for r in results)


def test_threshold_drops_unrelated_matches(client, upload, hbka_pdf):
    upload("hbka.pdf", hbka_pdf)

    assert retrieve("best pizza recipe", 5, None, min_score=0.15) == []


def test_empty_query_is_422_and_blank_query_is_400(client):
    assert client.post("/search", json={"query": ""}).status_code == 422
    assert client.post("/search", json={"query": "   "}).status_code == 400