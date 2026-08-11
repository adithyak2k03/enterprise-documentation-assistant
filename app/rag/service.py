from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage

from app.llm.service import create_llm
from app.rag.models import RAGResponse, Source
from app.rag.prompts import SYSTEM_PROMPT
from app.retrieval.service import retrieve


def build_context(documents: list[Document]) -> str:
    context_parts = []

    for index, document in enumerate(documents, start=1):
        context_parts.append(
            f"""[Source {index}]
File: {document.metadata.get("file_name")}
Page: {document.metadata.get("page_number")}
Content:
{document.page_content}
"""
        )

    return "\n\n".join(context_parts)


def answer_question(query: str) -> RAGResponse:
    documents = retrieve(query)

    if not documents:
        return RAGResponse(
            answer="I don't have enough information in the "
            "provided documentation to answer this question.",
            sources=[],
            context="",
        )

    context = build_context(documents)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=f"""Documentation context:

{context}

User question:
{query}

Answer the question using only the documentation context."""
        ),
    ]

    llm = create_llm()

    response = llm.invoke(
        messages,
        config={
            "metadata": {
                "component": "rag",
                "environment": "local",
            },
            "tags": ["rag", "gemini"],
        },
    )

    return RAGResponse(
        answer=response.content,
        sources=[
            Source(
                file_name=document.metadata["file_name"],
                page_number=document.metadata["page_number"],
            )
            for document in documents
        ],
        context=context
    )
