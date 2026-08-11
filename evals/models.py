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

class JudgeResult(BaseModel):
    score: int = Field(ge=1, le=5)
    reasoning: str


class EvaluationResult(BaseModel):
    id: str
    category: EvaluationCategory
    source_score: float
    answer_correctness: JudgeResult | None = None
    faithfulness: JudgeResult | None = None