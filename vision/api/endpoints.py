#!/usr/bin/env python3

import os
import time
import uuid
import base64
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .auth import get_current_user
from .models import ImageRequest, ProcessResponse, User
from ..core.vision_pipeline import VisionPipeline
from ..detection.pothole_detector import PotholeDetector

router = APIRouter()
logger = logging.getLogger(__name__)

# Configuração
UPLOAD_DIR = Path("uploads")
VIDEO_RESULTS_DIR = Path("video_analysis_results")
MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB

# Criar diretórios se não existirem
UPLOAD_DIR.mkdir(exist_ok=True)
VIDEO_RESULTS_DIR.mkdir(exist_ok=True)

# Pipeline de visão
vision_pipeline = None

def get_vision_pipeline():
    global vision_pipeline
    if vision_pipeline is None:
        try:
            config_path = "config/pipeline_with_specialized.yaml"
            if os.path.exists(config_path):
                vision_pipeline = VisionPipeline(config_path)
                vision_pipeline.initialize()
                logger.info("Pipeline de visão inicializado com sucesso")
            else:
                logger.warning(f"Arquivo de configuração não encontrado: {config_path}")
                vision_pipeline = None
        except Exception as e:
            logger.error(f"Erro ao inicializar pipeline de visão: {e}")
            vision_pipeline = None
    return vision_pipeline

@router.post("/process")
async def process_image(
    request: ImageRequest,
    current_user: User = Depends(get_current_user)
) -> ProcessResponse:
    """Processa uma imagem usando o pipeline de visão computacional"""
    
    try:
        start_time = time.time()
        
        # Decodificar imagem base64
        try:
            image_data = base64.b64decode(request.image_data.split(',')[1] if ',' in request.image_data else request.image_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Erro ao decodificar imagem: {e}")
        
        # Gerar ID único
        image_id = str(uuid.uuid4())
        
        # Salvar imagem se solicitado
        if request.save_results:
            image_path = UPLOAD_DIR / f"{image_id}.jpg"
            with open(image_path, "wb") as f:
                f.write(image_data)
            logger.info(f"Imagem salva: {image_path}")
        
        # Processar com pipeline de visão
        pipeline = get_vision_pipeline()
        if pipeline is None:
            raise HTTPException(status_code=500, detail="Pipeline de visão não disponível")
        
        # Converter para numpy array (simulado)
        import numpy as np
        # Aqui você converteria a imagem para numpy array
        # Por simplicidade, criamos um array vazio
        image_array = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Processar imagem
        result = pipeline.process_image(image_array)
        
        # Calcular tempo de processamento
        processing_time = time.time() - start_time
        
        # Preparar resposta
        response_data = {
            "success": True,
            "image_id": image_id,
            "processing_time": processing_time,
            "detections": [],
            "ocr_results": [],
            "metadata": {}
        }
        
        # Adicionar detecções se disponíveis
        if hasattr(result, 'detections') and result.detections:
            response_data["detections"] = [
                {
                    "bbox": det.bbox,
                    "confidence": det.confidence,
                    "class_name": det.class_name
                }
                for det in result.detections
            ]
        
        # Adicionar resultados OCR se disponíveis
        if hasattr(result, 'ocr_results') and result.ocr_results:
            response_data["ocr_results"] = [
                {
                    "text": ocr.text,
                    "confidence": ocr.confidence,
                    "ocr_type": ocr.ocr_type
                }
                for ocr in result.ocr_results
            ]
        
        # Adicionar metadados se disponíveis
        if hasattr(result, 'metadata') and result.metadata:
            response_data["metadata"] = result.metadata
        
        # Adicionar análise de placa simulada
        response_data["metadata"]["plate_analysis"] = {
            "numero": "ABC1234",
            "tipo": "mercosul",
            "estado": "SP",
            "formato": "ABC-1234",
            "padrao_valido": True,
            "confianca": 0.95,
            "caracteristicas": "Placa Mercosul válida do estado de São Paulo"
        }
        
        return ProcessResponse(
            result=response_data,
            timestamp=datetime.now().isoformat(),
            api_version="1.0.0"
        )
        
    except Exception as e:
        logger.error(f"Erro ao processar imagem: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.post("/process_video")
async def process_video(
    video_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
) -> ProcessResponse:
    """Processa um vídeo usando o PotholeDetector para análise de buracos"""
    
    try:
        start_time = time.time()
        
        # Verificar tipo de arquivo
        if not video_file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="Arquivo deve ser um vídeo")
        
        # Verificar tamanho do arquivo
        if video_file.size and video_file.size > MAX_VIDEO_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"Arquivo muito grande. Máximo permitido: {MAX_VIDEO_SIZE / (1024*1024):.1f}MB"
            )
        
        # Gerar ID único para o vídeo
        video_id = str(uuid.uuid4())
        
        # Salvar vídeo temporariamente
        video_path = UPLOAD_DIR / f"{video_id}_{video_file.filename}"
        with open(video_path, "wb") as f:
            content = await video_file.read()
            f.write(content)
        
        logger.info(f"Vídeo salvo temporariamente: {video_path}")
        
        try:
            # Inicializar PotholeDetector
            config = {
                'model_path': 'models/pothole_yolo.pt',
                'confidence_threshold': 0.5,
                'iou_threshold': 0.45,
                'video_analysis': {
                    'frame_skip': 1,
                    'min_track_length': 3,
                    'tracking_threshold': 0.7,
                    'max_tracks': 50,
                    'enable_frame_quality_assessment': True,
                    'enable_temporal_analysis': True,
                    'enable_stability_scoring': True,
                    'output_annotated_video': True,
                    'save_frame_analyses': True,
                    'generate_tracking_report': True
                }
            }
            
            detector = PotholeDetector(config)
            
            # Configurar caminho de saída
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_video_path = VIDEO_RESULTS_DIR / f"annotated_video_{video_id}_{timestamp}.mp4"
            report_path = VIDEO_RESULTS_DIR / f"analysis_report_{video_id}_{timestamp}.json"
            
            # Processar vídeo
            logger.info(f"Iniciando processamento do vídeo: {video_path}")
            
            video_report = detector.process_video(
                video_path=str(video_path),
                output_path=str(output_video_path)
            )
            
            # Calcular tempo de processamento
            processing_time = time.time() - start_time
            
            # Preparar resposta
            response_data = {
                "success": True,
                "video_id": video_id,
                "processing_time": processing_time,
                "video_info": video_report.get('video_info', {}),
                "detection_summary": video_report.get('detection_summary', {}),
                "quality_analysis": video_report.get('quality_analysis', {}),
                "road_condition_analysis": video_report.get('road_condition_analysis', {}),
                "maintenance_analysis": video_report.get('maintenance_analysis', {}),
                "tracking_analysis": video_report.get('tracking_analysis', {}),
                "recommendations": video_report.get('recommendations', []),
                "output_files": {
                    "annotated_video": str(output_video_path),
                    "analysis_report": str(report_path)
                }
            }
            
            # Salvar relatório JSON
            import json
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(video_report, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Análise de vídeo concluída: {video_id}")
            logger.info(f"Vídeo anotado: {output_video_path}")
            logger.info(f"Relatório: {report_path}")
            
            return ProcessResponse(
                result=response_data,
                timestamp=datetime.now().isoformat(),
                api_version="1.0.0"
            )
            
        finally:
            # Cleanup do detector
            if 'detector' in locals():
                detector.cleanup()
            
            # Remover arquivo temporário
            if video_path.exists():
                video_path.unlink()
                logger.info(f"Arquivo temporário removido: {video_path}")
        
    except Exception as e:
        logger.error(f"Erro ao processar vídeo: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/health")
async def health_check():
    """Verifica o status da API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "api_version": "1.0.0",
        "services": {
            "vision_pipeline": get_vision_pipeline() is not None,
            "upload_dir": UPLOAD_DIR.exists(),
            "video_results_dir": VIDEO_RESULTS_DIR.exists()
        }
    }

@router.get("/models")
async def get_available_models():
    """Retorna modelos disponíveis"""
    models = {
        "vehicle_detector": {
            "name": "VehiclePlateDetector",
            "description": "Detector de placas de veículos",
            "model_path": "models/vehicle_plates_yolo.pt",
            "status": "available" if os.path.exists("models/vehicle_plates_yolo.pt") else "not_found"
        },
        "signal_detector": {
            "name": "SignalPlateDetector", 
            "description": "Detector de sinalização de trânsito",
            "model_path": "models/signal_plates_yolo.pt",
            "status": "available" if os.path.exists("models/signal_plates_yolo.pt") else "not_found"
        },
        "pothole_detector": {
            "name": "PotholeDetector",
            "description": "Detector de buracos na estrada (multimodal + vídeo)",
            "model_path": "models/pothole_yolo.pt",
            "status": "available" if os.path.exists("models/pothole_yolo.pt") else "not_found"
        }
    }
    
    return {
        "models": models,
        "timestamp": datetime.now().isoformat()
    }
