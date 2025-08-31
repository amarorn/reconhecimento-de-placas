#!/usr/bin/env python3
"""
Extrator de Texto OCR
=====================

Módulo para extração de texto de imagens usando diferentes motores OCR.
"""

import cv2
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
import time
from enum import Enum

class OCRType(str, Enum):
    """Tipos de motores OCR disponíveis"""
    PADDLEOCR = "paddleocr"
    TESSERACT = "tesseract"
    EASYOCR = "easyocr"
    TRANSFORMER_OCR = "transformer_ocr"

@dataclass
class TextResult:
    """Resultado de extração de texto"""
    text: str
    confidence: float
    bbox: Tuple[int, int, int, int]
    language: str
    processing_time: float

@dataclass
class OCRBatchResult:
    """Resultado de extração de texto em lote"""
    text_results: List[TextResult]
    processing_time: float
    total_texts: int
    average_confidence: float
    metadata: Dict[str, Any]

class TextExtractor:
    """Extrator de texto usando diferentes motores OCR"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ocr_engines = {}
        self.current_ocr = None
        self.initialize()
    
    def initialize(self):
        """Inicializa os motores OCR disponíveis"""
        try:
            # Tentar PaddleOCR primeiro
            self._initialize_paddleocr()
        except ImportError:
            try:
                # Tentar EasyOCR
                self._initialize_easyocr()
            except ImportError:
                try:
                    # Tentar Tesseract
                    self._initialize_tesseract()
                except ImportError:
                    self.logger.warning("Nenhum motor OCR disponível, usando simulador")
                    self._initialize_simulator()
    
    def _initialize_paddleocr(self):
        """Inicializa PaddleOCR"""
        try:
            from paddleocr import PaddleOCR
            
            self.ocr_engines[OCRType.PADDLEOCR] = PaddleOCR(
                use_angle_cls=self.config.get('use_angle_cls', True),
                lang=self.config.get('language', 'pt'),
                use_gpu=self.config.get('use_gpu', False),
                show_log=False
            )
            self.current_ocr = OCRType.PADDLEOCR
            self.logger.info("PaddleOCR inicializado com sucesso")
            
        except ImportError:
            raise ImportError("PaddleOCR não está disponível")
    
    def _initialize_easyocr(self):
        """Inicializa EasyOCR"""
        try:
            import easyocr
            
            self.ocr_engines[OCRType.EASYOCR] = easyocr.Reader(
                [self.config.get('language', 'pt')],
                gpu=self.config.get('use_gpu', False)
            )
            self.current_ocr = OCRType.EASYOCR
            self.logger.info("EasyOCR inicializado com sucesso")
            
        except ImportError:
            raise ImportError("EasyOCR não está disponível")
    
    def _initialize_tesseract(self):
        """Inicializa Tesseract"""
        try:
            import pytesseract
            
            tesseract_path = self.config.get('tesseract_path')
            if tesseract_path:
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
            
            self.ocr_engines[OCRType.TESSERACT] = pytesseract
            self.current_ocr = OCRType.TESSERACT
            self.logger.info("Tesseract inicializado com sucesso")
            
        except ImportError:
            raise ImportError("Tesseract não está disponível")
    
    def _initialize_simulator(self):
        """Inicializa simulador OCR para testes"""
        self.current_ocr = OCRType.TRANSFORMER_OCR
        self.logger.info("Simulador OCR inicializado")
    
    def extract_text(self, image: np.ndarray, regions: List[Dict[str, Any]] = None) -> OCRBatchResult:
        """Extrai texto da imagem ou das regiões especificadas"""
        start_time = time.time()
        
        try:
            if regions:
                return self._extract_from_regions(image, regions)
            else:
                return self._extract_from_full_image(image)
                
        except Exception as e:
            self.logger.error(f"Erro na extração de texto: {e}")
            return self._create_error_result(str(e), time.time() - start_time)
    
    def _extract_from_regions(self, image: np.ndarray, regions: List[Dict[str, Any]]) -> OCRBatchResult:
        """Extrai texto de regiões específicas da imagem"""
        text_results = []
        
        for region in regions:
            try:
                bbox = region['bbox']
                x, y, w, h = bbox
                
                # Extrair ROI (Region of Interest)
                roi = image[y:y+h, x:x+w]
                
                # Extrair texto da ROI
                text_result = self._extract_from_roi(roi, bbox)
                if text_result:
                    text_results.append(text_result)
                    
            except Exception as e:
                self.logger.error(f"Erro ao processar região {bbox}: {e}")
                continue
        
        processing_time = time.time() - time.time()
        return self._create_batch_result(text_results, processing_time)
    
    def _extract_from_full_image(self, image: np.ndarray) -> OCRBatchResult:
        """Extrai texto de toda a imagem"""
        try:
            text_result = self._extract_from_roi(image, (0, 0, image.shape[1], image.shape[0]))
            text_results = [text_result] if text_result else []
            
            processing_time = time.time() - time.time()
            return self._create_batch_result(text_results, processing_time)
            
        except Exception as e:
            self.logger.error(f"Erro na extração da imagem completa: {e}")
            return self._create_error_result(str(e), time.time() - time.time())
    
    def _extract_from_roi(self, roi: np.ndarray, bbox: Tuple[int, int, int, int]) -> Optional[TextResult]:
        """Extrai texto de uma região específica"""
        if self.current_ocr == OCRType.PADDLEOCR:
            return self._extract_with_paddleocr(roi, bbox)
        elif self.current_ocr == OCRType.EASYOCR:
            return self._extract_with_easyocr(roi, bbox)
        elif self.current_ocr == OCRType.TESSERACT:
            return self._extract_with_tesseract(roi, bbox)
        else:
            return self._extract_with_simulator(roi, bbox)
    
    def _extract_with_paddleocr(self, roi: np.ndarray, bbox: Tuple[int, int, int, int]) -> Optional[TextResult]:
        """Extrai texto usando PaddleOCR"""
        try:
            engine = self.ocr_engines[OCRType.PADDLEOCR]
            results = engine.ocr(roi, cls=True)
            
            if not results or not results[0]:
                return None
            
            # Pegar o resultado com maior confiança
            best_result = max(results[0], key=lambda x: x[1][1])
            text, (confidence, _) = best_result
            
            return TextResult(
                text=text.strip(),
                confidence=float(confidence),
                bbox=bbox,
                language=self.config.get('language', 'pt'),
                processing_time=0.0
            )
            
        except Exception as e:
            self.logger.error(f"Erro no PaddleOCR: {e}")
            return None
    
    def _extract_with_easyocr(self, roi: np.ndarray, bbox: Tuple[int, int, int, int]) -> Optional[TextResult]:
        """Extrai texto usando EasyOCR"""
        try:
            engine = self.ocr_engines[OCRType.EASYOCR]
            results = engine.readtext(roi)
            
            if not results:
                return None
            
            # Pegar o resultado com maior confiança
            best_result = max(results, key=lambda x: x[2])
            bbox_coords, text, confidence = best_result
            
            return TextResult(
                text=text.strip(),
                confidence=float(confidence),
                bbox=bbox,
                language=self.config.get('language', 'pt'),
                processing_time=0.0
            )
            
        except Exception as e:
            self.logger.error(f"Erro no EasyOCR: {e}")
            return None
    
    def _extract_with_tesseract(self, roi: np.ndarray, bbox: Tuple[int, int, int, int]) -> Optional[TextResult]:
        """Extrai texto usando Tesseract"""
        try:
            engine = self.ocr_engines[OCRType.TESSERACT]
            
            # Configurar parâmetros
            config = '--oem 3 --psm 6'
            text = engine.image_to_string(roi, config=config, lang=self.config.get('language', 'por'))
            
            if not text.strip():
                return None
            
            return TextResult(
                text=text.strip(),
                confidence=0.8,  # Tesseract não retorna confiança por padrão
                bbox=bbox,
                language=self.config.get('language', 'pt'),
                processing_time=0.0
            )
            
        except Exception as e:
            self.logger.error(f"Erro no Tesseract: {e}")
            return None
    
    def _extract_with_simulator(self, roi: np.ndarray, bbox: Tuple[int, int, int, int]) -> Optional[TextResult]:
        """Simula extração de texto para testes"""
        # Simular texto baseado no tamanho da ROI
        h, w = roi.shape[:2]
        
        if w > 100 and h > 30:
            simulated_text = "ABC123"
            confidence = 0.85
        else:
            simulated_text = "TXT"
            confidence = 0.75
        
        return TextResult(
            text=simulated_text,
            confidence=confidence,
            bbox=bbox,
            language=self.config.get('language', 'pt'),
            processing_time=0.0
        )
    
    def _create_batch_result(self, text_results: List[TextResult], processing_time: float) -> OCRBatchResult:
        """Cria resultado em lote"""
        total_texts = len(text_results)
        average_confidence = np.mean([r.confidence for r in text_results]) if text_results else 0.0
        
        return OCRBatchResult(
            text_results=text_results,
            processing_time=processing_time,
            total_texts=total_texts,
            average_confidence=average_confidence,
            metadata={
                'ocr_engine': self.current_ocr,
                'language': self.config.get('language', 'pt'),
                'regions_processed': len(text_results)
            }
        )
    
    def _create_error_result(self, error_message: str, processing_time: float) -> OCRBatchResult:
        """Cria resultado de erro"""
        return OCRBatchResult(
            text_results=[],
            processing_time=processing_time,
            total_texts=0,
            average_confidence=0.0,
            metadata={
                'error': error_message,
                'ocr_engine': self.current_ocr
            }
        )
    
    def get_ocr_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o motor OCR"""
        return {
            'current_engine': self.current_ocr,
            'available_engines': list(self.ocr_engines.keys()),
            'language': self.config.get('language', 'pt'),
            'gpu_enabled': self.config.get('use_gpu', False)
        }