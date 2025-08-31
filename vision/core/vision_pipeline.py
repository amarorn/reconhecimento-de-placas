#!/usr/bin/env python3
"""
Pipeline de Visão Computacional
===============================

Pipeline principal que integra pré-processamento, detecção e OCR.
"""

import cv2
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
from datetime import datetime
import time
from pathlib import Path
import json

from .base_processor import BaseVisionProcessor, ProcessingResult
from ..preprocessing.image_preprocessor import ImagePreprocessor
from ..detection.yolo_detector import YOLODetector
from ..detection.specialized_detector import SpecializedDetector, UnifiedDetectionResult
from ..ocr.text_extractor import TextExtractor

@dataclass
class PipelineResult:
    success: bool
    image_path: str
    processing_time: float
    detections: List[Dict[str, Any]]
    ocr_results: List[Dict[str, Any]]
    integrated_results: List[Dict[str, Any]]
    specialized_results: Optional[UnifiedDetectionResult] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class VisionPipeline(BaseVisionProcessor):
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.preprocessor = None
        self.detector = None
        self.specialized_detector = None
        self.text_extractor = None
        self.cache = {}
        self._initialized_at = None
        self._last_processing_time = 0.0
        self._total_processed_images = 0
        self._processing_times = []
        self.initialize()
    
    def initialize(self):
        try:
            if 'preprocessor' in self.config:
                self.preprocessor = ImagePreprocessor(self.config['preprocessor'])
            
            if 'detector' in self.config:
                self.detector = YOLODetector(self.config['detector'])
            
            if 'specialized_detector' in self.config:
                self.specialized_detector = SpecializedDetector(self.config['specialized_detector'])
            
            if 'ocr' in self.config:
                self.text_extractor = TextExtractor(self.config['ocr'])
            
            self._initialized_at = datetime.utcnow()
            self.logger.info("Pipeline inicializado com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar pipeline: {e}")
            raise
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        if self.preprocessor is None:
            return image
        
        try:
            result = self.preprocessor.preprocess(image)
            return result.processed_image
        except Exception as e:
            self.logger.error(f"Erro no pré-processamento: {e}")
            return image
    
    def detect_objects(self, image: np.ndarray) -> List[Dict[str, Any]]:
        if self.detector is None:
            return []
        
        try:
            detections = self.detector.detect(image)
            return detections
        except Exception as e:
            self.logger.error(f"Erro na detecção: {e}")
            return []
    
    def detect_specialized(self, image: np.ndarray) -> Optional[UnifiedDetectionResult]:
        if self.specialized_detector is None:
            return None
        
        try:
            result = self.specialized_detector.detect_all(image)
            return result
        except Exception as e:
            self.logger.error(f"Erro na detecção especializada: {e}")
            return None
    
    def extract_text(self, image: np.ndarray, regions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if self.text_extractor is None:
            return []
        
        try:
            ocr_regions = []
            for region in regions:
                if 'bbox' in region:
                    ocr_regions.append({
                        'bbox': region['bbox']
                    })
            
            if not ocr_regions:
                return []
            
            text_results = self.text_extractor.extract_text_batch(image, ocr_regions)
            
            return [
                {
                    'text': text_result.text,
                    'confidence': text_result.confidence,
                    'bbox': text_result.bbox,
                    'language': text_result.language,
                    'processing_time': text_result.processing_time
                }
                for text_result in text_results
            ]
            
        except Exception as e:
            self.logger.error(f"Erro na extração de texto: {e}")
            return []
    
    def integrate_detections(self, detections: List[Dict[str, Any]], 
                           ocr_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        integrated_results = []
        
        for detection in detections:
            matching_texts = []
            
            for ocr_result in ocr_results:
                if self._check_overlap(detection['bbox'], ocr_result['bbox']):
                    matching_texts.append(ocr_result)
            
            integrated_result = {
                'detection': detection,
                'texts': matching_texts,
                'primary_text': self._select_primary_text(matching_texts),
                'confidence_score': self._calculate_integrated_confidence(detection, matching_texts)
            }
            
            integrated_results.append(integrated_result)
        
        return integrated_results
    
    def _check_overlap(self, bbox1: Tuple[int, int, int, int], 
                      bbox2: Tuple[int, int, int, int]) -> bool:
        x1_1, y1_1, w1, h1 = bbox1
        x2_1, y2_1 = x1_1 + w1, y1_1 + h1
        
        x1_2, y1_2, w2, h2 = bbox2
        x2_2, y2_2 = x1_2 + w2, y1_2 + h2
        
        overlap_x = max(0, min(x2_1, x2_2) - max(x1_1, x1_2))
        overlap_y = max(0, min(y2_1, y2_2) - max(y1_1, y1_2))
        
        overlap_area = overlap_x * overlap_y
        area1 = w1 * h1
        area2 = w2 * h2
        
        min_area = min(area1, area2)
        return overlap_area > 0.3 * min_area
    
    def _select_primary_text(self, texts: List[Dict[str, Any]]) -> Optional[str]:
        if not texts:
            return None
        
        best_result = max(texts, key=lambda x: x['confidence'])
        return best_result['text']
    
    def _calculate_integrated_confidence(self, detection: Dict[str, Any], 
                                       texts: List[Dict[str, Any]]) -> float:
        detection_conf = detection.get('confidence', 0.0)
        
        if not texts:
            return detection_conf * 0.5
        
        text_conf = max(text['confidence'] for text in texts)
        return (detection_conf + text_conf) / 2
    
    def postprocess_results(self, detections: List[Dict[str, Any]], 
                          ocr_results: List[Dict[str, Any]]) -> ProcessingResult:
        integrated_results = self.integrate_detections(detections, ocr_results)
        
        return ProcessingResult(
            success=True,
            image_path="",
            processing_time=0.0,
            detections=detections,
            ocr_results=ocr_results,
            metadata={
                'integrated_results': integrated_results,
                'total_detections': len(detections),
                'total_texts': len(ocr_results)
            }
        )
    
    def process_image(self, image_path: str) -> PipelineResult:
        start_time = time.time()
        
        try:
            image = self.load_image(image_path)
            if image is None:
                return PipelineResult(
                    success=False,
                    image_path=image_path,
                    processing_time=0.0,
                    detections=[],
                    ocr_results=[],
                    integrated_results=[],
                    error_message="Falha ao carregar imagem"
                )
            
            processed_image = self.preprocess_image(image)
            
            detections = self.detect_objects(processed_image)
            ocr_results = self.extract_text(processed_image, detections)
            integrated_results = self.integrate_detections(detections, ocr_results)
            
            specialized_results = self.detect_specialized(processed_image)
            
            processing_time = time.time() - start_time
            
            metadata = self._generate_metadata(
                detections, ocr_results, integrated_results, specialized_results
            )
            
            result = PipelineResult(
                success=True,
                image_path=image_path,
                processing_time=processing_time,
                detections=detections,
                ocr_results=ocr_results,
                integrated_results=integrated_results,
                specialized_results=specialized_results,
                metadata=metadata
            )
            
            self._update_statistics(processing_time)
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"Erro ao processar imagem {image_path}: {e}")
            
            return PipelineResult(
                success=False,
                image_path=image_path,
                processing_time=processing_time,
                detections=[],
                ocr_results=[],
                integrated_results=[],
                error_message=str(e)
            )
    
    def process_batch(self, image_paths: List[str]) -> List[PipelineResult]:
        results = []
        
        for image_path in image_paths:
            try:
                result = self.process_image(image_path)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Erro ao processar lote {image_path}: {e}")
                error_result = PipelineResult(
                    success=False,
                    image_path=image_path,
                    processing_time=0.0,
                    detections=[],
                    ocr_results=[],
                    integrated_results=[],
                    error_message=str(e)
                )
                results.append(error_result)
        
        return results
    
    def _generate_metadata(self, detections: List[Dict[str, Any]], 
                          ocr_results: List[Dict[str, Any]], 
                          integrated_results: List[Dict[str, Any]],
                          specialized_results: Optional[UnifiedDetectionResult]) -> Dict[str, Any]:
        
        metadata = {
            'pipeline_version': '2.0.0',
            'components': {
                'preprocessor': self.preprocessor is not None,
                'detector': self.detector is not None,
                'specialized_detector': self.specialized_detector is not None,
                'ocr': self.text_extractor is not None
            },
            'processing_info': {
                'initialized_at': getattr(self, '_initialized_at', None),
                'cache_size': len(self.cache),
                'config': self.config
            }
        }
        
        if specialized_results:
            metadata['specialized_detection'] = {
                'vehicle_plates': len(specialized_results.vehicle_plates),
                'signal_plates': len(specialized_results.signal_plates),
                'potholes': len(specialized_results.potholes),
                'total_specialized': specialized_results.total_detections
            }
        
        return metadata
    
    def _update_statistics(self, processing_time: float):
        self._last_processing_time = processing_time
        self._total_processed_images += 1
        self._processing_times.append(processing_time)
        
        if len(self._processing_times) > 100:
            self._processing_times.pop(0)
    
    def get_statistics(self) -> Dict[str, Any]:
        if not self._processing_times:
            return {
                'total_processed': 0,
                'average_processing_time': 0.0,
                'last_processing_time': 0.0
            }
        
        return {
            'total_processed': self._total_processed_images,
            'average_processing_time': np.mean(self._processing_times),
            'last_processing_time': self._last_processing_time,
            'min_processing_time': np.min(self._processing_times),
            'max_processing_time': np.max(self._processing_times)
        }
    
    def cleanup(self):
        if self.preprocessor:
            self.preprocessor.cleanup()
        if self.detector:
            self.detector.cleanup()
        if self.specialized_detector:
            self.specialized_detector.cleanup()
        if self.text_extractor:
            self.text_extractor.cleanup()
