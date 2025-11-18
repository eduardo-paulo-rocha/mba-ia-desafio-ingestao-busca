# Otimizando o Uso do Gemini CLI no Projeto

Este documento fornece instruções sobre como otimizar a utilização do Gemini CLI neste projeto, cobrindo desde a configuração inicial até o uso avançado e benchmarking.

## Configuração do Modelo Gemini

A configuração do Gemini é feita através de variáveis de ambiente. Crie um arquivo `.env` na raiz do projeto e adicione as seguintes variáveis:

```env
OPENAI_API_KEY=sk-...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_LLM_MODEL=gpt-4o-mini
```

### Usando o Gemini 2.0 Flash via OpenRouter

Para avaliações e benchmarks, você pode configurar o projeto para usar o `Gemini 2.0 Flash` através do OpenRouter. Isso permite um controle mais granular sobre os custos e modelos.

**Exemplo de configuração em Python:**

```python
def setup_gemini_config():
    """
    Cria uma configuração de avaliação customizada usando o Gemini 2.0 Flash via OpenRouter.
    """
    evaluation_config = {
        "model_name": "google/gemini-2.0-flash-001",  # Formato OpenRouter para Gemini
        "provider": "openai_endpoint",  # Usa o OpenRouter como endpoint
        "openai_endpoint_url": "https://openrouter.ai/api/v1",
        "temperature": 0,  # Temperatura zero para avaliações consistentes
    }

    print(f"Usando Gemini 2.0 Flash para avaliação: {evaluation_config}")
    return evaluation_config
```

## Ingestão de Documentos

O script `ingest.py` é responsável por ler, processar e armazenar o conteúdo de um arquivo PDF no banco de dados vetorial.

### Como Executar a Ingestão

1.  **Defina o caminho do PDF:**
    Aponte a variável de ambiente `PDF_PATH` para o local do seu arquivo.

    ```powershell
    $env:PDF_PATH = './data/meu_documento.pdf'
    ```

2.  **Execute o script:**

    ```powershell
    python .\src\ingest.py
    ```

O script irá:
- Ler o PDF do caminho especificado.
- Dividir o texto em `chunks` de aproximadamente 1000 caracteres.
- Gerar `embeddings` para cada `chunk` usando o modelo da OpenAI.
- Armazenar os `chunks` e `embeddings` no PostgreSQL.

## Interagindo com o Chat

Após a ingestão, inicie o chat para fazer perguntas sobre o conteúdo do documento.

```powershell
python .\src\chat.py
```

O sistema irá:
1.  Vetorizar sua pergunta.
2.  Buscar os `chunks` mais relevantes no banco de dados.
3.  Construir um `prompt` com o contexto recuperado.
4.  Chamar o modelo de linguagem (LLM) para gerar uma resposta baseada **exclusivamente** no contexto.

## Configurações Avançadas

### Trocando o Modelo de Linguagem

Você pode alterar o modelo de LLM usado para geração de respostas modificando a variável `OPENAI_LLM_MODEL` no seu arquivo `.env`.

**Exemplo:**

```env
# Modelo padrão
OPENAI_LLM_MODEL=gpt-4o-mini

# Modelo alternativo (mais poderoso)
# OPENAI_LLM_MODEL=gpt-4
```

### Benchmarking e Avaliação

O diretório `examples` (não presente neste projeto, mas como referência) contém scripts para executar benchmarks com os modelos Gemini.

**Exemplo de uso:**

```bash
# Executa com configurações padrão
python run_gemini_benchmark_fixed.py

# Executa com um número customizado de exemplos
python run_gemini_benchmark_fixed.py --examples 5
```

Esses scripts são úteis para avaliar a performance e o custo de diferentes modelos Gemini em suas tarefas específicas.
