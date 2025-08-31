
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging
from datetime import datetime
from ..core.vision_pipeline import VisionPipeline
from ..detection.yolo_detector import YOLODetector
from ..ocr.text_extractor import TextExtractor
from ..ocr.plate_classifier import PlateClassifier
from ..preprocessing.image_preprocessor import ImagePreprocessor
from ..api.models import (
    DetectionRequest, DetectionResponse, 
    SignalPlateRequest, SignalPlateResponse,
    VehiclePlateRequest, VehiclePlateResponse,
    HealthResponse, PipelineStatus
)
from ..api.auth import get_current_user
from ..api.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["vision"])

preprocessor_config = {
    'resize_enabled': True,
    'target_size': (640, 640),
    'denoising_enabled': True,
    'contrast_enhancement': True,
    'normalization': True,
    'additional_filters': False
}
preprocessor = ImagePreprocessor(preprocessor_config)

signal_detector_config = {
    'weights_path': 'yolov8n.pt',
    'device': 'auto',
    'confidence_threshold': 0.5,
    'nms_threshold': 0.4,
    'input_size': (640, 640)
}

vehicle_detector_config = {
    'weights_path': 'yolov8n.pt',
    'device': 'auto',
    'confidence_threshold': 0.5,
    'nms_threshold': 0.4,
    'input_size': (640, 640)
}

signal_detector = YOLODetector(signal_detector_config)
vehicle_detector = YOLODetector(vehicle_detector_config)

text_extractor_config = {
    'type': 'PADDLEOCR',
    'language': 'pt',
    'use_gpu': False,
    'use_angle_cls': True
}

pipeline_config = {
    'max_workers': 2,
    'batch_size': 4
}

text_extractor = TextExtractor(text_extractor_config)
plate_classifier = PlateClassifier()
pipeline = VisionPipeline(pipeline_config)

@router.get("/health", response_model=HealthResponse)
async def health_check():
    Detecção de placas de sinalização
    
    - **image**: Imagem em base64 ou URL
    - **confidence_threshold**: Limite de confiança (0.0-1.0)
    - **iou_threshold**: Limite de IoU para NMS
    Detecção de placas de veículos
    
    - **image**: Imagem em base64 ou URL
    - **confidence_threshold**: Limite de confiança (0.0-1.0)
    - **iou_threshold**: Limite de IoU para NMS
    - **vehicle_type**: Tipo de veículo (car, truck, motorcycle, bus)
    Detecção geral (endpoint legado para compatibilidade)
    
    - **image**: Imagem em base64 ou URL
    - **detection_type**: Tipo de detecção (signal, vehicle, both)
    try:
        return PipelineStatus(
            pipeline_status="active",
            last_processing_time=pipeline.get_last_processing_time(),
            total_processed_images=pipeline.get_total_processed_images(),
            average_processing_time=pipeline.get_average_processing_time(),
            memory_usage=pipeline.get_memory_usage(),
            cpu_usage=pipeline.get_cpu_usage()
        )
    except Exception as e:
        logger.error(f"Erro ao obter status do pipeline: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
