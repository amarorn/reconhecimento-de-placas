#!/usr/bin/env python3
"""
Testes Unitários para Pipeline Principal de Visão Computacional
===============================================================

Testa todas as funcionalidades do VisionPipeline.
"""

import pytest
import numpy as np
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from vision.core.vision_pipeline import (
    VisionPipeline, 
    PipelineResult,
    ProcessingResult
)
from vision.preprocessing.image_preprocessor import ImagePreprocessor
from vision.detection.yolo_detector import YOLODetector
from vision.ocr.text_extractor import TextExtractor

class TestVisionPipeline:
    """Testes para VisionPipeline"""
    
    @pytest.fixture
    def sample_image(self):
        """Cria uma imagem de teste"""
        return np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
    
    @pytest.fixture
    def mock_config(self):
        """Cria configuração mock para testes"""
        return {
            'preprocessing': {
                'resize_enabled': True,
                'target_size': (64, 64),
                'denoising_enabled': True,
                'contrast_enhancement': True,
                'normalization': True
            },
            'detection': {
                'weights_path': 'yolov8n.pt',
                'confidence_threshold': 0.5,
                'nms_threshold': 0.4,
                'input_size': (64, 64),
                'device': 'cpu'
            },
            'ocr': {
                'type': 'paddleocr',
                'language': 'pt',
                'confidence_threshold': 0.7,
                'use_gpu': False
            },
            'validation_rules': {
                'min_plate_size': (50, 50),
                'max_plate_size': (800, 400),
                'min_text_length': 3,
                'max_text_length': 20,
                'min_confidence': 0.3
            },
            'log_level': 'INFO'
        }
    
    @pytest.fixture
    def temp_image_file(self, sample_image):
        """Cria um arquivo de imagem temporário"""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            # Simular salvamento de imagem
            f.write(b'fake_image_data')
            temp_path = f.name
        
        yield temp_path
        
        # Limpar arquivo temporário
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @patch('vision.preprocessing.image_preprocessor.ImagePreprocessor')
    @patch('vision.detection.yolo_detector.YOLODetector')
    @patch('vision.ocr.text_extractor.TextExtractor')
    def test_initialization(self, mock_ocr, mock_detector, mock_preprocessor, mock_config):
        """Testa inicialização do pipeline"""
        # Mock dos componentes
        mock_preprocessor_instance = Mock()
        mock_preprocessor.return_value = mock_preprocessor_instance
        
        mock_detector_instance = Mock()
        mock_detector.return_value = mock_detector_instance
        
        mock_ocr_instance = Mock()
        mock_ocr.return_value = mock_ocr_instance
        
        pipeline = VisionPipeline(mock_config)
        
        assert pipeline is not None
        assert pipeline.config == mock_config
        assert pipeline.preprocessor is not None
        assert pipeline.detector is not None
        assert pipeline.text_extractor is not None
        assert hasattr(pipeline, '_initialized_at')
    
    @patch('vision.preprocessing.image_preprocessor.ImagePreprocessor')
    @patch('vision.detection.yolo_detector.YOLODetector')
    @patch('vision.ocr.text_extractor.TextExtractor')
    def test_preprocess_image(self, mock_ocr, mock_detector, mock_preprocessor, mock_config, sample_image):
        """Testa pré-processamento de imagem"""
        # Mock do pré-processador
        mock_preprocessor_instance = Mock()
        mock_preprocessor.return_value = mock_preprocessor_instance
        
        mock_result = Mock()
        mock_result.processed_image = sample_image
        mock_preprocessor_instance.preprocess.return_value = mock_result
        
        mock_detector.return_value = Mock()
        mock_ocr.return_value = Mock()
        
        pipeline = VisionPipeline(mock_config)
        
        result = pipeline.preprocess_image(sample_image)
        
        assert result is not None
        mock_preprocessor_instance.preprocess.assert_called_once_with(sample_image)
    
    @patch('vision.preprocessing.image_preprocessor.ImagePreprocessor')
    @patch('vision.detection.yolo_detector.YOLODetector')
    @patch('vision.ocr.text_extractor.TextExtractor')
    def test_detect_objects(self, mock_ocr, mock_detector, mock_preprocessor, mock_config, sample_image):
        """Testa detecção de objetos"""
        # Mock do detector
        mock_detector_instance = Mock()
        mock_detector.return_value = mock_detector_instance
        
        mock_result = Mock()
        mock_result.detections = [
            Mock(bbox=(100, 100, 50, 50), confidence=0.8, class_id=0, 
                 class_name='traffic_sign', area=2500, center=(125, 125))
        ]
        mock_detector_instance.detect.return_value = mock_result
        
        mock_preprocessor.return_value = Mock()
        mock_ocr.return_value = Mock()
        
        pipeline = VisionPipeline(mock_config)
        
        result = pipeline.detect_objects(sample_image)
        
        assert len(result) == 1
        assert result[0]['bbox'] == (100, 100, 50, 50)
        assert result[0]['confidence'] == 0.8
        assert result[0]['class_name'] == 'traffic_sign'
    
    @patch('vision.preprocessing.image_preprocessor.ImagePreprocessor')
    @patch('vision.detection.yolo_detector.YOLODetector')
    @patch('vision.ocr.text_extractor.TextExtractor')
    def test_extract_text(self, mock_ocr, mock_detector, mock_preprocessor, mock_config, sample_image):
        """Testa extração de texto"""
        # Mock do extrator de texto
        mock_ocr_instance = Mock()
        mock_ocr.return_value = mock_ocr_instance
        
        mock_result = Mock()
        mock_result.text_results = [
            Mock(text='ABC1234', confidence=0.9, bbox=(100, 100, 50, 30), 
                 language='pt', processing_time=0.1)
        ]
        mock_ocr_instance.extract_text.return_value = mock_result
        
        mock_preprocessor.return_value = Mock()
        mock_detector.return_value = Mock()
        
        pipeline = VisionPipeline(mock_config)
        
        regions = [{'bbox': (100, 100, 50, 30)}]
        result = pipeline.extract_text(sample_image, regions)
        
        assert len(result) == 1
        assert result[0]['text'] == 'ABC1234'
        assert result[0]['confidence'] == 0.9
        assert result[0]['bbox'] == (100, 100, 50, 30)
    
    @patch('vision.preprocessing.image_preprocessor.ImagePreprocessor')
    @patch('vision.detection.yolo_detector.YOLODetector')
    @patch('vision.ocr.text_extractor.TextExtractor')
    def test_postprocess_results(self, mock_ocr, mock_detector, mock_preprocessor, mock_config):
        """Testa pós-processamento de resultados"""
        mock_preprocessor.return_value = Mock()
        mock_detector.return_value = Mock()
        mock_ocr.return_value = Mock()
        
        pipeline = VisionPipeline(mock_config)
        
        detections = [
            {'bbox': (100, 100, 50, 50), 'confidence': 0.8, 'class_id': 0, 
             'class_name': 'traffic_sign', 'area': 2500, 'center': (125, 125)}
        ]
        
        ocr_results = [
            {'text': 'ABC1234', 'confidence': 0.9, 'bbox': (100, 100, 50, 30), 
             'language': 'pt', 'processing_time': 0.1}
        ]
        
        result = pipeline.postprocess_results(detections, ocr_results)
        
        assert isinstance(result, ProcessingResult)
        assert result.success is True
        assert len(result.detections) == 1
        assert len(result.ocr_results) == 1
        assert 'pipeline_version' in result.metadata
    
    @patch('vision.preprocessing.image_preprocessor.ImagePreprocessor')
    @patch('vision.detection.yolo_detector.YOLODetector')
    @patch('vision.ocr.text_extractor.TextExtractor')
    def test_integrate_detections_and_ocr(self, mock_ocr, mock_detector, mock_preprocessor, mock_config):
        """Testa integração de detecções com OCR"""
        mock_preprocessor.return_value = Mock()
        mock_detector.return_value = Mock()
        mock_ocr.return_value = Mock()
        
        pipeline = VisionPipeline(mock_config)
        
        detections = [
            {'bbox': (100, 100, 50, 50), 'confidence': 0.8, 'class_id': 0, 
             'class_name': 'traffic_sign', 'area': 2500, 'center': (125, 125)}
        ]
        
        ocr_results = [
            {'text': 'ABC1234', 'confidence': 0.9, 'bbox': (100, 100, 50, 30), 
             'language': 'pt', 'processing_time': 0.1}
        ]
        
        integrated = pipeline._integrate_detections_and_ocr(detections, ocr_results)
        
        assert len(integrated) == 1
        assert integrated[0]['detection'] == detections[0]
        assert len(integrated[0]['texts']) == 1
        assert integrated[0]['primary_text'] == 'ABC1234'
        assert 'confidence_score' in integrated[0]
    
    @patch('vision.preprocessing.image_preprocessor.ImagePreprocessor')
    @patch('vision.detection.yolo_detector.YOLODetector')
    @patch('vision.ocr.text_extractor.TextExtractor')
    def test_bbox_overlap_calculation(self, mock_ocr, mock_detector, mock_preprocessor, mock_config):
        """Testa cálculo de sobreposição de bounding boxes"""
        mock_preprocessor.return_value = Mock()
        mock_detector.return_value = Mock()
        mock_ocr.return_value = Mock()
        
        pipeline = VisionPipeline(mock_config)
        
        # Bounding boxes que se sobrepõem
        bbox1 = (100, 100, 50, 50)  # x, y, w, h
        bbox2 = (120, 120, 50, 50)  # Sobreposição parcial
        
        overlap = pipeline._calculate_bbox_overlap(bbox1, bbox2)
        
        assert isinstance(overlap, float)
        assert 0.0 < overlap < 1.0
        
        # Bounding boxes que não se sobrepõem
        bbox3 = (200, 200, 50, 50)
        overlap = pipeline._calculate_bbox_overlap(bbox1, bbox3)
        assert overlap == 0.0
    
    @patch('vision.preprocessing.image_preprocessor.ImagePreprocessor')
    @patch('vision.detection.yolo_detector.YOLODetector')
    @patch('vision.ocr.text_extractor.TextExtractor')
    def test_validation_rules(self, mock_ocr, mock_detector, mock_preprocessor, mock_config):
        """Testa regras de validação"""
        mock_preprocessor.return_value = Mock()
        mock_detector.return_value = Mock()
        mock_ocr.return_value = Mock()
        
        pipeline = VisionPipeline(mock_config)
        
        # Resultado válido
        valid_result = {
            'detection': {
                'bbox': (100, 100, 100, 50),  # w=100, h=50
                'confidence': 0.8
            },
            'primary_text': 'ABC1234',
            'confidence_score': 0.8
        }
        
        is_valid = pipeline._validate_single_result(valid_result, mock_config['validation_rules'])
        assert is_valid is True
        
        # Resultado inválido - muito pequeno
        invalid_result = {
            'detection': {
                'bbox': (100, 100, 30, 30),  # w=30, h=30 (muito pequeno)
                'confidence': 0.8
            },
            'primary_text': 'ABC1234',
            'confidence_score': 0.8
        }
        
        is_valid = pipeline._validate_single_result(invalid_result, mock_config['validation_rules'])
        assert is_valid is False
    
    @patch('vision.preprocessing.image_preprocessor.ImagePreprocessor')
    @patch('vision.detection.yolo_detector.YOLODetector')
    @patch('vision.ocr.text_extractor.TextExtractor')
    def test_process_image_advanced(self, mock_ocr, mock_detector, mock_preprocessor, mock_config, temp_image_file):
        """Testa processamento avançado de imagem"""
        # Mock dos componentes
        mock_preprocessor_instance = Mock()
        mock_preprocessor.return_value = mock_preprocessor_instance
        
        mock_detector_instance = Mock()
        mock_detector.return_value = mock_detector_instance
        
        mock_ocr_instance = Mock()
        mock_ocr.return_value = mock_ocr_instance
        
        # Mock dos resultados
        mock_preprocessor_instance.preprocess.return_value = Mock(processed_image=np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8))
        mock_preprocessor_instance.get_preprocessing_summary.return_value = {'enhancement_applied': ['denoising']}
        
        mock_detection_result = Mock()
        mock_detection_result.detections = [
            Mock(bbox=(100, 100, 50, 50), confidence=0.8, class_id=0, 
                 class_name='traffic_sign', area=2500, center=(125, 125))
        ]
        mock_detection_result.processing_time = 0.5
        mock_detector_instance.detect.return_value = mock_detection_result
        mock_detector_instance.get_detection_statistics.return_value = {'average_confidence': 0.8}
        
        mock_ocr_result = Mock()
        mock_ocr_result.text_results = [
            Mock(text='ABC1234', confidence=0.9, bbox=(100, 100, 50, 30), 
                 language='pt', processing_time=0.1)
        ]
        mock_ocr_result.total_processing_time = 0.1
        mock_ocr_instance.extract_text.return_value = mock_ocr_result
        mock_ocr_instance.get_ocr_statistics.return_value = {'average_confidence': 0.9}
        
        pipeline = VisionPipeline(mock_config)
        
        result = pipeline.process_image_advanced(temp_image_file)
        
        assert isinstance(result, PipelineResult)
        assert result.success is True
        assert result.image_path == temp_image_file
        assert result.processing_time > 0
        assert result.preprocessing_result is not None
        assert result.detection_result is not None
        assert result.ocr_result is not None
        assert len(result.final_results) > 0
    
    @patch('vision.preprocessing.image_preprocessor.ImagePreprocessor')
    @patch('vision.detection.yolo_detector.YOLODetector')
    @patch('vision.ocr.text_extractor.TextExtractor')
    def test_process_batch(self, mock_ocr, mock_detector, mock_preprocessor, mock_config, temp_image_file):
        """Testa processamento em lote"""
        # Mock dos componentes
        mock_preprocessor_instance = Mock()
        mock_preprocessor.return_value = mock_preprocessor_instance
        
        mock_detector_instance = Mock()
        mock_detector.return_value = mock_detector_instance
        
        mock_ocr_instance = Mock()
        mock_ocr.return_value = mock_ocr_instance
        
        # Mock dos resultados
        mock_preprocessor_instance.preprocess.return_value = Mock(processed_image=np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8))
        mock_preprocessor_instance.get_preprocessing_summary.return_value = {'enhancement_applied': ['denoising']}
        
        mock_detection_result = Mock()
        mock_detection_result.detections = [
            Mock(bbox=(100, 100, 50, 50), confidence=0.8, class_id=0, 
                 class_name='traffic_sign', area=2500, center=(125, 125))
        ]
        mock_detection_result.processing_time = 0.5
        mock_detector_instance.detect.return_value = mock_detection_result
        mock_detector_instance.get_detection_statistics.return_value = {'average_confidence': 0.8}
        
        mock_ocr_result = Mock()
        mock_ocr_result.text_results = [
            Mock(text='ABC1234', confidence=0.9, bbox=(100, 100, 50, 30), 
                 language='pt', processing_time=0.1)
        ]
        mock_ocr_result.total_processing_time = 0.1
        mock_ocr_instance.extract_text.return_value = mock_ocr_result
        mock_ocr_instance.get_ocr_statistics.return_value = {'average_confidence': 0.9}
        
        pipeline = VisionPipeline(mock_config)
        
        image_paths = [temp_image_file]
        results = pipeline.process_batch(image_paths)
        
        assert len(results) == 1
        assert results[0].success is True
        assert results[0].image_path == temp_image_file
    
    @patch('vision.preprocessing.image_preprocessor.ImagePreprocessor')
    @patch('vision.detection.yolo_detector.YOLODetector')
    @patch('vision.ocr.text_extractor.TextExtractor')
    def test_pipeline_statistics(self, mock_ocr, mock_detector, mock_preprocessor, mock_config):
        """Testa estatísticas do pipeline"""
        mock_preprocessor.return_value = Mock()
        mock_detector.return_value = Mock()
        mock_ocr.return_value = Mock()
        
        pipeline = VisionPipeline(mock_config)
        
        stats = pipeline.get_pipeline_statistics()
        
        assert isinstance(stats, dict)
        assert stats['pipeline_version'] == '2.0.0'
        assert 'components' in stats
        assert 'preprocessor' in stats['components']
        assert 'detector' in stats['components']
        assert 'ocr' in stats['components']
        assert stats['initialized_at'] is not None
        assert stats['cache_size'] == 0
    
    @patch('vision.preprocessing.image_preprocessor.ImagePreprocessor')
    @patch('vision.detection.yolo_detector.YOLODetector')
    @patch('vision.ocr.text_extractor.TextExtractor')
    def test_cleanup(self, mock_ocr, mock_detector, mock_preprocessor, mock_config):
        """Testa limpeza de recursos"""
        mock_preprocessor_instance = Mock()
        mock_preprocessor.return_value = mock_preprocessor_instance
        
        mock_detector_instance = Mock()
        mock_detector.return_value = mock_detector_instance
        
        mock_ocr_instance = Mock()
        mock_ocr.return_value = mock_ocr_instance
        
        pipeline = VisionPipeline(mock_config)
        
        # Verificar que os componentes foram inicializados
        assert pipeline.preprocessor is not None
        assert pipeline.detector is not None
        assert pipeline.text_extractor is not None
        
        # Executar cleanup
        pipeline.cleanup()
        
        # Verificar que os componentes foram limpos
        assert pipeline.preprocessor is None
        assert pipeline.detector is None
        assert pipeline.text_extractor is None
        assert len(pipeline.cache) == 0

class TestPipelineResult:
    """Testes para PipelineResult"""
    
    def test_initialization(self):
        """Testa inicialização do resultado do pipeline"""
        result = PipelineResult(
            success=True,
            image_path="test.jpg",
            processing_time=1.5,
            preprocessing_result={'test': 'data'},
            detection_result={'test': 'data'},
            ocr_result={'test': 'data'},
            final_results=[],
            metadata={'test': 'data'}
        )
        
        assert result.success is True
        assert result.image_path == "test.jpg"
        assert result.processing_time == 1.5
        assert result.preprocessing_result == {'test': 'data'}
        assert result.detection_result == {'test': 'data'}
        assert result.ocr_result == {'test': 'data'}
        assert result.final_results == []
        assert result.metadata == {'test': 'data'}
        assert result.timestamp is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])