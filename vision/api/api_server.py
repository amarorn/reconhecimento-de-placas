#!/usr/bin/env python3
"""
Servidor da API REST - Arquitetura de Visão Computacional
=========================================================

Este módulo implementa o servidor FastAPI principal com todos os endpoints
e funcionalidades de visão computacional.
"""

import os
import time
import logging
from datetime import datetime
from typing import Optional, Dict, Any

try:
    from fastapi import FastAPI, Request, Response
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    from fastapi.responses import JSONResponse
    from fastapi.exceptions import RequestValidationError
    from fastapi.openapi.utils import get_openapi
    from starlette.exceptions import HTTPException as StarletteHTTPException
except ImportError:
    FastAPI = None
    get_openapi = None

from .routers import (
    health_router, vision_router, 
    monitoring_router, auth_router
)
from .endpoints import router as video_endpoints

logger = logging.getLogger(__name__)

DEFAULT_HOST = os.getenv("HOST", "0.0.0.0")
DEFAULT_PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))


class VisionAPI:
    def __init__(self, title: str = "API de Visão Computacional", 
                 description: str = "API para detecção e reconhecimento de placas, sinais de trânsito e análise de vídeo",
                 version: str = "1.0.0",
                 debug: bool = DEBUG):
        self.title = title
        self.description = description
        self.version = version
        self.debug = debug
        self.start_time = time.time()
        self.app = None
        
    def _create_app(self) -> FastAPI:
        if not FastAPI:
            raise RuntimeError("FastAPI não está disponível")
        
        return FastAPI(
            title=self.title,
            description=self.description,
            version=self.version,
            debug=self.debug,
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json"
        )
    
    def _setup_middlewares(self):
        if not self.app:
            return
            
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        if ALLOWED_HOSTS != ["*"]:
            self.app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=ALLOWED_HOSTS
            )
        
        logger.info("Middlewares configurados")
    
    def _setup_rate_limiting(self):
        if not self.app or not RATE_LIMIT_ENABLED:
            return
            
        logger.info("Rate limiting configurado (simulado)")
    
    def _setup_logging_middleware(self):
        if not self.app:
            return
        
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            start_time = time.time()
            
            response = await call_next(request)
            
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            logger.info(
                f"{request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Tempo: {process_time:.3f}s"
            )
            return response
    
    def _setup_routes(self):
        if not self.app:
            return
        
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
        
        # Adicionar endpoints de vídeo
        if video_endpoints:
            self.app.include_router(video_endpoints, prefix="/vision", tags=["Video Analysis"])
            logger.info("Endpoints de análise de vídeo adicionados")
        
        @self.app.get("/")
        async def root():
            return {
                "message": f"Bem-vindo à {self.title}",
                "version": self.version,
                "status": "operational",
                "timestamp": datetime.utcnow().isoformat(),
                "uptime": time.time() - self.start_time
            }
        
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
                    "auth": auth_router is not None,
                    "video_analysis": video_endpoints is not None
                }
            }
    
    def _setup_error_handlers(self):
        if not self.app:
            return
        
        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            return JSONResponse(
                status_code=422,
                content={
                    "detail": "Erro de validação dos dados",
                    "errors": exc.errors()
                }
            )
        
        @self.app.exception_handler(StarletteHTTPException)
        async def http_exception_handler(request: Request, exc: StarletteHTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "detail": exc.detail,
                    "status_code": exc.status_code
                }
            )
        
        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            logger.error(f"Erro não tratado: {exc}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Erro interno do servidor",
                    "status_code": 500
                }
            )
    
    def _setup_events(self):
        if not self.app:
            return
        
        @self.app.on_event("startup")
        async def startup_event():
            logger.info(f"{self.title} iniciando...")
            logger.info(f"Versão: {self.version}")
            logger.info(f"Debug: {self.debug}")
            logger.info(f"Host: {DEFAULT_HOST}")
            logger.info(f"Porta: {DEFAULT_PORT}")
            
            self._check_components()
        
        @self.app.on_event("shutdown")
        async def shutdown_event():
            logger.info(f"{self.title} encerrando...")
            self._cleanup()
    
    def _check_components(self):
        logger.info("Verificando componentes...")
        
        required_modules = [
            "fastapi", "uvicorn", "numpy", "opencv-python"
        ]
        
        missing_modules = []
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)
        
        if missing_modules:
            logger.warning(f"Módulos não disponíveis: {missing_modules}")
            return False
        
        return True
    
    def _cleanup(self):
        logger.info("Limpando recursos...")
        
        try:
            if hasattr(self, 'vision_pipeline'):
                self.vision_pipeline.cleanup()
                logger.info("Pipeline de visão limpo")
        except Exception as e:
            logger.error(f"Erro ao limpar pipeline: {e}")
        
        logger.info("Limpeza concluída")
    
    def _setup_openapi(self):
        if not self.app:
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
            
            self.app.openapi_schema = openapi_schema
            return self.app.openapi_schema
        
        self.app.openapi = custom_openapi
    
    def initialize(self) -> FastAPI:
        logger.info("Inicializando API...")
        
        self.app = self._create_app()
        self._setup_middlewares()
        self._setup_rate_limiting()
        self._setup_logging_middleware()
        self._setup_routes()
        self._setup_error_handlers()
        self._setup_events()
        self._setup_openapi()
        
        logger.info("API inicializada com sucesso")
        return self.app


def get_app() -> FastAPI:
    api = VisionAPI()
    return api.initialize()


def run(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, 
        debug: bool = DEBUG, reload: bool = False):
    import uvicorn
    
    if not uvicorn:
        raise RuntimeError("Uvicorn não está disponível")
    
    api = VisionAPI(debug=debug)
    app = api.initialize()
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload
    )


def create_app() -> FastAPI:
    return get_app()


def start_api_server():
    run()


if __name__ == "__main__":
    start_api_server()


vision_api = VisionAPI()
app = vision_api.initialize()
