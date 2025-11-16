#!/bin/bash

# Script de teste para validar inicialização do banco de dados PostgreSQL + pgvector + schema
# Uso: bash db-init.sh  ou  ./db-init.sh
# Compatível com: Linux, macOS, Windows (WSL/Git Bash)

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Função para imprimir com cor
print_section() {
    echo -e "${GREEN}$1${NC}"
}

print_step() {
    echo -e "\n${CYAN}$1${NC}"
}

print_info() {
    echo -e "${YELLOW}$1${NC}"
}

print_error() {
    echo -e "${RED}$1${NC}"
}

# Verificar se docker-compose está disponível
if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
    print_error "❌ Erro: docker-compose não encontrado. Instale Docker e Docker Compose."
    exit 1
fi

# Se apenas 'docker' está disponível, usar 'docker compose' (versão mais recente)
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

print_section "=== Testando inicialização do PostgreSQL + pgvector + schema ==="

print_step "[1/4] Limpando containers e volumes anteriores..."
$DOCKER_COMPOSE down -v || true

print_step "[2/4] Iniciando containers..."
$DOCKER_COMPOSE up -d

print_step "[3/4] Aguardando conclusão dos bootstraps (30s)..."
sleep 30

print_step "[4/4] Validando criação de objetos..."

print_info "\n--- Status dos containers ---"
$DOCKER_COMPOSE ps

print_info "\n--- Logs do bootstrap_schema ---"
$DOCKER_COMPOSE logs bootstrap_schema

print_info "\n--- Verificando tabelas criadas ---"
docker exec postgres_rag psql -U postgres -d rag -c "\dt public.*"

print_info "\n--- Verificando índices criados ---"
docker exec postgres_rag psql -U postgres -d rag -c "\di public.*"

print_info "\n--- Verificando extensão vector ---"
docker exec postgres_rag psql -U postgres -d rag -c "SELECT * FROM pg_extension WHERE extname = 'vector';"

print_info "\n--- Verificando função search_documentos ---"
docker exec postgres_rag psql -U postgres -d rag -c "SELECT proname, pronargs FROM pg_proc WHERE proname = 'search_documentos';"

print_section "\n✅ Teste completo!"
