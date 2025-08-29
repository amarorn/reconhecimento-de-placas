"""
Servidor Principal da API REST - Arquitetura de Visão Computacional
==================================================================

Servidor FastAPI com todos os endpoints e configurações.
"""

import os
import time
import logging
import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any

# Dependências FastAPI
try:
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    from fastapi.responses import JSONResponse
    from fastapi.openapi.utils import get_openapi
    import uvicorn
except ImportError as e:
    print(f"⚠️ Dependências FastAPI não disponíveis: {e}")
    print("Instale com: pip install fastapi uvicorn")
    FastAPI = None
    Request = None
    HTTPException = Exception
    CORSMiddleware = None
    TrustedHostMiddleware = None
    JSONResponse = None
    get_openapi = None
    uvicorn = None

# Importar componentes da API
try:
    from .endpoints import (
        health_router,
        vision_router,
        monitoring_router,
        auth_router
    )
    from .auth import auth_manager
    from .models import ErrorResponse
except ImportError as e:
    print(f"⚠️ Componentes da API não disponíveis: {e}")
    health_router = None
    vision_router = None
    monitoring_router = None
    auth_router = None
    auth_manager = None
    ErrorResponse = None

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JSON Encoder customizado para datetime
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# =============================================================================
# CONFIGURAÇÕES DA API
# =============================================================================

# Configurações padrão
DEFAULT_HOST = os.getenv("API_HOST", "0.0.0.0")
DEFAULT_PORT = int(os.getenv("API_PORT", "8000"))
DEFAULT_RELOAD = os.getenv("API_RELOAD", "false").lower() == "true"

# Configurações de segurança
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Configurações de rate limiting
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

# =============================================================================
# CLASSE PRINCIPAL DA API
# =============================================================================

class VisionAPI:
    """Classe principal da API de visão computacional"""
    
    def __init__(
        self,
        title: str = "Vision API",
        description: str = "API REST para visão computacional",
        version: str = "3.0.0",
        debug: bool = None
    ):
        self.title = title
        self.description = description
        self.version = version
        # Usar variável de ambiente DEBUG se não especificado
        if debug is None:
            self.debug = os.getenv("DEBUG", "false").lower() == "true"
        else:
            self.debug = debug
        self.start_time = time.time()
        
        # Criar aplicação FastAPI
        self.app = self._create_app()
        
        # Configurar middlewares
        self._setup_middlewares()
        
        # Configurar rotas
        self._setup_routes()
        
        # Configurar handlers de erro
        self._setup_error_handlers()
        
        # Configurar eventos
        self._setup_events()
        
        # Configurar OpenAPI
        self._setup_openapi()
        
        logger.info(f"API '{self.title}' inicializada com sucesso")
    
    def _create_app(self) -> FastAPI:
        """Cria aplicação FastAPI"""
        if not FastAPI:
            raise RuntimeError("FastAPI não está disponível")
        
        return FastAPI(
            title=self.title,
            description=self.description,
            version=self.version,
            debug=self.debug,
            docs_url="/docs" if self.debug else None,
            redoc_url="/redoc" if self.debug else None,
            openapi_url="/openapi.json" if self.debug else None
        )
    
    def _setup_middlewares(self):
        """Configura middlewares da aplicação"""
        if not self.app:
            return
        
        # CORS
        if CORS_ORIGINS:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=CORS_ORIGINS,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        
        # Trusted Hosts
        if ALLOWED_HOSTS and ALLOWED_HOSTS != ["*"]:
            self.app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=ALLOWED_HOSTS
            )
        
        # Rate Limiting (simulado)
        if RATE_LIMIT_ENABLED:
            self._setup_rate_limiting()
        
        # Logging
        self._setup_logging_middleware()
    
    def _setup_rate_limiting(self):
        """Configura rate limiting"""
        # TODO: Implementar rate limiting real
        logger.info("Rate limiting configurado (simulado)")
    
    def _setup_logging_middleware(self):
        """Configura middleware de logging"""
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            start_time = time.time()
            
            # Log da requisição
            logger.info(f"Requisição: {request.method} {request.url}")
            
            # Processar requisição
            response = await call_next(request)
            
            # Calcular tempo de resposta
            process_time = time.time() - start_time
            
            # Log da resposta
            logger.info(f"Resposta: {response.status_code} em {process_time:.3f}s")
            
            # Adicionar header de tempo de processamento
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
    
    def _setup_routes(self):
        """Configura rotas da aplicação"""
        if not self.app:
            return
        
        # Adicionar routers
        if health_router:
            self.app.include_router(health_router)
            logger.info("Router de saúde adicionado")
        
        if vision_router:
            self.app.include_router(vision_router)
            logger.info("Router de visão computacional adicionado")
        
        if monitoring_router:
            self.app.include_router(monitoring_router)
            logger.info("Router de monitoramento adicionado")
        
        if auth_router:
            self.app.include_router(auth_router)
            logger.info("Router de autenticação adicionado")
        
        # Rota raiz
        @self.app.get("/")
        async def root():
            return {
                "message": f"Bem-vindo à {self.title}",
                "version": self.version,
                "status": "operational",
                "timestamp": datetime.utcnow().isoformat(),
                "uptime": time.time() - self.start_time
            }
        
        # Rota de informações da API
        @self.app.get("/info")
        async def api_info():
            return {
                "title": self.title,
                "description": self.description,
                "version": self.version,
                "debug": self.debug,
                "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
                "uptime": time.time() - self.start_time,
                "components": {
                    "health": health_router is not None,
                    "vision": vision_router is not None,
                    "monitoring": monitoring_router is not None,
                    "auth": auth_router is not None
                }
            }
    
    def _setup_error_handlers(self):
        """Configura handlers de erro"""
        if not self.app:
            return
        
        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            error_response = ErrorResponse(
                error_code=f"HTTP_{exc.status_code}",
                error_message=exc.detail,
                timestamp=datetime.utcnow().isoformat(),
                request_id=request.headers.get("X-Request-ID", "unknown")
            )
            
            return JSONResponse(
                status_code=exc.status_code,
                content=json.loads(json.dumps(error_response.dict(), cls=CustomJSONEncoder))
            )
        
        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            logger.error(f"Erro não tratado: {exc}")
            
            error_response = ErrorResponse(
                error_code="INTERNAL_ERROR",
                error_message="Erro interno do servidor",
                timestamp=datetime.utcnow().isoformat(),
                request_id=request.headers.get("X-Request-ID", "unknown"),
                details={"exception_type": type(exc).__name__}
            )
            
            return JSONResponse(
                status_code=500,
                content=json.loads(json.dumps(error_response.dict(), cls=CustomJSONEncoder))
            )
    
    def _setup_events(self):
        """Configura eventos da aplicação"""
        if not self.app:
            return
        
        @self.app.on_event("startup")
        async def startup_event():
            logger.info(f"🚀 {self.title} iniciando...")
            logger.info(f"📊 Versão: {self.version}")
            logger.info(f"🔧 Debug: {self.debug}")
            logger.info(f"🌐 Host: {DEFAULT_HOST}")
            logger.info(f"🔌 Porta: {DEFAULT_PORT}")
            
            # Verificar componentes
            self._check_components()
        
        @self.app.on_event("shutdown")
        async def shutdown_event():
            logger.info(f"🛑 {self.title} parando...")
            
            # Limpeza se necessário
            self._cleanup()
    
    def _check_components(self):
        """Verifica status dos componentes"""
        logger.info("🔍 Verificando componentes...")
        
        components_status = {
            "health_router": health_router is not None,
            "vision_router": vision_router is not None,
            "monitoring_router": monitoring_router is not None,
            "auth_router": auth_router is not None,
            "auth_manager": auth_manager is not None
        }
        
        for component, status in components_status.items():
            status_icon = "✅" if status else "❌"
            logger.info(f"   {status_icon} {component}: {'Disponível' if status else 'Indisponível'}")
        
        # Verificar dependências
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Verifica dependências do sistema"""
        logger.info("📦 Verificando dependências...")
        
        try:
            import fastapi
            logger.info("   ✅ FastAPI disponível")
        except ImportError:
            logger.warning("   ⚠️ FastAPI não disponível")
        
        try:
            import uvicorn
            logger.info("   ✅ Uvicorn disponível")
        except ImportError:
            logger.warning("   ⚠️ Uvicorn não disponível")
        
        try:
            import numpy
            logger.info("   ✅ NumPy disponível")
        except ImportError:
            logger.warning("   ⚠️ NumPy não disponível")
        
        try:
            import cv2
            logger.info("   ✅ OpenCV disponível")
        except ImportError:
            logger.warning("   ⚠️ OpenCV não disponível")
    
    def _cleanup(self):
        """Executa limpeza na parada"""
        logger.info("🧹 Executando limpeza...")
        # TODO: Implementar limpeza de recursos
    
    def _setup_openapi(self):
        """Configura documentação OpenAPI"""
        if not self.app or not get_openapi:
            return
        
        def custom_openapi():
            if self.app.openapi_schema:
                return self.app.openapi_schema
            
            openapi_schema = get_openapi(
                title=self.title,
                version=self.version,
                description=self.description,
                routes=self.app.routes,
            )
            
            # Personalizar esquema OpenAPI
            openapi_schema["info"]["x-logo"] = {
                "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
            }
            
            self.app.openapi_schema = openapi_schema
            return self.app.openapi_schema
        
        self.app.openapi = custom_openapi
    
    def get_app(self) -> FastAPI:
        """Retorna a aplicação FastAPI"""
        return self.app
    
    def run(
        self,
        host: str = None,
        port: int = None,
        reload: bool = None,
        **kwargs
    ):
        """Executa o servidor da API"""
        if not uvicorn:
            raise RuntimeError("Uvicorn não está disponível")
        
        host = host or DEFAULT_HOST
        port = port or DEFAULT_PORT
        reload = reload if reload is not None else DEFAULT_RELOAD
        
        logger.info(f"🚀 Iniciando servidor em {host}:{port}")
        
        uvicorn.run(
            "vision.api.api_server:app",
            host=host,
            port=port,
            reload=reload,
            **kwargs
        )

# =============================================================================
# FUNÇÕES DE UTILIDADE
# =============================================================================

def create_app(
    title: str = "Vision API",
    description: str = "API REST para visão computacional",
    version: str = "3.0.0",
    debug: bool = False
) -> FastAPI:
    """Cria aplicação FastAPI configurada"""
    api = VisionAPI(title, description, version, debug)
    return api.get_app()

def start_api_server(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    reload: bool = DEFAULT_RELOAD,
    **kwargs
):
    """Inicia o servidor da API"""
    api = VisionAPI()
    api.run(host=host, port=port, reload=reload, **kwargs)

# =============================================================================
# INSTÂNCIA GLOBAL
# =============================================================================

# Criar instância global da API
vision_api = VisionAPI()

# Obter aplicação para uso externo
app = vision_api.get_app()

# =============================================================================
# CONFIGURAÇÕES ADICIONAIS
# =============================================================================

# Configurar logging para a aplicação
if app:
    # Adicionar middleware de logging adicional
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    
    # Adicionar middleware de request ID
    @app.middleware("http")
    async def add_request_id_header(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

# =============================================================================
# EXECUÇÃO DIRETA
# =============================================================================

if __name__ == "__main__":
    # Executar servidor diretamente
    start_api_server()