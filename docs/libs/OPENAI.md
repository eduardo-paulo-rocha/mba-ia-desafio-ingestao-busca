# OpenAI SDK

## Overview

**Version:** 1.102.0  
**Type:** OpenAI API Client Library  
**Repository:** https://github.com/openai/openai-python  
**Documentation:** https://platform.openai.com/docs/api-reference

The OpenAI Python SDK provides a simple and intuitive interface for interacting with OpenAI's language models, embeddings, and other APIs. It includes support for streaming, async operations, file uploads, and advanced features like batch processing and vision capabilities.

## Key Features

### 1. Chat Completions API
- GPT-4, GPT-4 Turbo, GPT-3.5 Turbo models
- Streaming responses
- Function calling
- Vision capabilities (image analysis)
- JSON mode

### 2. Embeddings API
- Text embedding models (text-embedding-3-small, text-embedding-3-large)
- Batch processing
- Dimension specification

### 3. Audio API
- Speech-to-text (Whisper)
- Text-to-speech
- Streaming audio

### 4. Image Generation
- DALL-E 3 text-to-image
- Image editing and variations

### 5. File Management
- Upload and manage files
- Batch operations

## Installation

```bash
# Basic installation
pip install openai==1.102.0

# With async support
pip install openai[async]==1.102.0
```

## Basic Usage

### 1. Simple Chat Completion

```python
from openai import OpenAI

client = OpenAI(api_key="your-api-key")

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello! What can you help me with?"}
    ],
    temperature=0.7,
    max_tokens=150
)

print(response.choices[0].message.content)
```

### 2. Streaming Responses

```python
from openai import OpenAI

client = OpenAI()

stream = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Write a short poem about AI"}
    ],
    stream=True
)

# Stream tokens as they arrive
for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="", flush=True)

print()  # Newline at end
```

### 3. Chat with Conversation History

```python
from openai import OpenAI

client = OpenAI()

messages = [
    {"role": "system", "content": "You are a helpful assistant."}
]

def chat(user_message):
    messages.append({"role": "user", "content": user_message})
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7
    )
    
    assistant_message = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_message})
    
    return assistant_message

# Multi-turn conversation
print(chat("What is machine learning?"))
print(chat("Can you explain neural networks?"))
print(chat("How does backpropagation work?"))
```

### 4. Function Calling

```python
from openai import OpenAI
import json

client = OpenAI()

def get_weather(location):
    # Mock weather API
    return f"The weather in {location} is sunny, 72°F"

def get_stock_price(symbol):
    # Mock stock API
    return f"Stock price for {symbol} is $150"

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The location"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Get stock price for a symbol",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    }
                },
                "required": ["symbol"]
            }
        }
    }
]

messages = [
    {"role": "user", "content": "What's the weather in New York and the stock price for AAPL?"}
]

response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

# Process tool calls
while response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        if tool_call.function.name == "get_weather":
            args = json.loads(tool_call.function.arguments)
            result = get_weather(args["location"])
        elif tool_call.function.name == "get_stock_price":
            args = json.loads(tool_call.function.arguments)
            result = get_stock_price(args["symbol"])
        
        messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": response.choices[0].message.tool_calls
        })
        
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result
        })
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=tools
    )

print(response.choices[0].message.content)
```

### 5. Vision Capabilities

```python
from openai import OpenAI
import base64

client = OpenAI()

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Local image
image_data = encode_image("path/to/image.jpg")
response = client.chat.completions.create(
    model="gpt-4-vision-preview",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}"
                    }
                }
            ]
        }
    ]
)

print(response.choices[0].message.content)

# Image from URL
response = client.chat.completions.create(
    model="gpt-4-vision-preview",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Analyze this image"},
                {
                    "type": "image_url",
                    "image_url": {"url": "https://example.com/image.jpg"}
                }
            ]
        }
    ]
)
```

## Embeddings API

### 1. Generate Text Embeddings

```python
from openai import OpenAI

client = OpenAI()

# Single embedding
response = client.embeddings.create(
    model="text-embedding-3-small",  # 1536 dimensions
    input="The quick brown fox jumps over the lazy dog"
)

embedding = response.data[0].embedding
print(f"Embedding dimension: {len(embedding)}")

# Batch embeddings
texts = [
    "Document 1 content",
    "Document 2 content",
    "Document 3 content"
]

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=texts
)

embeddings = [item.embedding for item in response.data]
print(f"Generated {len(embeddings)} embeddings")
```

### 2. Custom Embedding Dimensions

```python
from openai import OpenAI

client = OpenAI()

# Reduce dimensions (saves cost, maintains semantic meaning)
response = client.embeddings.create(
    model="text-embedding-3-large",
    input="Your text here",
    dimensions=256  # Instead of 3072
)

embedding = response.data[0].embedding
print(f"Reduced embedding dimension: {len(embedding)}")
```

## Audio API

### 1. Speech-to-Text (Whisper)

```python
from openai import OpenAI

client = OpenAI()

# Transcribe audio
with open("audio.mp3", "rb") as audio_file:
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="en"
    )

print(transcript.text)

# Translate audio to English
with open("audio.mp3", "rb") as audio_file:
    translation = client.audio.translations.create(
        model="whisper-1",
        file=audio_file
    )

print(translation.text)
```

### 2. Text-to-Speech

```python
from openai import OpenAI

client = OpenAI()

response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",  # nova, onyx, echo, shimmer
    input="The quick brown fox jumps over the lazy dog"
)

# Save audio to file
with open("output.mp3", "wb") as f:
    f.write(response.content)

# Streaming audio
response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="Your text here",
    stream=True
)

with open("output_stream.mp3", "wb") as f:
    for chunk in response.iter_bytes():
        f.write(chunk)
```

## Integration with RAG Project

### In `src/ingest.py` - Generate Embeddings

```python
from openai import OpenAI
import psycopg
from pgvector.psycopg import register_vector
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

def ingest_pdf(pdf_path: str):
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
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
    
    # Generate embeddings
    print(f"Generating embeddings for {len(chunks)} chunks...")
    
    with conn.cursor() as cur:
        with cur.copy(
            "COPY pdf_chunks (filename, chunk_number, content, embedding) FROM STDIN"
        ) as copy:
            for i, chunk in enumerate(chunks):
                # Generate embedding using OpenAI
                response = client.embeddings.create(
                    model="text-embedding-3-small",
                    input=chunk.page_content
                )
                embedding = response.data[0].embedding
                
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

### In `src/search.py` - Generate Responses

```python
from openai import OpenAI
import psycopg
from pgvector.psycopg import register_vector
import os

def search_prompt(question: str):
    # Initialize clients
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Generate query embedding
    query_response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    )
    query_embedding = query_response.data[0].embedding
    
    # Connect to database and retrieve relevant context
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
    
    # Generate response using LLM
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": """You are a helpful assistant that answers questions 
                based only on the provided context. If the answer is not in the context, 
                reply: "Não tenho informações necessárias para responder sua pergunta."
                """
            },
            {
                "role": "user",
                "content": f"""Context:
                {context}
                
                Question: {question}
                
                Answer based only on the context above:"""
            }
        ],
        temperature=0.7,
        max_tokens=500
    )
    
    return response.choices[0].message.content

# Chat interface
def main():
    print("Chat with your documents (type 'quit' to exit)")
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
from openai import OpenAI
from search import search_prompt
import os

class DocumentChat:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.conversation_history = [
            {
                "role": "system",
                "content": """You are a helpful assistant that answers questions 
                based on provided document context. Always cite sources when possible."""
            }
        ]
    
    def chat(self, user_message: str) -> str:
        # Get context from RAG pipeline
        context = search_prompt(user_message)
        
        # Add context to message
        enhanced_message = f"{context}\n\nUser Question: {user_message}"
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": enhanced_message
        })
        
        # Get response
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=self.conversation_history,
            temperature=0.7,
            max_tokens=500
        )
        
        assistant_message = response.choices[0].message.content
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message
    
    def clear_history(self):
        self.conversation_history = self.conversation_history[:1]  # Keep system message

def main():
    chat = DocumentChat()
    
    print("Document Q&A Chat (type 'quit' to exit, 'clear' to clear history)")
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'quit':
            break
        elif user_input.lower() == 'clear':
            chat.clear_history()
            print("Conversation history cleared.")
            continue
        elif not user_input:
            continue
        
        response = chat.chat(user_input)
        print(f"\nAssistant: {response}")

if __name__ == "__main__":
    main()
```

## Error Handling

```python
from openai import OpenAI, RateLimitError, APIConnectionError, APIStatusError
import time

client = OpenAI()

def robust_api_call(max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "Hello"}],
                max_retries=2
            )
            return response
        
        except RateLimitError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
        
        except APIConnectionError as e:
            print(f"Connection error: {e}")
            raise
        
        except APIStatusError as e:
            print(f"API error {e.status_code}: {e.message}")
            raise

# Usage
try:
    response = robust_api_call()
except Exception as e:
    print(f"Failed after retries: {e}")
```

## Batch Processing API

```python
from openai import OpenAI
import json
import time

client = OpenAI()

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
        "params": {
            "model": "text-embedding-3-small",
            "input": text
        }
    })

# Create batch file
batch_content = "\n".join(json.dumps(req) for req in requests)

with open("batch_requests.jsonl", "w") as f:
    f.write(batch_content)

# Upload batch
with open("batch_requests.jsonl", "rb") as f:
    batch_input_file = client.files.create(
        file=f,
        purpose="batch"
    ).id

# Create batch job
batch_job = client.batches.create(
    input_file_id=batch_input_file,
    endpoint="/v1/embeddings",
    completion_window="24h"
)

print(f"Batch ID: {batch_job.id}")
print(f"Status: {batch_job.status}")

# Poll for completion
while batch_job.status not in ["completed", "failed"]:
    time.sleep(30)
    batch_job = client.batches.retrieve(batch_job.id)
    print(f"Status: {batch_job.status}")

# Get results
if batch_job.status == "completed":
    result_file_id = batch_job.output_file_id
    result_content = client.files.content(result_file_id).text
    
    for line in result_content.strip().split("\n"):
        result = json.loads(line)
        print(f"ID: {result['custom_id']}, Result: {result['result']}")
```

## Configuration

```python
import os
from openai import OpenAI

# Set API key via environment variable
os.environ["OPENAI_API_KEY"] = "sk-..."

# Or pass directly (not recommended for production)
client = OpenAI(api_key="sk-...")

# Custom base URL (for Azure OpenAI)
client = OpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2024-02-01"
)
```

## References

- [OpenAI Platform Documentation](https://platform.openai.com/docs)
- [API Reference](https://platform.openai.com/docs/api-reference)
- [GitHub Repository](https://github.com/openai/openai-python)
- [Model Overview](https://platform.openai.com/docs/models)
- [Pricing](https://openai.com/pricing)
