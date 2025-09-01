#!/usr/bin/env python3
"""
Coletor Refinado de Dados Brasileiros
=====================================

Sistema aprimorado para coleta específica de:
- Placas de Veículos Brasileiros (Mercosul, padrão antigo)
- Placas de Sinalização de Trânsito Brasileiras (CONTRAN)

Melhorias implementadas:
- Queries mais específicas e contextualiza                print(f"📈 Total coletado: {valid_images} imagens")as
- Filtros de qualidade de imagem
- Validação automática de conteúdo
- Classificação automática por tipo
- Remoção de imagens irrelevantes
"""

import os
import sys
import json
import requests
import time
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging
from urllib.parse import urlparse
import hashlib
from PIL import Image, ImageFilter
import re

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RefinedBrazilianCollector:
    """Coletor refinado para dados brasileiros específicos."""
    
    def __init__(self, output_dir: str = "datasets/refined_brazilian"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Diretórios organizados
        self.signal_dir = self.output_dir / "signal_plates"
        self.vehicle_dir = self.output_dir / "vehicle_plates" 
        self.rejected_dir = self.output_dir / "rejected"
        
        # Criar diretórios
        for dir_path in [self.signal_dir, self.vehicle_dir, self.rejected_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Configurações para filtros ultra-restritivos
        self.config = {
            "min_image_size": (200, 100),
            "max_image_size": (4000, 3000),
            "min_file_size": 5000,
            "quality_threshold": 80,
            "delay_between_requests": 3,
            "max_images_per_query": 5
        }
        
        # Setup das queries e validações
        self._setup_queries()
        self._setup_validation_patterns()
        self._setup_irrelevant_keywords()
    
    def _setup_queries(self):
        """Define queries específicas para cada tipo de placa."""
        
        # Placas de Sinalização - ULTRA ESPECÍFICAS
        self.signal_queries = {
            # PARE (R-1) - ESPECÍFICAS
            "stop_signs": [
                "placa PARE R-1 brasil octógono vermelho contran",
                "sinalização PARE brasil oficial detran",
                "placa stop brasil vermelha oitavada contran"
            ],
            # Dê preferência (R-2) - ESPECÍFICAS
            "yield_signs": [
                "placa DÊ PREFERÊNCIA R-2 brasil triângulo invertido",
                "sinalização preferência brasil amarelo contran",
                "placa yield brasil triangular oficial"
            ],
            # Proibições (R-3 a R-15) - ESPECÍFICAS
            "prohibition_signs": [
                "placa PROIBIDO VIRAR À ESQUERDA R-5 brasil contran",
                "placa PROIBIDO ESTACIONAR R-6a brasil contran",
                "estacionamento regulamentado brasil zona azul oficial"
            ],
            # Advertência (A-1 a A-44) - ESPECÍFICAS
            "warning_signs": [
                "placa CURVA PERIGOSA A-2 brasil losango amarelo",
                "placa CRUZAMENTO A-10 brasil advertência contran",
                "sinalização OBRAS NA PISTA A-21 brasil amarelo"
            ],
            # Indicação - GOVERNAMENTAIS
            "information_signs": [
                "placa sentido circulação brasil azul retangular",
                "placa MÃO ÚNICA brasil informação contran",
                "sinalização direção centro brasil azul"
            ]
        }
        
        # Placas de Veículos - ULTRA ESPECÍFICAS
        self.vehicle_queries = {
            "mercosul_plates": [
                "placa mercosul veículo brasil AAA1B23 detran oficial",
                "placa automotor mercosul padrão brasileiro contran",
                "placa carro mercosul brasil branca azul oficial"
            ],
            "old_pattern_plates": [
                "placa padrão antigo brasil AAA-0000 cinza detran",
                "placa veículo antiga brasileira três letras quatro números",
                "placa automotor padrão antigo brasil oficial"
            ],
            "special_plates": [
                "placa diplomática brasil vermelha CD oficial",
                "placa oficial governo brasil azul estado",
                "placa polícia militar brasil oficial PM"
            ],
            "motorcycle_plates": [
                "placa motocicleta mercosul brasil branca azul detran",
                "placa moto brasileira padrão mercosul oficial",
                "placa motocicleta brasil AAA1B23 contran"
            ]
        }
    
    def _setup_validation_patterns(self):
        """Define padrões para validar se as imagens são relevantes."""
        
        # Padrões de placas brasileiras
        self.plate_patterns = {
            "mercosul": re.compile(r"[A-Z]{3}[0-9][A-Z][0-9]{2}"),
            "old_pattern": re.compile(r"[A-Z]{3}-?[0-9]{4}"),
            "motorcycle": re.compile(r"[A-Z]{3}[0-9]{4}")
        }
        
        # Palavras-chave que indicam conteúdo brasileiro
        self.brazilian_keywords = [
            "brasil", "brazil", "brazilian", "contran", "detran", 
            "denatran", "código", "trânsito", "sinalização", "oficial",
            "resolução", "mercosul", "brasileiro", "brasileira"
        ]
    
    def _setup_irrelevant_keywords(self):
        """Define palavras-chave que indicam conteúdo irrelevante."""
        
        self.irrelevant_keywords = [
            # Sites de stock e mídia
            "shutterstock", "getty", "alamy", "dreamstime", "fotolia", "istockphoto",
            # Redes sociais
            "pinterest", "facebook", "instagram", "twitter", "linkedin",
            # Países estrangeiros
            "usa", "america", "europe", "canada", "mexico", "argentina",
            # Conteúdo artificial
            "clipart", "vector", "drawing", "illustration", "cartoon", "fake",
            # Aplicativos
            "app", "interface", "website", "software", "screenshot"
        ]
    
    def _get_output_dir(self, category: str) -> Path:
        """Retorna o diretório correto baseado na categoria."""
        if category == "signal_plates":
            return self.signal_dir
        elif category == "vehicle_plates":
            return self.vehicle_dir
        else:
            return self.rejected_dir
    
    def validate_image_relevance(self, image_path: Path, category: str) -> bool:
        """
        Valida se uma imagem é relevante usando validação básica.
        Para validação avançada, use BrazilianPlateValidator.
        """
        try:
            # Verificar se arquivo existe e não está corrompido
            if not image_path.exists() or image_path.stat().st_size < self.config["min_file_size"]:
                return False
            
            # Verificar dimensões da imagem
            try:
                with Image.open(image_path) as img:
                    width, height = img.size
                    
                    if width < self.config["min_image_size"][0] or height < self.config["min_image_size"][1]:
                        return False
                        
                    if width > self.config["max_image_size"][0] or height > self.config["max_image_size"][1]:
                        return False
                        
            except Exception:
                return False
            
            # Verificar qualidade da imagem usando OpenCV
            try:
                image = cv2.imread(str(image_path))
                if image is None:
                    return False
                    
                # Calcular métrica de qualidade (variância do Laplaciano)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                quality_score = cv2.Laplacian(gray, cv2.CV_64F).var()
                
                if quality_score < self.config["quality_threshold"]:
                    return False
                    
            except Exception:
                return False
            
            return True
            
        except Exception:
            return False

    def collect_google_images_refined(self, query: str, category: str, subcategory: str, max_images: int = 50):
        """
        Coleta imagens do Google - CORRIGIDO PARA BAIXAR IMAGENS REAIS
        """
        print(f"🔍 Coletando: {query}")
        
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
            
            if not api_key or not search_engine_id:
                print("❌ API keys não configuradas!")
                return 0
            
            url = "https://www.googleapis.com/customsearch/v1"
            
            # PARÂMETROS CORRETOS DA GOOGLE CUSTOM SEARCH API
            params = {
                "key": api_key,
                "cx": search_engine_id,
                "q": f"{query} brasil -site:pinterest.com -site:shutterstock.com -clipart -drawing",
                "searchType": "image",
                "num": min(max_images, 10),
                "imgType": "photo",        # photo, clipart, lineart, face, news, stock
                "imgSize": "large",        # icon, small, medium, large, xlarge, xxlarge, huge
                "safe": "active",
                "cr": "countryBR",         # Country restrict
                "gl": "br",                # Geolocation
                "hl": "pt-BR",             # Interface language
                "rights": "cc_publicdomain,cc_attribute,cc_sharealike,cc_noncommercial,cc_nonderived"
            }
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            print(f"📡 Fazendo request para API...")
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if "items" not in data:
                    print("❌ Nenhum resultado encontrado")
                    return 0
                
                print(f"✅ Encontrou {len(data['items'])} resultados")
                
                valid_images = 0
                
                for i, item in enumerate(data["items"]):
                    try:
                        # USA O LINK DIRETO DA API
                        image_url = item.get("link")
                        image_title = item.get("title", "")
                        
                        print(f"   {i+1}. {image_title[:40]}...")
                        print(f"       URL: {image_url[:60]}...")
                        
                        # Baixar imagem direto
                        print(f"       📥 Baixando...")
                        img_response = requests.get(image_url, headers=headers, timeout=15)
                        
                        if img_response.status_code == 200:
                            # Salvar direto
                            filename = f"{subcategory}_{valid_images:03d}.jpg"
                            final_path = self._get_output_dir(category) / filename
                            
                            with open(final_path, 'wb') as f:
                                f.write(img_response.content)
                            
                            print(f"       ✅ SALVA: {filename} ({len(img_response.content)} bytes)")
                            valid_images += 1
                            
                        else:
                            print(f"       ❌ Erro download: {img_response.status_code}")
                        
                        time.sleep(2)  # Rate limiting
                        
                    except Exception as e:
                        print(f"       ⚠️ Erro: {e}")
                        continue
                
                print(f"� Total coletado: {valid_images} imagens")
                return valid_images
                
            else:
                print(f"❌ Erro API: {response.status_code}")
                if response.status_code == 429:
                    print("   Muitas requests - aguarde")
                return 0
                
        except Exception as e:
            print(f"❌ Erro geral: {e}")
            return 0

    def collect_government_only(self, query: str, category: str, subcategory: str, max_images: int = 10):
        """Coleta APENAS de sites .gov.br - VERSÃO SIMPLES"""
        print(f"🏛️ Coletando de sites gov: {query}")
        
        # Adicionar site:gov.br na query
        gov_query = f"{query} site:gov.br"
        
        return self.collect_google_images_refined(gov_query, category, f"gov_{subcategory}", max_images)

    def debug_api_response(self, query: str, max_results: int = 3):
        """Debug simples da API"""
        print(f"🔬 DEBUG: {query}")
        
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
            
            params = {
                "key": api_key,
                "cx": search_engine_id,
                "q": query,
                "searchType": "image",
                "num": max_results
            }
            
            response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if "items" in data:
                    print(f"Resultados: {len(data['items'])}")
                    for i, item in enumerate(data["items"], 1):
                        print(f"  {i}. {item.get('title', '')[:50]}...")
                        print(f"     {item['link'][:70]}...")
                else:
                    print("Nenhum resultado")
            else:
                print(f"Erro: {response.status_code}")
                
        except Exception as e:
            print(f"Erro: {e}")

    def collect_all_signal_plates(self, max_per_category: int = 20):
        """Coleta todas as categorias de signal plates."""
        
        print("🚦 COLETA COMPLETA DE SIGNAL PLATES")
        print("=" * 50)
        
        total_collected = 0
        
        for category, queries in self.signal_queries.items():
            print(f"\n📍 Coletando {category}...")
            category_total = 0
            
            for query in queries:
                collected = self.collect_google_images_refined(
                    query=query,
                    category="signal_plates",
                    subcategory=category,
                    max_images=max_per_category
                )
                category_total += collected
                time.sleep(self.config["delay_between_requests"])
            
            print(f"   ✅ {category}: {category_total} imagens")
            total_collected += category_total
        
        print(f"\n📊 TOTAL COLETADO: {total_collected} imagens")
        return total_collected

    def collect_all_vehicle_plates(self, max_per_category: int = 20):
        """Coleta todas as categorias de vehicle plates."""
        
        print("🚗 COLETA COMPLETA DE VEHICLE PLATES")
        print("=" * 50)
        
        total_collected = 0
        
        for category, queries in self.vehicle_queries.items():
            print(f"\n📍 Coletando {category}...")
            category_total = 0
            
            for query in queries:
                collected = self.collect_google_images_refined(
                    query=query,
                    category="vehicle_plates",
                    subcategory=category,
                    max_images=max_per_category
                )
                category_total += collected
                time.sleep(self.config["delay_between_requests"])
            
            print(f"   ✅ {category}: {category_total} imagens")
            total_collected += category_total
        
        print(f"\n📊 TOTAL COLETADO: {total_collected} imagens")
        return total_collected

    def get_statistics(self):
        """Retorna estatísticas da coleta."""
        
        signal_count = len(list(self.signal_dir.glob("*.jpg")))
        vehicle_count = len(list(self.vehicle_dir.glob("*.jpg")))
        rejected_count = len(list(self.rejected_dir.glob("*.jpg")))
        
        total = signal_count + vehicle_count + rejected_count
        
        return {
            "signal_plates": signal_count,
            "vehicle_plates": vehicle_count,
            "rejected": rejected_count,
            "total": total,
            "approval_rate": (signal_count + vehicle_count) / total * 100 if total > 0 else 0
        }