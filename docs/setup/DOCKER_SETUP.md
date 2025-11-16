# Estratégias de Inicialização do Banco de Dados com Docker Compose

## 1. Abordagem Recomendada: Serviço Bootstrap Dedicado ✅ (IMPLEMENTADA)

### Como funciona
O `docker-compose.yml` agora inclui um terceiro serviço (`bootstrap_schema`) que:
1. Aguarda o sucesso de `bootstrap_vector_ext` (que cria a extensão vector)
2. Monta o diretório `./sql` como volume leitura-apenas
3. Executa o script `create_documentos_table.sql` via `psql`

### Comando para iniciar
```powershell
docker-compose up -d
```

Isso inicia os três serviços em ordem:
- `postgres` (aguarda healthcheck)
- `bootstrap_vector_ext` (após postgres estar saudável)
- `bootstrap_schema` (após vector_ext completar com sucesso)

### Verificar status
```powershell
# Ver logs de inicialização
docker-compose logs -f bootstrap_schema

# Verificar se as tabelas foram criadas
docker exec postgres_rag psql -U postgres -d rag -c "\dt public.*"
```

### ✅ Vantagens
- **Inicialização completa**: Toda a infraestrutura (extensão + tabelas + índices) é criada automaticamente
- **Idempotente**: O script usa `IF NOT EXISTS`, é seguro executar múltiplas vezes
- **Rastreável**: Logs do Docker mostram exatamente o que foi feito
- **Sem estado manual**: Não precisa de comandos manuais adicionais
- **Ideal para CI/CD**: Ótimo para pipelines de integração contínua

### ⚠️ Cuidados necessários

1. **Ordem de dependências**: Certifique-se de que `bootstrap_vector_ext` está com `restart: "no"`
   - Se restart fosse `always`, o `bootstrap_schema` nunca iniciaria (estaria sempre esperando)

2. **Permissões de volume**: O diretório `./sql` deve estar acessível ao container
   - Em Windows com WSL2, geralmente funciona sem problemas

3. **Caracteres especiais em SQL**: O script SQL usa sintaxe PostgreSQL padrão
   - A variável `\set EMBEDDING_DIM 1536` não é interpolada, mas funciona se usada em contextos compatíveis
   - Se precisar dessa variável, use parametrização na aplicação

4. **Idempotência**: Sempre use `IF NOT EXISTS` para tabelas, índices e extensões
   - Permite reinicialização sem erros

5. **Senha do container**: Está hardcoded em `POSTGRES_PASSWORD`
   - Em produção, use secrets do Docker Swarm ou arquivos `.env` externo

---

## 2. Alternativa: Script de Inicialização (init-db.sh)

### Como funciona
Criar um arquivo `init-db.sh` que roda automaticamente quando o container inicia.

### Implementação
```bash
# init-db.sh
#!/bin/bash
set -e

echo "Criando extensão pgvector..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -c "CREATE EXTENSION IF NOT EXISTS vector;"

echo "Criando schema..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f /docker-entrypoint-initdb.d/create_documentos_table.sql
```

Atualizar `docker-compose.yml`:
```yaml
postgres:
  image: pgvector/pgvector:pg17
  volumes:
    - ./sql:/docker-entrypoint-initdb.d
    - postgres_data:/var/lib/postgresql/data
```

### ✅ Vantagens
- Mais simples: Menos serviços no compose
- Nativo do PostgreSQL: Usa o mecanismo padrão de inicialização
- Menor overhead: Uma única imagem executa tudo

### ❌ Desvantagens
- Menos controle: Scripts no diretório `/docker-entrypoint-initdb.d` são executados automaticamente
- Difícil de reiniciar: Se precisar limpar, tem que dropar volumes
- Menos rastreável: Logs são misturados com inicialização do postgres
- Sem verificação de saúde: Não há garantia de qual script rodou com sucesso

---

## 3. Alternativa: Migrations em Python (Alembic)

### Como funciona
Usar uma ferramenta como Alembic para versionar e aplicar mudanças de schema.

### Implementação
```python
# migrations/versions/001_create_documentos.py
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        'documentos',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('documento_id', sa.String),
        sa.Column('chunk_index', sa.Integer),
        sa.Column('texto', sa.String),
        sa.Column('embedding', Vector(1536)),
        # ... mais colunas
    )
```

Executar na inicialização:
```python
# src/init_db.py
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from alembic.operations import Operations

def init_db():
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))
    command.upgrade(alembic_cfg, "head")
```

### ✅ Vantagens
- Versionado: Histórico completo de mudanças
- Reversível: Pode fazer downgrade (`alembic downgrade`)
- Integrado com código: Migrations em Python, não SQL puro
- Ideal para evolução: Fácil adicionar novas tabelas/colunas

### ❌ Desvantagens
- Mais complexo: Requer configuração de Alembic
- Mais dependências: Adiciona `alembic`, `sqlalchemy`
- Overhead inicial: Mais código para manutenção

---

## 4. Alternativa: Script Manual Local

### Como funciona
Executar manualmente após `docker-compose up`:

```powershell
docker-compose up -d
Start-Sleep -Seconds 10
docker exec postgres_rag psql -U postgres -d rag -f ./sql/create_documentos_table.sql
```

### ✅ Vantagens
- Simples: Sem mudanças no Docker Compose
- Controle total: Você decide quando aplicar
- Flexível: Fácil adicionar validações antes de executar

### ❌ Desvantagens
- Manual: Requer lembrar de rodar o script
- Erro-prone: Fácil esquecer em deployments
- Não é reproduzível: Difícil em CI/CD
- Estado inconsistente: Pode deixar o banco parcialmente inicializado

---

## Matriz de Comparação

| Critério | Bootstrap Dedicado | init-db.sh | Alembic | Manual |
|----------|------------------|-----------|---------|--------|
| **Automático** | ✅ Sim | ✅ Sim | ✅ Sim | ❌ Não |
| **Idempotente** | ✅ Sim | ⚠️ Sim* | ✅ Sim | ⚠️ Sim* |
| **Versionado** | ❌ Não | ❌ Não | ✅ Sim | ❌ Não |
| **Reversível** | ❌ Não | ❌ Não | ✅ Sim | ❌ Não |
| **Complexidade** | 🟢 Baixa | 🟢 Baixa | 🟠 Média | 🟢 Baixa |
| **CI/CD Friendly** | ✅ Excelente | ✅ Bom | ✅ Excelente | ❌ Ruim |
| **Logs claros** | ✅ Sim | ⚠️ Misturados | ✅ Sim | ⚠️ Depende |

*Com `IF NOT EXISTS`, mas requer limpeza manual de volumes para reset total.

---

## Recomendação Final

**Use a Abordagem 1 (Bootstrap Dedicado)** para este projeto porque:

1. ✅ Projeto é **POC** (prova de conceito) → não precisa de versionamento completo
2. ✅ Schema é **estável** → não muda frequentemente
3. ✅ Ótimo para **desenvolvimento local**
4. ✅ Funciona bem em **CI/CD**
5. ✅ **Sem overhead** de dependências adicionais

Migraçao para **Alembic** apenas se:
- Schema precisar evoluir frequentemente
- Precisar fazer rollbacks
- Tiver múltiplos ambientes (dev, staging, prod)

---

## Próximos Passos

1. Teste a inicialização:
   ```powershell
   docker-compose down -v  # Remove volumes anteriores
   docker-compose up -d
   docker-compose logs bootstrap_schema  # Verifique sucesso
   ```

2. Valide as tabelas:
   ```powershell
   docker exec postgres_rag psql -U postgres -d rag -c "\dt public.*"
   docker exec postgres_rag psql -U postgres -d rag -c "\di public.*"
   ```

3. Teste a função de busca:
   ```powershell
   docker exec postgres_rag psql -U postgres -d rag -c "SELECT * FROM pg_proc WHERE proname = 'search_documentos';"
   ```
