"""
Detector YOLO Especializado em Placas de Veículos
=================================================

Detector especializado para identificar e localizar placas de veículos
de diferentes tipos (carros, caminhões, motos, ônibus, etc.).
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
from ..api.models import VehicleType, PlateType, BoundingBox, VehiclePlateDetection, VehiclePlateInfo

logger = logging.getLogger(__name__)

class VehiclePlateDetector(BaseDetector):
    """Detector especializado em placas de veículos"""
    
    # Classes específicas para veículos e placas
    VEHICLE_CLASSES = {
        0: "car",
        1: "truck", 
        2: "motorcycle",
        3: "bus",
        4: "van",
        5: "tractor",
        6: "trailer",
        7: "ambulance",
        8: "fire_truck",
        9: "police_car",
        10: "taxi",
        11: "delivery_truck"
    }
    
    PLATE_CLASSES = {
        0: "mercosul_plate",
        1: "mercosul_motorcycle_plate",
        2: "old_standard_plate",
        3: "diplomatic_plate",
        4: "official_plate",
        5: "temporary_plate",
        6: "commercial_plate",
        7: "special_plate"
    }
    
    # Mapeamento para tipos de veículos
    VEHICLE_TYPE_MAPPING = {
        "car": VehicleType.CAR,
        "truck": VehicleType.TRUCK,
        "motorcycle": VehicleType.MOTORCYCLE,
        "bus": VehicleType.BUS,
        "van": VehicleType.VAN,
        "tractor": VehicleType.TRACTOR
    }
    
    # Mapeamento para tipos de placas
    PLATE_TYPE_MAPPING = {
        "mercosul_plate": PlateType.MERCOSUL,
        "mercosul_motorcycle_plate": PlateType.MERCOSUL_MOTORCYCLE,
        "old_standard_plate": PlateType.OLD_STANDARD,
        "diplomatic_plate": PlateType.DIPLOMATIC,
        "official_plate": PlateType.OFFICIAL,
        "temporary_plate": PlateType.TEMPORARY
    }
    
    def __init__(
        self,
        model_path: str = "models/vehicle_plates_yolo.pt",
        confidence_threshold: float = 0.5,
        iou_threshold: float = 0.45,
        device: str = "auto"
    ):
        """
        Inicializa o detector de placas de veículos
        
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
        
        # Configurações específicas para placas de veículos
        self.min_plate_size = 40  # Tamanho mínimo em pixels
        self.max_plate_size = 800  # Tamanho máximo em pixels
        self.plate_aspect_ratio_range = (2.0, 5.0)  # Proporção típica de placas
        
        # Configurações específicas para veículos
        self.min_vehicle_size = 100  # Tamanho mínimo em pixels
        self.max_vehicle_size = 2000  # Tamanho máximo em pixels
        
    def detect_vehicle_plates(
        self, 
        image: np.ndarray,
        vehicle_type: Optional[VehicleType] = None,
        confidence_threshold: Optional[float] = None,
        iou_threshold: Optional[float] = None
    ) -> List[VehiclePlateDetection]:
        """
        Detecta placas de veículos na imagem
        
        Args:
            image: Imagem de entrada (numpy array)
            vehicle_type: Tipo específico de veículo para detectar
            confidence_threshold: Limite de confiança personalizado
            iou_threshold: Limite de IoU personalizado
            
        Returns:
            Lista de detecções de placas de veículos
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
                        
                        # Determinar se é veículo ou placa
                        if class_id < len(self.VEHICLE_CLASSES):
                            # É um veículo
                            if self._validate_vehicle_detection(bbox, confidence, vehicle_type):
                                vehicle_info = self._extract_vehicle_info(class_id, bbox)
                                detections.append(vehicle_info)
                        else:
                            # É uma placa
                            if self._validate_plate_detection(bbox, confidence):
                                plate_info = self._extract_plate_info(class_id, bbox, confidence)
                                detections.append(plate_info)
            
            # Ordenar por confiança (maior primeiro)
            detections.sort(key=lambda x: x.confidence, reverse=True)
            
            # Agrupar veículos com suas placas
            grouped_detections = self._group_vehicles_with_plates(detections)
            
            logger.info(f"Detectadas {len(grouped_detections)} placas de veículos")
            return grouped_detections
            
        except Exception as e:
            logger.error(f"Erro na detecção de placas de veículos: {e}")
            return []
    
    def _validate_vehicle_detection(
        self, 
        bbox: np.ndarray, 
        confidence: float,
        target_vehicle_type: Optional[VehicleType] = None
    ) -> bool:
        """
        Valida se uma detecção de veículo é válida
        
        Args:
            bbox: Bounding box [x1, y1, x2, y2]
            confidence: Confiança da detecção
            target_vehicle_type: Tipo de veículo específico para validar
            
        Returns:
            True se a detecção for válida
        """
        try:
            # Calcular dimensões
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            
            # Verificar tamanho mínimo
            if width < self.min_vehicle_size or height < self.min_vehicle_size:
                return False
            
            # Verificar tamanho máximo
            if width > self.max_vehicle_size or height > self.max_vehicle_size:
                return False
            
            # Verificar confiança mínima
            if confidence < self.confidence_threshold:
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Erro na validação da detecção de veículo: {e}")
            return False
    
    def _validate_plate_detection(
        self, 
        bbox: np.ndarray, 
        confidence: float
    ) -> bool:
        """
        Valida se uma detecção de placa é válida
        
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
            if width < self.min_plate_size or height < self.min_plate_size:
                return False
            
            # Verificar tamanho máximo
            if width > self.max_plate_size or height > self.max_plate_size:
                return False
            
            # Verificar proporção típica de placas
            aspect_ratio = width / height
            if not (self.plate_aspect_ratio_range[0] <= aspect_ratio <= self.plate_aspect_ratio_range[1]):
                return False
            
            # Verificar confiança mínima
            if confidence < self.confidence_threshold:
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Erro na validação da detecção de placa: {e}")
            return False
    
    def _extract_vehicle_info(
        self, 
        class_id: int, 
        bbox: np.ndarray
    ) -> Dict[str, Any]:
        """
        Extrai informações do veículo detectado
        
        Args:
            class_id: ID da classe do veículo
            bbox: Bounding box do veículo
            
        Returns:
            Dicionário com informações do veículo
        """
        try:
            class_name = self.VEHICLE_CLASSES.get(class_id, "unknown")
            vehicle_type = self.VEHICLE_TYPE_MAPPING.get(class_name, VehicleType.CAR)
            
            return {
                "type": "vehicle",
                "class_id": class_id,
                "class_name": class_name,
                "vehicle_type": vehicle_type,
                "bbox": bbox,
                "confidence": 1.0  # Veículos têm confiança alta por padrão
            }
            
        except Exception as e:
            logger.warning(f"Erro ao extrair informações do veículo: {e}")
            return {
                "type": "vehicle",
                "class_id": class_id,
                "class_name": "unknown",
                "vehicle_type": VehicleType.CAR,
                "bbox": bbox,
                "confidence": 0.5
            }
    
    def _extract_plate_info(
        self, 
        class_id: int, 
        bbox: np.ndarray,
        confidence: float
    ) -> Dict[str, Any]:
        """
        Extrai informações da placa detectada
        
        Args:
            class_id: ID da classe da placa
            bbox: Bounding box da placa
            confidence: Confiança da detecção
            
        Returns:
            Dicionário com informações da placa
        """
        try:
            # Ajustar class_id para mapeamento de placas
            plate_class_id = class_id - len(self.VEHICLE_CLASSES)
            class_name = self.PLATE_CLASSES.get(plate_class_id, "unknown_plate")
            plate_type = self.PLATE_TYPE_MAPPING.get(class_name, PlateType.MERCOSUL)
            
            return {
                "type": "plate",
                "class_id": plate_class_id,
                "class_name": class_name,
                "plate_type": plate_type,
                "bbox": bbox,
                "confidence": confidence
            }
            
        except Exception as e:
            logger.warning(f"Erro ao extrair informações da placa: {e}")
            return {
                "type": "plate",
                "class_id": class_id,
                "class_name": "unknown_plate",
                "plate_type": PlateType.MERCOSUL,
                "bbox": bbox,
                "confidence": confidence
            }
    
    def _group_vehicles_with_plates(
        self, 
        detections: List[Dict[str, Any]]
    ) -> List[VehiclePlateDetection]:
        """
        Agrupa veículos com suas respectivas placas
        
        Args:
            detections: Lista de detecções de veículos e placas
            
        Returns:
            Lista de detecções agrupadas
        """
        try:
            vehicles = [d for d in detections if d["type"] == "vehicle"]
            plates = [d for d in detections if d["type"] == "plate"]
            
            grouped_detections = []
            
            for vehicle in vehicles:
                # Encontrar placa mais próxima do veículo
                closest_plate = self._find_closest_plate(vehicle, plates)
                
                if closest_plate:
                    # Criar detecção agrupada
                    bbox_model = BoundingBox(
                        x1=int(closest_plate["bbox"][0]),
                        y1=int(closest_plate["bbox"][1]),
                        x2=int(closest_plate["bbox"][2]),
                        y2=int(closest_plate["bbox"][3])
                    )
                    
                    plate_info = VehiclePlateInfo(
                        plate_type=closest_plate["plate_type"],
                        vehicle_type=vehicle["vehicle_type"],
                        country="Brasil",  # Padrão para o projeto
                        state=None  # Será determinado pelo OCR
                    )
                    
                    detection = VehiclePlateDetection(
                        bbox=bbox_model,
                        confidence=closest_plate["confidence"],
                        plate_number=None,  # Será extraído pelo OCR
                        plate_type=plate_info,
                        vehicle_type=vehicle["vehicle_type"],
                        country=plate_info.country,
                        state=plate_info.state
                    )
                    
                    grouped_detections.append(detection)
            
            return grouped_detections
            
        except Exception as e:
            logger.error(f"Erro ao agrupar veículos com placas: {e}")
            return []
    
    def _find_closest_plate(
        self, 
        vehicle: Dict[str, Any], 
        plates: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Encontra a placa mais próxima de um veículo
        
        Args:
            vehicle: Informações do veículo
            plates: Lista de placas detectadas
            
        Returns:
            Placa mais próxima ou None
        """
        try:
            if not plates:
                return None
            
            vehicle_center = self._calculate_bbox_center(vehicle["bbox"])
            closest_plate = None
            min_distance = float('inf')
            
            for plate in plates:
                plate_center = self._calculate_bbox_center(plate["bbox"])
                distance = self._calculate_distance(vehicle_center, plate_center)
                
                if distance < min_distance:
                    min_distance = distance
                    closest_plate = plate
            
            # Verificar se a distância é razoável (placa deve estar próxima ao veículo)
            if min_distance < 200:  # 200 pixels de tolerância
                return closest_plate
            
            return None
            
        except Exception as e:
            logger.warning(f"Erro ao encontrar placa mais próxima: {e}")
            return None
    
    def _calculate_bbox_center(self, bbox: np.ndarray) -> Tuple[float, float]:
        """Calcula o centro de uma bounding box"""
        center_x = (bbox[0] + bbox[2]) / 2
        center_y = (bbox[1] + bbox[3]) / 2
        return (center_x, center_y)
    
    def _calculate_distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calcula a distância euclidiana entre dois pontos"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def detect_specific_vehicle_plates(
        self,
        image: np.ndarray,
        vehicle_types: List[VehicleType],
        plate_types: Optional[List[PlateType]] = None,
        confidence_threshold: Optional[float] = None
    ) -> List[VehiclePlateDetection]:
        """
        Detecta placas de tipos específicos de veículos
        
        Args:
            image: Imagem de entrada
            vehicle_types: Lista de tipos de veículos para detectar
            plate_types: Lista de tipos de placas para detectar
            confidence_threshold: Limite de confiança personalizado
            
        Returns:
            Lista de detecções filtradas
        """
        # Detectar todas as placas
        all_detections = self.detect_vehicle_plates(image, confidence_threshold=confidence_threshold)
        
        # Filtrar por tipos de veículos
        filtered_detections = [
            det for det in all_detections 
            if det.vehicle_type in vehicle_types
        ]
        
        # Filtrar por tipos de placas se especificado
        if plate_types:
            filtered_detections = [
                det for det in filtered_detections 
                if det.plate_type.plate_type in plate_types
            ]
        
        logger.info(f"Filtradas {len(filtered_detections)} detecções dos tipos solicitados")
        return filtered_detections
    
    def get_detection_statistics(self, detections: List[VehiclePlateDetection]) -> Dict[str, Any]:
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
                "vehicle_types": {},
                "plate_types": {},
                "bbox_sizes": []
            }
        
        # Contar tipos de veículos
        vehicle_types = {}
        for det in detections:
            vehicle_type = det.vehicle_type.value
            vehicle_types[vehicle_type] = vehicle_types.get(vehicle_type, 0) + 1
        
        # Contar tipos de placas
        plate_types = {}
        for det in detections:
            plate_type = det.plate_type.plate_type.value
            plate_types[plate_type] = plate_types.get(plate_type, 0) + 1
        
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
            "vehicle_types": vehicle_types,
            "plate_types": plate_types,
            "bbox_sizes": bbox_sizes
        }
