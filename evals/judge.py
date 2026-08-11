from langchain_core.messages import HumanMessage, SystemMessage

from app.llm.service import create_llm
from evals.models import JudgeResult

ANSWER_CORRECTNESS_PROMPT = """You are evaluating the correctness of an answer
to a documentation question.

Compare the expected answer with the generated answer.

Score from 1 to 5:

5 = Completely correct and equivalent in meaning
4 = Mostly correct with minor omissions
3 = Partially correct
2 = Mostly incorrect
1 = Completely incorrect

Return only valid JSON:
{
  "score": 1-5,
  "reasoning": "..."
}
"""


FAITHFULNESS_PROMPT = """You are evaluating whether an answer is supported by
the provided documentation context.

The answer must not introduce facts that are unsupported by the context.

Score from 1 to 5:

5 = Fully supported by the context
4 = Mostly supported with minor issues
3 = Partially supported
2 = Contains significant unsupported claims
1 = Mostly or completely unsupported

Return only valid JSON:
{
  "score": 1-5,
  "reasoning": "..."
}
"""


def judge_answer_correctness(
    question: str,
    expected_answer: str,
    generated_answer: str,
) -> JudgeResult:
    llm = create_llm()

    prompt = f"""
Question:
{question}

Expected answer:
{expected_answer}

Generated answer:
{generated_answer}
"""

    response = llm.invoke(
        [
            SystemMessage(content=ANSWER_CORRECTNESS_PROMPT),
            HumanMessage(content=prompt),
        ]
    )

    content = response.content.strip()

    if content.startswith("```json"):
        content = content[7:]

    if content.endswith("```"):
        content = content[:-3]

    return JudgeResult.model_validate_json(content.strip())


def judge_faithfulness(
    question: str,
    context: str,
    generated_answer: str,
) -> JudgeResult:
    llm = create_llm()

    prompt = f"""
Question:
{question}

Documentation context:
{context}

Generated answer:
{generated_answer}
"""

    response = llm.invoke(
        [
            SystemMessage(content=FAITHFULNESS_PROMPT),
            HumanMessage(content=prompt),
        ]
    )

    content = response.content.strip()

    if content.startswith("```json"):
        content = content[7:]

    if content.endswith("```"):
        content = content[:-3]

    return JudgeResult.model_validate_json(content.strip())
