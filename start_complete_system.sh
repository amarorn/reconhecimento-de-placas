#!/bin/bash

# Script para Iniciar Sistema Completo - Visão Computacional
# =========================================================

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

# Verificar Docker
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        error "Docker não está rodando"
        exit 1
    fi
    success "Docker verificado"
}

# Parar serviços existentes
stop_services() {
    log "Parando serviços existentes..."
    docker-compose down --remove-orphans 2>/dev/null || true
    success "Serviços parados"
}

# Construir imagens
build_images() {
    log "Construindo imagens..."
    
    # API
    docker-compose build vision-api
    success "Imagem da API construída"
    
    # Interface
    docker-compose build vision-interface
    success "Imagem da interface construída"
}

# Iniciar serviços
start_services() {
    log "Iniciando serviços completos..."
    
    # Iniciar serviços essenciais
    docker-compose up -d \
        postgres \
        redis \
        vision-api \
        vision-interface
    
    success "Serviços iniciados"
}

# Verificar saúde dos serviços
check_health() {
    log "Verificando saúde dos serviços..."
    
    # Aguardar serviços ficarem prontos
    sleep 15
    
    # API
    if curl -s http://localhost:8000/health > /dev/null; then
        success "API está saudável"
    else
        warning "API ainda não está respondendo"
    fi
    
    # Interface
    if curl -s http://localhost:3000/health > /dev/null; then
        success "Interface está saudável"
    else
        warning "Interface ainda não está respondendo"
    fi
}

# Mostrar informações
show_info() {
    echo
    echo -e "${GREEN}🎉 Sistema Completo Iniciado!${NC}"
    echo "=" * 40
    echo
    echo "📱 INTERFACES DISPONÍVEIS:"
    echo "  🖥️  Interface Web:     http://localhost:3000"
    echo "  📚 Swagger UI:        http://localhost:8000/docs"
    echo "  ⚕️  Health Check:      http://localhost:8000/health"
    echo "  ℹ️  API Info:          http://localhost:8000/info"
    echo
    echo "🚗 FUNCIONALIDADES:"
    echo "  ✅ Upload de imagens"
    echo "  ✅ Classificação de placas (Mercosul/Convencional)"
    echo "  ✅ Identificação de estados"
    echo "  ✅ Extração de números"
    echo "  ✅ OCR avançado"
    echo "  ✅ Detecção com YOLO"
    echo
    echo "🔐 CREDENCIAIS:"
    echo "  Usuário: admin"
    echo "  Senha:   admin123"
    echo
    echo "📋 COMANDOS ÚTEIS:"
    echo "  docker-compose logs -f              # Ver logs"
    echo "  docker-compose down                 # Parar tudo"
    echo "  docker-compose up -d                # Reiniciar"
    echo "  ./test_api.sh                       # Testar API"
    echo
}

# Função principal
main() {
    echo -e "${BLUE}🚀 Iniciando Sistema Completo de Visão Computacional${NC}"
    echo "=" * 60
    echo
    
    check_docker
    stop_services
    build_images
    start_services
    check_health
    show_info
    
    echo "✅ Sistema pronto para uso!"
}

# Executar
main "$@"
