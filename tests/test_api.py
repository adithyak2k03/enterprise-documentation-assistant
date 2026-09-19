from fastapi.testclient import TestClient

from app.api import app

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
