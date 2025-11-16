# Psycopg 3

## Overview

**Version:** 3.2.9  
**Type:** PostgreSQL Adapter  
**Repository:** https://github.com/psycopg/psycopg  
**Documentation:** https://www.psycopg.org/psycopg3/

Psycopg is the most popular PostgreSQL database adapter for Python. Version 3 is a modern reimplementation that provides both synchronous and asynchronous interfaces, with emphasis on safety, robustness, and compatibility with the DB-API 2.0 specification.

## Key Features

### 1. Connection Management
- Context managers for automatic cleanup
- Connection pooling support
- Async/await syntax
- Transaction management

### 2. Data Type Support
- JSON/JSONB types
- Arrays and ranges
- UUIDs
- Custom types
- Vector types (via pgvector integration)

### 3. Advanced Features
- Pipeline mode for batching commands
- Server-side cursors for large datasets
- COPY operations for bulk loading
- Prepared statements
- Row factories for flexible result formats

## Installation

```bash
# Basic installation
pip install psycopg==3.2.9

# With binary acceleration
pip install psycopg[binary]==3.2.9

# With connection pooling
pip install psycopg[pool]==3.2.9

# All extras
pip install psycopg[all]==3.2.9
```

## Architecture

### Connection Layers

```
Application Code
    ↓
Psycopg Client API (sync/async)
    ↓
Protocol Layer (text/binary)
    ↓
libpq (PostgreSQL client library)
    ↓
Network
    ↓
PostgreSQL Server
```

## Usage Examples

### 1. Basic Connection and Query

```python
import psycopg

# Context manager for automatic cleanup
with psycopg.connect("dbname=mydb user=postgres") as conn:
    with conn.cursor() as cur:
        # Create table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                title TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Insert data
        cur.execute(
            "INSERT INTO documents (title, content) VALUES (%s, %s)",
            ("Title 1", "Content 1")
        )
        
        # Fetch results
        cur.execute("SELECT * FROM documents WHERE id = %s", (1,))
        row = cur.fetchone()
        print(row)
        
        conn.commit()
```

### 2. Parameterized Queries (SQL Injection Prevention)

```python
import psycopg

with psycopg.connect("dbname=mydb") as conn:
    with conn.cursor() as cur:
        # Safe: Parameters are properly escaped
        user_input = "O'Brien"
        cur.execute(
            "INSERT INTO users (name) VALUES (%s)",
            (user_input,)
        )
        
        # Batch operations
        data = [
            ("Alice", 30),
            ("Bob", 25),
            ("Charlie", 35)
        ]
        cur.executemany(
            "INSERT INTO users (name, age) VALUES (%s, %s)",
            data
        )
        
        conn.commit()
```

### 3. Row Factories

```python
import psycopg
from psycopg.rows import dict_row, namedtuple_row, class_row
from dataclasses import dataclass

with psycopg.connect("dbname=mydb") as conn:
    # Dictionary rows
    cur = conn.cursor(row_factory=dict_row)
    cur.execute("SELECT id, title FROM documents LIMIT 1")
    row = cur.fetchone()
    print(row['title'])
    
    # Named tuple rows
    cur = conn.cursor(row_factory=namedtuple_row)
    cur.execute("SELECT id, title FROM documents LIMIT 1")
    row = cur.fetchone()
    print(row.title)
    
    # Custom class rows
    @dataclass
    class Document:
        id: int
        title: str
    
    cur = conn.cursor(row_factory=class_row(Document))
    cur.execute("SELECT id, title FROM documents LIMIT 1")
    doc = cur.fetchone()
    print(f"Document: {doc.title}")
```

### 4. Async Operations

```python
import asyncio
import psycopg

async def async_database_operations():
    # Async connection
    async with await psycopg.AsyncConnection.connect("dbname=mydb") as aconn:
        async with aconn.cursor() as acur:
            # Async query
            await acur.execute("SELECT COUNT(*) FROM documents")
            count = await acur.fetchone()
            print(f"Total documents: {count[0]}")
            
            # Async transaction
            async with aconn.transaction():
                await acur.execute("INSERT INTO documents (title) VALUES (%s)", ("New doc",))
            
            await aconn.commit()

# Run async operation
asyncio.run(async_database_operations())
```

### 5. COPY Operations (Bulk Loading)

```python
import psycopg
import csv

# Bulk insert using COPY (10-100x faster)
with psycopg.connect("dbname=mydb") as conn:
    with conn.cursor() as cur:
        # COPY FROM stdin
        with cur.copy("COPY documents (title, content) FROM STDIN") as copy:
            copy.write_row(["Title 1", "Content 1"])
            copy.write_row(["Title 2", "Content 2"])
        
        # COPY from file
        with open("data.csv") as f:
            with cur.copy("COPY documents (title, content) FROM STDIN") as copy:
                for row in csv.reader(f):
                    copy.write_row(row)
        
        conn.commit()
```

### 6. JSON Support

```python
import psycopg
from psycopg.types.json import Json

with psycopg.connect("dbname=mydb") as conn:
    cur = conn.cursor()
    
    # Insert JSON data
    metadata = {"author": "John", "tags": ["AI", "ML"]}
    cur.execute(
        "INSERT INTO documents (title, metadata) VALUES (%s, %s)",
        ("Document", Json(metadata))
    )
    
    # Query JSON
    cur.execute(
        "SELECT metadata->>'author' AS author FROM documents WHERE id = %s",
        (1,)
    )
    author = cur.fetchone()[0]
    print(f"Author: {author}")
    
    conn.commit()
```

### 7. Vector Support with pgvector

```python
import psycopg
from pgvector.psycopg import register_vector
import numpy as np

# Register vector type
conn = psycopg.connect("dbname=mydb", autocommit=True)
conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
register_vector(conn)

# Use vectors
with psycopg.connect("dbname=mydb") as conn:
    with conn.cursor() as cur:
        # Create table with vector column
        cur.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                id SERIAL PRIMARY KEY,
                content TEXT,
                embedding vector(1536)
            )
        """)
        
        # Insert vector
        embedding = np.random.rand(1536).astype(np.float32)
        cur.execute(
            "INSERT INTO embeddings (content, embedding) VALUES (%s, %s)",
            ("Document content", embedding)
        )
        
        # Similarity search
        query_embedding = np.random.rand(1536).astype(np.float32)
        cur.execute(
            "SELECT id, content FROM embeddings ORDER BY embedding <-> %s LIMIT 5",
            (query_embedding,)
        )
        
        conn.commit()
```

## Integration with RAG Project

### In `src/ingest.py`

```python
import psycopg
from pgvector.psycopg import register_vector
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import os

def ingest_pdf(pdf_path: str):
    # Load and split PDF
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(docs)
    
    # Connect to database
    conn = psycopg.connect(os.getenv("DATABASE_URL"), autocommit=True)
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    register_vector(conn)
    
    # Create table
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pdf_chunks (
                id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
                filename TEXT,
                chunk_number INT,
                content TEXT,
                embedding vector(1536),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
    
    # Generate embeddings and store
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    with conn.cursor() as cur:
        with cur.copy(
            "COPY pdf_chunks (filename, chunk_number, content, embedding) FROM STDIN"
        ) as copy:
            for i, chunk in enumerate(chunks):
                embedding = embeddings.embed_query(chunk.page_content)
                copy.write_row([
                    os.path.basename(pdf_path),
                    i,
                    chunk.page_content,
                    embedding
                ])
    
    # Create index
    with conn.cursor() as cur:
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_embedding 
            ON pdf_chunks USING hnsw (embedding vector_cosine_ops)
        """)
    
    conn.close()
    print(f"Ingested {len(chunks)} chunks")
```

### In `src/search.py`

```python
import psycopg
from pgvector.psycopg import register_vector
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
import os

def search_prompt(question: str):
    # Connect to database
    conn = psycopg.connect(os.getenv("DATABASE_URL"))
    register_vector(conn)
    
    # Generate query embedding
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    query_embedding = embeddings.embed_query(question)
    
    # Retrieve relevant chunks
    with conn.cursor() as cur:
        cur.execute("""
            SELECT content, embedding <=> %s AS distance
            FROM pdf_chunks
            ORDER BY distance
            LIMIT 5
        """, (query_embedding,))
        
        results = cur.fetchall()
        context = "\n\n".join([row[0] for row in results])
    
    conn.close()
    
    # Generate response using LLM
    llm = ChatOpenAI(model="gpt-4")
    
    prompt = f"""
    Based on the following context, answer the user's question.
    If the answer is not in the context, say "Não tenho informações necessárias para responder sua pergunta."
    
    Context:
    {context}
    
    Question: {question}
    
    Answer:
    """
    
    from langchain_core.messages import HumanMessage
    response = llm.invoke([HumanMessage(content=prompt)])
    
    return response.content
```

## Connection Pooling

```python
from psycopg_pool import ConnectionPool

# Create pool
pool = ConnectionPool(
    "dbname=mydb user=postgres",
    min_size=5,
    max_size=20,
    timeout=5.0
)

# Use connections from pool
with pool.connection() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM documents")
        count = cur.fetchone()[0]
        print(f"Total: {count}")

# Async pool
from psycopg_pool import AsyncConnectionPool
import asyncio

async def use_async_pool():
    pool = AsyncConnectionPool(
        "dbname=mydb",
        min_size=5,
        max_size=20
    )
    
    await pool.wait()
    
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT COUNT(*) FROM documents")
            count = await cur.fetchone()
    
    await pool.close()

asyncio.run(use_async_pool())
```

## Error Handling

```python
import psycopg
from psycopg import errors

try:
    with psycopg.connect("dbname=mydb") as conn:
        conn.execute("INSERT INTO documents (title) VALUES (%s)", ("Title",))
except errors.UniqueViolation:
    print("Duplicate key error")
except errors.IntegrityError:
    print("Integrity constraint violated")
except errors.OperationalError:
    print("Connection or operational error")
except psycopg.Error as e:
    print(f"Database error: {e}")
```

## Performance Tips

1. **Use COPY for bulk operations** (100x+ faster than INSERT)
2. **Use connection pooling** for concurrent applications
3. **Use prepared statements** for repeated queries
4. **Use server-side cursors** for large result sets
5. **Create appropriate indexes** on frequently queried columns

## Configuration

```python
# Connection parameters
conn = psycopg.connect(
    dbname="mydb",
    user="postgres",
    password="password",
    host="localhost",
    port=5432,
    connect_timeout=10,
    autocommit=False
)

# Connection string
conn = psycopg.connect(
    "postgresql://user:password@localhost:5432/dbname"
)
```

## References

- [Psycopg Documentation](https://www.psycopg.org/psycopg3/)
- [GitHub Repository](https://github.com/psycopg/psycopg)
- [API Reference](https://www.psycopg.org/psycopg3/api/index.html)
- [Migration from Psycopg2](https://www.psycopg.org/psycopg3/docs/basic/from_psycopg2.html)
