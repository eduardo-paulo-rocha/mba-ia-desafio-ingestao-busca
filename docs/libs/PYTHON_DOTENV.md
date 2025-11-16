# python-dotenv

## Overview

**Version:** 1.1.1  
**Type:** Environment Configuration Management  
**Repository:** https://github.com/theskumar/python-dotenv  
**Documentation:** https://python-dotenv.readthedocs.io/

python-dotenv is a Python library that reads key-value pairs from `.env` files and sets them as environment variables. It's essential for managing configuration, API keys, database credentials, and other sensitive data securely without hardcoding them into source code.

## Key Features

### 1. Environment Variable Loading
- Load variables from `.env` files
- Override existing environment variables
- Support for nested `.env` files
- Variable interpolation and expansion

### 2. POSIX Variable Expansion
- Support for `${VAR}` syntax
- Default values: `${VAR:-default}`
- Variable expansion across definitions

### 3. Flexible Configuration
- Find `.env` files automatically
- Custom parsing and validation
- Support for multiline values
- Comments and blank lines

### 4. CLI Tools
- Command-line interface for managing variables
- Integration with shell and scripts

## Installation

```bash
# Basic installation
pip install python-dotenv==1.1.1

# With CLI support
pip install python-dotenv[cli]==1.1.1

# With IPython extension
pip install python-dotenv[ipython]==1.1.1
```

## Basic Usage

### 1. Simple Environment Loading

```python
from dotenv import load_dotenv
import os

# Load variables from .env file in current directory
load_dotenv()

# Access environment variables
database_url = os.getenv("DATABASE_URL")
api_key = os.getenv("OPENAI_API_KEY")
pdf_path = os.getenv("PDF_PATH")

print(f"Database: {database_url}")
print(f"API Key: {api_key}")
print(f"PDF Path: {pdf_path}")
```

### 2. Load from Specific File

```python
from dotenv import load_dotenv
import os

# Load from specific .env file
load_dotenv(".env.production")

# Load from different directory
load_dotenv("./config/.env")

# Override existing environment variables
load_dotenv(override=True)
```

### 3. Get All Variables as Dictionary

```python
from dotenv import dotenv_values

# Load variables as dictionary (doesn't set env vars)
config = dotenv_values(".env")

database_url = config["DATABASE_URL"]
api_key = config["OPENAI_API_KEY"]
debug = config.get("DEBUG", "False") == "True"

print(f"Config: {config}")
```

### 4. Find .env File Automatically

```python
from dotenv import find_dotenv, load_dotenv

# Find .env file starting from current directory
env_file = find_dotenv()

if env_file:
    print(f"Found .env file: {env_file}")
    load_dotenv(env_file)
else:
    print(".env file not found")
```

## .env File Format

### 1. Basic Variables

```env
# .env file example
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
PDF_PATH=./documents/
DEBUG=True
MAX_WORKERS=4
```

### 2. Variables with Spaces (Quoted)

```env
# Values with spaces must be quoted
GREETING="Hello World"
DESCRIPTION='This is a description with spaces'
MULTILINE_VALUE="Line 1
Line 2
Line 3"
```

### 3. POSIX Variable Expansion

```env
# Variable references (requires bash_export=True)
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=postgres
DATABASE_PASSWORD=secret

# Build connection string using variables
DATABASE_URL=postgresql://${DATABASE_USER}:${DATABASE_PASSWORD}@${DATABASE_HOST}:${DATABASE_PORT}/mydb

# Default values
DATABASE_BACKUP=${DATABASE_BACKUP_URL:-postgresql://backup-host/backup_db}
ENVIRONMENT=${ENV:-development}

# Nested expansion
DOCUMENT_PATH=/data/documents
PDF_PATH=${DOCUMENT_PATH}/pdfs
CONFIG_PATH=${DOCUMENT_PATH}/config
```

### 4. Comments

```env
# This is a comment
DATABASE_URL=postgresql://localhost/mydb

# API Keys (keep secret!)
OPENAI_API_KEY=sk-...     # OpenAI API key
GOOGLE_API_KEY=AIza...    # Google API key

# Feature flags
DEBUG=False                # Enable debug logging
TESTING=False              # Enable testing mode
```

## Advanced Usage

### 1. Custom Parsing

```python
from dotenv import dotenv_values
import os

# Custom .env parser
config = dotenv_values(".env")

# Type conversion
def get_config_int(key, default=0):
    try:
        return int(config.get(key, default))
    except ValueError:
        return default

def get_config_bool(key, default=False):
    return config.get(key, str(default)).lower() == 'true'

# Usage
max_workers = get_config_int("MAX_WORKERS", 4)
debug = get_config_bool("DEBUG", False)
```

### 2. Variable Interpolation

```python
from dotenv import load_dotenv
import os

# .env file with variables
# BASE_PATH=/data
# PDF_PATH=${BASE_PATH}/pdfs
# MODELS_PATH=${BASE_PATH}/models

load_dotenv()

# Note: Basic dotenv doesn't interpolate by default
# For interpolation, use custom logic
import re

def interpolate_env():
    config = dotenv_values(".env")
    
    # Multiple passes to handle nested variables
    for _ in range(3):
        for key, value in config.items():
            # Find ${VAR} patterns
            matches = re.findall(r'\$\{([^}]+)\}', value)
            for match in matches:
                if match in config:
                    value = value.replace(f"${{{match}}}", config[match])
                config[key] = value
    
    # Set in environment
    for key, value in config.items():
        os.environ[key] = value

interpolate_env()

# Now variables are interpolated
print(os.getenv("PDF_PATH"))  # /data/pdfs
```

### 3. Managing Multiple Environments

```python
from dotenv import load_dotenv
import os

def load_environment(env=None):
    """Load environment based on settings"""
    
    if env is None:
        env = os.getenv("ENVIRONMENT", "development")
    
    # Load base .env
    load_dotenv(".env")
    
    # Load environment-specific .env
    env_file = f".env.{env}"
    load_dotenv(env_file, override=True)
    
    print(f"Loaded environment: {env}")
    
    return env

# Usage
environment = load_environment("production")

# Settings can be overridden based on environment
print(f"Database: {os.getenv('DATABASE_URL')}")
print(f"Debug: {os.getenv('DEBUG')}")
```

## Integration with RAG Project

### 1. In Project Root - .env File

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/rag
VECTOR_EXTENSION=vector

# LLM Configuration
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...

# Model Selection (use one)
LLM_PROVIDER=openai          # or 'google'
EMBEDDING_MODEL=text-embedding-3-small

# Paths
PDF_PATH=./documents/
LOGS_PATH=./logs/
CACHE_PATH=./cache/

# Application Configuration
DEBUG=False
LOG_LEVEL=INFO
MAX_WORKERS=4
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Optional Configuration with Defaults (use in code)
# TEMPERATURE=0.7
# MAX_TOKENS=500
```

### 2. In `src/config.py` - Centralized Configuration

```python
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_file = Path(__file__).parent.parent / ".env"
load_dotenv(env_file)

class Config:
    """Application configuration"""
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not set in .env")
    
    # LLM Configuration
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
    
    if LLM_PROVIDER == "openai":
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set for OpenAI provider")
    
    elif LLM_PROVIDER == "google":
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not set for Google provider")
    
    # Paths
    PDF_PATH = Path(os.getenv("PDF_PATH", "./documents/"))
    LOGS_PATH = Path(os.getenv("LOGS_PATH", "./logs/"))
    CACHE_PATH = Path(os.getenv("CACHE_PATH", "./cache/"))
    
    # Ensure directories exist
    PDF_PATH.mkdir(exist_ok=True)
    LOGS_PATH.mkdir(exist_ok=True)
    CACHE_PATH.mkdir(exist_ok=True)
    
    # Application
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
    
    # Chunking
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # Optional with defaults
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "500"))
    
    @classmethod
    def to_dict(cls):
        """Return configuration as dictionary"""
        return {
            key: getattr(cls, key)
            for key in dir(cls)
            if not key.startswith("_") and key.isupper()
        }

# Usage
if __name__ == "__main__":
    config = Config()
    print("Configuration loaded:")
    for key, value in config.to_dict().items():
        # Hide sensitive keys
        if "KEY" in key or "PASSWORD" in key:
            print(f"  {key}: {'*' * 10}")
        else:
            print(f"  {key}: {value}")
```

### 3. In `src/ingest.py` - Use Configuration

```python
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from pypdf import PdfReader
import psycopg
from pgvector.psycopg import register_vector
from langchain_text_splitters import RecursiveCharacterTextSplitter

def ingest_pdf(pdf_path: str):
    """Ingest PDF using configuration from .env"""
    
    # Access configuration
    db_url = Config.DATABASE_URL
    chunk_size = Config.CHUNK_SIZE
    chunk_overlap = Config.CHUNK_OVERLAP
    
    print(f"Using configuration:")
    print(f"  Database: {db_url.split('@')[1] if '@' in db_url else 'localhost'}")
    print(f"  Chunk size: {chunk_size}")
    print(f"  Chunk overlap: {chunk_overlap}")
    
    # Read PDF
    reader = PdfReader(pdf_path)
    
    # Extract and chunk
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    chunks = splitter.split_text(text)
    
    # Connect to database
    conn = psycopg.connect(db_url, autocommit=True)
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    register_vector(conn)
    
    print(f"Processing {len(chunks)} chunks...")
    
    # Store chunks (implementation continues...)

if __name__ == "__main__":
    pdf_path = str(Config.PDF_PATH / "example.pdf")
    ingest_pdf(pdf_path)
```

### 4. In `src/search.py` - Use Configuration

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
import psycopg
from pgvector.psycopg import register_vector

def search_prompt(question: str) -> str:
    """Search and generate response using configuration"""
    
    if Config.LLM_PROVIDER == "openai":
        from langchain_openai import OpenAIEmbeddings, ChatOpenAI
        
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=Config.OPENAI_API_KEY
        )
        
        llm = ChatOpenAI(
            model="gpt-4",
            api_key=Config.OPENAI_API_KEY,
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS
        )
    
    elif Config.LLM_PROVIDER == "google":
        import google.generativeai as genai
        
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        
        # Simplified for Google
        embeddings = None  # Use Google embeddings
        llm = genai.GenerativeModel("gemini-1.5-pro")
    
    # Connect to database
    conn = psycopg.connect(Config.DATABASE_URL)
    register_vector(conn)
    
    # Search and respond...
    
    conn.close()
```

### 5. In `src/chat.py` - Initialize Application

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from search import search_prompt
import logging

# Setup logging using configuration
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Chat interface using configuration"""
    
    logger.info(f"Starting chat application (Debug: {Config.DEBUG})")
    logger.info(f"LLM Provider: {Config.LLM_PROVIDER}")
    
    if Config.DEBUG:
        # Show configuration in debug mode
        config_dict = Config.to_dict()
        logger.debug(f"Configuration: {config_dict}")
    
    print("Chat with your documents (type 'quit' to exit)")
    
    while True:
        question = input("\nYou: ").strip()
        
        if question.lower() == 'quit':
            break
        
        if not question:
            continue
        
        try:
            answer = search_prompt(question)
            print(f"\nAssistant: {answer}")
        
        except Exception as e:
            logger.error(f"Error: {e}")
            print("Sorry, an error occurred.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
```

## CLI Usage

```bash
# Get environment variable
python -m dotenv get DATABASE_URL

# Set environment variable
python -m dotenv set OPENAI_API_KEY sk-...

# List all variables
python -m dotenv list

# Run command with environment
python -m dotenv run python src/chat.py
```

## Security Best Practices

### 1. Never Commit .env Files

```bash
# .gitignore
.env
.env.local
.env.*.local
.env.production
```

### 2. Use .env.example for Documentation

```env
# .env.example (commit this to repository)
# Copy this file to .env and fill in your values

DATABASE_URL=postgresql://user:password@localhost:5432/dbname
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
PDF_PATH=./documents/
DEBUG=False
```

### 3. Validate Required Variables

```python
from dotenv import load_dotenv
import os

load_dotenv()

REQUIRED_VARS = [
    "DATABASE_URL",
    "OPENAI_API_KEY",
    "PDF_PATH"
]

missing = [var for var in REQUIRED_VARS if not os.getenv(var)]

if missing:
    raise ValueError(f"Missing required environment variables: {missing}")

print("✓ All required environment variables set")
```

## IPython Integration

```python
# In IPython or Jupyter
%load_ext dotenv
%dotenv .env

# Now environment variables are loaded in Jupyter
import os
print(os.getenv("DATABASE_URL"))
```

## References

- [python-dotenv Documentation](https://python-dotenv.readthedocs.io/)
- [GitHub Repository](https://github.com/theskumar/python-dotenv)
- [PyPI Package](https://pypi.org/project/python-dotenv/)
- [Best Practices Guide](https://github.com/theskumar/python-dotenv/wiki/Best-Practices)
