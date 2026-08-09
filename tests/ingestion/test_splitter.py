from langchain_core.documents import Document

from app.ingestion.splitter import split_documents


def test_split_documents_preserves_document_id():
    documents = [
        Document(
            page_content="This is a test document. " * 100,
            metadata={
                "document_id": "doc-123",
                "file_name": "test.pdf",
                "source": "test.pdf",
                "page_number": 1,
            },
        )
    ]

    chunks = split_documents(
        documents,
        chunk_size=100,
        chunk_overlap=20,
    )

    assert len(chunks) > 1

    for chunk in chunks:
        assert chunk.metadata["document_id"] == "doc-123"
        assert "chunk_id" in chunk.metadata
        assert chunk.page_content