import sys

from app.ingestion.service import ingest_pdf


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python -m app.ingestion.cli <pdf_path>")

    chunks = ingest_pdf(sys.argv[1])

    print(f"Generated {len(chunks)} chunks.")

    for chunk in chunks[:3]:
        print("\n--- CHUNK ---")
        print(chunk.page_content[:500])
        print(chunk.metadata)


if __name__ == "__main__":
    main()