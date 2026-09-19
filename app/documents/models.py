from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class DocumentRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    file_name: str
    stored_name: str
    mime_type: str
    file_path: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
