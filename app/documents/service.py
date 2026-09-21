from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.documents.models import DocumentRecord


class DocumentService:
    def __init__(self, storage_dir: str | Path | None = None, database_path: str | Path | None = None) -> None:
        self.storage_dir = Path(storage_dir or "data/uploads")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.database_path = Path(database_path or "data/documents.db")
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
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    file_name TEXT NOT NULL,
                    stored_name TEXT NOT NULL,
                    mime_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    uploaded_at TEXT NOT NULL
                )
                """
            )

    def add_document(
        self,
        file_name: str,
        file_bytes: bytes,
        content_type: str,
    ) -> DocumentRecord:
        document_id = str(uuid4())
        stored_name = f"{document_id}_{file_name}"
        file_path = self.storage_dir / stored_name
        file_path.write_bytes(file_bytes)

        uploaded_at = datetime.now(UTC).isoformat()

        record = DocumentRecord(
            id=document_id,
            file_name=file_name,
            stored_name=stored_name,
            mime_type=content_type,
            file_path=str(file_path),
            uploaded_at=datetime.fromisoformat(uploaded_at),
        )

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO documents (id, file_name, stored_name, mime_type, file_path, uploaded_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    record.id,
                    record.file_name,
                    record.stored_name,
                    record.mime_type,
                    record.file_path,
                    uploaded_at,
                ),
            )

        return record

    def list_documents(self) -> list[DocumentRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, file_name, stored_name, mime_type, file_path, uploaded_at FROM documents ORDER BY uploaded_at DESC"
            ).fetchall()

        return [
            DocumentRecord(
                id=row["id"],
                file_name=row["file_name"],
                stored_name=row["stored_name"],
                mime_type=row["mime_type"],
                file_path=row["file_path"],
                uploaded_at=datetime.fromisoformat(row["uploaded_at"]),
            )
            for row in rows
        ]

    def get_document(self, document_id: str) -> DocumentRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, file_name, stored_name, mime_type, file_path, uploaded_at FROM documents WHERE id = ?",
                (document_id,),
            ).fetchone()

        if row is None:
            return None

        return DocumentRecord(
            id=row["id"],
            file_name=row["file_name"],
            stored_name=row["stored_name"],
            mime_type=row["mime_type"],
            file_path=row["file_path"],
            uploaded_at=datetime.fromisoformat(row["uploaded_at"]),
        )

    def delete_document(self, document_id: str) -> bool:
        record = self.get_document(document_id)
        if record is None:
            return False

        file_path = Path(record.file_path)
        if file_path.exists():
            file_path.unlink()

        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))

        try:
            from app.vector_store.chroma import create_vector_store

            vector_store = create_vector_store()
            if hasattr(vector_store, "delete"):
                try:
                    vector_store.delete(where={"document_id": document_id})
                except TypeError:
                    vector_store.delete(filter={"document_id": document_id})
        except Exception:
            pass

        return cursor.rowcount > 0
