from langchain_core.documents import Document

from app.vector_store.chroma import create_vector_store


def add_documents(documents: list[Document]) -> list[str]:
    vector_store = create_vector_store()

    return vector_store.add_documents(documents)
