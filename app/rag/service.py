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


def prepare_query_with_context(query: str, conversation_context: str | None = None) -> str:
    if not conversation_context:
        return query

    return (
        "Conversation history:\n"
        f"{conversation_context}\n\n"
        f"User question:\n{query}"
    )


def answer_question(query: str, conversation_context: str | None = None, document_id: str | None = None) -> RAGResponse:
    augmented_query = prepare_query_with_context(query, conversation_context)
    documents = retrieve(augmented_query, document_id=document_id)

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

Conversation history:
{conversation_context or 'None'}

User question:
{query}

Answer the question using only the documentation context and the recent conversation history when relevant."""
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
