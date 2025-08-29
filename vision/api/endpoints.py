"""
Endpoints da API REST - Arquitetura de Visão Computacional
=========================================================

Endpoints principais para processamento de imagens e monitoramento.
"""

import time
import uuid
import base64
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from io import BytesIO
import asyncio

# Dependências FastAPI
try:
    from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
    from fastapi.responses import JSONResponse
    import numpy as np
    import cv2
    from PIL import Image
except ImportError as e:
    print(f"⚠️ Dependências FastAPI não disponíveis: {e}")
    print("Instale com: pip install fastapi uvicorn opencv-python pillow")
    APIRouter = None
    HTTPException = Exception
    Depends = lambda x: x
    status = None
    BackgroundTasks = None
    JSONResponse = None
    np = None
    cv2 = None
    Image = None

# Importar componentes da arquitetura
try:
    from ..core.vision_pipeline import VisionPipeline
    from ..monitoring import pipeline_monitor, metrics_collector
    from .models import *
    from .auth import auth_manager, get_current_user, UserInDB
    from .security import create_access_token, create_refresh_token, verify_token
except ImportError as e:
    print(f"⚠️ Componentes da arquitetura não disponíveis: {e}")
    VisionPipeline = None
    pipeline_monitor = None
    metrics_collector = None

# Configuração de logging
logger = logging.getLogger(__name__)

# =============================================================================
# ROUTERS
# =============================================================================

# Router para verificação de saúde
health_router = APIRouter(prefix="/health", tags=["Health"])

# Router para visão computacional
vision_router = APIRouter(prefix="/vision", tags=["Vision"])

# Router para monitoramento
monitoring_router = APIRouter(prefix="/monitoring", tags=["Monitoring"])

# Router para autenticação
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

# =============================================================================
# UTILITÁRIOS
# =============================================================================

def decode_image_base64(image_data: str) -> np.ndarray:
    """Decodifica imagem em base64 para numpy array"""
    try:
        # Remover prefixo data:image/...;base64, se existir
        if "data:image" in image_data:
            image_data = image_data.split(",")[1]
        
        # Decodificar base64
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))
        
        # Converter para numpy array
        image_array = np.array(image)
        
        # Converter BGR para RGB se necessário
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        return image_array
    
    except Exception as e:
        logger.error(f"Erro ao decodificar imagem: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de imagem inválido: {str(e)}"
        )

def encode_image_base64(image_array: np.ndarray) -> str:
    """Codifica numpy array para base64"""
    try:
        # Converter BGR para RGB se necessário
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        
        # Converter para PIL Image
        image = Image.fromarray(image_array)
        
        # Salvar em buffer
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        
        # Codificar em base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/jpeg;base64,{image_base64}"
    
    except Exception as e:
        logger.error(f"Erro ao codificar imagem: {e}")
        return ""

def create_processing_result(
    image_id: str,
    success: bool,
    processing_time: float,
    detections: List[Dict] = None,
    ocr_results: List[Dict] = None,
    annotated_image: np.ndarray = None,
    error_message: str = None
) -> ProcessingResult:
    """Cria resultado de processamento padronizado"""
    
    # Converter detecções para modelo Pydantic
    detection_results = []
    if detections:
        for det in detections:
            detection_results.append(DetectionResult(
                bbox=det.get('bbox', [0, 0, 0, 0]),
                confidence=det.get('confidence', 0.0),
                class_id=det.get('class_id', 0),
                class_name=det.get('class_name', 'unknown'),
                detection_type=det.get('detection_type', 'unknown')
            ))
    
    # Converter resultados OCR para modelo Pydantic
    ocr_results_list = []
    if ocr_results:
        for ocr in ocr_results:
            ocr_results_list.append(OCRResult(
                text=ocr.get('text', ''),
                confidence=ocr.get('confidence', 0.0),
                bbox=ocr.get('bbox', [0, 0, 0, 0]),
                ocr_type=ocr.get('ocr_type', 'auto')
            ))
    
    # Codificar imagem anotada se fornecida
    annotated_image_base64 = None
    if annotated_image is not None:
        annotated_image_base64 = encode_image_base64(annotated_image)
    
    return ProcessingResult(
        image_id=image_id,
        success=success,
        processing_time=processing_time,
        detections=detection_results,
        ocr_results=ocr_results_list,
        annotated_image=annotated_image_base64,
        error_message=error_message
    )

# =============================================================================
# ENDPOINTS DE SAÚDE
# =============================================================================

@health_router.get("/", response_model=HealthResponse)
async def health_check():
    """Verificação de saúde da API"""
    try:
        # Obter métricas do sistema
        system_metrics = {}
        if metrics_collector:
            current_metrics = metrics_collector.get_current_metrics()
            system_metrics = current_metrics.get('system', {})
        
        # Verificar componentes
        components = {
            "api": "healthy",
            "pipeline": "healthy" if VisionPipeline else "unavailable",
            "monitoring": "healthy" if pipeline_monitor else "unavailable",
            "auth": "healthy" if auth_manager else "unavailable"
        }
        
        # Calcular uptime (simulado)
        uptime = time.time() % 86400  # Simular uptime
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            version="3.0.0",
            uptime=uptime,
            components=components,
            memory_usage=system_metrics.get('memory_percent'),
            cpu_usage=system_metrics.get('cpu_percent')
        )
    
    except Exception as e:
        logger.error(f"Erro na verificação de saúde: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            version="3.0.0",
            uptime=0.0,
            components={"api": "unhealthy"},
            memory_usage=None,
            cpu_usage=None
        )

@health_router.get("/ready")
async def readiness_check():
    """Verificação de prontidão da API"""
    try:
        # Verificar se todos os componentes estão prontos
        ready = all([
            VisionPipeline is not None,
            pipeline_monitor is not None,
            auth_manager is not None
        ])
        
        if ready:
            return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="API não está pronta"
            )
    
    except Exception as e:
        logger.error(f"Erro na verificação de prontidão: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Erro na verificação de prontidão: {str(e)}"
        )

# =============================================================================
# ENDPOINTS DE VISÃO COMPUTACIONAL
# =============================================================================

@vision_router.post("/process", response_model=ImageResponse)
async def process_image(
    request: ProcessingRequest,
    current_user: UserInDB = Depends(get_current_user),
    background_tasks: BackgroundTasks = None
):
    """Processa uma imagem com visão computacional"""
    
    try:
        start_time = time.time()
        
        # Verificar permissões
        if not current_user.has_any_permission(["read", "write", "admin"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão insuficiente para processar imagens"
            )
        
        # Decodificar imagem
        image_array = decode_image_base64(request.image_request.image_data)
        
        # Gerar ID único
        image_id = str(uuid.uuid4())
        request_id = str(uuid.uuid4())
        
        # Processar imagem (simulado por enquanto)
        # TODO: Integrar com VisionPipeline real
        processing_time = time.time() - start_time
        
        # Simular resultados
        detections = [
            {
                "bbox": [100, 100, 200, 150],
                "confidence": 0.85,
                "class_id": 1,
                "class_name": "traffic_sign",
                "detection_type": "traffic_sign"
            }
        ]
        
        ocr_results = [
            {
                "text": "PARE",
                "confidence": 0.92,
                "bbox": [110, 110, 190, 140],
                "ocr_type": "paddle"
            }
        ]
        
        # Criar resultado
        processing_result = create_processing_result(
            image_id=image_id,
            success=True,
            processing_time=processing_time,
            detections=detections,
            ocr_results=ocr_results
        )
        
        # Rastrear processamento se monitoramento estiver disponível
        if pipeline_monitor:
            pipeline_monitor.track_image_processing(
                image_path=image_id,
                success=True,
                processing_time=processing_time,
                detections=len(detections),
                texts=len(ocr_results),
                detection_confidence=detections[0]['confidence'] if detections else 0.0,
                ocr_confidence=ocr_results[0]['confidence'] if ocr_results else 0.0
            )
        
        # Criar resposta
        response = ImageResponse(
            request_id=request_id,
            timestamp=datetime.utcnow(),
            result=processing_result,
            api_version="3.0.0"
        )
        
        # Adicionar tarefa em background se solicitado
        if background_tasks and request.save_results:
            background_tasks.add_task(save_processing_results, image_id, processing_result)
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no processamento de imagem: {e}")
        
        # Criar resposta de erro
        error_result = create_processing_result(
            image_id=str(uuid.uuid4()),
            success=False,
            processing_time=0.0,
            error_message=str(e)
        )
        
        error_response = ImageResponse(
            request_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            result=error_result,
            api_version="3.0.0"
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno no processamento: {str(e)}"
        )

@vision_router.post("/batch", response_model=BatchResponse)
async def process_batch(
    request: BatchRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """Processa um lote de imagens"""
    
    try:
        # Verificar permissões
        if not current_user.has_any_permission(["read", "write", "admin"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão insuficiente para processamento em lote"
            )
        
        start_time = time.time()
        batch_id = str(uuid.uuid4())
        
        # Processar requisições
        results = []
        successful_requests = 0
        failed_requests = 0
        
        for i, processing_request in enumerate(request.requests):
            try:
                # Simular processamento
                image_id = str(uuid.uuid4())
                processing_time = 0.1  # Simulado
                
                # Simular resultados
                detections = [
                    {
                        "bbox": [100, 100, 200, 150],
                        "confidence": 0.85,
                        "class_id": 1,
                        "class_name": "traffic_sign",
                        "detection_type": "traffic_sign"
                    }
                ]
                
                ocr_results = [
                    {
                        "text": "PARE",
                        "confidence": 0.92,
                        "bbox": [110, 110, 190, 140],
                        "ocr_type": "paddle"
                    }
                ]
                
                # Criar resultado
                result = create_processing_result(
                    image_id=image_id,
                    success=True,
                    processing_time=processing_time,
                    detections=detections,
                    ocr_results=ocr_results
                )
                
                results.append(result)
                successful_requests += 1
                
            except Exception as e:
                logger.error(f"Erro no processamento da imagem {i}: {e}")
                
                error_result = create_processing_result(
                    image_id=str(uuid.uuid4()),
                    success=False,
                    processing_time=0.0,
                    error_message=str(e)
                )
                
                results.append(error_result)
                failed_requests += 1
        
        total_time = time.time() - start_time
        
        return BatchResponse(
            batch_id=batch_id,
            timestamp=datetime.utcnow(),
            total_requests=len(request.requests),
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            results=results,
            processing_time=total_time,
            api_version="3.0.0"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no processamento em lote: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno no processamento em lote: {str(e)}"
        )

@vision_router.get("/status")
async def get_vision_status():
    """Obtém status do sistema de visão computacional"""
    try:
        # Verificar componentes
        pipeline_available = VisionPipeline is not None
        monitoring_available = pipeline_monitor is not None
        
        # Obter métricas se disponível
        pipeline_metrics = {}
        if monitoring_available:
            try:
                pipeline_metrics = pipeline_monitor.get_pipeline_summary()
            except Exception:
                pipeline_metrics = {"error": "Não foi possível obter métricas"}
        
        return {
            "status": "operational" if pipeline_available else "unavailable",
            "pipeline_available": pipeline_available,
            "monitoring_available": monitoring_available,
            "pipeline_metrics": pipeline_metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Erro ao obter status da visão: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# =============================================================================
# ENDPOINTS DE MONITORAMENTO
# =============================================================================

@monitoring_router.get("/metrics", response_model=MetricsResponse)
async def get_system_metrics(
    current_user: UserInDB = Depends(get_current_user)
):
    """Obtém métricas do sistema"""
    
    try:
        # Verificar permissões
        if not current_user.has_any_permission(["monitor", "admin"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão insuficiente para acessar métricas"
            )
        
        # Obter métricas do sistema
        system_metrics = {}
        api_metrics = {}
        pipeline_metrics = {}
        performance_metrics = {}
        
        if metrics_collector:
            current_metrics = metrics_collector.get_current_metrics()
            system_metrics = current_metrics.get('system', {})
            api_metrics = current_metrics.get('api', {})
            pipeline_metrics = current_metrics.get('pipeline', {})
            performance_metrics = current_metrics.get('performance', {})
        
        return MetricsResponse(
            timestamp=datetime.utcnow(),
            system_metrics=system_metrics,
            api_metrics=api_metrics,
            pipeline_metrics=pipeline_metrics,
            performance_metrics=performance_metrics
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter métricas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter métricas: {str(e)}"
        )

@monitoring_router.get("/alerts", response_model=AlertResponse)
async def get_system_alerts(
    current_user: UserInDB = Depends(get_current_user)
):
    """Obtém alertas do sistema"""
    
    try:
        # Verificar permissões
        if not current_user.has_any_permission(["monitor", "admin"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão insuficiente para acessar alertas"
            )
        
        # Obter alertas se disponível
        alerts = []
        total_alerts = 0
        critical_alerts = 0
        warning_alerts = 0
        info_alerts = 0
        
        if pipeline_monitor:
            try:
                status = pipeline_monitor.get_pipeline_summary()
                alerts_data = status.get('alerts', {}).get('active_alerts', [])
                
                for alert in alerts_data:
                    alerts.append({
                        "id": alert.get('id', 'unknown'),
                        "title": alert.get('title', 'Unknown Alert'),
                        "message": alert.get('message', ''),
                        "severity": alert.get('severity', 'info'),
                        "category": alert.get('category', 'unknown'),
                        "timestamp": alert.get('timestamp', datetime.utcnow().isoformat())
                    })
                
                total_alerts = len(alerts)
                critical_alerts = sum(1 for a in alerts if a.get('severity') == 'critical')
                warning_alerts = sum(1 for a in alerts if a.get('severity') == 'warning')
                info_alerts = sum(1 for a in alerts if a.get('severity') == 'info')
                
            except Exception:
                alerts = []
                total_alerts = 0
        
        return AlertResponse(
            alerts=alerts,
            total_alerts=total_alerts,
            critical_alerts=critical_alerts,
            warning_alerts=warning_alerts,
            info_alerts=info_alerts
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter alertas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter alertas: {str(e)}"
        )

# =============================================================================
# ENDPOINTS DE AUTENTICAÇÃO
# =============================================================================

@auth_router.post("/login", response_model=TokenResponse)
async def login(user_credentials: UserLogin):
    """Autentica usuário e retorna token JWT"""
    
    try:
        # Autenticar usuário
        user = auth_manager.authenticate_user(
            user_credentials.username,
            user_credentials.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Criar tokens
        access_token_expires = datetime.utcnow() + timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires - datetime.utcnow()
        )
        
        refresh_token = create_refresh_token(data={"sub": user.username})
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=1800,  # 30 minutos
            refresh_token=refresh_token
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno no login: {str(e)}"
        )

@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """Renova token de acesso usando refresh token"""
    
    try:
        # Verificar refresh token
        payload = verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido"
            )
        
        username = payload.get("sub")
        user = auth_manager.get_user_by_username(username)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado ou inativo"
            )
        
        # Criar novo access token
        access_token_expires = datetime.utcnow() + timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires - datetime.utcnow()
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=1800,  # 30 minutos
            refresh_token=refresh_token
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na renovação do token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno na renovação do token: {str(e)}"
        )

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_user)):
    """Obtém informações do usuário atual"""
    
    return UserResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        permissions=current_user.permissions,
        created_at=current_user.created_at
    )

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

async def save_processing_results(image_id: str, result: ProcessingResult):
    """Salva resultados de processamento em background"""
    try:
        # TODO: Implementar salvamento em banco de dados
        logger.info(f"Salvando resultados para imagem {image_id}")
        
        # Simular salvamento
        await asyncio.sleep(0.1)
        
        logger.info(f"Resultados salvos com sucesso para imagem {image_id}")
    
    except Exception as e:
        logger.error(f"Erro ao salvar resultados para imagem {image_id}: {e}")

# =============================================================================
# CONFIGURAÇÃO DOS ROUTERS
# =============================================================================

# Adicionar middleware de logging se disponível
if APIRouter:
    # Configurar logging para todos os endpoints
    for router in [health_router, vision_router, monitoring_router, auth_router]:
        router.add_middleware(logging.StreamHandler)