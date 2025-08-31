#!/usr/bin/env python3

import cv2
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path
import time
from dataclasses import dataclass

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    YOLO = None

@dataclass
class SignalPlateDetection:
    bbox: Tuple[int, int, int, int]
    confidence: float
    class_name: str
    signal_type: Optional[str] = None
    signal_category: Optional[str] = None
    regulatory_code: Optional[str] = None

class SignalPlateDetector:
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = None
        self.device = "auto"
        self.confidence_threshold = config.get('confidence_threshold', 0.5)
        self.iou_threshold = config.get('iou_threshold', 0.45)
        self.model_path = config.get('model_path', 'models/signal_plates_yolo.pt')
        
        self.regulatory_signs = [
            'stop_sign', 'yield_sign', 'no_entry', 'no_left_turn', 'no_right_turn',
            'no_u_turn', 'no_parking', 'no_stopping', 'no_overtaking', 'speed_limit',
            'weight_limit', 'height_limit', 'width_limit', 'customs', 'chains_required'
        ]
        
        self.warning_signs = [
            'curve_left', 'curve_right', 'double_curve', 'intersection', 'roundabout',
            'pedestrian_crossing', 'school_zone', 'construction', 'animals', 'falling_rocks'
        ]
        
        self.information_signs = [
            'one_way', 'two_way', 'priority_road', 'keep_right', 'keep_left',
            'buses_only', 'bicycles_only', 'pedestrians_only', 'parking', 'hospital'
        ]
        
        self.initialize()
    
    def initialize(self):
        if not YOLO_AVAILABLE:
            raise RuntimeError("Ultralytics YOLO não está disponível")
        
        try:
            self.model = YOLO(self.model_path)
            self.device = self._detect_device()
            self.logger.info(f"SignalPlateDetector inicializado com modelo: {self.model_path}")
            self.logger.info(f"Dispositivo detectado: {self.device}")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar modelo: {e}")
            raise
    
    def _detect_device(self) -> str:
        if not YOLO_AVAILABLE:
            return "cpu"
        
        try:
            if self.model.device.type == "cuda":
                return "cuda"
            elif self.model.device.type == "mps":
                return "mps"
            else:
                return "cpu"
        except:
            return "cpu"
    
    def detect(self, image: np.ndarray) -> List[SignalPlateDetection]:
        if self.model is None:
            return []
        
        try:
            start_time = time.time()
            
            results = self.model(
                image,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                verbose=False
            )
            
            detections = []
            
            for result in results:
                boxes = result.boxes
                if boxes is None:
                    continue
                
                for box in boxes:
                    bbox = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    class_name = self.model.names[class_id]
                    
                    detection = SignalPlateDetection(
                        bbox=tuple(bbox.astype(int)),
                        confidence=confidence,
                        class_name=class_name
                    )
                    
                    detection = self._classify_signal(detection)
                    detections.append(detection)
            
            processing_time = time.time() - start_time
            self.logger.info(f"Detectadas {len(detections)} placas de sinalização em {processing_time:.3f}s")
            
            return detections
            
        except Exception as e:
            self.logger.error(f"Erro na detecção: {e}")
            return []
    
    def _classify_signal(self, detection: SignalPlateDetection) -> SignalPlateDetection:
        class_name = detection.class_name.lower()
        
        if any(sign in class_name for sign in self.regulatory_signs):
            detection.signal_category = "regulatory"
            detection.regulatory_code = self._get_regulatory_code(class_name)
        elif any(sign in class_name for sign in self.warning_signs):
            detection.signal_category = "warning"
        elif any(sign in class_name for sign in self.information_signs):
            detection.signal_category = "information"
        else:
            detection.signal_category = "unknown"
        
        detection.signal_type = class_name
        return detection
    
    def _get_regulatory_code(self, class_name: str) -> Optional[str]:
        regulatory_mapping = {
            'stop_sign': 'R-1',
            'yield_sign': 'R-2',
            'no_entry': 'R-3',
            'no_left_turn': 'R-4',
            'no_right_turn': 'R-5',
            'no_u_turn': 'R-6',
            'no_parking': 'R-7',
            'no_stopping': 'R-8',
            'no_overtaking': 'R-9',
            'speed_limit': 'R-10',
            'weight_limit': 'R-11',
            'height_limit': 'R-12',
            'width_limit': 'R-13',
            'customs': 'R-14',
            'chains_required': 'R-15'
        }
        
        return regulatory_mapping.get(class_name)
    
    def filter_by_category(self, detections: List[SignalPlateDetection], category: str) -> List[SignalPlateDetection]:
        return [det for det in detections if det.signal_category == category]
    
    def filter_by_type(self, detections: List[SignalPlateDetection], signal_type: str) -> List[SignalPlateDetection]:
        return [det for det in detections if det.signal_type == signal_type]
    
    def get_detection_statistics(self, detections: List[SignalPlateDetection]) -> Dict[str, Any]:
        if not detections:
            return {
                'total_detections': 0,
                'regulatory_count': 0,
                'warning_count': 0,
                'information_count': 0,
                'average_confidence': 0.0
            }
        
        regulatory_count = len(self.filter_by_category(detections, "regulatory"))
        warning_count = len(self.filter_by_category(detections, "warning"))
        information_count = len(self.filter_by_category(detections, "information"))
        confidences = [det.confidence for det in detections]
        
        return {
            'total_detections': len(detections),
            'regulatory_count': regulatory_count,
            'warning_count': warning_count,
            'information_count': information_count,
            'average_confidence': np.mean(confidences),
            'min_confidence': np.min(confidences),
            'max_confidence': np.max(confidences)
        }
    
    def draw_detections(self, image: np.ndarray, detections: List[SignalPlateDetection]) -> np.ndarray:
        output_image = image.copy()
        
        for detection in detections:
            x1, y1, x2, y2 = detection.bbox
            confidence = detection.confidence
            
            if detection.signal_category == "regulatory":
                color = (0, 0, 255)
                label = f"Regulamentação: {detection.signal_type} ({confidence:.2f})"
                if detection.regulatory_code:
                    label += f" [{detection.regulatory_code}]"
            elif detection.signal_category == "warning":
                color = (0, 165, 255)
                label = f"Aviso: {detection.signal_type} ({confidence:.2f})"
            elif detection.signal_category == "information":
                color = (0, 255, 0)
                label = f"Informação: {detection.signal_type} ({confidence:.2f})"
            else:
                color = (128, 128, 128)
                label = f"Sinal: {detection.signal_type} ({confidence:.2f})"
            
            cv2.rectangle(output_image, (x1, y1), (x2, y2), color, 2)
            
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(output_image, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), color, -1)
            cv2.putText(output_image, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return output_image
    
    def cleanup(self):
        if self.model:
            del self.model
            self.model = None
