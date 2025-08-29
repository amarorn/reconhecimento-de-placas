"""
Módulo de Visão Computacional Refatorado
========================================

Este módulo implementa uma arquitetura moderna e modular para
reconhecimento de placas de trânsito e veículos usando técnicas
avançadas de visão computacional.
"""

__version__ = "2.0.0"
__author__ = "Equipe de Desenvolvimento"
__description__ = "Arquitetura refatorada de visão computacional para reconhecimento de placas"

# Importar componentes principais
from .core.vision_pipeline import VisionPipeline
from .core.base_processor import BaseVisionProcessor, ProcessingResult

# Importar componentes especializados
from .preprocessing.image_preprocessor import ImagePreprocessor
from .detection.yolo_detector import YOLODetector
from .ocr.text_extractor import TextExtractor

# Configurações
from ..config.vision_architecture import (
    VisionArchitectureConfig,
    ModelConfig,
    OCRConfig,
    PreprocessingConfig,
    ConfigPresets
)

__all__ = [
    # Classes principais
    'VisionPipeline',
    'BaseVisionProcessor',
    'ProcessingResult',
    
    # Componentes especializados
    'ImagePreprocessor',
    'YOLODetector',
    'TextExtractor',
    
    # Configurações
    'VisionArchitectureConfig',
    'ModelConfig',
    'OCRConfig',
    'PreprocessingConfig',
    'ConfigPresets',
    
    # Versão
    '__version__',
    '__author__',
    '__description__'
]

# Configuração de logging padrão
import logging

# Configurar logging para o módulo
logging.getLogger(__name__).addHandler(logging.NullHandler())

def get_version():
    """Retorna a versão do módulo"""
    return __version__

def get_components():
    """Retorna lista de componentes disponíveis"""
    return {
        'core': ['VisionPipeline', 'BaseVisionProcessor'],
        'preprocessing': ['ImagePreprocessor'],
        'detection': ['YOLODetector'],
        'ocr': ['TextExtractor']
    }

def create_pipeline(config=None):
    """Cria uma instância do pipeline com configuração padrão"""
    if config is None:
        from ..config.vision_architecture import ConfigPresets
        config = ConfigPresets.development().__dict__
    
    return VisionPipeline(config)