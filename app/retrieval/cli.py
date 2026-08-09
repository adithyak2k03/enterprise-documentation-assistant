import sys

from app.retrieval.service import retrieve


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python -m app.retrieval.cli <query>")

    query = sys.argv[1]

    documents = retrieve(query)

    print(f"Retrieved {len(documents)} documents.\n")

    for index, document in enumerate(documents, start=1):
        print(f"--- RESULT {index} ---")
        print(document.page_content[:500])
        print(document.metadata)
        print()


if __name__ == "__main__":
    main()
