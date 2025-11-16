# Inicialização do Banco de Dados - Guia Rápido

## Resumo da Solução

O `docker-compose.yml` foi atualizado para **criar automaticamente todos os objetos de banco de dados** (extensão pgvector, tabelas, índices e função) na primeira inicialização.

## Como Usar

### 1️⃣ Iniciar a pilha completa

```powershell
docker-compose up -d
```

Este comando inicia:
- ✅ Container PostgreSQL com pgvector
- ✅ Bootstrap da extensão vector
- ✅ Bootstrap do schema (tabelas, índices, função)

### 2️⃣ Verificar status

```powershell
# Ver se todos os serviços estão rodando
docker-compose ps

# Ver logs da inicialização do schema
docker-compose logs bootstrap_schema
```

### 3️⃣ Validar criação dos objetos

```powershell
# Verificar tabelas
docker exec postgres_rag psql -U postgres -d rag -c "\dt public.*"

# Verificar índices
docker exec postgres_rag psql -U postgres -d rag -c "\di public.*"

# Verificar extensão vector
docker exec postgres_rag psql -U postgres -d rag -c "SELECT * FROM pg_extension WHERE extname = 'vector';"

# Verificar função de busca
docker exec postgres_rag psql -U postgres -d rag -c "\df+ search_documentos"
```

## ⚙️ O que foi modificado

### Arquivo: `docker-compose.yml`

Adicionado novo serviço `bootstrap_schema`:

```yaml
bootstrap_schema:
  image: pgvector/pgvector:pg17
  depends_on:
    bootstrap_vector_ext:
      condition: service_completed_successfully
  volumes:
    - ./sql:/sql
  entrypoint: ["/bin/sh", "-c"]
  command: >
    PGPASSWORD=postgres
    psql "postgresql://postgres@postgres:5432/rag" -v ON_ERROR_STOP=1
    -f /sql/create_documentos_table.sql
  restart: "no"
```

**O que faz:**
- Aguarda conclusão bem-sucedida do `bootstrap_vector_ext`
- Monta o diretório `./sql` como volume de leitura
- Executa `create_documentos_table.sql` automaticamente
- Não reinicia (permite que Docker Compose saiba quando terminou)

## ⚠️ Cuidados Importantes

### 1. Ordem de Execução
A ordem é **automática** e garantida:
```
postgres (healthcheck ok) 
    ↓
bootstrap_vector_ext (CREATE EXTENSION)
    ↓
bootstrap_schema (CREATE TABLE, INDEX, FUNCTION)
```

### 2. Idempotência
O script `create_documentos_table.sql` usa `IF NOT EXISTS` em todos os objetos:
- ✅ Seguro executar múltiplas vezes
- ✅ Não gera erros se objetos já existem
- ✅ Ideal para reinicializações

### 3. Volume do SQL
A pasta `./sql` é montada como **volume de leitura** (`ro` é implícito):
- ✅ Arquivo `create_documentos_table.sql` deve existir localmente
- ✅ Mudanças no arquivo local são refletidas no container
- ✅ Container não pode modificar arquivos

### 4. Reset do Banco

Se precisar limpar e recomeçar:

```powershell
# Para tudo e remove volumes
docker-compose down -v

# Inicia novamente (schema será recriado)
docker-compose up -d
```

### 5. Senha Hardcoded

A senha está hardcoded no compose: `POSTGRES_PASSWORD: postgres`

**Para desenvolvimento local:** OK

**Para produção:**
- Use Docker secrets
- Use arquivo `.env` externo
- Use variáveis de ambiente

Exemplo com `.env`:
```bash
# .env
POSTGRES_PASSWORD=senhaSegura123
```

```yaml
# docker-compose.yml
environment:
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

## 📝 Troubleshooting

### Container `bootstrap_schema` não inicia

```powershell
# Ver logs completos
docker-compose logs bootstrap_schema

# Verificar se bootstrap_vector_ext terminou com sucesso
docker-compose logs bootstrap_vector_ext
```

### Tabelas não foram criadas

```powershell
# Acessar o banco manualmente
docker exec -it postgres_rag psql -U postgres -d rag

# Dentro do psql, verificar:
rag=# \dt public.*
rag=# SELECT * FROM pg_tables WHERE schemaname = 'public';
```

### Erro: "arquivo não encontrado"

```powershell
# Verificar se o arquivo existe
Get-ChildItem -Path "./sql"

# Verificar caminho relativo
Get-Location
```

## 🔗 Próximos Passos

1. **Testar conexão da aplicação**: 
   - Ver `src/ingest.py` e `src/search.py` para confirmar que usam a conexão correta

2. **Ajustar dimensão de embedding** (se necessário):
   - Padrão: `vector(1536)` (para modelos como OpenAI)
   - Se usar outro modelo, editar `create_documentos_table.sql` antes de iniciar

3. **Rodar script de teste** (opcional):
   ```powershell
   .\test-db-init.ps1
   ```

## 📚 Outras Abordagens Possíveis

Veja o arquivo **`DOCKER_SETUP.md`** para uma comparação completa de:
- ✅ **Bootstrap Dedicado** (implementado aqui)
- Script de inicialização (init-db.sh)
- Migrations com Alembic
- Manual local

---

**Dúvidas?** Consulte `DOCKER_SETUP.md` para mais detalhes técnicos.
