

import pytest
import numpy as np
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import json

sys.path.append(str(Path(__file__).parent.parent))

from vision.core.vision_pipeline import VisionPipeline
from config.vision_architecture import ConfigPresets

class TestIntegration:
        img = np.ones((640, 640, 3), dtype=np.uint8) * 255
        
        cv2.rectangle(img, (200, 200), (440, 300), (0, 0, 255), -1)
        
        cv2.putText(img, "PARE", (250, 260), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        
        return img
    
    @pytest.fixture
    def temp_image_file(self, sample_image):
        config = ConfigPresets.development()
        return config.__dict__
    
    @patch('vision.preprocessing.image_preprocessor.ImagePreprocessor')
    @patch('vision.detection.yolo_detector.YOLODetector')
    @patch('vision.ocr.text_extractor.TextExtractor')
    def test_full_pipeline_integration(self, mock_ocr, mock_detector, mock_preprocessor, 
                                     development_config, temp_image_file):
        mock_preprocessor_instance = Mock()
        mock_preprocessor.return_value = mock_preprocessor_instance
        
        mock_detector_instance = Mock()
        mock_detector.return_value = mock_detector_instance
        
        mock_ocr_instance = Mock()
        mock_ocr.return_value = mock_ocr_instance
        
        mock_preprocessor_instance.preprocess.return_value = Mock(
            processed_image=np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        )
        mock_preprocessor_instance.get_preprocessing_summary.return_value = {
            'enhancement_applied': ['denoising']
        }
        
        mock_detection_result = Mock()
        mock_detection_result.detections = [
            Mock(bbox=(200, 200, 240, 100), confidence=0.85, class_id=0, 
                 class_name='traffic_sign', area=24000, center=(320, 250))
        ]
        mock_detection_result.processing_time = 0.3
        mock_detector_instance.detect.return_value = mock_detection_result
        mock_detector_instance.get_detection_statistics.return_value = {
            'total_detections': 1,
            'average_confidence': 0.85
        }
        
        mock_ocr_result = Mock()
        mock_ocr_result.text_results = [
            Mock(text='PARE', confidence=0.92, bbox=(200, 200, 240, 100), 
                 language='pt', processing_time=0.2)
        ]
        mock_ocr_result.total_processing_time = 0.2
        mock_ocr_instance.extract_text.return_value = mock_ocr_result
        mock_ocr_instance.get_ocr_statistics.return_value = {
            'total_texts': 1,
            'average_confidence': 0.92
        }
        
        pipeline = VisionPipeline(development_config)
        
        image_paths = [temp_image_file, temp_image_file]
        results = pipeline.process_batch(image_paths, "temp_output")
        
        assert len(results) == 2
        for result in results:
            assert result.success is True
            assert result.image_path == temp_image_file
            assert len(result.final_results) == 1
        
        output_dir = Path("temp_output")
        assert output_dir.exists()
        
        import shutil
        shutil.rmtree("temp_output")
    
    @patch('vision.preprocessing.image_preprocessor.ImagePreprocessor')
    @patch('vision.detection.yolo_detector.YOLODetector')
    @patch('vision.ocr.text_extractor.TextExtractor')
    def test_error_handling_integration(self, mock_ocr, mock_detector, mock_preprocessor, 
                                      development_config, temp_image_file):
        mock_preprocessor.return_value = Mock()
        mock_detector.return_value = Mock()
        mock_ocr.return_value = Mock()
        
        dev_config = ConfigPresets.development().__dict__
        dev_pipeline = VisionPipeline(dev_config)
        
        assert dev_pipeline.config['detection']['device'] == 'cpu'
        assert dev_pipeline.config['ocr']['use_gpu'] is False
        
        prod_config = ConfigPresets.production().__dict__
        prod_pipeline = VisionPipeline(prod_config)
        
        assert prod_config['detection']['device'] == 'cuda'
        assert prod_config['ocr']['use_gpu'] is True
        
        edge_config = ConfigPresets.edge().__dict__
        edge_pipeline = VisionPipeline(edge_config)
        
        assert edge_config['detection']['device'] == 'cpu'
        assert edge_config['detection']['half_precision'] is True
    
    @patch('vision.preprocessing.image_preprocessor.ImagePreprocessor')
    @patch('vision.detection.yolo_detector.YOLODetector')
    @patch('vision.ocr.text_extractor.TextExtractor')
    def test_pipeline_statistics_integration(self, mock_ocr, mock_detector, mock_preprocessor, 
                                           development_config):
        mock_preprocessor_instance = Mock()
        mock_preprocessor.return_value = mock_preprocessor_instance
        
        mock_detector_instance = Mock()
        mock_detector.return_value = mock_detector_instance
        
        mock_ocr_instance = Mock()
        mock_ocr.return_value = mock_ocr_instance
        
        pipeline = VisionPipeline(development_config)
        
        assert pipeline.preprocessor is not None
        assert pipeline.detector is not None
        assert pipeline.text_extractor is not None
        
        pipeline.cleanup()
        
        assert pipeline.preprocessor is None
        assert pipeline.detector is None
        assert pipeline.text_extractor is None
        assert len(pipeline.cache) == 0

class TestEndToEnd:
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
                'type': 'tesseract',
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
            'log_level': 'WARNING'
        }
    
    def test_real_pipeline_creation(self, real_config):
        valid_configs = [
            ConfigPresets.development(),
            ConfigPresets.production(),
            ConfigPresets.edge()
        ]
        
        for config in valid_configs:
            assert config is not None
            assert hasattr(config, 'detection_model')
            assert hasattr(config, 'ocr_model')
            assert hasattr(config, 'preprocessing')
            assert hasattr(config, 'pipeline')

if __name__ == "__main__":
    pytest.main([__file__, "-v"])