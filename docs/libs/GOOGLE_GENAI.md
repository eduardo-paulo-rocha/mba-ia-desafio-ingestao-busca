# Google Generative AI SDK

## Overview

**Version:** Latest (typically 0.14+)  
**Type:** Google Generative AI API Client Library  
**Repository:** https://github.com/googleapis/python-genai  
**Documentation:** https://ai.google.dev/

The Google Generative AI Python SDK provides access to Google's Gemini models and other generative AI capabilities. It supports text generation, multimodal input, function calling, embeddings, streaming, and batch processing with a Python-first design.

## Key Features

### 1. Text Generation with Gemini
- Gemini 1.5 Pro and Flash models
- Streaming responses
- Function calling
- JSON mode and structured outputs
- Caching for reduced latency

### 2. Multimodal Input
- Image analysis and understanding
- Video analysis
- Mixed text and image inputs
- Audio input support

### 3. Embeddings API
- Text embedding generation
- Batch embedding support
- Configurable embedding models

### 4. Caching (Context Caching)
- Reduce costs on repeated requests
- Faster response times

### 5. Batch Processing
- Process multiple requests efficiently
- Cost-effective large-scale operations

## Installation

```bash
# Basic installation
pip install google-generativeai

# Latest version
pip install --upgrade google-generativeai
```

## Basic Usage

### 1. Simple Text Generation

```python
import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-pro")

response = model.generate_content(
    "Explain machine learning in simple terms"
)

print(response.text)
```

### 2. Streaming Responses

```python
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-pro")

stream = model.generate_content(
    "Write a creative short story about AI",
    stream=True
)

for chunk in stream:
    print(chunk.text, end="", flush=True)

print()
```

### 3. Chat with Conversation History

```python
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-pro")

chat = model.start_chat(history=[])

# Multi-turn conversation
messages = [
    "What is machine learning?",
    "Can you explain neural networks?",
    "How does backpropagation work?"
]

for msg in messages:
    print(f"User: {msg}")
    response = chat.send_message(msg)
    print(f"Assistant: {response.text}\n")
```

### 4. Vision - Image Analysis

```python
import google.generativeai as genai
from PIL import Image
import os

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-pro")

# Load image
image = Image.open("path/to/image.jpg")

response = model.generate_content([
    "What's in this image? Please describe in detail.",
    image
])

print(response.text)

# Image from URL
response = model.generate_content([
    "Analyze this image:",
    "https://example.com/image.jpg"
])

print(response.text)
```

### 5. Multimodal Input (Text + Image + Text)

```python
import google.generativeai as genai
from PIL import Image

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-pro")

image = Image.open("document.jpg")

response = model.generate_content([
    "I have an image of a document. ",
    image,
    " Please extract and summarize the key information."
])

print(response.text)
```

### 6. Function Calling

```python
import google.generativeai as genai
import json

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

tools = [
    {
        "function_declarations": [
            {
                "name": "get_weather",
                "description": "Get weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Location name"
                        }
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "get_stock_price",
                "description": "Get stock price",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock ticker"
                        }
                    },
                    "required": ["symbol"]
                }
            }
        ]
    }
]

model = genai.GenerativeModel(
    "gemini-1.5-pro",
    tools=tools
)

chat = model.start_chat()

response = chat.send_message(
    "What's the weather in NYC and Apple stock price?"
)

# Process function calls
while True:
    if response.parts[-1].function_call:
        calls = response.parts[-1].function_call
        
        # Implement your functions
        def get_weather(location):
            return f"Weather in {location}: Sunny, 72°F"
        
        def get_stock_price(symbol):
            return f"Stock: {symbol} = $150"
        
        results = []
        for call in calls.parts:
            if call.function_call.name == "get_weather":
                result = get_weather(
                    call.function_call.args["location"]
                )
            elif call.function_call.name == "get_stock_price":
                result = get_stock_price(
                    call.function_call.args["symbol"]
                )
            
            results.append({
                "function_call": call.function_call,
                "result": result
            })
        
        # Send results back
        response = chat.send_message(results)
    else:
        print(response.text)
        break
```

### 7. JSON Mode and Structured Output

```python
import google.generativeai as genai
from typing import Optional

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-pro")

# Define schema
schema = {
    "type": "OBJECT",
    "properties": {
        "title": {"type": "STRING"},
        "author": {"type": "STRING"},
        "summary": {"type": "STRING"},
        "key_points": {
            "type": "ARRAY",
            "items": {"type": "STRING"}
        },
        "sentiment": {
            "type": "ENUM",
            "enum": ["positive", "negative", "neutral"]
        }
    }
}

response = model.generate_content(
    "Analyze this document and extract structured information.",
    generation_config=genai.types.GenerationConfig(
        response_mime_type="application/json",
        response_schema=schema
    )
)

import json
structured_data = json.loads(response.text)
print(structured_data)
```

## Embeddings API

### 1. Generate Text Embeddings

```python
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Single embedding
result = genai.embed_content(
    model="models/embedding-001",
    content="The quick brown fox jumps over the lazy dog"
)

embedding = result['embedding']
print(f"Embedding dimension: {len(embedding)}")

# Batch embeddings
texts = [
    "Document 1 content",
    "Document 2 content",
    "Document 3 content"
]

batch_result = genai.embed_content(
    model="models/embedding-001",
    content=texts
)

print(f"Generated {len(batch_result['embeddings'])} embeddings")
```

### 2. Embedding with Title (for documents)

```python
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

result = genai.embed_content(
    model="models/embedding-001",
    content={
        "parts": [
            {
                "text": "This is the document content..."
            }
        ]
    }
)

embedding = result['embedding']
```

## Batch Processing

```python
import google.generativeai as genai
import json
import time

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Prepare batch requests
requests = []

texts = [
    "Document 1 content",
    "Document 2 content",
    "Document 3 content"
]

for i, text in enumerate(texts):
    requests.append({
        "custom_id": f"doc-{i}",
        "generation_config": {
            "candidate_count": 1
        },
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": f"Summarize: {text}"}
                ]
            }
        ]
    })

# Create batch file
batch_content = "\n".join(json.dumps(req) for req in requests)

with open("batch_requests.jsonl", "w") as f:
    f.write(batch_content)

# Upload and process
with open("batch_requests.jsonl", "rb") as f:
    batch_file = genai.upload_file(f)

print(f"Batch file ID: {batch_file.name}")

# Note: Batch API may have different availability
# Check current API capabilities
```

## Caching (Context Caching)

```python
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Prepare cached content (reduce costs on repeated usage)
with open("large_document.txt", "r") as f:
    document_content = f.read()

model = genai.GenerativeModel("gemini-1.5-pro")

# First request - creates cache
response1 = model.generate_content(
    [
        {
            "text": document_content,
            "cache_control": {"type": "ephemeral"}
        },
        "Summarize the key points"
    ]
)

print("First response (cache created):")
print(response1.text)

# Second request - uses cache (30-50% cost reduction)
response2 = model.generate_content(
    [
        {
            "text": document_content,
            "cache_control": {"type": "ephemeral"}
        },
        "What are the main themes?"
    ]
)

print("Second response (cache used):")
print(response2.text)

# Check cache usage in metadata
print(f"\nUsage: {response2.usage_metadata}")
```

## Integration with RAG Project

### In `src/ingest.py` - Generate Embeddings

```python
import google.generativeai as genai
import psycopg
from pgvector.psycopg import register_vector
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

def ingest_pdf_with_gemini(pdf_path: str):
    # Initialize Gemini
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    
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
    
    # Generate embeddings using Gemini
    print(f"Generating embeddings for {len(chunks)} chunks...")
    
    with conn.cursor() as cur:
        with cur.copy(
            "COPY pdf_chunks (filename, chunk_number, content, embedding) FROM STDIN"
        ) as copy:
            for i, chunk in enumerate(chunks):
                # Generate embedding using Gemini
                result = genai.embed_content(
                    model="models/embedding-001",
                    content=chunk.page_content
                )
                embedding = result['embedding']
                
                copy.write_row([
                    os.path.basename(pdf_path),
                    i,
                    chunk.page_content,
                    embedding
                ])
                
                if (i + 1) % 10 == 0:
                    print(f"Processed {i + 1}/{len(chunks)} chunks")
    
    print(f"✓ Ingested {len(chunks)} chunks into vector database")
```

### In `src/search.py` - Generate Responses with Gemini

```python
import google.generativeai as genai
import psycopg
from pgvector.psycopg import register_vector
import os

def search_prompt(question: str):
    # Initialize Gemini
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-pro")
    
    # Generate query embedding
    query_result = genai.embed_content(
        model="models/embedding-001",
        content=question
    )
    query_embedding = query_result['embedding']
    
    # Connect to database and retrieve context
    conn = psycopg.connect(os.getenv("DATABASE_URL"))
    register_vector(conn)
    
    with conn.cursor() as cur:
        # Vector similarity search
        cur.execute("""
            SELECT content, embedding <=> %s AS distance
            FROM pdf_chunks
            WHERE (embedding <=> %s) < 0.8
            ORDER BY distance
            LIMIT 5
        """, (query_embedding, query_embedding))
        
        results = cur.fetchall()
        context = "\n\n".join([row[0] for row in results])
    
    conn.close()
    
    # Generate response using Gemini
    response = model.generate_content(
        f"""Based on the following context, answer the user's question.
        If the answer is not in the context, reply: "Não tenho informações necessárias para responder sua pergunta."
        
        Context:
        {context}
        
        Question: {question}
        
        Answer based only on the context above:"""
    )
    
    return response.text

# Chat interface
def main():
    print("Chat with your documents using Gemini (type 'quit' to exit)")
    while True:
        question = input("\nYou: ").strip()
        if question.lower() == 'quit':
            break
        
        answer = search_prompt(question)
        print(f"\nAssistant: {answer}")

if __name__ == "__main__":
    main()
```

### In `src/chat.py` - Multi-turn Conversation

```python
import google.generativeai as genai
from search import search_prompt
import os

class GeminiDocumentChat:
    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel("gemini-1.5-pro")
        self.chat = self.model.start_chat(history=[])
    
    def chat_message(self, user_message: str) -> str:
        # Get context from RAG pipeline
        context = search_prompt(user_message)
        
        # Create enhanced prompt
        enhanced_prompt = f"""Based on this context, answer the user's question:

Context:
{context}

Question: {user_message}

Answer:"""
        
        # Send to Gemini with full context
        response = self.chat.send_message(enhanced_prompt)
        
        return response.text
    
    def clear_history(self):
        self.chat = self.model.start_chat(history=[])

def main():
    chat = GeminiDocumentChat()
    
    print("Document Q&A with Gemini (type 'quit' to exit)")
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'quit':
            break
        elif not user_input:
            continue
        
        response = chat.chat_message(user_input)
        print(f"\nAssistant: {response}")

if __name__ == "__main__":
    main()
```

## Error Handling

```python
import google.generativeai as genai
from google.api_core import exceptions
import time

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def robust_generate(prompt, max_retries=3):
    model = genai.GenerativeModel("gemini-1.5-pro")
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response
        
        except exceptions.ResourceExhausted:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
        
        except exceptions.DeadlineExceeded:
            print("Request timeout")
            raise
        
        except exceptions.GoogleAPICallError as e:
            print(f"API error: {e}")
            raise

# Usage
try:
    response = robust_generate("Your prompt here")
    print(response.text)
except Exception as e:
    print(f"Failed: {e}")
```

## Configuration

```python
import google.generativeai as genai
import os

# Set API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Check available models
for model in genai.list_models():
    print(f"Model: {model.name}, Supported: {model.supported_generation_methods}")

# Generation configuration
generation_config = genai.types.GenerationConfig(
    temperature=0.7,
    top_p=0.95,
    top_k=40,
    max_output_tokens=2048,
    candidate_count=1
)

model = genai.GenerativeModel(
    "gemini-1.5-pro",
    generation_config=generation_config
)
```

## Available Models

| Model | Capabilities | Use Case |
|-------|-------------|----------|
| gemini-1.5-pro | Text, vision, function calling | Complex tasks, reasoning |
| gemini-1.5-flash | Fast, efficient | Quick responses, embeddings |
| gemini-1.0-pro | Text generation | Legacy, general text |
| embedding-001 | Text embeddings | Semantic search, RAG |

## References

- [Google AI Studio](https://aistudio.google.com/)
- [Gemini API Documentation](https://ai.google.dev/)
- [Python SDK GitHub](https://github.com/googleapis/python-genai)
- [API Pricing](https://ai.google.dev/pricing)
- [Model Card for Gemini](https://ai.google.dev/gemini-api/docs/models/gemini)
