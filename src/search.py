import os
import psycopg
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI
from pgvector.psycopg import register_vector

load_dotenv()

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

# Configs (env overrides)
DATABASE_URL = os.getenv("DATABASE_URL")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_MODEL = os.getenv("OPENAI_LLM_MODEL", "gpt-5-nano")

K_RESULTS = 10  # número de resultados mais relevantes a recuperar


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


def get_embedding_openai(text: str) -> list:
    """
    Vetoriza o texto usando a API OpenAI.
    Retorna um array de floats que será convertido para vector(1536) pelo pgvector.
    """
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY não encontrada no ambiente.")

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    embedding = response.data[0].embedding
    # Converter para lista de floats (pgvector.psycopg registra o adaptador automaticamente)
    return list(embedding)


def search_documents(conn: psycopg.Connection, query_embedding: list, k: int = K_RESULTS) -> list:
    """
    Busca os k documentos mais relevantes usando a função SQL plpgsql.
    
    O embedding é convertido para string no formato pgvector antes de ser enviado.
    A função search_documentos no banco recebe como vector(1536).
    
    Args:
        conn: Conexão psycopg com pgvector registrado
        query_embedding: Lista de floats do embedding
        k: Número de resultados a retornar (padrão: 10)
    
    Returns:
        Lista de tuplas com (id, documento_id, chunk_index, texto, metadata, distance)
    """
    # Converter lista para formato pgvector: "[1.0, 2.0, 3.0, ...]"
    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
    
    sql = "SELECT * FROM public.search_documentos(%s::vector(1536), %s);"
    
    with conn.cursor() as cur:
        cur.execute(sql, (embedding_str, k))
        results = cur.fetchall()
    
    return results


def format_context(search_results: list) -> str:
    """Formata os resultados da busca em contexto para o prompt."""
    if not search_results:
        return ""
    
    context_parts = []
    for result in search_results:
        # result: (id, documento_id, chunk_index, texto, metadata, distance)
        doc_id = result[1]
        chunk_idx = result[2]
        texto = result[3]
        context_parts.append(f"[Doc: {doc_id}, Chunk: {chunk_idx}]\n{texto}")
    
    return "\n\n---\n\n".join(context_parts)


def call_llm(prompt: str) -> str:
    """
    Chama o modelo LLM com o prompt montado.
    
    Note: gpt-5-nano requer temperature=1 (default).
    Por isso, não especificamos temperatura para manter compatibilidade com diferentes modelos.
    """
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY não encontrada no ambiente.")

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ]
        # Sem especificar temperature para usar o padrão do modelo
    )
    
    return response.choices[0].message.content


def search_prompt(question: Optional[str] = None) -> str:
    """
    Realiza busca semântica nos dados vetorizados e retorna a resposta da LLM.
    
    Processo:
    1. Vetoriza a pergunta usando OpenAI Embeddings
    2. Busca os 10 resultados mais relevantes no banco vetorial
    3. Monta o prompt com o contexto recuperado
    4. Chama a LLM (GPT) com o prompt
    5. Retorna a resposta ao usuário
    
    Args:
        question: A pergunta do usuário (str). Obrigatório.
    
    Returns:
        str: A resposta da LLM ou mensagem de erro.
    
    Raises:
        ValueError: Se question for None ou vazio
        Exception: Erros de conexão com banco ou API
    """
    try:
        # Validar pergunta
        if not question or not isinstance(question, str):
            raise ValueError("A pergunta deve ser uma string não-vazia.")
        
        question = question.strip()
        if not question:
            raise ValueError("A pergunta não pode estar vazia.")
        
        print(f"[INFO] Pergunta recebida: {question}")
        
        # Etapa 1: Vetorizar a pergunta
        print(f"[INFO] Vetorizando pergunta...")
        query_embedding = get_embedding_openai(question)
        print(f"[INFO] Embedding gerado com sucesso.")
        
        # Etapa 2: Buscar documentos mais relevantes
        print(f"[INFO] Buscando {K_RESULTS} documentos mais relevantes no banco de dados...")
        conn = get_db_conn()
        try:
            search_results = search_documents(conn, query_embedding, k=K_RESULTS)
            
            if not search_results:
                print("[WARN] Nenhum documento encontrado.")
                return "Não tenho informações necessárias para responder sua pergunta."
            
            print(f"[INFO] {len(search_results)} documentos encontrados.")
            
            # Etapa 3: Formatar contexto e montar prompt
            print(f"[INFO] Formatando contexto...")
            contexto = format_context(search_results)
            
            prompt_final = PROMPT_TEMPLATE.format(
                contexto=contexto,
                pergunta=question
            )
            
            # Etapa 4: Chamar a LLM
            print(f"[INFO] Chamando LLM ({LLM_MODEL})...")
            resposta = call_llm(prompt_final)
            
            print(f"[INFO] Resposta gerada com sucesso.")
            return resposta
        
        finally:
            conn.close()
    
    except Exception as e:
        print(f"[ERRO] Falha ao processar pergunta: {e}")
        raise