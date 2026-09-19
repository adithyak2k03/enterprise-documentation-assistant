from __future__ import annotations

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

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
