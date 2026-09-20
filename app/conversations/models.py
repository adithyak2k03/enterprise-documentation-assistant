from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class ConversationRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class MessageRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    conversation_id: str
    role: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
