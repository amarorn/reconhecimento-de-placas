"""
Modelos Pydantic para a API REST
================================
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

# =============================================================================
# ENUMS
# =============================================================================

class DetectionType(str, Enum):
    """Tipos de detecção disponíveis"""
    SIGNAL = "signal"
    VEHICLE = "vehicle"
    BOTH = "both"

class VehicleType(str, Enum):
    """Tipos de veículos suportados"""
    CAR = "car"
    TRUCK = "truck"
    MOTORCYCLE = "motorcycle"
    BUS = "bus"
    VAN = "van"
    TRACTOR = "tractor"

class PlateType(str, Enum):
    """Tipos de placas"""
    MERCOSUL = "mercosul"
    MERCOSUL_MOTORCYCLE = "mercosul_motorcycle"
    OLD_STANDARD = "old_standard"
    DIPLOMATIC = "diplomatic"
    OFFICIAL = "official"
    TEMPORARY = "temporary"
    SIGNAL = "signal"
    TRAFFIC_SIGN = "traffic_sign"
    STREET_SIGN = "street_sign"
    BUILDING_SIGN = "building_sign"

class SignalPlateType(str, Enum):
    """Tipos de placas de sinalização"""
    STOP = "stop"
    YIELD = "yield"
    SPEED_LIMIT = "speed_limit"
    NO_PARKING = "no_parking"
    ONE_WAY = "one_way"
    PEDESTRIAN_CROSSING = "pedestrian_crossing"
    SCHOOL_ZONE = "school_zone"
    CONSTRUCTION = "construction"
    WARNING = "warning"
    INFORMATION = "information"

# =============================================================================
# MODELOS BASE
# =============================================================================

class BaseRequest(BaseModel):
    """Modelo base para requisições"""
    image_id: Optional[str] = Field(None, description="ID único da imagem")
    confidence_threshold: float = Field(0.5, ge=0.0, le=1.0, description="Limite de confiança para detecção")
    iou_threshold: float = Field(0.45, ge=0.0, le=1.0, description="Limite de IoU para NMS")

class BaseResponse(BaseModel):
    """Modelo base para respostas"""
    success: bool = Field(..., description="Indica se a operação foi bem-sucedida")
    message: str = Field(..., description="Mensagem descritiva do resultado")
    timestamp: datetime = Field(..., description="Timestamp da operação")
    image_id: Optional[str] = Field(None, description="ID da imagem processada")
    processing_time: Optional[float] = Field(None, description="Tempo de processamento em segundos")

# =============================================================================
# MODELOS DE DETECÇÃO
# =============================================================================

class BoundingBox(BaseModel):
    """Caixa delimitadora (bounding box)"""
    x1: int = Field(..., description="Coordenada X do canto superior esquerdo")
    y1: int = Field(..., description="Coordenada Y do canto superior esquerdo")
    x2: int = Field(..., description="Coordenada X do canto inferior direito")
    y2: int = Field(..., description="Coordenada Y do canto inferior direito")

class DetectionResult(BaseModel):
    """Resultado de uma detecção"""
    bbox: BoundingBox = Field(..., description="Caixa delimitadora da detecção")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confiança da detecção")
    class_id: int = Field(..., description="ID da classe detectada")
    class_name: str = Field(..., description="Nome da classe detectada")

# =============================================================================
# MODELOS DE PLACAS DE SINALIZAÇÃO
# =============================================================================

class SignalPlateRequest(BaseRequest):
    """Requisição para detecção de placas de sinalização"""
    image: Union[str, HttpUrl] = Field(..., description="Imagem em base64 ou URL")
    signal_types: Optional[List[SignalPlateType]] = Field(None, description="Tipos de sinalização específicos para detectar")

class SignalPlateDetection(BaseModel):
    """Detecção de placa de sinalização"""
    bbox: BoundingBox = Field(..., description="Caixa delimitadora da placa")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confiança da detecção")
    plate_type: SignalPlateType = Field(..., description="Tipo da placa de sinalização")
    text: Optional[str] = Field(None, description="Texto extraído da placa")

class SignalPlateResponse(BaseResponse):
    """Resposta para detecção de placas de sinalização"""
    detections: List[SignalPlateDetection] = Field(..., description="Lista de placas detectadas")
    total_detections: int = Field(..., description="Total de placas detectadas")

# =============================================================================
# MODELOS DE PLACAS DE VEÍCULOS
# =============================================================================

class VehiclePlateRequest(BaseRequest):
    """Requisição para detecção de placas de veículos"""
    image: Union[str, HttpUrl] = Field(..., description="Imagem em base64 ou URL")
    vehicle_type: VehicleType = Field(..., description="Tipo de veículo para detecção")
    plate_types: Optional[List[PlateType]] = Field(None, description="Tipos de placas específicos para detectar")

class VehiclePlateInfo(BaseModel):
    """Informações da placa do veículo"""
    plate_type: PlateType = Field(..., description="Tipo da placa")
    vehicle_type: VehicleType = Field(..., description="Tipo do veículo")
    country: str = Field(..., description="País da placa")
    state: Optional[str] = Field(None, description="Estado/província da placa")

class VehiclePlateDetection(BaseModel):
    """Detecção de placa de veículo"""
    bbox: BoundingBox = Field(..., description="Caixa delimitadora da placa")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confiança da detecção")
    plate_number: Optional[str] = Field(None, description="Número da placa extraído")
    plate_type: VehiclePlateInfo = Field(..., description="Informações da placa")
    vehicle_type: VehicleType = Field(..., description="Tipo do veículo")
    country: str = Field(..., description="País da placa")
    state: Optional[str] = Field(None, description="Estado/província da placa")

class VehiclePlateResponse(BaseResponse):
    """Resposta para detecção de placas de veículos"""
    detections: List[VehiclePlateDetection] = Field(..., description="Lista de placas detectadas")
    total_detections: int = Field(..., description="Total de placas detectadas")
    vehicle_type: VehicleType = Field(..., description="Tipo de veículo processado")

# =============================================================================
# MODELOS DE DETECÇÃO GERAL
# =============================================================================

class DetectionRequest(BaseRequest):
    """Requisição para detecção geral"""
    image: Union[str, HttpUrl] = Field(..., description="Imagem em base64 ou URL")
    detection_type: DetectionType = Field(..., description="Tipo de detecção a ser realizada")

class DetectionResponse(BaseResponse):
    """Resposta para detecção geral"""
    results: Dict[str, Any] = Field(..., description="Resultados da detecção")

# =============================================================================
# MODELOS DE SAÚDE E STATUS
# =============================================================================

class HealthResponse(BaseModel):
    """Resposta de verificação de saúde"""
    status: str = Field(..., description="Status da API")
    timestamp: datetime = Field(..., description="Timestamp da verificação")
    version: str = Field(..., description="Versão da API")
    uptime: float = Field(..., description="Tempo de atividade em segundos")
    components: Dict[str, str] = Field(..., description="Status dos componentes")
    memory_usage: Optional[float] = Field(None, description="Uso de memória em MB")
    cpu_usage: Optional[float] = Field(None, description="Uso de CPU em porcentagem")

class PipelineStatus(BaseModel):
    """Status do pipeline de visão computacional"""
    pipeline_status: str = Field(..., description="Status do pipeline")
    last_processing_time: Optional[float] = Field(None, description="Tempo do último processamento")
    total_processed_images: int = Field(..., description="Total de imagens processadas")
    average_processing_time: Optional[float] = Field(None, description="Tempo médio de processamento")
    memory_usage: Optional[float] = Field(None, description="Uso de memória em MB")
    cpu_usage: Optional[float] = Field(None, description="Uso de CPU em porcentagem")

# =============================================================================
# MODELOS DE AUTENTICAÇÃO
# =============================================================================

class UserLogin(BaseModel):
    """Credenciais de login"""
    username: str = Field(..., description="Nome de usuário")
    password: str = Field(..., description="Senha")

class TokenResponse(BaseModel):
    """Resposta de autenticação"""
    access_token: str = Field(..., description="Token de acesso JWT")
    token_type: str = Field(..., description="Tipo do token")
    expires_in: int = Field(..., description="Tempo de expiração em segundos")
    refresh_token: str = Field(..., description="Token de renovação")

class User(BaseModel):
    """Informações do usuário"""
    user_id: str = Field(..., description="ID único do usuário")
    username: str = Field(..., description="Nome de usuário")
    email: str = Field(..., description="Email do usuário")
    is_active: bool = Field(..., description="Indica se o usuário está ativo")
    permissions: List[str] = Field(..., description="Permissões do usuário")

# =============================================================================
# MODELOS DE UPLOAD
# =============================================================================

class UploadResponse(BaseModel):
    """Resposta de upload"""
    success: bool = Field(..., description="Indica se o upload foi bem-sucedido")
    message: str = Field(..., description="Mensagem descritiva do resultado")
    image_id: str = Field(..., description="ID único da imagem enviada")
    filename: str = Field(..., description="Nome do arquivo enviado")