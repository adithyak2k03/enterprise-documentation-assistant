from langchain_core.messages import HumanMessage, SystemMessage

from app.llm.prompts import SYSTEM_PROMPT
from app.llm.service import create_llm


def main() -> None:
    llm = create_llm()

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content="Explain Retrieval-Augmented Generation in one paragraph."),
    ]

    response = llm.invoke(
        messages,
        config={
            "metadata": {
                "component": "llm",
                "environment": "local",
            },
            "tags": ["llm", "gemini"],
        },
    )

    print(response.content)


if __name__ == "__main__":
    main()
