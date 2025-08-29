"""
Endpoints da API REST para Visão Computacional
==============================================
"""

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

# Configuração de logging
logger = logging.getLogger(__name__)

# Router principal
router = APIRouter(prefix="/api/v1", tags=["vision"])

# Instâncias dos componentes
preprocessor = ImagePreprocessor()
signal_detector = YOLODetector(model_path="models/signal_plates_yolo.pt")
vehicle_detector = YOLODetector(model_path="models/vehicle_plates_yolo.pt")
text_extractor = TextExtractor()
plate_classifier = PlateClassifier()
pipeline = VisionPipeline()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Verificação de saúde da API"""
    try:
        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            version="3.0.0",
            uptime=pipeline.get_uptime(),
            components={
                "api": "healthy",
                "pipeline": "healthy",
                "monitoring": "healthy",
                "auth": "healthy"
            },
            memory_usage=pipeline.get_memory_usage(),
            cpu_usage=pipeline.get_cpu_usage()
        )
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/detect/signal-plates", response_model=SignalPlateResponse)
async def detect_signal_plates(
    request: SignalPlateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Detecção de placas de sinalização
    
    - **image**: Imagem em base64 ou URL
    - **confidence_threshold**: Limite de confiança (0.0-1.0)
    - **iou_threshold**: Limite de IoU para NMS
    """
    try:
        logger.info(f"Detecção de placas de sinalização solicitada por {current_user.username}")
        
        # Pré-processamento da imagem
        processed_image = preprocessor.preprocess_image(request.image)
        
        # Detecção com YOLO especializado em placas de sinalização
        detections = signal_detector.detect(
            image=processed_image,
            confidence_threshold=request.confidence_threshold,
            iou_threshold=request.iou_threshold
        )
        
        # Classificação das placas detectadas
        classified_plates = []
        for detection in detections:
            plate_region = preprocessor.extract_region(processed_image, detection.bbox)
            plate_type = plate_classifier.classify_signal_plate(plate_region)
            
            classified_plates.append({
                "bbox": detection.bbox,
                "confidence": detection.confidence,
                "plate_type": plate_type,
                "text": text_extractor.extract_text(plate_region)
            })
        
        return SignalPlateResponse(
            success=True,
            message="Placas de sinalização detectadas com sucesso",
            timestamp=datetime.utcnow(),
            image_id=request.image_id,
            detections=classified_plates,
            total_detections=len(classified_plates),
            processing_time=pipeline.get_last_processing_time()
        )
        
    except Exception as e:
        logger.error(f"Erro na detecção de placas de sinalização: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect/vehicle-plates", response_model=VehiclePlateResponse)
async def detect_vehicle_plates(
    request: VehiclePlateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Detecção de placas de veículos
    
    - **image**: Imagem em base64 ou URL
    - **confidence_threshold**: Limite de confiança (0.0-1.0)
    - **iou_threshold**: Limite de IoU para NMS
    - **vehicle_type**: Tipo de veículo (car, truck, motorcycle, bus)
    """
    try:
        logger.info(f"Detecção de placas de veículos solicitada por {current_user.username}")
        
        # Pré-processamento da imagem
        processed_image = preprocessor.preprocess_image(request.image)
        
        # Detecção com YOLO especializado em placas de veículos
        detections = vehicle_detector.detect(
            image=processed_image,
            confidence_threshold=request.confidence_threshold,
            iou_threshold=request.iou_threshold
        )
        
        # Classificação das placas detectadas
        classified_plates = []
        for detection in detections:
            plate_region = preprocessor.extract_region(processed_image, detection.bbox)
            plate_info = plate_classifier.classify_vehicle_plate(
                plate_region, 
                vehicle_type=request.vehicle_type
            )
            
            classified_plates.append({
                "bbox": detection.bbox,
                "confidence": detection.confidence,
                "plate_number": text_extractor.extract_text(plate_region),
                "plate_type": plate_info.plate_type,
                "vehicle_type": plate_info.vehicle_type,
                "country": plate_info.country,
                "state": plate_info.state
            })
        
        return VehiclePlateResponse(
            success=True,
            message="Placas de veículos detectadas com sucesso",
            timestamp=datetime.utcnow(),
            image_id=request.image_id,
            detections=classified_plates,
            total_detections=len(classified_plates),
            vehicle_type=request.vehicle_type,
            processing_time=pipeline.get_last_processing_time()
        )
        
    except Exception as e:
        logger.error(f"Erro na detecção de placas de veículos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect/general", response_model=DetectionResponse)
async def detect_general(
    request: DetectionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Detecção geral (endpoint legado para compatibilidade)
    
    - **image**: Imagem em base64 ou URL
    - **detection_type**: Tipo de detecção (signal, vehicle, both)
    """
    try:
        logger.info(f"Detecção geral solicitada por {current_user.username}")
        
        # Pré-processamento da imagem
        processed_image = preprocessor.preprocess_image(request.image)
        
        results = {}
        
        if request.detection_type in ["signal", "both"]:
            # Detecção de placas de sinalização
            signal_detections = signal_detector.detect(
                image=processed_image,
                confidence_threshold=request.confidence_threshold,
                iou_threshold=request.iou_threshold
            )
            results["signal_plates"] = signal_detections
        
        if request.detection_type in ["vehicle", "both"]:
            # Detecção de placas de veículos
            vehicle_detections = vehicle_detector.detect(
                image=processed_image,
                confidence_threshold=request.confidence_threshold,
                iou_threshold=request.iou_threshold
            )
            results["vehicle_plates"] = vehicle_detections
        
        return DetectionResponse(
            success=True,
            message="Detecção geral realizada com sucesso",
            timestamp=datetime.utcnow(),
            image_id=request.image_id,
            results=results,
            processing_time=pipeline.get_last_processing_time()
        )
        
    except Exception as e:
        logger.error(f"Erro na detecção geral: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", response_model=PipelineStatus)
async def get_pipeline_status():
    """Status do pipeline de visão computacional"""
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
    """Upload de imagem para processamento"""
    try:
        logger.info(f"Upload de imagem solicitado por {current_user.username}")
        
        # Validação do arquivo
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")
        
        # Processamento do upload
        image_id = pipeline.process_upload(file)
        
        return JSONResponse(
            content={
                "success": True,
                "message": "Imagem enviada com sucesso",
                "image_id": image_id,
                "filename": file.filename
            }
        )
        
    except Exception as e:
        logger.error(f"Erro no upload de imagem: {e}")
        raise HTTPException(status_code=500, detail=str(e))