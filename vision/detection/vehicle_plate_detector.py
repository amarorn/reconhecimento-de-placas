
import cv2
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging
from pathlib import Path
import torch
from ultralytics import YOLO

from .base_detector import BaseDetector
from ..preprocessing.image_preprocessor import ImagePreprocessor
from ..api.models import VehicleType, PlateType, BoundingBox, VehiclePlateDetection, VehiclePlateInfo

logger = logging.getLogger(__name__)

class VehiclePlateDetector(BaseDetector):
        Inicializa o detector de placas de veículos
        
        Args:
            model_path: Caminho para o modelo YOLO treinado
            confidence_threshold: Limite de confiança para detecções
            iou_threshold: Limite de IoU para NMS
            device: Dispositivo para inferência (cpu, cuda, auto)
        Detecta placas de veículos na imagem
        
        Args:
            image: Imagem de entrada (numpy array)
            vehicle_type: Tipo específico de veículo para detectar
            confidence_threshold: Limite de confiança personalizado
            iou_threshold: Limite de IoU personalizado
            
        Returns:
            Lista de detecções de placas de veículos
        Valida se uma detecção de veículo é válida
        
        Args:
            bbox: Bounding box [x1, y1, x2, y2]
            confidence: Confiança da detecção
            target_vehicle_type: Tipo de veículo específico para validar
            
        Returns:
            True se a detecção for válida
        Valida se uma detecção de placa é válida
        
        Args:
            bbox: Bounding box [x1, y1, x2, y2]
            confidence: Confiança da detecção
            
        Returns:
            True se a detecção for válida
        Extrai informações do veículo detectado
        
        Args:
            class_id: ID da classe do veículo
            bbox: Bounding box do veículo
            
        Returns:
            Dicionário com informações do veículo
        Extrai informações da placa detectada
        
        Args:
            class_id: ID da classe da placa
            bbox: Bounding box da placa
            confidence: Confiança da detecção
            
        Returns:
            Dicionário com informações da placa
        Agrupa veículos com suas respectivas placas
        
        Args:
            detections: Lista de detecções de veículos e placas
            
        Returns:
            Lista de detecções agrupadas
        Encontra a placa mais próxima de um veículo
        
        Args:
            vehicle: Informações do veículo
            plates: Lista de placas detectadas
            
        Returns:
            Placa mais próxima ou None
        center_x = (bbox[0] + bbox[2]) / 2
        center_y = (bbox[1] + bbox[3]) / 2
        return (center_x, center_y)
    
    def _calculate_distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        Detecta placas de tipos específicos de veículos
        
        Args:
            image: Imagem de entrada
            vehicle_types: Lista de tipos de veículos para detectar
            plate_types: Lista de tipos de placas para detectar
            confidence_threshold: Limite de confiança personalizado
            
        Returns:
            Lista de detecções filtradas
        Obtém estatísticas das detecções
        
        Args:
            detections: Lista de detecções
            
        Returns:
            Dicionário com estatísticas
