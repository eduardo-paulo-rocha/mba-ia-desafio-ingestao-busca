# LangChain Framework

## Overview

**Version:** 0.3.27  
**Type:** AI Framework  
**Repository:** https://github.com/langchain-ai/langchain  
**Documentation:** https://docs.langchain.com

LangChain is a comprehensive framework for developing applications powered by large language models (LLMs). It simplifies every stage of the LLM application lifecycle with open-source components and third-party integrations. The framework is designed to overcome LLM limitations by integrating them with external data sources and computational tools, especially through Retrieval-Augmented Generation (RAG).

## Key Components

### 1. Core Modules
- **LangChain Core**: Foundational abstractions for building LLM applications
- **LangChain Community**: Community-maintained integrations with various providers
- **LangChain Text Splitters**: Document chunking and splitting utilities

### 2. LLM Integrations
- OpenAI (ChatGPT, GPT-4)
- Anthropic (Claude)
- Google Generative AI (Gemini)
- Azure OpenAI

### 3. Vector Stores & RAG
- Integration with pgvector for PostgreSQL
- Support for semantic search
- Document retrieval and augmentation

### 4. Agents & Chains
- Create autonomous agents with LLM reasoning
- Chain multiple operations together
- Tool calling and function integration

## Installation

```bash
# Basic installation
pip install langchain==0.3.27

# With OpenAI support
pip install "langchain[openai]"

# With Google GenAI support
pip install "langchain[google-genai]"

# With all integrations (not recommended)
pip install langchain-community
```

## Usage Examples

### Basic Chat Completion

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# Initialize LLM
model = ChatOpenAI(model="gpt-4", temperature=0.7)

# Create and send message
response = model.invoke([HumanMessage(content="What is machine learning?")])
print(response.content)
```

### Chat with History

```python
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI

# Create conversational chain
llm = ChatOpenAI(model="gpt-4")
memory = ConversationBufferMemory()

# Multi-turn conversation
messages = [{"role": "user", "content": "Hello"}]
response = llm.invoke(messages)
```

### Vector Store with Embeddings

```python
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVectorStore

# Create embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Initialize vector store (with pgvector)
vector_store = PGVectorStore(
    embeddings=embeddings,
    collection_name="documents",
    connection="postgresql+psycopg://user:pass@localhost/dbname"
)

# Add documents
docs = [{"content": "Document 1", "metadata": {...}}]
vector_store.add_documents(docs)

# Similarity search
results = vector_store.similarity_search("query text", k=5)
```

### RAG Pipeline

```python
from langchain.chains import RetrievalQA
from langchain_postgres import PGVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Setup
embeddings = OpenAIEmbeddings()
vector_store = PGVectorStore(
    embeddings=embeddings,
    collection_name="docs",
    connection="postgresql+psycopg://..."
)

# Create QA chain
llm = ChatOpenAI(model="gpt-4")
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_store.as_retriever()
)

# Query
result = qa_chain({"query": "What is in the documents?"})
```

### Document Processing

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

# Load PDF
loader = PyPDFLoader("document.pdf")
docs = loader.load()

# Split into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = splitter.split_documents(docs)
```

## Integration with This Project

In this RAG project, LangChain is used for:

1. **Data Ingestion (`src/ingest.py`)**
   - Loading and processing PDF files
   - Chunking documents into manageable pieces
   - Converting chunks to embeddings

2. **Vector Storage**
   - Storing embeddings in PostgreSQL with pgvector
   - Managing document metadata
   - Efficient similarity search

3. **Retrieval & Generation (`src/search.py`)**
   - Implementing RAG pipeline
   - Retrieving relevant context
   - Generating responses with LLM

4. **Chat Interface (`src/chat.py`)**
   - Managing conversation flow
   - Handling multi-turn interactions
   - Maintaining conversation history

## Best Practices

### 1. Environment Management
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
```

### 2. Error Handling
```python
try:
    response = chain.invoke({"query": "question"})
except Exception as e:
    print(f"Error: {e}")
    # Fallback or retry logic
```

### 3. Memory Management
- Use streaming for large document processing
- Implement pagination for large result sets
- Clear memory after conversation completion

### 4. Caching
```python
from langchain.cache import InMemoryCache
import langchain
langchain.llm_cache = InMemoryCache()
```

## Configuration for RAG Project

### Key Environment Variables
```bash
# LLM Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# Alternative: Google Gemini
GOOGLE_API_KEY=...

# Database Configuration (PostgreSQL + pgvector)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rag
DB_USER=langchain
DB_PASSWORD=password

# Application
PDF_PATH=./data/pdfs
LOG_LEVEL=INFO
```

## Performance Optimization

1. **Batch Processing**: Process multiple documents in batches
2. **Caching**: Cache embeddings and frequent queries
3. **Indexing**: Create indexes on vector columns
4. **Async Operations**: Use async chains for I/O bound operations

## Troubleshooting

### Common Issues

1. **Connection Errors to PostgreSQL**
   - Verify connection string format
   - Check database credentials
   - Ensure pgvector extension is installed

2. **Embedding Dimension Mismatch**
   - Ensure consistent embedding model
   - Match vector dimensions with database schema

3. **Memory Issues with Large PDFs**
   - Use streaming or chunking
   - Process documents in smaller batches

## References

- [LangChain Documentation](https://docs.langchain.com)
- [LangChain GitHub Repository](https://github.com/langchain-ai/langchain)
- [RAG Implementation Guide](https://docs.langchain.com/en/latest/modules/indexes/document_loaders.html)
- [API Reference](https://api.python.langchain.com/)

## Dependencies

This library depends on:
- `langchain-core` (0.3.74)
- `langchain-community` (0.3.27)
- `langchain-text-splitters` (0.3.9)
- `langchain-openai` (0.3.30) - for OpenAI integration
- `langchain-google-genai` (2.1.9) - for Google AI integration
- `langchain-postgres` (0.0.15) - for PostgreSQL/pgvector

## Related Libraries in Project

- **langchain-postgres**: PostgreSQL and pgvector backend
- **langchain-openai**: OpenAI model integration
- **langchain-google-genai**: Google Gemini integration
- **psycopg**: PostgreSQL adapter
- **pgvector**: Vector similarity search
