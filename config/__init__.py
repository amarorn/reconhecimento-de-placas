"""
Módulo de Configuração da Arquitetura de Visão Computacional
============================================================

Este módulo contém todas as configurações e presets para a
arquitetura refatorada de visão computacional.
"""

__version__ = "2.0.0"
__author__ = "Equipe de Desenvolvimento"

# Importar configurações principais
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
    # Classes de configuração
    'VisionArchitectureConfig',
    'ModelConfig',
    'OCRConfig',
    'PreprocessingConfig',
    'PipelineConfig',
    
    # Enums
    'ModelType',
    'OCRType',
    'PreprocessingType',
    
    # Funções utilitárias
    'ConfigPresets',
    'load_config',
    
    # Versão
    '__version__',
    '__author__'
]

def get_default_config():
    """Retorna configuração padrão"""
    return ConfigPresets.development()

def get_production_config():
    """Retorna configuração para produção"""
    return ConfigPresets.production()

def get_edge_config():
    """Retorna configuração para edge computing"""
    return ConfigPresets.edge()

def list_available_configs():
    """Lista todas as configurações disponíveis"""
    return {
        'development': 'Configuração para desenvolvimento',
        'production': 'Configuração para produção',
        'edge': 'Configuração para edge computing'
    }