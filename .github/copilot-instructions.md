## Quick context

This repository is a small proof-of-concept RAG (retrieval-augmented generation) pipeline.
- Data ingestion: `src/ingest.py` (currently a stub) — intended to load PDFs from the path in `PDF_PATH` (.env).
- Vector store: Postgres + pgvector (see `docker-compose.yml` and `requirements.txt` — `pgvector`, `psycopg`, `langchain-postgres`).
- Retrieval & prompt: `src/search.py` defines the prompt template and `search_prompt()` (currently a stub).
- Chat launcher: `src/chat.py` calls `search_prompt()` to start the chat flow.

The README is minimal; many functions are currently placeholders. Use the files above as the source of truth.

## What the agent should know and do first

1. Look at `docker-compose.yml` — the project expects a Postgres container with the `vector` extension. The repo provides a bootstrap service that creates the extension.
2. Check `.env`/environment variables — the code uses `python-dotenv` and expects `PDF_PATH` and likely API keys (OpenAI / Google GenAI) in environment variables.
3. The codebase uses LangChain-style libraries (see `requirements.txt`). Integration points: `langchain`, `langchain-postgres`, `openai`, `google-ai-generativelanguage`.

## Concrete developer workflows (examples you can run locally)

- Install deps (PowerShell):
```
pip install -r requirements.txt
```
- Start Postgres + pgvector (from repo root):
```
docker-compose up -d
```
Wait for `postgres` to be healthy and for `bootstrap_vector_ext` to run once (it applies CREATE EXTENSION IF NOT EXISTS vector).

- Run the chat launcher while env vars are set (example):
```
$env:PDF_PATH = 'data/my.pdf'; python .\src\chat.py
```

If you need to run as a module in some environments use `python src/chat.py` — the project is simple flat scripts, not a package.

## Project-specific patterns & conventions (observed)

- Strict prompt rule: `src/search.py` contains the prompt template that enforces responses only from retrieved CONTEXT and to reply `"Não tenho informações necessárias para responder sua pergunta."` when context is missing. Any agent edits should preserve that behavior.
- Environment via `dotenv` is the canonical configuration mechanism — prefer env variables to hard-coded paths.
- Vector DB = Postgres + pgvector. Expect code that writes/reads vectors via `psycopg` or LangChain Postgres connectors.

## Integration points and required secrets

- Database: `docker-compose.yml` exposes Postgres on 5432 and creates a `rag` DB. The agent should not assume another DB is present.
- LLM APIs: The code includes `openai` and Google GenAI SDKs in `requirements.txt`. The agent should look for API key usage or env var names when adding or editing model calls.

## When editing or adding code — concrete tips

- If you implement ingestion, set `PDF_PATH` via `.env` and add a small CLI in `src/ingest.py` to load, split, and upsert vectors into Postgres (`pgvector`) — prefer using LangChain clients where available.
- Preserve the prompt template in `src/search.py`. If you change the wording, keep the rule that the model must only answer from CONTEXT and return the exact Portuguese fallback string when missing.
- Prefer small, testable functions: add unit tests next to modules (not yet present) before changing behavior.

## Files to inspect for further changes
- `src/ingest.py` — ingestion pipeline (stub)
- `src/search.py` — prompt, retrieval, chain (stub)
- `src/chat.py` — CLI/entrypoint that invokes `search_prompt()`
- `docker-compose.yml` — Postgres + bootstrap extension
- `requirements.txt` — shows third-party libraries and should guide imports

## Example PR checklist for the repo
- Run `pip install -r requirements.txt` and `docker-compose up -d` locally.
- Verify Postgres container is healthy and that `vector` extension exists.
- Keep the strict prompt fallback behavior.
- Document any new env vars in `README.md`.

## If anything is missing
If you need more specifics (env var names for LLM keys, exact vector table schema, or example ingestion code), ask and I'll extract or implement them — currently many functions are intentionally left as stubs.

---
Please review this file and tell me whether you'd like more detail in any section (e.g., example ingestion code, exact env var names, or a short test harness).
