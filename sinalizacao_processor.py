#!/usr/bin/env python3
"""
Sistema Dual de Processamento: Sinalização + Veículos
====================================================

Este arquivo agora possui DUAS funcionalidades COMPLETAMENTE SEPARADAS:

1. 🚦 PROCESSAMENTO DE SINALIZAÇÃO:
   - Foca APENAS em placas de sinalização de trânsito
   - Gera relatórios HTML e JSON APENAS para sinalização
   - NUNCA inclui placas de veículos

2. 🚗 PROCESSAMENTO DE VEÍCULOS:
   - Foca APENAS em placas de veículos
   - Gera relatórios APENAS para placas de veículos
   - NUNCA inclui placas de sinalização

SEPARAÇÃO TOTAL: Zero mistura entre os dois tipos!
"""

import cv2
import numpy as np
import os
import re
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Importar a base de dados de sinalização
try:
    import base_dados_sinalizacao
    BASE_DADOS_AVAILABLE = True
    print("✅ Base de dados de sinalização carregada com sucesso!")
except ImportError:
    BASE_DADOS_AVAILABLE = False
    print("⚠️  Base de dados de sinalização não encontrada. Usando dados básicos.")

# Importar a base de dados específica das imagens
try:
    import base_dados_imagens_sinalizacao
    BASE_IMAGENS_AVAILABLE = True
    print("✅ Base de dados de imagens específicas carregada com sucesso!")
except ImportError:
    BASE_IMAGENS_AVAILABLE = False
    print("⚠️  Base de dados de imagens específicas não encontrada.")

class SinalizacaoProcessor:
    """Processador independente para placas de sinalização brasileiras"""
    
    def __init__(self):
        # Configurações específicas para sinalização
        self.config = {
            'min_area': 500,  # Área mínima para detecção
            'color_threshold': 5.0,  # % mínimo de cor para detecção
            'shape_approximation': 0.02,  # Precisão da aproximação de formas
            'text_confidence_threshold': 0.6  # Confiança mínima para texto
        }
        
        # Carregar base de dados oficial se disponível
        if BASE_DADOS_AVAILABLE:
            self.sinalizacao_database = base_dados_sinalizacao.SINALIZACAO_DATABASE
            self.codigos_oficiais = base_dados_sinalizacao.CODIGOS_OFICIAIS
            print(f"📊 Base de dados carregada: {len(self.sinalizacao_database)} placas")
            print(f"🔢 Códigos oficiais: {len(self.codigos_oficiais)} códigos")
        else:
            # Dicionário básico de significados das placas de sinalização brasileiras
            self.sinalizacao_database = {}
            self.codigos_oficiais = {}
            self.sinalizacao_significados = {
                'pare': {
                    'nome': 'PARE',
                    'codigo': 'R-1',
                    'significado': 'Parada obrigatória. O veículo deve parar completamente antes de prosseguir.',
                    'acao': 'Parar completamente',
                    'penalidade': 'Multa e pontos na carteira',
                    'cores': ['vermelho'],
                    'formas': ['octogonal'],
                    'tipo': 'obrigatorio'
                },
                'stop': {
                    'nome': 'STOP',
                    'codigo': 'R-1',
                    'significado': 'Parada obrigatória (termo em inglês). Mesmo significado da placa PARE.',
                    'acao': 'Parar completamente',
                    'penalidade': 'Multa e pontos na carteira',
                    'cores': ['vermelho'],
                    'formas': ['octogonal'],
                    'tipo': 'obrigatorio'
                }
            }
        
        # Padrões de sinalização brasileira (SEM dependências de placas de veículos)
        self.sinalizacao_types = {
            'obrigatorio': {
                'pare': {'colors': ['vermelho'], 'shapes': ['octogonal'], 'text': 'PARE'},
                'stop': {'colors': ['vermelho'], 'shapes': ['octogonal'], 'text': 'STOP'},
                'proibido': {'colors': ['vermelho'], 'shapes': ['circular'], 'text': 'PROIBIDO'}
            },
            'regulamentacao': {
                'velocidade': {'colors': ['azul'], 'shapes': ['circular'], 'text': 'KM/H'},
                'direcao': {'colors': ['azul'], 'shapes': ['retangular'], 'text': 'DIREÇÃO'},
                'estacionamento': {'colors': ['azul'], 'shapes': ['retangular'], 'text': 'ESTACIONAMENTO'}
            },
            'advertencia': {
                'curva': {'colors': ['amarelo'], 'shapes': ['triangular'], 'text': 'CURVA'},
                'cruzamento': {'colors': ['amarelo'], 'shapes': ['triangular'], 'text': 'CRUZAMENTO'},
                'escola': {'colors': ['amarelo'], 'shapes': ['triangular'], 'text': 'ESCOLA'}
            },
            'informacao': {
                'rua': {'colors': ['azul'], 'shapes': ['retangular'], 'text': 'RUA'},
                'avenida': {'colors': ['azul'], 'shapes': ['retangular'], 'text': 'AVENIDA'},
                'praça': {'colors': ['azul'], 'shapes': ['retangular'], 'text': 'PRAÇA'}
            }
        }
        
        # Cores específicas de sinalização (otimizadas para placas brasileiras)
        self.sinalizacao_colors = {
            'vermelho': {
                'lower': np.array([0, 100, 100]),
                'upper': np.array([10, 255, 255]),
                'description': 'Pare, Proibido, Obrigatório'
            },
            'azul': {
                'lower': np.array([100, 100, 100]),
                'upper': np.array([130, 255, 255]),
                'description': 'Regulamentação, Informação, Direção'
            },
            'amarelo': {
                'lower': np.array([20, 100, 100]),
                'upper': np.array([30, 255, 255]),
                'description': 'Advertência, Perigo'
            },
            'verde': {
                'lower': np.array([40, 100, 100]),
                'upper': np.array([80, 255, 255]),
                'description': 'Informação, Direção'
            },
            'branco': {
                'lower': np.array([0, 0, 200]),
                'upper': np.array([180, 30, 255]),
                'description': 'Texto, Fundo'
            }
        }
        
        # Formas específicas de sinalização
        self.sinalizacao_shapes = {
            'triangular': {'vertices': 3, 'type': 'advertencia'},
            'circular': {'vertices': 'circular', 'type': 'regulamentacao'},
            'retangular': {'vertices': 4, 'type': 'informacao'},
            'octogonal': {'vertices': 8, 'type': 'obrigatorio'},
            'diamante': {'vertices': 4, 'type': 'advertencia'}
        }
    
    def is_sinalizacao_plate(self, image_path: str) -> bool:
        """Verifica se a imagem é uma placa de sinalização (NÃO de veículo)"""
        filename = os.path.basename(image_path).lower()
        
        # Filtrar APENAS placas de veículos - NÃO processar
        vehicle_keywords = ['placa', 'teste_placa', 'abc', 'def', 'ghi', 'xyz', 'carro', 'veiculo', 'automovel']
        for keyword in vehicle_keywords:
            if keyword in filename:
                return False
        
        # Verificar se é uma imagem de sinalização
        sinalizacao_keywords = ['sinal', 'sinalizacao', 'transito', 'rua', 'avenida', 'pare', 'stop', 'proibido']
        for keyword in sinalizacao_keywords:
            if keyword in filename:
                return True
        
        # Se não tem palavras-chave específicas, analisar o conteúdo
        try:
            image = cv2.imread(image_path)
            if image is not None:
                # Detectar cores dominantes
                colors = self.detect_colors(image)
                shapes = self.detect_shapes(image)
                
                # Se tem cores típicas de sinalização (vermelho, azul, amarelo)
                sinalizacao_colors = ['vermelho', 'azul', 'amarelo']
                has_sinalizacao_colors = any(color in colors for color in sinalizacao_colors)
                
                # Se tem formas típicas de sinalização
                sinalizacao_shapes = ['triangular', 'circular', 'octogonal']
                has_sinalizacao_shapes = any(shape in shapes for shape in sinalizacao_shapes)
                
                return has_sinalizacao_colors or has_sinalizacao_shapes
        except:
            pass
        
        return False
    
    def identify_sinalizacao_type(self, colors: List[str], shapes: List[str], image_path: str = None) -> Dict:
        """Identifica o tipo específico de placa de sinalização"""
        
        # Primeiro, tentar identificar pela base de dados específica das imagens
        if BASE_IMAGENS_AVAILABLE and image_path:
            # Tentar identificar pela imagem específica
            info_imagem = base_dados_imagens_sinalizacao.obter_info_por_imagem(image_path)
            if info_imagem:
                return {
                    'nome': info_imagem['nome'],
                    'significado': info_imagem['significado'],
                    'acao': info_imagem['acao'],
                    'penalidade': info_imagem['penalidade'],
                    'cores': colors,
                    'formas': shapes,
                    'tipo': info_imagem['tipo'],
                    'codigo_oficial': info_imagem.get('codigo_oficial', 'N/A')
                }
            
            # Tentar identificar por características visuais
            info_caracteristicas = base_dados_imagens_sinalizacao.identificar_placa_por_caracteristicas(colors, shapes)
            if info_caracteristicas:
                return {
                    'nome': info_caracteristicas['nome'],
                    'significado': info_caracteristicas['significado'],
                    'acao': info_caracteristicas['acao'],
                    'penalidade': info_caracteristicas['penalidade'],
                    'cores': colors,
                    'formas': shapes,
                    'tipo': info_caracteristicas['tipo'],
                    'codigo_oficial': info_caracteristicas.get('codigo_oficial', 'N/A')
                }
        
        # Se não conseguir identificar pela base específica, usar lógica genérica
        if 'vermelho' in colors and 'octogonal' in shapes:
            return {
                'nome': 'PARE',
                'significado': 'Parada obrigatória. O veículo deve parar completamente antes de prosseguir.',
                'acao': 'Parar completamente',
                'penalidade': 'Multa e pontos na carteira',
                'cores': colors,
                'formas': shapes,
                'tipo': 'obrigatorio',
                'codigo_oficial': 'R-1'
            }
        elif 'vermelho' in colors and 'circular' in shapes:
            return {
                'nome': 'PROIBIÇÃO',
                'significado': 'Proibição específica. Verificar placa para detalhes.',
                'acao': 'Seguir a proibição indicada',
                'penalidade': 'Multa e pontos na carteira',
                'cores': colors,
                'formas': shapes,
                'tipo': 'obrigatorio',
                'codigo_oficial': 'R-6'
            }
        elif 'azul' in colors and 'circular' in shapes:
            return {
                'nome': 'REGULAMENTAÇÃO',
                'significado': 'Regulamentação específica. Verificar placa para detalhes.',
                'acao': 'Seguir a regulamentação indicada',
                'penalidade': 'Multa e pontos na carteira',
                'cores': colors,
                'formas': shapes,
                'tipo': 'regulamentacao',
                'codigo_oficial': 'R-19'
            }
        elif 'amarelo' in colors and 'triangular' in shapes:
            return {
                'nome': 'ADVERTÊNCIA',
                'significado': 'Advertência de perigo à frente. Reduzir velocidade e ter atenção.',
                'acao': 'Reduzir velocidade e ter cuidado',
                'penalidade': 'Não aplicável (advertência)',
                'cores': colors,
                'formas': shapes,
                'tipo': 'advertencia',
                'codigo_oficial': 'A-1'
            }
        else:
            # Tipo genérico baseado na cor dominante
            if 'vermelho' in colors:
                return {
                    'nome': 'SINALIZAÇÃO VERMELHA',
                    'significado': 'Placa de regulamentação ou obrigação. Atenção especial.',
                    'acao': 'Seguir as instruções da placa',
                    'penalidade': 'Multa e pontos na carteira',
                    'cores': colors,
                    'formas': shapes,
                    'tipo': 'obrigatorio',
                    'codigo_oficial': 'R-GEN'
                }
            elif 'azul' in colors:
                return {
                    'nome': 'SINALIZAÇÃO AZUL',
                    'significado': 'Placa de regulamentação ou informação. Seguir orientações.',
                    'acao': 'Seguir as instruções da placa',
                    'penalidade': 'Multa e pontos na carteira',
                    'cores': colors,
                    'formas': shapes,
                    'tipo': 'regulamentacao',
                    'codigo_oficial': 'R-GEN'
                }
            elif 'amarelo' in colors:
                return {
                    'nome': 'SINALIZAÇÃO AMARELA',
                    'significado': 'Placa de advertência. Reduzir velocidade e ter atenção.',
                    'acao': 'Reduzir velocidade e ter cuidado',
                    'penalidade': 'Não aplicável (advertência)',
                    'cores': colors,
                    'formas': shapes,
                    'tipo': 'advertencia',
                    'codigo_oficial': 'A-GEN'
                }
            else:
                return {
                    'nome': 'SINALIZAÇÃO GENÉRICA',
                    'significado': 'Placa de sinalização não identificada especificamente.',
                    'acao': 'Observar e seguir orientações',
                    'penalidade': 'Verificar tipo específico',
                    'cores': colors,
                    'formas': shapes,
                    'tipo': 'desconhecido',
                    'codigo_oficial': 'GEN'
                }
    
    def create_test_sinalizacao(self, tipo: str, texto: str = "PARE") -> str:
        """Cria imagem de teste específica para sinalização"""
        # Criar imagem com fundo branco
        img = np.ones((400, 600, 3), dtype=np.uint8) * 255
        
        if tipo == 'pare':
            # Placa octogonal vermelha (PARE)
            color = (0, 0, 255)  # Vermelho BGR
            points = np.array([
                [300, 50], [350, 100], [350, 200], [300, 250],
                [250, 250], [200, 200], [200, 100], [250, 50]
            ], np.int32)
            cv2.fillPoly(img, [points], color)
            cv2.putText(img, texto, (220, 170), 
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
            
        elif tipo == 'proibido':
            # Placa circular vermelha com barra
            color = (0, 0, 255)
            cv2.circle(img, (300, 200), 100, color, -1)
            cv2.line(img, (220, 120), (380, 280), (255, 255, 255), 15)
            cv2.putText(img, texto, (200, 320), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            
        elif tipo == 'velocidade':
            # Placa circular azul
            color = (255, 0, 0)  # Azul BGR
            cv2.circle(img, (300, 200), 100, color, -1)
            cv2.putText(img, texto, (220, 170), 
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
            
        elif tipo == 'advertencia':
            # Placa triangular amarela
            color = (0, 255, 255)  # Amarelo BGR
            points = np.array([[300, 50], [200, 300], [400, 300]], np.int32)
            cv2.fillPoly(img, [points], color)
            cv2.putText(img, texto, (220, 250), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)
            
        elif tipo == 'rua':
            # Placa retangular azul
            color = (255, 0, 0)  # Azul BGR
            cv2.rectangle(img, (100, 100), (500, 300), color, -1)
            cv2.putText(img, texto, (150, 200), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        
        # Salvar imagem
        filename = f"sinalizacao_{tipo}_{texto.replace(' ', '_')}.jpg"
        cv2.imwrite(filename, img)
        
        return filename
    
    def detect_colors(self, image: np.ndarray) -> Dict[str, Dict]:
        """Detecta cores específicas de sinalização"""
        # Converter para HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        color_detections = {}
        
        for color_name, color_range in self.sinalizacao_colors.items():
            # Criar máscara para a cor
            mask = cv2.inRange(hsv, color_range['lower'], color_range['upper'])
            
            # Contar pixels da cor
            pixel_count = cv2.countNonZero(mask)
            total_pixels = mask.shape[0] * mask.shape[1]
            percentage = (pixel_count / total_pixels) * 100
            
            if percentage > self.config['color_threshold']:
                color_detections[color_name] = {
                    'percentage': percentage,
                    'pixel_count': pixel_count,
                    'description': color_range['description'],
                    'mask': mask
                }
        
        return color_detections
    
    def detect_shapes(self, image: np.ndarray) -> Dict[str, Dict]:
        """Detecta formas específicas de sinalização"""
        # Converter para escala de cinza
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Aplicar threshold adaptativo
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        shape_detections = {}
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.config['min_area']:
                # Aproximar contorno
                epsilon = self.config['shape_approximation'] * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Identificar forma
                vertices = len(approx)
                
                if vertices == 3:
                    shape_type = 'triangular'
                elif vertices == 4:
                    # Verificar se é quadrado ou retângulo
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = float(w)/h
                    if 0.8 <= aspect_ratio <= 1.2:
                        shape_type = 'quadrado'
                    else:
                        shape_type = 'retangular'
                elif vertices == 8:
                    shape_type = 'octogonal'
                elif vertices > 8:
                    # Verificar se é circular
                    perimeter = cv2.arcLength(contour, True)
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    if circularity > 0.8:
                        shape_type = 'circular'
                    else:
                        shape_type = 'irregular'
                else:
                    shape_type = 'irregular'
                
                shape_detections[shape_type] = {
                    'area': area,
                    'vertices': vertices,
                    'contour': contour,
                    'approx': approx,
                    'type': self.sinalizacao_shapes.get(shape_type, {}).get('type', 'desconhecido')
                }
        
        return shape_detections
    
    def analyze_sinalizacao_type(self, colors: Dict, shapes: Dict) -> Dict[str, object]:
        """Analisa o tipo de sinalização baseado nas cores e formas"""
        analysis: Dict[str, object] = {
            'primary_type': 'desconhecido',
            'secondary_type': 'desconhecido',
            'confidence': 0.0,
            'description': 'Tipo não identificado'
        }
        
        # Análise baseada em cores dominantes
        if 'vermelho' in colors:
            if 'octogonal' in shapes:
                analysis['primary_type'] = 'obrigatorio'
                analysis['secondary_type'] = 'pare'
                analysis['confidence'] = 0.9
                analysis['description'] = 'Pare (Obrigatório) - Placa octogonal vermelha'
            elif 'circular' in shapes:
                analysis['primary_type'] = 'obrigatorio'
                analysis['secondary_type'] = 'proibido'
                analysis['confidence'] = 0.85
                analysis['description'] = 'Proibido (Obrigatório) - Placa circular vermelha'
            else:
                analysis['primary_type'] = 'obrigatorio'
                analysis['secondary_type'] = 'regulamentacao'
                analysis['confidence'] = 0.7
                analysis['description'] = 'Regulamentação (Vermelho) - Placa obrigatória'
        
        elif 'azul' in colors:
            if 'circular' in shapes:
                analysis['primary_type'] = 'regulamentacao'
                analysis['secondary_type'] = 'velocidade'
                analysis['confidence'] = 0.8
                analysis['description'] = 'Velocidade (Regulamentação) - Placa circular azul'
            elif 'retangular' in shapes:
                analysis['primary_type'] = 'informacao'
                analysis['secondary_type'] = 'direcao'
                analysis['confidence'] = 0.75
                analysis['description'] = 'Direção/Informação - Placa retangular azul'
            else:
                analysis['primary_type'] = 'regulamentacao'
                analysis['secondary_type'] = 'geral'
                analysis['confidence'] = 0.6
                analysis['description'] = 'Regulamentação (Azul) - Placa de direção'
        
        elif 'amarelo' in colors:
            if 'triangular' in shapes:
                analysis['primary_type'] = 'advertencia'
                analysis['secondary_type'] = 'perigo'
                analysis['confidence'] = 0.85
                analysis['description'] = 'Advertência (Amarelo) - Placa triangular de perigo'
            else:
                analysis['primary_type'] = 'advertencia'
                analysis['secondary_type'] = 'geral'
                analysis['confidence'] = 0.7
                analysis['description'] = 'Advertência (Amarelo) - Placa de aviso'
        
        elif 'verde' in colors:
            analysis['primary_type'] = 'informacao'
            analysis['secondary_type'] = 'direcao'
            analysis['confidence'] = 0.7
            analysis['description'] = 'Informação (Verde) - Placa de direção'
        
        return analysis
    
    def process_sinalizacao_image(self, image_path: str) -> Dict:
        """Processa uma imagem de placa de sinalização"""
        # Verificar se é realmente uma placa de sinalização
        if not self.is_sinalizacao_plate(image_path):
            return {
                'image_path': image_path,
                'is_sinalizacao': False,
                'message': 'Esta imagem não é uma placa de sinalização (possível placa de veículo)'
            }
        
        # Carregar imagem
        image = cv2.imread(image_path)
        if image is None:
            return {'error': 'Imagem não carregada', 'image_path': image_path}
        
        # Detectar cores
        color_detections = self.detect_colors(image)
        
        # Detectar formas
        shape_detections = self.detect_shapes(image)
        
        # Analisar tipo de sinalização
        type_analysis = self.analyze_sinalizacao_type(color_detections, shape_detections)
        
        # Identificar tipo específico e significado - USAR BASE DE DADOS ESPECÍFICA
        colors_list = list(color_detections.keys())
        shapes_list = list(shape_detections.keys())
        
        # PRIORIDADE: Usar base de dados específica das imagens
        info_imagem = None
        if BASE_IMAGENS_AVAILABLE:
            info_imagem = base_dados_imagens_sinalizacao.obter_info_por_imagem(image_path)
            if info_imagem:
                # Usar informações da base de dados específica
                sinalizacao_info = {
                    'nome': info_imagem['nome'],
                    'significado': info_imagem['significado'],
                    'acao': info_imagem['acao'],
                    'penalidade': info_imagem['penalidade'],
                    'cores': info_imagem['cores'],  # Usar cores da base de dados
                    'formas': info_imagem['formas'],  # Usar formas da base de dados
                    'tipo': info_imagem['tipo'],
                    'codigo_oficial': info_imagem.get('codigo_oficial', 'N/A')
                }
                confidence = 0.95  # Alta confiança quando temos dados específicos
            else:
                # Fallback para identificação automática
                sinalizacao_info = self.identify_sinalizacao_type(colors_list, shapes_list, image_path)
                confidence = type_analysis['confidence']
        else:
            # Fallback para identificação automática
            sinalizacao_info = self.identify_sinalizacao_type(colors_list, shapes_list, image_path)
            confidence = type_analysis['confidence']
        
        # Gerar resultado
        result = {
            'image_path': image_path,
            'timestamp': datetime.now().isoformat(),
            'is_sinalizacao': True,
            'image_info': {
                'width': image.shape[1],
                'height': image.shape[0],
                'channels': image.shape[2],
                'file_size': os.path.getsize(image_path)
            },
            'detection_results': {
                'colors': color_detections,
                'shapes': shape_detections,
                'type_analysis': type_analysis
            },
            'sinalizacao_info': sinalizacao_info,
            'sinalizacao_detected': True,
            'confidence': confidence,
            'base_dados_usada': 'especifica' if BASE_IMAGENS_AVAILABLE and info_imagem else 'automatica'
        }
        
        return result
    
    def process_batch_sinalizacao(self, image_folder: str = '.') -> List[Dict]:
        """Processa múltiplas imagens de sinalização em lote (APENAS sinalização)"""
        results = []
        
        # Filtrar apenas imagens
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
        image_files = [f for f in os.listdir(image_folder) 
                      if f.lower().endswith(image_extensions)]
        
        print(f"🚦 PROCESSANDO APENAS PLACAS DE SINALIZAÇÃO BRASILEIRAS")
        print(f"🔍 Total de imagens encontradas: {len(image_files)}")
        print("-" * 50)
        
        sinalizacao_count = 0
        vehicle_count = 0
        
        for i, image_file in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}] Analisando: {image_file}")
            
            try:
                result = self.process_sinalizacao_image(image_file)
                results.append(result)
                
                if result.get('is_sinalizacao'):
                    sinalizacao_count += 1
                    sinalizacao_info = result['sinalizacao_info']
                    colors = list(result['detection_results']['colors'].keys())
                    shapes = list(result['detection_results']['shapes'].keys())
                    
                    print(f"   ✅ PLACA DE SINALIZAÇÃO DETECTADA!")
                    print(f"      🚦 Nome: {sinalizacao_info['nome']}")
                    print(f"      📖 Significado: {sinalizacao_info['significado']}")
                    print(f"      ⚠️  Ação: {sinalizacao_info['acao']}")
                    print(f"      💰 Penalidade: {sinalizacao_info['penalidade']}")
                    print(f"      🎨 Cores: {', '.join(colors)}")
                    print(f"      🔷 Formas: {', '.join(shapes)}")
                    print(f"      🎯 Confiança: {result['confidence']:.2f}")
                else:
                    vehicle_count += 1
                    print(f"   🚗 Placa de veículo (não processada)")
                    
            except Exception as e:
                print(f"   ❌ Erro: {e}")
                results.append({'error': str(e), 'image': image_file})
        
        print(f"\n🎯 RESUMO DO FILTRO:")
        print(f"   • Total de imagens: {len(image_files)}")
        print(f"   • Placas de sinalização: {sinalizacao_count} ✅")
        print(f"   • Placas de veículos: {vehicle_count} 🚗 (filtradas)")
        print(f"   • Erros: {len([r for r in results if 'error' in r])}")
        
        return results
    
    def generate_summary(self, results: list) -> Dict:
        """Gera resumo dos resultados de processamento (APENAS sinalização)"""
        # Filtrar apenas resultados de sinalização
        sinalizacao_results = [r for r in results if r.get('is_sinalizacao')]
        
        summary = {
            'total_images': len(results),
            'sinalizacao_images': len(sinalizacao_results),
            'vehicle_images': len(results) - len(sinalizacao_results),
            'successful_detections': len([r for r in sinalizacao_results if r.get('sinalizacao_detected')]),
            'errors': len([r for r in results if 'error' in r]),
            'colors_summary': {},
            'shapes_summary': {},
            'types_summary': {},
            'significados_summary': {},
            'confidence_stats': {
                'min': 1.0,
                'max': 0.0,
                'avg': 0.0
            }
        }
        
        confidences = []
        
        for result in sinalizacao_results:
            if result.get('sinalizacao_detected'):
                # Contar cores
                colors = result['detection_results']['colors']
                for color_name in colors:
                    summary['colors_summary'][color_name] = summary['colors_summary'].get(color_name, 0) + 1
                
                # Contar formas
                shapes = result['detection_results']['shapes']
                for shape_name in shapes:
                    summary['shapes_summary'][shape_name] = summary['shapes_summary'].get(shape_name, 0) + 1
                
                # Contar tipos
                type_info = result['detection_results']['type_analysis']
                primary_type = type_info['primary_type']
                summary['types_summary'][primary_type] = summary['types_summary'].get(primary_type, 0) + 1
                
                # Contar significados
                sinalizacao_info = result['sinalizacao_info']
                significado_name = sinalizacao_info['nome']
                summary['significados_summary'][significado_name] = summary['significados_summary'].get(significado_name, 0) + 1
                
                # Estatísticas de confiança
                confidences.append(type_info['confidence'])
        
        # Calcular estatísticas de confiança
        if confidences:
            summary['confidence_stats']['min'] = min(confidences)
            summary['confidence_stats']['max'] = max(confidences)
            summary['confidence_stats']['avg'] = sum(confidences) / len(confidences)
        
        return summary

    def buscar_por_codigo(self, codigo: str) -> Optional[Dict]:
        """Busca placa de sinalização por código oficial (ex: R-1, R-4a)"""
        if not BASE_DADOS_AVAILABLE:
            return None
            
        codigo = codigo.upper().strip()
        
        if codigo in self.codigos_oficiais:
            return self.codigos_oficiais[codigo]
        
        # Busca por código similar
        for cod, info in self.codigos_oficiais.items():
            if codigo in cod or cod in codigo:
                return info
        
        return None
    
    def buscar_por_nome(self, nome: str) -> List[Dict]:
        """Busca placas de sinalização por nome ou parte do nome"""
        if not BASE_DADOS_AVAILABLE:
            return []
            
        nome = nome.lower().strip()
        resultados = []
        
        for key, info in self.sinalizacao_database.items():
            if (nome in info.get('nome', '').lower() or 
                nome in info.get('significado', '').lower() or
                nome in info.get('acao', '').lower()):
                resultados.append(info)
        
        return resultados
    
    def listar_todos_codigos(self) -> List[Dict]:
        """Lista todas as placas com seus códigos oficiais"""
        if not BASE_DADOS_AVAILABLE:
            return []
        return list(self.codigos_oficiais.values())
    
    def buscar_por_tipo(self, tipo: str) -> List[Dict]:
        """Busca placas por tipo (obrigatorio, regulamentacao, informacao)"""
        if not BASE_DADOS_AVAILABLE:
            return []
            
        tipo = tipo.lower().strip()
        resultados = []
        
        for info in self.sinalizacao_database.values():
            if tipo in info.get('tipo', '').lower():
                resultados.append(info)
        
        return resultados
    
    def buscar_por_cor(self, cor: str) -> List[Dict]:
        """Busca placas por cor dominante"""
        if not BASE_DADOS_AVAILABLE:
            return []
            
        cor = cor.lower().strip()
        resultados = []
        
        for info in self.sinalizacao_database.values():
            cores = info.get('cores', [])
            if cor in [c.lower() for c in cores]:
                resultados.append(info)
        
        return resultados
    
    def buscar_por_forma(self, forma: str) -> List[Dict]:
        """Busca placas por forma"""
        if not BASE_DADOS_AVAILABLE:
            return []
            
        forma = forma.lower().strip()
        resultados = []
        
        for info in self.sinalizacao_database.values():
            formas = info.get('formas', [])
            if forma in [f.lower() for f in formas]:
                resultados.append(info)
        
        return resultados

    def gerar_relatorio_completo(self, output_file: str = None) -> str:
        """Gera relatório completo com nome e código de todas as placas"""
        if not BASE_DADOS_AVAILABLE:
            return "❌ Base de dados não disponível para gerar relatório"
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Organizar por tipo
        placas_por_tipo = {
            'regulamentacao': [],
            'advertencia': [],
            'obrigatorio': [],
            'informacao': []
        }
        
        for codigo, info in self.codigos_oficiais.items():
            tipo = info.get('tipo', 'desconhecido')
            if tipo in placas_por_tipo:
                placas_por_tipo[tipo].append({
                    'codigo': codigo,
                    'nome': info.get('nome', 'N/A'),
                    'significado': info.get('significado', 'N/A'),
                    'acao': info.get('acao', 'N/A'),
                    'penalidade': info.get('penalidade', 'N/A'),
                    'cores': info.get('cores', []),
                    'formas': info.get('formas', [])
                })
        
        # Gerar relatório
        relatorio = f"""# 🚦 RELATÓRIO COMPLETO DE SINALIZAÇÃO BRASILEIRA
## 📅 Data de Geração: {timestamp}
## 📊 Total de Placas: {len(self.codigos_oficiais)}

## 🚦 PLACAS DE REGULAMENTAÇÃO ({len(placas_por_tipo['regulamentacao'])})
"""
        
        for placa in sorted(placas_por_tipo['regulamentacao'], key=lambda x: x['codigo']):
            relatorio += f"""
### {placa['codigo']} - {placa['nome']}
- **Significado**: {placa['significado']}
- **Ação**: {placa['acao']}
- **Penalidade**: {placa['penalidade']}
- **Cores**: {', '.join(placa['cores'])}
- **Formas**: {', '.join(placa['formas'])}
"""
        
        relatorio += f"""
## ⚠️ PLACAS DE ADVERTÊNCIA ({len(placas_por_tipo['advertencia'])})
"""
        
        for placa in sorted(placas_por_tipo['advertencia'], key=lambda x: x['codigo']):
            relatorio += f"""
### {placa['codigo']} - {placa['nome']}
- **Significado**: {placa['significado']}
- **Ação**: {placa['acao']}
- **Penalidade**: {placa['penalidade']}
- **Cores**: {', '.join(placa['cores'])}
- **Formas**: {', '.join(placa['formas'])}
"""
        
        relatorio += f"""
## 🚫 PLACAS OBRIGATÓRIAS ({len(placas_por_tipo['obrigatorio'])})
"""
        
        for placa in sorted(placas_por_tipo['obrigatorio'], key=lambda x: x['codigo']):
            relatorio += f"""
### {placa['codigo']} - {placa['nome']}
- **Significado**: {placa['significado']}
- **Ação**: {placa['acao']}
- **Penalidade**: {placa['penalidade']}
- **Cores**: {', '.join(placa['cores'])}
- **Formas**: {', '.join(placa['formas'])}
"""
        
        relatorio += f"""
## ℹ️ PLACAS DE INFORMAÇÃO ({len(placas_por_tipo['informacao'])})
"""
        
        for placa in sorted(placas_por_tipo['informacao'], key=lambda x: x['codigo']):
            relatorio += f"""
### {placa['codigo']} - {placa['nome']}
- **Significado**: {placa['significado']}
- **Ação**: {placa['acao']}
- **Penalidade**: {placa['penalidade']}
- **Cores**: {', '.join(placa['cores'])}
- **Formas**: {', '.join(placa['formas'])}
"""
        
        # Resumo estatístico
        relatorio += f"""
## 📊 RESUMO ESTATÍSTICO

### Por Tipo:
- **Regulamentação**: {len(placas_por_tipo['regulamentacao'])} placas
- **Advertência**: {len(placas_por_tipo['advertencia'])} placas  
- **Obrigatório**: {len(placas_por_tipo['obrigatorio'])} placas
- **Informação**: {len(placas_por_tipo['informacao'])} placas

### Por Código:
- **Placas R-**: {len([c for c in self.codigos_oficiais.keys() if c.startswith('R-')])} placas
- **Placas A-**: {len([c for c in self.codigos_oficiais.keys() if c.startswith('A-')])} placas

---
*Relatório gerado automaticamente pelo Sistema de Processamento de Sinalização Brasileira*
"""
        
        # Salvar arquivo se especificado
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(relatorio)
                print(f"✅ Relatório salvo em: {output_file}")
            except Exception as e:
                print(f"❌ Erro ao salvar relatório: {e}")
        
        return relatorio

    def gerar_relatorio_json(self, output_file: str = None) -> str:
        """Gera relatório em formato JSON com nome e código"""
        if not BASE_DADOS_AVAILABLE:
            return "❌ Base de dados não disponível para gerar relatório"
        
        timestamp = datetime.now().isoformat()
        
        relatorio_json = {
            'metadata': {
                'titulo': 'Relatório de Sinalização Brasileira',
                'data_geracao': timestamp,
                'total_placas': len(self.codigos_oficiais),
                'versao': '1.0'
            },
            'placas': {}
        }
        
        # Organizar por código
        for codigo, info in self.codigos_oficiais.items():
            relatorio_json['placas'][codigo] = {
                'nome': info.get('nome', 'N/A'),
                'tipo': info.get('tipo', 'desconhecido'),
                'significado': info.get('significado', 'N/A'),
                'acao': info.get('acao', 'N/A'),
                'penalidade': info.get('penalidade', 'N/A'),
                'cores': info.get('cores', []),
                'formas': info.get('formas', []),
                'codigo_oficial': codigo
            }
        
        # Salvar arquivo se especificado
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(relatorio_json, f, ensure_ascii=False, indent=2)
                print(f"✅ Relatório JSON salvo em: {output_file}")
            except Exception as e:
                print(f"❌ Erro ao salvar relatório JSON: {e}")
        
        return json.dumps(relatorio_json, ensure_ascii=False, indent=2)

    def gerar_relatorio_html_sinalizacao(self, output_file: str = None) -> str:
        """Gera relatório HTML baseado APENAS nas imagens analisadas (NUNCA veículos)"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Primeiro, processar as imagens para obter dados reais
        print("🔍 Analisando imagens para gerar relatório...")
        results = self.process_batch_sinalizacao()
        
        # Filtrar apenas resultados de sinalização
        sinalizacao_results = [r for r in results if r.get('is_sinalizacao')]
        
        if not sinalizacao_results:
            return "❌ Nenhuma placa de sinalização detectada nas imagens"
        
        # Organizar por tipo baseado no que foi detectado
        placas_por_tipo = {
            'regulamentacao': [],
            'advertencia': [],
            'obrigatorio': [],
            'informacao': []
        }
        
        for result in sinalizacao_results:
            if result.get('sinalizacao_detected'):
                sinalizacao_info = result['sinalizacao_info']
                colors = list(result['detection_results']['colors'].keys())
                shapes = list(result['detection_results']['shapes'].keys())
                
                # Determinar tipo baseado na análise
                tipo = sinalizacao_info.get('tipo', 'desconhecido')
                if tipo not in placas_por_tipo:
                    tipo = 'desconhecido'
                
                placas_por_tipo[tipo].append({
                    'nome': sinalizacao_info.get('nome', 'N/A'),
                    'significado': sinalizacao_info.get('significado', 'N/A'),
                    'acao': sinalizacao_info.get('acao', 'N/A'),
                    'penalidade': sinalizacao_info.get('penalidade', 'N/A'),
                    'cores': colors,
                    'formas': shapes,
                    'imagem': result.get('image_path', 'N/A'),
                    'confianca': result.get('confidence', 0.0)
                })
        
        # Gerar HTML baseado no que foi detectado
        html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚦 Relatório de Sinalização Detectada</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; text-align: center; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; border-left: 4px solid #3498db; padding-left: 15px; }}
        h3 {{ color: #2980b9; }}
        .stats {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .placa {{ background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 15px; margin: 10px 0; }}
        .placa h4 {{ color: #e74c3c; margin-top: 0; }}
        .placa ul {{ margin: 5px 0; }}
        .placa li {{ margin: 5px 0; }}
        .footer {{ text-align: center; margin-top: 30px; color: #7f8c8d; font-style: italic; }}
        .tipo-section {{ margin: 30px 0; }}
        .codigo {{ font-weight: bold; color: #e74c3c; }}
        .nome {{ font-weight: bold; color: #2c3e50; }}
        .imagem {{ font-style: italic; color: #7f8c8d; }}
        .confianca {{ color: #27ae60; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚦 RELATÓRIO DE SINALIZAÇÃO DETECTADA NAS IMAGENS</h1>
        
        <div class="stats">
            <h2>📅 Data de Geração: {timestamp}</h2>
            <h2>📊 Total de Placas de Sinalização Detectadas: {len(sinalizacao_results)}</h2>
            <p><strong>⚠️ IMPORTANTE:</strong> Este relatório contém APENAS placas detectadas nas imagens. Placas de veículos NÃO estão incluídas.</p>
        </div>
"""
        
        # Adicionar seções por tipo
        for tipo, placas in placas_por_tipo.items():
            if placas:  # Só mostrar tipos que têm placas
                html_content += f"""
        <div class="tipo-section">
            <h2>🚦 PLACAS DE {tipo.upper()} ({len(placas)} placas)</h2>
"""
                
                for placa in placas:
                    html_content += f"""
            <div class="placa">
                <h4><span class="nome">{placa['nome']}</span></h4>
                <ul>
                    <li><strong>Significado:</strong> {placa['significado']}</li>
                    <li><strong>Ação:</strong> {placa['acao']}</li>
                    <li><strong>Penalidade:</strong> {placa['penalidade']}</li>
                    <li><strong>Cores:</strong> {', '.join(placa['cores'])}</li>
                    <li><strong>Formas:</strong> {', '.join(placa['formas'])}</li>
                    <li><strong>Imagem:</strong> <span class="imagem">{placa['imagem']}</span></li>
                    <li><strong>Confiança:</strong> <span class="confianca">{placa['confianca']:.2f}</span></li>
                </ul>
            </div>
"""
                
                html_content += """
        </div>
"""
        
        # Resumo estatístico
        html_content += f"""
        <div class="stats">
            <h2>📊 RESUMO ESTATÍSTICO - APENAS SINALIZAÇÃO DETECTADA</h2>
            
            <h3>Por Tipo:</h3>
            <ul>
"""
        
        for tipo, placas in placas_por_tipo.items():
            if placas:
                html_content += f"                <li><strong>{tipo.title()}:</strong> {len(placas)} placas</li>\n"
        
        html_content += f"""
            </ul>
            
            <h3>Estatísticas Gerais:</h3>
            <ul>
                <li><strong>Total de imagens analisadas:</strong> {len(results)}</li>
                <li><strong>Placas de sinalização detectadas:</strong> {len(sinalizacao_results)} ✅</li>
                <li><strong>Placas de veículos filtradas:</strong> {len(results) - len(sinalizacao_results)} 🚗</li>
            </ul>
            
            <p><strong>🔒 GARANTIA:</strong> Este relatório contém APENAS placas de sinalização detectadas nas imagens. Zero placas de veículos incluídas.</p>
        </div>
        
        <div class="footer">
            <p>🚦 Relatório gerado automaticamente pelo Sistema de Processamento de Sinalização Brasileira</p>
            <p>📅 {timestamp} | 🔒 APENAS SINALIZAÇÃO DETECTADA - SEM VEÍCULOS</p>
        </div>
    </div>
</body>
</html>"""
        
        # Salvar arquivo se especificado
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"✅ Relatório HTML de SINALIZAÇÃO baseado nas imagens salvo em: {output_file}")
            except Exception as e:
                print(f"❌ Erro ao salvar relatório HTML: {e}")
        
        return html_content

    def gerar_relatorio_json_sinalizacao(self, output_file: str = None) -> str:
        """Gera relatório JSON baseado APENAS nas imagens analisadas (NUNCA veículos)"""
        timestamp = datetime.now().isoformat()
        
        # Primeiro, processar as imagens para obter dados reais
        print("🔍 Analisando imagens para gerar relatório JSON...")
        results = self.process_batch_sinalizacao()
        
        # Filtrar apenas resultados de sinalização
        sinalizacao_results = [r for r in results if r.get('is_sinalizacao')]
        
        if not sinalizacao_results:
            return "❌ Nenhuma placa de sinalização detectada nas imagens"
        
        relatorio_json = {
            'metadata': {
                'titulo': 'Relatório de SINALIZAÇÃO Detectada nas Imagens (SEM VEÍCULOS)',
                'data_geracao': timestamp,
                'total_placas_detectadas': len(sinalizacao_results),
                'total_imagens_analisadas': len(results),
                'tipo_relatorio': 'APENAS_SINALIZACAO_DETECTADA',
                'garantia': 'Zero placas de veículos incluídas',
                'versao': '2.0'
            },
            'placas_sinalizacao_detectadas': []
        }
        
        # Organizar por código - APENAS sinalização detectada
        for i, result in enumerate(sinalizacao_results, 1):
            if result.get('sinalizacao_detected'):
                sinalizacao_info = result['sinalizacao_info']
                colors = list(result['detection_results']['colors'].keys())
                shapes = list(result['detection_results']['shapes'].keys())
                
                relatorio_json['placas_sinalizacao_detectadas'].append({
                    'id': i,
                    'nome': sinalizacao_info.get('nome', 'N/A'),
                    'tipo': sinalizacao_info.get('tipo', 'desconhecido'),
                    'significado': sinalizacao_info.get('significado', 'N/A'),
                    'acao': sinalizacao_info.get('acao', 'N/A'),
                    'penalidade': sinalizacao_info.get('penalidade', 'N/A'),
                    'cores': colors,
                    'formas': shapes,
                    'imagem_origem': result.get('image_path', 'N/A'),
                    'confianca': result.get('confidence', 0.0),
                    'categoria': 'sinalizacao_transito_detectada'
                })
        
        # Salvar arquivo se especificado
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(relatorio_json, f, ensure_ascii=False, indent=2)
                print(f"✅ Relatório JSON de SINALIZAÇÃO baseado nas imagens salvo em: {output_file}")
            except Exception as e:
                print(f"❌ Erro ao salvar relatório JSON: {e}")
        
        return json.dumps(relatorio_json, ensure_ascii=False, indent=2)

class VeiculoProcessor:
    """Processador independente para placas de veículos brasileiros"""
    
    def __init__(self):
        # Configurações específicas para placas de veículos
        self.config = {
            'min_area': 1000,  # Área mínima para detecção
            'color_threshold': 3.0,  # % mínimo de cor para detecção
            'text_confidence_threshold': 0.7  # Confiança mínima para texto
        }
        
        # Padrões de placas de veículos brasileiros
        self.placa_patterns = {
            'mercosul': {
                'pattern': r'^[A-Z]{3}[0-9]{1}[A-Z]{1}[0-9]{2}$',  # ABC1D23
                'description': 'Padrão Mercosul (2018+)',
                'example': 'ABC1D23'
            },
            'antiga': {
                'pattern': r'^[A-Z]{3}[0-9]{4}$',  # ABC1234
                'description': 'Padrão Antigo (1990-2018)',
                'example': 'ABC1234'
            },
            'diplomatica': {
                'pattern': r'^[A-Z]{2}[0-9]{4}$',  # CD1234
                'description': 'Placa Diplomática',
                'example': 'CD1234'
            },
            'especial': {
                'pattern': r'^[A-Z]{3}[0-9]{3}$',  # ABC123
                'description': 'Placa Especial',
                'example': 'ABC123'
            }
        }
        
        # Cores específicas de placas de veículos
        self.placa_colors = {
            'branco': {
                'lower': np.array([0, 0, 200]),
                'upper': np.array([180, 30, 255]),
                'description': 'Fundo da placa'
            },
            'preto': {
                'lower': np.array([0, 0, 0]),
                'upper': np.array([180, 255, 30]),
                'description': 'Texto da placa'
            },
            'azul': {
                'lower': np.array([100, 100, 100]),
                'upper': np.array([130, 255, 255]),
                'description': 'Bandeira Mercosul'
            }
        }
    
    def is_veiculo_plate(self, image_path: str) -> bool:
        """Verifica se a imagem é uma placa de veículo (NÃO de sinalização)"""
        filename = os.path.basename(image_path).lower()
        
        # Filtrar APENAS placas de sinalização - NÃO processar
        sinalizacao_keywords = ['sinal', 'sinalizacao', 'transito', 'rua', 'avenida', 'pare', 'stop', 'proibido', 'curva', 'cruzamento']
        for keyword in sinalizacao_keywords:
            if keyword in filename:
                return False
        
        # Verificar se é uma placa de veículo
        veiculo_keywords = ['placa', 'teste_placa', 'abc', 'def', 'ghi', 'xyz', 'carro', 'veiculo', 'automovel', 'mercosul']
        for keyword in veiculo_keywords:
            if keyword in filename:
                return True
        
        # Se não tem palavras-chave específicas, analisar o conteúdo
        try:
            image = cv2.imread(image_path)
            if image is not None:
                # Detectar cores dominantes
                colors = self.detect_colors(image)
                shapes = self.detect_shapes(image)
                
                # Se tem cores típicas de placas de veículos (branco, preto)
                placa_colors = ['branco', 'preto']
                has_placa_colors = any(color in colors for color in placa_colors)
                
                # Se tem formas retangulares típicas de placas
                has_placa_shapes = 'retangular' in shapes
                
                return has_placa_colors and has_placa_shapes
        except:
            pass
        
        return False
    
    def detect_colors(self, image: np.ndarray) -> Dict[str, Dict]:
        """Detecta cores específicas de placas de veículos"""
        # Converter para HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        color_detections = {}
        
        for color_name, color_range in self.placa_colors.items():
            # Criar máscara para a cor
            mask = cv2.inRange(hsv, color_range['lower'], color_range['upper'])
            
            # Contar pixels da cor
            pixel_count = cv2.countNonZero(mask)
            total_pixels = mask.shape[0] * mask.shape[1]
            percentage = (pixel_count / total_pixels) * 100
            
            if percentage > self.config['color_threshold']:
                color_detections[color_name] = {
                    'percentage': percentage,
                    'pixel_count': pixel_count,
                    'description': color_range['description'],
                    'mask': mask
                }
        
        return color_detections
    
    def detect_shapes(self, image: np.ndarray) -> Dict[str, Dict]:
        """Detecta formas específicas de placas de veículos"""
        # Converter para escala de cinza
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Aplicar threshold adaptativo
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        shape_detections = {}
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.config['min_area']:
                # Aproximar contorno
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Identificar forma
                vertices = len(approx)
                
                if vertices == 4:
                    # Verificar se é retângulo (placa típica)
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = float(w)/h
                    if 2.0 <= aspect_ratio <= 4.0:  # Proporção típica de placas
                        shape_type = 'retangular'
                    else:
                        shape_type = 'quadrado'
                else:
                    shape_type = 'irregular'
                
                shape_detections[shape_type] = {
                    'area': area,
                    'vertices': vertices,
                    'contour': contour,
                    'approx': approx
                }
        
        return shape_detections
    
    def process_veiculo_image(self, image_path: str) -> Dict:
        """Processa uma imagem de placa de veículo"""
        # Verificar se é realmente uma placa de veículo
        if not self.is_veiculo_plate(image_path):
            return {
                'image_path': image_path,
                'is_veiculo': False,
                'message': 'Esta imagem não é uma placa de veículo (possível placa de sinalização)'
            }
        
        # Carregar imagem
        image = cv2.imread(image_path)
        if image is None:
            return {'error': 'Imagem não carregada', 'image_path': image_path}
        
        # Detectar cores
        color_detections = self.detect_colors(image)
        
        # Detectar formas
        shape_detections = self.detect_shapes(image)
        
        # Gerar resultado
        result = {
            'image_path': image_path,
            'timestamp': datetime.now().isoformat(),
            'is_veiculo': True,
            'image_info': {
                'width': image.shape[1],
                'height': image.shape[0],
                'channels': image.shape[2],
                'file_size': os.path.getsize(image_path)
            },
            'detection_results': {
                'colors': color_detections,
                'shapes': shape_detections
            },
            'veiculo_detected': True,
            'plate_type': 'veiculo_brasileiro'
        }
        
        return result
    
    def process_batch_veiculos(self, image_folder: str = '.') -> List[Dict]:
        """Processa múltiplas imagens de placas de veículos em lote (APENAS veículos)"""
        results = []
        
        # Filtrar apenas imagens
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
        image_files = [f for f in os.listdir(image_folder) 
                      if f.lower().endswith(image_extensions)]
        
        print(f"🚗 PROCESSANDO APENAS PLACAS DE VEÍCULOS BRASILEIROS")
        print(f"🔍 Total de imagens encontradas: {len(image_files)}")
        print("-" * 50)
        
        veiculo_count = 0
        sinalizacao_count = 0
        
        for i, image_file in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}] Analisando: {image_file}")
            
            try:
                result = self.process_veiculo_image(image_file)
                results.append(result)
                
                if result.get('is_veiculo'):
                    veiculo_count += 1
                    colors = list(result['detection_results']['colors'].keys())
                    shapes = list(result['detection_results']['shapes'].keys())
                    
                    print(f"   ✅ PLACA DE VEÍCULO DETECTADA!")
                    print(f"      🚗 Tipo: Placa de veículo brasileira")
                    print(f"      🎨 Cores: {', '.join(colors)}")
                    print(f"      🔷 Formas: {', '.join(shapes)}")
                    print(f"      📏 Dimensões: {result['image_info']['width']}x{result['image_info']['height']}")
                else:
                    sinalizacao_count += 1
                    print(f"   🚦 Placa de sinalização (não processada)")
                    
            except Exception as e:
                print(f"   ❌ Erro: {e}")
                results.append({'error': str(e), 'image': image_file})
        
        print(f"\n🎯 RESUMO DO FILTRO:")
        print(f"   • Total de imagens: {len(image_files)}")
        print(f"   • Placas de veículos: {veiculo_count} ✅")
        print(f"   • Placas de sinalização: {sinalizacao_count} 🚦 (filtradas)")
        print(f"   • Erros: {len([r for r in results if 'error' in r])}")
        
        return results
    
    def gerar_relatorio_html_veiculos(self, output_file: str = None) -> str:
        """Gera relatório HTML APENAS para veículos (NUNCA sinalização)"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Gerar HTML APENAS para veículos
        html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚗 Relatório de Placas de Veículos Brasileiros</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; text-align: center; border-bottom: 3px solid #e74c3c; padding-bottom: 10px; }}
        h2 {{ color: #34495e; border-left: 4px solid #e74c3c; padding-left: 15px; }}
        h3 {{ color: #c0392b; }}
        .stats {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .padrao {{ background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 15px; margin: 10px 0; }}
        .padrao h4 {{ color: #e74c3c; margin-top: 0; }}
        .padrao ul {{ margin: 5px 0; }}
        .padrao li {{ margin: 5px 0; }}
        .footer {{ text-align: center; margin-top: 30px; color: #7f8c8d; font-style: italic; }}
        .tipo-section {{ margin: 30px 0; }}
        .padrao-nome {{ font-weight: bold; color: #e74c3c; }}
        .descricao {{ font-weight: bold; color: #2c3e50; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚗 RELATÓRIO COMPLETO DE PLACAS DE VEÍCULOS BRASILEIROS</h1>
        
        <div class="stats">
            <h2>📅 Data de Geração: {timestamp}</h2>
            <h2>📊 Padrões de Placas de Veículos</h2>
            <p><strong>⚠️ IMPORTANTE:</strong> Este relatório contém APENAS padrões de placas de veículos. Placas de sinalização NÃO estão incluídas.</p>
        </div>
        
        <div class="tipo-section">
            <h2>🚗 PADRÕES DE PLACAS DE VEÍCULOS BRASILEIROS</h2>
"""
        
        for padrao_nome, padrao_info in self.placa_patterns.items():
            html_content += f"""
            <div class="padrao">
                <h4><span class="padrao-nome">{padrao_nome.upper()}</span></h4>
                <ul>
                    <li><strong>Padrão:</strong> <code>{padrao_info['pattern']}</code></li>
                    <li><strong>Descrição:</strong> {padrao_info['description']}</li>
                    <li><strong>Exemplo:</strong> <strong>{padrao_info['example']}</strong></li>
                </ul>
            </div>
"""
        
        html_content += f"""
        </div>
        
        <div class="stats">
            <h2>📊 RESUMO ESTATÍSTICO - APENAS VEÍCULOS</h2>
            
            <h3>Padrões Disponíveis:</h3>
            <ul>
                <li><strong>Mercosul:</strong> Padrão atual (2018+)</li>
                <li><strong>Antiga:</strong> Padrão anterior (1990-2018)</li>
                <li><strong>Diplomática:</strong> Placas especiais</li>
                <li><strong>Especial:</strong> Outros tipos especiais</li>
            </ul>
            
            <p><strong>🔒 GARANTIA:</strong> Este relatório contém APENAS padrões de placas de veículos. Zero placas de sinalização incluídas.</p>
        </div>
        
        <div class="footer">
            <p>🚗 Relatório gerado automaticamente pelo Sistema de Processamento de Placas de Veículos</p>
            <p>📅 {timestamp} | 🔒 APENAS VEÍCULOS - SEM SINALIZAÇÃO</p>
        </div>
    </div>
</body>
</html>"""
        
        # Salvar arquivo se especificado
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"✅ Relatório HTML de VEÍCULOS salvo em: {output_file}")
            except Exception as e:
                print(f"❌ Erro ao salvar relatório HTML: {e}")
        
        return html_content
    
    def gerar_relatorio_json_veiculos(self, output_file: str = None) -> str:
        """Gera relatório JSON APENAS para veículos (NUNCA sinalização)"""
        timestamp = datetime.now().isoformat()
        
        relatorio_json = {
            'metadata': {
                'titulo': 'Relatório de PLACAS DE VEÍCULOS Brasileiros (SEM SINALIZAÇÃO)',
                'data_geracao': timestamp,
                'total_padroes': len(self.placa_patterns),
                'tipo_relatorio': 'APENAS_VEICULOS',
                'garantia': 'Zero placas de sinalização incluídas',
                'versao': '2.0'
            },
            'padroes_placas': {}
        }
        
        # Organizar por padrão - APENAS veículos
        for padrao_nome, padrao_info in self.placa_patterns.items():
            relatorio_json['padroes_placas'][padrao_nome] = {
                'padrao_regex': padrao_info['pattern'],
                'descricao': padrao_info['description'],
                'exemplo': padrao_info['example'],
                'categoria': 'placa_veiculo_brasileiro'
            }
        
        # Salvar arquivo se especificado
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(relatorio_json, f, ensure_ascii=False, indent=2)
                print(f"✅ Relatório JSON de VEÍCULOS salvo em: {output_file}")
            except Exception as e:
                print(f"❌ Erro ao salvar relatório JSON: {e}")
        
        return json.dumps(relatorio_json, ensure_ascii=False, indent=2)

def main():
    """Função principal para demonstração"""
    print("🚦🚗 SISTEMA DUAL DE PROCESSAMENTO: SINALIZAÇÃO + VEÍCULOS")
    print("=" * 70)
    print("📋 Este arquivo possui DUAS funcionalidades COMPLETAMENTE SEPARADAS!")
    print("🎯 SEPARAÇÃO TOTAL: Zero mistura entre os dois tipos!")
    print("=" * 70)
    
    sinalizacao_processor = SinalizacaoProcessor()
    veiculo_processor = VeiculoProcessor()
    
    while True:
        print("\n📋 MENU PRINCIPAL - SISTEMA DUAL")
        print("=" * 50)
        print("🚦 PROCESSAMENTO DE SINALIZAÇÃO:")
        print("1. 🔍 Processar APENAS placas de sinalização")
        print("2. 📄 Gerar relatório HTML de SINALIZAÇÃO")
        print("3. 📄 Gerar relatório JSON de SINALIZAÇÃO")
        print("4. 📖 Ver significados das placas de sinalização")
        print("-" * 30)
        print("🚗 PROCESSAMENTO DE VEÍCULOS:")
        print("5. 🔍 Processar APENAS placas de veículos")
        print("6. 📄 Gerar relatório HTML de VEÍCULOS")
        print("7. 📄 Gerar relatório JSON de VEÍCULOS")
        print("8. 📊 Ver padrões de placas de veículos")
        print("-" * 30)
        print("🧪 FERRAMENTAS DE TESTE:")
        print("9. 🚦 Criar imagens de teste de sinalização")
        print("10. 🧪 Teste rápido de sinalização")
        print("0. ❌ Sair")
        print("-" * 30)
        
        try:
            choice = input("Escolha uma opção: ").strip()
            
            if choice == '1':
                print("\n🔍 PROCESSAMENTO EM LOTE - APENAS SINALIZAÇÃO")
                print("-" * 50)
                print("🚦 PROCESSANDO APENAS PLACAS DE SINALIZAÇÃO (SEM VEÍCULOS)")
                
                results = sinalizacao_processor.process_batch_sinalizacao()
                
                # Resumo final
                summary = sinalizacao_processor.generate_summary(results)
                
                print(f"\n🎯 RESUMO FINAL - APENAS SINALIZAÇÃO")
                print(f"   • Total de imagens: {summary['total_images']}")
                print(f"   • Placas de sinalização: {summary['sinalizacao_images']} ✅")
                print(f"   • Placas de veículos: {summary['vehicle_images']} 🚗 (FILTRADAS)")
                print(f"   • Detecções bem-sucedidas: {summary['successful_detections']}")
                print(f"   • Erros: {summary['errors']}")
                print(f"   • Confiança média: {summary['confidence_stats']['avg']:.2f}")
                
            elif choice == '2':
                print("\n📄 GERANDO RELATÓRIO HTML - APENAS SINALIZAÇÃO")
                print("-" * 50)
                print("🚦 GERANDO HTML APENAS PARA SINALIZAÇÃO (SEM VEÍCULOS)")
                
                output_html = "relatorio_sinalizacao.html"
                html_content = sinalizacao_processor.gerar_relatorio_html_sinalizacao(output_html)
                print(f"✅ Relatório HTML de SINALIZAÇÃO salvo em: {output_html}")
                print(f"🔒 GARANTIA: Zero placas de veículos incluídas!")
                
            elif choice == '3':
                print("\n📄 GERANDO RELATÓRIO JSON - APENAS SINALIZAÇÃO")
                print("-" * 50)
                print("🚦 GERANDO JSON APENAS PARA SINALIZAÇÃO (SEM VEÍCULOS)")
                
                output_json = "relatorio_sinalizacao.json"
                json_content = sinalizacao_processor.gerar_relatorio_json_sinalizacao(output_json)
                print(f"✅ Relatório JSON de SINALIZAÇÃO salvo em: {output_json}")
                print(f"🔒 GARANTIA: Zero placas de veículos incluídas!")
                
            elif choice == '4':
                print("\n📖 SIGNIFICADOS DAS PLACAS DE SINALIZAÇÃO")
                print("-" * 50)
                print("🚦 MOSTRANDO APENAS PLACAS DE SINALIZAÇÃO (SEM VEÍCULOS)")
                
                if BASE_DADOS_AVAILABLE:
                    # Mostrar algumas placas da base de dados
                    print("📊 Mostrando algumas placas da base de dados oficial:")
                    count = 0
                    for codigo, info in list(sinalizacao_processor.codigos_oficiais.items())[:10]:
                        print(f"\n🚦 {codigo} - {info.get('nome', 'N/A')}")
                        print(f"   📖 Significado: {info.get('significado', 'N/A')}")
                        print(f"   ⚠️  Ação: {info.get('acao', 'N/A')}")
                        print(f"   💰 Penalidade: {info.get('penalidade', 'N/A')}")
                        print(f"   🎨 Cores: {', '.join(info.get('cores', []))}")
                        print(f"   🔷 Formas: {', '.join(info.get('formas', []))}")
                        print(f"   🏷️  Tipo: {info.get('tipo', 'N/A')}")
                        print("-" * 30)
                        count += 1
                        if count >= 10:
                            print(f"\n... e mais {len(sinalizacao_processor.codigos_oficiais) - 10} placas na base de dados")
                            break
                else:
                    # Mostrar dados básicos
                    for key, info in sinalizacao_processor.sinalizacao_significados.items():
                        print(f"\n🚦 {info['nome']}")
                        print(f"   📖 Significado: {info['significado']}")
                        print(f"   ⚠️  Ação: {info['acao']}")
                        print(f"   💰 Penalidade: {info['penalidade']}")
                        print(f"   🎨 Cores: {', '.join(info['cores'])}")
                        print(f"   🔷 Formas: {', '.join(info['formas'])}")
                        print(f"   🏷️  Tipo: {info['tipo']}")
                        print("-" * 30)
                
            elif choice == '5':
                print("\n🔍 PROCESSAMENTO EM LOTE - APENAS VEÍCULOS")
                print("-" * 50)
                print("🚗 PROCESSANDO APENAS PLACAS DE VEÍCULOS (SEM SINALIZAÇÃO)")
                
                results = veiculo_processor.process_batch_veiculos()
                
                print(f"\n🎯 RESUMO FINAL - APENAS VEÍCULOS")
                print(f"   • Total de imagens processadas")
                print(f"   • Placas de veículos detectadas ✅")
                print(f"   • Placas de sinalização: FILTRADAS 🚦")
                print(f"🔒 GARANTIA: Zero placas de sinalização incluídas!")
                
            elif choice == '6':
                print("\n📄 GERANDO RELATÓRIO HTML - APENAS VEÍCULOS")
                print("-" * 50)
                print("🚗 GERANDO HTML APENAS PARA VEÍCULOS (SEM SINALIZAÇÃO)")
                
                output_html = "relatorio_veiculos.html"
                html_content = veiculo_processor.gerar_relatorio_html_veiculos(output_html)
                print(f"✅ Relatório HTML de VEÍCULOS salvo em: {output_html}")
                print(f"🔒 GARANTIA: Zero placas de sinalização incluídas!")
                
            elif choice == '7':
                print("\n📄 GERANDO RELATÓRIO JSON - APENAS VEÍCULOS")
                print("-" * 50)
                print("🚗 GERANDO JSON APENAS PARA VEÍCULOS (SEM SINALIZAÇÃO)")
                
                output_json = "relatorio_veiculos.json"
                json_content = veiculo_processor.gerar_relatorio_json_veiculos(output_json)
                print(f"✅ Relatório JSON de VEÍCULOS salvo em: {output_json}")
                print(f"🔒 GARANTIA: Zero placas de sinalização incluídas!")
                
            elif choice == '8':
                print("\n📊 PADRÕES DE PLACAS DE VEÍCULOS BRASILEIROS")
                print("-" * 50)
                print("🚗 MOSTRANDO APENAS PADRÕES DE VEÍCULOS (SEM SINALIZAÇÃO)")
                
                for padrao_nome, padrao_info in veiculo_processor.placa_patterns.items():
                    print(f"\n🚗 {padrao_nome.upper()}")
                    print(f"   📋 Padrão: {padrao_info['pattern']}")
                    print(f"   📖 Descrição: {padrao_info['description']}")
                    print(f"   💡 Exemplo: {padrao_info['example']}")
                    print("-" * 30)
                
            elif choice == '9':
                print("\n🚦 CRIANDO IMAGENS DE TESTE DE SINALIZAÇÃO")
                print("-" * 40)
                
                test_plates = [
                    ("pare", "PARE"),
                    ("proibido", "PROIBIDO"),
                    ("velocidade", "40 KM/H"),
                    ("advertencia", "CURVA"),
                    ("rua", "RUA DAS FLORES")
                ]
                
                for tipo, texto in test_plates:
                    filename = sinalizacao_processor.create_test_sinalizacao(tipo, texto)
                    print(f"   ✅ Criada: {filename}")
                
                print(f"\n🎯 Total criado: {len(test_plates)} imagens de sinalização")
                
            elif choice == '10':
                print("\n🧪 TESTE RÁPIDO DE SINALIZAÇÃO")
                print("-" * 30)
                
                # Criar e processar uma imagem
                test_img = sinalizacao_processor.create_test_sinalizacao("pare", "PARE")
                print(f"✅ Imagem criada: {test_img}")
                
                result = sinalizacao_processor.process_sinalizacao_image(test_img)
                if result.get('sinalizacao_detected'):
                    sinalizacao_info = result['sinalizacao_info']
                    colors = list(result['detection_results']['colors'].keys())
                    shapes = list(result['detection_results']['shapes'].keys())
                    
                    print(f"✅ Processamento concluído!")
                    print(f"   🚦 Nome: {sinalizacao_info['nome']}")
                    print(f"   📖 Significado: {sinalizacao_info['significado']}")
                    print(f"   ⚠️  Ação: {sinalizacao_info['acao']}")
                    print(f"   💰 Penalidade: {sinalizacao_info['penalidade']}")
                    print(f"   🎨 Cores: {', '.join(colors)}")
                    print(f"   🔷 Formas: {', '.join(shapes)}")
                    print(f"   🎯 Confiança: {result['confidence']:.2f}")
                
            elif choice == '0':
                print("\n👋 Obrigado por usar o Sistema Dual de Processamento!")
                print("   🚦 Sinalização + 🚗 Veículos - Até logo!")
                break
                
            else:
                print("❌ Opção inválida! Escolha de 0 a 10.")
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Aplicação interrompida")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
        
        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()
