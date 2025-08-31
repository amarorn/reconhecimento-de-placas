#!/usr/bin/env python3
"""
API de Visão Computacional
==========================

Módulo principal da API REST para visão computacional.
"""

__version__ = "3.0.0"
__author__ = "Equipe de Desenvolvimento"

from .api_server import (
    VisionAPI,
    start_api_server,
    create_app
)

from .models import (
    DetectionRequest,
    SignalPlateRequest,
    VehiclePlateRequest,
    HealthResponse
)

from .auth import (
    AuthManager,
    get_current_user,
    create_access_token
)

import logging

# Configurar logging
api_logger = logging.getLogger(__name__)
api_logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
console_handler.setFormatter(formatter)

if not api_logger.handlers:
    api_logger.addHandler(console_handler)

def check_api_dependencies():
    """Verifica se as dependências da API estão disponíveis"""
    try:
        import fastapi
        import uvicorn
        return True
    except ImportError:
        return False

def get_api_info():
    """Retorna informações sobre a API"""
    return {
        'version': __version__,
        'author': __author__,
        'dependencies_ok': check_api_dependencies(),
        'components': [
            'VisionAPI',
            'start_api_server',
            'create_app'
        ],
        'features': [
            'API REST completa com FastAPI',
            'Autenticação JWT',
            'Documentação Swagger/OpenAPI',
            'Endpoints para visão computacional',
            'Monitoramento integrado',
            'Validação de dados com Pydantic',
            'Rate limiting e throttling',
            'Integração com pipeline principal'
        ]
    }

# Verificar dependências na inicialização
_deps_ok = check_api_dependencies()

__all__ = [
    'VisionAPI',
    'start_api_server',
    'create_app',
    'DetectionRequest',
    'SignalPlateRequest',
    'VehiclePlateRequest',
    'HealthResponse',
    'AuthManager',
    'get_current_user',
    'create_access_token',

    'check_api_dependencies',
    'get_api_info'
]