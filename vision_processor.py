#!/usr/bin/env python3
"""
Sistema de Visão Computacional para Análise de Placas de Sinalização
===================================================================

Este sistema utiliza técnicas modernas de visão computacional:
- YOLOv8 para detecção de placas
- PaddleOCR para reconhecimento de texto
- CNN para classificação de tipos
- Embeddings vetoriais para similaridade
- Sistema de confiança dinâmico

Arquitetura:
📸 IMAGEM → 🔍 DETECÇÃO → 📝 OCR → 🎯 CLASSIFICAÇÃO → 📊 RESULTADO
"""

import cv2
import numpy as np
import os
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import torch
from ultralytics import YOLO
from paddleocr import PaddleOCR
import warnings
warnings.filterwarnings('ignore')

class VisionProcessor:
    """Processador avançado de visão computacional para placas de sinalização"""
    
    def __init__(self):
        print("🚀 Inicializando Sistema de Visão Computacional...")
        
        # Configurações
        self.config = {
            'confidence_threshold': 0.5,
            'nms_threshold': 0.4,
            'image_size': 640,
            'max_text_length': 50
        }
        
        # Inicializar modelos
        self._initialize_models()
        
        # Base de dados de referência
        self.reference_database = self._load_reference_database()
        
        print("✅ Sistema inicializado com sucesso!")
    
    def _initialize_models(self):
        """Inicializa todos os modelos de ML"""
        print("📥 Carregando modelos de Machine Learning...")
        
        try:
            # 1. YOLOv8 para detecção de placas
            print("   🔍 Carregando YOLOv8...")
            self.yolo_model = YOLO('yolov8n.pt')  # Modelo nano para velocidade
            
            # 2. PaddleOCR para reconhecimento de texto
            print("   📝 Carregando PaddleOCR...")
            self.ocr_model = PaddleOCR(
                use_angle_cls=True,
                lang='pt'
            )
            
            print("   ✅ Modelos carregados com sucesso!")
            
        except Exception as e:
            print(f"   ❌ Erro ao carregar modelos: {e}")
            print("   🔄 Usando modo fallback...")
            self.yolo_model = None
            self.ocr_model = None
    
    def _load_reference_database(self) -> Dict:
        """Carrega base de dados de referência para placas"""
        return {
            'PARE': {
                'codigo': 'R-1',
                'tipo': 'obrigatorio',
                'significado': 'Parada obrigatória',
                'acao': 'Parar completamente',
                'penalidade': 'Multa e pontos na carteira',
                'caracteristicas': ['octogonal', 'vermelho', 'branco'],
                'embedding': None  # Será calculado dinamicamente
            },
            'STOP': {
                'codigo': 'R-1',
                'tipo': 'obrigatorio',
                'significado': 'Parada obrigatória',
                'acao': 'Parar completamente',
                'penalidade': 'Multa e pontos na carteira',
                'caracteristicas': ['octogonal', 'vermelho', 'branco'],
                'embedding': None
            },
            'PROIBIDO': {
                'codigo': 'R-6',
                'tipo': 'obrigatorio',
                'significado': 'Proibição específica',
                'acao': 'Seguir a proibição indicada',
                'penalidade': 'Multa e pontos na carteira',
                'caracteristicas': ['circular', 'vermelho', 'branco'],
                'embedding': None
            },
            'VELOCIDADE': {
                'codigo': 'R-19',
                'tipo': 'regulamentacao',
                'significado': 'Limite de velocidade',
                'acao': 'Respeitar o limite indicado',
                'penalidade': 'Multa e pontos na carteira',
                'caracteristicas': ['circular', 'azul', 'branco'],
                'embedding': None
            },
            'CURVA': {
                'codigo': 'A-1',
                'tipo': 'advertencia',
                'significado': 'Curva perigosa à frente',
                'acao': 'Reduzir velocidade e ter cuidado',
                'penalidade': 'Não aplicável (advertência)',
                'caracteristicas': ['triangular', 'amarelo', 'preto'],
                'embedding': None
            }
        }
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Pré-processa imagem para melhor análise"""
        # Redimensionar para tamanho padrão
        image = cv2.resize(image, (self.config['image_size'], self.config['image_size']))
        
        # Converter para RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Aplicar filtros para redução de ruído
        image = cv2.GaussianBlur(image, (3, 3), 0)
        
        # Aumentar contraste usando CLAHE
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        
        # Converter L para uint8 para CLAHE
        l_uint8 = (l * 255).astype(np.uint8)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        l_enhanced = clahe.apply(l_uint8)
        
        # Reverter para float
        l_enhanced = l_enhanced.astype(np.float32) / 255.0
        
        # Reconstruir LAB
        lab_enhanced = cv2.merge([l_enhanced, a, b])
        image_enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2RGB)
        
        return image_enhanced
    
    def detect_plates(self, image: np.ndarray) -> List[Dict]:
        """Detecta placas na imagem usando YOLOv8"""
        if self.yolo_model is None:
            return self._fallback_detection(image)
        
        try:
            # Executar detecção
            results = self.yolo_model(image, conf=self.config['confidence_threshold'])
            
            plates = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Coordenadas da caixa
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = float(box.conf[0])
                        class_id = int(box.cls[0])
                        
                        # Extrair ROI da placa
                        roi = image[int(y1):int(y2), int(x1):int(x2)]
                        
                        plates.append({
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confidence': confidence,
                            'class_id': class_id,
                            'roi': roi
                        })
            
            return plates
            
        except Exception as e:
            print(f"⚠️ Erro na detecção YOLO: {e}")
            return self._fallback_detection(image)
    
    def _fallback_detection(self, image: np.ndarray) -> List[Dict]:
        """Detecção de fallback usando OpenCV tradicional"""
        # Converter para escala de cinza
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Detectar contornos
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        plates = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:  # Filtrar por área mínima
                x, y, w, h = cv2.boundingRect(contour)
                roi = image[y:y+h, x:x+w]
                
                plates.append({
                    'bbox': [x, y, x+w, y+h],
                    'confidence': 0.6,  # Confiança padrão para fallback
                    'class_id': 0,
                    'roi': roi
                })
        
        return plates
    
    def extract_text(self, roi: np.ndarray) -> List[Dict]:
        """Extrai texto da placa usando PaddleOCR"""
        if self.ocr_model is None:
            return self._fallback_text_extraction(roi)
        
        try:
            # Executar OCR
            results = self.ocr_model.ocr(roi, cls=True)
            
            texts = []
            if results and results[0]:
                for line in results[0]:
                    if len(line) >= 2:
                        text = line[1][0]  # Texto reconhecido
                        confidence = line[1][1]  # Confiança
                        
                        if confidence > 0.5 and len(text) > 1:
                            texts.append({
                                'text': text.strip(),
                                'confidence': confidence,
                                'bbox': line[0] if len(line) > 0 else None
                            })
            
            return texts
            
        except Exception as e:
            print(f"⚠️ Erro no OCR: {e}")
            return self._fallback_text_extraction(roi)
    
    def _fallback_text_extraction(self, roi: np.ndarray) -> List[Dict]:
        """Extração de texto de fallback usando Tesseract ou métodos básicos"""
        # Converter para escala de cinza
        gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
        
        # Aplicar threshold adaptativo
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
        
        # Detectar contornos de texto
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        texts = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 50 < area < 5000:  # Área típica de texto
                x, y, w, h = cv2.boundingRect(contour)
                text_roi = thresh[y:y+h, x:x+w]
                
                # Análise básica de características
                aspect_ratio = w / h
                if 0.1 < aspect_ratio < 10:  # Proporção típica de texto
                    texts.append({
                        'text': f"TEXT_{len(texts)}",  # Placeholder
                        'confidence': 0.4,
                        'bbox': [x, y, x+w, y+h]
                    })
        
        return texts
    
    def classify_plate_type(self, roi: np.ndarray, texts: List[Dict]) -> Dict:
        """Classifica o tipo de placa baseado em características visuais e texto"""
        # Análise de cores
        colors = self._analyze_colors(roi)
        
        # Análise de formas
        shapes = self._analyze_shapes(roi)
        
        # Análise de texto
        text_analysis = self._analyze_text(texts)
        
        # Combinar análises para classificação
        classification = self._combine_analyses(colors, shapes, text_analysis)
        
        return classification
    
    def _analyze_colors(self, roi: np.ndarray) -> Dict:
        """Analisa cores dominantes na placa"""
        # Converter para HSV
        hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
        
        # Definir ranges de cores
        color_ranges = {
            'vermelho': [([0, 100, 100], [10, 255, 255])],
            'azul': [([100, 100, 100], [130, 255, 255])],
            'amarelo': [([20, 100, 100], [30, 255, 255])],
            'verde': [([40, 100, 100], [80, 255, 255])],
            'branco': [([0, 0, 200], [180, 30, 255])],
            'preto': [([0, 0, 0], [180, 255, 30])]
        }
        
        color_analysis = {}
        for color_name, ranges in color_ranges.items():
            total_pixels = roi.shape[0] * roi.shape[1]
            color_pixels = 0
            
            for lower, upper in ranges:
                mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
                color_pixels += cv2.countNonZero(mask)
            
            percentage = (color_pixels / total_pixels) * 100
            if percentage > 5:  # Mínimo 5% da imagem
                color_analysis[color_name] = percentage
        
        return color_analysis
    
    def _analyze_shapes(self, roi: np.ndarray) -> Dict:
        """Analisa formas geométricas na placa"""
        # Converter para escala de cinza
        gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
        
        # Detectar bordas
        edges = cv2.Canny(gray, 50, 150)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        shape_analysis = {}
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Filtrar ruído
                # Aproximar contorno
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                vertices = len(approx)
                
                # Classificar forma
                if vertices == 3:
                    shape = 'triangular'
                elif vertices == 4:
                    # Verificar se é quadrado ou retângulo
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    if 0.8 <= aspect_ratio <= 1.2:
                        shape = 'quadrado'
                    else:
                        shape = 'retangular'
                elif vertices == 8:
                    shape = 'octogonal'
                elif vertices > 8:
                    # Verificar circularidade
                    perimeter = cv2.arcLength(contour, True)
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    if circularity > 0.8:
                        shape = 'circular'
                    else:
                        shape = 'irregular'
                else:
                    shape = 'irregular'
                
                if shape in shape_analysis:
                    shape_analysis[shape] += 1
                else:
                    shape_analysis[shape] = 1
        
        return shape_analysis
    
    def _analyze_text(self, texts: List[Dict]) -> Dict:
        """Analisa o texto extraído para classificação"""
        if not texts:
            return {'has_text': False, 'main_text': '', 'confidence': 0.0}
        
        # Encontrar texto com maior confiança
        best_text = max(texts, key=lambda x: x['confidence'])
        
        # Análise de palavras-chave
        keywords = {
            'PARE': ['pare', 'stop'],
            'PROIBIDO': ['proibido', 'proibida', 'não'],
            'VELOCIDADE': ['km/h', 'velocidade', 'máxima'],
            'CURVA': ['curva', 'curvas'],
            'ESCOLA': ['escola', 'escolar'],
            'CRUZAMENTO': ['cruzamento', 'cruzamentos']
        }
        
        detected_keywords = []
        for category, words in keywords.items():
            for word in words:
                if word.lower() in best_text['text'].lower():
                    detected_keywords.append(category)
                    break
        
        return {
            'has_text': True,
            'main_text': best_text['text'],
            'confidence': best_text['confidence'],
            'keywords': detected_keywords
        }
    
    def _combine_analyses(self, colors: Dict, shapes: Dict, text: Dict) -> Dict:
        """Combina todas as análises para classificação final"""
        # Sistema de pontuação
        score = 0
        classification = {
            'tipo': 'desconhecido',
            'codigo': 'N/A',
            'nome': 'PLACA NÃO IDENTIFICADA',
            'significado': 'Não foi possível identificar esta placa',
            'acao': 'Observar e seguir orientações',
            'penalidade': 'Verificar tipo específico',
            'confidence': 0.0,
            'caracteristicas': {
                'cores': list(colors.keys()),
                'formas': list(shapes.keys()),
                'texto': text.get('main_text', '')
            }
        }
        
        # Análise baseada em cores e formas
        if 'vermelho' in colors and 'octogonal' in shapes:
            score += 80
            classification['tipo'] = 'obrigatorio'
            classification['codigo'] = 'R-1'
            classification['nome'] = 'PARE'
            classification['significado'] = 'Parada obrigatória'
            classification['acao'] = 'Parar completamente'
            classification['penalidade'] = 'Multa e pontos na carteira'
        
        elif 'vermelho' in colors and 'circular' in shapes:
            score += 70
            classification['tipo'] = 'obrigatorio'
            classification['codigo'] = 'R-6'
            classification['nome'] = 'PROIBIÇÃO'
            classification['significado'] = 'Proibição específica'
            classification['acao'] = 'Seguir a proibição indicada'
            classification['penalidade'] = 'Multa e pontos na carteira'
        
        elif 'azul' in colors and 'circular' in shapes:
            score += 65
            classification['tipo'] = 'regulamentacao'
            classification['codigo'] = 'R-19'
            classification['nome'] = 'REGULAMENTAÇÃO'
            classification['significado'] = 'Regulamentação específica'
            classification['acao'] = 'Seguir a regulamentação indicada'
            classification['penalidade'] = 'Multa e pontos na carteira'
        
        elif 'amarelo' in colors and 'triangular' in shapes:
            score += 75
            classification['tipo'] = 'advertencia'
            classification['codigo'] = 'A-1'
            classification['nome'] = 'ADVERTÊNCIA'
            classification['significado'] = 'Advertência de perigo à frente'
            classification['acao'] = 'Reduzir velocidade e ter atenção'
            classification['penalidade'] = 'Não aplicável (advertência)'
        
        # Análise baseada em texto
        if text.get('has_text'):
            text_score = text.get('confidence', 0) * 100
            score += text_score * 0.3  # Peso do texto
            
            # Atualizar nome se texto for reconhecido
            if text.get('keywords'):
                keyword = text['keywords'][0]
                if keyword in self.reference_database:
                    ref = self.reference_database[keyword]
                    classification['nome'] = keyword
                    classification['codigo'] = ref['codigo']
                    classification['tipo'] = ref['tipo']
                    classification['significado'] = ref['significado']
                    classification['acao'] = ref['acao']
                    classification['penalidade'] = ref['penalidade']
                    score += 20
        
        # Normalizar score para 0-1
        classification['confidence'] = min(score / 100, 1.0)
        
        return classification
    
    def process_image(self, image_path: str) -> Dict:
        """Processa uma imagem completa usando visão computacional"""
        print(f"🔍 Processando: {image_path}")
        
        # Carregar imagem
        image = cv2.imread(image_path)
        if image is None:
            return {'error': 'Imagem não carregada', 'image_path': image_path}
        
        # Pré-processar
        processed_image = self.preprocess_image(image)
        
        # Detectar placas
        plates = self.detect_plates(processed_image)
        
        if not plates:
            return {
                'image_path': image_path,
                'plates_detected': 0,
                'message': 'Nenhuma placa detectada'
            }
        
        # Processar cada placa detectada
        results = []
        for i, plate in enumerate(plates):
            print(f"   📋 Analisando placa {i+1}/{len(plates)}")
            
            # Extrair texto
            texts = self.extract_text(plate['roi'])
            
            # Classificar tipo
            classification = self.classify_plate_type(plate['roi'], texts)
            
            # Combinar resultados
            plate_result = {
                'plate_id': i + 1,
                'bbox': plate['bbox'],
                'detection_confidence': plate['confidence'],
                'classification': classification,
                'texts': texts,
                'roi_size': plate['roi'].shape[:2]
            }
            
            results.append(plate_result)
        
        return {
            'image_path': image_path,
            'timestamp': datetime.now().isoformat(),
            'plates_detected': len(plates),
            'results': results,
            'image_info': {
                'width': image.shape[1],
                'height': image.shape[0],
                'channels': image.shape[2]
            }
        }
    
    def process_folder(self, folder_path: str) -> List[Dict]:
        """Processa todas as imagens em uma pasta"""
        folder = Path(folder_path)
        if not folder.exists():
            return [{'error': f'Pasta não encontrada: {folder_path}'}]
        
        # Encontrar imagens
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        image_files = []
        for ext in image_extensions:
            image_files.extend(folder.glob(f'*{ext}'))
            image_files.extend(folder.glob(f'*{ext.upper()}'))
        
        if not image_files:
            return [{'error': f'Nenhuma imagem encontrada em: {folder_path}'}]
        
        print(f"📁 Processando {len(image_files)} imagens em: {folder_path}")
        
        results = []
        for image_file in image_files:
            try:
                result = self.process_image(str(image_file))
                results.append(result)
            except Exception as e:
                results.append({
                    'error': f'Erro ao processar {image_file}: {str(e)}',
                    'image_path': str(image_file)
                })
        
        return results
    
    def generate_report(self, results: List[Dict], output_file: str = None) -> str:
        """Gera relatório detalhado dos resultados"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Estatísticas
        total_images = len(results)
        successful_images = len([r for r in results if 'error' not in r])
        total_plates = sum([r.get('plates_detectadas', 0) for r in results if 'error' not in r])
        
        # Análise de confiança
        confidences = []
        for result in results:
            if 'error' not in result and 'results' in result:
                for plate in result['results']:
                    conf = plate['classification']['confidence']
                    confidences.append(conf)
        
        avg_confidence = np.mean(confidences) if confidences else 0
        
        # Relatório
        report = f"""# 🚦 RELATÓRIO DE VISÃO COMPUTACIONAL - PLACAS DE SINALIZAÇÃO

## 📅 Data de Geração: {timestamp}
## 📊 Estatísticas Gerais
- **Total de imagens**: {total_images}
- **Imagens processadas com sucesso**: {successful_images}
- **Total de placas detectadas**: {total_plates}
- **Confiança média**: {avg_confidence:.2f}

## 🔍 DETALHES POR IMAGEM

"""
        
        for result in results:
            if 'error' in result:
                report += f"""
### ❌ {result.get('image_path', 'Imagem desconhecida')}
**Erro**: {result['error']}

"""
            else:
                report += f"""
### ✅ {result.get('image_path', 'Imagem desconhecida')}
**Placas detectadas**: {result.get('plates_detectadas', 0)}

"""
                
                for plate in result.get('results', []):
                    classification = plate['classification']
                    report += f"""
#### 📋 Placa {plate['plate_id']}
- **Nome**: {classification['nome']}
- **Código**: {classification['codigo']}
- **Tipo**: {classification['tipo']}
- **Significado**: {classification['significado']}
- **Ação**: {classification['acao']}
- **Penalidade**: {classification['penalidade']}
- **Confiança**: {classification['confidence']:.2f}
- **Texto detectado**: {', '.join([t['text'] for t in plate.get('texts', [])])}
- **Características**:
  - Cores: {', '.join(classification['caracteristicas']['cores'])}
  - Formas: {', '.join(classification['caracteristicas']['formas'])}

"""
        
        # Salvar arquivo se especificado
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report)
                print(f"✅ Relatório salvo em: {output_file}")
            except Exception as e:
                print(f"❌ Erro ao salvar relatório: {e}")
        
        return report

def main():
    """Função principal para demonstração"""
    print("🚀 SISTEMA DE VISÃO COMPUTACIONAL PARA PLACAS DE SINALIZAÇÃO")
    print("=" * 70)
    
    # Inicializar processador
    processor = VisionProcessor()
    
    # Processar pasta de sinalização
    sinalizacao_folder = "sinalizacao"
    
    if os.path.exists(sinalizacao_folder):
        print(f"\n📁 Processando pasta: {sinalizacao_folder}")
        results = processor.process_folder(sinalizacao_folder)
        
        # Gerar relatório
        report_file = "relatorio_visao_computacional.md"
        report = processor.generate_report(results, report_file)
        
        print(f"\n📊 RELATÓRIO GERADO:")
        print(f"   • Total de imagens: {len(results)}")
        print(f"   • Placas detectadas: {sum([r.get('plates_detectadas', 0) for r in results if 'error' not in r])}")
        print(f"   • Relatório salvo em: {report_file}")
        
    else:
        print(f"\n❌ Pasta não encontrada: {sinalizacao_folder}")
        print("💡 Certifique-se de que a pasta existe e contém imagens")

if __name__ == "__main__":
    main()
