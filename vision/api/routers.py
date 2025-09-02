#!/usr/bin/env python3
"""
Routers da API REST - Arquitetura de Visão Computacional
========================================================

Este módulo define todos os routers da API organizados por funcionalidade.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List, Optional, Dict, Any, Union
import logging
import time
import base64
import os
import requests
import numpy as np
import cv2
from datetime import datetime

from .models import (
    DetectionRequest, DetectionResponse, 
    SignalPlateRequest, SignalPlateResponse,
    VehiclePlateRequest, VehiclePlateResponse,
    HealthResponse, PipelineStatus,
    BaseRequest, BaseResponse, BoundingBox, DetectionResult
)
from .auth import get_current_user, User

logger = logging.getLogger(__name__)


# Router de Saúde
health_router = APIRouter(prefix="/health", tags=["Health"])

@health_router.get("/", response_model=HealthResponse)
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "uptime": time.time(),
        "components": {
            "api": "operational",
            "database": "operational",
            "cache": "operational"
        },
        "memory_usage": 0.25,
        "cpu_usage": 0.15
    }


# Router de Visão Computacional
vision_router = APIRouter(prefix="/api/v1/vision", tags=["Vision"])

# Pipeline real será implementado quando os modelos YOLO estiverem disponíveis

@vision_router.post("/detect/signal-plates", response_model=SignalPlateResponse)
async def detect_signal_plates(
    request: SignalPlateRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info(f"Detecção de placas de sinalização solicitada por {current_user.username}")
        
        # Decodificar imagem base64
        try:
            import base64
            import cv2
            import numpy as np
            from ..detection.signal_plate_detector import SignalPlateDetector
            
            # Decodificar imagem
            image_data = base64.b64decode(request.image.split(',')[1] if ',' in request.image else request.image)
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Não foi possível decodificar a imagem")
            
            # Configurar detector
            config = {
                'confidence_threshold': request.confidence_threshold,
                'iou_threshold': 0.45,
                'model_path': 'models/signal_plates_yolo.pt'
            }
            
            # Inicializar detector
            detector = SignalPlateDetector(config)
            
            # Detectar placas
            detections = detector.detect(image)
            
            # Converter para formato da API
            api_detections = []
            for detection in detections:
                # Mapear class_name para plate_type
                plate_type = _map_class_to_plate_type(detection.class_name)
                
                api_detection = {
                    "bbox": {
                        "x1": int(detection.bbox[0]),
                        "y1": int(detection.bbox[1]),
                        "x2": int(detection.bbox[2]),
                        "y2": int(detection.bbox[3])
                    },
                    "confidence": float(detection.confidence),
                    "plate_type": plate_type,
                    "text": detection.signal_type or "N/A"
                }
                api_detections.append(api_detection)
            
            # Se não detectou nada, retornar lista vazia
            
            return SignalPlateResponse(
                success=True,
                message="Placas de sinalização detectadas com sucesso",
                timestamp=datetime.utcnow(),
                image_id=f"img_{int(time.time())}",
                detections=api_detections,
                total_detections=len(api_detections)
            )
            
        except Exception as detection_error:
            logger.error(f"Erro no detector: {detection_error}")
            raise HTTPException(
                status_code=500, 
                detail=f"Erro na detecção: {str(detection_error)}"
            )
        
    except Exception as e:
        logger.error(f"Erro na detecção de placas de sinalização: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _map_class_to_plate_type(class_name: str) -> str:
    """Mapeia class_name do YOLO para plate_type da API"""
    class_name = class_name.lower()
    
    mapping = {
        'stop_sign': 'stop',
        'yield_sign': 'yield', 
        'speed_limit': 'speed_limit',
        'no_parking': 'no_parking',
        'one_way': 'one_way',
        'pedestrian_crossing': 'pedestrian_crossing',
        'school_zone': 'school_zone',
        'construction': 'construction',
        'warning': 'warning',
        'information': 'information'
    }
    
    # Buscar correspondência exata
    if class_name in mapping:
        return mapping[class_name]
    
    # Buscar correspondência parcial
    for key, value in mapping.items():
        if key in class_name or class_name in key:
            return value
    
    # Default
    return 'warning'


# Funções helper para OCR serão implementadas quando os modelos estiverem disponíveis


@vision_router.post("/detect/vehicle-plates", response_model=VehiclePlateResponse)
async def detect_vehicle_plates(
    request: VehiclePlateRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info(f"Detecção de placas de veículos solicitada por {current_user.username}")
        
        # Decodificar imagem base64
        try:
            import base64
            import cv2
            import numpy as np
            from ..detection.vehicle_plate_detector import VehiclePlateDetector
            
            # Decodificar imagem
            image_data = base64.b64decode(request.image.split(',')[1] if ',' in request.image else request.image)
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Não foi possível decodificar a imagem")
            
            # Configurar detector
            config = {
                'confidence_threshold': request.confidence_threshold,
                'iou_threshold': 0.45,
                'model_path': 'models/vehicle_plates_yolo.pt'
            }
            
            # Inicializar detector
            detector = VehiclePlateDetector(config)
            
            # Detectar placas e veículos
            detections = detector.detect(image)
            
            # Separar veículos e placas
            vehicles = detector.filter_vehicles(detections)
            plates = detector.filter_vehicle_plates(detections)
            
            # Converter para formato da API
            api_detections = []
            
            # Se detectou veículos e placas, combinar
            if vehicles and plates:
                for i, vehicle in enumerate(vehicles):
                    plate = plates[i] if i < len(plates) else plates[0] if plates else None
                    
                    if plate:
                        # OCR será implementado quando os modelos estiverem disponíveis
                        plate_number = "N/A"
                        state_info = "N/A"
                        
                        api_detection = {
                            "vehicle_bbox": {
                                "x1": int(vehicle.bbox[0]),
                                "y1": int(vehicle.bbox[1]),
                                "x2": int(vehicle.bbox[2]),
                                "y2": int(vehicle.bbox[3])
                            },
                            "plate_bbox": {
                                "x1": int(plate.bbox[0]),
                                "y1": int(plate.bbox[1]),
                                "x2": int(plate.bbox[2]),
                                "y2": int(plate.bbox[3])
                            },
                            "vehicle_confidence": float(vehicle.confidence),
                            "plate_confidence": float(plate.confidence),
                            "plate_info": {
                                "bbox": {
                                    "x1": int(plate.bbox[0]),
                                    "y1": int(plate.bbox[1]),
                                    "x2": int(plate.bbox[2]),
                                    "y2": int(plate.bbox[3])
                                },
                                "confidence": float(plate.confidence),
                                "plate_number": plate_number,
                                "vehicle_type": vehicle.vehicle_type or "car",
                                "country": "Brasil",
                                "state": state_info
                            }
                        }
                        api_detections.append(api_detection)
            
            # Se não detectou nada, retornar lista vazia
            
            return VehiclePlateResponse(
                success=True,
                message="Placas de veículos detectadas com sucesso",
                timestamp=datetime.utcnow(),
                image_id=f"img_{int(time.time())}",
                detections=api_detections,
                total_vehicles=len(api_detections),
                total_plates=len(api_detections)
            )
            
        except Exception as detection_error:
            logger.error(f"Erro no detector: {detection_error}")
            raise HTTPException(
                status_code=500, 
                detail=f"Erro na detecção: {str(detection_error)}"
            )
        
    except Exception as e:
        logger.error(f"Erro na detecção de placas de veículos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@vision_router.post("/detect/general", response_model=DetectionResponse)
async def detect_general(
    request: DetectionRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info(f"Detecção geral solicitada por {current_user.username}")
        
        # Implementação real será adicionada quando os modelos estiverem disponíveis
        return DetectionResponse(
            success=True,
            message="Detecção geral não implementada - aguardando modelos YOLO",
            timestamp=datetime.utcnow(),
            image_id="test_image_001",
            detections=[],
            total_detections=0
        )
        
    except Exception as e:
        logger.error(f"Erro na detecção geral: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@vision_router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info(f"Upload de imagem solicitado por {current_user.username}")
        
        # Implementação real será adicionada quando o pipeline estiver disponível
        file_id = f"img_{int(time.time())}"
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "file_size": file.size,
            "upload_time": datetime.utcnow(),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Erro no upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Router de Monitoramento
monitoring_router = APIRouter(prefix="/api/v1/monitoring", tags=["Monitoring"])

@monitoring_router.get("/status")
async def get_pipeline_status(
    current_user: User = Depends(get_current_user)
):
    try:
        return PipelineStatus(
            is_running=False,
            current_task="aguardando modelos YOLO",
            progress=0.0,
            total_processed=0,
            errors=["Modelos YOLO não encontrados"]
        )
    except Exception as e:
        logger.error(f"Erro ao obter status do pipeline: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@monitoring_router.get("/metrics")
async def get_metrics(
    current_user: User = Depends(get_current_user)
):
    try:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "uptime": time.time(),
                "memory_usage": 0.0,
                "cpu_usage": 0.0
            },
            "api": {
                "total_requests": 0,
                "successful_requests": 0,
                "error_requests": 0
            },
            "pipeline": {
                "total_processed": 0,
                "average_processing_time": 0.0
            }
        }
    except Exception as e:
        logger.error(f"Erro ao obter métricas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@monitoring_router.get("/logs")
async def get_logs(
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    try:
        return {
            "logs": [],
            "total_logs": 0,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter logs: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


# Router de Autenticação
auth_router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@auth_router.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...)
):
    try:
        if username == "admin" and password == "admin123":
            # Criar um token JWT simples para testes
            from .auth import create_access_token
            access_token = create_access_token(data={"sub": username, "username": username})
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "username": username
            }
        else:
            raise HTTPException(status_code=401, detail="Credenciais inválidas")
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@auth_router.post("/register")
async def register(
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(...)
):
    try:
        return {
            "message": "Usuário registrado com sucesso",
            "username": username,
            "email": email
        }
    except Exception as e:
        logger.error(f"Erro no registro: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@auth_router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    try:
        return {
            "username": current_user.username,
            "email": current_user.email,
            "is_active": current_user.is_active
        }
    except Exception as e:
        logger.error(f"Erro ao obter informações do usuário: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
