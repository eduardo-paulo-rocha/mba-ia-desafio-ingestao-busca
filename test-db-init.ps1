# Script de teste para validar inicialização do banco de dados PostgreSQL + pgvector + schema
# Uso: .\test-db-init.ps1

[CmdletBinding()]
param()

Write-Host "=== Testando inicialização do PostgreSQL + pgvector + schema ===" -ForegroundColor Green

Write-Host "`n[1/4] Limpando containers e volumes anteriores..." -ForegroundColor Cyan
docker-compose down -v

Write-Host "`n[2/4] Iniciando containers..." -ForegroundColor Cyan
docker-compose up -d

Write-Host "`n[3/4] Aguardando conclusão dos bootstraps (30s)..." -ForegroundColor Cyan
Start-Sleep -Seconds 30

Write-Host "`n[4/4] Validando criação de objetos..." -ForegroundColor Cyan

Write-Host "`n--- Status dos containers ---" -ForegroundColor Yellow
docker-compose ps

Write-Host "`n--- Logs do bootstrap_schema ---" -ForegroundColor Yellow
docker-compose logs bootstrap_schema

Write-Host "`n--- Verificando tabelas criadas ---" -ForegroundColor Yellow
docker exec postgres_rag psql -U postgres -d rag -c "\dt public.*"

Write-Host "`n--- Verificando índices criados ---" -ForegroundColor Yellow
docker exec postgres_rag psql -U postgres -d rag -c "\di public.*"

Write-Host "`n--- Verificando extensão vector ---" -ForegroundColor Yellow
docker exec postgres_rag psql -U postgres -d rag -c "SELECT * FROM pg_extension WHERE extname = 'vector';"

Write-Host "`n--- Verificando função search_documentos ---" -ForegroundColor Yellow
docker exec postgres_rag psql -U postgres -d rag -c "SELECT proname, pronargs FROM pg_proc WHERE proname = 'search_documentos';"

Write-Host "`n✅ Teste completo!" -ForegroundColor Green
