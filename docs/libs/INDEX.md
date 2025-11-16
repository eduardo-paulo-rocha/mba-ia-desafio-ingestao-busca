# Library Documentation Index

## Overview

This directory contains comprehensive documentation for all critical third-party libraries used in the MBA RAG (Retrieval-Augmented Generation) project. Each library file includes installation instructions, basic usage, advanced patterns, and integration examples specific to this project's architecture.

## Project Architecture

The RAG pipeline follows this flow:

```
PDF Files (.pdf)
    ↓
    └─→ [Ingestion Pipeline] ──→ PyPDF (extract text)
                                  ├─→ LangChain (chunk text)
                                  └─→ OpenAI/Gemini (generate embeddings)
                                      ↓
                                      [Vector Database]
                                      ├─→ PostgreSQL + pgvector (store chunks & vectors)
                                      └─→ Psycopg (database adapter)
                                          ↓
                                          [User Queries]
                                          ├─→ OpenAI/Gemini (query embedding)
                                          ├─→ LangChain (retrieval chain)
                                          └─→ PostgreSQL (similarity search)
                                              ↓
                                              [Response Generation]
                                              └─→ ChatOpenAI/Gemini (LLM response)
                                                  ↓
                                                  User Response
```

## Library Documentation Files

### Core Framework

#### 1. [LANGCHAIN.md](LANGCHAIN.md)
- **Type:** AI Application Framework
- **Version:** 0.3.27+
- **Purpose:** Orchestrates entire RAG pipeline from ingestion to response
- **Key Components:**
  - LLMChain and Runnable abstractions
  - Document loaders and text splitters
  - Vector store integrations
  - Prompt templates and chains
- **Use Cases:**
  - Building chat applications
  - Creating RAG pipelines
  - Document processing workflows
- **Project Integration:** Core orchestration layer for `src/chat.py` and `src/search.py`

---

### Database & Vector Storage

#### 2. [LANGCHAIN_POSTGRES.md](LANGCHAIN_POSTGRES.md)
- **Type:** PostgreSQL Vector Store Integration
- **Version:** Latest (LangChain-postgres)
- **Purpose:** Connects LangChain to PostgreSQL+pgvector for semantic search
- **Key Components:**
  - PGEngine initialization
  - PGVectorStore creation and management
  - Async similarity search operations
  - Bulk loading with COPY
  - Index management (HNSW, IVFFlat)
- **Use Cases:**
  - Storing document chunks with embeddings
  - Semantic similarity search
  - Hybrid search combining vector and metadata
- **Project Integration:** Core component for storing and retrieving PDF chunks in `src/ingest.py` and `src/search.py`

#### 3. [PGVECTOR.md](PGVECTOR.md)
- **Type:** PostgreSQL Extension for Vector Operations
- **Version:** 0.3.6
- **Purpose:** Adds vector similarity search capabilities to PostgreSQL
- **Key Features:**
  - Multiple vector types (full precision, half precision, sparse, binary)
  - Distance metrics (L2, cosine, inner product, Hamming, Jaccard)
  - HNSW and IVFFlat indexing strategies
  - Performance optimization techniques
- **Use Cases:**
  - Storing 1536-dimensional embeddings from OpenAI/Gemini
  - Fast similarity search across millions of chunks
  - Supporting hybrid queries with metadata filtering
- **Project Integration:** Storage backend for semantic search operations

#### 4. [PSYCOPG.md](PSYCOPG.md)
- **Type:** PostgreSQL Database Adapter
- **Version:** 3.2.9
- **Purpose:** Python interface to PostgreSQL database
- **Key Features:**
  - Synchronous and asynchronous operations
  - Connection pooling for concurrent access
  - COPY operations for bulk loading (100x faster)
  - Type adaptation for custom types (vectors, JSON)
  - Parameterized queries (SQL injection protection)
- **Use Cases:**
  - Database connection management
  - Bulk ingestion of chunks
  - Similarity search queries
  - Vector type registration
- **Project Integration:** Database layer used by LangChain-Postgres for all DB operations

---

### LLM API Integration

#### 5. [OPENAI.md](OPENAI.md)
- **Type:** OpenAI API Python Client
- **Version:** 1.102.0
- **Purpose:** Access to GPT-4, embeddings, and other OpenAI APIs
- **Key Features:**
  - Chat completions with streaming
  - Function calling for tool use
  - Vision capabilities (image analysis)
  - Embeddings generation (text-embedding-3-small: 1536 dimensions)
  - Batch processing API
  - Error handling and retries
- **Use Cases:**
  - Generating embeddings for chunks during ingestion
  - Answering user questions using LLM
  - Multi-turn conversations
- **Project Integration:**
  - Embedding generation in `src/ingest.py`
  - Response generation in `src/search.py`
  - Chat management in `src/chat.py`
- **Models Used:**
  - `text-embedding-3-small` (1536 dimensions, cost-effective)
  - `gpt-4` (reasoning, complex tasks)

#### 6. [GOOGLE_GENAI.md](GOOGLE_GENAI.md)
- **Type:** Google Generative AI Python Client
- **Purpose:** Access to Gemini models and embeddings (alternative to OpenAI)
- **Key Features:**
  - Gemini Pro and Flash models
  - Multimodal input (text, images, video)
  - Function calling
  - JSON mode and structured outputs
  - Context caching for cost reduction
  - Batch processing
- **Use Cases:**
  - Alternative LLM provider to OpenAI
  - Multimodal document analysis
  - Cost optimization through caching
- **Project Integration:**
  - Can be used instead of OpenAI for embedding and response generation
  - Configured via `LLM_PROVIDER` in `.env`

---

### Document Processing

#### 7. [PYPDF.md](PYPDF.md)
- **Type:** PDF Processing Library
- **Version:** 6.0.0
- **Purpose:** Extract text and metadata from PDF files
- **Key Features:**
  - Text extraction from PDFs
  - Page manipulation (merge, split, rotate, crop)
  - Metadata handling
  - Encryption/decryption support
  - Watermarking and stamping
  - Batch processing
- **Use Cases:**
  - Extracting text from source PDFs
  - Splitting multi-page documents
  - Preprocessing before chunking
- **Project Integration:** Primary document loader in `src/ingest.py` for extracting text from `PDF_PATH`

---

### Configuration Management

#### 8. [PYTHON_DOTENV.md](PYTHON_DOTENV.md)
- **Type:** Environment Configuration Manager
- **Version:** 1.1.1
- **Purpose:** Load configuration from `.env` files securely
- **Key Features:**
  - Load environment variables from `.env` file
  - Variable interpolation with `${VAR}` syntax
  - Multiple environment support (.env.development, .env.production)
  - Validation and type conversion
  - POSIX variable expansion
- **Use Cases:**
  - Managing API keys (OPENAI_API_KEY, GOOGLE_API_KEY)
  - Database connection strings (DATABASE_URL)
  - Application paths and settings (PDF_PATH, DEBUG)
  - Environment-specific configuration
- **Project Integration:** Centralized configuration system for all `src/` modules
- **Critical Variables:**
  ```env
  DATABASE_URL=postgresql://...
  OPENAI_API_KEY=sk-...
  GOOGLE_API_KEY=AIza...
  PDF_PATH=./documents/
  LLM_PROVIDER=openai  # or 'google'
  ```

---

## Quick Reference by Use Case

### Adding a New PDF to the System

**Files to Reference:**
1. [PYPDF.md](PYPDF.md) - Understanding PDF text extraction
2. [LANGCHAIN.md](LANGCHAIN.md) - Text splitting strategies
3. [PSYCOPG.md](PSYCOPG.md) - Database operations
4. [PYTHON_DOTENV.md](PYTHON_DOTENV.md) - Configuration management

**Process:** PDF → PyPDF (extract) → LangChain (chunk) → OpenAI/Gemini (embed) → Psycopg (store) → pgvector (index)

### Searching and Retrieving Documents

**Files to Reference:**
1. [LANGCHAIN_POSTGRES.md](LANGCHAIN_POSTGRES.md) - Vector store retrieval
2. [PGVECTOR.md](PGVECTOR.md) - Similarity metrics and indexing
3. [OPENAI.md](OPENAI.md) / [GOOGLE_GENAI.md](GOOGLE_GENAI.md) - Embedding generation
4. [LANGCHAIN.md](LANGCHAIN.md) - RAG pipeline orchestration

**Process:** Query → Embed → Similarity Search → Retrieve Context → Generate Response

### Configuring API Keys and Credentials

**Files to Reference:**
1. [PYTHON_DOTENV.md](PYTHON_DOTENV.md) - .env setup and management
2. [OPENAI.md](OPENAI.md) - OpenAI configuration
3. [GOOGLE_GENAI.md](GOOGLE_GENAI.md) - Google configuration
4. [PSYCOPG.md](PSYCOPG.md) - Database connection

### Optimizing Database Performance

**Files to Reference:**
1. [PGVECTOR.md](PGVECTOR.md) - Index strategies (HNSW vs IVFFlat)
2. [PSYCOPG.md](PSYCOPG.md) - Connection pooling and COPY operations
3. [LANGCHAIN_POSTGRES.md](LANGCHAIN_POSTGRES.md) - Bulk loading patterns

### Switching Between LLM Providers

**Files to Reference:**
1. [OPENAI.md](OPENAI.md) - GPT-4, embeddings setup
2. [GOOGLE_GENAI.md](GOOGLE_GENAI.md) - Gemini, embeddings setup
3. [PYTHON_DOTENV.md](PYTHON_DOTENV.md) - LLM_PROVIDER configuration

---

## Configuration Quick Start

### .env File Template

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/rag
VECTOR_EXTENSION=vector

# LLM Configuration
OPENAI_API_KEY=sk-...              # Get from https://platform.openai.com/account/api-keys
GOOGLE_API_KEY=AIza...             # Get from https://ai.google.dev/

# LLM Provider Selection
LLM_PROVIDER=openai                # or 'google'
EMBEDDING_MODEL=text-embedding-3-small

# Application Paths
PDF_PATH=./documents/              # Where PDF files are stored
LOGS_PATH=./logs/                  # Where logs are written
CACHE_PATH=./cache/                # Cache directory

# Application Settings
DEBUG=False                         # Enable debug logging
LOG_LEVEL=INFO                     # Logging level
MAX_WORKERS=4                      # Concurrent workers
CHUNK_SIZE=1000                    # Text chunk size for splitting
CHUNK_OVERLAP=200                  # Overlap between chunks

# LLM Parameters
TEMPERATURE=0.7                    # Response randomness (0-1)
MAX_TOKENS=500                     # Maximum response length
```

### Project File Integration

```
docs/libs/
├── INDEX.md (this file)
├── LANGCHAIN.md ─────────┐
├── LANGCHAIN_POSTGRES.md │
├── PGVECTOR.md           │
├── PSYCOPG.md            │
├── OPENAI.md             ├─→ Used by src/
├── GOOGLE_GENAI.md       │
├── PYPDF.md              │
└── PYTHON_DOTENV.md ─────┘

src/
├── chat.py ────────────────→ Imports LangChain, OpenAI/Google
├── search.py ──────────────→ Imports LangChain, Psycopg, pgvector
├── ingest.py ──────────────→ Imports PyPDF, LangChain, OpenAI/Google
└── config.py (reference) ──→ Uses python-dotenv
```

---

## Dependency Graph

```
python-dotenv (.env config)
    ↓
LangChain (core orchestration)
    ├─→ PYPDF (document loading)
    ├─→ OpenAI/Google GenAI (embeddings & LLM)
    ├─→ LangChain-Postgres (vector store)
    │     ├─→ Psycopg (DB connection)
    │     └─→ pgvector (vector operations)
    │         └─→ PostgreSQL (persistence)
    └─→ [Your Application]
        ├─→ chat.py (chat interface)
        ├─→ search.py (RAG pipeline)
        └─→ ingest.py (document ingestion)
```

---

## Common Integration Patterns

### Pattern 1: Basic RAG Query

```python
# See: LANGCHAIN.md, LANGCHAIN_POSTGRES.md, OPENAI.md
query = "What does the document say about X?"
embedding = openai_client.embeddings.create(input=query)
results = vector_store.similarity_search(embedding)
response = llm.generate(results + query)
```

### Pattern 2: Batch Ingestion

```python
# See: PYPDF.md, PSYCOPG.md, LANGCHAIN_POSTGRES.md
for pdf in directory:
    text = pdf_reader.extract_text(pdf)
    chunks = splitter.split(text)
    embeddings = embedding_model.embed(chunks)
    vector_store.bulk_insert(chunks, embeddings)
```

### Pattern 3: Multi-turn Conversation

```python
# See: LANGCHAIN.md, OPENAI.md/GOOGLE_GENAI.md
conversation_history = []
for user_message in messages:
    context = search_relevant_chunks(user_message)
    response = llm.generate(context + history)
    conversation_history.append(response)
```

### Pattern 4: Environment-aware Configuration

```python
# See: PYTHON_DOTENV.md, all library files
load_dotenv()
if os.getenv("LLM_PROVIDER") == "openai":
    use_openai_client()
else:
    use_gemini_client()
```

---

## Library Versions and Requirements

| Library | Version | Purpose |
|---------|---------|---------|
| langchain | 0.3.27+ | Core AI framework |
| langchain-postgres | Latest | Vector store integration |
| pgvector | 0.3.6 | Postgres vector type |
| psycopg | 3.2.9 | Postgres adapter |
| openai | 1.102.0 | OpenAI API client |
| google-generativeai | Latest | Google AI client |
| pypdf | 6.0.0 | PDF processing |
| python-dotenv | 1.1.1 | Environment config |

For complete requirements, see `requirements.txt` in project root.

---

## Troubleshooting Guide

### Issue: Connection to PostgreSQL Fails
**See:** [PSYCOPG.md](PSYCOPG.md#error-handling) - Connection troubleshooting  
**Also Check:**
- DATABASE_URL format in `.env`
- PostgreSQL server is running
- pgvector extension installed

### Issue: Embeddings Not Generated
**See:** [OPENAI.md](OPENAI.md#error-handling) / [GOOGLE_GENAI.md](GOOGLE_GENAI.md#error-handling)  
**Also Check:**
- API keys are correct
- Rate limits not exceeded
- Text input is valid

### Issue: PDF Text Not Extracting Properly
**See:** [PYPDF.md](PYPDF.md#error-handling)  
**Also Check:**
- PDF is not scanned image (use OCR if needed)
- PDF format is standard PDF
- File permissions are correct

### Issue: Vector Search Returns Poor Results
**See:** [PGVECTOR.md](PGVECTOR.md#performance-tips)  
**Also Check:**
- HNSW index is created
- Similarity metric is appropriate
- Chunk size and overlap are reasonable

---

## Additional Resources

### Official Documentation
- [LangChain Docs](https://docs.langchain.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Google Generative AI Docs](https://ai.google.dev/)
- [PostgreSQL pgvector](https://github.com/pgvector/pgvector)

### Project Documentation
- See `README.md` in project root for setup instructions
- See `docker-compose.yml` for database setup

### Getting Help
- Check the "Error Handling" section in each library file
- Review the "Integration with RAG Project" sections for practical examples
- Consult troubleshooting sections within individual library docs

---

## Document Maintenance

These documentation files are generated from official library sources using Context7 MCP. They are designed to be:
- **Practical:** Focused on real use cases in this project
- **Current:** Based on latest library versions
- **Integrated:** Show how libraries work together
- **Actionable:** Include copy-paste examples

**Last Updated:** 2024
**Project:** MBA RAG (Retrieval-Augmented Generation) Pipeline
