# Desafio MBA Engenharia de Software com IA - Full Cycle

## 📋 Propósito do Software

Este projeto é um **pipeline RAG (Retrieval-Augmented Generation)** completo que implementa:

1. **Ingestão**: Leitura de um arquivo PDF e armazenamento de seus dados em um banco PostgreSQL com a extensão pgVector para busca semântica.
2. **Busca & Resposta**: Interface de linha de comando (CLI) que permite ao usuário fazer perguntas e receber respostas baseadas exclusivamente no conteúdo do PDF ingestion, utilizando embeddings e LLM.

O sistema garante que as respostas sejam sempre fundamentadas no contexto do documento, sem utilizar conhecimento externo.

---

## 📁 Estrutura do Projeto

```
mba-ia-desafio-ingestao-busca/
├── src/
│   ├── ingest.py          # Pipeline de ingestão: lê PDF, vetoriza e salva no banco
│   ├── search.py          # Motor de busca semântica e geração de respostas
│   └── chat.py            # Interface CLI interativa para o usuário
├── sql/
│   └── create_documentos_table.sql  # Schema SQL com tabela e função de busca
├── scripts/
│   ├── db-init.ps1        # Script PowerShell para inicializar o ambiente (Windows)
│   └── db-init.sh         # Script Bash para inicializar o ambiente (Linux/macOS)
├── docker-compose.yml     # Orquestração: PostgreSQL + pgVector + bootstrap
├── requirements.txt       # Dependências Python
├── .env                   # Variáveis de ambiente (PDF_PATH, API keys, BD)
└── README.md              # Este arquivo
```

### Componentes Principais

| Arquivo | Propósito |
|---------|-----------|
| **`src/ingest.py`** | Lê PDF, extrai texto, divide em chunks, vetoriza com OpenAI Embeddings, e faz upsert no PostgreSQL. |
| **`src/search.py`** | Realiza busca semântica vetorial, monta prompt com contexto e chama a LLM (GPT) para gerar resposta. |
| **`src/chat.py`** | CLI interativa que captura perguntas do usuário e exibe respostas fornecidas pelo `search_prompt()`. |
| **`docker-compose.yml`** | Define serviços: PostgreSQL com pgVector, bootstrap para extensão e schema. |
| **`scripts/db-init.ps1`** | Script PowerShell que gerencia containers Docker (down, up, validação). Usar em **Windows**. |
| **`scripts/db-init.sh`** | Script Bash que gerencia containers Docker (down, up, validação). Usar em **Linux/macOS**. |
| **`sql/create_documentos_table.sql`** | DDL: cria tabela `documentos`, índice IVFFLAT e função `search_documentos()`. |

---

## 🚀 Configuração e Execução

### Fluxo de Inicialização

```mermaid
graph TD
    A["1️⃣ Executar Script de Inicialização<br/>Windows: db-init.ps1<br/>Linux/macOS: db-init.sh"] -->|Inicializa stack Docker| B["PostgreSQL + pgVector"]
    B -->|Extension criada| C["pgvector extension"]
    B -->|Schema carregado| D["Tabela documentos + Índices"]
    
    D --> E["2️⃣ Executar python src/ingest.py"]
    E -->|Lê PDF| F["Extrai Texto"]
    F -->|Divide em chunks| G["Chunking com overlap"]
    G -->|Gera embeddings| H["OpenAI Embeddings API"]
    H -->|Armazena| I["PostgreSQL + pgVector"]
    
    I --> J["3️⃣ Executar python src/chat.py"]
    J -->|Usuário digita pergunta| K["Pergunta do Usuário"]
    K -->|Vetoriza| L["OpenAI Embeddings API"]
    L -->|Busca semântica| M["search_documentos SQL function"]
    M -->|Recupera contexto| N["K-NN sobre embeddings"]
    N -->|Monta prompt| O["PROMPT + CONTEXTO"]
    O -->|Chamada LLM| P["OpenAI GPT API"]
    P -->|Responde baseado em contexto| Q["Resposta ao Usuário"]
```

---

## 📝 Descrição de Cada Etapa

### 1️⃣ Inicialização do Banco de Dados (`db-init.ps1`)

**Propósito**: Gerenciar ciclo de vida dos containers Docker que formam a infraestrutura do projeto.

**Ações realizadas**:
- ✅ Remove containers e volumes anteriores (`docker-compose down -v`)
- ✅ Inicia novos containers (`docker-compose up -d`)
  - **postgres**: Container PostgreSQL 17 com extensão pgVector pré-instalada
  - **bootstrap_vector_ext**: Cria extensão `vector` no banco
  - **bootstrap_schema**: Carrega o schema SQL (tabela `documentos` e função `search_documentos()`)
- ✅ Valida saúde dos serviços com health checks
- ✅ Exibe logs e status de inicialização para diagnóstico

**Resultado**: Banco de dados pronto com schema, índices e função de busca semântica operacionais.

---

### 2️⃣ Ingestão de PDFs (`python src/ingest.py`)

**Propósito**: Ler um arquivo PDF, processar seu conteúdo e armazená-lo como embeddings vetoriais no banco de dados.

**Ações realizadas**:

1. **Leitura do PDF** (`read_pdf_pages()`)
   - Extrai texto de todas as páginas usando `pypdf`

2. **Chunking Inteligente** (`chunk_text_with_pages()`)
   - Divide o texto em chunks de ~1000 caracteres com 150 de sobreposição
   - Rastreia página de origem de cada chunk

3. **Vetorização** (`get_embedding_openai()`)
   - Converte cada chunk em embedding 1536-dimensional via OpenAI Embeddings API
   - Gera por lote para otimizar requisições

4. **Armazenamento** (`upsert_chunks()`)
   - Salva em tabela `documentos` com:
     - `texto`: conteúdo do chunk
     - `embedding`: vetor para busca semântica
     - `content_hash`: hash SHA256 para deduplicação
     - `metadata`: JSON com info de origem e char offsets
   - Usa UPSERT para atualizar documentos já ingeridos

**Resultado**: Base de dados vetorial pronta para consultas semânticas.

---

### 3️⃣ Chat Interativo (`python src/chat.py`)

**Propósito**: Fornecer interface CLI para o usuário fazer perguntas e receber respostas baseadas no PDF.

**Fluxo de Resposta** (`search_prompt()`):

1. **Validação**: Verifica se pergunta é válida e não vazia

2. **Vetorização da Pergunta** (`get_embedding_openai()`)
   - Transforma pergunta em embedding 1536-dimensional

3. **Busca Semântica** (`search_documents()`)
   - Executa função SQL `search_documentos()` no PostgreSQL
   - Usa distância L2 (cosine similarity) em índice IVFFLAT
   - Retorna top-10 chunks mais relevantes

4. **Construção do Prompt**
   - Formata contexto recuperado
   - Monta prompt com regras estritas:
     - ✅ Responda **APENAS** baseado no CONTEXTO
     - ✅ Se informação não está no contexto, retorne: *"Não tenho informações necessárias para responder sua pergunta."*
     - ✅ Nunca invente ou use conhecimento externo

5. **Chamada da LLM** (`call_llm()`)
   - Envia prompt a OpenAI GPT (modelo configurável)
   - Recebe resposta garantidamente fundamentada nos documentos

6. **Exibição**: Mostra resposta ao usuário no terminal

**Exemplo de Interação**:
```
Você: Qual é o tema principal do documento?
[PROCESSANDO...]
Assistente: [Resposta baseada no contexto do PDF]
```

---

## 🛠️ Pré-requisitos

- **Python 3.10+**
- **Docker** e **Docker Compose**
- **Variáveis de Ambiente** (`.env`):
  ```env
  PDF_PATH=./data/documento.pdf
  OPENAI_API_KEY=sk-...
  OPENAI_EMBEDDING_MODEL=text-embedding-3-small
  OPENAI_LLM_MODEL=gpt-4o-mini
  DATABASE_URL=postgresql://postgres:postgres@localhost:5432/rag
  ```

---

## ⚙️ Como Executar

### Passo 1: Instalar Dependências
```powershell
pip install -r requirements.txt
```

### Passo 2: Inicializar Infraestrutura

**Windows (PowerShell)**:
```powershell
.\scripts\db-init.ps1
```

**Linux/macOS (Bash)**:
```bash
bash ./scripts/db-init.sh
```
ou
```bash
./scripts/db-init.sh
```

### Passo 3: Ingerir PDF
```powershell
$env:PDF_PATH = './data/meu_documento.pdf'
python .\src\ingest.py
```

### Passo 4: Iniciar Chat
```powershell
python .\src\chat.py
```

Digite perguntas e pressione Enter. Use `sair`, `exit` ou `quit` para encerrar.

---

## 📚 Tecnologias Utilizadas

- **Python**: Linguagem principal
- **LangChain**: Orquestração de embeddings e LLM
- **PostgreSQL + pgVector**: Banco de dados vetorial
- **OpenAI API**: Embeddings e LLM
- **psycopg**: Driver PostgreSQL nativo para Python
- **pypdf**: Extração de texto de PDFs
- **Docker & Docker Compose**: Containerização e orquestração

---

## 🔒 Segurança & Garantias

- ✅ **Respostas Verificadas**: Toda resposta é gerada com contexto recuperado do PDF
- ✅ **Nenhum Conhecimento Externo**: Modelo é instruído a recusar perguntas sem contexto
- ✅ **Rastreabilidade**: Cada resposta inclui referência ao chunk (Doc ID, Chunk Index, Páginas)
- ✅ **Deduplicação**: Hashes SHA256 evitam ingestão duplicada