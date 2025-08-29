#!/usr/bin/env python3
"""
Sistema Simplificado de Visão Computacional para Placas de Sinalização
====================================================================

Versão otimizada que funciona com as bibliotecas disponíveis
"""

import cv2
import numpy as np
import os
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from pathlib import Path

class SimpleVisionProcessor:
    """Processador simplificado de visão computacional para placas de sinalização"""
    
    def __init__(self):
        print("🚀 Inicializando Sistema Simplificado de Visão Computacional...")
        
        # Configurações
        self.config = {
            'min_area': 5000,  # Área mínima para detecção
            'confidence_threshold': 0.3,
            'image_size': 640
        }
        
        # Base de dados de referência
        self.reference_database = self._load_reference_database()
        
        print("✅ Sistema inicializado com sucesso!")
    
    def _load_reference_database(self) -> Dict:
        """Carrega base de dados de referência para placas"""
        return {
            'PARE': {
                'codigo': 'R-1',
                'tipo': 'obrigatorio',
                'significado': 'Parada obrigatória',
                'acao': 'Parar completamente',
                'penalidade': 'Multa e pontos na carteira',
                'caracteristicas': ['octogonal', 'vermelho', 'branco']
            },
            'STOP': {
                'codigo': 'R-1',
                'tipo': 'obrigatorio',
                'significado': 'Parada obrigatória',
                'acao': 'Parar completamente',
                'penalidade': 'Multa e pontos na carteira',
                'caracteristicas': ['octogonal', 'vermelho', 'branco']
            },
            'PROIBIDO': {
                'codigo': 'R-6',
                'tipo': 'obrigatorio',
                'significado': 'Proibição específica',
                'acao': 'Seguir a proibição indicada',
                'penalidade': 'Multa e pontos na carteira',
                'caracteristicas': ['circular', 'vermelho', 'branco']
            },
            'VELOCIDADE': {
                'codigo': 'R-19',
                'tipo': 'regulamentacao',
                'significado': 'Limite de velocidade',
                'acao': 'Respeitar o limite indicado',
                'penalidade': 'Multa e pontos na carteira',
                'caracteristicas': ['circular', 'azul', 'branco']
            },
            'CURVA': {
                'codigo': 'A-1',
                'tipo': 'advertencia',
                'significado': 'Curva perigosa à frente',
                'acao': 'Reduzir velocidade e ter cuidado',
                'penalidade': 'Não aplicável (advertência)',
                'caracteristicas': ['triangular', 'amarelo', 'preto']
            }
        }
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Pré-processa imagem para melhor análise"""
        try:
            # Redimensionar para tamanho padrão
            image = cv2.resize(image, (self.config['image_size'], self.config['image_size']))
            
            # Converter para RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Aplicar filtros para redução de ruído
            image = cv2.GaussianBlur(image, (3, 3), 0)
            
            # Aumentar contraste
            lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            
            # Aplicar CLAHE no canal L
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            l = clahe.apply(l)
            
            # Reconstruir LAB
            lab = cv2.merge([l, a, b])
            image = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
            
            return image
            
        except Exception as e:
            print(f"⚠️ Erro no pré-processamento: {e}")
            # Retornar imagem original se houver erro
            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    def detect_plates(self, image: np.ndarray) -> List[Dict]:
        """Detecta placas na imagem usando análise de contornos"""
        try:
            # Converter para escala de cinza
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Aplicar threshold adaptativo
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY, 11, 2)
            
            # Detectar contornos
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            plates = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > self.config['min_area']:
                    # Aproximar contorno
                    epsilon = 0.02 * cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, epsilon, True)
                    
                    # Verificar se é uma forma válida
                    if len(approx) >= 3:
                        x, y, w, h = cv2.boundingRect(contour)
                        
                        # Extrair ROI da placa
                        roi = image[y:y+h, x:x+w]
                        
                        plates.append({
                            'bbox': [x, y, x+w, y+h],
                            'confidence': 0.7,  # Confiança padrão
                            'contour': contour,
                            'approx': approx,
                            'roi': roi,
                            'area': area
                        })
            
            return plates
            
        except Exception as e:
            print(f"⚠️ Erro na detecção: {e}")
            return []
    
    def analyze_colors(self, roi: np.ndarray) -> Dict:
        """Analisa cores dominantes na placa"""
        try:
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
            total_pixels = roi.shape[0] * roi.shape[1]
            
            for color_name, ranges in color_ranges.items():
                color_pixels = 0
                
                for lower, upper in ranges:
                    mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
                    color_pixels += cv2.countNonZero(mask)
                
                percentage = (color_pixels / total_pixels) * 100
                if percentage > 5:  # Mínimo 5% da imagem
                    color_analysis[color_name] = percentage
            
            return color_analysis
            
        except Exception as e:
            print(f"⚠️ Erro na análise de cores: {e}")
            return {}
    
    def analyze_shapes(self, roi: np.ndarray, approx: np.ndarray) -> Dict:
        """Analisa formas geométricas na placa"""
        try:
            vertices = len(approx)
            
            shape_analysis = {}
            
            if vertices == 3:
                shape_analysis['triangular'] = 1
            elif vertices == 4:
                # Verificar se é quadrado ou retângulo
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = w / h
                if 0.8 <= aspect_ratio <= 1.2:
                    shape_analysis['quadrado'] = 1
                else:
                    shape_analysis['retangular'] = 1
            elif vertices == 8:
                shape_analysis['octogonal'] = 1
            elif vertices > 8:
                # Verificar circularidade
                area = cv2.contourArea(approx)
                perimeter = cv2.arcLength(approx, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    if circularity > 0.8:
                        shape_analysis['circular'] = 1
                    else:
                        shape_analysis['irregular'] = 1
            else:
                shape_analysis['irregular'] = 1
            
            return shape_analysis
            
        except Exception as e:
            print(f"⚠️ Erro na análise de formas: {e}")
            return {}
    
    def classify_plate_type(self, colors: Dict, shapes: Dict) -> Dict:
        """Classifica o tipo de placa baseado em características visuais"""
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
                'formas': list(shapes.keys())
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
        
        # Normalizar score para 0-1
        classification['confidence'] = min(score / 100, 1.0)
        
        return classification
    
    def process_image(self, image_path: str) -> Dict:
        """Processa uma imagem completa usando visão computacional"""
        print(f"🔍 Processando: {image_path}")
        
        try:
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
                
                # Analisar cores
                colors = self.analyze_colors(plate['roi'])
                
                # Analisar formas
                shapes = self.analyze_shapes(plate['roi'], plate['approx'])
                
                # Classificar tipo
                classification = self.classify_plate_type(colors, shapes)
                
                # Combinar resultados
                plate_result = {
                    'plate_id': i + 1,
                    'bbox': plate['bbox'],
                    'detection_confidence': plate['confidence'],
                    'classification': classification,
                    'roi_size': plate['roi'].shape[:2],
                    'area': plate['area']
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
            
        except Exception as e:
            return {
                'error': f'Erro ao processar {image_path}: {str(e)}',
                'image_path': image_path
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
            result = self.process_image(str(image_file))
            results.append(result)
        
        return results
    
    def generate_report(self, results: List[Dict], output_file: str = None) -> str:
        """Gera relatório detalhado dos resultados"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Estatísticas
        total_images = len(results)
        successful_images = len([r for r in results if 'error' not in r])
        total_plates = sum([r.get('plates_detected', 0) for r in results if 'error' not in r])
        
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
**Placas detectadas**: {result.get('plates_detected', 0)}

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
- **Características**:
  - Cores: {', '.join(classification['caracteristicas']['cores'])}
  - Formas: {', '.join(classification['caracteristicas']['formas'])}
- **Área**: {plate.get('area', 0):.0f} pixels

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
    print("🚀 SISTEMA SIMPLIFICADO DE VISÃO COMPUTACIONAL PARA PLACAS DE SINALIZAÇÃO")
    print("=" * 70)
    
    # Inicializar processador
    processor = SimpleVisionProcessor()
    
    # Processar pasta de sinalização
    sinalizacao_folder = "sinalizacao"
    
    if os.path.exists(sinalizacao_folder):
        print(f"\n📁 Processando pasta: {sinalizacao_folder}")
        results = processor.process_folder(sinalizacao_folder)
        
        # Gerar relatório
        report_file = "relatorio_visao_simples.md"
        report = processor.generate_report(results, report_file)
        
        print(f"\n📊 RELATÓRIO GERADO:")
        print(f"   • Total de imagens: {len(results)}")
        print(f"   • Placas detectadas: {sum([r.get('plates_detected', 0) for r in results if 'error' not in r])}")
        print(f"   • Relatório salvo em: {report_file}")
        
    else:
        print(f"\n❌ Pasta não encontrada: {sinalizacao_folder}")
        print("💡 Certifique-se de que a pasta existe e contém imagens")

if __name__ == "__main__":
    main()
