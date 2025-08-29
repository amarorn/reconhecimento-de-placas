"""
Modelos de Dados da API REST - Arquitetura de Visão Computacional
================================================================

Modelos Pydantic para validação e serialização de dados da API.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

# =============================================================================
# ENUMS
# =============================================================================

class ProcessingMode(str, Enum):
    """Modos de processamento disponíveis"""
    FAST = "fast"
    BALANCED = "balanced"
    ACCURATE = "accurate"

class ImageFormat(str, Enum):
    """Formatos de imagem suportados"""
    JPEG = "jpeg"
    PNG = "png"
    BMP = "bmp"
    TIFF = "tiff"

class DetectionType(str, Enum):
    """Tipos de detecção disponíveis"""
    TRAFFIC_SIGN = "traffic_sign"
    LICENSE_PLATE = "license_plate"
    VEHICLE = "vehicle"
    ALL = "all"

class OCRType(str, Enum):
    """Tipos de OCR disponíveis"""
    PADDLE = "paddle"
    EASY = "easy"
    TESSERACT = "tesseract"
    TRANSFORMER = "transformer"
    AUTO = "auto"

# =============================================================================
# MODELOS DE REQUISIÇÃO
# =============================================================================

class ImageRequest(BaseModel):
    """Requisição para processamento de imagem única"""
    
    image_data: str = Field(..., description="Imagem em base64 ou URL")
    image_format: ImageFormat = Field(ImageFormat.JPEG, description="Formato da imagem")
    processing_mode: ProcessingMode = Field(ProcessingMode.BALANCED, description="Modo de processamento")
    detection_types: List[DetectionType] = Field([DetectionType.ALL], description="Tipos de detecção")
    ocr_types: List[OCRType] = Field([OCRType.AUTO], description="Tipos de OCR")
    confidence_threshold: float = Field(0.5, ge=0.0, le=1.0, description="Threshold de confiança")
    max_detections: int = Field(10, ge=1, le=100, description="Máximo de detecções")
    preprocessing_options: Optional[Dict[str, Any]] = Field(None, description="Opções de pré-processamento")
    
    @validator('confidence_threshold')
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('confidence_threshold deve estar entre 0.0 e 1.0')
        return v
    
    @validator('max_detections')
    def validate_max_detections(cls, v):
        if v < 1 or v > 100:
            raise ValueError('max_detections deve estar entre 1 e 100')
        return v

class ProcessingRequest(BaseModel):
    """Requisição para processamento com opções avançadas"""
    
    image_request: ImageRequest = Field(..., description="Configuração da imagem")
    save_results: bool = Field(False, description="Salvar resultados no sistema")
    return_annotated_image: bool = Field(False, description="Retornar imagem anotada")
    return_confidence_scores: bool = Field(True, description="Retornar scores de confiança")
    return_processing_time: bool = Field(True, description="Retornar tempo de processamento")
    custom_metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados customizados")

class BatchRequest(BaseModel):
    """Requisição para processamento em lote"""
    
    requests: List[ProcessingRequest] = Field(..., description="Lista de requisições")
    batch_size: int = Field(10, ge=1, le=100, description="Tamanho do lote")
    parallel_processing: bool = Field(True, description="Processamento paralelo")
    priority: str = Field("normal", description="Prioridade do processamento")
    
    @validator('batch_size')
    def validate_batch_size(cls, v):
        if v < 1 or v > 100:
            raise ValueError('batch_size deve estar entre 1 e 100')
        return v
    
    @validator('requests')
    def validate_requests(cls, v):
        if len(v) == 0:
            raise ValueError('requests não pode estar vazio')
        if len(v) > 1000:
            raise ValueError('máximo de 1000 requisições por lote')
        return v

# =============================================================================
# MODELOS DE RESPOSTA
# =============================================================================

class DetectionResult(BaseModel):
    """Resultado de uma detecção"""
    
    bbox: List[float] = Field(..., description="Bounding box [x1, y1, x2, y2]")
    confidence: float = Field(..., description="Confiança da detecção")
    class_id: int = Field(..., description="ID da classe")
    class_name: str = Field(..., description="Nome da classe")
    detection_type: DetectionType = Field(..., description="Tipo de detecção")

class OCRResult(BaseModel):
    """Resultado de OCR"""
    
    text: str = Field(..., description="Texto extraído")
    confidence: float = Field(..., description="Confiança da extração")
    bbox: List[float] = Field(..., description="Bounding box do texto")
    ocr_type: OCRType = Field(..., description="Tipo de OCR usado")

class ProcessingResult(BaseModel):
    """Resultado do processamento de uma imagem"""
    
    image_id: str = Field(..., description="ID único da imagem")
    success: bool = Field(..., description="Sucesso do processamento")
    processing_time: float = Field(..., description="Tempo de processamento em segundos")
    detections: List[DetectionResult] = Field([], description="Lista de detecções")
    ocr_results: List[OCRResult] = Field([], description="Resultados de OCR")
    annotated_image: Optional[str] = Field(None, description="Imagem anotada em base64")
    error_message: Optional[str] = Field(None, description="Mensagem de erro se houver")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados adicionais")

class ImageResponse(BaseModel):
    """Resposta para processamento de imagem única"""
    
    request_id: str = Field(..., description="ID único da requisição")
    timestamp: datetime = Field(..., description="Timestamp do processamento")
    result: ProcessingResult = Field(..., description="Resultado do processamento")
    api_version: str = Field(..., description="Versão da API")

class ProcessingResponse(BaseModel):
    """Resposta para processamento com opções avançadas"""
    
    image_response: ImageResponse = Field(..., description="Resposta da imagem")
    additional_info: Optional[Dict[str, Any]] = Field(None, description="Informações adicionais")

class BatchResponse(BaseModel):
    """Resposta para processamento em lote"""
    
    batch_id: str = Field(..., description="ID único do lote")
    timestamp: datetime = Field(..., description="Timestamp do processamento")
    total_requests: int = Field(..., description="Total de requisições")
    successful_requests: int = Field(..., description="Requisições bem-sucedidas")
    failed_requests: int = Field(..., description="Requisições falhadas")
    results: List[ProcessingResult] = Field(..., description="Resultados do processamento")
    processing_time: float = Field(..., description="Tempo total de processamento")
    api_version: str = Field(..., description="Versão da API")

# =============================================================================
# MODELOS DE SISTEMA
# =============================================================================

class HealthResponse(BaseModel):
    """Resposta de verificação de saúde da API"""
    
    status: str = Field(..., description="Status da API")
    timestamp: datetime = Field(..., description="Timestamp da verificação")
    version: str = Field(..., description="Versão da API")
    uptime: float = Field(..., description="Tempo de atividade em segundos")
    components: Dict[str, str] = Field(..., description="Status dos componentes")
    memory_usage: Optional[float] = Field(None, description="Uso de memória em MB")
    cpu_usage: Optional[float] = Field(None, description="Uso de CPU em %")

class ErrorResponse(BaseModel):
    """Resposta de erro padronizada"""
    
    error_code: str = Field(..., description="Código do erro")
    error_message: str = Field(..., description="Mensagem do erro")
    timestamp: datetime = Field(..., description="Timestamp do erro")
    request_id: Optional[str] = Field(None, description="ID da requisição")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalhes adicionais")

class StatusResponse(BaseModel):
    """Resposta de status do sistema"""
    
    system_status: str = Field(..., description="Status geral do sistema")
    api_status: str = Field(..., description="Status da API")
    pipeline_status: str = Field(..., description="Status do pipeline de visão")
    dashboard_status: str = Field(..., description="Status do dashboard")
    timestamp: datetime = Field(..., description="Timestamp do status")

# =============================================================================
# MODELOS DE AUTENTICAÇÃO
# =============================================================================

class UserLogin(BaseModel):
    """Requisição de login do usuário"""
    
    username: str = Field(..., description="Nome de usuário")
    password: str = Field(..., description="Senha")

class UserResponse(BaseModel):
    """Resposta de usuário"""
    
    user_id: str = Field(..., description="ID do usuário")
    username: str = Field(..., description="Nome de usuário")
    email: str = Field(..., description="Email do usuário")
    is_active: bool = Field(..., description="Se o usuário está ativo")
    permissions: List[str] = Field(..., description="Permissões do usuário")
    created_at: datetime = Field(..., description="Data de criação")

class TokenResponse(BaseModel):
    """Resposta de token de autenticação"""
    
    access_token: str = Field(..., description="Token de acesso")
    token_type: str = Field("bearer", description="Tipo do token")
    expires_in: int = Field(..., description="Tempo de expiração em segundos")
    refresh_token: Optional[str] = Field(None, description="Token de refresh")

# =============================================================================
# MODELOS DE MONITORAMENTO
# =============================================================================

class MetricsResponse(BaseModel):
    """Resposta de métricas do sistema"""
    
    timestamp: datetime = Field(..., description="Timestamp das métricas")
    system_metrics: Dict[str, float] = Field(..., description="Métricas do sistema")
    api_metrics: Dict[str, float] = Field(..., description="Métricas da API")
    pipeline_metrics: Dict[str, float] = Field(..., description="Métricas do pipeline")
    performance_metrics: Dict[str, float] = Field(..., description="Métricas de performance")

class AlertResponse(BaseModel):
    """Resposta de alertas do sistema"""
    
    alerts: List[Dict[str, Any]] = Field(..., description="Lista de alertas ativos")
    total_alerts: int = Field(..., description="Total de alertas")
    critical_alerts: int = Field(..., description="Alertas críticos")
    warning_alerts: int = Field(..., description="Alertas de aviso")
    info_alerts: int = Field(..., description="Alertas informativos")

# =============================================================================
# VALIDADORES GLOBAIS
# =============================================================================

@validator('bbox')
def validate_bbox(cls, v):
    """Valida bounding box"""
    if len(v) != 4:
        raise ValueError('bbox deve ter exatamente 4 valores [x1, y1, x2, y2]')
    if any(x < 0 for x in v):
        raise ValueError('bbox não pode ter valores negativos')
    if v[0] >= v[2] or v[1] >= v[3]:
        raise ValueError('bbox inválido: x1 < x2 e y1 < y2')
    return v

# =============================================================================
# CONFIGURAÇÕES DOS MODELOS
# =============================================================================

class Config:
    """Configurações dos modelos Pydantic"""
    
    # Permitir campos extras
    extra = "forbid"
    
    # Validação de tipos
    validate_assignment = True
    
    # Serialização de enums
    use_enum_values = True
    
    # Formato de datetime
    json_encoders = {
        datetime: lambda v: v.isoformat()
    }
    
    # Exemplo de uso
    schema_extra = {
        "example": {
            "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
            "processing_mode": "balanced",
            "detection_types": ["traffic_sign", "license_plate"],
            "confidence_threshold": 0.7
        }
    }