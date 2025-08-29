#!/usr/bin/env python3
"""
Testes Unitários para Sistema OCR
=================================

Testa todas as funcionalidades do TextExtractor.
"""

import pytest
import numpy as np
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from vision.ocr.text_extractor import (
    TextExtractor, 
    TextResult, 
    OCRBatchResult,
    OCRType
)

class TestTextExtractor:
    """Testes para TextExtractor"""
    
    @pytest.fixture
    def sample_image(self):
        """Cria uma imagem de teste"""
        return np.random.randint(0, 255, (100, 200, 3), dtype=np.uint8)
    
    @pytest.fixture
    def mock_config(self):
        """Cria configuração mock para testes"""
        return {
            'type': OCRType.PADDLEOCR,
            'language': 'pt',
            'confidence_threshold': 0.7,
            'use_gpu': False,
            'apply_plate_rules': True
        }
    
    @pytest.fixture
    def sample_regions(self):
        """Cria regiões de teste"""
        return [
            {'bbox': (50, 50, 100, 30)},
            {'bbox': (150, 50, 100, 30)}
        ]
    
    @patch('vision.ocr.text_extractor.PaddleOCR')
    def test_initialization_paddleocr(self, mock_paddleocr, mock_config):
        """Testa inicialização com PaddleOCR"""
        mock_ocr = Mock()
        mock_paddleocr.return_value = mock_ocr
        
        extractor = TextExtractor(mock_config)
        
        assert extractor is not None
        assert extractor.current_ocr == OCRType.PADDLEOCR
        assert OCRType.PADDLEOCR in extractor.ocr_engines
    
    @patch('vision.ocr.text_extractor.easyocr')
    def test_initialization_easyocr(self, mock_easyocr, mock_config):
        """Testa inicialização com EasyOCR"""
        mock_config['type'] = OCRType.EASYOCR
        mock_reader = Mock()
        mock_easyocr.Reader.return_value = mock_reader
        
        extractor = TextExtractor(mock_config)
        
        assert extractor is not None
        assert extractor.current_ocr == OCRType.EASYOCR
        assert OCRType.EASYOCR in extractor.ocr_engines
    
    @patch('vision.ocr.text_extractor.pytesseract')
    def test_initialization_tesseract(self, mock_tesseract, mock_config):
        """Testa inicialização com Tesseract"""
        mock_config['type'] = OCRType.TESSERACT
        
        extractor = TextExtractor(mock_config)
        
        assert extractor is not None
        assert extractor.current_ocr == OCRType.TESSERACT
        assert OCRType.TESSERACT in extractor.ocr_engines
    
    @patch('vision.ocr.text_extractor.transformers')
    def test_initialization_transformer(self, mock_transformers, mock_config):
        """Testa inicialização com Transformers"""
        mock_config['type'] = OCRType.TRANSFORMER_OCR
        
        # Mock dos componentes do Transformers
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
        """Testa extração de texto com PaddleOCR"""
        mock_ocr = Mock()
        mock_paddleocr.return_value = mock_ocr
        
        # Mock dos resultados do PaddleOCR
        mock_ocr.ocr.return_value = [
            [
                ([[50, 50], [150, 50], [150, 80], [50, 80]], ('ABC1234', 0.9)),
                ([[150, 50], [250, 50], [250, 80], [150, 80]], ('XYZ5678', 0.8))
            ]
        ]
        
        extractor = TextExtractor(mock_config)
        
        result = extractor.extract_text(sample_image, sample_regions)
        
        assert isinstance(result, OCRBatchResult)
        assert len(result.text_results) == 2
        assert result.text_results[0].text == 'ABC1234'
        assert result.text_results[0].confidence == 0.9
        assert result.text_results[1].text == 'XYZ5678'
        assert result.text_results[1].confidence == 0.8
    
    @patch('vision.ocr.text_extractor.easyocr')
    def test_extract_text_easyocr(self, mock_easyocr, mock_config, sample_image, sample_regions):
        """Testa extração de texto com EasyOCR"""
        mock_config['type'] = OCRType.EASYOCR
        mock_reader = Mock()
        mock_easyocr.Reader.return_value = mock_reader
        
        # Mock dos resultados do EasyOCR
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
        """Testa extração de texto com Tesseract"""
        mock_config['type'] = OCRType.TESSERACT
        
        # Mock dos resultados do Tesseract
        mock_tesseract.image_to_string.return_value = 'ABC1234\nXYZ5678'
        
        extractor = TextExtractor(mock_config)
        
        result = extractor.extract_text(sample_image, sample_regions)
        
        assert isinstance(result, OCRBatchResult)
        assert len(result.text_results) == 2
    
    @patch('vision.ocr.text_extractor.transformers')
    def test_extract_text_transformer(self, mock_transformers, mock_config, sample_image, sample_regions):
        """Testa extração de texto com Transformers"""
        mock_config['type'] = OCRType.TRANSFORMER_OCR
        
        # Mock dos componentes do Transformers
        mock_processor = Mock()
        mock_model = Mock()
        mock_transformers.TrOCRProcessor.from_pretrained.return_value = mock_processor
        mock_transformers.VisionEncoderDecoderModel.from_pretrained.return_value = mock_model
        
        # Mock do processamento
        mock_pixel_values = Mock()
        mock_processor.return_value = {'pixel_values': mock_pixel_values}
        mock_model.generate.return_value = Mock()
        mock_processor.batch_decode.return_value = ['ABC1234']
        
        extractor = TextExtractor(mock_config)
        
        result = extractor.extract_text(sample_image, sample_regions)
        
        assert isinstance(result, OCRBatchResult)
        assert len(result.text_results) == 1
    
    def test_postprocess_text(self, mock_config):
        """Testa pós-processamento de texto"""
        extractor = TextExtractor(mock_config)
        
        # Testar texto normal
        processed = extractor.postprocess_text("ABC1234")
        assert processed == "ABC1234"
        
        # Testar texto com espaços extras
        processed = extractor.postprocess_text("  ABC  1234  ")
        assert processed == "ABC1234"
        
        # Testar texto com caracteres especiais
        processed = extractor.postprocess_text("ABC-1234!")
        assert processed == "ABC1234"
    
    def test_apply_plate_rules(self, mock_config):
        """Testa aplicação de regras de placas"""
        extractor = TextExtractor(mock_config)
        
        # Testar padrão brasileiro
        result = extractor._apply_plate_rules("ABC1234")
        assert result == "ABC1234"
        
        # Testar padrão mercosul
        result = extractor._apply_plate_rules("ABC1D23")
        assert result == "ABC1D23"
        
        # Testar padrão moto
        result = extractor._apply_plate_rules("ABC12D3")
        assert result == "ABC12D3"
        
        # Testar texto inválido
        result = extractor._apply_plate_rules("INVALID")
        assert result == "INVALID"
    
    def test_assess_image_quality(self, mock_config):
        """Testa avaliação de qualidade de imagem"""
        extractor = TextExtractor(mock_config)
        
        # Criar imagem de teste
        test_image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        
        quality = extractor._assess_image_quality(test_image)
        
        assert isinstance(quality, float)
        assert 0.0 <= quality <= 1.0
    
    def test_estimate_tesseract_confidence(self, mock_config):
        """Testa estimativa de confiança para Tesseract"""
        extractor = TextExtractor(mock_config)
        
        # Testar com texto vazio
        confidence = extractor._estimate_tesseract_confidence(np.zeros((100, 100)), "")
        assert confidence == 0.0
        
        # Testar com texto válido
        confidence = extractor._estimate_tesseract_confidence(np.random.randint(0, 255, (100, 100)), "ABC1234")
        assert 0.0 <= confidence <= 1.0
    
    def test_get_ocr_statistics(self, mock_config):
        """Testa estatísticas do OCR"""
        extractor = TextExtractor(mock_config)
        
        # Criar resultado de teste
        text_results = [
            TextResult(
                text="ABC1234",
                confidence=0.9,
                bbox=(50, 50, 100, 30),
                language="pt",
                processing_time=0.1
            ),
            TextResult(
                text="XYZ5678",
                confidence=0.8,
                bbox=(150, 50, 100, 30),
                language="pt",
                processing_time=0.15
            )
        ]
        
        result = OCRBatchResult(
            text_results=text_results,
            total_processing_time=0.25,
            metadata={'test': 'data'}
        )
        
        stats = extractor.get_ocr_statistics(result)
        
        assert stats['total_texts'] == 2
        assert stats['average_confidence'] == 0.85
        assert stats['min_confidence'] == 0.8
        assert stats['max_confidence'] == 0.9
        assert stats['average_text_length'] == 7.0
        assert stats['total_processing_time'] == 0.25
    
    def test_error_handling(self, mock_config):
        """Testa tratamento de erros"""
        extractor = TextExtractor(mock_config)
        
        # Testar com imagem None
        with pytest.raises(AttributeError):
            extractor.extract_text(None, [])
    
    def test_cleanup(self, mock_config):
        """Testa limpeza de recursos"""
        extractor = TextExtractor(mock_config)
        
        # Adicionar alguns motores mock
        extractor.ocr_engines = {
            OCRType.PADDLEOCR: Mock(),
            OCRType.EASYOCR: Mock()
        }
        extractor.current_ocr = OCRType.PADDLEOCR
        
        extractor.cleanup()
        
        assert len(extractor.ocr_engines) == 0
        assert extractor.current_ocr is None

class TestTextResult:
    """Testes para TextResult"""
    
    def test_initialization(self):
        """Testa inicialização do resultado de texto"""
        result = TextResult(
            text="ABC1234",
            confidence=0.9,
            bbox=(50, 50, 100, 30),
            language="pt",
            processing_time=0.1
        )
        
        assert result.text == "ABC1234"
        assert result.confidence == 0.9
        assert result.bbox == (50, 50, 100, 30)
        assert result.language == "pt"
        assert result.processing_time == 0.1

class TestOCRBatchResult:
    """Testes para OCRBatchResult"""
    
    def test_initialization(self):
        """Testa inicialização do resultado em lote"""
        text_results = []
        result = OCRBatchResult(
            text_results=text_results,
            total_processing_time=0.25,
            metadata={'test': 'data'}
        )
        
        assert result.text_results == text_results
        assert result.total_processing_time == 0.25
        assert result.metadata == {'test': 'data'}

if __name__ == "__main__":
    pytest.main([__file__, "-v"])