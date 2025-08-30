
__version__ = "2.0.0"
__author__ = "Equipe de Desenvolvimento"

from .dashboard_server import (
    DashboardServer,
    start_dashboard
)

import logging

dashboard_logger = logging.getLogger(__name__)
dashboard_logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
console_handler.setFormatter(formatter)

if not dashboard_logger.handlers:
    dashboard_logger.addHandler(console_handler)

def check_dashboard_dependencies():
    Inicia o dashboard com verificação de dependências
    
    Args:
        host: Host para bind do servidor
        port: Porta para bind do servidor
        check_deps: Se deve verificar dependências antes de iniciar
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

_deps_ok = check_dashboard_dependencies()

__all__ = [
    'DashboardServer',
    'start_dashboard',
    'start_dashboard_safe',
    'check_dashboard_dependencies',
    'get_dashboard_info'
]