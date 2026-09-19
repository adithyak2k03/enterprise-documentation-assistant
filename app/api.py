from __future__ import annotations

from datetime import datetime

from fastapi import FastAPI, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from app.documents.service import DocumentService
from app.langgraph.service import run_question


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1)


class SourceResponse(BaseModel):
    file_name: str
    page_number: int


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceResponse] = Field(default_factory=list)
    context: str = ""


class DocumentUploadResponse(BaseModel):
    id: str
    file_name: str
    stored_name: str
    mime_type: str
    file_path: str
    uploaded_at: datetime


class DocumentDeleteResponse(BaseModel):
    id: str
    deleted: bool


document_service = DocumentService(storage_dir="data/uploads", database_path="data/documents.db")

app = FastAPI(title="Enterprise Documentation Assistant")


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query_documents(payload: QueryRequest) -> QueryResponse:
    if not payload.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty.",
        )

    result = run_question(payload.question)

    sources = [
        SourceResponse(
            file_name=source["file_name"],
            page_number=source["page_number"],
        )
        for source in result.get("sources", [])
    ]

    return QueryResponse(
        answer=result.get("answer", ""),
        sources=sources,
        context=result.get("context", ""),
    )


@app.post("/documents", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
def upload_document(file: UploadFile = File(...)) -> DocumentUploadResponse:
    if file.filename is None or not file.filename.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A file name is required.",
        )

    content = file.file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    document = document_service.add_document(
        file_name=file.filename,
        file_bytes=content,
        content_type=file.content_type or "application/octet-stream",
    )

    return DocumentUploadResponse(
        id=document.id,
        file_name=document.file_name,
        stored_name=document.stored_name,
        mime_type=document.mime_type,
        file_path=document.file_path,
        uploaded_at=document.uploaded_at,
    )


@app.get("/documents", response_model=list[DocumentUploadResponse])
def list_documents() -> list[DocumentUploadResponse]:
    documents = document_service.list_documents()
    return [
        DocumentUploadResponse(
            id=document.id,
            file_name=document.file_name,
            stored_name=document.stored_name,
            mime_type=document.mime_type,
            file_path=document.file_path,
            uploaded_at=document.uploaded_at,
        )
        for document in documents
    ]


@app.delete("/documents/{document_id}", response_model=DocumentDeleteResponse)
def delete_document(document_id: str) -> DocumentDeleteResponse:
    deleted = document_service.delete_document(document_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    return DocumentDeleteResponse(id=document_id, deleted=True)
