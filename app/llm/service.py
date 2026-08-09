from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import settings


def create_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=settings.llm_model,
        google_api_key=settings.llm_api_key,
        temperature=0,
    )
