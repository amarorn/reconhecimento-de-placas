import cv2
import numpy as np
import easyocr
import re
from typing import List, Tuple, Optional
import matplotlib.pyplot as plt
from PIL import Image
import os

class PlateRecognizer:
    """
    Classe para reconhecimento de placas de trânsito usando visão computacional
    """
    
    def __init__(self, language: str = 'pt'):
        """
        Inicializa o reconhecedor de placas
        
        Args:
            language: Idioma para OCR (pt para português)
        """
        self.reader = easyocr.Reader([language], gpu=False)
        self.plate_pattern = re.compile(r'[A-Z]{3}[0-9]{4}|[A-Z]{3}[0-9]{1}[A-Z]{1}[0-9]{2}')
        
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Pré-processa a imagem para melhorar o reconhecimento
        
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
        # Detectar bordas
        edges = cv2.Canny(image, 50, 200)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filtrar contornos por área e forma
        plate_candidates = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filtrar por área mínima
            if area > 1000:
                # Aproximar contorno por polígono
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Verificar se é quadrilátero (4 vértices)
                if len(approx) == 4:
                    # Verificar se é retangular
                    x, y, w, h = cv2.boundingRect(approx)
                    aspect_ratio = w / float(h)
                    
                    # Placas geralmente têm proporção entre 2.0 e 5.5
                    if 2.0 <= aspect_ratio <= 5.5:
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
    
    def recognize_plate_text(self, plate_image: np.ndarray) -> Optional[str]:
        """
        Reconhece o texto da placa usando OCR
        
        Args:
            plate_image: Imagem da placa
            
        Returns:
            Texto reconhecido ou None
        """
        try:
            # Converter para RGB para o EasyOCR
            plate_rgb = cv2.cvtColor(plate_image, cv2.COLOR_BGR2RGB)
            
            # Realizar OCR
            results = self.reader.readtext(plate_rgb)
            
            if results:
                # Extrair texto dos resultados
                texts = [result[1] for result in results]
                confidence_scores = [result[2] for result in results]
                
                # Filtrar por padrão de placa brasileira
                for text, confidence in zip(texts, confidence_scores):
                    # Limpar texto
                    clean_text = re.sub(r'[^A-Z0-9]', '', text.upper())
                    
                    # Verificar se segue padrão de placa
                    if self.plate_pattern.match(clean_text) and confidence > 0.5:
                        return clean_text
                
                # Se não encontrou padrão exato, retornar o texto com maior confiança
                if confidence_scores:
                    best_idx = np.argmax(confidence_scores)
                    return texts[best_idx]
            
            return None
            
        except Exception as e:
            print(f"Erro no OCR: {e}")
            return None
    
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
            
            # Reconhecer texto
            plate_text = self.recognize_plate_text(plate_img)
            
            if plate_text:
                results['plates_found'].append({
                    'text': plate_text,
                    'confidence': 0.8,  # Placeholder
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
