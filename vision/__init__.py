__version__ = "2.0.0"
__author__ = "Equipe de Desenvolvimento"
__description__ = "Arquitetura refatorada de visão computacional para reconhecimento de placas"

from .core.vision_pipeline import VisionPipeline
from .core.base_processor import BaseVisionProcessor, ProcessingResult

from .preprocessing.image_preprocessor import ImagePreprocessor
from .detection.yolo_detector import YOLODetector
from .ocr.text_extractor import TextExtractor

try:
    from config.vision_architecture import (
        VisionArchitectureConfig,
        ModelConfig,
        OCRConfig,
        PreprocessingConfig,
        ConfigPresets
    )
except ImportError:
    VisionArchitectureConfig = None
    ModelConfig = None
    OCRConfig = None
    PreprocessingConfig = None
    ConfigPresets = None

__all__ = [
    'VisionPipeline',
    'BaseVisionProcessor',
    'ProcessingResult',
    
    'ImagePreprocessor',
    'YOLODetector',
    'TextExtractor',
    
    'VisionArchitectureConfig',
    'ModelConfig',
    'OCRConfig',
    'PreprocessingConfig',
    'ConfigPresets',
    
    '__version__',
    '__author__',
    '__description__'
]

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

def get_version():
    return __version__

def get_components():
    return {
        'core': ['VisionPipeline', 'BaseVisionProcessor'],
        'preprocessing': ['ImagePreprocessor'],
        'detection': ['YOLODetector'],
        'ocr': ['TextExtractor']
    }

def create_pipeline(config=None):
    if config is None:
        from config.vision_architecture import ConfigPresets
        config = ConfigPresets.development().__dict__
    
    return VisionPipeline(config)