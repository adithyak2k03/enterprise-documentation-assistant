from app.documents.models import DocumentRecord
from app.ingestion.models import IngestionResult
from app.ingestion.service import ingest_document


def test_ingest_document_sets_contract_after_upload(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("Alpha beta gamma delta. " * 20, encoding="utf-8")

    document = DocumentRecord(
        id="doc-123",
        file_name="sample.txt",
        stored_name="doc-123_sample.txt",
        mime_type="text/plain",
        file_path=str(file_path),
    )

    result = ingest_document(document)

    assert isinstance(result, IngestionResult)
    assert result.document_id == "doc-123"
    assert result.file_name == "sample.txt"
    assert result.file_path == str(file_path)
    assert result.status == "completed"
    assert result.total_chunks > 0
    assert result.error is None


def test_ingest_document_loads_and_chunks_uploaded_file(monkeypatch, tmp_path):
    file_path = tmp_path / "notes.txt"
    file_path.write_text("Alpha beta gamma delta. " * 20, encoding="utf-8")

    document = DocumentRecord(
        id="doc-456",
        file_name="notes.txt",
        stored_name="doc-456_notes.txt",
        mime_type="text/plain",
        file_path=str(file_path),
    )

    captured = {}

    def fake_add_documents(chunks):
        captured["chunks"] = chunks
        return [f"id-{index}" for index in range(len(chunks))]

    monkeypatch.setattr("app.ingestion.service.document_exists", lambda _document_id: False)
    monkeypatch.setattr("app.ingestion.service.add_documents", fake_add_documents)

    result = ingest_document(document)

    assert result.status == "completed"
    assert result.total_chunks > 0
    assert result.error is None
    assert len(captured["chunks"]) == result.total_chunks
    assert captured["chunks"][0].metadata["file_name"] == "notes.txt"


def test_ingest_document_refreshes_existing_chunks_for_same_document(monkeypatch, tmp_path):
    file_path = tmp_path / "refresh.txt"
    file_path.write_text("updated content. " * 30, encoding="utf-8")

    document = DocumentRecord(
        id="doc-refresh",
        file_name="refresh.txt",
        stored_name="doc-refresh_refresh.txt",
        mime_type="text/plain",
        file_path=str(file_path),
    )

    calls = []

    def fake_refresh_document(document_id, chunks):
        calls.append((document_id, len(chunks)))
        return [f"new-id-{index}" for index in range(len(chunks))]

    monkeypatch.setattr("app.ingestion.service.document_exists", lambda _document_id: True)
    monkeypatch.setattr("app.ingestion.service.refresh_document", fake_refresh_document)

    result = ingest_document(document)

    assert result.status == "completed"
    assert calls == [("doc-refresh", result.total_chunks)]
