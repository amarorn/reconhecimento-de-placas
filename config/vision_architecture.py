#!/usr/bin/env python3
"""
Configuração da Arquitetura de Visão Computacional
==================================================

Configurações para modelos, OCR e pipeline de processamento.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from enum import Enum
import json
from pathlib import Path

class ModelType(Enum):
    YOLO = "yolo"
    DETR = "detr"
    EFFICIENTDET = "efficientdet"
    CUSTOM = "custom"

class OCRType(Enum):
    PADDLEOCR = "paddleocr"
    EASYOCR = "easyocr"
    TESSERACT = "tesseract"
    TRANSFORMERS = "transformers"

class PreprocessingType(Enum):
    CLAHE = "clahe"
    BILATERAL = "bilateral"
    NON_LOCAL_MEANS = "non_local_means"
    SHARPENING = "sharpening"
    EMBOSSING = "embossing"
    GAMMA = "gamma"

@dataclass
class ModelConfig:
    type: ModelType = ModelType.YOLO
    weights_path: str = "yolov8n.pt"
    confidence_threshold: float = 0.5
    iou_threshold: float = 0.45
    device: str = "auto"
    half_precision: bool = False
    max_detections: int = 100

@dataclass
class OCRConfig:
    type: OCRType = OCRType.PADDLEOCR
    language: str = "pt"
    confidence_threshold: float = 0.5
    max_text_length: int = 100
    enable_fallback: bool = True
    fallback_order: List[OCRType] = field(default_factory=lambda: [
        OCRType.PADDLEOCR, OCRType.EASYOCR, OCRType.TESSERACT
    ])

@dataclass
class PreprocessingConfig:
    enabled: bool = True
    methods: List[PreprocessingType] = field(default_factory=lambda: [
        PreprocessingType.CLAHE, PreprocessingType.BILATERAL
    ])
    target_size: tuple = (640, 640)
    normalize: bool = True
    enhance_contrast: bool = True
    reduce_noise: bool = True

@dataclass
class SpecializedDetectorConfig:
    enabled: bool = True
    enabled_detectors: List[str] = field(default_factory=lambda: [
        'vehicle', 'signal', 'pothole'
    ])
    
    vehicle_detector: Dict[str, Any] = field(default_factory=lambda: {
        'model_path': 'models/vehicle_plates_yolo.pt',
        'confidence_threshold': 0.5,
        'iou_threshold': 0.45,
        'device': 'auto'
    })
    
    signal_detector: Dict[str, Any] = field(default_factory=lambda: {
        'model_path': 'models/signal_plates_yolo.pt',
        'confidence_threshold': 0.5,
        'iou_threshold': 0.45,
        'device': 'auto'
    })
    
    pothole_detector: Dict[str, Any] = field(default_factory=lambda: {
        'model_path': 'models/pothole_yolo.pt',
        'confidence_threshold': 0.5,
        'iou_threshold': 0.45,
        'device': 'auto',
        'analysis': {
            'enable_depth_estimation': True,
            'enable_area_calculation': True,
            'enable_risk_scoring': True
        }
    })

@dataclass
class PipelineConfig:
    enable_preprocessing: bool = True
    enable_detection: bool = True
    enable_specialized_detection: bool = True
    enable_ocr: bool = True
    enable_integration: bool = True
    batch_size: int = 8
    cache_results: bool = True
    max_cache_size: int = 1000

@dataclass
class VisionArchitectureConfig:
    model: ModelConfig = field(default_factory=ModelConfig)
    ocr: OCRConfig = field(default_factory=OCRConfig)
    preprocessing: PreprocessingConfig = field(default_factory=PreprocessingConfig)
    specialized_detector: SpecializedDetectorConfig = field(default_factory=SpecializedDetectorConfig)
    pipeline: PipelineConfig = field(default_factory=PipelineConfig)
    
    # Configurações globais
    log_level: str = "INFO"
    enable_monitoring: bool = True
    enable_metrics: bool = True
    enable_alerts: bool = True
    
    # Configurações de performance
    max_processing_time: float = 30.0
    enable_async: bool = False
    enable_multiprocessing: bool = False
    max_workers: int = 4
    
    # Configurações de validação
    validation_rules: Dict[str, Any] = field(default_factory=lambda: {
        'min_plate_size': (50, 50),
        'max_plate_size': (300, 100),
        'min_confidence': 0.3,
        'max_processing_time': 60.0
    })

class ConfigPresets:
    
    @staticmethod
    def development() -> VisionArchitectureConfig:
        return VisionArchitectureConfig(
            model=ModelConfig(
                weights_path="yolov8n.pt",
                confidence_threshold=0.3,
                device="cpu"
            ),
            ocr=OCRConfig(
                type=OCRType.PADDLEOCR,
                confidence_threshold=0.3
            ),
            preprocessing=PreprocessingConfig(
                enabled=True,
                target_size=(640, 640)
            ),
            specialized_detector=SpecializedDetectorConfig(
                enabled=True,
                vehicle_detector={'confidence_threshold': 0.3},
                signal_detector={'confidence_threshold': 0.3},
                pothole_detector={'confidence_threshold': 0.3}
            ),
            pipeline=PipelineConfig(
                batch_size=4,
                cache_results=True
            ),
            log_level="DEBUG",
            enable_monitoring=True
        )
    
    @staticmethod
    def production() -> VisionArchitectureConfig:
        return VisionArchitectureConfig(
            model=ModelConfig(
                weights_path="yolov8l.pt",
                confidence_threshold=0.6,
                device="auto",
                half_precision=True
            ),
            ocr=OCRConfig(
                type=OCRType.PADDLEOCR,
                confidence_threshold=0.6,
                enable_fallback=True
            ),
            preprocessing=PreprocessingConfig(
                enabled=True,
                target_size=(1024, 1024)
            ),
            specialized_detector=SpecializedDetectorConfig(
                enabled=True,
                vehicle_detector={'confidence_threshold': 0.6},
                signal_detector={'confidence_threshold': 0.6},
                pothole_detector={'confidence_threshold': 0.6}
            ),
            pipeline=PipelineConfig(
                batch_size=16,
                cache_results=True,
                max_cache_size=5000
            ),
            log_level="INFO",
            enable_monitoring=True,
            enable_async=True,
            enable_multiprocessing=True,
            max_workers=8
        )
    
    @staticmethod
    def edge() -> VisionArchitectureConfig:
        return VisionArchitectureConfig(
            model=ModelConfig(
                weights_path="yolov8n.pt",
                confidence_threshold=0.4,
                device="cpu",
                max_detections=50
            ),
            ocr=OCRConfig(
                type=OCRType.TESSERACT,
                confidence_threshold=0.4,
                enable_fallback=False
            ),
            preprocessing=PreprocessingConfig(
                enabled=True,
                target_size=(416, 416),
                methods=[PreprocessingType.CLAHE]
            ),
            specialized_detector=SpecializedDetectorConfig(
                enabled=True,
                enabled_detectors=['vehicle', 'signal'],
                vehicle_detector={'confidence_threshold': 0.4},
                signal_detector={'confidence_threshold': 0.4}
            ),
            pipeline=PipelineConfig(
                batch_size=1,
                cache_results=False
            ),
            log_level="WARNING",
            enable_monitoring=False,
            max_processing_time=10.0
        )

def load_config(config_path: Union[str, Path]) -> VisionArchitectureConfig:
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    
    return VisionArchitectureConfig(**config_data)

def save_config(config: VisionArchitectureConfig, config_path: Union[str, Path]):
    config_path = Path(config_path)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config.__dict__, f, indent=2, default=str)

def create_specialized_config() -> Dict[str, Any]:
    return {
        'enabled_detectors': ['vehicle', 'signal', 'pothole'],
        'vehicle_detector': {
            'model_path': 'models/vehicle_plates_yolo.pt',
            'confidence_threshold': 0.5,
            'iou_threshold': 0.45,
            'device': 'auto'
        },
        'signal_detector': {
            'model_path': 'models/signal_plates_yolo.pt',
            'confidence_threshold': 0.5,
            'iou_threshold': 0.45,
            'device': 'auto'
        },
        'pothole_detector': {
            'model_path': 'models/pothole_yolo.pt',
            'confidence_threshold': 0.5,
            'iou_threshold': 0.45,
            'device': 'auto',
            'analysis': {
                'enable_depth_estimation': True,
                'enable_area_calculation': True,
                'enable_risk_scoring': True
            }
        }
    }