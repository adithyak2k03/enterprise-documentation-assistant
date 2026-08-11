from typing import Literal

from pydantic import BaseModel, Field

EvaluationCategory = Literal[
    "Answerable",
    "Answerable but requires combining information",
    "Unanswerable",
]


class ExpectedSource(BaseModel):
    file_name: str
    page_number: int


class EvaluationCase(BaseModel):
    id: str
    question: str
    expected_answer: str | None
    expected_sources: list[ExpectedSource] = Field(default_factory=list)
    answerable: bool
    category: EvaluationCategory
