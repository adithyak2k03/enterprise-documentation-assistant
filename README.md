# Enterprise Documentation Assistant

An enterprise-style documentation assistant built around LLMs and Retrieval-Augmented Generation (RAG).

The project allows documentation such as PDFs to be ingested, processed into chunks, embedded into a vector store, and queried using natural language. The retrieved documentation is then provided to an LLM to generate grounded answers with source information.

The project is being built incrementally, with the focus on understanding the underlying architecture rather than putting every component into the project from the beginning.

## Current Features

- PDF document ingestion
- Document metadata extraction
- Recursive text chunking
- Google Gemini embeddings
- Chroma vector store
- Similarity-based retrieval
- Metadata-aware retrieval
- Retrieval relevance threshold
- Gemini-based answer generation
- Context-grounded responses
- Source information in responses
- LangSmith tracing for LLM/RAG execution
- Environment-based configuration
- Pytest-based testing
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
│   ├── config.py
│   ├── cli.py
│   │
│   ├── llm/
│   │   ├── prompts.py
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

The current implementation focuses on establishing a working RAG foundation before adding application infrastructure such as FastAPI and LangGraph.

The next planned milestones are:

- Improve retrieval quality and introduce a practical evaluation dataset
- Add conversation history
- Introduce LangGraph where it provides a clear benefit
- Expose the application through FastAPI
- Add document management APIs
- Add Docker-based deployment
- Consider a lightweight frontend if it adds meaningful value

These will be introduced only when they solve an actual requirement rather than being added for the sake of increasing the technology list.
