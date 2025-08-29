#!/usr/bin/env python3
"""
Testes Unitários para Pré-processamento de Imagens
==================================================

Testa todas as funcionalidades do ImagePreprocessor.
"""

import pytest
import numpy as np
import cv2
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from vision.preprocessing.image_preprocessor import (
    ImagePreprocessor, 
    EnhancementMethod, 
    DenoisingMethod,
    PreprocessingResult
)

class TestImagePreprocessor:
    """Testes para ImagePreprocessor"""
    
    @pytest.fixture
    def sample_image(self):
        """Cria uma imagem de teste"""
        # Criar imagem de teste com ruído
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        # Adicionar ruído
        noise = np.random.normal(0, 25, img.shape).astype(np.uint8)
        img = np.clip(img + noise, 0, 255).astype(np.uint8)
        return img
    
    @pytest.fixture
    def preprocessor(self):
        """Cria uma instância do preprocessor"""
        config = {
            'resize_enabled': True,
            'target_size': (64, 64),
            'denoising_enabled': True,
            'contrast_enhancement': True,
            'normalization': True
        }
        return ImagePreprocessor(config)
    
    def test_initialization(self, preprocessor):
        """Testa inicialização do preprocessor"""
        assert preprocessor is not None
        assert hasattr(preprocessor, 'config')
        assert preprocessor.config['resize_enabled'] is True
    
    def test_resize_image(self, preprocessor, sample_image):
        """Testa redimensionamento de imagem"""
        target_size = (64, 64)
        resized = preprocessor.resize_image(sample_image, target_size)
        
        assert resized.shape[:2] == target_size
        assert resized.dtype == sample_image.dtype
    
    def test_resize_methods(self, preprocessor, sample_image):
        """Testa diferentes métodos de redimensionamento"""
        target_size = (64, 64)
        
        # Testar diferentes métodos
        methods = ['bilinear', 'bicubic', 'lanczos', 'nearest']
        for method in methods:
            preprocessor.config['resize_method'] = method
            resized = preprocessor.resize_image(sample_image, target_size)
            assert resized.shape[:2] == target_size
    
    def test_denoising_methods(self, preprocessor, sample_image):
        """Testa diferentes métodos de redução de ruído"""
        # Testar Gaussian
        preprocessor.config['denoising_method'] = DenoisingMethod.GAUSSIAN
        denoised = preprocessor.apply_denoising(sample_image)
        assert denoised.shape == sample_image.shape
        
        # Testar Bilateral
        preprocessor.config['denoising_method'] = DenoisingMethod.BILATERAL
        denoised = preprocessor.apply_denoising(sample_image)
        assert denoised.shape == sample_image.shape
        
        # Testar Median
        preprocessor.config['denoising_method'] = DenoisingMethod.MEDIAN
        denoised = preprocessor.apply_denoising(sample_image)
        assert denoised.shape == sample_image.shape
    
    def test_contrast_enhancement(self, preprocessor, sample_image):
        """Testa melhoria de contraste"""
        # Testar CLAHE
        preprocessor.config['contrast_method'] = EnhancementMethod.CLAHE
        enhanced = preprocessor.enhance_contrast(sample_image)
        assert enhanced.shape == sample_image.shape
        
        # Testar Histogram Equalization
        preprocessor.config['contrast_method'] = EnhancementMethod.HISTOGRAM_EQUALIZATION
        enhanced = preprocessor.enhance_contrast(sample_image)
        assert enhanced.shape == sample_image.shape
    
    def test_normalization(self, preprocessor, sample_image):
        """Testa normalização de imagem"""
        # Testar normalização padrão
        normalized = preprocessor.normalize_image(sample_image)
        assert normalized.dtype == np.uint8
        
        # Testar normalização minmax
        preprocessor.config['normalization_type'] = 'minmax'
        normalized = preprocessor.normalize_image(sample_image)
        assert normalized.dtype == np.uint8
        
        # Testar normalização zscore
        preprocessor.config['normalization_type'] = 'zscore'
        normalized = preprocessor.normalize_image(sample_image)
        assert normalized.dtype == np.uint8
    
    def test_additional_filters(self, preprocessor, sample_image):
        """Testa filtros adicionais"""
        # Habilitar filtros
        preprocessor.config['sharpen_enabled'] = True
        preprocessor.config['emboss_enabled'] = True
        preprocessor.config['gamma_correction'] = True
        
        filtered = preprocessor.apply_additional_filters(sample_image)
        assert filtered.shape == sample_image.shape
    
    def test_text_region_enhancement(self, preprocessor, sample_image):
        """Testa melhoria de regiões de texto"""
        enhanced = preprocessor.detect_and_enhance_text_regions(sample_image)
        assert enhanced.shape == sample_image.shape
    
    def test_full_pipeline(self, preprocessor, sample_image):
        """Testa pipeline completo de pré-processamento"""
        result = preprocessor.preprocess(sample_image)
        
        assert isinstance(result, PreprocessingResult)
        assert result.processed_image is not None
        assert result.metadata is not None
        assert result.enhancement_applied is not None
        
        # Verificar metadados
        assert 'original_shape' in result.metadata
        assert 'final_shape' in result.metadata
        assert 'enhancements_applied' in result.metadata
    
    def test_error_handling(self, preprocessor):
        """Testa tratamento de erros"""
        # Testar com imagem None
        with pytest.raises(ValueError):
            preprocessor.preprocess(None)
    
    def test_configuration_summary(self, preprocessor):
        """Testa resumo de configuração"""
        summary = preprocessor.get_preprocessing_summary()
        
        assert isinstance(summary, dict)
        assert 'resize_enabled' in summary
        assert 'denoising_enabled' in summary
        assert 'contrast_enhancement' in summary
        assert 'normalization' in summary
    
    def test_edge_cases(self, preprocessor):
        """Testa casos extremos"""
        # Imagem muito pequena
        small_img = np.random.randint(0, 255, (10, 10, 3), dtype=np.uint8)
        result = preprocessor.preprocess(small_img)
        assert result.processed_image is not None
        
        # Imagem em escala de cinza
        gray_img = np.random.randint(0, 255, (50, 50), dtype=np.uint8)
        result = preprocessor.preprocess(gray_img)
        assert result.processed_image is not None

class TestPreprocessingResult:
    """Testes para PreprocessingResult"""
    
    def test_initialization(self):
        """Testa inicialização do resultado"""
        processed_image = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        metadata = {'test': 'data'}
        enhancements = ['denoising', 'contrast']
        
        result = PreprocessingResult(
            processed_image=processed_image,
            metadata=metadata,
            enhancement_applied=enhancements
        )
        
        assert result.processed_image is not None
        assert result.metadata == metadata
        assert result.enhancement_applied == enhancements

if __name__ == "__main__":
    pytest.main([__file__, "-v"])