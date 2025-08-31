

import pytest
import numpy as np
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

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
        return np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
    
    @pytest.fixture
    def mock_config(self):
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            f.write(b'fake_image_data')
            temp_path = f.name
        
        yield temp_path
        
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @patch('vision.preprocessing.image_preprocessor.ImagePreprocessor')
    @patch('vision.detection.yolo_detector.YOLODetector')
    @patch('vision.ocr.text_extractor.TextExtractor')
    def test_initialization(self, mock_ocr, mock_detector, mock_preprocessor, mock_config):
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
        mock_preprocessor.return_value = Mock()
        mock_detector.return_value = Mock()
        mock_ocr.return_value = Mock()
        
        pipeline = VisionPipeline(mock_config)
        
        valid_result = {
            'detection': {
                'bbox': (100, 100, 100, 50),
                'confidence': 0.8
            },
            'primary_text': 'ABC1234',
            'confidence_score': 0.8
        }
        
        is_valid = pipeline._validate_single_result(valid_result, mock_config['validation_rules'])
        assert is_valid is True
        
        invalid_result = {
            'detection': {
                'bbox': (100, 100, 30, 30),
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
        mock_preprocessor_instance = Mock()
        mock_preprocessor.return_value = mock_preprocessor_instance
        
        mock_detector_instance = Mock()
        mock_detector.return_value = mock_detector_instance
        
        mock_ocr_instance = Mock()
        mock_ocr.return_value = mock_ocr_instance
        
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
        mock_preprocessor_instance = Mock()
        mock_preprocessor.return_value = mock_preprocessor_instance
        
        mock_detector_instance = Mock()
        mock_detector.return_value = mock_detector_instance
        
        mock_ocr_instance = Mock()
        mock_ocr.return_value = mock_ocr_instance
        
        pipeline = VisionPipeline(mock_config)
        
        assert pipeline.preprocessor is not None
        assert pipeline.detector is not None
        assert pipeline.text_extractor is not None
        
        pipeline.cleanup()
        
        assert pipeline.preprocessor is None
        assert pipeline.detector is None
        assert pipeline.text_extractor is None
        assert len(pipeline.cache) == 0

class TestPipelineResult:
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