import os
import json
import hashlib
from typing import List, Dict, Tuple, Any
from dotenv import load_dotenv
from pypdf import PdfReader
from openai import OpenAI
import psycopg
from pgvector.psycopg import register_vector

load_dotenv()

# Configs (env overrides)
PDF_PATH = os.getenv("PDF_PATH", "./document.pdf")
DATABASE_URL = os.getenv("DATABASE_URL")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
UPsert_BATCH = 8


def read_pdf_pages(path: str) -> List[str]:
    reader = PdfReader(path)
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return pages


def build_full_text_and_offsets(pages: List[str]) -> Tuple[str, List[int]]:
    # returns full_text and list of start offsets for each page (0-based)
    offsets = []
    pos = 0
    pieces = []
    for p in pages:
        offsets.append(pos)
        pieces.append(p)
        pos += len(p) + 1  # +1 for separator we add between pages
    full_text = "\n".join(pages)
    return full_text, offsets


def char_offset_to_page(offsets: List[int], char_idx: int) -> int:
    # returns page index (0-based) for given char index in the full_text
    # binary search manual
    lo = 0
    hi = len(offsets) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if offsets[mid] <= char_idx:
            lo = mid + 1
        else:
            hi = mid - 1
    # hi will be the page index where offsets[hi] <= char_idx < offsets[hi+1]
    return max(0, hi)


def chunk_text_with_pages(full_text: str, offsets: List[int], chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[Dict[str, Any]]:
    step = chunk_size - overlap
    chunks = []
    n = len(full_text)
    idx = 0
    chunk_index = 0
    while idx < n:
        end = min(idx + chunk_size, n)
        text_chunk = full_text[idx:end]
        start_char = idx
        end_char = end - 1
        page_start = char_offset_to_page(offsets, start_char)
        page_end = char_offset_to_page(offsets, end_char)
        chunks.append({
            "chunk_index": chunk_index,
            "texto": text_chunk,
            "start_char": start_char,
            "end_char": end_char,
            "page_start": page_start + 1,  # store pages as 1-based
            "page_end": page_end + 1,
        })
        chunk_index += 1
        if end == n:
            break
        idx += step
    return chunks


def compute_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def get_embedding_openai(text: str) -> List[float]:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY não encontrada no ambiente.")

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    embedding = response.data[0].embedding

    return embedding


def get_db_conn():
    if DATABASE_URL:
        conn = psycopg.connect(DATABASE_URL, autocommit=False)
    else:
        # fallback to individual PG_* env vars
        conninfo = {
            "host": os.getenv("PGHOST", "localhost"),
            "port": os.getenv("PGPORT", "5432"),
            "user": os.getenv("PGUSER", "postgres"),
            "password": os.getenv("PGPASSWORD", "postgres"),
            "dbname": os.getenv("PGDATABASE", "rag"),
        }
        dsn = "host={host} port={port} user={user} password={password} dbname={dbname}".format(**conninfo)
        conn = psycopg.connect(dsn, autocommit=False)
    # register pgvector adapter for this connection
    register_vector(conn)
    return conn


def ensure_vector_extension(conn: psycopg.Connection):
    try:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        conn.commit()
    except Exception as e:
        # If user lacks permission to create extension, we still continue and let subsequent ops fail with clearer error
        print(f"[WARN] Não foi possível criar/garantir extensão vector: {e}")
        conn.rollback()


def get_table_embedding_dim(conn: psycopg.Connection) -> int:
    sql = """
    SELECT format_type(a.atttypid, a.atttypmod) AS typ
    FROM pg_attribute a
    JOIN pg_class c ON a.attrelid = c.oid
    JOIN pg_namespace n ON c.relnamespace = n.oid
    WHERE c.relname = 'documentos' AND n.nspname = 'public' AND a.attname = 'embedding';
    """
    row = conn.execute(sql).fetchone()
    if row and row[0]:
        typ = row[0]  # e.g. "vector(1536)"
        if typ.startswith("vector(") and typ.endswith(")"):
            try:
                dim = int(typ[len("vector("):-1])
                return dim
            except Exception:
                pass
    return -1  # unknown


def alter_embedding_dim(conn: psycopg.Connection, new_dim: int):
    # Alters column type to desired vector dimension.
    sql = f"ALTER TABLE public.documentos ALTER COLUMN embedding TYPE vector({new_dim});"
    print(f"[INFO] Alterando dimensão da coluna embedding para vector({new_dim}) ...")
    conn.execute(sql)
    conn.commit()
    print("[INFO] ALTER TABLE concluído.")


UPSERT_SQL = """
INSERT INTO public.documentos(documento_id, chunk_index, texto, embedding, page_start, page_end, content_hash, metadata)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (documento_id, chunk_index) DO UPDATE
  SET texto = EXCLUDED.texto,
      embedding = EXCLUDED.embedding,
      page_start = EXCLUDED.page_start,
      page_end = EXCLUDED.page_end,
      content_hash = EXCLUDED.content_hash,
      metadata = EXCLUDED.metadata,
      criado_em = now();
"""


def upsert_chunks(conn: psycopg.Connection, documento_id: str, chunk_items: List[Dict[str, Any]]):
    # chunk_items: list of dicts containing keys:
    # chunk_index, texto, page_start, page_end, content_hash, metadata (dict), embedding (list[float])
    with conn.cursor() as cur:
        for item in chunk_items:
            # pgvector accepts embeddings as lists directly
            embedding = item["embedding"]
            metadata_json = json.dumps(item.get("metadata") or {})
            cur.execute(UPSERT_SQL, (
                documento_id,
                item["chunk_index"],
                item["texto"],
                embedding,
                item["page_start"],
                item["page_end"],
                item["content_hash"],
                metadata_json
            ))
        conn.commit()


def ingest_pdf(path: str):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"PDF não encontrado em: {path}")

    print(f"[INFO] Lendo PDF: {path}")
    pages = read_pdf_pages(path)
    full_text, offsets = build_full_text_and_offsets(pages)
    print(f"[INFO] {len(pages)} páginas extraídas, texto total {len(full_text)} caracteres.")

    chunks = chunk_text_with_pages(full_text, offsets, CHUNK_SIZE, CHUNK_OVERLAP)
    print(f"[INFO] Gerados {len(chunks)} chunks (chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}).")

    documento_id = os.path.basename(path)

    conn = get_db_conn()
    try:
        ensure_vector_extension(conn)
        db_dim = get_table_embedding_dim(conn)
        print(f"[INFO] dimensão do embedding na tabela: {db_dim if db_dim>0 else 'desconhecida'}")

        # We'll process in batches
        batch_items = []
        for i, c in enumerate(chunks):
            texto = c["texto"].strip()
            if not texto:
                continue
            content_hash = compute_sha256(texto)
            # metadata base: we include offsets to help rastrear
            metadata = {
                "source_file": documento_id,
                "chunk_char_start": c["start_char"],
                "chunk_char_end": c["end_char"]
            }

            # generate embedding
            try:
                emb = get_embedding_openai(texto)
            except Exception as e:
                print(f"[ERROR] erro ao gerar embedding para chunk {c['chunk_index']}: {e}")
                raise

            emb_len = len(emb)
            # if DB dim unknown, attempt to set to emb_len
            if db_dim <= 0:
                print(f"[WARN] Dimensão atual da coluna embedding desconhecida; definindo para {emb_len}.")
                try:
                    alter_embedding_dim(conn, emb_len)
                    db_dim = emb_len
                except Exception as e:
                    print(f"[ERROR] Falha ao alterar dimensão embedding: {e}")
                    conn.rollback()
                    raise

            # If dim mismatch, alter table (warn)
            if emb_len != db_dim:
                print(f"[WARN] Dimensão do embedding ({emb_len}) difere da coluna ({db_dim}). Tentando ajustar a coluna para {emb_len}.")
                try:
                    alter_embedding_dim(conn, emb_len)
                    db_dim = emb_len
                except Exception as e:
                    print(f"[ERROR] Não foi possível ajustar dimensão da coluna: {e}")
                    conn.rollback()
                    raise

            batch_items.append({
                "chunk_index": c["chunk_index"],
                "texto": texto,
                "page_start": c["page_start"],
                "page_end": c["page_end"],
                "content_hash": content_hash,
                "metadata": metadata,
                "embedding": emb
            })

            # commit batch
            if len(batch_items) >= UPsert_BATCH:
                upsert_chunks(conn, documento_id, batch_items)
                print(f"[INFO] Upserted {len(batch_items)} chunks (progresso {i+1}/{len(chunks)}).")
                batch_items = []

        # final batch
        if batch_items:
            upsert_chunks(conn, documento_id, batch_items)
            print(f"[INFO] Upserted {len(batch_items)} chunks (final).")

    finally:
        conn.close()
        print("[INFO] Conexão ao banco fechada.")


if __name__ == "__main__":
    try:
        ingest_pdf(PDF_PATH)
    except Exception as e:
        print(f"[FATAL] Ingestão falhou: {e}")
        raise