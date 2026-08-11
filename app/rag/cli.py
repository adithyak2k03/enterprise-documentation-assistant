import sys

from app.rag.service import answer_question


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python -m app.rag.cli "<question>"')

    question = sys.argv[1]

    result = answer_question(question)

    print("\nANSWER")
    print("======")
    print(result.answer)

    print("\nSOURCES")
    print("=======")

    for source in result.sources:
        print(f"- {source.metadata.get('file_name')} (page {source.metadata.get('page_number')})")


if __name__ == "__main__":
    main()
