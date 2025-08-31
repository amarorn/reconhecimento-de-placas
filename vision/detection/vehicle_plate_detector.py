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
class VehiclePlateDetection:
    bbox: Tuple[int, int, int, int]
    confidence: float
    class_name: str
    plate_text: Optional[str] = None
    plate_type: Optional[str] = None
    vehicle_type: Optional[str] = None

class VehiclePlateDetector:
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = None
        self.device = "auto"
        self.confidence_threshold = config.get('confidence_threshold', 0.5)
        self.iou_threshold = config.get('iou_threshold', 0.45)
        self.model_path = config.get('model_path', 'models/vehicle_plates_yolo.pt')
        
        self.vehicle_classes = [
            'car', 'truck', 'bus', 'motorcycle', 'bicycle', 'van', 'pickup'
        ]
        
        self.plate_classes = [
            'mercosul_plate', 'old_plate', 'diplomatic_plate', 'official_plate',
            'motorcycle_plate', 'truck_plate', 'trailer_plate'
        ]
        
        self.initialize()
    
    def initialize(self):
        if not YOLO_AVAILABLE:
            raise RuntimeError("Ultralytics YOLO não está disponível")
        
        try:
            self.model = YOLO(self.model_path)
            self.device = self._detect_device()
            self.logger.info(f"VehiclePlateDetector inicializado com modelo: {self.model_path}")
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
    
    def detect(self, image: np.ndarray) -> List[VehiclePlateDetection]:
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
                    
                    detection = VehiclePlateDetection(
                        bbox=tuple(bbox.astype(int)),
                        confidence=confidence,
                        class_name=class_name
                    )
                    
                    detection = self._classify_detection(detection)
                    detections.append(detection)
            
            processing_time = time.time() - start_time
            self.logger.info(f"Detectadas {len(detections)} placas/veículos em {processing_time:.3f}s")
            
            return detections
            
        except Exception as e:
            self.logger.error(f"Erro na detecção: {e}")
            return []
    
    def _classify_detection(self, detection: VehiclePlateDetection) -> VehiclePlateDetection:
        class_name = detection.class_name.lower()
        
        if any(vehicle in class_name for vehicle in self.vehicle_classes):
            detection.vehicle_type = class_name
        elif any(plate in class_name for plate in self.plate_classes):
            detection.plate_type = class_name
        else:
            detection.plate_type = "unknown_plate"
        
        return detection
    
    def filter_vehicle_plates(self, detections: List[VehiclePlateDetection]) -> List[VehiclePlateDetection]:
        return [det for det in detections if det.plate_type is not None]
    
    def filter_vehicles(self, detections: List[VehiclePlateDetection]) -> List[VehiclePlateDetection]:
        return [det for det in detections if det.vehicle_type is not None]
    
    def get_detection_statistics(self, detections: List[VehiclePlateDetection]) -> Dict[str, Any]:
        if not detections:
            return {
                'total_detections': 0,
                'vehicle_count': 0,
                'plate_count': 0,
                'average_confidence': 0.0
            }
        
        vehicle_count = len(self.filter_vehicles(detections))
        plate_count = len(self.filter_vehicle_plates(detections))
        confidences = [det.confidence for det in detections]
        
        return {
            'total_detections': len(detections),
            'vehicle_count': vehicle_count,
            'plate_count': plate_count,
            'average_confidence': np.mean(confidences),
            'min_confidence': np.min(confidences),
            'max_confidence': np.max(confidences)
        }
    
    def draw_detections(self, image: np.ndarray, detections: List[VehiclePlateDetection]) -> np.ndarray:
        output_image = image.copy()
        
        for detection in detections:
            x1, y1, x2, y2 = detection.bbox
            confidence = detection.confidence
            
            if detection.plate_type:
                color = (0, 255, 0)
                label = f"Placa: {detection.plate_type} ({confidence:.2f})"
            elif detection.vehicle_type:
                color = (255, 0, 0)
                label = f"Veículo: {detection.vehicle_type} ({confidence:.2f})"
            else:
                color = (128, 128, 128)
                label = f"Objeto: {detection.class_name} ({confidence:.2f})"
            
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
