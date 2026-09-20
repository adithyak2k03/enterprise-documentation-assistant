from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.conversations.models import ConversationRecord, MessageRecord


class ConversationService:
    def __init__(self, database_path: str | Path | None = None) -> None:
        self.database_path = Path(database_path or "data/conversations.db")
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
                """
            )

    def create_conversation(self, title: str | None = None) -> ConversationRecord:
        conversation_id = str(uuid4())
        now = datetime.now(UTC).isoformat()
        record = ConversationRecord(
            id=conversation_id,
            title=title,
            created_at=datetime.fromisoformat(now),
            updated_at=datetime.fromisoformat(now),
        )

        with self._connect() as conn:
            conn.execute(
                "INSERT INTO conversations (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (
                    record.id,
                    record.title,
                    now,
                    now,
                ),
            )

        return record

    def add_message(self, conversation_id: str, role: str, content: str) -> MessageRecord:
        message_id = str(uuid4())
        created_at = datetime.now(UTC).isoformat()

        record = MessageRecord(
            id=message_id,
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=datetime.fromisoformat(created_at),
        )

        with self._connect() as conn:
            conn.execute(
                "INSERT INTO messages (id, conversation_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
                (
                    record.id,
                    record.conversation_id,
                    record.role,
                    record.content,
                    created_at,
                ),
            )
            conn.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (created_at, conversation_id),
            )

        return record

    def list_conversations(self) -> list[ConversationRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, title, created_at, updated_at FROM conversations ORDER BY updated_at DESC"
            ).fetchall()

        return [
            ConversationRecord(
                id=row["id"],
                title=row["title"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )
            for row in rows
        ]

    def get_conversation(self, conversation_id: str) -> ConversationRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, title, created_at, updated_at FROM conversations WHERE id = ?",
                (conversation_id,),
            ).fetchone()

        if row is None:
            return None

        return ConversationRecord(
            id=row["id"],
            title=row["title"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def list_messages(self, conversation_id: str) -> list[MessageRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, conversation_id, role, content, created_at FROM messages WHERE conversation_id = ? ORDER BY created_at ASC",
                (conversation_id,),
            ).fetchall()

        return [
            MessageRecord(
                id=row["id"],
                conversation_id=row["conversation_id"],
                role=row["role"],
                content=row["content"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            for row in rows
        ]

    def get_recent_messages(self, conversation_id: str, max_turns: int = 6) -> list[MessageRecord]:
        messages = self.list_messages(conversation_id)
        if max_turns <= 0:
            return []
        return messages[-max_turns:]

    def get_recent_context(self, conversation_id: str, max_turns: int = 6) -> str:
        messages = self.get_recent_messages(conversation_id, max_turns=max_turns)
        if not messages:
            return ""

        context_lines = []
        for message in messages:
            role = message.role.capitalize()
            context_lines.append(f"{role}: {message.content}")

        return "\n".join(context_lines)
