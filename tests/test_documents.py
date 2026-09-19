from pathlib import Path

from app.documents.service import DocumentService


def test_document_service_persists_and_lists_documents(tmp_path):
    storage_dir = tmp_path / "uploads"
    db_path = tmp_path / "documents.db"
    service = DocumentService(storage_dir=storage_dir, database_path=db_path)

    document = service.add_document(
        file_name="sample.pdf",
        file_bytes=b"hello pdf",
        content_type="application/pdf",
    )

    assert document.file_name == "sample.pdf"
    assert document.mime_type == "application/pdf"
    assert service.list_documents()[0].file_name == "sample.pdf"
    assert Path(document.file_path).exists()


def test_document_service_deletes_record_and_file(tmp_path):
    storage_dir = tmp_path / "uploads"
    db_path = tmp_path / "documents.db"
    service = DocumentService(storage_dir=storage_dir, database_path=db_path)

    document = service.add_document(
        file_name="delete-me.pdf",
        file_bytes=b"delete me",
        content_type="application/pdf",
    )

    deleted = service.delete_document(document.id)

    assert deleted is True
    assert service.list_documents() == []
    assert not Path(document.file_path).exists()
