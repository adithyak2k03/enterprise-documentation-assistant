from fastapi.testclient import TestClient

import app.api as api
from app.api import app
from app.conversations.service import ConversationService
from app.documents.service import DocumentService

client = TestClient(app)


def test_healthcheck():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_query_returns_answer_and_sources():
    response = client.post("/query", json={"question": "What does this document say about agents?"})

    assert response.status_code == 200
    payload = response.json()
    assert "answer" in payload
    assert isinstance(payload["sources"], list)
    assert isinstance(payload["context"], str)


def test_query_rejects_empty_question():
    response = client.post("/query", json={"question": "   "})

    assert response.status_code == 400
    assert response.json()["detail"] == "Question cannot be empty."


def test_upload_document_saves_file_and_returns_metadata(monkeypatch, tmp_path):
    service = DocumentService(storage_dir=tmp_path / "uploads", database_path=tmp_path / "documents.db")
    monkeypatch.setattr(api, "document_service", service)

    response = client.post(
        "/documents",
        files={"file": ("sample.pdf", b"hello pdf", "application/pdf")},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["file_name"] == "sample.pdf"
    assert payload["mime_type"] == "application/pdf"
    assert payload["stored_name"].endswith("_sample.pdf")
    assert payload["id"]


def test_list_documents_returns_uploaded_files(monkeypatch, tmp_path):
    service = DocumentService(storage_dir=tmp_path / "uploads", database_path=tmp_path / "documents.db")
    monkeypatch.setattr(api, "document_service", service)

    client.post(
        "/documents",
        files={"file": ("doc-one.pdf", b"one", "application/pdf")},
    )
    client.post(
        "/documents",
        files={"file": ("doc-two.pdf", b"two", "application/pdf")},
    )

    response = client.get("/documents")

    assert response.status_code == 200
    payload = response.json()
    assert [item["file_name"] for item in payload] == ["doc-two.pdf", "doc-one.pdf"]


def test_delete_document_removes_record_and_file(monkeypatch, tmp_path):
    service = DocumentService(storage_dir=tmp_path / "uploads", database_path=tmp_path / "documents.db")
    monkeypatch.setattr(api, "document_service", service)

    upload = client.post(
        "/documents",
        files={"file": ("delete-me.pdf", b"delete me", "application/pdf")},
    )
    document_id = upload.json()["id"]

    response = client.delete(f"/documents/{document_id}")

    assert response.status_code == 200
    assert response.json() == {"id": document_id, "deleted": True}
    assert client.get("/documents").json() == []


def test_create_and_list_conversations(monkeypatch, tmp_path):
    service = ConversationService(database_path=tmp_path / "conversations.db")
    monkeypatch.setattr(api, "conversation_service", service)

    create_response = client.post("/conversations", json={"title": "Demo chat"})
    assert create_response.status_code == 201
    payload = create_response.json()
    assert payload["title"] == "Demo chat"

    list_response = client.get("/conversations")
    assert list_response.status_code == 200
    assert list_response.json()[0]["title"] == "Demo chat"


def test_get_missing_conversation_returns_404(monkeypatch, tmp_path):
    service = ConversationService(database_path=tmp_path / "conversations.db")
    monkeypatch.setattr(api, "conversation_service", service)

    response = client.get("/conversations/not-found")

    assert response.status_code == 404
    assert response.json()["detail"] == "Conversation not found."


def test_add_message_to_conversation_and_fetch_thread(monkeypatch, tmp_path):
    service = ConversationService(database_path=tmp_path / "conversations.db")
    monkeypatch.setattr(api, "conversation_service", service)

    conversation = service.create_conversation(title="Thread test")

    user_response = client.post(
        f"/conversations/{conversation.id}/messages",
        json={"role": "user", "content": "hello there"},
    )
    assistant_response = client.post(
        f"/conversations/{conversation.id}/messages",
        json={"role": "assistant", "content": "general kenobi"},
    )

    assert user_response.status_code == 201
    assert assistant_response.status_code == 201

    thread_response = client.get(f"/conversations/{conversation.id}/messages")
    assert thread_response.status_code == 200
    payload = thread_response.json()
    assert [item["role"] for item in payload] == ["user", "assistant"]
    assert [item["content"] for item in payload] == ["hello there", "general kenobi"]


def test_add_message_rejects_invalid_role_and_blank_content(monkeypatch, tmp_path):
    service = ConversationService(database_path=tmp_path / "conversations.db")
    monkeypatch.setattr(api, "conversation_service", service)

    conversation = service.create_conversation(title="Validation")

    bad_role = client.post(
        f"/conversations/{conversation.id}/messages",
        json={"role": "system", "content": "not allowed"},
    )
    blank_content = client.post(
        f"/conversations/{conversation.id}/messages",
        json={"role": "user", "content": "   "},
    )

    assert bad_role.status_code == 400
    assert bad_role.json()["detail"] == "Role must be 'user' or 'assistant'."
    assert blank_content.status_code == 400
    assert blank_content.json()["detail"] == "Message content cannot be empty."


def test_query_uses_recent_conversation_context(monkeypatch, tmp_path):
    service = ConversationService(database_path=tmp_path / "conversations.db")
    monkeypatch.setattr(api, "conversation_service", service)

    conversation = service.create_conversation(title="Memory test")
    service.add_message(conversation.id, "user", "What does this doc cover?")
    service.add_message(conversation.id, "assistant", "It covers agents.")

    captured = {}

    def fake_run_question(question, conversation_context=None):
        captured["question"] = question
        captured["conversation_context"] = conversation_context
        return {"answer": "ok", "sources": [], "context": ""}

    monkeypatch.setattr(api, "run_question", fake_run_question)

    response = client.post(
        "/query",
        json={"question": "What about the risks?", "conversation_id": conversation.id},
    )

    assert response.status_code == 200
    assert captured["question"] == "What about the risks?"
    assert "User: What does this doc cover?" in captured["conversation_context"]
    assert "Assistant: It covers agents." in captured["conversation_context"]
