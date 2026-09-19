from app.langgraph.service import (
    rag_graph,
    route_after_retrieval,
    route_after_verification,
    run_question,
)


def test_route_after_retrieval_no_documents():
    assert route_after_retrieval({"documents": []}) == "no_documents"


def test_route_after_retrieval_has_documents():
    assert route_after_retrieval({"documents": [{"id": "doc-1"}]}) == "generate"


def test_route_after_verification_retries_when_needed():
    assert route_after_verification({"answer": "", "retry_count": 0}) == "retry"


def test_route_after_verification_finalizes_after_limit():
    assert route_after_verification({"answer": "", "retry_count": 1}) == "final"


def test_graph_runs_with_question():
    result = rag_graph.invoke({"question": "What does this document say about agents?"})

    assert "question" in result
    assert "answer" in result
    assert "sources" in result
    assert result["question"] == "What does this document say about agents?"


def test_run_question_uses_real_services():
    result = run_question("What does this document say about agents?")

    assert result["answer"]
    assert isinstance(result["sources"], list)
