from langchain_core.documents import Document

from app.vector_store.chroma import create_vector_store


def retrieve(
    query: str,
    top_k: int = 4,
    document_id: str | None = None,
) -> list[Document]:
    vector_store = create_vector_store()

    filter_metadata = None

    if document_id:
        filter_metadata = {"document_id": document_id}

    return vector_store.similarity_search(
        query,
        k=top_k,
        filter=filter_metadata,
    )
