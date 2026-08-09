import pytest

from app.ingestion.loader import load_pdf


def test_load_pdf_rejects_missing_file():
    with pytest.raises(FileNotFoundError):
        load_pdf("does-not-exist.pdf")


def test_load_pdf_rejects_unsupported_file():
    with pytest.raises(ValueError):
        load_pdf("D:\\2026 Projects\\enterprise-documentation-assistant\\tests\\ingestion\\document.txt")