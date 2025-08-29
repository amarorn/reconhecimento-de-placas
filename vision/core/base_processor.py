#!/usr/bin/env python3
"""
Classe Base para Processadores de Visão Computacional
====================================================

Esta classe define a interface comum para todos os processadores
de visão computacional no sistema refatorado.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import cv2
import logging
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ProcessingResult:
    """Resultado do processamento de uma imagem"""
    success: bool
    image_path: str
    processing_time: float
    detections: List[Dict[str, Any]]
    ocr_results: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class BaseVisionProcessor(ABC):
    """Classe base para processadores de visão computacional"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.setup_logging()
        self.initialize()
    
    def setup_logging(self):
        """Configura o sistema de logging"""
        log_level = getattr(logging, self.config.get('log_level', 'INFO'))
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    @abstractmethod
    def initialize(self):
        """Inicializa o processador"""
        pass
    
    @abstractmethod
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Pré-processa a imagem"""
        pass
    
    @abstractmethod
    def detect_objects(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detecta objetos na imagem"""
        pass
    
    @abstractmethod
    def extract_text(self, image: np.ndarray, regions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extrai texto das regiões detectadas"""
        pass
    
    @abstractmethod
    def postprocess_results(self, detections: List[Dict[str, Any]], 
                          ocr_results: List[Dict[str, Any]]) -> ProcessingResult:
        """Pós-processa os resultados"""
        pass
    
    def process_image(self, image_path: str) -> ProcessingResult:
        """Processa uma imagem completa"""
        start_time = datetime.now()
        
        try:
            # Carregar imagem
            image = self.load_image(image_path)
            if image is None:
                return ProcessingResult(
                    success=False,
                    image_path=image_path,
                    processing_time=0.0,
                    detections=[],
                    ocr_results=[],
                    metadata={},
                    error_message="Falha ao carregar imagem"
                )
            
            # Pipeline de processamento
            processed_image = self.preprocess_image(image)
            detections = self.detect_objects(processed_image)
            ocr_results = self.extract_text(processed_image, detections)
            result = self.postprocess_results(detections, ocr_results)
            
            # Calcular tempo de processamento
            processing_time = (datetime.now() - start_time).total_seconds()
            result.processing_time = processing_time
            result.image_path = image_path
            result.success = True
            
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Erro ao processar imagem {image_path}: {e}")
            
            return ProcessingResult(
                success=False,
                image_path=image_path,
                processing_time=processing_time,
                detections=[],
                ocr_results=[],
                metadata={},
                error_message=str(e)
            )
    
    def load_image(self, image_path: str) -> Optional[np.ndarray]:
        """Carrega uma imagem do disco"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"Não foi possível carregar a imagem: {image_path}")
                return None
            
            # Converter BGR para RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return image
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar imagem {image_path}: {e}")
            return None
    
    def save_image(self, image: np.ndarray, output_path: str) -> bool:
        """Salva uma imagem no disco"""
        try:
            # Converter RGB para BGR para OpenCV
            if len(image.shape) == 3:
                image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            else:
                image_bgr = image
            
            success = cv2.imwrite(output_path, image_bgr)
            if success:
                self.logger.info(f"Imagem salva em: {output_path}")
            else:
                self.logger.error(f"Falha ao salvar imagem em: {output_path}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar imagem {output_path}: {e}")
            return False
    
    def validate_image(self, image: np.ndarray) -> bool:
        """Valida se a imagem é adequada para processamento"""
        if image is None:
            return False
        
        if len(image.shape) < 2:
            return False
        
        height, width = image.shape[:2]
        min_size = self.config.get('validation_rules', {}).get('min_plate_size', (50, 50))
        
        if height < min_size[0] or width < min_size[1]:
            return False
        
        return True
    
    def get_metadata(self) -> Dict[str, Any]:
        """Retorna metadados do processador"""
        return {
            'processor_type': self.__class__.__name__,
            'config': self.config,
            'initialized_at': getattr(self, '_initialized_at', None)
        }
    
    def cleanup(self):
        """Limpa recursos do processador"""
        pass