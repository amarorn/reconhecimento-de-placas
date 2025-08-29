#!/usr/bin/env python3
"""
Sistema de Visão Computacional Integrado com Dataset MBST
========================================================

Este sistema combina visão computacional com o dataset oficial do MBST
para classificação precisa de placas de sinalização brasileiras.
"""

import cv2
import numpy as np
import os
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from pathlib import Path

class VisionWithMBST:
    """Sistema de visão computacional integrado com dataset MBST"""
    
    def __init__(self):
        print("🚀 Inicializando Sistema de Visão Computacional com MBST...")
        
        # Configurações
        self.config = {
            'min_area': 3000,
            'confidence_threshold': 0.3,
            'image_size': 640,
            'color_threshold': 3.0
        }
        
        # Carregar dataset MBST
        self.mbst_dataset = self._load_mbst_dataset()
        
        # Sistema de classificação
        self.classification_rules = self._initialize_classification_rules()
        
        print(f"✅ Dataset MBST carregado: {len(self.mbst_dataset)} placas")
        print("✅ Sistema inicializado com sucesso!")
    
    def _load_mbst_dataset(self) -> Dict:
        """Carrega o dataset oficial do MBST"""
        try:
            dataset_path = "dataset_mbst/dataset_completo_mbst.json"
            if os.path.exists(dataset_path):
                with open(dataset_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print("⚠️ Dataset MBST não encontrado, usando dados básicos")
                return self._get_basic_dataset()
        except Exception as e:
            print(f"⚠️ Erro ao carregar dataset MBST: {e}")
            return self._get_basic_dataset()
    
    def _get_basic_dataset(self) -> Dict:
        """Dataset básico de fallback"""
        return {
            "placas": {
                "R-1": {
                    "nome": "PARE",
                    "tipo": "regulamentacao",
                    "significado": "Parada obrigatória",
                    "acao": "Parar completamente",
                    "penalidade": "Multa e pontos na carteira",
                    "cores": ["vermelho", "branco"],
                    "formas": ["octogonal"]
                }
            }
        }
    
    def _initialize_classification_rules(self) -> Dict:
        """Inicializa regras de classificação baseadas no MBST"""
        return {
            'regulamentacao': {
                'cores_primarias': ['vermelho', 'azul'],
                'formas_tipicas': ['octogonal', 'circular', 'retangular'],
                'padrao': 'proibicao_obrigacao'
            },
            'advertencia': {
                'cores_primarias': ['amarelo', 'laranja'],
                'formas_tipicas': ['triangular', 'diamante'],
                'padrao': 'perigo_aviso'
            },
            'informacao': {
                'cores_primarias': ['azul', 'verde', 'branco'],
                'formas_tipicas': ['retangular', 'quadrado'],
                'padrao': 'dados_orientacao'
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
            
            # Aumentar contraste usando CLAHE
            lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            l = clahe.apply(l)
            
            # Reconstruir LAB
            lab = cv2.merge([l, a, b])
            image = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
            
            return image
            
        except Exception as e:
            print(f"⚠️ Erro no pré-processamento: {e}")
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
                        
                        # Calcular características da forma
                        shape_features = self._analyze_shape_features(contour, approx)
                        
                        plates.append({
                            'bbox': [x, y, x+w, y+h],
                            'confidence': 0.7,
                            'contour': contour,
                            'approx': approx,
                            'roi': roi,
                            'area': area,
                            'shape_features': shape_features
                        })
            
            return plates
            
        except Exception as e:
            print(f"⚠️ Erro na detecção: {e}")
            return []
    
    def _analyze_shape_features(self, contour: np.ndarray, approx: np.ndarray) -> Dict:
        """Analisa características detalhadas da forma"""
        try:
            vertices = len(approx)
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            
            # Características básicas
            features = {
                'vertices': vertices,
                'area': area,
                'perimeter': perimeter,
                'compactness': (perimeter * perimeter) / (4 * np.pi * area) if area > 0 else 0
            }
            
            # Classificação de forma
            if vertices == 3:
                features['shape_type'] = 'triangular'
                features['regularity'] = self._calculate_triangle_regularity(approx)
            elif vertices == 4:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                if 0.8 <= aspect_ratio <= 1.2:
                    features['shape_type'] = 'quadrado'
                    features['regularity'] = self._calculate_rectangle_regularity(approx)
                else:
                    features['shape_type'] = 'retangular'
                    features['regularity'] = self._calculate_rectangle_regularity(approx)
            elif vertices == 8:
                features['shape_type'] = 'octogonal'
                features['regularity'] = self._calculate_octagon_regularity(approx)
            elif vertices > 8:
                # Verificar circularidade
                circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
                if circularity > 0.8:
                    features['shape_type'] = 'circular'
                    features['regularity'] = circularity
                else:
                    features['shape_type'] = 'irregular'
                    features['regularity'] = 0.3
            else:
                features['shape_type'] = 'irregular'
                features['regularity'] = 0.2
            
            return features
            
        except Exception as e:
            print(f"⚠️ Erro na análise de forma: {e}")
            return {'shape_type': 'desconhecido', 'regularity': 0.0}
    
    def _calculate_triangle_regularity(self, approx: np.ndarray) -> float:
        """Calcula regularidade de um triângulo"""
        try:
            if len(approx) == 3:
                angles = []
                for i in range(3):
                    p1 = approx[i][0]
                    p2 = approx[(i+1)%3][0]
                    p3 = approx[(i+2)%3][0]
                    
                    v1 = p1 - p2
                    v2 = p3 - p2
                    
                    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                    cos_angle = np.clip(cos_angle, -1, 1)
                    angle = np.arccos(cos_angle)
                    angles.append(angle)
                
                ideal_angle = np.pi / 3
                angle_diff = sum(abs(angle - ideal_angle) for angle in angles)
                regularity = max(0, 1 - angle_diff / (np.pi / 2))
                
                return regularity
        except:
            pass
        return 0.5
    
    def _calculate_rectangle_regularity(self, approx: np.ndarray) -> float:
        """Calcula regularidade de um retângulo"""
        try:
            if len(approx) == 4:
                angles = []
                for i in range(4):
                    p1 = approx[i][0]
                    p2 = approx[(i+1)%4][0]
                    p3 = approx[(i+2)%4][0]
                    
                    v1 = p1 - p2
                    v2 = p3 - p2
                    
                    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                    cos_angle = np.clip(cos_angle, -1, 1)
                    angle = np.arccos(cos_angle)
                    angles.append(angle)
                
                ideal_angle = np.pi / 2
                angle_diff = sum(abs(angle - ideal_angle) for angle in angles)
                regularity = max(0, 1 - angle_diff / (np.pi / 2))
                
                return regularity
        except:
            pass
        return 0.5
    
    def _calculate_octagon_regularity(self, approx: np.ndarray) -> float:
        """Calcula regularidade de um octógono"""
        try:
            if len(approx) == 8:
                angles = []
                for i in range(8):
                    p1 = approx[i][0]
                    p2 = approx[(i+1)%8][0]
                    p3 = approx[(i+2)%8][0]
                    
                    v1 = p1 - p2
                    v2 = p3 - p2
                    
                    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                    cos_angle = np.clip(cos_angle, -1, 1)
                    angle = np.arccos(cos_angle)
                    angles.append(angle)
                
                ideal_angle = 3 * np.pi / 4
                angle_diff = sum(abs(angle - ideal_angle) for angle in angles)
                regularity = max(0, 1 - angle_diff / (np.pi / 2))
                
                return regularity
        except:
            pass
        return 0.5
    
    def analyze_colors(self, roi: np.ndarray) -> Dict:
        """Analisa cores dominantes na placa"""
        try:
            # Converter para HSV
            hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
            
            # Definir ranges de cores mais precisos
            color_ranges = {
                'vermelho': [
                    ([0, 100, 100], [10, 255, 255]),      # Vermelho baixo
                    ([160, 100, 100], [180, 255, 255])    # Vermelho alto
                ],
                'azul': [([100, 100, 100], [130, 255, 255])],
                'amarelo': [([20, 100, 100], [30, 255, 255])],
                'laranja': [([10, 100, 100], [20, 255, 255])],
                'verde': [([40, 100, 100], [80, 255, 255])],
                'branco': [([0, 0, 200], [180, 30, 255])],
                'preto': [([0, 0, 0], [180, 255, 30])],
                'cinza': [([0, 0, 50], [180, 30, 200])]
            }
            
            color_analysis = {}
            total_pixels = roi.shape[0] * roi.shape[1]
            
            for color_name, ranges in color_ranges.items():
                color_pixels = 0
                
                for lower, upper in ranges:
                    mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
                    color_pixels += cv2.countNonZero(mask)
                
                percentage = (color_pixels / total_pixels) * 100
                if percentage > self.config['color_threshold']:
                    color_analysis[color_name] = {
                        'percentage': percentage,
                        'pixel_count': color_pixels,
                        'dominance': 'primary' if percentage > 15 else 'secondary'
                    }
            
            return color_analysis
            
        except Exception as e:
            print(f"⚠️ Erro na análise de cores: {e}")
            return {}
    
    def classify_with_mbst(self, colors: Dict, shape_features: Dict) -> Dict:
        """Classifica a placa usando o dataset MBST"""
        try:
            # Sistema de pontuação baseado no MBST
            scores = {
                'regulamentacao': 0,
                'advertencia': 0,
                'informacao': 0
            }
            
            # Análise baseada em cores
            primary_colors = [color for color, info in colors.items() 
                            if info.get('dominance') == 'primary']
            
            for color in primary_colors:
                if color in ['vermelho', 'azul']:
                    scores['regulamentacao'] += 40
                elif color in ['amarelo', 'laranja']:
                    scores['advertencia'] += 35
                elif color in ['verde', 'branco']:
                    scores['informacao'] += 30
            
            # Análise baseada em formas
            shape_type = shape_features.get('shape_type', 'desconhecido')
            regularity = shape_features.get('regularity', 0)
            
            if shape_type == 'octogonal':
                scores['regulamentacao'] += 30
            elif shape_type == 'triangular':
                scores['advertencia'] += 30
            elif shape_type == 'circular':
                scores['regulamentacao'] += 20
            elif shape_type == 'retangular':
                scores['informacao'] += 25
            
            # Bônus por regularidade
            regularity_bonus = regularity * 20
            for category in scores:
                scores[category] += regularity_bonus
            
            # Determinar categoria vencedora
            best_category = max(scores, key=scores.get)
            best_score = scores[best_category]
            
            # Normalizar score para 0-1
            confidence = min(best_score / 100, 1.0)
            
            # Buscar placa mais similar no MBST
            best_match = self._find_best_mbst_match(colors, shape_features, best_category)
            
            # Classificação com MBST
            classification = {
                'tipo': best_category,
                'codigo': best_match.get('codigo', 'N/A'),
                'nome': best_match.get('nome', 'PLACA NÃO IDENTIFICADA'),
                'significado': best_match.get('significado', 'Não foi possível identificar esta placa'),
                'acao': best_match.get('acao', 'Observar e seguir orientações'),
                'penalidade': best_match.get('penalidade', 'Verificar tipo específico'),
                'confidence': confidence,
                'caracteristicas': {
                    'cores': list(colors.keys()),
                    'formas': [shape_type],
                    'regularidade': regularity,
                    'vertices': shape_features.get('vertices', 0)
                },
                'scores_detalhados': scores,
                'mbst_match': best_match.get('codigo', 'N/A'),
                'fonte': 'Dataset MBST Oficial'
            }
            
            return classification
            
        except Exception as e:
            print(f"⚠️ Erro na classificação com MBST: {e}")
            return self._get_fallback_classification()
    
    def _find_best_mbst_match(self, colors: Dict, shape_features: Dict, category: str) -> Dict:
        """Encontra a melhor correspondência no dataset MBST"""
        try:
            best_match = None
            best_score = 0
            
            for codigo, placa in self.mbst_dataset['placas'].items():
                if placa.get('tipo') == category:
                    score = 0
                    
                    # Pontuar por cores
                    placa_cores = set(placa.get('cores', []))
                    detected_colors = set(colors.keys())
                    color_match = len(placa_cores.intersection(detected_colors))
                    score += color_match * 20
                    
                    # Pontuar por formas
                    placa_formas = set(placa.get('formas', []))
                    detected_shape = shape_features.get('shape_type', '')
                    if detected_shape in placa_formas:
                        score += 30
                    
                    # Pontuar por tipo
                    if placa.get('tipo') == category:
                        score += 25
                    
                    if score > best_score:
                        best_score = score
                        best_match = {
                            'codigo': codigo,
                            'nome': placa.get('nome', ''),
                            'significado': placa.get('significado', ''),
                            'acao': placa.get('acao', ''),
                            'penalidade': placa.get('penalidade', ''),
                            'score': score
                        }
            
            return best_match if best_match else {}
            
        except Exception as e:
            print(f"⚠️ Erro ao buscar match no MBST: {e}")
            return {}
    
    def _get_fallback_classification(self) -> Dict:
        """Classificação de fallback em caso de erro"""
        return {
            'tipo': 'desconhecido',
            'codigo': 'N/A',
            'nome': 'PLACA NÃO IDENTIFICADA',
            'significado': 'Não foi possível identificar esta placa',
            'acao': 'Observar e seguir orientações',
            'penalidade': 'Verificar tipo específico',
            'confidence': 0.0,
            'caracteristicas': {
                'cores': [],
                'formas': ['desconhecido'],
                'regularidade': 0.0,
                'vertices': 0
            },
            'scores_detalhados': {},
            'mbst_match': 'N/A',
            'fonte': 'Fallback'
        }
    
    def process_image(self, image_path: str) -> Dict:
        """Processa uma imagem completa usando visão computacional com MBST"""
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
                
                # Classificar com MBST
                classification = self.classify_with_mbst(colors, plate['shape_features'])
                
                # Combinar resultados
                plate_result = {
                    'plate_id': i + 1,
                    'bbox': plate['bbox'],
                    'detection_confidence': plate['confidence'],
                    'classification': classification,
                    'roi_size': plate['roi'].shape[:2],
                    'area': plate['area'],
                    'shape_features': plate['shape_features'],
                    'color_analysis': colors
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
        mbst_matches = 0
        for result in results:
            if 'error' not in result and 'results' in result:
                for plate in result['results']:
                    conf = plate['classification']['confidence']
                    confidences.append(conf)
                    
                    if plate['classification'].get('mbst_match') != 'N/A':
                        mbst_matches += 1
        
        avg_confidence = np.mean(confidences) if confidences else 0
        
        # Relatório
        report = f"""# 🚦 RELATÓRIO DE VISÃO COMPUTACIONAL COM MBST - PLACAS DE SINALIZAÇÃO

## 📅 Data de Geração: {timestamp}
## 📚 Fonte: Dataset MBST Oficial + Visão Computacional
## 🔢 Versão: 4.0

## 📈 ESTATÍSTICAS GERAIS
- **Total de imagens**: {total_images}
- **Imagens processadas com sucesso**: {successful_images}
- **Total de placas detectadas**: {total_plates}
- **Confiança média**: {avg_confidence:.2f}
- **Matches com MBST**: {mbst_matches}/{total_plates} ({(mbst_matches/total_plates*100):.1f}%)

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
- **Código MBST**: {classification['codigo']}
- **Tipo**: {classification['tipo']}
- **Significado**: {classification['significado']}
- **Ação**: {classification['acao']}
- **Penalidade**: {classification['penalidade']}
- **Confiança**: {classification['confidence']:.2f}
- **Fonte**: {classification.get('fonte', 'N/A')}
- **Características**:
  - Cores: {', '.join(classification['caracteristicas']['cores'])}
  - Forma: {classification['caracteristicas']['formas'][0]}
  - Regularidade: {classification['caracteristicas']['regularidade']:.2f}
  - Vértices: {classification['caracteristicas']['vertices']}
- **Área**: {plate.get('area', 0):.0f} pixels
- **Scores Detalhados**:
  - Regulamentação: {classification.get('scores_detalhados', {}).get('regulamentacao', 0):.1f}
  - Advertência: {classification.get('scores_detalhados', {}).get('advertencia', 0):.1f}
  - Informação: {classification.get('scores_detalhados', {}).get('informacao', 0):.1f}

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
    print("🚀 SISTEMA DE VISÃO COMPUTACIONAL INTEGRADO COM MBST")
    print("=" * 70)
    
    # Inicializar processador
    processor = VisionWithMBST()
    
    # Processar pasta de sinalização
    sinalizacao_folder = "sinalizacao"
    
    if os.path.exists(sinalizacao_folder):
        print(f"\n📁 Processando pasta: {sinalizacao_folder}")
        results = processor.process_folder(sinalizacao_folder)
        
        # Gerar relatório
        report_file = "relatorio_visao_mbst.md"
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
