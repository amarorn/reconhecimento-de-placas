"""
Detector YOLO Especializado em Placas de Sinalização
====================================================

Detector especializado para identificar e localizar placas de sinalização
de trânsito, placas de rua, placas de construção, etc.
"""

import cv2
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging
from pathlib import Path
import torch
from ultralytics import YOLO

from .base_detector import BaseDetector
from ..preprocessing.image_preprocessor import ImagePreprocessor
from ..api.models import SignalPlateType, BoundingBox, SignalPlateDetection

logger = logging.getLogger(__name__)

class SignalPlateDetector(BaseDetector):
    """Detector especializado em placas de sinalização"""
    
    # Classes específicas para placas de sinalização
    SIGNAL_CLASSES = {
        0: "stop_sign",
        1: "yield_sign", 
        2: "speed_limit",
        3: "no_parking",
        4: "one_way",
        5: "pedestrian_crossing",
        6: "school_zone",
        7: "construction",
        8: "warning",
        9: "information",
        10: "street_sign",
        11: "building_sign",
        12: "traffic_light",
        13: "railroad_crossing",
        14: "bicycle_lane",
        15: "bus_lane"
    }
    
    # Mapeamento para tipos de sinalização
    SIGNAL_TYPE_MAPPING = {
        "stop_sign": SignalPlateType.STOP,
        "yield_sign": SignalPlateType.YIELD,
        "speed_limit": SignalPlateType.SPEED_LIMIT,
        "no_parking": SignalPlateType.NO_PARKING,
        "one_way": SignalPlateType.ONE_WAY,
        "pedestrian_crossing": SignalPlateType.PEDESTRIAN_CROSSING,
        "school_zone": SignalPlateType.SCHOOL_ZONE,
        "construction": SignalPlateType.CONSTRUCTION,
        "warning": SignalPlateType.WARNING,
        "information": SignalPlateType.INFORMATION,
        "street_sign": SignalPlateType.STREET_SIGN,
        "building_sign": SignalPlateType.BUILDING_SIGN
    }
    
    def __init__(
        self,
        model_path: str = "models/signal_plates_yolo.pt",
        confidence_threshold: float = 0.5,
        iou_threshold: float = 0.45,
        device: str = "auto"
    ):
        """
        Inicializa o detector de placas de sinalização
        
        Args:
            model_path: Caminho para o modelo YOLO treinado
            confidence_threshold: Limite de confiança para detecções
            iou_threshold: Limite de IoU para NMS
            device: Dispositivo para inferência (cpu, cuda, auto)
        """
        super().__init__(model_path, confidence_threshold, iou_threshold, device)
        
        # Verificar se o modelo existe
        if not Path(model_path).exists():
            logger.warning(f"Modelo {model_path} não encontrado, usando modelo padrão")
            self.model_path = "yolov8n.pt"
        
        # Carregar modelo YOLO
        try:
            self.model = YOLO(self.model_path)
            logger.info(f"Modelo YOLO carregado: {self.model_path}")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo YOLO: {e}")
            raise
        
        # Pré-processador de imagem
        self.preprocessor = ImagePreprocessor()
        
        # Configurações específicas para placas de sinalização
        self.min_signal_size = 32  # Tamanho mínimo em pixels
        self.max_signal_size = 512  # Tamanho máximo em pixels
        self.aspect_ratio_range = (0.5, 2.0)  # Faixa de proporção aceitável
        
    def detect_signals(
        self, 
        image: np.ndarray,
        confidence_threshold: Optional[float] = None,
        iou_threshold: Optional[float] = None
    ) -> List[SignalPlateDetection]:
        """
        Detecta placas de sinalização na imagem
        
        Args:
            image: Imagem de entrada (numpy array)
            confidence_threshold: Limite de confiança personalizado
            iou_threshold: Limite de IoU personalizado
            
        Returns:
            Lista de detecções de placas de sinalização
        """
        try:
            # Usar thresholds personalizados ou padrão
            conf_thresh = confidence_threshold or self.confidence_threshold
            iou_thresh = iou_threshold or self.iou_threshold
            
            # Pré-processar imagem
            processed_image = self.preprocessor.preprocess_for_detection(image)
            
            # Executar detecção YOLO
            results = self.model(
                processed_image,
                conf=conf_thresh,
                iou=iou_thresh,
                verbose=False
            )
            
            # Processar resultados
            detections = []
            for result in results:
                if result.boxes is not None:
                    boxes = result.boxes
                    for box in boxes:
                        # Extrair informações da detecção
                        bbox = box.xyxy[0].cpu().numpy()  # [x1, y1, x2, y2]
                        confidence = float(box.conf[0].cpu().numpy())
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        # Validar tamanho e proporção
                        if self._validate_signal_detection(bbox, confidence):
                            # Converter para modelo Pydantic
                            bbox_model = BoundingBox(
                                x1=int(bbox[0]), y1=int(bbox[1]),
                                x2=int(bbox[2]), y2=int(bbox[3])
                            )
                            
                            # Mapear classe para tipo de sinalização
                            class_name = self.SIGNAL_CLASSES.get(class_id, "unknown")
                            signal_type = self.SIGNAL_TYPE_MAPPING.get(
                                class_name, SignalPlateType.INFORMATION
                            )
                            
                            # Criar detecção
                            detection = SignalPlateDetection(
                                bbox=bbox_model,
                                confidence=confidence,
                                plate_type=signal_type
                            )
                            
                            detections.append(detection)
            
            # Ordenar por confiança (maior primeiro)
            detections.sort(key=lambda x: x.confidence, reverse=True)
            
            logger.info(f"Detectadas {len(detections)} placas de sinalização")
            return detections
            
        except Exception as e:
            logger.error(f"Erro na detecção de placas de sinalização: {e}")
            return []
    
    def _validate_signal_detection(
        self, 
        bbox: np.ndarray, 
        confidence: float
    ) -> bool:
        """
        Valida se uma detecção de placa de sinalização é válida
        
        Args:
            bbox: Bounding box [x1, y1, x2, y2]
            confidence: Confiança da detecção
            
        Returns:
            True se a detecção for válida
        """
        try:
            # Calcular dimensões
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            
            # Verificar tamanho mínimo
            if width < self.min_signal_size or height < self.min_signal_size:
                return False
            
            # Verificar tamanho máximo
            if width > self.max_signal_size or height > self.max_signal_size:
                return False
            
            # Verificar proporção
            aspect_ratio = width / height
            if not (self.aspect_ratio_range[0] <= aspect_ratio <= self.aspect_ratio_range[1]):
                return False
            
            # Verificar confiança mínima
            if confidence < self.confidence_threshold:
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Erro na validação da detecção: {e}")
            return False
    
    def detect_specific_signals(
        self,
        image: np.ndarray,
        signal_types: List[SignalPlateType],
        confidence_threshold: Optional[float] = None
    ) -> List[SignalPlateDetection]:
        """
        Detecta tipos específicos de placas de sinalização
        
        Args:
            image: Imagem de entrada
            signal_types: Lista de tipos de sinalização para detectar
            confidence_threshold: Limite de confiança personalizado
            
        Returns:
            Lista de detecções filtradas por tipo
        """
        # Detectar todas as placas
        all_detections = self.detect_signals(image, confidence_threshold)
        
        # Filtrar por tipos solicitados
        filtered_detections = [
            det for det in all_detections 
            if det.plate_type in signal_types
        ]
        
        logger.info(f"Filtradas {len(filtered_detections)} detecções dos tipos solicitados")
        return filtered_detections
    
    def get_detection_statistics(self, detections: List[SignalPlateDetection]) -> Dict[str, Any]:
        """
        Obtém estatísticas das detecções
        
        Args:
            detections: Lista de detecções
            
        Returns:
            Dicionário com estatísticas
        """
        if not detections:
            return {
                "total_detections": 0,
                "average_confidence": 0.0,
                "signal_types": {},
                "bbox_sizes": []
            }
        
        # Contar tipos de sinalização
        signal_types = {}
        for det in detections:
            signal_type = det.plate_type.value
            signal_types[signal_type] = signal_types.get(signal_type, 0) + 1
        
        # Calcular confiança média
        avg_confidence = sum(det.confidence for det in detections) / len(detections)
        
        # Calcular tamanhos das bounding boxes
        bbox_sizes = []
        for det in detections:
            width = det.bbox.x2 - det.bbox.x1
            height = det.bbox.y2 - det.bbox.y1
            bbox_sizes.append({"width": width, "height": height})
        
        return {
            "total_detections": len(detections),
            "average_confidence": round(avg_confidence, 3),
            "signal_types": signal_types,
            "bbox_sizes": bbox_sizes
        }
    
    def enhance_detection_quality(
        self, 
        image: np.ndarray, 
        detections: List[SignalPlateDetection]
    ) -> List[SignalPlateDetection]:
        """
        Melhora a qualidade das detecções usando técnicas avançadas
        
        Args:
            image: Imagem de entrada
            detections: Lista de detecções iniciais
            
        Returns:
            Lista de detecções melhoradas
        """
        enhanced_detections = []
        
        for detection in detections:
            try:
                # Extrair região da placa
                x1, y1 = detection.bbox.x1, detection.bbox.y1
                x2, y2 = detection.bbox.x2, detection.bbox.y2
                
                # Garantir coordenadas válidas
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(image.shape[1], x2), min(image.shape[0], y2)
                
                if x2 > x1 and y2 > y1:
                    plate_region = image[y1:y2, x1:x2]
                    
                    # Aplicar técnicas de melhoria
                    enhanced_confidence = self._apply_enhancement_techniques(
                        plate_region, detection.confidence
                    )
                    
                    # Criar detecção melhorada
                    enhanced_detection = SignalPlateDetection(
                        bbox=detection.bbox,
                        confidence=enhanced_confidence,
                        plate_type=detection.plate_type
                    )
                    
                    enhanced_detections.append(enhanced_detection)
                    
            except Exception as e:
                logger.warning(f"Erro ao melhorar detecção: {e}")
                enhanced_detections.append(detection)
        
        return enhanced_detections
    
    def _apply_enhancement_techniques(
        self, 
        plate_region: np.ndarray, 
        base_confidence: float
    ) -> float:
        """
        Aplica técnicas de melhoria na região da placa
        
        Args:
            plate_region: Região da placa detectada
            base_confidence: Confiança base da detecção
            
        Returns:
            Confiança melhorada
        """
        try:
            enhanced_confidence = base_confidence
            
            # Verificar nitidez da imagem
            if plate_region.size > 0:
                # Calcular gradiente para estimar nitidez
                gray = cv2.cvtColor(plate_region, cv2.COLOR_BGR2GRAY)
                laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                
                # Ajustar confiança baseada na nitidez
                if laplacian_var > 100:  # Imagem nítida
                    enhanced_confidence *= 1.1
                elif laplacian_var < 50:  # Imagem borrada
                    enhanced_confidence *= 0.9
                
                # Verificar contraste
                contrast = np.std(gray)
                if contrast > 50:  # Alto contraste
                    enhanced_confidence *= 1.05
                elif contrast < 20:  # Baixo contraste
                    enhanced_confidence *= 0.95
            
            # Limitar confiança entre 0.0 e 1.0
            return max(0.0, min(1.0, enhanced_confidence))
            
        except Exception as e:
            logger.warning(f"Erro ao aplicar técnicas de melhoria: {e}")
            return base_confidence
