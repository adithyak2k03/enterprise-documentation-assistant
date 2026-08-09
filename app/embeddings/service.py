from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import settings


def create_embeddings() -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model,
        google_api_key=settings.llm_api_key,
    )
