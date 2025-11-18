# GEMINI.md - Instruções para Interação com o Projeto

## Visão Geral do Projeto

Este é um projeto de **pipeline RAG (Retrieval-Augmented Generation)**, construído em Python, que permite a ingestão e a busca de informações em documentos PDF. O sistema é projetado para fornecer respostas a perguntas do usuário baseadas exclusivamente no conteúdo do documento fornecido, sem o uso de conhecimento externo.

A arquitetura do projeto é composta por três componentes principais:

1.  **Ingestão de Dados (`src/ingest.py`):** Um script que lê um arquivo PDF, o divide em `chunks` de texto, gera `embeddings` vetoriais para cada `chunk` usando a API da OpenAI e, em seguida, armazena esses dados em um banco de dados PostgreSQL com a extensão `pgvector`.

2.  **Busca e Geração de Respostas (`src/search.py`):** Um motor de busca que, dada uma pergunta do usuário, a vetoriza e busca os `chunks` de texto mais relevantes no banco de dados. Em seguida, ele constrói um `prompt` com o contexto recuperado e o envia para um modelo de linguagem (LLM) da OpenAI para gerar uma resposta.

3.  **Interface de Chat (`src/chat.py`):** Uma interface de linha de comando (CLI) que permite ao usuário interagir com o sistema, fazendo perguntas e recebendo as respostas geradas.

## Tecnologias e Dependências

*   **Linguagem:** Python 3.10+
*   **Banco de Dados:** PostgreSQL com a extensão `pgvector` para busca semântica.
*   **Orquestração:** Docker e Docker Compose para gerenciar os contêineres do banco de dados.
*   **Bibliotecas Principais:**
    *   `langchain`: Para orquestrar a interação com os modelos de `embedding` e LLM.
    *   `openai`: Para gerar os `embeddings` e as respostas.
    *   `psycopg`: Para a conexão com o banco de dados PostgreSQL.
    *   `pypdf`: Para a extração de texto de arquivos PDF.
    *   `python-dotenv`: Para o gerenciamento de variáveis de ambiente.

## Como Construir e Executar o Projeto

### Pré-requisitos

*   Python 3.10+
*   Docker e Docker Compose
*   Chave de API da OpenAI

### 1. Instalação das Dependências

Para instalar as dependências do Python, execute o seguinte comando:

```bash
pip install -r requirements.txt
```

### 2. Configuração das Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto e adicione as seguintes variáveis:

```env
PDF_PATH=./document.pdf
OPENAI_API_KEY=sua-chave-de-api-da-openai
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_LLM_MODEL=gpt-4o-mini
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/rag
```

### 3. Inicialização da Infraestrutura

Para iniciar o banco de dados PostgreSQL com o `pgvector`, execute o script de inicialização apropriado para o seu sistema operacional:

**Windows (PowerShell):**

```powershell
.\scripts\db-init.ps1
```

**Linux/macOS (Bash):**

```bash
./scripts/db-init.sh
```

### 4. Ingestão do Documento

Para ingerir o documento PDF no banco de dados, execute o script `ingest.py`:

```bash
python src/ingest.py
```

### 5. Interação com o Chat

Após a ingestão do documento, você pode iniciar o chat para fazer perguntas:

```bash
python src/chat.py
```

## Convenções de Desenvolvimento

*   **Estilo de Código:** O projeto segue o estilo de código PEP 8, com o uso de `type hints` para a verificação de tipos.
*   **Testes:** O projeto não possui uma suíte de testes automatizados. Para testar, é necessário executar os scripts manualmente e verificar os resultados.
*   **Contribuições:** Para contribuir com o projeto, siga o `forking workflow`:
    1.  Faça um `fork` do repositório.
    2.  Crie um `branch` para a sua `feature` ou correção.
    3.  Implemente as suas alterações.
    4.  Envie um `pull request` com uma descrição detalhada das suas alterações.
