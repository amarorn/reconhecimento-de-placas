#!/usr/bin/env python3
"""
Pré-processamento de Imagens
============================

Módulo para pré-processamento de imagens antes da detecção.
"""

import cv2
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

class EnhancementMethod(str, Enum):
    """Métodos de melhoria de contraste"""
    HISTOGRAM_EQUALIZATION = "histogram_equalization"
    CLAHE = "clahe"
    ADAPTIVE_THRESHOLD = "adaptive_threshold"

class DenoisingMethod(str, Enum):
    """Métodos de redução de ruído"""
    BILATERAL = "bilateral"
    GAUSSIAN = "gaussian"
    MEDIAN = "median"
    NLM = "nlm"

@dataclass
class PreprocessingResult:
    """Resultado do pré-processamento"""
    processed_image: np.ndarray
    original_shape: Tuple[int, int, int]
    processing_time: float
    applied_methods: List[str]
    metadata: Dict[str, Any]

class ImagePreprocessor:
    """Pré-processador de imagens"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.enhancement_methods = []
        self.denoising_methods = []
    
    def preprocess(self, image: np.ndarray) -> PreprocessingResult:
        """Executa pré-processamento completo da imagem"""
        import time
        start_time = time.time()
        
        original_shape = image.shape
        processed_image = image.copy()
        applied_methods = []
        
        try:
            # Redimensionamento
            if self.config.get('resize_enabled', True):
                processed_image = self._resize_image(processed_image)
                applied_methods.append('resize')
            
            # Redução de ruído
            if self.config.get('denoising_enabled', True):
                processed_image = self._apply_denoising(processed_image)
                applied_methods.append('denoising')
            
            # Melhoria de contraste
            if self.config.get('contrast_enhancement', True):
                processed_image = self._enhance_contrast(processed_image)
                applied_methods.append('contrast_enhancement')
            
            # Normalização
            if self.config.get('normalization', True):
                processed_image = self._normalize_image(processed_image)
                applied_methods.append('normalization')
            
            # Filtros adicionais
            if self.config.get('additional_filters', False):
                processed_image = self._apply_additional_filters(processed_image)
                applied_methods.append('additional_filters')
            
            processing_time = time.time() - start_time
            
            return PreprocessingResult(
                processed_image=processed_image,
                original_shape=original_shape,
                processing_time=processing_time,
                applied_methods=applied_methods,
                metadata={
                    'config': self.config,
                    'final_shape': processed_image.shape
                }
            )
            
        except Exception as e:
            self.logger.error(f"Erro no pré-processamento: {e}")
            processing_time = time.time() - start_time
            
            return PreprocessingResult(
                processed_image=image,
                original_shape=original_shape,
                processing_time=processing_time,
                applied_methods=applied_methods,
                metadata={
                    'error': str(e),
                    'config': self.config
                }
            )
    
    def _resize_image(self, image: np.ndarray) -> np.ndarray:
        """Redimensiona a imagem"""
        target_size = self.config.get('target_size', (640, 640))
        method = self.config.get('resize_method', cv2.INTER_LINEAR)
        
        if method == 'bilinear':
            method = cv2.INTER_LINEAR
        elif method == 'bicubic':
            method = cv2.INTER_CUBIC
        elif method == 'lanczos':
            method = cv2.INTER_LANCZOS4
        elif method == 'nearest':
            method = cv2.INTER_NEAREST
        
        resized = cv2.resize(image, target_size, interpolation=method)
        self.logger.debug(f"Imagem redimensionada de {image.shape} para {target_size}")
        
        return resized
    
    def _apply_denoising(self, image: np.ndarray) -> np.ndarray:
        """Aplica redução de ruído"""
        method = self.config.get('denoising_method', DenoisingMethod.BILATERAL)
        
        if method == DenoisingMethod.BILATERAL:
            return cv2.bilateralFilter(image, 9, 75, 75)
        
        elif method == DenoisingMethod.GAUSSIAN:
            return cv2.GaussianBlur(image, (5, 5), 0)
        
        elif method == DenoisingMethod.MEDIAN:
            return cv2.medianBlur(image, 5)
        
        elif method == DenoisingMethod.NLM:
            return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        
        return image
    
    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Melhora o contraste da imagem"""
        method = self.config.get('contrast_method', EnhancementMethod.CLAHE)
        
        if method == EnhancementMethod.HISTOGRAM_EQUALIZATION:
            if len(image.shape) == 3:
                enhanced = np.zeros_like(image)
                for i in range(3):
                    enhanced[:, :, i] = cv2.equalizeHist(image[:, :, i])
                return enhanced
            else:
                return cv2.equalizeHist(image)
        
        elif method == EnhancementMethod.CLAHE:
            clahe = cv2.createCLAHE(
                clipLimit=self.config.get('clahe_clip_limit', 2.0),
                tileGridSize=self.config.get('clahe_tile_size', (8, 8))
            )
            
            if len(image.shape) == 3:
                enhanced = np.zeros_like(image)
                for i in range(3):
                    enhanced[:, :, i] = clahe.apply(image[:, :, i])
                return enhanced
            else:
                return clahe.apply(image)
        
        elif method == EnhancementMethod.ADAPTIVE_THRESHOLD:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image
            
            adaptive_thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            return adaptive_thresh
        
        return image
    
    def _normalize_image(self, image: np.ndarray) -> np.ndarray:
        """Aplica normalização e filtros adicionais"""
        if self.config.get('sharpen_enabled', False):
            kernel = np.array([[-1, -1, -1],
                             [-1,  9, -1],
                             [-1, -1, -1]])
            image = cv2.filter2D(image, -1, kernel)
        
        if self.config.get('emboss_enabled', False):
            kernel = np.array([[-2, -1, 0],
                             [-1,  1, 1],
                             [ 0,  1, 2]])
            image = cv2.filter2D(image, -1, kernel)
        
        if self.config.get('gamma_correction', False):
            gamma = self.config.get('gamma_value', 1.2)
            inv_gamma = 1.0 / gamma
            table = np.array([((i / 255.0) ** inv_gamma) * 255
                            for i in np.arange(0, 256)]).astype("uint8")
            image = cv2.LUT(image, table)
        
        return image
    
    def _apply_additional_filters(self, image: np.ndarray) -> np.ndarray:
        """Aplica filtros adicionais"""
        if self.config.get('edge_detection', False):
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image
            
            edges = cv2.Canny(gray, 50, 150)
            return cv2.addWeighted(image, 0.7, cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB), 0.3, 0)
        
        return image
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Retorna resumo da configuração"""
        return {
            'resize_enabled': self.config.get('resize_enabled', True),
            'denoising_enabled': self.config.get('denoising_enabled', True),
            'contrast_enhancement': self.config.get('contrast_enhancement', True),
            'normalization': self.config.get('normalization', True),
            'additional_filters': self.config.get('additional_filters', False),
            'target_size': self.config.get('target_size', (640, 640)),
            'denoising_method': str(self.config.get('denoising_method', DenoisingMethod.BILATERAL)),
            'contrast_method': str(self.config.get('contrast_method', EnhancementMethod.CLAHE))
        }