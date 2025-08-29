#!/bin/bash

# Script de Teste da API - Visão Computacional
# ============================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCESSO]${NC} $1"
}

error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

# URL base da API
API_URL="http://localhost:8000"

# Verificar se a API está rodando
check_api() {
    log "Verificando se a API está rodando..."
    
    if curl -s "$API_URL/health" > /dev/null; then
        success "API está rodando"
        return 0
    else
        error "API não está respondendo em $API_URL"
        echo "Execute: docker-compose up -d vision-api"
        exit 1
    fi
}

# Fazer login e obter token
login() {
    log "Fazendo login..."
    
    response=$(curl -s -X POST "$API_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"username":"admin","password":"admin123"}')
    
    if echo "$response" | grep -q "access_token"; then
        TOKEN=$(echo "$response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
        success "Login realizado com sucesso"
        echo "Token: ${TOKEN:0:20}..."
        return 0
    else
        error "Falha no login"
        echo "Resposta: $response"
        exit 1
    fi
}

# Testar health check
test_health() {
    log "Testando endpoint /health..."
    
    response=$(curl -s "$API_URL/health")
    status=$(echo "$response" | grep -o '"status":"[^"]*' | cut -d'"' -f4)
    
    if [ "$status" = "healthy" ]; then
        success "Health check OK"
        echo "$response" | head -3
    else
        warning "Health check com problemas"
        echo "$response"
    fi
}

# Testar status da visão
test_vision_status() {
    log "Testando status do sistema de visão..."
    
    response=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/vision/status")
    
    if echo "$response" | grep -q '"status"'; then
        success "Status da visão obtido"
        echo "$response"
    else
        error "Falha ao obter status da visão"
        echo "$response"
    fi
}

# Testar processamento de imagem (simulado)
test_image_processing() {
    log "Testando processamento de imagem (simulado)..."
    
    # Imagem base64 mínima (1x1 pixel)
    BASE64="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD//2Q="
    
    response=$(curl -s -X POST "$API_URL/vision/process" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"image_request\": {
                \"image_data\": \"$BASE64\"
            },
            \"save_results\": false
        }")
    
    if echo "$response" | grep -q '"success"'; then
        success "Processamento de imagem OK"
        echo "$response" | head -5
    else
        error "Falha no processamento de imagem"
        echo "$response"
    fi
}

# Testar métricas
test_metrics() {
    log "Testando endpoint de métricas..."
    
    response=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/monitoring/metrics")
    
    if echo "$response" | grep -q '"timestamp"'; then
        success "Métricas obtidas"
        echo "$response" | head -3
    else
        warning "Métricas não disponíveis (normal em desenvolvimento)"
        echo "$response"
    fi
}

# Testar documentação Swagger
test_docs() {
    log "Verificando documentação Swagger..."
    
    if curl -s "$API_URL/docs" | grep -q "Swagger"; then
        success "Swagger UI disponível em $API_URL/docs"
    else
        warning "Swagger UI não disponível"
        echo "Certifique-se de que DEBUG=true está configurado"
    fi
}

# Função principal
main() {
    echo "🧪 Testando API de Visão Computacional"
    echo "======================================"
    echo
    
    check_api
    echo
    
    login
    echo
    
    test_health
    echo
    
    test_vision_status
    echo
    
    test_image_processing
    echo
    
    test_metrics
    echo
    
    test_docs
    echo
    
    success "🎉 Testes concluídos!"
    echo
    echo "📋 Próximos passos:"
    echo "  1. Acesse $API_URL/docs para testar visualmente"
    echo "  2. Para habilitar pipeline real: docker-compose build vision-api && docker-compose up -d vision-api"
    echo "  3. Para testar com imagem real: substitua BASE64 no script"
}

# Executar função principal
main "$@"
