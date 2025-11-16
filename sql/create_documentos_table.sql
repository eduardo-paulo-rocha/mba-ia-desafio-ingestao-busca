-- create_documentos_table.sql
-- Script para criar a tabela `documentos` para armazenar chunks de PDF e embeddings usando pgvector.
-- Requisitos de ingestão (documentado aqui):
--  - chunk_size = 1000 caracteres
--  - overlap = 150 caracteres
--  - cada chunk deve ser convertido em embedding e armazenado em coluna tipo vector
--  - objetivo: permitir busca dos top-K mais relevantes (ex.: k=10)
-- OBS: Ajuste a dimensão do vetor (EMBEDDING_DIM) de acordo com o modelo de embeddings usado (ex.: 1536, 1024, 3072, etc.).

-- Assunção padrão: embedding dimension = 1536. Alterar se necessário.
\set EMBEDDING_DIM 1536

BEGIN;

-- Habilita a extensão pgvector (se ainda não estiver habilitada)
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabela principal
CREATE TABLE IF NOT EXISTS public.documentos (
    id BIGSERIAL PRIMARY KEY,
    documento_id TEXT,
    chunk_index INT NOT NULL,
    texto TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    texto_len INT GENERATED ALWAYS AS (char_length(texto)) STORED,
    page_start INT,
    page_end INT,
    content_hash TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    criado_em TIMESTAMPTZ DEFAULT now()
);

-- Garantia de unicidade por documento + chunk (opcional, útil para upserts/dedup)
CREATE UNIQUE INDEX IF NOT EXISTS uq_documento_chunk ON public.documentos (documento_id, chunk_index);

-- Índice ANN com ivfflat para busca rápida (ajuste lists conforme o volume de dados)
-- Recomendação: lists = sqrt(N) ~ ou experimentar valores entre 100-1000 conforme a cardinalidade.
CREATE INDEX IF NOT EXISTS idx_documentos_embedding_ivfflat
    ON public.documentos USING ivfflat (embedding vector_l2_ops)
    WITH (lists = 100);

-- Índice GIN em metadata para consultas por metadados
CREATE INDEX IF NOT EXISTS idx_documentos_metadata ON public.documentos USING gin (metadata);

COMMIT;

-- Exemplo de consulta para buscar os 10 itens mais próximos (k = 10):
-- Substitua :query_vector pela representação vetorial do texto de consulta.
-- Exemplo (psycopg3 / psycopg): execute a query com o parâmetro de tipo vector
-- SELECT id, documento_id, chunk_index, texto, metadata, embedding <-> :query_vector AS distance
-- FROM public.documentos
-- ORDER BY embedding <-> :query_vector
-- LIMIT 10;

-- Opcional: criar função que encapsula a busca (ajuste a dimensão se necessário)
CREATE OR REPLACE FUNCTION public.search_documentos(query_embedding vector(1536), k INT DEFAULT 10)
RETURNS TABLE(
    id BIGINT,
    documento_id TEXT,
    chunk_index INT,
    texto TEXT,
    metadata JSONB,
    distance FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT d.id, d.documento_id, d.chunk_index, d.texto, d.metadata, d.embedding <-> query_embedding AS distance
    FROM public.documentos d
    ORDER BY d.embedding <-> query_embedding
    LIMIT k;
END;
$$ LANGUAGE plpgsql STABLE;

-- Nota sobre dimensionamento e tuning:
--  - Ajuste vector(1536) para a dimensão usada pelos embeddings do seu modelo.
--  - Ajuste o parâmetro lists do índice ivfflat conforme o volume (mais listas -> buscas mais rápidas, mas custo de indexação maior).
--  - Para medidas de similaridade diferentes de L2, adapte a operação e o índice (pgvector provê operadores e opções).

-- Exemplo de inserção (parametrizada):
-- INSERT INTO public.documentos(documento_id, chunk_index, texto, embedding, page_start, page_end, content_hash, metadata)
-- VALUES ($1, $2, $3, $4, $5, $6, $7, $8);

-- FIM
