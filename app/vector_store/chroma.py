from langchain_chroma import Chroma

from app.embeddings.service import create_embeddings

COLLECTION_NAME = "documentation"


def create_vector_store() -> Chroma:
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=create_embeddings(),
        persist_directory=".chroma",
    )
