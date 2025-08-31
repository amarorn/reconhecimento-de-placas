#!/usr/bin/env python3
"""
Configuração da Arquitetura de Visão Computacional
==================================================

Configurações para modelos, OCR e pipeline de processamento.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import os

class ModelType(str, Enum):
    """Tipos de modelos disponíveis"""
    YOLO = "yolo"
    PADDLEOCR = "paddleocr"
    EASYOCR = "easyocr"
    TESSERACT = "tesseract"

class PreprocessingType(str, Enum):
    """Tipos de pré-processamento"""
    BASIC = "basic"
    AI_ENHANCED = "ai_enhanced"
    CUSTOM = "custom"

@dataclass
class ModelConfig:
    """Configuração de modelo de detecção"""
    name: str
    type: ModelType
    weights_path: str
    confidence_threshold: float = 0.5
    nms_threshold: float = 0.4
    input_size: Tuple[int, int] = (640, 640)
    device: str = "auto"
    half_precision: bool = False

@dataclass
class OCRConfig:
    """Configuração de OCR"""
    type: ModelType
    language: str = "pt"
    confidence_threshold: float = 0.8
    use_gpu: bool = False
    use_angle_cls: bool = True

@dataclass
class PreprocessingConfig:
    """Configuração de pré-processamento"""
    type: PreprocessingType
    resize_enabled: bool = True
    target_size: Tuple[int, int] = (640, 640)
    resize_method: str = "bilinear"
    denoising_enabled: bool = True
    denoising_method: str = "bilateral"
    contrast_enhancement: bool = True
    contrast_method: str = "clahe"
    normalization: bool = True
    augmentation: bool = False

@dataclass
class PipelineConfig:
    """Configuração do pipeline"""
    detection_model: ModelConfig
    ocr_model: OCRConfig
    preprocessing: PreprocessingConfig
    enable_cache: bool = True
    cache_size: int = 1000
    enable_async: bool = True
    max_workers: int = 4
    log_level: str = "INFO"
    enable_metrics: bool = True
    enable_profiling: bool = True
    validation_rules: Optional[Dict[str, Any]] = None

@dataclass
class VisionArchitectureConfig:
    """Configuração principal da arquitetura"""
    detection_model: ModelConfig
    ocr_model: OCRConfig
    preprocessing: PreprocessingConfig
    enable_cache: bool = True
    cache_size: int = 1000
    enable_async: bool = True
    max_workers: int = 4
    log_level: str = "INFO"
    enable_metrics: bool = True
    enable_profiling: bool = True
    validation_rules: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validação pós-inicialização"""
        if not self.detection_model:
            raise ValueError("Modelo de detecção é obrigatório")
        if not self.ocr_model:
            raise ValueError("Modelo OCR é obrigatório")
    
    @staticmethod
    def development():
        """Configuração para desenvolvimento"""
        return VisionArchitectureConfig(
            detection_model=ModelConfig(
                name="yolov8n",
                type=ModelType.YOLO,
                weights_path="models/yolov8n.pt",
                confidence_threshold=0.5,
                device="cpu"
            ),
            ocr_model=OCRConfig(
                type=ModelType.PADDLEOCR,
                language="pt",
                confidence_threshold=0.7,
                use_gpu=False
            ),
            preprocessing=PreprocessingConfig(
                type=PreprocessingType.BASIC,
                resize_enabled=True,
                target_size=(640, 640),
                denoising_enabled=True,
                contrast_enhancement=True
            ),
            enable_cache=True,
            enable_async=True,
            max_workers=2,
            log_level="DEBUG"
        )
    
    @staticmethod
    def production():
        """Configuração para produção"""
        return VisionArchitectureConfig(
            detection_model=ModelConfig(
                name="yolov8n",
                type=ModelType.YOLO,
                weights_path="models/yolov8n.pt",
                confidence_threshold=0.5,
                device="cpu"
            ),
            ocr_model=OCRConfig(
                type=ModelType.EASYOCR,
                language="pt",
                confidence_threshold=0.7,
                use_gpu=False
            ),
            preprocessing=PreprocessingConfig(
                type=PreprocessingType.BASIC,
                resize_enabled=True,
                target_size=(640, 640),
                denoising_enabled=True,
                contrast_enhancement=True
            ),
            enable_cache=False,
            enable_async=False,
            max_workers=2,
            log_level="INFO"
        )
    
    @staticmethod
    def edge():
        """Configuração para dispositivos edge"""
        return VisionArchitectureConfig(
            detection_model=ModelConfig(
                name="yolov8n",
                type=ModelType.YOLO,
                weights_path="models/yolov8n.pt",
                confidence_threshold=0.3,
                device="cpu",
                input_size=(320, 320)
            ),
            ocr_model=OCRConfig(
                type=ModelType.TESSERACT,
                language="pt",
                confidence_threshold=0.6,
                use_gpu=False
            ),
            preprocessing=PreprocessingConfig(
                type=PreprocessingType.BASIC,
                resize_enabled=True,
                target_size=(320, 320),
                denoising_enabled=False,
                contrast_enhancement=False
            ),
            enable_cache=False,
            enable_async=False,
            max_workers=1,
            log_level="WARNING"
        )

class ConfigPresets:
    """Presets de configuração predefinidos"""
    
    @staticmethod
    def development():
        """Preset para desenvolvimento"""
        return VisionArchitectureConfig.development()
    
    @staticmethod
    def production():
        """Preset para produção"""
        return VisionArchitectureConfig.production()
    
    @staticmethod
    def edge():
        """Preset para dispositivos edge"""
        return VisionArchitectureConfig.edge()
    
    @staticmethod
    def custom(config_path: str = None):
        """Preset customizado"""
        if config_path and os.path.exists(config_path):
            # TODO: Implementar carregamento de arquivo de configuração
            pass
        
        return VisionArchitectureConfig.development()

# Configuração padrão
DEFAULT_CONFIG = VisionArchitectureConfig.development()

def load_config(config_path: str = None) -> VisionArchitectureConfig:
    """Carrega configuração de arquivo ou usa padrão"""
    if config_path and os.path.exists(config_path):
        # TODO: Implementar carregamento de arquivo de configuração
        pass
    
    return DEFAULT_CONFIG