from pydantic import BaseModel, Field


class Source(BaseModel):
    file_name: str
    page_number: int


class RAGResponse(BaseModel):
    answer: str
    sources: list[Source] = Field(default_factory=list)
    context: str = ""
