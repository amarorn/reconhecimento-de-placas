#!/usr/bin/env python3
"""
Detector YOLO para Placas de Trânsito e Veículos
================================================

Este módulo implementa detecção de objetos usando YOLOv8
especialmente otimizado para placas de trânsito e veículos.
"""

import cv2
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
import logging
from dataclasses import dataclass
from pathlib import Path
import torch
from ultralytics import YOLO
import warnings
warnings.filterwarnings('ignore')

@dataclass
class DetectionResult:
    """Resultado de uma detecção"""
    bbox: Tuple[int, int, int, int]  # x, y, w, h
    confidence: float
    class_id: int
    class_name: str
    area: float
    center: Tuple[int, int]

@dataclass
class DetectionBatchResult:
    """Resultado de detecção em lote"""
    detections: List[DetectionResult]
    processing_time: float
    image_shape: Tuple[int, int]
    metadata: Dict[str, Any]

class YOLODetector:
    """Detector YOLO para placas de trânsito e veículos"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = None
        self.class_names = []
        self.device = self._get_device()
        self.initialize()
    
    def _get_device(self) -> str:
        """Determina o melhor dispositivo disponível"""
        if self.config.get('device') == 'auto':
            if torch.cuda.is_available():
                return 'cuda'
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return 'mps'
            else:
                return 'cpu'
        return self.config.get('device', 'cpu')
    
    def initialize(self):
        """Inicializa o modelo YOLO"""
        try:
            model_path = self.config.get('weights_path', 'yolov8n.pt')
            
            if not Path(model_path).exists():
                self.logger.warning(f"Modelo não encontrado em {model_path}, baixando...")
                # YOLO baixará automaticamente se não existir
            
            self.logger.info(f"Inicializando YOLO com modelo: {model_path}")
            self.model = YOLO(model_path)
            
            # Configurar dispositivo
            self.model.to(self.device)
            
            # Configurar parâmetros
            self.confidence_threshold = self.config.get('confidence_threshold', 0.5)
            self.nms_threshold = self.config.get('nms_threshold', 0.4)
            self.input_size = self.config.get('input_size', (640, 640))
            
            # Carregar nomes das classes
            self._load_class_names()
            
            self.logger.info(f"YOLO inicializado com sucesso no dispositivo: {self.device}")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar YOLO: {e}")
            raise
    
    def _load_class_names(self):
        """Carrega nomes das classes do modelo"""
        try:
            if hasattr(self.model, 'names'):
                self.class_names = list(self.model.names.values())
            else:
                # Classes padrão para detecção de placas
                self.class_names = [
                    'traffic_sign', 'vehicle_plate', 'vehicle', 'person',
                    'bicycle', 'motorcycle', 'car', 'bus', 'truck'
                ]
            
            self.logger.info(f"Classes carregadas: {self.class_names}")
            
        except Exception as e:
            self.logger.warning(f"Erro ao carregar nomes das classes: {e}")
            self.class_names = ['object']
    
    def detect(self, image: np.ndarray) -> DetectionBatchResult:
        """Executa detecção na imagem"""
        if self.model is None:
            raise RuntimeError("Modelo YOLO não foi inicializado")
        
        start_time = torch.cuda.Event(enable_timing=True) if self.device == 'cuda' else None
        end_time = torch.cuda.Event(enable_timing=True) if self.device == 'cuda' else None
        
        if start_time:
            start_time.record()
        
        try:
            # Executar inferência
            results = self.model(
                image,
                conf=self.confidence_threshold,
                iou=self.nms_threshold,
                imgsz=self.input_size,
                verbose=False
            )
            
            # Processar resultados
            detections = self._process_results(results[0], image.shape)
            
            # Calcular tempo de processamento
            if end_time:
                end_time.record()
                torch.cuda.synchronize()
                processing_time = start_time.elapsed_time(end_time) / 1000.0  # Converter para segundos
            else:
                processing_time = 0.0
            
            return DetectionBatchResult(
                detections=detections,
                processing_time=processing_time,
                image_shape=image.shape,
                metadata={
                    'model_name': self.config.get('weights_path', 'yolov8n.pt'),
                    'device': self.device,
                    'confidence_threshold': self.confidence_threshold,
                    'nms_threshold': self.nms_threshold
                }
            )
            
        except Exception as e:
            self.logger.error(f"Erro durante detecção: {e}")
            raise
    
    def _process_results(self, result, image_shape: Tuple[int, int]) -> List[DetectionResult]:
        """Processa os resultados brutos do YOLO"""
        detections = []
        
        if result.boxes is None:
            return detections
        
        boxes = result.boxes
        for i in range(len(boxes)):
            # Extrair coordenadas
            x1, y1, x2, y2 = boxes.xyxy[i].cpu().numpy()
            confidence = float(boxes.conf[i].cpu().numpy())
            class_id = int(boxes.cls[i].cpu().numpy())
            
            # Converter para formato (x, y, w, h)
            x, y, w, h = int(x1), int(y1), int(x2 - x1), int(y2 - y1)
            
            # Obter nome da classe
            class_name = self.class_names[class_id] if class_id < len(self.class_names) else f"class_{class_id}"
            
            # Calcular área e centro
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
        
        return detections
    
    def detect_traffic_signs(self, image: np.ndarray) -> List[DetectionResult]:
        """Detecta especificamente placas de trânsito"""
        all_detections = self.detect(image)
        
        # Filtrar apenas placas de trânsito
        traffic_signs = [
            det for det in all_detections.detections
            if det.class_name in ['traffic_sign', 'sign'] or 
               'sign' in det.class_name.lower() or
               'traffic' in det.class_name.lower()
        ]
        
        return traffic_signs
    
    def detect_vehicle_plates(self, image: np.ndarray) -> List[DetectionResult]:
        """Detecta especificamente placas de veículos"""
        all_detections = self.detect(image)
        
        # Filtrar apenas placas de veículos
        vehicle_plates = [
            det for det in all_detections.detections
            if det.class_name in ['vehicle_plate', 'plate', 'license_plate'] or
               'plate' in det.class_name.lower() or
               'license' in det.class_name.lower()
        ]
        
        return vehicle_plates
    
    def detect_vehicles(self, image: np.ndarray) -> List[DetectionResult]:
        """Detecta especificamente veículos"""
        all_detections = self.detect(image)
        
        # Filtrar apenas veículos
        vehicles = [
            det for det in all_detections.detections
            if det.class_name in ['vehicle', 'car', 'truck', 'bus', 'motorcycle', 'bicycle'] or
               det.class_name.lower() in ['car', 'truck', 'bus', 'motorcycle', 'bicycle']
        ]
        
        return vehicles
    
    def filter_detections_by_size(self, detections: List[DetectionResult], 
                                 min_area: float = 1000, 
                                 max_area: float = float('inf')) -> List[DetectionResult]:
        """Filtra detecções por tamanho"""
        return [
            det for det in detections
            if min_area <= det.area <= max_area
        ]
    
    def filter_detections_by_confidence(self, detections: List[DetectionResult], 
                                      min_confidence: float = 0.5) -> List[DetectionResult]:
        """Filtra detecções por confiança"""
        return [
            det for det in detections
            if det.confidence >= min_confidence
        ]
    
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
            # Contar classes
            class_counts[det.class_name] = class_counts.get(det.class_name, 0) + 1
            
            # Categorizar por tamanho
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
            'size_distribution': size_ranges,
            'average_area': np.mean([det.area for det in detections])
        }
    
    def draw_detections(self, image: np.ndarray, detections: List[DetectionResult], 
                       show_labels: bool = True, show_confidence: bool = True) -> np.ndarray:
        """Desenha as detecções na imagem"""
        output_image = image.copy()
        
        for det in detections:
            x, y, w, h = det.bbox
            
            # Cor baseada na classe
            color = self._get_class_color(det.class_name)
            
            # Desenhar bounding box
            cv2.rectangle(output_image, (x, y), (x + w, y + h), color, 2)
            
            # Desenhar label
            if show_labels:
                label = det.class_name
                if show_confidence:
                    label += f" {det.confidence:.2f}"
                
                # Calcular tamanho do texto
                font_scale = 0.6
                thickness = 2
                (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
                
                # Desenhar fundo do texto
                cv2.rectangle(output_image, (x, y - text_height - 10), 
                            (x + text_width, y), color, -1)
                
                # Desenhar texto
                cv2.putText(output_image, label, (x, y - 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)
        
        return output_image
    
    def _get_class_color(self, class_name: str) -> Tuple[int, int, int]:
        """Retorna cor para uma classe específica"""
        color_map = {
            'traffic_sign': (0, 255, 0),      # Verde
            'vehicle_plate': (255, 0, 0),     # Azul
            'vehicle': (0, 0, 255),           # Vermelho
            'car': (0, 0, 255),               # Vermelho
            'truck': (0, 0, 255),             # Vermelho
            'bus': (0, 0, 255),               # Vermelho
            'motorcycle': (0, 0, 255),        # Vermelho
            'bicycle': (0, 0, 255),           # Vermelho
            'person': (255, 255, 0),          # Ciano
        }
        
        return color_map.get(class_name, (128, 128, 128))  # Cinza padrão
    
    def cleanup(self):
        """Limpa recursos do detector"""
        if self.model is not None:
            del self.model
            self.model = None
        
        if self.device == 'cuda':
            torch.cuda.empty_cache()