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
from ..ocr.text_extractor import TextExtractor

@dataclass
class PipelineResult:
    """Resultado do processamento do pipeline"""
    success: bool
    image_path: str
    processing_time: float
    detections: List[Dict[str, Any]]
    ocr_results: List[Dict[str, Any]]
    integrated_results: List[Dict[str, Any]]
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class VisionPipeline(BaseVisionProcessor):
    """Pipeline principal de visão computacional"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.preprocessor = None
        self.detector = None
        self.text_extractor = None
        self.cache = {}
        self._initialized_at = None
        self._last_processing_time = 0.0
        self._total_processed_images = 0
        self._processing_times = []
        self.initialize()
    
    def initialize(self):
        """Inicializa os componentes do pipeline"""
        try:
            if 'preprocessor' in self.config:
                self.preprocessor = ImagePreprocessor(self.config['preprocessor'])
            
            if 'detector' in self.config:
                self.detector = YOLODetector(self.config['detector'])
            
            if 'ocr' in self.config:
                self.text_extractor = TextExtractor(self.config['ocr'])
            
            self._initialized_at = datetime.utcnow()
            self.logger.info("Pipeline inicializado com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar pipeline: {e}")
            raise
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Pré-processa a imagem"""
        if self.preprocessor is None:
            return image
        
        try:
            result = self.preprocessor.preprocess(image)
            return result.processed_image
        except Exception as e:
            self.logger.error(f"Erro no pré-processamento: {e}")
            return image
    
    def detect_objects(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detecta objetos na imagem"""
        if self.detector is None:
            return []
        
        try:
            detections = self.detector.detect(image)
            return detections
        except Exception as e:
            self.logger.error(f"Erro na detecção: {e}")
            return []
    
    def extract_text(self, image: np.ndarray, regions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extrai texto das regiões detectadas"""
        if self.text_extractor is None:
            return []
        
        try:
            ocr_regions = []
            for region in regions:
                ocr_regions.append({
                    'bbox': region['bbox']
                })
            
            result = self.text_extractor.extract_text(image, ocr_regions)
            
            ocr_results = []
            for text_result in result.text_results:
                ocr_results.append({
                    'text': text_result.text,
                    'confidence': text_result.confidence,
                    'bbox': text_result.bbox,
                    'language': text_result.language,
                    'processing_time': text_result.processing_time
                })
            
            return ocr_results
            
        except Exception as e:
            self.logger.error(f"Erro na extração de texto: {e}")
            return []
    
    def postprocess_results(self, detections: List[Dict[str, Any]], 
                          ocr_results: List[Dict[str, Any]]) -> ProcessingResult:
        """Implementa método abstrato da classe base"""
        integrated = self.integrate_results(detections, ocr_results)
        
        return ProcessingResult(
            success=True,
            image_path="",
            processing_time=0.0,
            detections=detections,
            ocr_results=ocr_results,
            metadata={
                'integrated_results': integrated,
                'pipeline_version': '2.0.0'
            }
        )
    
    def integrate_results(self, detections: List[Dict[str, Any]], 
                        ocr_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Integra resultados de detecção e OCR"""
        integrated = []
        
        for detection in detections:
            matching_texts = self._find_matching_texts(detection, ocr_results)
            
            integrated_result = {
                'detection': detection,
                'texts': matching_texts,
                'primary_text': self._select_primary_text(matching_texts),
                'confidence_score': self._calculate_integrated_confidence(detection, matching_texts)
            }
            
            integrated.append(integrated_result)
        
        return integrated
    
    def _find_matching_texts(self, detection: Dict[str, Any], 
                            ocr_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Encontra textos que correspondem à detecção baseado em sobreposição"""
        matching = []
        
        for ocr_result in ocr_results:
            overlap_score = self._calculate_overlap(detection['bbox'], ocr_result['bbox'])
            if overlap_score > 0.3:
                matching.append({
                    **ocr_result,
                    'overlap_score': overlap_score
                })
        
        return matching
    
    def _calculate_overlap(self, bbox1: Tuple, bbox2: Tuple) -> float:
        """Calcula sobreposição entre duas bounding boxes"""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection = (x_right - x_left) * (y_bottom - y_top)
        union = w1 * h1 + w2 * h2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def _select_primary_text(self, matching_texts: List[Dict[str, Any]]) -> Optional[str]:
        """Seleciona o texto principal baseado na confiança e sobreposição"""
        if not matching_texts:
            return None
        
        scored_texts = []
        for text in matching_texts:
            score = text['confidence'] * 0.7 + text['overlap_score'] * 0.3
            scored_texts.append((score, text))
        
        scored_texts.sort(reverse=True)
        return scored_texts[0][1]['text']
    
    def _calculate_integrated_confidence(self, detection: Dict[str, Any], 
                                       matching_texts: List[Dict[str, Any]]) -> float:
        """Calcula confiança integrada da detecção"""
        detection_conf = detection['confidence']
        
        if not matching_texts:
            return detection_conf * 0.5
        
        ocr_conf = np.mean([t['confidence'] for t in matching_texts])
        overlap_score = np.mean([t['overlap_score'] for t in matching_texts])
        
        integrated_conf = (detection_conf * 0.4 + 
                          ocr_conf * 0.4 + 
                          overlap_score * 0.2)
        
        return integrated_conf
    
    def process_image(self, image_path: str) -> PipelineResult:
        """Processa uma imagem através do pipeline completo"""
        start_time = time.time()
        
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Não foi possível carregar a imagem: {image_path}")
            
            processed_image = self.preprocess_image(image)
            detections = self.detect_objects(processed_image)
            ocr_results = self.extract_text(processed_image, detections)
            integrated_results = self.integrate_results(detections, ocr_results)
            
            processing_time = time.time() - start_time
            self._update_processing_stats(processing_time)
            
            return PipelineResult(
                success=True,
                image_path=image_path,
                processing_time=processing_time,
                detections=detections,
                ocr_results=ocr_results,
                integrated_results=integrated_results,
                metadata={
                    'pipeline_version': '2.0.0',
                    'components': {
                        'preprocessor': self.preprocessor is not None,
                        'detector': self.detector is not None,
                        'ocr': self.text_extractor is not None
                    }
                }
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"Erro no processamento de {image_path}: {e}")
            
            return PipelineResult(
                success=False,
                image_path=image_path,
                processing_time=processing_time,
                detections=[],
                ocr_results=[],
                integrated_results=[],
                error_message=str(e)
            )
    
    def process_batch(self, image_paths: List[str], output_dir: Optional[str] = None) -> List[PipelineResult]:
        """Processa um lote de imagens"""
        results = []
        
        for i, image_path in enumerate(image_paths):
            self.logger.info(f"Processando imagem {i+1}/{len(image_paths)}: {image_path}")
            
            try:
                result = self.process_image(image_path)
                results.append(result)
                
                if output_dir and result.success:
                    self._save_result(result, output_dir, i)
                    
            except Exception as e:
                self.logger.error(f"Erro ao processar {image_path}: {e}")
                results.append(PipelineResult(
                    success=False,
                    image_path=image_path,
                    processing_time=0.0,
                    detections=[],
                    ocr_results=[],
                    integrated_results=[],
                    error_message=str(e)
                ))
        
        return results
    
    def _save_result(self, result: PipelineResult, output_dir: str, index: int):
        """Salva resultado em arquivo"""
        output_path = Path(output_dir) / f"result_{index:04d}.json"
        
        with open(output_path, 'w') as f:
            json.dump({
                'success': result.success,
                'image_path': result.image_path,
                'processing_time': result.processing_time,
                'detections_count': len(result.detections),
                'ocr_results_count': len(result.ocr_results),
                'integrated_results_count': len(result.integrated_results),
                'error_message': result.error_message,
                'metadata': result.metadata
            }, f, indent=2, default=str)
    
    def _update_processing_stats(self, processing_time: float):
        """Atualiza estatísticas de processamento"""
        self._last_processing_time = processing_time
        self._total_processed_images += 1
        self._processing_times.append(processing_time)
        
        if len(self._processing_times) > 100:
            self._processing_times.pop(0)
    
    def get_last_processing_time(self) -> float:
        """Retorna o tempo do último processamento"""
        return self._last_processing_time
    
    def get_total_processed_images(self) -> int:
        """Retorna o total de imagens processadas"""
        return self._total_processed_images
    
    def get_average_processing_time(self) -> float:
        """Retorna o tempo médio de processamento"""
        if not self._processing_times:
            return 0.0
        return np.mean(self._processing_times)
    
    def get_memory_usage(self) -> float:
        """Retorna uso de memória em MB (simulado)"""
        return 0.25
    
    def get_cpu_usage(self) -> float:
        """Retorna uso de CPU em porcentagem (simulado)"""
        return 0.15
    
    def get_uptime(self) -> float:
        """Retorna tempo de atividade em segundos"""
        if self._initialized_at is None:
            return 0.0
        return (datetime.utcnow() - self._initialized_at).total_seconds()
    
    def cleanup(self):
        """Executa limpeza de recursos"""
        self.logger.info("Executando limpeza do pipeline...")
        
        self.cache.clear()
        self._processing_times.clear()
        
        self.logger.info("Limpeza concluída")
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do pipeline"""
        return {
            'pipeline_version': '2.0.0',
            'components': {
                'preprocessor': self.preprocessor is not None,
                'detector': self.detector is not None,
                'ocr': self.text_extractor is not None
            },
            'initialized_at': getattr(self, '_initialized_at', None),
            'cache_size': len(self.cache),
            'config': self.config
        }
