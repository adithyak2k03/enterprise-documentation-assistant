# Enterprise Documentation Assistant

An enterprise-style documentation assistant built around LLMs and Retrieval-Augmented Generation (RAG).

The project allows documentation such as PDFs to be ingested, processed into chunks, embedded into a vector store, and queried using natural language. The retrieved documentation is then provided to an LLM to generate grounded answers with source information.

The project is being built incrementally, with the focus on understanding the underlying architecture rather than putting every component into the project from the beginning.

## Current Features

- PDF and text document ingestion
- Document upload, list, and delete API lifecycle
- Local SQLite-backed document persistence
- Document metadata and file storage handling
- Recursive text chunking for retrieval
- Google Gemini embeddings
- Chroma vector store integration
- Similarity-based retrieval with relevance safeguards
- Conversation creation and message persistence in SQLite
- Bounded recent-context memory for multi-turn Q&A
- LangGraph orchestration around the RAG flow
- FastAPI app wrapper for local testing and debugging
- Swagger/OpenAPI docs for interactive API validation
- Query endpoint with optional conversation ID support
- Context-grounded answer generation with source metadata
- LangSmith tracing for LLM/RAG execution
- Environment-based configuration
- Pytest-based testing and API contract checks
- Ruff linting and formatting

## Current Architecture

```mermaid
flowchart TD
    A[PDF Document] --> B[PDF Loader]
    B --> C[Document Metadata]
    C --> D[Text Chunking]
    D --> E[Gemini Embeddings]
    E --> F[Chroma Vector Store]

    G[User Question] --> H[Similarity Retrieval]
    F --> H
    H --> I[Relevant Chunks]
    I --> J[Context Construction]
    J --> K[Gemini LLM]
    K --> L[Grounded Answer]
    I --> M[Sources]

    K -. Tracing .-> N[LangSmith]
```

## Technology Stack

### Backend and Language

- Python 3.12
- LangChain
- Pydantic Settings

### LLM and AI

- Google Gemini
- Gemini Embeddings
- LangSmith

### Retrieval

- Chroma
- Vector similarity search
- Metadata filtering

### Development

- uv
- pytest
- Ruff
- Git

## Project Structure

```text
enterprise-documentation-assistant/
│
├── app/
│   ├── api.py
│   ├── config.py
│   ├── cli.py
│   │
│   ├── llm/
│   │   ├── prompts.py
│   │   └── service.py
│   │
│   ├── langgraph/
│   │   ├── __init__.py
│   │   └── service.py
│   │
│   ├── ingestion/
│   │   ├── loader.py
│   │   ├── splitter.py
│   │   └── service.py
│   │
│   ├── embeddings/
│   │   └── service.py
│   │
│   ├── vector_store/
│   │   ├── chroma.py
│   │   └── service.py
│   │
│   ├── retrieval/
│   │   └── service.py
│   │
│   └── rag/
│       ├── prompts.py
│       ├── service.py
│       └── cli.py
│
├── tests/
│   ├── test_api.py
│   ├── test_config.py
│   ├── test_langgraph.py
│   └── ...
├── docs/
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── pyproject.toml
└── uv.lock
```

The core RAG functionality is kept independent from the eventual HTTP API layer. This allows the ingestion, retrieval, and generation logic to be tested and executed without FastAPI.

## Configuration

Configuration is loaded through Pydantic Settings and environment variables.

Example:

```env
# LLM
LLM_PROVIDER=google
LLM_MODEL=gemini-2.5-flash
LLM_API_KEY=

# Embeddings
EMBEDDING_MODEL=gemini-embedding-001

# LangSmith
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=enterprise-documentation-assistant
```

The actual `.env` file is not committed to the repository.

## Running the Project

Install dependencies:

```bash
uv sync
```

Run the LLM example:

```bash
uv run python -m app.cli
```

Ingest a PDF:

```bash
uv run python -m app.ingestion.cli "path/to/document.pdf"
```

Run a retrieval query:

```bash
uv run python -m app.retrieval.cli "your question"
```

Run the RAG pipeline:

```bash
uv run python -m app.rag.cli "your question"
```

Run tests:

```bash
uv run pytest
```

Run linting:

```bash
uv run ruff check .
```

Start the FastAPI app locally:

```bash
uv run uvicorn app.api:app --reload
```

Then open the Swagger UI:

```text
http://127.0.0.1:8000/docs
```

### Swagger smoke test checklist

Test these in order from the Swagger UI:

1. `GET /health`
   - should return `{"status": "ok"}`
2. `POST /documents`
   - upload a small PDF or text file
   - confirm a 201 response with `id`, `file_name`, `stored_name`, `mime_type`, `file_path`, and `uploaded_at`
3. `GET /documents`
   - confirm the uploaded document appears in the returned list
4. `DELETE /documents/{document_id}`
   - confirm the document is removed and the response contains `deleted: true`
5. `POST /conversations`
   - create a conversation and confirm the returned `id` and timestamps
6. `POST /conversations/{conversation_id}/messages`
   - add a user message and an assistant reply to validate the thread model
7. `GET /conversations/{conversation_id}/messages`
   - confirm the list is returned in order
8. `POST /query`
   - submit a question like `"What does this document say about agents?"` with an optional `conversation_id`
   - confirm a valid answer payload with `answer`, `sources`, and `context`

Expected validation notes:

- document upload should reject empty filenames
- document upload should reject empty files
- invalid message roles should be rejected with HTTP 400
- blank message content should be rejected with HTTP 400
- query should reject blank questions with HTTP 400
- missing document IDs should return 404 on delete
- missing conversations should return 404 on message and query requests

### Current milestone status

The project has reached the milestone of a working local RAG + memory-enabled API:

1. persisted document storage and lifecycle
2. persisted conversation history and bounded chat memory
3. query endpoint wired to recent conversation context
4. local API validation via FastAPI and Swagger
5. contract-level regression coverage in pytest

The next likely steps are not architectural rework but practical hardening:

1. automatic ingestion of uploaded documents into the vector store
2. retrieval tuning and evaluation coverage
3. deployment packaging and environment stabilization
4. optional frontend or operational UI only if a concrete workflow requires it

## RAG Pipeline

The current implementation follows a simple two-step RAG architecture.

### Ingestion

```text
PDF
 ↓
PDF Loader
 ↓
Document objects
 ↓
Metadata enrichment
 ↓
Text splitting
 ↓
Chunks
 ↓
Embeddings
 ↓
Chroma
```

### Question Answering

```text
Question
 ↓
Similarity Search
 ↓
Relevant Chunks
 ↓
Context Construction
 ↓
Gemini
 ↓
Grounded Answer
 ↓
Source Information
```

The system also applies a retrieval relevance threshold so that low-relevance results are not blindly passed to the LLM.

## Observability

LangSmith is integrated from the early stages of the project rather than being added after the RAG pipeline.

It is currently used to observe:

- LLM calls
- RAG execution
- Metadata and tags associated with runs
- Development and debugging information

Application logging and LangSmith are kept conceptually separate. Application logging will be responsible for operational events and errors, while LangSmith is used for LLM/RAG observability.

Sensitive information such as API keys should never be added to application logs or custom trace metadata.

## Development Approach

The project is intentionally being developed incrementally.

The current implementation focuses on a working RAG foundation plus a minimal orchestration and API layer. LangGraph is used as a thin orchestration wrapper, while FastAPI remains a lightweight local API surface for testing and demonstration. The current milestone includes document storage, persisted conversations, and bounded memory support without overbuilding the system beyond the immediate product need.

The next planned milestones are:

- automatic document-to-vector ingestion after upload
- retrieval quality improvements and a small evaluation set
- deployment packaging and environment hardening
- optional frontend or admin tooling only when user workflows justify it

These will be introduced only when they solve an actual requirement rather than being added for the sake of increasing the technology list.
