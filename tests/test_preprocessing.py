

import pytest
import numpy as np
import cv2
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from vision.preprocessing.image_preprocessor import (
    ImagePreprocessor, 
    EnhancementMethod, 
    DenoisingMethod,
    PreprocessingResult
)

class TestImagePreprocessor:
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        noise = np.random.normal(0, 25, img.shape).astype(np.uint8)
        img = np.clip(img + noise, 0, 255).astype(np.uint8)
        return img
    
    @pytest.fixture
    def preprocessor(self):
        assert preprocessor is not None
        assert hasattr(preprocessor, 'config')
        assert preprocessor.config['resize_enabled'] is True
    
    def test_resize_image(self, preprocessor, sample_image):
        target_size = (64, 64)
        
        methods = ['bilinear', 'bicubic', 'lanczos', 'nearest']
        for method in methods:
            preprocessor.config['resize_method'] = method
            resized = preprocessor.resize_image(sample_image, target_size)
            assert resized.shape[:2] == target_size
    
    def test_denoising_methods(self, preprocessor, sample_image):
        preprocessor.config['contrast_method'] = EnhancementMethod.CLAHE
        enhanced = preprocessor.enhance_contrast(sample_image)
        assert enhanced.shape == sample_image.shape
        
        preprocessor.config['contrast_method'] = EnhancementMethod.HISTOGRAM_EQUALIZATION
        enhanced = preprocessor.enhance_contrast(sample_image)
        assert enhanced.shape == sample_image.shape
    
    def test_normalization(self, preprocessor, sample_image):
        preprocessor.config['sharpen_enabled'] = True
        preprocessor.config['emboss_enabled'] = True
        preprocessor.config['gamma_correction'] = True
        
        filtered = preprocessor.apply_additional_filters(sample_image)
        assert filtered.shape == sample_image.shape
    
    def test_text_region_enhancement(self, preprocessor, sample_image):
        result = preprocessor.preprocess(sample_image)
        
        assert isinstance(result, PreprocessingResult)
        assert result.processed_image is not None
        assert result.metadata is not None
        assert result.enhancement_applied is not None
        
        assert 'original_shape' in result.metadata
        assert 'final_shape' in result.metadata
        assert 'enhancements_applied' in result.metadata
    
    def test_error_handling(self, preprocessor):
        summary = preprocessor.get_preprocessing_summary()
        
        assert isinstance(summary, dict)
        assert 'resize_enabled' in summary
        assert 'denoising_enabled' in summary
        assert 'contrast_enhancement' in summary
        assert 'normalization' in summary
    
    def test_edge_cases(self, preprocessor):
    
    def test_initialization(self):
