from pathlib import Path
from uuid import uuid4

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


def load_pdf(file_path: str) -> list[Document]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Document not found: {file_path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Unsupported file type: {path.suffix}")

    document_id = str(uuid4())

    loader = PyPDFLoader(str(path))
    documents = loader.load()

    for document in documents:
        document.metadata.update(
            {
                "document_id": document_id,
                "file_name": path.name,
                "source": str(path),
                "page_number": document.metadata.get("page", 0) + 1,
            }
        )

    return documents