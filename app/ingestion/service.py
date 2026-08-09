from langchain_core.documents import Document

from app.ingestion.loader import load_pdf
from app.ingestion.splitter import split_documents
from app.vector_store.service import add_documents


def ingest_pdf(file_path: str) -> list[Document]:
    documents = load_pdf(file_path)
    chunks = split_documents(documents)

    add_documents(chunks)

    return chunks
