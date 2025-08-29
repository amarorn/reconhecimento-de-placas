#!/usr/bin/env python3
"""
Pipeline Principal de Visão Computacional
========================================

Este módulo implementa o pipeline principal que integra todos os componentes
de visão computacional para reconhecimento de placas de trânsito e veículos.
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

# Importar componentes do pipeline
from .base_processor import BaseVisionProcessor, ProcessingResult
from ..preprocessing.image_preprocessor import ImagePreprocessor
from ..detection.yolo_detector import YOLODetector
from ..ocr.text_extractor import TextExtractor

@dataclass
class PipelineResult:
    """Resultado completo do pipeline"""
    success: bool
    image_path: str
    processing_time: float
    preprocessing_result: Optional[Dict[str, Any]] = None
    detection_result: Optional[Dict[str, Any]] = None
    ocr_result: Optional[Dict[str, Any]] = None
    final_results: List[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.final_results is None:
            self.final_results = []

class VisionPipeline(BaseVisionProcessor):
    """Pipeline principal de visão computacional"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.preprocessor = None
        self.detector = None
        self.text_extractor = None
        self.cache = {}
        self.initialize()
    
    def initialize(self):
        """Inicializa todos os componentes do pipeline"""
        try:
            self.logger.info("🚀 Inicializando Pipeline de Visão Computacional...")
            
            # 1. Inicializar pré-processador
            self.logger.info("📸 Inicializando pré-processador...")
            preprocessor_config = self.config.get('preprocessing', {})
            self.preprocessor = ImagePreprocessor(preprocessor_config)
            
            # 2. Inicializar detector
            self.logger.info("🔍 Inicializando detector...")
            detector_config = self.config.get('detection', {})
            self.detector = YOLODetector(detector_config)
            
            # 3. Inicializar extrator de texto
            self.logger.info("📝 Inicializando extrator de texto...")
            ocr_config = self.config.get('ocr', {})
            self.text_extractor = TextExtractor(ocr_config)
            
            self._initialized_at = datetime.now()
            self.logger.info("✅ Pipeline inicializado com sucesso!")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar pipeline: {e}")
            raise
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Pré-processa a imagem usando o componente especializado"""
        if self.preprocessor is None:
            raise RuntimeError("Pré-processador não foi inicializado")
        
        try:
            result = self.preprocessor.preprocess(image)
            return result.processed_image
        except Exception as e:
            self.logger.error(f"Erro no pré-processamento: {e}")
            return image  # Retornar imagem original em caso de erro
    
    def detect_objects(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detecta objetos usando o detector YOLO"""
        if self.detector is None:
            raise RuntimeError("Detector não foi inicializado")
        
        try:
            result = self.detector.detect(image)
            
            # Converter para formato esperado
            detections = []
            for det in result.detections:
                detections.append({
                    'bbox': det.bbox,
                    'confidence': det.confidence,
                    'class_id': det.class_id,
                    'class_name': det.class_name,
                    'area': det.area,
                    'center': det.center
                })
            
            return detections
            
        except Exception as e:
            self.logger.error(f"Erro na detecção: {e}")
            return []
    
    def extract_text(self, image: np.ndarray, regions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extrai texto das regiões detectadas"""
        if self.text_extractor is None:
            raise RuntimeError("Extrator de texto não foi inicializado")
        
        try:
            # Converter regiões para formato esperado pelo OCR
            ocr_regions = []
            for region in regions:
                ocr_regions.append({
                    'bbox': region['bbox']
                })
            
            result = self.text_extractor.extract_text(image, ocr_regions)
            
            # Converter para formato esperado
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
        """Pós-processa e integra todos os resultados"""
        try:
            # Integrar detecções com OCR
            integrated_results = self._integrate_detections_and_ocr(detections, ocr_results)
            
            # Aplicar validação e filtros
            validated_results = self._validate_results(integrated_results)
            
            # Criar resultado final
            result = ProcessingResult(
                success=True,
                image_path="",  # Será definido pelo método principal
                processing_time=0.0,  # Será definido pelo método principal
                detections=detections,
                ocr_results=ocr_results,
                metadata={
                    'pipeline_version': '2.0.0',
                    'components_used': ['preprocessor', 'detector', 'ocr'],
                    'integration_method': 'bbox_matching',
                    'validation_rules_applied': list(self.config.get('validation_rules', {}).keys())
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro no pós-processamento: {e}")
            return ProcessingResult(
                success=False,
                image_path="",
                processing_time=0.0,
                detections=[],
                ocr_results=[],
                metadata={},
                error_message=str(e)
            )
    
    def _integrate_detections_and_ocr(self, detections: List[Dict[str, Any]], 
                                    ocr_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Integra resultados de detecção com OCR"""
        integrated = []
        
        for detection in detections:
            # Encontrar texto correspondente baseado na sobreposição de bounding boxes
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
        """Encontra textos que correspondem a uma detecção"""
        matching = []
        det_bbox = detection['bbox']
        
        for ocr_result in ocr_results:
            ocr_bbox = ocr_result['bbox']
            
            # Calcular sobreposição
            overlap = self._calculate_bbox_overlap(det_bbox, ocr_bbox)
            
            if overlap > 0.3:  # Threshold de sobreposição
                matching.append({
                    **ocr_result,
                    'overlap_score': overlap
                })
        
        # Ordenar por sobreposição
        matching.sort(key=lambda x: x['overlap_score'], reverse=True)
        return matching
    
    def _calculate_bbox_overlap(self, bbox1: Tuple[int, int, int, int], 
                               bbox2: Tuple[int, int, int, int]) -> float:
        """Calcula sobreposição entre dois bounding boxes"""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        # Calcular interseção
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
        """Seleciona o texto principal de uma lista de textos correspondentes"""
        if not matching_texts:
            return None
        
        # Selecionar baseado na confiança e sobreposição
        best_text = max(matching_texts, 
                       key=lambda x: x['confidence'] * x['overlap_score'])
        
        return best_text['text']
    
    def _calculate_integrated_confidence(self, detection: Dict[str, Any], 
                                       matching_texts: List[Dict[str, Any]]) -> float:
        """Calcula confiança integrada considerando detecção e OCR"""
        detection_conf = detection['confidence']
        
        if not matching_texts:
            return detection_conf * 0.5  # Penalizar se não houver texto
        
        # Média ponderada da confiança de detecção e OCR
        ocr_conf = np.mean([t['confidence'] for t in matching_texts])
        overlap_score = np.mean([t['overlap_score'] for t in matching_texts])
        
        integrated_conf = (detection_conf * 0.4 + 
                          ocr_conf * 0.4 + 
                          overlap_score * 0.2)
        
        return integrated_conf
    
    def _validate_results(self, integrated_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Valida os resultados integrados"""
        validation_rules = self.config.get('validation_rules', {})
        validated = []
        
        for result in integrated_results:
            if self._validate_single_result(result, validation_rules):
                validated.append(result)
        
        return validated
    
    def _validate_single_result(self, result: Dict[str, Any], 
                              validation_rules: Dict[str, Any]) -> bool:
        """Valida um resultado individual"""
        detection = result['detection']
        
        # Validar tamanho
        min_size = validation_rules.get('min_plate_size', (50, 50))
        max_size = validation_rules.get('max_plate_size', (800, 400))
        
        w, h = detection['bbox'][2], detection['bbox'][3]
        if w < min_size[0] or h < min_size[1] or w > max_size[0] or h > max_size[1]:
            return False
        
        # Validar confiança
        min_confidence = validation_rules.get('min_confidence', 0.3)
        if result['confidence_score'] < min_confidence:
            return False
        
        # Validar texto se disponível
        if result['primary_text']:
            text = result['primary_text']
            min_length = validation_rules.get('min_text_length', 3)
            max_length = validation_rules.get('max_text_length', 20)
            
            if len(text) < min_length or len(text) > max_length:
                return False
        
        return True
    
    def process_image_advanced(self, image_path: str) -> PipelineResult:
        """Processa uma imagem com pipeline avançado"""
        start_time = time.time()
        
        try:
            # Carregar imagem
            image = self.load_image(image_path)
            if image is None:
                return PipelineResult(
                    success=False,
                    image_path=image_path,
                    processing_time=0.0,
                    error_message="Falha ao carregar imagem"
                )
            
            # 1. Pré-processamento
            self.logger.info("📸 Aplicando pré-processamento...")
            preprocessed_image = self.preprocess_image(image)
            preprocessing_metadata = self.preprocessor.get_preprocessing_summary()
            
            # 2. Detecção
            self.logger.info("🔍 Executando detecção...")
            detection_result = self.detector.detect(preprocessed_image)
            detection_metadata = self.detector.get_detection_statistics(detection_result.detections)
            
            # 3. OCR nas regiões detectadas
            self.logger.info("📝 Extraindo texto...")
            ocr_result = self.text_extractor.extract_text(preprocessed_image, 
                                                         [{'bbox': det.bbox} for det in detection_result.detections])
            ocr_metadata = self.text_extractor.get_ocr_statistics(ocr_result)
            
            # 4. Integração e validação
            self.logger.info("🔗 Integrando resultados...")
            integrated_results = self._integrate_detections_and_ocr(
                [{'bbox': det.bbox, 'confidence': det.confidence, 'class_id': det.class_id, 
                  'class_name': det.class_name, 'area': det.area, 'center': det.center} 
                 for det in detection_result.detections],
                [{'text': r.text, 'confidence': r.confidence, 'bbox': r.bbox, 
                  'language': r.language, 'processing_time': r.processing_time} 
                 for r in ocr_result.text_results]
            )
            
            validated_results = self._validate_results(integrated_results)
            
            # 5. Criar resultado final
            processing_time = time.time() - start_time
            
            result = PipelineResult(
                success=True,
                image_path=image_path,
                processing_time=processing_time,
                preprocessing_result=preprocessing_metadata,
                detection_result=detection_metadata,
                ocr_result=ocr_metadata,
                final_results=validated_results,
                metadata={
                    'pipeline_version': '2.0.0',
                    'components_used': ['preprocessor', 'detector', 'ocr'],
                    'total_detections': len(detection_result.detections),
                    'total_texts': len(ocr_result.text_results),
                    'validated_results': len(validated_results),
                    'processing_times': {
                        'preprocessing': preprocessing_metadata.get('processing_time', 0),
                        'detection': detection_result.processing_time,
                        'ocr': ocr_result.total_processing_time,
                        'total': processing_time
                    }
                }
            )
            
            self.logger.info(f"✅ Processamento concluído em {processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"❌ Erro no processamento: {e}")
            
            return PipelineResult(
                success=False,
                image_path=image_path,
                processing_time=processing_time,
                error_message=str(e)
            )
    
    def process_batch(self, image_paths: List[str], 
                     output_dir: str = None) -> List[PipelineResult]:
        """Processa múltiplas imagens em lote"""
        results = []
        
        for i, image_path in enumerate(image_paths):
            self.logger.info(f"🔄 Processando imagem {i+1}/{len(image_paths)}: {image_path}")
            
            try:
                result = self.process_image_advanced(image_path)
                results.append(result)
                
                # Salvar resultado se diretório de saída for especificado
                if output_dir and result.success:
                    self._save_result(result, output_dir, i)
                    
            except Exception as e:
                self.logger.error(f"Erro ao processar {image_path}: {e}")
                results.append(PipelineResult(
                    success=False,
                    image_path=image_path,
                    processing_time=0.0,
                    error_message=str(e)
                ))
        
        return results
    
    def _save_result(self, result: PipelineResult, output_dir: str, index: int):
        """Salva resultado do processamento"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Salvar metadados
            metadata_file = output_path / f"result_{index:04d}.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'success': result.success,
                    'image_path': result.image_path,
                    'processing_time': result.processing_time,
                    'final_results': result.final_results,
                    'metadata': result.metadata,
                    'timestamp': result.timestamp.isoformat()
                }, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Resultado salvo em: {metadata_file}")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar resultado: {e}")
    
    def get_pipeline_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do pipeline"""
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
    
    def cleanup(self):
        """Limpa recursos do pipeline"""
        self.logger.info("🧹 Limpando recursos do pipeline...")
        
        if self.preprocessor:
            self.preprocessor = None
        
        if self.detector:
            self.detector.cleanup()
            self.detector = None
        
        if self.text_extractor:
            self.text_extractor.cleanup()
            self.text_extractor = None
        
        self.cache.clear()
        super().cleanup()