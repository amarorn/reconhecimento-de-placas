#!/usr/bin/env python3

import cv2
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from pathlib import Path
import time
from dataclasses import dataclass

from .vehicle_plate_detector import VehiclePlateDetector, VehiclePlateDetection
from .signal_plate_detector import SignalPlateDetector, SignalPlateDetection
from .pothole_detector import PotholeDetector, PotholeDetection

@dataclass
class UnifiedDetectionResult:
    vehicle_plates: List[VehiclePlateDetection]
    signal_plates: List[SignalPlateDetection]
    potholes: List[PotholeDetection]
    processing_time: float
    total_detections: int
    metadata: Dict[str, Any]

class SpecializedDetector:
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.vehicle_detector = None
        self.signal_detector = None
        self.pothole_detector = None
        
        self.enabled_detectors = config.get('enabled_detectors', ['vehicle', 'signal', 'pothole'])
        
        self.initialize()
    
    def initialize(self):
        try:
            if 'vehicle' in self.enabled_detectors:
                vehicle_config = self.config.get('vehicle_detector', {})
                self.vehicle_detector = VehiclePlateDetector(vehicle_config)
                self.logger.info("VehiclePlateDetector inicializado")
            
            if 'signal' in self.enabled_detectors:
                signal_config = self.config.get('signal_detector', {})
                self.signal_detector = SignalPlateDetector(signal_config)
                self.logger.info("SignalPlateDetector inicializado")
            
            if 'pothole' in self.enabled_detectors:
                pothole_config = self.config.get('pothole_detector', {})
                self.pothole_detector = PotholeDetector(pothole_config)
                self.logger.info("PotholeDetector inicializado")
            
            self.logger.info(f"SpecializedDetector inicializado com detectores: {self.enabled_detectors}")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar detectores especializados: {e}")
            raise
    
    def detect_all(self, image: np.ndarray) -> UnifiedDetectionResult:
        start_time = time.time()
        
        vehicle_plates = []
        signal_plates = []
        potholes = []
        
        try:
            if self.vehicle_detector:
                vehicle_plates = self.vehicle_detector.detect(image)
                self.logger.info(f"Detectadas {len(vehicle_plates)} placas/veículos")
            
            if self.signal_detector:
                signal_plates = self.signal_detector.detect(image)
                self.logger.info(f"Detectadas {len(signal_plates)} placas de sinalização")
            
            if self.pothole_detector:
                potholes = self.pothole_detector.detect(image)
                self.logger.info(f"Detectados {len(potholes)} buracos")
            
        except Exception as e:
            self.logger.error(f"Erro durante detecção: {e}")
        
        processing_time = time.time() - start_time
        total_detections = len(vehicle_plates) + len(signal_plates) + len(potholes)
        
        metadata = self._generate_metadata(vehicle_plates, signal_plates, potholes)
        
        return UnifiedDetectionResult(
            vehicle_plates=vehicle_plates,
            signal_plates=signal_plates,
            potholes=potholes,
            processing_time=processing_time,
            total_detections=total_detections,
            metadata=metadata
        )
    
    def detect_vehicle_plates(self, image: np.ndarray) -> List[VehiclePlateDetection]:
        if not self.vehicle_detector:
            return []
        return self.vehicle_detector.detect(image)
    
    def detect_signal_plates(self, image: np.ndarray) -> List[SignalPlateDetection]:
        if not self.signal_detector:
            return []
        return self.signal_detector.detect(image)
    
    def detect_potholes(self, image: np.ndarray) -> List[PotholeDetection]:
        if not self.pothole_detector:
            return []
        return self.pothole_detector.detect(image)
    
    def _generate_metadata(self, vehicle_plates: List[VehiclePlateDetection], 
                          signal_plates: List[SignalPlateDetection], 
                          potholes: List[PotholeDetection]) -> Dict[str, Any]:
        
        metadata = {
            'detection_summary': {
                'vehicle_plates': len(vehicle_plates),
                'signal_plates': len(signal_plates),
                'potholes': len(potholes),
                'total': len(vehicle_plates) + len(signal_plates) + len(potholes)
            },
            'timestamp': time.time()
        }
        
        if vehicle_plates:
            vehicle_stats = self.vehicle_detector.get_detection_statistics(vehicle_plates)
            metadata['vehicle_statistics'] = vehicle_stats
        
        if signal_plates:
            signal_stats = self.signal_detector.get_detection_statistics(signal_plates)
            metadata['signal_statistics'] = signal_stats
        
        if potholes:
            pothole_stats = self.pothole_detector.get_detection_statistics(potholes)
            metadata['pothole_statistics'] = pothole_stats
            
            road_report = self.pothole_detector.generate_road_report(potholes)
            metadata['road_report'] = road_report
        
        return metadata
    
    def draw_all_detections(self, image: np.ndarray, result: UnifiedDetectionResult) -> np.ndarray:
        output_image = image.copy()
        
        if self.vehicle_detector and result.vehicle_plates:
            output_image = self.vehicle_detector.draw_detections(output_image, result.vehicle_plates)
        
        if self.signal_detector and result.signal_plates:
            output_image = self.signal_detector.draw_detections(output_image, result.signal_plates)
        
        if self.pothole_detector and result.potholes:
            output_image = self.pothole_detector.draw_detections(output_image, result.potholes)
        
        return output_image
    
    def get_comprehensive_statistics(self, result: UnifiedDetectionResult) -> Dict[str, Any]:
        stats = {
            'overview': {
                'total_detections': result.total_detections,
                'processing_time': result.processing_time,
                'detectors_enabled': self.enabled_detectors
            },
            'vehicle_analysis': {},
            'signal_analysis': {},
            'pothole_analysis': {},
            'road_condition': {}
        }
        
        if result.vehicle_plates and self.vehicle_detector:
            vehicle_stats = self.vehicle_detector.get_detection_statistics(result.vehicle_plates)
            stats['vehicle_analysis'] = vehicle_stats
        
        if result.signal_plates and self.signal_detector:
            signal_stats = self.signal_detector.get_detection_statistics(result.signal_plates)
            stats['signal_analysis'] = signal_stats
        
        if result.potholes and self.pothole_detector:
            pothole_stats = self.pothole_detector.get_detection_statistics(result.potholes)
            road_report = self.pothole_detector.generate_road_report(result.potholes)
            
            stats['pothole_analysis'] = pothole_stats
            stats['road_condition'] = road_report
        
        return stats
    
    def filter_by_confidence(self, result: UnifiedDetectionResult, 
                           min_confidence: float = 0.5) -> UnifiedDetectionResult:
        
        filtered_vehicle = [det for det in result.vehicle_plates if det.confidence >= min_confidence]
        filtered_signal = [det for det in result.signal_plates if det.confidence >= min_confidence]
        filtered_potholes = [det for det in result.potholes if det.confidence >= min_confidence]
        
        total_filtered = len(filtered_vehicle) + len(filtered_signal) + len(filtered_potholes)
        
        return UnifiedDetectionResult(
            vehicle_plates=filtered_vehicle,
            signal_plates=filtered_signal,
            potholes=filtered_potholes,
            processing_time=result.processing_time,
            total_detections=total_filtered,
            metadata=result.metadata
        )
    
    def export_detections(self, result: UnifiedDetectionResult, 
                         format: str = 'json') -> Union[str, Dict[str, Any]]:
        
        if format.lower() == 'json':
            export_data = {
                'vehicle_plates': [
                    {
                        'bbox': det.bbox,
                        'confidence': det.confidence,
                        'class_name': det.class_name,
                        'plate_type': det.plate_type,
                        'vehicle_type': det.vehicle_type
                    } for det in result.vehicle_plates
                ],
                'signal_plates': [
                    {
                        'bbox': det.bbox,
                        'confidence': det.confidence,
                        'class_name': det.class_name,
                        'signal_type': det.signal_type,
                        'signal_category': det.signal_category,
                        'regulatory_code': det.regulatory_code
                    } for det in result.signal_plates
                ],
                'potholes': [
                    {
                        'bbox': det.bbox,
                        'confidence': det.confidence,
                        'class_name': det.class_name,
                        'pothole_type': det.pothole_type,
                        'severity_level': det.severity_level,
                        'depth_estimate': det.depth_estimate,
                        'area_estimate': det.area_estimate,
                        'risk_score': det.risk_score
                    } for det in result.potholes
                ],
                'metadata': result.metadata
            }
            
            return export_data
        
        elif format.lower() == 'csv':
            csv_lines = ['Type,Bbox,Confidence,Class,Details\n']
            
            for det in result.vehicle_plates:
                details = f"Plate:{det.plate_type},Vehicle:{det.vehicle_type}"
                csv_lines.append(f"Vehicle,{det.bbox},{det.confidence},{det.class_name},{details}\n")
            
            for det in result.signal_plates:
                details = f"Signal:{det.signal_type},Category:{det.signal_category},Code:{det.regulatory_code}"
                csv_lines.append(f"Signal,{det.bbox},{det.confidence},{det.class_name},{details}\n")
            
            for det in result.potholes:
                details = f"Type:{det.pothole_type},Severity:{det.severity_level},Risk:{det.risk_score}"
                csv_lines.append(f"Pothole,{det.bbox},{det.confidence},{det.class_name},{details}\n")
            
            return ''.join(csv_lines)
        
        else:
            raise ValueError(f"Formato não suportado: {format}")
    
    def cleanup(self):
        if self.vehicle_detector:
            self.vehicle_detector.cleanup()
        if self.signal_detector:
            self.signal_detector.cleanup()
        if self.pothole_detector:
            self.pothole_detector.cleanup()
