import pytest
from pydantic import ValidationError

from evals.models import EvaluationCase


def test_evaluation_case_validates():
    case = EvaluationCase(
        id="test-001",
        question="What is RAG?",
        expected_answer="Retrieval-Augmented Generation.",
        expected_sources=[],
        answerable=True,
        category="Answerable",
    )

    assert case.id == "test-001"


def test_invalid_category_is_rejected():
    with pytest.raises(ValidationError):
        EvaluationCase(
            id="test-001",
            question="What is RAG?",
            expected_answer="...",
            expected_sources=[],
            answerable=True,
            category="Something else",
        )
