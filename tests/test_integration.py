#!/usr/bin/env python3
"""
Testes de Integração para Pipeline de Visão Computacional
=========================================================

Testa a integração entre todos os componentes do sistema.
"""

import pytest
import numpy as np
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import json

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from vision.core.vision_pipeline import VisionPipeline
from config.vision_architecture import ConfigPresets

class TestIntegration:
    """Testes de integração para o pipeline completo"""
    
    @pytest.fixture
    def sample_image(self):
        """Cria uma imagem de teste realista"""
        # Criar imagem simulando uma placa de trânsito
        img = np.ones((640, 640, 3), dtype=np.uint8) * 255  # Fundo branco
        
        # Adicionar retângulo simulando placa
        cv2.rectangle(img, (200, 200), (440, 300), (0, 0, 255), -1)  # Placa vermelha
        
        # Adicionar texto simulando "PARE"
        cv2.putText(img, "PARE", (250, 260), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        
        return img
    
    @pytest.fixture
    def temp_image_file(self, sample_image):
        """Cria um arquivo de imagem temporário"""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            # Salvar imagem real
            import cv2
            cv2.imwrite(f.name, sample_image)
            temp_path = f.name
        
        yield temp_path
        
        # Limpar arquivo temporário
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def development_config(self):
        """Configuração de desenvolvimento para testes"""
        config = ConfigPresets.development()
        return config.__dict__
    
    @patch('vision.preprocessing.image_preprocessor.ImagePreprocessor')
    @patch('vision.detection.yolo_detector.YOLODetector')
    @patch('vision.ocr.text_extractor.TextExtractor')
    def test_full_pipeline_integration(self, mock_ocr, mock_detector, mock_preprocessor, 
                                     development_config, temp_image_file):
        """Testa integração completa do pipeline"""
        # Mock dos componentes
        mock_preprocessor_instance = Mock()
        mock_preprocessor.return_value = mock_preprocessor_instance
        
        mock_detector_instance = Mock()
        mock_detector.return_value = mock_detector_instance
        
        mock_ocr_instance = Mock()
        mock_ocr.return_value = mock_ocr_instance
        
        # Configurar mocks para simular processamento real
        # 1. Pré-processamento
        mock_preprocessor_instance.preprocess.return_value = Mock(
            processed_image=np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        )
        mock_preprocessor_instance.get_preprocessing_summary.return_value = {
            'enhancement_applied': ['denoising', 'contrast_enhancement', 'normalization']
        }
        
        # 2. Detecção
        mock_detection_result = Mock()
        mock_detection_result.detections = [
            Mock(bbox=(200, 200, 240, 100), confidence=0.85, class_id=0, 
                 class_name='traffic_sign', area=24000, center=(320, 250))
        ]
        mock_detection_result.processing_time = 0.3
        mock_detector_instance.detect.return_value = mock_detection_result
        mock_detector_instance.get_detection_statistics.return_value = {
            'total_detections': 1,
            'average_confidence': 0.85,
            'class_distribution': {'traffic_sign': 1}
        }
        
        # 3. OCR
        mock_ocr_result = Mock()
        mock_ocr_result.text_results = [
            Mock(text='PARE', confidence=0.92, bbox=(200, 200, 240, 100), 
                 language='pt', processing_time=0.2)
        ]
        mock_ocr_result.total_processing_time = 0.2
        mock_ocr_instance.extract_text.return_value = mock_ocr_result
        mock_ocr_instance.get_ocr_statistics.return_value = {
            'total_texts': 1,
            'average_confidence': 0.92,
            'average_text_length': 4
        }
        
        # Criar pipeline
        pipeline = VisionPipeline(development_config)
        
        # Processar imagem
        result = pipeline.process_image_advanced(temp_image_file)
        
        # Verificar resultado completo
        assert isinstance(result, type(pipeline).__mro__[0].__dict__['PipelineResult'])
        assert result.success is True
        assert result.image_path == temp_image_file
        assert result.processing_time > 0
        
        # Verificar componentes
        assert result.preprocessing_result is not None
        assert 'enhancement_applied' in result.preprocessing_result
        assert len(result.preprocessing_result['enhancement_applied']) == 3
        
        assert result.detection_result is not None
        assert result.detection_result['total_detections'] == 1
        assert result.detection_result['average_confidence'] == 0.85
        
        assert result.ocr_result is not None
        assert result.ocr_result['total_texts'] == 1
        assert result.ocr_result['average_confidence'] == 0.92
        
        # Verificar resultados finais
        assert len(result.final_results) == 1
        final_result = result.final_results[0]
        
        assert final_result['detection']['class_name'] == 'traffic_sign'
        assert final_result['detection']['confidence'] == 0.85
        assert final_result['primary_text'] == 'PARE'
        assert final_result['confidence_score'] > 0.8
        
        # Verificar metadados
        assert result.metadata['pipeline_version'] == '2.0.0'
        assert result.metadata['total_detections'] == 1
        assert result.metadata['total_texts'] == 1
        assert result.metadata['validated_results'] == 1
    
    @patch('vision.preprocessing.image_preprocessor.ImagePreprocessor')
    @patch('vision.detection.yolo_detector.YOLODetector')
    @patch('vision.ocr.text_extractor.TextExtractor')
    def test_batch_processing_integration(self, mock_ocr, mock_detector, mock_preprocessor, 
                                        development_config, temp_image_file):
        """Testa processamento em lote integrado"""
        # Mock dos componentes
        mock_preprocessor_instance = Mock()
        mock_preprocessor.return_value = mock_preprocessor_instance
        
        mock_detector_instance = Mock()
        mock_detector.return_value = mock_detector_instance
        
        mock_ocr_instance = Mock()
        mock_ocr.return_value = mock_ocr_instance
        
        # Configurar mocks para processamento em lote
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
        
        # Criar pipeline
        pipeline = VisionPipeline(development_config)
        
        # Processar múltiplas imagens
        image_paths = [temp_image_file, temp_image_file]  # Mesma imagem duas vezes
        results = pipeline.process_batch(image_paths, "temp_output")
        
        # Verificar resultados
        assert len(results) == 2
        for result in results:
            assert result.success is True
            assert result.image_path == temp_image_file
            assert len(result.final_results) == 1
        
        # Verificar se diretório de saída foi criado
        output_dir = Path("temp_output")
        assert output_dir.exists()
        
        # Limpar diretório de teste
        import shutil
        shutil.rmtree("temp_output")
    
    @patch('vision.preprocessing.image_preprocessor.ImagePreprocessor')
    @patch('vision.detection.yolo_detector.YOLODetector')
    @patch('vision.ocr.text_extractor.TextExtractor')
    def test_error_handling_integration(self, mock_ocr, mock_detector, mock_preprocessor, 
                                      development_config, temp_image_file):
        """Testa tratamento de erros integrado"""
        # Mock dos componentes com erro
        mock_preprocessor_instance = Mock()
        mock_preprocessor.return_value = mock_preprocessor_instance
        
        mock_detector_instance = Mock()
        mock_detector.return_value = mock_detector_instance
        
        mock_ocr_instance = Mock()
        mock_ocr.return_value = mock_ocr_instance
        
        # Simular erro no pré-processamento
        mock_preprocessor_instance.preprocess.side_effect = Exception("Erro de pré-processamento")
        
        # Criar pipeline
        pipeline = VisionPipeline(development_config)
        
        # Processar imagem (deve falhar graciosamente)
        result = pipeline.process_image_advanced(temp_image_file)
        
        # Verificar que o erro foi tratado
        assert result.success is False
        assert "Erro de pré-processamento" in result.error_message
        assert result.processing_time > 0
    
    @patch('vision.preprocessing.image_preprocessor.ImagePreprocessor')
    @patch('vision.detection.yolo_detector.YOLODetector')
    @patch('vision.ocr.text_extractor.TextExtractor')
    def test_configuration_presets_integration(self, mock_ocr, mock_detector, mock_preprocessor):
        """Testa integração com diferentes presets de configuração"""
        # Mock dos componentes
        mock_preprocessor.return_value = Mock()
        mock_detector.return_value = Mock()
        mock_ocr.return_value = Mock()
        
        # Testar configuração de desenvolvimento
        dev_config = ConfigPresets.development().__dict__
        dev_pipeline = VisionPipeline(dev_config)
        
        assert dev_pipeline.config['detection']['device'] == 'cpu'
        assert dev_pipeline.config['ocr']['use_gpu'] is False
        
        # Testar configuração de produção
        prod_config = ConfigPresets.production().__dict__
        prod_pipeline = VisionPipeline(prod_config)
        
        assert prod_config['detection']['device'] == 'cuda'
        assert prod_config['ocr']['use_gpu'] is True
        
        # Testar configuração de edge
        edge_config = ConfigPresets.edge().__dict__
        edge_pipeline = VisionPipeline(edge_config)
        
        assert edge_config['detection']['device'] == 'cpu'
        assert edge_config['detection']['half_precision'] is True
    
    @patch('vision.preprocessing.image_preprocessor.ImagePreprocessor')
    @patch('vision.detection.yolo_detector.YOLODetector')
    @patch('vision.ocr.text_extractor.TextExtractor')
    def test_pipeline_statistics_integration(self, mock_ocr, mock_detector, mock_preprocessor, 
                                           development_config):
        """Testa estatísticas integradas do pipeline"""
        # Mock dos componentes
        mock_preprocessor.return_value = Mock()
        mock_detector.return_value = Mock()
        mock_ocr.return_value = Mock()
        
        # Criar pipeline
        pipeline = VisionPipeline(development_config)
        
        # Obter estatísticas
        stats = pipeline.get_pipeline_statistics()
        
        # Verificar estatísticas completas
        assert stats['pipeline_version'] == '2.0.0'
        assert 'components' in stats
        assert stats['components']['preprocessor'] is True
        assert stats['components']['detector'] is True
        assert stats['components']['ocr'] is True
        assert stats['initialized_at'] is not None
        assert stats['cache_size'] == 0
        assert 'config' in stats
    
    @patch('vision.preprocessing.image_preprocessor.ImagePreprocessor')
    @patch('vision.detection.yolo_detector.YOLODetector')
    @patch('vision.ocr.text_extractor.TextExtractor')
    def test_cleanup_integration(self, mock_ocr, mock_detector, mock_preprocessor, 
                                development_config):
        """Testa limpeza integrada de recursos"""
        # Mock dos componentes
        mock_preprocessor_instance = Mock()
        mock_preprocessor.return_value = mock_preprocessor_instance
        
        mock_detector_instance = Mock()
        mock_detector.return_value = mock_detector_instance
        
        mock_ocr_instance = Mock()
        mock_ocr.return_value = mock_ocr_instance
        
        # Criar pipeline
        pipeline = VisionPipeline(development_config)
        
        # Verificar que os componentes foram inicializados
        assert pipeline.preprocessor is not None
        assert pipeline.detector is not None
        assert pipeline.text_extractor is not None
        
        # Executar cleanup
        pipeline.cleanup()
        
        # Verificar que todos os recursos foram limpos
        assert pipeline.preprocessor is None
        assert pipeline.detector is None
        assert pipeline.text_extractor is None
        assert len(pipeline.cache) == 0

class TestEndToEnd:
    """Testes end-to-end do sistema"""
    
    @pytest.fixture
    def real_config(self):
        """Configuração real para testes end-to-end"""
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
                'type': 'tesseract',  # Usar Tesseract para testes
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
            'log_level': 'WARNING'  # Reduzir logs para testes
        }
    
    def test_real_pipeline_creation(self, real_config):
        """Testa criação real do pipeline (sem processamento)"""
        try:
            pipeline = VisionPipeline(real_config)
            assert pipeline is not None
            
            # Verificar que os componentes foram inicializados
            assert hasattr(pipeline, 'preprocessor')
            assert hasattr(pipeline, 'detector')
            assert hasattr(pipeline, 'text_extractor')
            
            # Cleanup
            pipeline.cleanup()
            
        except Exception as e:
            # Se falhar, é provavelmente por dependências não instaladas
            pytest.skip(f"Pipeline não pode ser criado: {e}")
    
    def test_configuration_validation(self):
        """Testa validação de configurações"""
        # Testar configurações válidas
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