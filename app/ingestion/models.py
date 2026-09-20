from __future__ import annotations

from pydantic import BaseModel, Field


class IngestionResult(BaseModel):
    document_id: str
    file_name: str
    file_path: str
    status: str = Field(default="queued")
    total_chunks: int = 0
    error: str | None = None
