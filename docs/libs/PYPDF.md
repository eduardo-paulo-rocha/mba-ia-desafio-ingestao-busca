# PyPDF

## Overview

**Version:** 6.0.0  
**Type:** PDF File Processing Library  
**Repository:** https://github.com/py-pdf/pypdf  
**Documentation:** https://pypdf.readthedocs.io/

PyPDF (formerly PyPDF2) is a pure Python library for reading and writing PDF files. It provides comprehensive functionality for text extraction, page manipulation, metadata handling, and document transformation without external dependencies.

## Key Features

### 1. Reading PDF Files
- Extract text and metadata
- Access document properties
- Page-by-page processing
- Encryption/decryption support

### 2. Writing and Manipulation
- Merge PDF documents
- Split documents
- Crop and rotate pages
- Add watermarks and stamps

### 3. Content Extraction
- Text extraction
- Image extraction
- Form field reading
- Annotation handling

### 4. Advanced Features
- Compress documents
- Add/remove bookmarks
- Modify document outline
- Working with PDF objects

## Installation

```bash
# Basic installation
pip install pypdf==6.0.0

# With extra dependencies (for image extraction)
pip install pypdf[images]==6.0.0

# For faster performance
pip install pypdf[crypto]==6.0.0
```

## Basic Usage

### 1. Reading PDF Files

```python
from pypdf import PdfReader

# Open PDF file
pdf_reader = PdfReader("document.pdf")

# Get number of pages
num_pages = len(pdf_reader.pages)
print(f"Total pages: {num_pages}")

# Extract text from first page
first_page = pdf_reader.pages[0]
text = first_page.extract_text()
print(text)

# Extract text from all pages
all_text = ""
for page in pdf_reader.pages:
    all_text += page.extract_text()

print(all_text)

# Get PDF metadata
metadata = pdf_reader.metadata
print(f"Title: {metadata.title}")
print(f"Author: {metadata.author}")
print(f"Subject: {metadata.subject}")
```

### 2. Extracting Text from Specific Pages

```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")

# Extract from pages 5-10
for page_num in range(5, 11):
    page = reader.pages[page_num]
    text = page.extract_text()
    print(f"--- Page {page_num + 1} ---")
    print(text)
    print()
```

### 3. Writing and Merging PDFs

```python
from pypdf import PdfWriter, PdfReader
import os

# Merge multiple PDFs
writer = PdfWriter()

pdf_files = ["document1.pdf", "document2.pdf", "document3.pdf"]

for pdf_file in pdf_files:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

# Write merged PDF
with open("merged.pdf", "wb") as output_file:
    writer.write(output_file)

print("✓ PDFs merged successfully")
```

### 4. Splitting PDFs

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("large_document.pdf")

# Split into individual page files
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    
    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)

print(f"✓ Split into {len(reader.pages)} files")

# Split in half
mid_point = len(reader.pages) // 2

writer1 = PdfWriter()
for page in reader.pages[:mid_point]:
    writer1.add_page(page)

with open("document_part1.pdf", "wb") as f:
    writer1.write(f)

writer2 = PdfWriter()
for page in reader.pages[mid_point:]:
    writer2.add_page(page)

with open("document_part2.pdf", "wb") as f:
    writer2.write(f)
```

### 5. Rotating and Cropping Pages

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    # Rotate page 90 degrees clockwise
    page.rotate_clockwise(90)
    
    # Crop page (left, bottom, right, top)
    page.cropbox.lower_left = (50, 50)
    page.cropbox.upper_right = (500, 750)
    
    writer.add_page(page)

with open("transformed.pdf", "wb") as output:
    writer.write(output)
```

### 6. Adding Watermarks and Stamps

```python
from pypdf import PdfReader, PdfWriter

# Load original and watermark PDFs
original = PdfReader("document.pdf")
watermark = PdfReader("watermark.pdf")
writer = PdfWriter()

watermark_page = watermark.pages[0]

# Apply watermark to each page
for page in original.pages:
    page.merge_page(watermark_page)
    writer.add_page(page)

with open("watermarked.pdf", "wb") as output:
    writer.write(output)
```

### 7. Encrypting and Decrypting PDFs

```python
from pypdf import PdfReader, PdfWriter

# Encrypt PDF
reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

# Add encryption
writer.encrypt("password123")

with open("encrypted.pdf", "wb") as f:
    writer.write(f)

# Decrypt PDF
encrypted_reader = PdfReader("encrypted.pdf")
encrypted_reader.decrypt("password123")

# Extract text from encrypted PDF
text = encrypted_reader.pages[0].extract_text()
print(text)
```

### 8. Working with PDF Objects and References

```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")

# Access raw PDF objects
page = reader.pages[0]

# Get page box dimensions
print(f"MediaBox: {page.mediabox}")
print(f"CropBox: {page.cropbox}")

# Get page resources
if "/Resources" in page:
    resources = page["/Resources"]
    print(f"Resources: {resources}")
```

## Batch Processing for RAG

### 1. Extract Text from Multiple PDFs

```python
from pypdf import PdfReader
import os
from pathlib import Path

def extract_all_pdfs(directory: str) -> dict:
    """Extract text from all PDFs in a directory"""
    
    pdf_data = {}
    pdf_files = Path(directory).glob("*.pdf")
    
    for pdf_path in pdf_files:
        print(f"Processing: {pdf_path.name}")
        
        try:
            reader = PdfReader(str(pdf_path))
            
            # Extract metadata
            metadata = {
                "title": reader.metadata.title if reader.metadata else "Unknown",
                "author": reader.metadata.author if reader.metadata else "Unknown",
                "pages": len(reader.pages)
            }
            
            # Extract text
            text_content = ""
            page_texts = []
            
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                page_texts.append(page_text)
                text_content += page_text + "\n"
            
            pdf_data[pdf_path.name] = {
                "metadata": metadata,
                "full_text": text_content,
                "pages": page_texts
            }
            
            print(f"  ✓ Extracted {len(reader.pages)} pages")
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
            pdf_data[pdf_path.name] = {"error": str(e)}
    
    return pdf_data

# Usage
pdfs = extract_all_pdfs("documents/")

for filename, data in pdfs.items():
    if "error" not in data:
        print(f"\n{filename}:")
        print(f"  Title: {data['metadata']['title']}")
        print(f"  Pages: {data['metadata']['pages']}")
        print(f"  Text length: {len(data['full_text'])} chars")
```

### 2. Split PDFs for Chunking

```python
from pypdf import PdfReader, PdfWriter
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

def prepare_pdf_chunks(pdf_path: str, chunk_size: int = 1000):
    """Extract and chunk PDF content"""
    
    reader = PdfReader(pdf_path)
    
    chunks = []
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        
        # Get page metadata
        metadata = {
            "source": os.path.basename(pdf_path),
            "page": page_num,
            "page_dimensions": str(page.mediabox)
        }
        
        # Split into chunks
        page_chunks = splitter.split_text(text)
        
        for chunk_idx, chunk in enumerate(page_chunks):
            chunks.append({
                "content": chunk,
                "page": page_num,
                "chunk_index": chunk_idx,
                "metadata": metadata
            })
    
    return chunks

# Usage
chunks = prepare_pdf_chunks("document.pdf")
print(f"Created {len(chunks)} chunks")

for chunk in chunks[:3]:
    print(f"\nPage {chunk['page']}, Chunk {chunk['chunk_index']}:")
    print(chunk['content'][:100] + "...")
```

## Integration with RAG Project

### In `src/ingest.py` - Complete Implementation

```python
from pypdf import PdfReader
import psycopg
from pgvector.psycopg import register_vector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import os
from pathlib import Path

def ingest_pdf(pdf_path: str):
    """Ingest PDF, extract text, chunk, embed, and store in vector DB"""
    
    print(f"Starting PDF ingestion: {pdf_path}")
    
    # Read PDF with PyPDF
    reader = PdfReader(pdf_path)
    
    # Extract text from all pages
    full_text = ""
    page_contents = []
    
    print(f"Extracting text from {len(reader.pages)} pages...")
    
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        page_contents.append({
            "page": page_num,
            "text": text,
            "length": len(text)
        })
        full_text += text + "\n"
    
    # Get PDF metadata
    metadata = reader.metadata or {}
    pdf_title = metadata.get("/Title", os.path.basename(pdf_path))
    
    # Chunk text using LangChain
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = splitter.split_text(full_text)
    print(f"Created {len(chunks)} chunks from PDF")
    
    # Connect to database
    conn = psycopg.connect(os.getenv("DATABASE_URL"), autocommit=True)
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    register_vector(conn)
    
    # Create table if not exists
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pdf_chunks (
                id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
                filename TEXT,
                title TEXT,
                chunk_number INT,
                content TEXT,
                embedding vector(1536),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
    
    # Generate embeddings and store chunks
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    print(f"Generating embeddings...")
    
    with conn.cursor() as cur:
        with cur.copy(
            """COPY pdf_chunks (filename, title, chunk_number, content, embedding) 
               FROM STDIN"""
        ) as copy:
            for i, chunk in enumerate(chunks):
                # Generate embedding
                embedding = embeddings.embed_query(chunk)
                
                copy.write_row([
                    os.path.basename(pdf_path),
                    pdf_title,
                    i,
                    chunk,
                    embedding
                ])
                
                if (i + 1) % 10 == 0:
                    print(f"  Processed {i + 1}/{len(chunks)} chunks")
    
    # Create HNSW index for fast similarity search
    with conn.cursor() as cur:
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_pdf_embedding_hnsw 
            ON pdf_chunks USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64)
        """)
    
    conn.close()
    
    print(f"✓ Successfully ingested {len(chunks)} chunks")
    return {
        "filename": os.path.basename(pdf_path),
        "pages": len(reader.pages),
        "chunks": len(chunks),
        "title": pdf_title
    }

def ingest_directory(directory: str):
    """Ingest all PDFs from a directory"""
    
    results = []
    pdf_files = Path(directory).glob("*.pdf")
    
    for pdf_path in pdf_files:
        try:
            result = ingest_pdf(str(pdf_path))
            results.append(result)
        except Exception as e:
            print(f"✗ Error processing {pdf_path}: {e}")
            results.append({"error": str(e)})
    
    return results

if __name__ == "__main__":
    pdf_dir = os.getenv("PDF_PATH", "documents/")
    results = ingest_directory(pdf_dir)
    
    print("\n=== Ingestion Summary ===")
    for result in results:
        if "error" in result:
            print(f"✗ {result}")
        else:
            print(f"✓ {result['filename']}: {result['chunks']} chunks")
```

## Advanced Operations

### 1. Extract Form Fields

```python
from pypdf import PdfReader

reader = PdfReader("form.pdf")

# Get form fields
if reader.get_fields():
    print("Form fields found:")
    for field_name, field in reader.get_fields().items():
        print(f"  {field_name}: {field}")
else:
    print("No form fields in this PDF")
```

### 2. Get Page Dimensions and Text Positions

```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")
page = reader.pages[0]

# Get page dimensions
print(f"MediaBox: {page.mediabox}")
print(f"Page width: {page.mediabox.width}")
print(f"Page height: {page.mediabox.height}")

# Extract text with position information
text_with_position = page.extract_text_with_positions()
print(f"Extracted text with positions: {len(text_with_position)} items")
```

### 3. Remove Pages

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("document.pdf")
writer = PdfWriter()

# Skip pages (e.g., table of contents, blank pages)
skip_pages = [0, 1, 5]  # Skip first 2 pages and page 6

for i, page in enumerate(reader.pages):
    if i not in skip_pages:
        writer.add_page(page)

with open("cleaned.pdf", "wb") as f:
    writer.write(f)

print(f"Kept {len(writer.pages)} pages")
```

## Error Handling

```python
from pypdf import PdfReader
from pypdf.errors import PdfReadError

try:
    reader = PdfReader("document.pdf")
    
    if not reader.pages:
        print("PDF has no pages")
    else:
        text = reader.pages[0].extract_text()
        print(text)

except FileNotFoundError:
    print("PDF file not found")

except PdfReadError as e:
    print(f"Error reading PDF: {e}")

except Exception as e:
    print(f"Unexpected error: {e}")
```

## Performance Tips

1. **Use bulk copy for batch operations** when inserting into database
2. **Extract text once** and cache results
3. **Use page-by-page processing** for large PDFs to manage memory
4. **Create indexes** on frequently searched fields
5. **Consider compression** for storage

## Configuration

```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")

# Check if encrypted
if reader.is_encrypted:
    reader.decrypt("password")

# Check if readable
if not reader.is_pdf:
    print("Not a valid PDF file")
```

## References

- [PyPDF Documentation](https://pypdf.readthedocs.io/)
- [GitHub Repository](https://github.com/py-pdf/pypdf)
- [API Reference](https://pypdf.readthedocs.io/en/latest/user/code-examples/)
- [Migration from PyPDF2](https://pypdf.readthedocs.io/en/latest/user/migrating-from-pypdf2.html)
