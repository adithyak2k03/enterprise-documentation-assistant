from __future__ import annotations

from datetime import datetime

from fastapi import FastAPI, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from app.conversations.service import ConversationService
from app.documents.service import DocumentService
from app.ingestion.service import ingest_document
from app.langgraph.service import run_question


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1)
    conversation_id: str | None = None


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


class ConversationCreateRequest(BaseModel):
    title: str | None = None


class ConversationResponse(BaseModel):
    id: str
    title: str | None = None
    created_at: datetime
    updated_at: datetime


class MessageCreateRequest(BaseModel):
    role: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime


document_service = DocumentService(storage_dir="data/uploads", database_path="data/documents.db")
conversation_service = ConversationService(database_path="data/conversations.db")

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

    conversation_context = None
    if payload.conversation_id:
        conversation = conversation_service.get_conversation(payload.conversation_id)
        if conversation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found.",
            )
        conversation_context = conversation_service.get_recent_context(payload.conversation_id, max_turns=6)

    result = run_question(payload.question, conversation_context=conversation_context)

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

    ingest_document(document)

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


@app.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(payload: ConversationCreateRequest) -> ConversationResponse:
    conversation = conversation_service.create_conversation(title=payload.title)
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )


@app.get("/conversations", response_model=list[ConversationResponse])
def list_conversations() -> list[ConversationResponse]:
    conversations = conversation_service.list_conversations()
    return [
        ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
        )
        for conversation in conversations
    ]


@app.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: str) -> ConversationResponse:
    conversation = conversation_service.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )


@app.post("/conversations/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def add_message(conversation_id: str, payload: MessageCreateRequest) -> MessageResponse:
    if conversation_service.get_conversation(conversation_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    role = payload.role.strip().lower()
    if role not in {"user", "assistant"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be 'user' or 'assistant'.",
        )

    if not payload.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be empty.",
        )

    message = conversation_service.add_message(conversation_id, role, payload.content)
    return MessageResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        role=message.role,
        content=message.content,
        created_at=message.created_at,
    )


@app.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
def list_messages(conversation_id: str) -> list[MessageResponse]:
    if conversation_service.get_conversation(conversation_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    messages = conversation_service.list_messages(conversation_id)
    return [
        MessageResponse(
            id=message.id,
            conversation_id=message.conversation_id,
            role=message.role,
            content=message.content,
            created_at=message.created_at,
        )
        for message in messages
    ]
