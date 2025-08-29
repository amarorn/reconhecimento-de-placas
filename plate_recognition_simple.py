#!/usr/bin/env python3
"""
Reconhecedor de Placas Simplificado - Versão de Demonstração
============================================================

Esta versão usa apenas OpenCV para detecção de placas, sem dependência
do EasyOCR, permitindo demonstração imediata da funcionalidade.
"""

import cv2
import numpy as np
import re
from typing import List, Optional
import matplotlib.pyplot as plt
import os

class SimplePlateRecognizer:
    """
    Versão simplificada do reconhecedor de placas usando apenas OpenCV
    """
    
    def __init__(self):
        """Inicializa o reconhecedor simplificado"""
        self.plate_pattern = re.compile(r'[A-Z]{3}[0-9]{4}|[A-Z]{3}[0-9]{1}[A-Z]{1}[0-9]{2}')
        
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Pré-processa a imagem para melhorar a detecção
        
        Args:
            image: Imagem de entrada
            
        Returns:
            Imagem pré-processada
        """
        # Converter para escala de cinza
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Aplicar filtro Gaussiano para reduzir ruído
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Aplicar equalização de histograma
        equalized = cv2.equalizeHist(blurred)
        
        # Aplicar filtro bilateral para preservar bordas
        bilateral = cv2.bilateralFilter(equalized, 11, 17, 17)
        
        return bilateral
    
    def detect_plate_regions(self, image: np.ndarray) -> List[np.ndarray]:
        """
        Detecta possíveis regiões de placas na imagem
        
        Args:
            image: Imagem pré-processada
            
        Returns:
            Lista de regiões candidatas
        """
        # Detectar bordas com parâmetros mais sensíveis
        edges = cv2.Canny(image, 30, 150)  # Reduzir limiares para detectar mais bordas
        
        # Aplicar operações morfológicas para conectar bordas
        kernel = np.ones((3,3), np.uint8)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filtrar contornos por área e forma
        plate_candidates = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Reduzir área mínima para detectar placas menores
            if area > 500:  # Reduzido de 1000 para 500
                # Aproximar contorno por polígono
                epsilon = 0.05 * cv2.arcLength(contour, True)  # Aumentado de 0.02 para 0.05
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Verificar se é quadrilátero (4 vértices) ou próximo disso
                if len(approx) >= 4 and len(approx) <= 6:  # Permitir mais flexibilidade
                    # Verificar se é retangular
                    x, y, w, h = cv2.boundingRect(approx)
                    aspect_ratio = w / float(h)
                    
                    # Placas geralmente têm proporção entre 1.5 e 6.0 (mais flexível)
                    if 1.5 <= aspect_ratio <= 6.0:
                        plate_candidates.append(approx)
        
        return plate_candidates
    
    def extract_plate_image(self, image: np.ndarray, contour: np.ndarray) -> np.ndarray:
        """
        Extrai a imagem da placa baseada no contorno detectado
        
        Args:
            image: Imagem original
            contour: Contorno da placa
            
        Returns:
            Imagem da placa extraída
        """
        # Obter retângulo delimitador
        x, y, w, h = cv2.boundingRect(contour)
        
        # Extrair região da placa
        plate_img = image[y:y+h, x:x+w]
        
        # Redimensionar para tamanho padrão
        plate_img = cv2.resize(plate_img, (300, 100))
        
        return plate_img
    
    def simulate_plate_recognition(self, plate_image: np.ndarray) -> Optional[str]:
        """
        Simula o reconhecimento de placa (versão de demonstração)
        
        Args:
            plate_image: Imagem da placa
            
        Returns:
            Texto simulado da placa
        """
        # Em uma versão real, aqui seria usado OCR
        # Para demonstração, retornamos um texto simulado
        return "ABC1234"  # Placa simulada
    
    def process_image(self, image_path: str, show_results: bool = True) -> dict:
        """
        Processa uma imagem completa para reconhecimento de placa
        
        Args:
            image_path: Caminho para a imagem
            show_results: Se deve mostrar os resultados visualmente
            
        Returns:
            Dicionário com resultados do processamento
        """
        # Carregar imagem
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Não foi possível carregar a imagem: {image_path}")
        
        # Pré-processar
        processed = self.preprocess_image(image)
        
        # Detectar regiões de placas
        plate_regions = self.detect_plate_regions(processed)
        
        results = {
            'image_path': image_path,
            'plates_found': [],
            'total_regions': len(plate_regions)
        }
        
        # Processar cada região candidata
        for i, contour in enumerate(plate_regions):
            # Extrair imagem da placa
            plate_img = self.extract_plate_image(image, contour)
            
            # Simular reconhecimento de texto
            plate_text = self.simulate_plate_recognition(plate_img)
            
            if plate_text:
                results['plates_found'].append({
                    'text': plate_text,
                    'confidence': 0.85,  # Simulado
                    'region_id': i
                })
        
        # Mostrar resultados se solicitado
        if show_results:
            self.visualize_results(image, plate_regions, results)
        
        return results
    
    def visualize_results(self, image: np.ndarray, contours: List[np.ndarray], results: dict):
        """
        Visualiza os resultados do reconhecimento
        
        Args:
            image: Imagem original
            contours: Contornos detectados
            results: Resultados do processamento
        """
        # Criar cópia da imagem para desenhar
        result_img = image.copy()
        
        # Desenhar contornos detectados
        cv2.drawContours(result_img, contours, -1, (0, 255, 0), 2)
        
        # Adicionar texto das placas encontradas
        for i, plate_info in enumerate(results['plates_found']):
            if i < len(contours):
                # Obter posição do contorno
                x, y, w, h = cv2.boundingRect(contours[i])
                
                # Adicionar texto da placa
                cv2.putText(result_img, plate_info['text'], 
                           (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.8, (0, 255, 0), 2)
        
        # Mostrar imagem
        plt.figure(figsize=(15, 10))
        plt.imshow(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB))
        plt.title(f"Placas detectadas: {len(results['plates_found'])}")
        plt.axis('off')
        plt.show()
        
        # Mostrar estatísticas
        print(f"\n=== RESULTADOS DO RECONHECIMENTO ===")
        print(f"Imagem: {results['image_path']}")
        print(f"Regiões candidatas detectadas: {results['total_regions']}")
        print(f"Placas encontradas: {len(results['plates_found'])}")
        
        for i, plate in enumerate(results['plates_found']):
            print(f"  Placa {i+1}: {plate['text']} (Confiança: {plate['confidence']:.2f})")
    
    def create_test_image(self, plate_text: str = "ABC1234") -> str:
        """
        Cria uma imagem de teste com uma placa simulada
        
        Args:
            plate_text: Texto da placa
            
        Returns:
            Caminho para a imagem criada
        """
        # Criar imagem branca
        img = np.ones((400, 800, 3), dtype=np.uint8) * 255
        
        # Adicionar retângulo da placa (fundo cinza)
        cv2.rectangle(img, (150, 150), (650, 250), (128, 128, 128), -1)
        
        # Adicionar texto da placa
        cv2.putText(img, plate_text, (200, 200), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
        
        # Salvar imagem
        filename = f"teste_placa_{plate_text}.jpg"
        cv2.imwrite(filename, img)
        
        return filename
    
    def batch_process(self, image_folder: str) -> List[dict]:
        """
        Processa múltiplas imagens em lote
        
        Args:
            image_folder: Pasta com as imagens
            
        Returns:
            Lista de resultados para cada imagem
        """
        results = []
        supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        
        for filename in os.listdir(image_folder):
            if any(filename.lower().endswith(fmt) for fmt in supported_formats):
                image_path = os.path.join(image_folder, filename)
                try:
                    result = self.process_image(image_path, show_results=False)
                    results.append(result)
                    print(f"Processado: {filename} - {len(result['plates_found'])} placas encontradas")
                except Exception as e:
                    print(f"Erro ao processar {filename}: {e}")
        
        return results

def main():
    """Função principal para demonstração"""
    print("🚗 RECONHECEDOR DE PLACAS SIMPLIFICADO")
    print("=" * 50)
    
    # Criar reconhecedor
    recognizer = SimplePlateRecognizer()
    
    # Criar imagem de teste
    print("\n📸 Criando imagem de teste...")
    test_image = recognizer.create_test_image("XYZ1A23")
    print(f"✅ Imagem criada: {test_image}")
    
    # Processar imagem
    print(f"\n🔍 Processando imagem: {test_image}")
    results = recognizer.process_image(test_image)
    
    print(f"\n🎯 Resumo:")
    print(f"   Imagem processada: {test_image}")
    print(f"   Regiões detectadas: {results['total_regions']}")
    print(f"   Placas encontradas: {len(results['plates_found'])}")
    
    # Criar mais imagens de teste
    print("\n📸 Criando mais imagens de teste...")
    test_plates = ["ABC1234", "DEF5678", "GHI9B01"]
    
    for plate in test_plates:
        test_img = recognizer.create_test_image(plate)
        print(f"   ✅ Criada: {test_img}")
    
    print("\n🚀 Para processar todas as imagens de teste:")
    print("   recognizer.batch_process('.')")

if __name__ == "__main__":
    main()
