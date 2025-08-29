"""
Módulo Dashboard - Arquitetura de Visão Computacional
====================================================

Dashboard web em tempo real para monitoramento e visualização de métricas.
"""

__version__ = "2.0.0"
__author__ = "Equipe de Desenvolvimento"

# Importar componentes principais
from .dashboard_server import (
    DashboardServer,
    start_dashboard
)

# Configuração de logging
import logging

# Configurar logging para o módulo dashboard
dashboard_logger = logging.getLogger(__name__)
dashboard_logger.setLevel(logging.INFO)

# Handler para console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formato do log
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
console_handler.setFormatter(formatter)

# Adicionar handler se não existir
if not dashboard_logger.handlers:
    dashboard_logger.addHandler(console_handler)

# Função para verificar dependências
def check_dashboard_dependencies():
    """Verifica se todas as dependências do dashboard estão disponíveis"""
    missing_deps = []
    
    try:
        import fastapi
    except ImportError:
        missing_deps.append("fastapi")
    
    try:
        import uvicorn
    except ImportError:
        missing_deps.append("uvicorn")
    
    try:
        import psutil
    except ImportError:
        missing_deps.append("psutil")
    
    try:
        import websockets
    except ImportError:
        missing_deps.append("websockets")
    
    if missing_deps:
        dashboard_logger.warning(f"Dependências faltando: {', '.join(missing_deps)}")
        dashboard_logger.warning("Instale com: pip install -r requirements_fase2.txt")
        return False
    
    dashboard_logger.info("Todas as dependências do dashboard estão disponíveis")
    return True

# Função para iniciar dashboard com verificação
def start_dashboard_safe(host: str = "0.0.0.0", port: int = 8080, check_deps: bool = True):
    """
    Inicia o dashboard com verificação de dependências
    
    Args:
        host: Host para bind do servidor
        port: Porta para bind do servidor
        check_deps: Se deve verificar dependências antes de iniciar
    """
    try:
        if check_deps and not check_dashboard_dependencies():
            dashboard_logger.error("Não foi possível iniciar dashboard devido a dependências faltando")
            return False
        
        dashboard_logger.info(f"Iniciando dashboard em {host}:{port}")
        start_dashboard(host, port)
        return True
        
    except Exception as e:
        dashboard_logger.error(f"Erro ao iniciar dashboard: {e}")
        return False

# Função para obter informações do dashboard
def get_dashboard_info() -> dict:
    """Obtém informações sobre o módulo dashboard"""
    return {
        'version': __version__,
        'author': __author__,
        'dependencies_ok': check_dashboard_dependencies(),
        'components': [
            'DashboardServer',
            'start_dashboard',
            'start_dashboard_safe'
        ],
        'features': [
            'Interface web responsiva',
            'Atualizações em tempo real via WebSockets',
            'API REST completa',
            'Gráficos interativos',
            'Sistema de alertas integrado',
            'Métricas em tempo real'
        ]
    }

# Verificar dependências ao importar
_deps_ok = check_dashboard_dependencies()

# Informações do módulo
__all__ = [
    'DashboardServer',
    'start_dashboard',
    'start_dashboard_safe',
    'check_dashboard_dependencies',
    'get_dashboard_info'
]