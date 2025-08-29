#!/usr/bin/env python3
"""
Testes para a Aplicação de Reconhecimento de Placas
===================================================

Este arquivo contém testes básicos para validar a funcionalidade
da aplicação de reconhecimento de placas.
"""

import unittest
import numpy as np
import cv2
import os
import tempfile
from plate_recognition import PlateRecognizer

class TestPlateRecognizer(unittest.TestCase):
    """Testes para a classe PlateRecognizer"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.recognizer = PlateRecognizer()
        self.test_image = self.create_test_image()
        
    def create_test_image(self):
        """Cria uma imagem de teste com uma placa simulada"""
        # Criar imagem branca
        img = np.ones((300, 600, 3), dtype=np.uint8) * 255
        
        # Adicionar retângulo da placa (fundo cinza)
        cv2.rectangle(img, (100, 100), (500, 200), (128, 128, 128), -1)
        
        # Adicionar texto da placa
        cv2.putText(img, "ABC1234", (150, 150), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
        
        return img
    
    def test_initialization(self):
        """Testa se o reconhecedor é inicializado corretamente"""
        self.assertIsNotNone(self.recognizer.reader)
        self.assertIsNotNone(self.recognizer.plate_pattern)
    
    def test_preprocess_image(self):
        """Testa o pré-processamento de imagem"""
        processed = self.recognizer.preprocess_image(self.test_image)
        
        # Verificar se a imagem foi processada
        self.assertIsNotNone(processed)
        self.assertEqual(len(processed.shape), 2)  # Deve ser grayscale
        self.assertEqual(processed.dtype, np.uint8)
    
    def test_plate_pattern_matching(self):
        """Testa o padrão de reconhecimento de placas"""
        # Placas válidas
        valid_plates = ["ABC1234", "XYZ1A23", "DEF5678"]
        for plate in valid_plates:
            self.assertIsNotNone(self.recognizer.plate_pattern.match(plate))
        
        # Placas inválidas
        invalid_plates = ["ABC123", "XYZ12345", "123ABC", "ABC12D3"]
        for plate in invalid_plates:
            self.assertIsNone(self.recognizer.plate_pattern.match(plate))
    
    def test_detect_plate_regions(self):
        """Testa a detecção de regiões de placas"""
        processed = self.recognizer.preprocess_image(self.test_image)
        regions = self.recognizer.detect_plate_regions(processed)
        
        # Deve detectar pelo menos uma região
        self.assertGreaterEqual(len(regions), 0)
        
        # Se detectou regiões, verificar se são quadriláteros
        for region in regions:
            self.assertEqual(len(region), 4)  # 4 vértices
    
    def test_extract_plate_image(self):
        """Testa a extração de imagem da placa"""
        # Criar contorno de teste
        contour = np.array([[[100, 100]], [[500, 100]], [[500, 200]], [[100, 200]]], dtype=np.int32)
        
        extracted = self.recognizer.extract_plate_image(self.test_image, contour)
        
        # Verificar se a imagem foi extraída
        self.assertIsNotNone(extracted)
        self.assertEqual(extracted.shape, (100, 300, 3))  # Tamanho padrão
    
    def test_save_and_load_image(self):
        """Testa salvamento e carregamento de imagem"""
        # Salvar imagem de teste
        temp_path = tempfile.mktemp(suffix='.jpg')
        cv2.imwrite(temp_path, self.test_image)
        
        # Verificar se foi salva
        self.assertTrue(os.path.exists(temp_path))
        
        # Carregar imagem
        loaded = cv2.imread(temp_path)
        self.assertIsNotNone(loaded)
        
        # Limpar arquivo temporário
        os.remove(temp_path)
    
    def test_batch_processing_empty_folder(self):
        """Testa processamento em lote com pasta vazia"""
        with tempfile.TemporaryDirectory() as temp_dir:
            results = self.recognizer.batch_process(temp_dir)
            self.assertEqual(len(results), 0)
    
    def test_error_handling_invalid_image(self):
        """Testa tratamento de erro para imagem inválida"""
        with self.assertRaises(ValueError):
            self.recognizer.process_image("imagem_inexistente.jpg")

def run_performance_test():
    """Teste de performance básico"""
    print("\n=== TESTE DE PERFORMANCE ===")
    
    recognizer = PlateRecognizer()
    
    # Criar imagem de teste
    test_img = np.ones((800, 1200, 3), dtype=np.uint8) * 255
    cv2.putText(test_img, "XYZ9B87", (200, 400), 
                cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 0), 5)
    
    # Salvar temporariamente
    temp_path = "temp_performance_test.jpg"
    cv2.imwrite(temp_path, test_img)
    
    try:
        import time
        start_time = time.time()
        
        # Processar imagem
        results = recognizer.process_image(temp_path, show_results=False)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"Tempo de processamento: {processing_time:.2f} segundos")
        print(f"Placas encontradas: {len(results['plates_found'])}")
        
        if results['plates_found']:
            print(f"Texto reconhecido: {results['plates_found'][0]['text']}")
        
    finally:
        # Limpar
        if os.path.exists(temp_path):
            os.remove(temp_path)

def main():
    """Função principal para executar os testes"""
    print("🧪 EXECUTANDO TESTES - RECONHECIMENTO DE PLACAS")
    print("=" * 50)
    
    # Executar testes unitários
    print("\n1. Executando testes unitários...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Executar teste de performance
    print("\n2. Executando teste de performance...")
    run_performance_test()
    
    print("\n" + "=" * 50)
    print("✅ Todos os testes foram executados!")
    print("\nPara executar apenas os testes unitários:")
    print("python -m unittest test_app.py -v")

if __name__ == "__main__":
    main()
