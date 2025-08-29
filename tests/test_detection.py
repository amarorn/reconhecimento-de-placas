#!/usr/bin/env python3
"""
Testes Unitários para Detector YOLO
===================================

Testa todas as funcionalidades do YOLODetector.
"""

import pytest
import numpy as np
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from vision.detection.yolo_detector import (
    YOLODetector, 
    DetectionResult, 
    DetectionBatchResult
)

class TestYOLODetector:
    """Testes para YOLODetector"""
    
    @pytest.fixture
    def sample_image(self):
        """Cria uma imagem de teste"""
        return np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
    
    @pytest.fixture
    def mock_config(self):
        """Cria configuração mock para testes"""
        return {
            'weights_path': 'yolov8n.pt',
            'confidence_threshold': 0.5,
            'nms_threshold': 0.4,
            'input_size': (640, 640),
            'device': 'cpu'
        }
    
    @pytest.fixture
    def mock_detection_result(self):
        """Cria resultado mock de detecção"""
        mock_result = Mock()
        mock_result.boxes = Mock()
        mock_result.boxes.xyxy = Mock()
        mock_result.boxes.conf = Mock()
        mock_result.boxes.cls = Mock()
        
        # Simular detecções
        mock_result.boxes.xyxy.return_value = np.array([[100, 100, 200, 200], [300, 300, 400, 400]])
        mock_result.boxes.conf.return_value = np.array([0.8, 0.7])
        mock_result.boxes.cls.return_value = np.array([0, 1])
        
        return mock_result
    
    @patch('vision.detection.yolo_detector.YOLO')
    def test_initialization(self, mock_yolo, mock_config):
        """Testa inicialização do detector"""
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        mock_model.names = {'0': 'traffic_sign', '1': 'vehicle'}
        
        detector = YOLODetector(mock_config)
        
        assert detector is not None
        assert detector.config == mock_config
        assert detector.confidence_threshold == 0.5
        assert detector.nms_threshold == 0.4
    
    @patch('vision.detection.yolo_detector.YOLO')
    def test_device_detection(self, mock_yolo, mock_config):
        """Testa detecção automática de dispositivo"""
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        mock_model.names = {'0': 'traffic_sign'}
        
        # Testar CPU
        with patch('torch.cuda.is_available', return_value=False):
            with patch('torch.backends.mps.is_available', return_value=False):
                detector = YOLODetector(mock_config)
                assert detector.device == 'cpu'
        
        # Testar CUDA
        with patch('torch.cuda.is_available', return_value=True):
            detector = YOLODetector(mock_config)
            assert detector.device == 'cuda'
    
    @patch('vision.detection.yolo_detector.YOLO')
    def test_detect(self, mock_yolo, mock_config, sample_image, mock_detection_result):
        """Testa detecção de objetos"""
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        mock_model.names = {'0': 'traffic_sign', '1': 'vehicle'}
        
        detector = YOLODetector(mock_config)
        detector.model = mock_model
        
        # Mock da inferência
        mock_model.return_value = [mock_detection_result]
        
        result = detector.detect(sample_image)
        
        assert isinstance(result, DetectionBatchResult)
        assert len(result.detections) == 2
        assert result.image_shape == sample_image.shape
    
    @patch('vision.detection.yolo_detector.YOLO')
    def test_detect_traffic_signs(self, mock_yolo, mock_config, sample_image):
        """Testa detecção específica de placas de trânsito"""
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        mock_model.names = {'0': 'traffic_sign', '1': 'vehicle'}
        
        detector = YOLODetector(mock_config)
        detector.model = mock_model
        
        # Mock da detecção
        mock_result = Mock()
        mock_result.boxes = Mock()
        mock_result.boxes.xyxy = Mock()
        mock_result.boxes.conf = Mock()
        mock_result.boxes.cls = Mock()
        
        # Simular detecção de placa de trânsito
        mock_result.boxes.xyxy.return_value = np.array([[100, 100, 200, 200]])
        mock_result.boxes.conf.return_value = np.array([0.8])
        mock_result.boxes.cls.return_value = np.array([0])
        
        mock_model.return_value = [mock_result]
        
        traffic_signs = detector.detect_traffic_signs(sample_image)
        assert len(traffic_signs) == 1
        assert traffic_signs[0].class_name == 'traffic_sign'
    
    @patch('vision.detection.yolo_detector.YOLO')
    def test_detect_vehicle_plates(self, mock_yolo, mock_config, sample_image):
        """Testa detecção específica de placas de veículos"""
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        mock_model.names = {'0': 'vehicle_plate', '1': 'vehicle'}
        
        detector = YOLODetector(mock_config)
        detector.model = mock_model
        
        # Mock da detecção
        mock_result = Mock()
        mock_result.boxes = Mock()
        mock_result.boxes.xyxy = Mock()
        mock_result.boxes.conf = Mock()
        mock_result.boxes.cls = Mock()
        
        # Simular detecção de placa de veículo
        mock_result.boxes.xyxy.return_value = np.array([[100, 100, 200, 200]])
        mock_result.boxes.conf.return_value = np.array([0.8])
        mock_result.boxes.cls.return_value = np.array([0])
        
        mock_model.return_value = [mock_result]
        
        vehicle_plates = detector.detect_vehicle_plates(sample_image)
        assert len(vehicle_plates) == 1
        assert vehicle_plates[0].class_name == 'vehicle_plate'
    
    @patch('vision.detection.yolo_detector.YOLO')
    def test_filter_detections(self, mock_yolo, mock_config):
        """Testa filtros de detecção"""
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        mock_model.names = {'0': 'traffic_sign'}
        
        detector = YOLODetector(mock_config)
        
        # Criar detecções de teste
        detections = [
            DetectionResult(
                bbox=(100, 100, 50, 50),
                confidence=0.8,
                class_id=0,
                class_name='traffic_sign',
                area=2500,
                center=(125, 125)
            ),
            DetectionResult(
                bbox=(200, 200, 100, 100),
                confidence=0.9,
                class_id=0,
                class_name='traffic_sign',
                area=10000,
                center=(250, 250)
            )
        ]
        
        # Filtrar por tamanho
        filtered_size = detector.filter_detections_by_size(detections, min_area=5000)
        assert len(filtered_size) == 1
        assert filtered_size[0].area == 10000
        
        # Filtrar por confiança
        filtered_conf = detector.filter_detections_by_confidence(detections, min_confidence=0.85)
        assert len(filtered_conf) == 1
        assert filtered_conf[0].confidence == 0.9
    
    @patch('vision.detection.yolo_detector.YOLO')
    def test_detection_statistics(self, mock_yolo, mock_config):
        """Testa estatísticas de detecção"""
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        mock_model.names = {'0': 'traffic_sign'}
        
        detector = YOLODetector(mock_config)
        
        # Criar detecções de teste
        detections = [
            DetectionResult(
                bbox=(100, 100, 50, 50),
                confidence=0.8,
                class_id=0,
                class_name='traffic_sign',
                area=2500,
                center=(125, 125)
            ),
            DetectionResult(
                bbox=(200, 200, 100, 100),
                confidence=0.9,
                class_id=0,
                class_name='traffic_sign',
                area=10000,
                center=(250, 250)
            )
        ]
        
        stats = detector.get_detection_statistics(detections)
        
        assert stats['total_detections'] == 2
        assert stats['average_confidence'] == 0.85
        assert stats['min_confidence'] == 0.8
        assert stats['max_confidence'] == 0.9
        assert 'traffic_sign' in stats['class_distribution']
        assert stats['class_distribution']['traffic_sign'] == 2
    
    @patch('vision.detection.yolo_detector.YOLO')
    def test_draw_detections(self, mock_yolo, mock_config, sample_image):
        """Testa desenho de detecções na imagem"""
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        mock_model.names = {'0': 'traffic_sign'}
        
        detector = YOLODetector(mock_config)
        
        # Criar detecções de teste
        detections = [
            DetectionResult(
                bbox=(100, 100, 50, 50),
                confidence=0.8,
                class_id=0,
                class_name='traffic_sign',
                area=2500,
                center=(125, 125)
            )
        ]
        
        # Desenhar detecções
        output_image = detector.draw_detections(sample_image, detections)
        
        assert output_image.shape == sample_image.shape
        assert not np.array_equal(output_image, sample_image)  # Deve ter mudanças
    
    @patch('vision.detection.yolo_detector.YOLO')
    def test_error_handling(self, mock_yolo, mock_config, sample_image):
        """Testa tratamento de erros"""
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        mock_model.names = {'0': 'traffic_sign'}
        
        detector = YOLODetector(mock_config)
        
        # Testar com modelo não inicializado
        detector.model = None
        with pytest.raises(RuntimeError):
            detector.detect(sample_image)
    
    @patch('vision.detection.yolo_detector.YOLO')
    def test_cleanup(self, mock_yolo, mock_config):
        """Testa limpeza de recursos"""
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        mock_model.names = {'0': 'traffic_sign'}
        
        detector = YOLODetector(mock_config)
        
        # Testar cleanup
        detector.cleanup()
        assert detector.model is None

class TestDetectionResult:
    """Testes para DetectionResult"""
    
    def test_initialization(self):
        """Testa inicialização do resultado de detecção"""
        result = DetectionResult(
            bbox=(100, 100, 50, 50),
            confidence=0.8,
            class_id=0,
            class_name='traffic_sign',
            area=2500,
            center=(125, 125)
        )
        
        assert result.bbox == (100, 100, 50, 50)
        assert result.confidence == 0.8
        assert result.class_id == 0
        assert result.class_name == 'traffic_sign'
        assert result.area == 2500
        assert result.center == (125, 125)

class TestDetectionBatchResult:
    """Testes para DetectionBatchResult"""
    
    def test_initialization(self):
        """Testa inicialização do resultado em lote"""
        detections = []
        result = DetectionBatchResult(
            detections=detections,
            processing_time=1.5,
            image_shape=(640, 640, 3),
            metadata={'test': 'data'}
        )
        
        assert result.detections == detections
        assert result.processing_time == 1.5
        assert result.image_shape == (640, 640, 3)
        assert result.metadata == {'test': 'data'}

if __name__ == "__main__":
    pytest.main([__file__, "-v"])