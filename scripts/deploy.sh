#!/bin/bash

# Script de Deploy - Arquitetura de Visão Computacional - Fase 4
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

# Verificar variáveis de ambiente
check_env() {
    if [ -z "$ENVIRONMENT" ]; then
        ENVIRONMENT="development"
        warning "ENVIRONMENT não definido, usando: $ENVIRONMENT"
    fi
    
    if [ "$ENVIRONMENT" = "production" ]; then
        if [ ! -f ".env.prod" ]; then
            error "Arquivo .env.prod não encontrado para deploy em produção"
            exit 1
        fi
        ENV_FILE=".env.prod"
        COMPOSE_FILE="docker-compose.prod.yml"
    else
        if [ ! -f ".env.dev" ]; then
            warning "Arquivo .env.dev não encontrado, usando variáveis padrão"
        fi
        ENV_FILE=".env.dev"
        COMPOSE_FILE="docker-compose.yml"
    fi
    
    success "Ambiente configurado: $ENVIRONMENT"
    success "Arquivo de configuração: $ENV_FILE"
    success "Compose file: $COMPOSE_FILE"
}

# Backup dos dados existentes
backup_data() {
    if [ "$ENVIRONMENT" = "production" ]; then
        log "Criando backup dos dados existentes..."
        
        if [ -d "backups" ]; then
            BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S).tar.gz"
            tar -czf "backups/$BACKUP_NAME" data/ logs/ 2>/dev/null || warning "Não foi possível criar backup"
            success "Backup criado: backups/$BACKUP_NAME"
        fi
    fi
}

# Parar serviços existentes
stop_services() {
    log "Parando serviços existentes..."
    
    if [ -f "$COMPOSE_FILE" ]; then
        docker-compose -f "$COMPOSE_FILE" down --remove-orphans || warning "Não foi possível parar serviços"
        success "Serviços parados"
    else
        warning "Arquivo $COMPOSE_FILE não encontrado"
    fi
}

# Limpar recursos não utilizados
cleanup() {
    log "Limpando recursos Docker não utilizados..."
    
    docker system prune -f || warning "Não foi possível limpar recursos"
    success "Limpeza concluída"
}

# Build das imagens
build_images() {
    log "Construindo imagens Docker..."
    
    if [ -f "$COMPOSE_FILE" ]; then
        docker-compose -f "$COMPOSE_FILE" build --no-cache || {
            error "Falha no build das imagens"
            exit 1
        }
        success "Imagens construídas com sucesso"
    else
        error "Arquivo $COMPOSE_FILE não encontrado"
        exit 1
    fi
}

# Iniciar serviços
start_services() {
    log "Iniciando serviços..."
    
    if [ -f "$COMPOSE_FILE" ]; then
        # Carregar variáveis de ambiente se o arquivo existir
        if [ -f "$ENV_FILE" ]; then
            export $(cat "$ENV_FILE" | grep -v '^#' | xargs)
        fi
        
        docker-compose -f "$COMPOSE_FILE" up -d || {
            error "Falha ao iniciar serviços"
            exit 1
        }
        success "Serviços iniciados com sucesso"
    else
        error "Arquivo $COMPOSE_FILE não encontrado"
        exit 1
    fi
}

# Verificar saúde dos serviços
health_check() {
    log "Verificando saúde dos serviços..."
    
    # Aguardar serviços iniciarem
    sleep 30
    
    # Verificar API
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        success "API está saudável"
    else
        error "API não está respondendo"
        return 1
    fi
    
    # Verificar Dashboard
    if curl -f http://localhost:8080/health > /dev/null 2>&1; then
        success "Dashboard está saudável"
    else
        error "Dashboard não está respondendo"
        return 1
    fi
    
    # Verificar Prometheus
    if curl -f http://localhost:9090/-/healthy > /dev/null 2>&1; then
        success "Prometheus está saudável"
    else
        error "Prometheus não está respondendo"
        return 1
    fi
    
    # Verificar Grafana
    if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
        success "Grafana está saudável"
    else
        error "Grafana não está respondendo"
        return 1
    fi
    
    success "Todos os serviços estão saudáveis"
}

# Mostrar status dos serviços
show_status() {
    log "Status dos serviços:"
    
    if [ -f "$COMPOSE_FILE" ]; then
        docker-compose -f "$COMPOSE_FILE" ps
    fi
    
    echo ""
    log "URLs dos serviços:"
    echo "  🌐 API: http://localhost:8000"
    echo "  📊 Dashboard: http://localhost:8080"
    echo "  📈 Prometheus: http://localhost:9090"
    echo "  📊 Grafana: http://localhost:3000 (admin/admin)"
    echo "  📝 Kibana: http://localhost:5601"
    echo "  🔍 Elasticsearch: http://localhost:9200"
    echo "  🗄️ PostgreSQL: localhost:5432"
    echo "  🚀 Redis: localhost:6379"
}

# Função principal
main() {
    log "🚀 Iniciando deploy da Arquitetura de Visão Computacional - Fase 4"
    log "Ambiente: $ENVIRONMENT"
    
    # Verificações
    check_docker
    check_docker_compose
    check_env
    
    # Deploy
    backup_data
    stop_services
    cleanup
    build_images
    start_services
    
    # Verificações pós-deploy
    if health_check; then
        success "🎉 Deploy concluído com sucesso!"
        show_status
    else
        error "❌ Deploy falhou na verificação de saúde"
        exit 1
    fi
}

# Tratamento de argumentos
case "${1:-}" in
    "dev"|"development")
        ENVIRONMENT="development"
        ;;
    "prod"|"production")
        ENVIRONMENT="production"
        ;;
    "stop")
        log "🛑 Parando serviços..."
        if [ -f "docker-compose.yml" ]; then
            docker-compose down
        fi
        if [ -f "docker-compose.prod.yml" ]; then
            docker-compose -f docker-compose.prod.yml down
        fi
        success "Serviços parados"
        exit 0
        ;;
    "restart")
        log "🔄 Reiniciando serviços..."
        if [ -f "docker-compose.yml" ]; then
            docker-compose restart
        fi
        if [ -f "docker-compose.prod.yml" ]; then
            docker-compose -f docker-compose.prod.yml restart
        fi
        success "Serviços reiniciados"
        exit 0
        ;;
    "logs")
        log "📋 Mostrando logs..."
        if [ -f "docker-compose.yml" ]; then
            docker-compose logs -f
        fi
        if [ -f "docker-compose.prod.yml" ]; then
            docker-compose -f docker-compose.prod.yml logs -f
        fi
        exit 0
        ;;
    "help"|"-h"|"--help")
        echo "Uso: $0 [comando]"
        echo ""
        echo "Comandos:"
        echo "  dev, development  - Deploy para desenvolvimento (padrão)"
        echo "  prod, production  - Deploy para produção"
        echo "  stop              - Parar todos os serviços"
        echo "  restart           - Reiniciar todos os serviços"
        echo "  logs              - Mostrar logs dos serviços"
        echo "  help, -h, --help  - Mostrar esta ajuda"
        echo ""
        echo "Exemplos:"
        echo "  $0                # Deploy para desenvolvimento"
        echo "  $0 prod           # Deploy para produção"
        echo "  $0 stop           # Parar serviços"
        exit 0
        ;;
esac

# Executar função principal
main "$@"