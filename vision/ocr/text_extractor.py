#!/usr/bin/env python3
"""
Extrator de Texto com Múltiplos Motores OCR
============================================

Este módulo implementa extração de texto usando diferentes motores OCR
especialmente otimizado para placas de trânsito e veículos.
"""

import cv2
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
import logging
from dataclasses import dataclass
from enum import Enum
import re
import os

class OCRType(Enum):
    """Tipos de OCR suportados"""
    PADDLEOCR = "paddleocr"
    EASYOCR = "easyocr"
    TESSERACT = "tesseract"
    TRANSFORMER_OCR = "transformer_ocr"

@dataclass
class TextResult:
    """Resultado de extração de texto"""
    text: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x, y, w, h
    language: str
    processing_time: float

@dataclass
class OCRBatchResult:
    """Resultado de OCR em lote"""
    text_results: List[TextResult]
    total_processing_time: float
    metadata: Dict[str, Any]

class TextExtractor:
    """Extrator de texto com múltiplos motores OCR"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ocr_engines = {}
        self.current_ocr = None
        self.initialize()
    
    def initialize(self):
        """Inicializa os motores OCR disponíveis"""
        try:
            ocr_type = self.config.get('type', OCRType.PADDLEOCR)
            
            if ocr_type == OCRType.PADDLEOCR:
                self._initialize_paddleocr()
            elif ocr_type == OCRType.EASYOCR:
                self._initialize_easyocr()
            elif ocr_type == OCRType.TESSERACT:
                self._initialize_tesseract()
            elif ocr_type == OCRType.TRANSFORMER_OCR:
                self._initialize_transformer_ocr()
            else:
                self.logger.warning(f"Tipo de OCR não suportado: {ocr_type}")
                self._initialize_paddleocr()  # Fallback
            
            self.logger.info(f"OCR inicializado com sucesso: {ocr_type}")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar OCR: {e}")
            # Tentar fallback
            self._initialize_fallback()
    
    def _initialize_paddleocr(self):
        """Inicializa PaddleOCR"""
        try:
            from paddleocr import PaddleOCR
            
            self.ocr_engines[OCRType.PADDLEOCR] = PaddleOCR(
                use_angle_cls=self.config.get('use_angle_cls', True),
                lang=self.config.get('language', 'pt'),
                use_gpu=self.config.get('use_gpu', True),
                show_log=False
            )
            self.current_ocr = OCRType.PADDLEOCR
            
        except ImportError:
            self.logger.warning("PaddleOCR não disponível, tentando próximo...")
            raise
    
    def _initialize_easyocr(self):
        """Inicializa EasyOCR"""
        try:
            import easyocr
            
            self.ocr_engines[OCRType.EASYOCR] = easyocr.Reader(
                [self.config.get('language', 'pt')],
                gpu=self.config.get('use_gpu', True),
                model_storage_directory='./models',
                download_enabled=True
            )
            self.current_ocr = OCRType.EASYOCR
            
        except ImportError:
            self.logger.warning("EasyOCR não disponível, tentando próximo...")
            raise
    
    def _initialize_tesseract(self):
        """Inicializa Tesseract"""
        try:
            import pytesseract
            
            # Configurar caminho do Tesseract se necessário
            tesseract_path = self.config.get('tesseract_path')
            if tesseract_path:
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
            
            self.ocr_engines[OCRType.TESSERACT] = pytesseract
            self.current_ocr = OCRType.TESSERACT
            
        except ImportError:
            self.logger.warning("Tesseract não disponível, tentando próximo...")
            raise
    
    def _initialize_transformer_ocr(self):
        """Inicializa OCR baseado em Transformers"""
        try:
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel
            
            model_name = self.config.get('transformer_model', 'microsoft/trocr-base-handwritten')
            processor = TrOCRProcessor.from_pretrained(model_name)
            model = VisionEncoderDecoderModel.from_pretrained(model_name)
            
            self.ocr_engines[OCRType.TRANSFORMER_OCR] = {
                'processor': processor,
                'model': model
            }
            self.current_ocr = OCRType.TRANSFORMER_OCR
            
        except ImportError:
            self.logger.warning("Transformers não disponível, tentando próximo...")
            raise
    
    def _initialize_fallback(self):
        """Inicializa OCR de fallback"""
        self.logger.info("Inicializando OCR de fallback...")
        
        # Tentar Tesseract como último recurso
        try:
            self._initialize_tesseract()
        except:
            self.logger.error("Nenhum motor OCR disponível!")
            raise RuntimeError("Nenhum motor OCR disponível")
    
    def extract_text(self, image: np.ndarray, regions: List[Dict[str, Any]] = None) -> OCRBatchResult:
        """Extrai texto da imagem ou das regiões especificadas"""
        start_time = self._get_time()
        
        if regions is None:
            # Processar imagem inteira
            regions = [{'bbox': (0, 0, image.shape[1], image.shape[0])}]
        
        text_results = []
        
        for region in regions:
            try:
                # Extrair região da imagem
                x, y, w, h = region['bbox']
                roi = image[y:y+h, x:x+w]
                
                if roi.size == 0:
                    continue
                
                # Aplicar OCR na região
                region_text = self._extract_from_region(roi)
                
                if region_text:
                    text_results.append(TextResult(
                        text=region_text['text'],
                        confidence=region_text['confidence'],
                        bbox=region['bbox'],
                        language=self.config.get('language', 'pt'),
                        processing_time=region_text['processing_time']
                    ))
                    
            except Exception as e:
                self.logger.warning(f"Erro ao processar região {region}: {e}")
                continue
        
        total_time = self._get_time() - start_time
        
        return OCRBatchResult(
            text_results=text_results,
            total_processing_time=total_time,
            metadata={
                'ocr_type': str(self.current_ocr),
                'regions_processed': len(regions),
                'texts_extracted': len(text_results)
            }
        )
    
    def _extract_from_region(self, roi: np.ndarray) -> Optional[Dict[str, Any]]:
        """Extrai texto de uma região específica"""
        start_time = self._get_time()
        
        try:
            if self.current_ocr == OCRType.PADDLEOCR:
                return self._extract_with_paddleocr(roi)
            elif self.current_ocr == OCRType.EASYOCR:
                return self._extract_with_easyocr(roi)
            elif self.current_ocr == OCRType.TESSERACT:
                return self._extract_with_tesseract(roi)
            elif self.current_ocr == OCRType.TRANSFORMER_OCR:
                return self._extract_with_transformer(roi)
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Erro na extração de texto: {e}")
            return None
    
    def _extract_with_paddleocr(self, roi: np.ndarray) -> Optional[Dict[str, Any]]:
        """Extrai texto usando PaddleOCR"""
        try:
            # Converter para BGR se necessário
            if len(roi.shape) == 3:
                roi_bgr = cv2.cvtColor(roi, cv2.COLOR_RGB2BGR)
            else:
                roi_bgr = roi
            
            results = self.ocr_engines[OCRType.PADDLEOCR].ocr(roi_bgr, cls=True)
            
            if not results or not results[0]:
                return None
            
            # PaddleOCR retorna lista de tuplas (bbox, (text, confidence))
            best_result = max(results[0], key=lambda x: x[1][1])  # Maior confiança
            
            text, confidence = best_result[1]
            processing_time = self._get_time() - start_time
            
            return {
                'text': text.strip(),
                'confidence': float(confidence),
                'processing_time': processing_time
            }
            
        except Exception as e:
            self.logger.error(f"Erro no PaddleOCR: {e}")
            return None
    
    def _extract_with_easyocr(self, roi: np.ndarray) -> Optional[Dict[str, Any]]:
        """Extrai texto usando EasyOCR"""
        try:
            results = self.ocr_engines[OCRType.EASYOCR].readtext(roi)
            
            if not results:
                return None
            
            # EasyOCR retorna lista de tuplas (bbox, text, confidence)
            best_result = max(results, key=lambda x: x[2])  # Maior confiança
            
            bbox, text, confidence = best_result
            processing_time = self._get_time() - start_time
            
            return {
                'text': text.strip(),
                'confidence': float(confidence),
                'processing_time': processing_time
            }
            
        except Exception as e:
            self.logger.error(f"Erro no EasyOCR: {e}")
            return None
    
    def _extract_with_tesseract(self, roi: np.ndarray) -> Optional[Dict[str, Any]]:
        """Extrai texto usando Tesseract"""
        try:
            # Configurar parâmetros do Tesseract
            config = '--oem 3 --psm 6'  # PSM 6: bloco uniforme de texto
            
            # Converter para escala de cinza se necessário
            if len(roi.shape) == 3:
                roi_gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
            else:
                roi_gray = roi
            
            # Aplicar pré-processamento para melhorar OCR
            roi_processed = self._preprocess_for_tesseract(roi_gray)
            
            # Extrair texto
            text = self.ocr_engines[OCRType.TESSERACT].image_to_string(
                roi_processed, 
                config=config,
                lang=self.config.get('language', 'por')
            )
            
            # Calcular confiança (Tesseract não fornece confiança por padrão)
            confidence = self._estimate_tesseract_confidence(roi_processed, text)
            
            processing_time = self._get_time() - start_time
            
            return {
                'text': text.strip(),
                'confidence': confidence,
                'processing_time': processing_time
            }
            
        except Exception as e:
            self.logger.error(f"Erro no Tesseract: {e}")
            return None
    
    def _extract_with_transformer(self, roi: np.ndarray) -> Optional[Dict[str, Any]]:
        """Extrai texto usando modelo Transformer"""
        try:
            engine = self.ocr_engines[OCRType.TRANSFORMER_OCR]
            processor = engine['processor']
            model = engine['model']
            
            # Converter para PIL Image
            from PIL import Image
            pil_image = Image.fromarray(roi)
            
            # Processar imagem
            pixel_values = processor(pil_image, return_tensors="pt").pixel_values
            
            # Gerar texto
            generated_ids = model.generate(pixel_values)
            generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            # Para modelos Transformer, usar confiança padrão
            confidence = 0.8
            
            processing_time = self._get_time() - start_time
            
            return {
                'text': generated_text.strip(),
                'confidence': confidence,
                'processing_time': processing_time
            }
            
        except Exception as e:
            self.logger.error(f"Erro no Transformer OCR: {e}")
            return None
    
    def _preprocess_for_tesseract(self, image: np.ndarray) -> np.ndarray:
        """Pré-processa imagem para melhorar resultados do Tesseract"""
        # Aplicar threshold adaptativo
        thresh = cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Remover ruído
        kernel = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def _estimate_tesseract_confidence(self, image: np.ndarray, text: str) -> float:
        """Estima confiança para resultados do Tesseract"""
        if not text.strip():
            return 0.0
        
        # Fatores para estimar confiança
        text_length = len(text.strip())
        image_quality = self._assess_image_quality(image)
        
        # Confiança baseada na qualidade da imagem e comprimento do texto
        base_confidence = min(0.9, 0.3 + image_quality * 0.4 + min(text_length / 20, 0.3))
        
        return base_confidence
    
    def _assess_image_quality(self, image: np.ndarray) -> float:
        """Avalia a qualidade da imagem para OCR"""
        # Calcular gradiente para avaliar nitidez
        grad_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Calcular variância local para avaliar contraste
        local_variance = cv2.GaussianBlur(image.astype(np.float64)**2, (5, 5), 1) - \
                        cv2.GaussianBlur(image.astype(np.float64), (5, 5), 1)**2
        
        # Normalizar métricas
        sharpness = np.mean(gradient_magnitude) / 255.0
        contrast = np.mean(local_variance) / (255.0**2)
        
        # Combinar métricas
        quality_score = (sharpness * 0.6 + contrast * 0.4)
        
        return min(1.0, quality_score)
    
    def _get_time(self) -> float:
        """Retorna tempo atual em segundos"""
        import time
        return time.time()
    
    def postprocess_text(self, text: str) -> str:
        """Pós-processa o texto extraído"""
        if not text:
            return text
        
        # Remover caracteres especiais e normalizar
        text = re.sub(r'[^\w\s\-]', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip().upper()
        
        # Aplicar regras específicas para placas
        if self.config.get('apply_plate_rules', True):
            text = self._apply_plate_rules(text)
        
        return text
    
    def _apply_plate_rules(self, text: str) -> str:
        """Aplica regras específicas para placas de trânsito e veículos"""
        # Remover espaços extras
        text = text.replace(' ', '')
        
        # Padrão brasileiro: 3 letras + 4 números (ABC1234)
        plate_pattern = re.compile(r'^[A-Z]{3}\d{4}$')
        if plate_pattern.match(text):
            return text
        
        # Padrão mercosul: 3 letras + 1 número + 1 letra + 2 números (ABC1D23)
        mercosul_pattern = re.compile(r'^[A-Z]{3}\d[A-Z]\d{2}$')
        if mercosul_pattern.match(text):
            return text
        
        # Padrão moto: 3 letras + 2 números + 1 letra + 1 número (ABC12D3)
        moto_pattern = re.compile(r'^[A-Z]{3}\d{2}[A-Z]\d$')
        if moto_pattern.match(text):
            return text
        
        # Se não corresponder a nenhum padrão, retornar texto limpo
        return text
    
    def get_ocr_statistics(self, results: OCRBatchResult) -> Dict[str, Any]:
        """Retorna estatísticas dos resultados OCR"""
        if not results.text_results:
            return {
                'total_texts': 0,
                'average_confidence': 0.0,
                'text_lengths': [],
                'processing_times': []
            }
        
        confidences = [r.confidence for r in results.text_results]
        text_lengths = [len(r.text) for r in results.text_results]
        processing_times = [r.processing_time for r in results.text_results]
        
        return {
            'total_texts': len(results.text_results),
            'average_confidence': np.mean(confidences),
            'min_confidence': np.min(confidences),
            'max_confidence': np.max(confidences),
            'average_text_length': np.mean(text_lengths),
            'average_processing_time': np.mean(processing_times),
            'total_processing_time': results.total_processing_time
        }
    
    def cleanup(self):
        """Limpa recursos do OCR"""
        for engine in self.ocr_engines.values():
            if hasattr(engine, 'cleanup'):
                engine.cleanup()
        
        self.ocr_engines.clear()
        self.current_ocr = None