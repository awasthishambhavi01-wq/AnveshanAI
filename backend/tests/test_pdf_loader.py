from app.services.pdf_loader import extract_pages


def test_pages_are_numbered_from_one(tmp_path, make_pdf):
    path = tmp_path / "a.pdf"
    path.write_bytes(make_pdf(["First page text", "Second page text"]))

    pages = extract_pages(path)

    assert [p["page"] for p in pages] == [1, 2]
    assert "First page" in pages[0]["text"]
    assert "Second page" in pages[1]["text"]