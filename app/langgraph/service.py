from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from app.rag.service import answer_question
from app.retrieval.service import retrieve


class LangGraphState(TypedDict):
    question: str
    documents: list[dict[str, Any]]
    answer: str
    sources: list[dict[str, Any]]
    context: str
    retry_count: int


def route_after_retrieval(state: LangGraphState) -> str:
    documents = state.get("documents") or []
    return "generate" if documents else "no_documents"


def route_after_verification(state: LangGraphState) -> str:
    retry_count = state.get("retry_count", 0)
    return "retry" if not state.get("answer") and retry_count < 1 else "final"


def retrieve_step(state: LangGraphState) -> LangGraphState:
    question = state["question"]
    documents = retrieve(question)

    return {
        **state,
        "documents": [doc.model_dump() if hasattr(doc, "model_dump") else doc for doc in documents],
        "retry_count": 0,
    }


def no_documents_step(state: LangGraphState) -> LangGraphState:
    return {
        **state,
        "answer": "I don't have enough information in the"
        " provided documentation to answer this question.",
        "sources": [],
        "context": "",
    }


def generate_step(state: LangGraphState) -> LangGraphState:
    question = state["question"]
    response = answer_question(question)

    return {
        **state,
        "answer": response.answer,
        "sources": [source.model_dump() for source in response.sources],
        "context": response.context,
        "retry_count": 0,
    }


def verify_step(state: LangGraphState) -> LangGraphState:
    answer = state.get("answer") or ""
    if not answer:
        retry_count = state.get("retry_count", 0) + 1
        return {**state, "retry_count": retry_count}

    return {**state, "retry_count": 0}


def retry_step(state: LangGraphState) -> LangGraphState:
    return {**state, "answer": "I don't have enough information "
    "in the provided documentation to answer this question."}


def build_graph():
    graph = StateGraph(LangGraphState)

    graph.add_node("retrieve", retrieve_step)
    graph.add_node("generate", generate_step)
    graph.add_node("verify", verify_step)
    graph.add_node("retry", retry_step)
    graph.add_node("no_documents", no_documents_step)

    graph.add_conditional_edges(
        "retrieve",
        route_after_retrieval,
        {
            "generate": "generate",
            "no_documents": "no_documents",
        },
    )
    graph.add_edge("generate", "verify")
    graph.add_conditional_edges(
        "verify",
        route_after_verification,
        {
            "retry": "retry",
            "final": END,
        },
    )
    graph.add_edge("retry", END)
    graph.add_edge("no_documents", END)
    graph.set_entry_point("retrieve")

    return graph.compile()


def run_question(question: str) -> dict[str, Any]:
    return rag_graph.invoke({"question": question})


rag_graph = build_graph()
