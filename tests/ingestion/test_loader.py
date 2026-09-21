from unittest.mock import patch

import pytest
from langchain_core.documents import Document

from app.ingestion.loader import load_pdf


def test_load_pdf_rejects_missing_file():
    with pytest.raises(FileNotFoundError):
        load_pdf("does-not-exist.pdf")


def test_load_pdf_rejects_unsupported_file():
    with pytest.raises(ValueError):
        load_pdf("""tests\\files\\document.txt""")


def test_load_pdf_uses_explicit_document_id(tmp_path, monkeypatch):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n")

    class FakePyPDFLoader:
        def __init__(self, path):
            self.path = path

        def load(self):
            return [Document(page_content="hello world", metadata={"page": 0})]

    monkeypatch.setattr("app.ingestion.loader.PyPDFLoader", FakePyPDFLoader)

    documents = load_pdf(str(pdf_path), document_id="doc-123")

    assert documents[0].metadata["document_id"] == "doc-123"
    assert documents[0].metadata["file_name"] == "sample.pdf"
