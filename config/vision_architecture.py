#!/usr/bin/env python3
"""
Configuração da Arquitetura de Visão Computacional Refatorada
============================================================

Esta configuração define a nova arquitetura modular e escalável para
o sistema de reconhecimento de placas de trânsito e veículos.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import os

class ModelType(Enum):
    """Tipos de modelos suportados"""
    YOLO = "yolo"
    DETR = "detr"
    EFFICIENTDET = "efficientdet"
    RETINANET = "retinanet"

class OCRType(Enum):
    """Tipos de OCR suportados"""
    PADDLEOCR = "paddleocr"
    EASYOCR = "easyocr"
    TESSERACT = "tesseract"
    TRANSFORMER_OCR = "transformer_ocr"

class PreprocessingType(Enum):
    """Tipos de pré-processamento"""
    BASIC = "basic"
    ADVANCED = "advanced"
    ADAPTIVE = "adaptive"
    AI_ENHANCED = "ai_enhanced"

@dataclass
class ModelConfig:
    """Configuração de modelo"""
    name: str
    type: ModelType
    weights_path: str
    confidence_threshold: float = 0.5
    nms_threshold: float = 0.4
    input_size: Tuple[int, int] = (640, 640)
    device: str = "auto"  # auto, cpu, cuda, mps
    half_precision: bool = False

@dataclass
class OCRConfig:
    """Configuração de OCR"""
    type: OCRType
    language: str = "pt"
    confidence_threshold: float = 0.7
    use_gpu: bool = True
    custom_vocabulary: Optional[List[str]] = None

@dataclass
class PreprocessingConfig:
    """Configuração de pré-processamento"""
    type: PreprocessingType
    resize_method: str = "bilinear"
    normalization: bool = True
    augmentation: bool = False
    denoising: bool = True
    contrast_enhancement: bool = True

@dataclass
class PipelineConfig:
    """Configuração do pipeline de processamento"""
    enable_preprocessing: bool = True
    enable_detection: bool = True
    enable_ocr: bool = True
    enable_postprocessing: bool = True
    enable_validation: bool = True
    max_processing_time: float = 30.0  # segundos

@dataclass
class VisionArchitectureConfig:
    """Configuração principal da arquitetura"""
    
    # Modelos
    detection_model: ModelConfig = ModelConfig(
        name="yolov8x",
        type=ModelType.YOLO,
        weights_path="models/yolov8x.pt",
        confidence_threshold=0.6,
        input_size=(640, 640)
    )
    
    ocr_model: OCRConfig = OCRConfig(
        type=OCRType.PADDLEOCR,
        language="pt",
        confidence_threshold=0.8
    )
    
    # Pipeline
    pipeline: PipelineConfig = PipelineConfig()
    
    # Pré-processamento
    preprocessing: PreprocessingConfig = PreprocessingConfig(
        type=PreprocessingType.AI_ENHANCED,
        denoising=True,
        contrast_enhancement=True
    )
    
    # Cache e otimização
    enable_cache: bool = True
    cache_size: int = 1000
    enable_async: bool = True
    max_workers: int = 4
    
    # Logging e monitoramento
    log_level: str = "INFO"
    enable_metrics: bool = True
    enable_profiling: bool = True
    
    # Validação
    validation_rules: Dict[str, Any] = None
    
    def __post_init__(self):
        """Validação pós-inicialização"""
        if self.validation_rules is None:
            self.validation_rules = {
                "min_plate_size": (50, 50),
                "max_plate_size": (800, 400),
                "min_text_length": 3,
                "max_text_length": 20,
                "allowed_characters": "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-"
            }

# Configurações específicas para diferentes cenários
class ConfigPresets:
    """Presets de configuração para diferentes cenários"""
    
    @staticmethod
    def production():
        """Configuração para produção"""
        return VisionArchitectureConfig(
            detection_model=ModelConfig(
                name="yolov8x",
                type=ModelType.YOLO,
                weights_path="models/yolov8x.pt",
                confidence_threshold=0.7,
                device="cuda"
            ),
            ocr_model=OCRConfig(
                type=OCRType.PADDLEOCR,
                confidence_threshold=0.85,
                use_gpu=True
            ),
            enable_cache=True,
            enable_async=True,
            max_workers=8,
            log_level="WARNING"
        )
    
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
                type=OCRType.EASYOCR,
                confidence_threshold=0.7,
                use_gpu=False
            ),
            enable_cache=False,
            enable_async=False,
            max_workers=2,
            log_level="DEBUG"
        )
    
    @staticmethod
    def edge():
        """Configuração para edge computing"""
        return VisionArchitectureConfig(
            detection_model=ModelConfig(
                name="yolov8n",
                type=ModelType.YOLO,
                weights_path="models/yolov8n.pt",
                confidence_threshold=0.6,
                device="cpu",
                half_precision=True
            ),
            ocr_model=OCRConfig(
                type=OCRType.TESSERACT,
                confidence_threshold=0.6,
                use_gpu=False
            ),
            enable_cache=True,
            enable_async=False,
            max_workers=1,
            log_level="ERROR"
        )

# Configuração padrão
DEFAULT_CONFIG = ConfigPresets.development()

def load_config(config_path: str = None) -> VisionArchitectureConfig:
    """Carrega configuração do arquivo ou usa padrão"""
    if config_path and os.path.exists(config_path):
        # TODO: Implementar carregamento de arquivo de configuração
        pass
    
    return DEFAULT_CONFIG