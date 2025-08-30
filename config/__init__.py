
__version__ = "2.0.0"
__author__ = "Equipe de Desenvolvimento"

from .vision_architecture import (
    VisionArchitectureConfig,
    ModelConfig,
    OCRConfig,
    PreprocessingConfig,
    PipelineConfig,
    ModelType,
    OCRType,
    PreprocessingType,
    ConfigPresets,
    load_config
)

__all__ = [
    'VisionArchitectureConfig',
    'ModelConfig',
    'OCRConfig',
    'PreprocessingConfig',
    'PipelineConfig',
    
    'ModelType',
    'OCRType',
    'PreprocessingType',
    
    'ConfigPresets',
    'load_config',
    
    '__version__',
    '__author__'
]

def get_default_config():
    return ConfigPresets.production()

def get_edge_config():
    return {
        'development': 'Configuração para desenvolvimento',
        'production': 'Configuração para produção',
        'edge': 'Configuração para edge computing'
    }