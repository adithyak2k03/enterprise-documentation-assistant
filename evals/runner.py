import json
from pathlib import Path

from app.rag.models import Source
from app.rag.service import answer_question
from evals.models import EvaluationCase

DATASET_PATH = Path(__file__).parent / "dataset.json"

ABSTENTION_MESSAGE = (
    "I don't have enough information in the provided documentation to answer this question."
)


def load_dataset() -> list[EvaluationCase]:
    with DATASET_PATH.open(encoding="utf-8") as file:
        data = json.load(file)

    return [EvaluationCase.model_validate(item) for item in data]


def source_match_score(
    expected_sources,
    actual_sources: list[Source],
) -> float:
    if not expected_sources:
        return 1.0 if not actual_sources else 0.0

    expected = {(source.file_name, source.page_number) for source in expected_sources}

    actual = {(source.file_name, source.page_number) for source in actual_sources}

    return len(expected & actual) / len(expected)


def evaluate_abstention(
    expected_answerable: bool,
    answer: str,
) -> bool:
    if expected_answerable:
        return True

    return ABSTENTION_MESSAGE.lower() in answer.lower()


def run_evaluations() -> None:
    cases = load_dataset()

    for index, case in enumerate(cases, start=1):
        result = answer_question(case.question)

        source_score = source_match_score(
            case.expected_sources,
            result.sources,
        )

        abstention_correct = evaluate_abstention(
            case.answerable,
            result.answer,
        )

        print(f"\nEvaluation {index}")
        print(f"Category: {case.category}")
        print(f"Question: {case.question}")
        print(f"Source score: {source_score:.2f}")
        print(f"Abstention correct: {abstention_correct}")
        print(f"Answer: {result.answer}")


if __name__ == "__main__":
    run_evaluations()
