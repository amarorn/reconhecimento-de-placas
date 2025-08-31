__version__ = "2.0.0"
__author__ = "Equipe de Desenvolvimento"
__description__ = "Arquitetura refatorada de visão computacional para reconhecimento de placas"

from .core.vision_pipeline import VisionPipeline, PipelineResult
from .core.base_processor import BaseVisionProcessor, ProcessingResult

from .preprocessing.image_preprocessor import ImagePreprocessor
from .detection.yolo_detector import YOLODetector
from .detection.vehicle_plate_detector import VehiclePlateDetector, VehiclePlateDetection
from .detection.signal_plate_detector import SignalPlateDetector, SignalPlateDetection
from .detection.pothole_detector import PotholeDetector, PotholeDetection
from .detection.specialized_detector import SpecializedDetector, UnifiedDetectionResult
from .ocr.text_extractor import TextExtractor

try:
    from config.vision_architecture import (
        VisionArchitectureConfig,
        ModelConfig,
        OCRConfig,
        PreprocessingConfig,
        SpecializedDetectorConfig,
        PipelineConfig,
        ConfigPresets
    )
except ImportError:
    VisionArchitectureConfig = None
    ModelConfig = None
    OCRConfig = None
    PreprocessingConfig = None
    SpecializedDetectorConfig = None
    PipelineConfig = None
    ConfigPresets = None

__all__ = [
    'VisionPipeline',
    'PipelineResult',
    'BaseVisionProcessor',
    'ProcessingResult',
    
    'ImagePreprocessor',
    'YOLODetector',
    'VehiclePlateDetector',
    'VehiclePlateDetection',
    'SignalPlateDetector',
    'SignalPlateDetection',
    'PotholeDetector',
    'PotholeDetection',
    'SpecializedDetector',
    'UnifiedDetectionResult',
    'TextExtractor',
    
    'VisionArchitectureConfig',
    'ModelConfig',
    'OCRConfig',
    'PreprocessingConfig',
    'SpecializedDetectorConfig',
    'PipelineConfig',
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
        'core': ['VisionPipeline', 'BaseVisionProcessor', 'PipelineResult'],
        'preprocessing': ['ImagePreprocessor'],
        'detection': [
            'YOLODetector',
            'VehiclePlateDetector',
            'SignalPlateDetector', 
            'PotholeDetector',
            'SpecializedDetector'
        ],
        'ocr': ['TextExtractor']
    }

def create_pipeline(config=None):
    if config is None:
        from config.vision_architecture import ConfigPresets
        config = ConfigPresets.development().__dict__
    
    return VisionPipeline(config)

def create_specialized_detector(config=None):
    if config is None:
        from config.vision_architecture import create_specialized_config
        config = create_specialized_config()
    
    return SpecializedDetector(config)