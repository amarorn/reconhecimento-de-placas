#!/usr/bin/env python3
"""
Processador de Pré-processamento de Imagens
==========================================

Este módulo implementa técnicas avançadas de pré-processamento
para melhorar a qualidade das imagens antes da detecção.
"""

import cv2
import numpy as np
from typing import Dict, Any, Tuple, Optional, List
import logging
from enum import Enum
from dataclasses import dataclass

class EnhancementMethod(Enum):
    """Métodos de melhoria de imagem"""
    HISTOGRAM_EQUALIZATION = "histogram_equalization"
    CLAHE = "clahe"
    ADAPTIVE_THRESHOLD = "adaptive_threshold"
    AI_ENHANCEMENT = "ai_enhancement"

class DenoisingMethod(Enum):
    """Métodos de redução de ruído"""
    GAUSSIAN = "gaussian"
    BILATERAL = "bilateral"
    MEDIAN = "median"
    NON_LOCAL_MEANS = "non_local_means"

@dataclass
class PreprocessingResult:
    """Resultado do pré-processamento"""
    processed_image: np.ndarray
    metadata: Dict[str, Any]
    enhancement_applied: List[str]

class ImagePreprocessor:
    """Processador avançado de pré-processamento de imagens"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.enhancement_methods = []
        self.denoising_methods = []
        
    def preprocess(self, image: np.ndarray) -> PreprocessingResult:
        """Aplica pipeline completo de pré-processamento"""
        if image is None:
            raise ValueError("Imagem não pode ser None")
        
        original_image = image.copy()
        metadata = {
            'original_shape': image.shape,
            'original_dtype': str(image.dtype),
            'enhancements_applied': []
        }
        
        # 1. Redimensionamento
        if self.config.get('resize_enabled', True):
            target_size = self.config.get('target_size', (640, 640))
            image = self.resize_image(image, target_size)
            metadata['resized_to'] = target_size
        
        # 2. Redução de ruído
        if self.config.get('denoising_enabled', True):
            image = self.apply_denoising(image)
            metadata['enhancements_applied'].append('denoising')
        
        # 3. Melhoria de contraste
        if self.config.get('contrast_enhancement', True):
            image = self.enhance_contrast(image)
            metadata['enhancements_applied'].append('contrast_enhancement')
        
        # 4. Normalização
        if self.config.get('normalization', True):
            image = self.normalize_image(image)
            metadata['enhancements_applied'].append('normalization')
        
        # 5. Filtros adicionais
        if self.config.get('additional_filters', False):
            image = self.apply_additional_filters(image)
            metadata['enhancements_applied'].append('additional_filters')
        
        metadata['final_shape'] = image.shape
        metadata['final_dtype'] = str(image.dtype)
        
        return PreprocessingResult(
            processed_image=image,
            metadata=metadata,
            enhancement_applied=metadata['enhancements_applied']
        )
    
    def resize_image(self, image: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
        """Redimensiona a imagem para o tamanho alvo"""
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
    
    def apply_denoising(self, image: np.ndarray) -> np.ndarray:
        """Aplica técnicas de redução de ruído"""
        method = self.config.get('denoising_method', DenoisingMethod.BILATERAL)
        
        if method == DenoisingMethod.GAUSSIAN:
            kernel_size = self.config.get('gaussian_kernel_size', (5, 5))
            sigma = self.config.get('gaussian_sigma', 1.0)
            return cv2.GaussianBlur(image, kernel_size, sigma)
        
        elif method == DenoisingMethod.BILATERAL:
            d = self.config.get('bilateral_d', 9)
            sigma_color = self.config.get('bilateral_sigma_color', 75)
            sigma_space = self.config.get('bilateral_sigma_space', 75)
            return cv2.bilateralFilter(image, d, sigma_color, sigma_space)
        
        elif method == DenoisingMethod.MEDIAN:
            kernel_size = self.config.get('median_kernel_size', 5)
            return cv2.medianBlur(image, kernel_size)
        
        elif method == DenoisingMethod.NON_LOCAL_MEANS:
            h = self.config.get('nlm_h', 10)
            return cv2.fastNlMeansDenoisingColored(image, None, h, h, 7, 21)
        
        return image
    
    def enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Melhora o contraste da imagem"""
        method = self.config.get('contrast_method', EnhancementMethod.CLAHE)
        
        if method == EnhancementMethod.HISTOGRAM_EQUALIZATION:
            if len(image.shape) == 3:
                # Para imagens coloridas, aplicar em cada canal
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
            # Aplicar threshold adaptativo para melhorar contraste
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
    
    def normalize_image(self, image: np.ndarray) -> np.ndarray:
        """Normaliza a imagem"""
        if self.config.get('normalization_type') == 'minmax':
            # Normalização Min-Max para [0, 1]
            normalized = (image - image.min()) / (image.max() - image.min())
            return (normalized * 255).astype(np.uint8)
        
        elif self.config.get('normalization_type') == 'zscore':
            # Normalização Z-score
            mean = np.mean(image)
            std = np.std(image)
            if std > 0:
                normalized = (image - mean) / std
                # Converter para [0, 255]
                normalized = ((normalized - normalized.min()) / 
                           (normalized.max() - normalized.min()) * 255)
                return normalized.astype(np.uint8)
        
        # Normalização padrão para [0, 255]
        if image.dtype != np.uint8:
            if image.max() <= 1.0:
                return (image * 255).astype(np.uint8)
            elif image.max() <= 255:
                return image.astype(np.uint8)
        
        return image
    
    def apply_additional_filters(self, image: np.ndarray) -> np.ndarray:
        """Aplica filtros adicionais para melhorar a qualidade"""
        # Filtro de sharpening
        if self.config.get('sharpen_enabled', False):
            kernel = np.array([[-1, -1, -1],
                             [-1,  9, -1],
                             [-1, -1, -1]])
            image = cv2.filter2D(image, -1, kernel)
        
        # Filtro de embossing
        if self.config.get('emboss_enabled', False):
            kernel = np.array([[-2, -1, 0],
                             [-1,  1, 1],
                             [ 0,  1, 2]])
            image = cv2.filter2D(image, -1, kernel)
        
        # Correção de gamma
        if self.config.get('gamma_correction', False):
            gamma = self.config.get('gamma_value', 1.2)
            inv_gamma = 1.0 / gamma
            table = np.array([((i / 255.0) ** inv_gamma) * 255
                            for i in np.arange(0, 256)]).astype("uint8")
            image = cv2.LUT(image, table)
        
        return image
    
    def detect_and_enhance_text_regions(self, image: np.ndarray) -> np.ndarray:
        """Detecta e melhora regiões de texto"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Detectar bordas
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filtrar contornos por área e proporção
        enhanced_image = image.copy()
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Área mínima
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                
                # Regiões de texto típicas têm proporção > 2
                if aspect_ratio > 2 and w > 50 and h > 10:
                    # Aplicar melhoria local
                    roi = enhanced_image[y:y+h, x:x+w]
                    if len(roi.shape) == 3:
                        roi_gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
                    else:
                        roi_gray = roi
                    
                    # Aplicar CLAHE local
                    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(4, 4))
                    enhanced_roi = clahe.apply(roi_gray)
                    
                    if len(enhanced_image.shape) == 3:
                        enhanced_image[y:y+h, x:x+w] = cv2.cvtColor(enhanced_roi, cv2.COLOR_GRAY2RGB)
                    else:
                        enhanced_image[y:y+h, x:x+w] = enhanced_roi
        
        return enhanced_image
    
    def get_preprocessing_summary(self) -> Dict[str, Any]:
        """Retorna resumo das configurações de pré-processamento"""
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