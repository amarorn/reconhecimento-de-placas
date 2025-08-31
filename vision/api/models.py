#!/usr/bin/env python3
"""
Modelos Pydantic para a API de Visão Computacional
==================================================

Este módulo define todos os modelos de dados para requisições e respostas da API.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class DetectionType(str, Enum):
    CAR = "car"
    TRUCK = "truck"
    MOTORCYCLE = "motorcycle"
    BUS = "bus"
    VAN = "van"
    TRACTOR = "tractor"


class VehicleType(str, Enum):
    CAR = "car"
    TRUCK = "truck"
    MOTORCYCLE = "motorcycle"
    BUS = "bus"
    VAN = "van"
    TRACTOR = "tractor"


class PlateType(str, Enum):
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


class SignalPlateType(str, Enum):
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


class VideoSourceType(str, Enum):
    CAMERA = "camera"
    FILE = "file"
    STREAM = "stream"


class BaseRequest(BaseModel):
    image: Union[str, HttpUrl] = Field(..., description="Imagem em base64 ou URL")
    confidence_threshold: Optional[float] = Field(0.5, ge=0.0, le=1.0, description="Limite de confiança para detecção")


class BaseResponse(BaseModel):
    success: bool = Field(..., description="Indica se a operação foi bem-sucedida")
    message: str = Field(..., description="Mensagem descritiva do resultado")
    timestamp: datetime = Field(..., description="Timestamp da operação")
    image_id: Optional[str] = Field(None, description="ID da imagem processada")
    processing_time: Optional[float] = Field(None, description="Tempo de processamento em segundos")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Descrição do erro")
    detail: Optional[str] = Field(None, description="Detalhes adicionais do erro")
    timestamp: datetime = Field(..., description="Timestamp do erro")


class BoundingBox(BaseModel):
    x1: int = Field(..., description="Coordenada X do canto superior esquerdo")
    y1: int = Field(..., description="Coordenada Y do canto superior esquerdo")
    x2: int = Field(..., description="Coordenada X do canto inferior direito")
    y2: int = Field(..., description="Coordenada Y do canto inferior direito")


class DetectionResult(BaseModel):
    bbox: BoundingBox = Field(..., description="Caixa delimitadora da detecção")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confiança da detecção")
    class_name: str = Field(..., description="Nome da classe detectada")
    class_id: int = Field(..., description="ID da classe detectada")


class VideoFrameResult(BaseModel):
    frame_number: int = Field(..., description="Número do frame")
    timestamp: float = Field(..., description="Timestamp do frame em segundos")
    detections: List[DetectionResult] = Field(default_factory=list, description="Detecções no frame")


class ImageRequest(BaseModel):
    """Modelo para requisição de processamento de imagem"""
    image_data: str = Field(..., description="Imagem em formato base64")
    save_results: bool = Field(False, description="Se deve salvar os resultados")
    return_annotated_image: bool = Field(False, description="Se deve retornar imagem anotada")
    return_confidence_scores: bool = Field(False, description="Se deve retornar scores de confiança")
    return_processing_time: bool = Field(False, description="Se deve retornar tempo de processamento")


class ProcessResponse(BaseModel):
    """Modelo para resposta de processamento (imagem ou vídeo)"""
    result: Dict[str, Any] = Field(..., description="Resultados do processamento")
    timestamp: str = Field(..., description="Timestamp da resposta")
    api_version: str = Field(..., description="Versão da API")


class SignalPlateRequest(BaseRequest):
    plate_types: Optional[List[PlateType]] = Field(None, description="Tipos de placas específicos para detectar")


class SignalPlateDetection(BaseModel):
    bbox: BoundingBox = Field(..., description="Caixa delimitadora da placa")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confiança da detecção")
    plate_type: SignalPlateType = Field(..., description="Tipo da placa de sinalização")
    text: Optional[str] = Field(None, description="Texto extraído da placa")


class SignalPlateResponse(BaseResponse):
    detections: List[SignalPlateDetection] = Field(..., description="Lista de placas de sinalização detectadas")
    total_detections: int = Field(..., description="Total de detecções realizadas")


class VehiclePlateRequest(BaseRequest):
    vehicle_type: VehicleType = Field(..., description="Tipo de veículo para detecção")


class VehiclePlateInfo(BaseModel):
    bbox: BoundingBox = Field(..., description="Caixa delimitadora da placa")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confiança da detecção")
    plate_number: Optional[str] = Field(None, description="Número da placa extraído")
    vehicle_type: VehicleType = Field(..., description="Tipo do veículo")
    country: str = Field(..., description="País da placa")
    state: Optional[str] = Field(None, description="Estado/província da placa")


class VehiclePlateDetection(BaseModel):
    vehicle_bbox: BoundingBox = Field(..., description="Caixa delimitadora do veículo")
    plate_bbox: BoundingBox = Field(..., description="Caixa delimitadora da placa")
    vehicle_confidence: float = Field(..., ge=0.0, le=1.0, description="Confiança da detecção do veículo")
    plate_confidence: float = Field(..., ge=0.0, le=1.0, description="Confiança da detecção da placa")
    plate_info: VehiclePlateInfo = Field(..., description="Informações da placa")


class VehiclePlateResponse(BaseResponse):
    detections: List[VehiclePlateDetection] = Field(..., description="Lista de veículos e placas detectados")
    total_vehicles: int = Field(..., description="Total de veículos detectados")
    total_plates: int = Field(..., description="Total de placas detectadas")


class DetectionRequest(BaseRequest):
    detection_type: DetectionType = Field(..., description="Tipo de detecção a ser realizada")


class DetectionResponse(BaseResponse):
    detections: List[DetectionResult] = Field(..., description="Lista de detecções realizadas")
    total_detections: int = Field(..., description="Total de detecções realizadas")


class VideoRequest(BaseModel):
    source_type: VideoSourceType = Field(..., description="Tipo de fonte de vídeo")
    source: Union[str, HttpUrl] = Field(..., description="Fonte do vídeo (URL, caminho do arquivo ou ID da câmera)")
    frame_interval: Optional[int] = Field(1, description="Intervalo entre frames para processamento")
    max_frames: Optional[int] = Field(None, description="Número máximo de frames para processar")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Status da API")
    timestamp: datetime = Field(..., description="Timestamp da verificação")
    version: str = Field(..., description="Versão da API")
    uptime: float = Field(..., description="Tempo de atividade em segundos")
    components: Dict[str, str] = Field(..., description="Status dos componentes")
    memory_usage: Optional[float] = Field(None, description="Uso de memória em MB")
    cpu_usage: Optional[float] = Field(None, description="Uso de CPU em porcentagem")


class PipelineStatus(BaseModel):
    is_running: bool = Field(..., description="Indica se o pipeline está rodando")
    current_task: Optional[str] = Field(None, description="Tarefa atual sendo executada")
    progress: Optional[float] = Field(None, ge=0.0, le=1.0, description="Progresso da tarefa atual")
    total_processed: int = Field(..., description="Total de itens processados")
    errors: List[str] = Field(default_factory=list, description="Lista de erros encontrados")


class UserLogin(BaseModel):
    username: str = Field(..., description="Nome de usuário")
    password: str = Field(..., description="Senha")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="Token de acesso")
    token_type: str = Field(..., description="Tipo do token")
    expires_in: int = Field(..., description="Tempo de expiração em segundos")


class User(BaseModel):
    """Modelo para usuário autenticado"""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class Token(BaseModel):
    """Modelo para token de autenticação"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Modelo para dados do token"""
    username: Optional[str] = None


class UploadResponse(BaseModel):
    file_id: str = Field(..., description="ID único do arquivo")
    filename: str = Field(..., description="Nome do arquivo")
    file_size: int = Field(..., description="Tamanho do arquivo em bytes")
    upload_time: datetime = Field(..., description="Timestamp do upload")
    status: str = Field(..., description="Status do upload")
