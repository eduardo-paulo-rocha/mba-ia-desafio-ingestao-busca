import os
from typing import List
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
import psycopg
from pgvector.psycopg import register_vector

load_dotenv()

# Configs (env overrides)
DATABASE_URL = os.getenv("DATABASE_URL")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def get_db_conn() -> psycopg.Connection:
    """Estabelece conexão com o banco de dados PostgreSQL."""
    if DATABASE_URL:
        conn = psycopg.connect(DATABASE_URL, autocommit=False)
    else:
        # Fallback para variáveis de ambiente individuais
        conninfo = {
            "host": os.getenv("PGHOST", "localhost"),
            "port": os.getenv("PGPORT", "5432"),
            "user": os.getenv("PGUSER", "postgres"),
            "password": os.getenv("PGPASSWORD", "postgres"),
            "dbname": os.getenv("PGDATABASE", "rag"),
        }
        dsn = "host={host} port={port} user={user} password={password} dbname={dbname}".format(**conninfo)
        conn = psycopg.connect(dsn, autocommit=False)
    
    # Registra o adaptador pgvector para esta conexão
    register_vector(conn)
    return conn


def get_embedding_openai(text: str) -> List[float]:
    """
    Vetoriza o texto usando a API OpenAI via LangChain.
    Retorna um array de floats que será convertido para vector(1536) pelo pgvector.
    """
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY não encontrada no ambiente.")

    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        api_key=OPENAI_API_KEY
    )
    embedding = embeddings.embed_query(text)
    # Converter para lista de floats (pgvector.psycopg registra o adaptador automaticamente)
    return list(embedding)
