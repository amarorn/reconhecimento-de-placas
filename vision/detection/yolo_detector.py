#!/usr/bin/env python3
"""
Detector YOLO para Visão Computacional
======================================

Detector baseado em YOLO para detecção de objetos em imagens.
"""

import cv2
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
import time

try:
    from ultralytics import YOLO
    import torch
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    YOLO = None
    torch = None

@dataclass
class DetectionResult:
    """Resultado de uma detecção"""
    bbox: Tuple[int, int, int, int]  # (x, y, w, h)
    confidence: float
    class_id: int
    class_name: str
    area: int
    center: Tuple[int, int]

@dataclass
class DetectionBatchResult:
    """Resultado de detecção em lote"""
    detections: List[DetectionResult]
    processing_time: float
    image_shape: Tuple[int, int, int]
    total_detections: int

class YOLODetector:
    """Detector YOLO para visão computacional"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = None
        self.class_names = []
        self.device = self._get_device()
        self.initialize()
    
    def _get_device(self) -> str:
        """Determina o melhor dispositivo disponível"""
        if not torch:
            return 'cpu'
        
        if torch.cuda.is_available():
            return 'cuda'
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return 'mps'
        else:
            return 'cpu'
    
    def initialize(self):
        """Inicializa o modelo YOLO"""
        try:
            if not YOLO_AVAILABLE:
                self.logger.warning("YOLO não está disponível, usando detector simulado")
                return
            
            model_path = self.config.get('model_path', 'yolov8n.pt')
            self.model = YOLO(model_path)
            
            if hasattr(self.model, 'names'):
                self.class_names = list(self.model.names.values())
            else:
                self.class_names = [
                    'traffic_sign', 'vehicle_plate', 'vehicle', 'person',
                    'bicycle', 'motorcycle', 'car', 'bus', 'truck'
                ]
            
            self.logger.info(f"Modelo YOLO inicializado: {model_path}")
            self.logger.info(f"Classes carregadas: {self.class_names}")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar modelo YOLO: {e}")
            self.model = None
    
    def detect(self, image: np.ndarray) -> List[DetectionResult]:
        """Executa detecção na imagem"""
        if self.model is None:
            return self._simulate_detection(image)
        
        try:
            start_time = time.time()
            
            results = self.model(image, verbose=False)
            result = results[0] if results else None
            
            if result is None or result.boxes is None:
                return []
            
            detections = []
            boxes = result.boxes
            
            for i in range(len(boxes)):
                x1, y1, x2, y2 = boxes.xyxy[i].cpu().numpy()
                confidence = float(boxes.conf[i].cpu().numpy())
                class_id = int(boxes.cls[i].cpu().numpy())
                
                x, y, w, h = int(x1), int(y1), int(x2 - x1), int(y2 - y1)
                
                class_name = self.class_names[class_id] if class_id < len(self.class_names) else f"class_{class_id}"
                
                area = w * h
                center = (x + w // 2, y + h // 2)
                
                detection = DetectionResult(
                    bbox=(x, y, w, h),
                    confidence=confidence,
                    class_id=class_id,
                    class_name=class_name,
                    area=area,
                    center=center
                )
                
                detections.append(detection)
            
            processing_time = time.time() - start_time
            self.logger.debug(f"Detecção concluída em {processing_time:.3f}s: {len(detections)} objetos")
            
            return detections
            
        except Exception as e:
            self.logger.error(f"Erro na detecção YOLO: {e}")
            return self._simulate_detection(image)
    
    def _simulate_detection(self, image: np.ndarray) -> List[DetectionResult]:
        """Simula detecção quando YOLO não está disponível"""
        h, w = image.shape[:2]
        
        # Simular algumas detecções
        detections = []
        
        # Detecção simulada 1
        detections.append(DetectionResult(
            bbox=(w//4, h//4, w//4, h//4),
            confidence=0.85,
            class_id=0,
            class_name='vehicle_plate',
            area=(w//4) * (h//4),
            center=(w//4 + w//8, h//4 + h//8)
        ))
        
        # Detecção simulada 2
        detections.append(DetectionResult(
            bbox=(w//2, h//2, w//6, h//6),
            confidence=0.72,
            class_id=1,
            class_name='traffic_sign',
            area=(w//6) * (h//6),
            center=(w//2 + w//12, h//2 + h//12)
        ))
        
        self.logger.info("Usando detecção simulada")
        return detections
    
    def detect_traffic_signs(self, image: np.ndarray) -> List[DetectionResult]:
        """Detecta especificamente placas de sinalização"""
        all_detections = self.detect(image)
        
        traffic_signs = [
            det for det in all_detections
            if det.class_name in ['traffic_sign', 'sign', 'stop_sign', 'yield_sign'] or
               'sign' in det.class_name.lower()
        ]
        
        return traffic_signs
    
    def detect_vehicle_plates(self, image: np.ndarray) -> List[DetectionResult]:
        """Detecta especificamente placas de veículos"""
        all_detections = self.detect(image)
        
        vehicle_plates = [
            det for det in all_detections
            if det.class_name in ['vehicle_plate', 'plate', 'license_plate'] or
               'plate' in det.class_name.lower() or
               'license' in det.class_name.lower()
        ]
        
        return vehicle_plates
    
    def detect_vehicles(self, image: np.ndarray, min_area: int = 5000, max_area: int = 100000) -> List[DetectionResult]:
        """Detecta veículos com filtro de área"""
        all_detections = self.detect(image)
        
        vehicles = [
            det for det in all_detections
            if det.class_name in ['vehicle', 'car', 'truck', 'bus', 'motorcycle'] and
               min_area <= det.area <= max_area
        ]
        
        return vehicles
    
    def filter_detections_by_confidence(self, detections: List[DetectionResult], 
                                      min_confidence: float = 0.5) -> List[DetectionResult]:
        """Filtra detecções por confiança mínima"""
        return [det for det in detections if det.confidence >= min_confidence]
    
    def get_detection_statistics(self, detections: List[DetectionResult]) -> Dict[str, Any]:
        """Retorna estatísticas das detecções"""
        if not detections:
            return {
                'total_detections': 0,
                'average_confidence': 0.0,
                'class_distribution': {},
                'size_distribution': {}
            }
        
        confidences = [det.confidence for det in detections]
        class_counts = {}
        size_ranges = {'small': 0, 'medium': 0, 'large': 0}
        
        for det in detections:
            class_counts[det.class_name] = class_counts.get(det.class_name, 0) + 1
            
            if det.area < 5000:
                size_ranges['small'] += 1
            elif det.area < 20000:
                size_ranges['medium'] += 1
            else:
                size_ranges['large'] += 1
        
        return {
            'total_detections': len(detections),
            'average_confidence': np.mean(confidences),
            'min_confidence': np.min(confidences),
            'max_confidence': np.max(confidences),
            'class_distribution': class_counts,
            'size_distribution': size_ranges
        }
    
    def draw_detections(self, image: np.ndarray, detections: List[DetectionResult], 
                       show_labels: bool = True, show_confidence: bool = True) -> np.ndarray:
        """Desenha as detecções na imagem"""
        result_image = image.copy()
        
        for det in detections:
            x, y, w, h = det.bbox
            
            # Desenhar bounding box
            cv2.rectangle(result_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Preparar texto do label
            label_parts = []
            if show_labels:
                label_parts.append(det.class_name)
            if show_confidence:
                label_parts.append(f"{det.confidence:.2f}")
            
            if label_parts:
                label = " ".join(label_parts)
                
                # Calcular tamanho do texto
                (text_width, text_height), baseline = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
                )
                
                # Desenhar fundo do texto
                cv2.rectangle(result_image, 
                            (x, y - text_height - baseline - 5),
                            (x + text_width, y),
                            (0, 255, 0), -1)
                
                # Desenhar texto
                cv2.putText(result_image, label, (x, y - baseline - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        return result_image
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o modelo"""
        if self.model is None:
            return {
                'model_type': 'simulated',
                'available': False,
                'device': self.device
            }
        
        return {
            'model_type': 'yolo',
            'available': True,
            'device': self.device,
            'class_count': len(self.class_names),
            'classes': self.class_names
        }
