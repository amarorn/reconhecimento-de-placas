

import pytest
import numpy as np
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

sys.path.append(str(Path(__file__).parent.parent))

from vision.ocr.text_extractor import (
    TextExtractor, 
    TextResult, 
    OCRBatchResult,
    OCRType
)

class TestTextExtractor:
        return np.random.randint(0, 255, (100, 200, 3), dtype=np.uint8)
    
    @pytest.fixture
    def mock_config(self):
        return [
            {'bbox': (50, 50, 100, 30)},
            {'bbox': (150, 50, 100, 30)}
        ]
    
    @patch('vision.ocr.text_extractor.PaddleOCR')
    def test_initialization_paddleocr(self, mock_paddleocr, mock_config):
        mock_config['type'] = OCRType.EASYOCR
        mock_reader = Mock()
        mock_easyocr.Reader.return_value = mock_reader
        
        extractor = TextExtractor(mock_config)
        
        assert extractor is not None
        assert extractor.current_ocr == OCRType.EASYOCR
        assert OCRType.EASYOCR in extractor.ocr_engines
    
    @patch('vision.ocr.text_extractor.pytesseract')
    def test_initialization_tesseract(self, mock_tesseract, mock_config):
        mock_config['type'] = OCRType.TRANSFORMER_OCR
        
        mock_processor = Mock()
        mock_model = Mock()
        mock_transformers.TrOCRProcessor.from_pretrained.return_value = mock_processor
        mock_transformers.VisionEncoderDecoderModel.from_pretrained.return_value = mock_model
        
        extractor = TextExtractor(mock_config)
        
        assert extractor is not None
        assert extractor.current_ocr == OCRType.TRANSFORMER_OCR
        assert OCRType.TRANSFORMER_OCR in extractor.ocr_engines
    
    @patch('vision.ocr.text_extractor.PaddleOCR')
    def test_extract_text_paddleocr(self, mock_paddleocr, mock_config, sample_image, sample_regions):
        mock_config['type'] = OCRType.EASYOCR
        mock_reader = Mock()
        mock_easyocr.Reader.return_value = mock_reader
        
        mock_reader.readtext.return_value = [
            ([[50, 50], [150, 50], [150, 80], [50, 80]], 'ABC1234', 0.9),
            ([[150, 50], [250, 50], [250, 80], [150, 80]], 'XYZ5678', 0.8)
        ]
        
        extractor = TextExtractor(mock_config)
        
        result = extractor.extract_text(sample_image, sample_regions)
        
        assert isinstance(result, OCRBatchResult)
        assert len(result.text_results) == 2
        assert result.text_results[0].text == 'ABC1234'
        assert result.text_results[0].confidence == 0.9
    
    @patch('vision.ocr.text_extractor.pytesseract')
    def test_extract_text_tesseract(self, mock_tesseract, mock_config, sample_image, sample_regions):
        mock_config['type'] = OCRType.TRANSFORMER_OCR
        
        mock_processor = Mock()
        mock_model = Mock()
        mock_transformers.TrOCRProcessor.from_pretrained.return_value = mock_processor
        mock_transformers.VisionEncoderDecoderModel.from_pretrained.return_value = mock_model
        
        mock_pixel_values = Mock()
        mock_processor.return_value = {'pixel_values': mock_pixel_values}
        mock_model.generate.return_value = Mock()
        mock_processor.batch_decode.return_value = ['ABC1234']
        
        extractor = TextExtractor(mock_config)
        
        result = extractor.extract_text(sample_image, sample_regions)
        
        assert isinstance(result, OCRBatchResult)
        assert len(result.text_results) == 1
    
    def test_postprocess_text(self, mock_config):
        extractor = TextExtractor(mock_config)
        
        result = extractor._apply_plate_rules("ABC1234")
        assert result == "ABC1234"
        
        result = extractor._apply_plate_rules("ABC1D23")
        assert result == "ABC1D23"
        
        result = extractor._apply_plate_rules("ABC12D3")
        assert result == "ABC12D3"
        
        result = extractor._apply_plate_rules("INVALID")
        assert result == "INVALID"
    
    def test_assess_image_quality(self, mock_config):
        extractor = TextExtractor(mock_config)
        
        confidence = extractor._estimate_tesseract_confidence(np.zeros((100, 100)), "")
        assert confidence == 0.0
        
        confidence = extractor._estimate_tesseract_confidence(np.random.randint(0, 255, (100, 100)), "ABC1234")
        assert 0.0 <= confidence <= 1.0
    
    def test_get_ocr_statistics(self, mock_config):
        extractor = TextExtractor(mock_config)
        
        with pytest.raises(AttributeError):
            extractor.extract_text(None, [])
    
    def test_cleanup(self, mock_config):
    
    def test_initialization(self):
    
    def test_initialization(self):
