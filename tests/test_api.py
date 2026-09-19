from fastapi.testclient import TestClient

import app.api as api
from app.api import app
from app.documents.service import DocumentService

client = TestClient(app)


def test_healthcheck():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_query_returns_answer_and_sources():
    response = client.post("/query", json={"question": "What does this document say about agents?"})

    assert response.status_code == 200
    payload = response.json()
    assert "answer" in payload
    assert isinstance(payload["sources"], list)
    assert isinstance(payload["context"], str)


def test_query_rejects_empty_question():
    response = client.post("/query", json={"question": "   "})

    assert response.status_code == 400
    assert response.json()["detail"] == "Question cannot be empty."


def test_upload_document_saves_file_and_returns_metadata(monkeypatch, tmp_path):
    service = DocumentService(storage_dir=tmp_path / "uploads", database_path=tmp_path / "documents.db")
    monkeypatch.setattr(api, "document_service", service)

    response = client.post(
        "/documents",
        files={"file": ("sample.pdf", b"hello pdf", "application/pdf")},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["file_name"] == "sample.pdf"
    assert payload["mime_type"] == "application/pdf"
    assert payload["stored_name"].endswith("_sample.pdf")
    assert payload["id"]


def test_list_documents_returns_uploaded_files(monkeypatch, tmp_path):
    service = DocumentService(storage_dir=tmp_path / "uploads", database_path=tmp_path / "documents.db")
    monkeypatch.setattr(api, "document_service", service)

    client.post(
        "/documents",
        files={"file": ("doc-one.pdf", b"one", "application/pdf")},
    )
    client.post(
        "/documents",
        files={"file": ("doc-two.pdf", b"two", "application/pdf")},
    )

    response = client.get("/documents")

    assert response.status_code == 200
    payload = response.json()
    assert [item["file_name"] for item in payload] == ["doc-two.pdf", "doc-one.pdf"]


def test_delete_document_removes_record_and_file(monkeypatch, tmp_path):
    service = DocumentService(storage_dir=tmp_path / "uploads", database_path=tmp_path / "documents.db")
    monkeypatch.setattr(api, "document_service", service)

    upload = client.post(
        "/documents",
        files={"file": ("delete-me.pdf", b"delete me", "application/pdf")},
    )
    document_id = upload.json()["id"]

    response = client.delete(f"/documents/{document_id}")

    assert response.status_code == 200
    assert response.json() == {"id": document_id, "deleted": True}
    assert client.get("/documents").json() == []
