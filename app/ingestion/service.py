from pathlib import Path

from langchain_core.documents import Document

from app.documents.models import DocumentRecord
from app.ingestion.loader import load_pdf
from app.ingestion.models import IngestionResult
from app.ingestion.splitter import split_documents
from app.vector_store.service import add_documents


def _load_document_for_ingestion(file_path: str, file_name: str, document_id: str) -> list[Document]:
    path = Path(file_path)
    if path.suffix.lower() == ".pdf":
        documents = load_pdf(file_path, document_id=document_id)
    else:
        text = path.read_text(encoding="utf-8")
        documents = [
            Document(
                page_content=text,
                metadata={
                    "document_id": document_id,
                    "file_name": file_name,
                    "source": str(path),
                    "page_number": 1,
                },
            )
        ]

    return documents


def document_exists(document_id: str) -> bool:
    from app.vector_store.chroma import create_vector_store

    vector_store = create_vector_store()
    try:
        result = vector_store.get(where={"document_id": document_id})
    except TypeError:
        result = vector_store.get(filter={"document_id": document_id})
    except Exception:
        return False

    ids = result.get("ids") if isinstance(result, dict) else None
    return bool(ids)


def refresh_document(document_id: str, chunks: list[Document]) -> list[str]:
    """Replace any existing vector entries for a document with the latest chunk set."""
    from app.vector_store.chroma import create_vector_store

    vector_store = create_vector_store()

    if hasattr(vector_store, "delete"):
        try:
            vector_store.delete(where={"document_id": document_id})
        except TypeError:
            vector_store.delete(filter={"document_id": document_id})

    return vector_store.add_documents(chunks)


def ingest_document(document: DocumentRecord) -> IngestionResult:
    try:
        documents = _load_document_for_ingestion(
            file_path=document.file_path,
            file_name=document.file_name,
            document_id=document.id,
        )
        chunks = split_documents(documents)

        if document_exists(document.id):
            refresh_document(document.id, chunks)
        else:
            add_documents(chunks)

        return IngestionResult(
            document_id=document.id,
            file_name=document.file_name,
            file_path=document.file_path,
            status="completed",
            total_chunks=len(chunks),
            error=None,
        )
    except Exception as exc:  # pragma: no cover - defensive path
        return IngestionResult(
            document_id=document.id,
            file_name=document.file_name,
            file_path=document.file_path,
            status="failed",
            total_chunks=0,
            error=str(exc),
        )


def ingest_pdf(file_path: str, document_id: str | None = None) -> list[Document]:
    documents = load_pdf(file_path, document_id=document_id)
    chunks = split_documents(documents)

    add_documents(chunks)

    return chunks
