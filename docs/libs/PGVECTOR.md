# pgvector

## Overview

**Version:** 0.3.6  
**Type:** PostgreSQL Extension  
**Repository:** https://github.com/pgvector/pgvector  
**Documentation:** https://github.com/pgvector/pgvector

pgvector is an open-source vector similarity search extension for PostgreSQL that enables efficient storage and querying of high-dimensional vectors. It provides exact and approximate nearest neighbor search capabilities, making it ideal for semantic search, recommendation systems, and machine learning applications.

## Key Features

### 1. Vector Types
- **Vector**: Full precision (32-bit float) embeddings
- **Halfvec**: Half precision (16-bit float) for memory efficiency
- **Sparsevec**: Sparse vectors for high-dimensional sparse embeddings
- **Bit**: Binary quantization for ultra-compact storage (8x compression)

### 2. Distance Metrics
- **L2 Distance** (`<->`): Euclidean distance
- **Cosine Distance** (`<=>`): Angular distance for normalized vectors
- **Inner Product** (`<#>`): Dot product for maximum similarity
- **Hamming Distance**: For binary vectors
- **Jaccard Distance**: For sparse vectors

### 3. Indexing Algorithms
- **HNSW** (Hierarchical Navigable Small World): Better quality, higher memory
- **IVFFlat** (Inverted File Flat): Faster builds, lower memory usage

## Installation

### Docker (Recommended for Development)

```bash
# PostgreSQL with pgvector pre-installed
docker run --name pgvector-container \
  -e POSTGRES_USER=langchain \
  -e POSTGRES_PASSWORD=langchain \
  -e POSTGRES_DB=langchain \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

### Python Package (Client Library)

```bash
# pgvector Python library
pip install pgvector==0.3.6

# SQLAlchemy integration
pip install pgvector[sqlalchemy]

# Django ORM integration
pip install pgvector[django]
```

### PostgreSQL Extension

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT version();
```

## Architecture

### Vector Type System

```
Full Precision Vector (32-bit float)
├── Default type for most applications
├── Dimension: up to 65535
├── Memory: 4 bytes per dimension
└── Best for: Production use, high accuracy

Half Precision Vector (16-bit float)
├── 50% memory reduction
├── Dimension: up to 65535
├── Memory: 2 bytes per dimension
└── Best for: Large-scale deployments, slight accuracy trade-off

Binary Quantization (1 bit)
├── 32x compression vs full precision
├── Dimension: up to 524,280 (due to bit packing)
├── Memory: 0.125 bytes per dimension
└── Best for: Ultra-large scale, very fast search

Sparse Vector
├── Stores only non-zero values
├── Efficient for high-dimensional sparse data
├── Best for: SPLADE embeddings, BM25 expansion
```

## Usage Examples

### 1. Basic Vector Operations with Psycopg 3

```python
import psycopg
from pgvector.psycopg import register_vector
import numpy as np

# Connect and register vector types
conn = psycopg.connect("postgresql://user:pass@localhost/dbname", autocommit=True)
conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
register_vector(conn)

# Create table
conn.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id bigserial PRIMARY KEY,
        content text,
        embedding vector(1536)
    )
""")

# Insert vectors
embedding = np.random.rand(1536).astype(np.float32)
conn.execute(
    "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
    ("Document content", embedding)
)

# Similarity search - L2 distance
query_embedding = np.random.rand(1536).astype(np.float32)
results = conn.execute(
    "SELECT id, content FROM documents ORDER BY embedding <-> %s LIMIT 5",
    (query_embedding,)
).fetchall()

# Cosine distance search
results = conn.execute(
    "SELECT id, content, embedding <=> %s AS distance FROM documents ORDER BY distance LIMIT 5",
    (query_embedding,)
).fetchall()
```

### 2. Django ORM Integration

```python
from django.db import models
from pgvector.django import VectorField, HalfVectorField

class Document(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    embedding = VectorField(dimensions=1536)  # Full precision
    half_embedding = HalfVectorField(dimensions=768)  # Half precision

# Semantic search
from pgvector.django import CosineDistance

query_embedding = get_embedding("search query")
similar_docs = Document.objects.annotate(
    distance=CosineDistance('embedding', query_embedding)
).order_by('distance')[:10]

for doc in similar_docs:
    print(f"{doc.title}: {doc.distance}")
```

### 3. SQLAlchemy Integration

```python
from sqlalchemy import create_engine, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from pgvector.sqlalchemy import Vector
import numpy as np

class Base(DeclarativeBase):
    pass

class Document(Base):
    __tablename__ = 'documents'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[Vector] = mapped_column(Vector(1536))

# Create tables
engine = create_engine('postgresql://user:pass@localhost/dbname')
Base.metadata.create_all(engine)

# Insert and search
with Session(engine) as session:
    # Add document
    doc = Document(
        title="ML Guide",
        content="Introduction to machine learning...",
        embedding=np.array([0.1, 0.2, 0.3, ...])
    )
    session.add(doc)
    session.commit()
    
    # Search
    query_vec = np.array([0.15, 0.25, 0.35, ...])
    results = session.query(Document).order_by(
        Document.embedding.l2_distance(query_vec)
    ).limit(5).all()
```

### 4. Indexing for Performance

```python
from sqlalchemy import Index, text
from pgvector.sqlalchemy import Vector

# HNSW index for better quality
hnsw_index = Index(
    'embedding_hnsw_idx',
    Document.embedding,
    postgresql_using='hnsw',
    postgresql_with={'m': 16, 'ef_construction': 64},
    postgresql_ops={'embedding': 'vector_l2_ops'}
)

# IVFFlat index for faster builds
ivfflat_index = Index(
    'embedding_ivfflat_idx',
    Document.embedding,
    postgresql_using='ivfflat',
    postgresql_with={'lists': 100},
    postgresql_ops={'embedding': 'vector_cosine_ops'}
)

# Create indexes
with engine.begin() as conn:
    hnsw_index.create(conn)
    ivfflat_index.create(conn)
```

### 5. RAG-Specific Example

```python
import psycopg
from pgvector.psycopg import register_vector
from openai import OpenAI
import numpy as np

# Setup database
conn = psycopg.connect("postgresql://langchain:langchain@localhost:5432/rag")
conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
register_vector(conn)

conn.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_base (
        id bigserial PRIMARY KEY,
        content text NOT NULL,
        embedding vector(1536),
        metadata jsonb
    )
""")

# Initialize OpenAI embeddings
client = OpenAI()

def embed_text(text):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return np.array(response.data[0].embedding)

# Store documents with embeddings
documents = [
    "Document 1 content...",
    "Document 2 content...",
    "Document 3 content..."
]

for i, doc in enumerate(documents):
    embedding = embed_text(doc)
    conn.execute(
        "INSERT INTO knowledge_base (content, embedding, metadata) VALUES (%s, %s, %s)",
        (doc, embedding, {"doc_id": i})
    )

# Create index
conn.execute("""
    CREATE INDEX ON knowledge_base USING hnsw (embedding vector_cosine_ops)
""")

# RAG retrieval function
def retrieve_context(query: str, top_k: int = 5):
    query_embedding = embed_text(query)
    
    results = conn.execute("""
        SELECT content, embedding <=> %s AS distance
        FROM knowledge_base
        ORDER BY distance
        LIMIT %s
    """, (query_embedding, top_k)).fetchall()
    
    return [row[0] for row in results]

# Example usage
context = retrieve_context("What is machine learning?")
for doc in context:
    print(f"Retrieved: {doc[:100]}...\n")
```

## Integration with RAG Project

### In Database Schema

```sql
-- Create main documents table with vectors
CREATE TABLE documents (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename text NOT NULL,
    content text NOT NULL,
    embedding vector(1536),
    chunk_number int,
    metadata jsonb,
    created_at timestamp DEFAULT now(),
    updated_at timestamp DEFAULT now()
);

-- HNSW index for cosine similarity
CREATE INDEX idx_embedding_cosine ON documents 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Additional indexes for metadata
CREATE INDEX idx_filename ON documents(filename);
CREATE INDEX idx_metadata ON documents USING GIN (metadata);

-- Statistics for query planning
ANALYZE documents;
```

### Configuration

```python
# In .env
DATABASE_URL=postgresql+psycopg://langchain:langchain@localhost:5432/rag
VECTOR_SIZE=1536
VECTOR_INDEX_TYPE=hnsw  # or 'ivfflat'
SEARCH_K=5
```

## Performance Considerations

### Index Selection

| Scenario | Recommended | Reason |
|----------|-------------|--------|
| < 10K vectors | No index | Linear search is fine |
| 10K-1M vectors | HNSW | Better recall, moderate memory |
| 1M+ vectors | IVFFlat | Lower memory, acceptable recall |
| Real-time critical | HNSW (m=32) | Highest accuracy |
| Cost sensitive | IVFFlat (lists=sqrt(n)) | Memory efficient |

### Optimization Tips

1. **Bulk Loading**
   ```python
   # Use COPY for fast bulk inserts
   with conn.cursor() as cur:
       with cur.copy("COPY documents (content, embedding) FROM STDIN") as copy:
           for doc, embedding in documents:
               copy.write_row([doc, embedding])
   ```

2. **Half-Precision Vectors**
   ```sql
   -- Reduce memory by 50% with minimal accuracy loss
   ALTER TABLE documents ADD COLUMN embedding_half halfvec(1536);
   UPDATE documents SET embedding_half = embedding::halfvec;
   CREATE INDEX idx_half ON documents USING hnsw (embedding_half vector_l2_ops);
   ```

3. **Distance Metric Selection**
   - **Cosine**: Best for normalized embeddings (OpenAI, Sentence Transformers)
   - **L2**: General purpose
   - **Inner Product**: When vectors are unit normalized

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "vector type does not exist" | Run `CREATE EXTENSION vector` |
| "vector dimension mismatch" | Ensure consistent embedding size |
| "index too large" | Use IVFFlat or half-precision vectors |
| "slow queries" | Create appropriate indexes |
| "memory exhaustion" | Use half vectors or binary quantization |

## References

- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [Python Library Documentation](https://github.com/pgvector/pgvector-python)
- [Django Integration](https://github.com/pgvector/pgvector-python#django)
- [Performance Benchmarks](https://github.com/pgvector/pgvector#performance)
