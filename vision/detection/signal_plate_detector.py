
import cv2
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging
from pathlib import Path
import torch
from ultralytics import YOLO

from .base_detector import BaseDetector
from ..preprocessing.image_preprocessor import ImagePreprocessor
from ..api.models import SignalPlateType, BoundingBox, SignalPlateDetection

logger = logging.getLogger(__name__)

class SignalPlateDetector(BaseDetector):
        Inicializa o detector de placas de sinalização
        
        Args:
            model_path: Caminho para o modelo YOLO treinado
            confidence_threshold: Limite de confiança para detecções
            iou_threshold: Limite de IoU para NMS
            device: Dispositivo para inferência (cpu, cuda, auto)
        Detecta placas de sinalização na imagem
        
        Args:
            image: Imagem de entrada (numpy array)
            confidence_threshold: Limite de confiança personalizado
            iou_threshold: Limite de IoU personalizado
            
        Returns:
            Lista de detecções de placas de sinalização
        Valida se uma detecção de placa de sinalização é válida
        
        Args:
            bbox: Bounding box [x1, y1, x2, y2]
            confidence: Confiança da detecção
            
        Returns:
            True se a detecção for válida
        Detecta tipos específicos de placas de sinalização
        
        Args:
            image: Imagem de entrada
            signal_types: Lista de tipos de sinalização para detectar
            confidence_threshold: Limite de confiança personalizado
            
        Returns:
            Lista de detecções filtradas por tipo
        Obtém estatísticas das detecções
        
        Args:
            detections: Lista de detecções
            
        Returns:
            Dicionário com estatísticas
        Melhora a qualidade das detecções usando técnicas avançadas
        
        Args:
            image: Imagem de entrada
            detections: Lista de detecções iniciais
            
        Returns:
            Lista de detecções melhoradas
        Aplica técnicas de melhoria na região da placa
        
        Args:
            plate_region: Região da placa detectada
            base_confidence: Confiança base da detecção
            
        Returns:
            Confiança melhorada
