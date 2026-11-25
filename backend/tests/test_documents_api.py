def test_upload_becomes_ready_and_is_indexed(client, upload, hbka_pdf, store):
    r = upload("hbka.pdf", hbka_pdf)

    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ready"
    assert body["duplicate"] is False
    assert len(store.items) > 0


def test_same_file_is_deduplicated(client, upload, hbka_pdf, store):
    first = upload("hbka.pdf", hbka_pdf).json()
    count = len(store.items)

    second = upload("copy-of-hbka.pdf", hbka_pdf).json()

    assert second["id"] == first["id"]
    assert second["duplicate"] is True
    assert len(store.items) == count  # nothing indexed twice


def test_non_pdf_extension_is_rejected(client):
    r = client.post("/documents", files={"file": ("notes.txt", b"hello", "text/plain")})
    assert r.status_code == 400


def test_fake_pdf_content_is_rejected(upload):
    assert upload("fake.pdf", b"this is not a pdf").status_code == 400


def test_pdf_without_text_is_marked_failed(client, upload, make_pdf):
    r = upload("scan.pdf", make_pdf([""]))
    assert r.json()["status"] == "failed"

    docs = client.get("/documents").json()
    assert "No extractable text" in docs[0]["error"]


def test_list_documents_shows_pages(client, upload, hbka_pdf):
    upload("hbka.pdf", hbka_pdf)

    docs = client.get("/documents").json()

    assert len(docs) == 1
    assert docs[0]["filename"] == "hbka.pdf"
    assert docs[0]["pages"] == 1


def test_delete_removes_pdf_file_and_vectors(client, upload, hbka_pdf, store, tmp_path):
    doc_id = upload("hbka.pdf", hbka_pdf).json()["id"]
    pdf_file = tmp_path / "data" / "uploads" / f"{doc_id}.pdf"
    assert pdf_file.exists()

    r = client.delete(f"/documents/{doc_id}")

    assert r.json() == {"deleted": True}
    assert not pdf_file.exists()
    assert store.items == []
    assert client.get("/documents").json() == []


def test_delete_unknown_document_is_404(client):
    assert client.delete("/documents/does-not-exist").status_code == 404