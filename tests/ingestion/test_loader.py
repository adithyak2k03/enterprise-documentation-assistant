import pytest

from app.ingestion.loader import load_pdf


def test_load_pdf_rejects_missing_file():
    with pytest.raises(FileNotFoundError):
        load_pdf("does-not-exist.pdf")


def test_load_pdf_rejects_unsupported_file():
    with pytest.raises(ValueError):
        load_pdf("""tests\\files\\document.txt""")
