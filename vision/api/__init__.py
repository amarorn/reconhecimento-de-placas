"""
Módulo API REST - Arquitetura de Visão Computacional
===================================================

API REST completa com FastAPI para integração e uso externo.
"""

__version__ = "3.0.0"
__author__ = "Equipe de Desenvolvimento"

# Importar componentes principais
from .api_server import (
    VisionAPI,
    start_api_server,
    create_app
)

from .endpoints import (
    health_router,
    vision_router,
    monitoring_router,
    auth_router
)

from .models import (
    ImageRequest,
    ImageResponse,
    ProcessingRequest,
    ProcessingResponse,
    BatchRequest,
    BatchResponse,
    ErrorResponse,
    HealthResponse
)

from .auth import (
    AuthManager,
    get_current_user,
    create_access_token,
    verify_token
)

# Configuração de logging
import logging

# Configurar logging para o módulo API
api_logger = logging.getLogger(__name__)
api_logger.setLevel(logging.INFO)

# Handler para console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formato do log
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
console_handler.setFormatter(formatter)

# Adicionar handler se não existir
if not api_logger.handlers:
    api_logger.addHandler(console_handler)

# Função para verificar dependências da API
def check_api_dependencies():
    """Verifica se todas as dependências da API estão disponíveis"""
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
        import pydantic
    except ImportError:
        missing_deps.append("pydantic")
    
    try:
        import python_jose
    except ImportError:
        missing_deps.append("python-jose")
    
    try:
        import passlib
    except ImportError:
        missing_deps.append("passlib")
    
    if missing_deps:
        api_logger.warning(f"Dependências da API faltando: {', '.join(missing_deps)}")
        api_logger.warning("Instale com: pip install -r requirements.txt")
        return False
    
    api_logger.info("Todas as dependências da API estão disponíveis")
    return True

# Função para iniciar API com verificação
def start_api_safe(host: str = "0.0.0.0", port: int = 8000, check_deps: bool = True):
    """
    Inicia a API com verificação de dependências
    
    Args:
        host: Host para bind do servidor
        port: Porta para bind do servidor
        check_deps: Se deve verificar dependências antes de iniciar
    """
    try:
        if check_deps and not check_api_dependencies():
            api_logger.error("Não foi possível iniciar API devido a dependências faltando")
            return False
        
        api_logger.info(f"Iniciando API REST em {host}:{port}")
        start_api_server(host, port)
        return True
        
    except Exception as e:
        api_logger.error(f"Erro ao iniciar API: {e}")
        return False

# Função para obter informações da API
def get_api_info() -> dict:
    """Obtém informações sobre o módulo API"""
    return {
        'version': __version__,
        'author': __author__,
        'dependencies_ok': check_api_dependencies(),
        'components': [
            'VisionAPI',
            'start_api_server',
            'create_app',
            'health_router',
            'vision_router',
            'monitoring_router',
            'auth_router'
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

# Verificar dependências ao importar
_deps_ok = check_api_dependencies()

# Informações do módulo
__all__ = [
    'VisionAPI',
    'start_api_server',
    'create_app',
    'health_router',
    'vision_router',
    'monitoring_router',
    'auth_router',
    'ImageRequest',
    'ImageResponse',
    'ProcessingRequest',
    'ProcessingResponse',
    'BatchRequest',
    'BatchResponse',
    'ErrorResponse',
    'HealthResponse',
    'AuthManager',
    'get_current_user',
    'create_access_token',
    'verify_token',
    'check_api_dependencies',
    'start_api_safe',
    'get_api_info'
]