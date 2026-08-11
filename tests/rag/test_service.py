from langchain_core.documents import Document

from app.rag.service import build_context


def test_build_context_includes_source_metadata():
    documents = [
        Document(
            page_content="The system uses FastAPI.",
            metadata={
                "file_name": "architecture.pdf",
                "page_number": 5,
            },
        )
    ]

    context = build_context(documents)

    assert "architecture.pdf" in context
    assert "Page: 5" in context
    assert "The system uses FastAPI." in context
