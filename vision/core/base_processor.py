

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import cv2
import logging
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ProcessingResult:
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
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.setup_logging()
        self.initialize()
    
    def setup_logging(self):
        log_level = getattr(logging, self.config.get('log_level', 'INFO'))
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    @abstractmethod
    def initialize(self):
        pass
    
    @abstractmethod
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        pass
    
    @abstractmethod
    def detect_objects(self, image: np.ndarray) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def extract_text(self, image: np.ndarray, regions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def postprocess_results(self, detections: List[Dict[str, Any]], 
                          ocr_results: List[Dict[str, Any]]) -> ProcessingResult:
        pass
    
    def process_image(self, image_path: str) -> ProcessingResult:
        start_time = datetime.now()
        
        try:
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
            
            processed_image = self.preprocess_image(image)
            detections = self.detect_objects(processed_image)
            ocr_results = self.extract_text(processed_image, detections)
            result = self.postprocess_results(detections, ocr_results)
            
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
        try:
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"Não foi possível carregar a imagem: {image_path}")
                return None
            
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return image
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar imagem {image_path}: {e}")
            return None
    
    def save_image(self, image: np.ndarray, output_path: str) -> bool:
        try:
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
        return {
            'processor_type': self.__class__.__name__,
            'config': self.config,
            'initialized_at': getattr(self, '_initialized_at', None)
        }
    
    def cleanup(self):
        pass