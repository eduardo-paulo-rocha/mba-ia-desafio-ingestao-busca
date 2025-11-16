# LangChain PostgreSQL Integration

## Overview

**Version:** 0.0.15  
**Type:** Database Adapter  
**Repository:** https://github.com/langchain-ai/langchain-postgres  
**Documentation:** https://github.com/langchain-ai/langchain-postgres/blob/main/README.md

langchain-postgres provides PostgreSQL abstractions backed by the pgvector extension for vector similarity search. It offers seamless integration between LangChain's vector store abstractions and PostgreSQL, enabling efficient semantic search over large document collections.

## Key Features

### 1. Vector Storage
- **PGVectorStore**: Full precision vector storage and retrieval
- **PGVector**: 768-dimensional and variable-sized embeddings
- Efficient L2, cosine, and inner product distance calculations

### 2. Advanced Indexing
- HNSW (Hierarchical Navigable Small World) indexes
- IVFFlat (Inverted File Flat) indexes
- Configurable index parameters

### 3. Integration
- Native LangChain vector store interface
- Python SQLAlchemy ORM support
- Seamless Psycopg 3 integration

## Installation

```bash
# Basic installation
pip install langchain-postgres==0.0.15

# With development dependencies
poetry install --with dev

# With all optional dependencies
pip install langchain-postgres[all]
```

## Prerequisites

### PostgreSQL Setup

```bash
# Docker setup with pgvector
docker run --name pgvector-container \
  -e POSTGRES_USER=langchain \
  -e POSTGRES_PASSWORD=langchain \
  -e POSTGRES_DB=langchain \
  -p 6024:5432 \
  pgvector/pgvector:pg16
```

### Database Configuration

```python
# Connection string format
CONNECTION_STRING = "postgresql+psycopg://user:password@localhost:5432/dbname"

# PostgreSQL Connection Parameters
POSTGRES_USER = "langchain"
POSTGRES_PASSWORD = "langchain"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "6024"
POSTGRES_DB = "langchain"
TABLE_NAME = "vectorstore"
VECTOR_SIZE = 1536  # OpenAI embedding dimension
```

## Architecture

### Core Components

```
┌─────────────────────────────────────┐
│   LangChain Application             │
├─────────────────────────────────────┤
│   LangChain Vector Store Interface  │
├─────────────────────────────────────┤
│   langchain-postgres                │
│   ├─ PGVectorStore                 │
│   ├─ PGEngine                      │
│   └─ Vector Operations             │
├─────────────────────────────────────┤
│   PostgreSQL + pgvector            │
│   ├─ vector type                   │
│   ├─ Similarity operators (<->)    │
│   └─ Index types (HNSW, IVFFlat)  │
└─────────────────────────────────────┘
```

## Usage Examples

### 1. Basic Vector Store Setup

```python
from langchain_postgres import PGVectorStore, PGEngine
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

# Initialize engine
pg_engine = PGEngine.from_connection_string(
    url="postgresql+psycopg://langchain:langchain@localhost:6024/langchain"
)

# Initialize embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Create vector store
vector_store = PGVectorStore.create_sync(
    engine=pg_engine,
    table_name="documents",
    embedding_service=embeddings
)

# Add documents
docs = [
    Document(page_content="Document 1 content", metadata={"source": "doc1"}),
    Document(page_content="Document 2 content", metadata={"source": "doc2"}),
]
vector_store.add_documents(docs)
```

### 2. Similarity Search

```python
# Basic similarity search
query = "information retrieval"
results = vector_store.similarity_search(query, k=5)

for doc in results:
    print(f"Score: {doc.metadata.get('score', 'N/A')}")
    print(f"Content: {doc.page_content}\n")

# Search with distance threshold
results = vector_store.similarity_search_with_score(
    query, 
    k=10,
    filter={"distance": {"$lt": 0.5}}
)
```

### 3. Async Operations

```python
import asyncio
from langchain_postgres import PGVectorStore

async def async_search():
    # Async similarity search
    results = await vector_store.asimilarity_search(
        "query text",
        k=5,
        filter={"metadata_field": "value"}
    )
    return results

# Run async operation
results = asyncio.run(async_search())
```

### 4. Advanced Filtering

```python
# Filter with metadata
results = vector_store.similarity_search(
    "query",
    k=5,
    filter={
        "$or": [
            {"source": "doc1"},
            {"source": "doc2"}
        ]
    }
)

# Filter with inequality
results = vector_store.similarity_search(
    "query",
    k=10,
    filter={"score": {"$gte": 0.7}}
)

# Complex nested filters
results = vector_store.similarity_search(
    "query",
    filter={
        "$and": [
            {"type": "pdf"},
            {"$or": [
                {"category": "technical"},
                {"category": "research"}
            ]},
            {"date": {"$gte": "2024-01-01"}}
        ]
    }
)
```

### 5. Bulk Operations with COPY

```python
from io import StringIO

# Efficient bulk insert using COPY command
data = [
    ("Document 1", [0.1, 0.2, 0.3, ...]),  # embedding
    ("Document 2", [0.4, 0.5, 0.6, ...]),
    # ... more documents
]

with pg_engine.connection() as conn:
    with conn.cursor() as cur:
        with cur.copy("COPY documents (content, embedding) FROM STDIN") as copy:
            for content, embedding in data:
                copy.write_row([content, embedding])
```

### 6. Index Management

```python
# Initialize vectorstore table with HNSW index
pg_engine.init_vectorstore_table(
    table_name="documents",
    vector_size=1536
)

# Create additional index for metadata
pg_engine.execute("""
    CREATE INDEX idx_source ON documents(metadata->>'source')
""")
```

## Integration with RAG Project

### In `src/ingest.py`

```python
from langchain_postgres import PGVectorStore, PGEngine
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def ingest_pdf(pdf_path: str):
    # Load PDF
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    
    # Split documents
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(docs)
    
    # Create embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Store in PostgreSQL
    pg_engine = PGEngine.from_connection_string(
        url=os.getenv("DATABASE_URL")
    )
    
    vector_store = PGVectorStore.create_sync(
        engine=pg_engine,
        table_name="pdf_documents",
        embedding_service=embeddings
    )
    
    # Add documents
    vector_store.add_documents(chunks)
    print(f"Stored {len(chunks)} chunks")
```

### In `src/search.py`

```python
from langchain_postgres import PGVectorStore, PGEngine
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA

def search_prompt(question: str):
    # Setup vector store
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    pg_engine = PGEngine.from_connection_string(
        url=os.getenv("DATABASE_URL")
    )
    
    vector_store = PGVectorStore(
        embedding_service=embeddings,
        table_name="pdf_documents",
        connection="postgresql+psycopg://..."
    )
    
    # Create retriever
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    
    # Create QA chain
    llm = ChatOpenAI(model="gpt-4")
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever
    )
    
    # Execute query
    result = qa_chain({"query": question})
    return result["result"]
```

## Performance Optimization

### 1. Index Strategy

```python
# Create HNSW index for better quality
pg_engine.execute("""
    CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64)
""")

# Or IVFFlat for faster builds
pg_engine.execute("""
    CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100)
""")
```

### 2. Query Optimization

```python
# Use search with metadata filters to reduce result set
results = vector_store.similarity_search(
    query,
    k=20,  # Larger k for pre-filtering
    filter={"document_type": "research"}
)
# Then filter further in application if needed
```

### 3. Connection Pooling

```python
from psycopg_pool import ConnectionPool

pool = ConnectionPool(
    "postgresql+psycopg://user:pass@localhost/dbname",
    min_size=5,
    max_size=20
)

# Use pool in vector store operations
```

## Configuration

### Environment Variables

```bash
# PostgreSQL
DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/dbname

# OpenAI
OPENAI_API_KEY=sk-...

# Application
VECTOR_TABLE_NAME=pdf_documents
VECTOR_SIZE=1536
SEARCH_K=5
```

## Schema Reference

### Default Table Structure

```sql
CREATE TABLE documents (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    content text NOT NULL,
    embedding vector(1536) NOT NULL,
    metadata jsonb,
    created_at timestamp DEFAULT now(),
    updated_at timestamp DEFAULT now()
);

CREATE INDEX idx_embedding ON documents USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_metadata ON documents USING GIN (metadata);
```

## Error Handling

```python
try:
    results = vector_store.similarity_search(query, k=5)
except Exception as e:
    print(f"Search failed: {e}")
    # Fallback to keyword search or retry with different parameters
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Connection refused | PostgreSQL not running | Start PostgreSQL container |
| pgvector not found | Extension not installed | Run `CREATE EXTENSION vector` |
| Dimension mismatch | Wrong embedding size | Match VECTOR_SIZE with model output |
| Slow queries | Missing indexes | Create HNSW or IVFFlat indexes |

## References

- [GitHub Repository](https://github.com/langchain-ai/langchain-postgres)
- [LangChain Documentation](https://docs.langchain.com/)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
