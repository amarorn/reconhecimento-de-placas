#!/bin/bash

# Script de Build Otimizado - Arquitetura de Visão Computacional
# ==============================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERRO]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCESSO]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

# Verificar se Docker está rodando
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        error "Docker não está rodando. Inicie o Docker e tente novamente."
        exit 1
    fi
    success "Docker está rodando"
}

# Verificar se Docker Compose está disponível
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose não está instalado"
        exit 1
    fi
    success "Docker Compose está disponível"
}

# Limpar recursos Docker
cleanup_docker() {
    log "🧹 Limpando recursos Docker não utilizados..."
    
    # Remover containers parados
    docker container prune -f 2>/dev/null || warning "Não foi possível limpar containers"
    
    # Remover imagens não utilizadas
    docker image prune -f 2>/dev/null || warning "Não foi possível limpar imagens"
    
    # Remover volumes não utilizados
    docker volume prune -f 2>/dev/null || warning "Não foi possível limpar volumes"
    
    # Remover redes não utilizadas
    docker network prune -f 2>/dev/null || warning "Não foi possível limpar redes"
    
    success "Limpeza concluída"
}

# Build da imagem de desenvolvimento
build_dev() {
    log "🏗️ Construindo imagem de desenvolvimento..."
    
    # Build com cache otimizado
    docker build \
        --file Dockerfile.dev \
        --tag vision-api:dev \
        --target development \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        --progress=plain \
        .
    
    if [ $? -eq 0 ]; then
        success "Imagem de desenvolvimento construída com sucesso"
    else
        error "Falha no build da imagem de desenvolvimento"
        exit 1
    fi
}

# Build da imagem de produção
build_prod() {
    log "🏗️ Construindo imagem de produção..."
    
    # Build com cache otimizado
    docker build \
        --file Dockerfile \
        --tag vision-api:prod \
        --target production \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        --progress=plain \
        .
    
    if [ $? -eq 0 ]; then
        success "Imagem de produção construída com sucesso"
    else
        error "Falha no build da imagem de produção"
        exit 1
    fi
}

# Build de todas as imagens
build_all() {
    log "🏗️ Construindo todas as imagens..."
    
    build_dev
    build_prod
    
    success "Todas as imagens foram construídas com sucesso"
}

# Verificar tamanho das imagens
check_image_sizes() {
    log "📊 Verificando tamanho das imagens..."
    
    echo ""
    echo "Tamanho das imagens:"
    docker images vision-api --format "table {{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    echo ""
}

# Função principal
main() {
    log "🚀 Iniciando build otimizado da Arquitetura de Visão Computacional"
    
    # Verificações
    check_docker
    check_docker_compose
    
    # Limpeza
    cleanup_docker
    
    # Build baseado no argumento
    case "${1:-}" in
        "dev"|"development")
            build_dev
            ;;
        "prod"|"production")
            build_prod
            ;;
        "all")
            build_all
            ;;
        "clean")
            cleanup_docker
            exit 0
            ;;
        "help"|"-h"|"--help")
            echo "Uso: $0 [comando]"
            echo ""
            echo "Comandos:"
            echo "  dev, development  - Build da imagem de desenvolvimento"
            echo "  prod, production  - Build da imagem de produção"
            echo "  all               - Build de todas as imagens"
            echo "  clean             - Limpar recursos Docker"
            echo "  help, -h, --help  - Mostrar esta ajuda"
            echo ""
            echo "Exemplos:"
            echo "  $0                # Build de desenvolvimento (padrão)"
            echo "  $0 prod           # Build de produção"
            echo "  $0 all            # Build de todas as imagens"
            echo "  $0 clean          # Limpar recursos"
            exit 0
            ;;
        *)
            # Padrão: build de desenvolvimento
            build_dev
            ;;
    esac
    
    # Verificar tamanhos
    check_image_sizes
    
    success "🎉 Build concluído com sucesso!"
    
    echo ""
    echo "📋 Próximos passos:"
    echo "  1. Para desenvolvimento: docker-compose up -d"
    echo "  2. Para produção: docker-compose -f docker-compose.prod.yml up -d"
    echo "  3. Para ver logs: docker-compose logs -f"
    echo "  4. Para parar: docker-compose down"
}

# Executar função principal
main "$@"