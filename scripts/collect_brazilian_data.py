

import os
import sys
import json
import requests
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from urllib.parse import urlparse, urljoin
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrazilianDataCollector:
    
    def __init__(self, output_dir: str = "datasets/raw_brazilian"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.signal_dir = self.output_dir / "signal_plates"
        self.vehicle_dir = self.output_dir / "vehicle_plates"
        self.signal_dir.mkdir(exist_ok=True)
        self.vehicle_dir.mkdir(exist_ok=True)
        
        self.config = {
            "max_images_per_category": 1000,
            "delay_between_requests": 1.0,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        self.data_sources = {
            "signal_plates": {
                "google_images": [
                    "stop sign brazil",
                    "yield sign brazil",
                    "no entry sign brazil",
                    "no left turn sign brazil",
                    "no right turn sign brazil",
                    "no u turn sign brazil",
                    "no parking sign brazil",
                    "regulated parking sign brazil",
                    "no stopping sign brazil",
                    "no overtaking sign brazil",
                    "no lane change sign brazil",
                    "no trucks sign brazil",
                    "no motor vehicles sign brazil",
                    "no animal vehicles sign brazil",
                    "no bicycles sign brazil",
                    "no tractors sign brazil",
                    "weight limit sign brazil",
                    "height limit sign brazil",
                    "speed limit sign brazil",
                    "no horn sign brazil",
                    "customs sign brazil",
                    "chains required sign brazil",
                    "keep right sign brazil",
                    "one way sign brazil",
                    "priority road sign brazil",
                    "turn left sign brazil",
                    "turn right sign brazil",
                    "go straight sign brazil",
                    "heavy vehicles keep right sign brazil",
                    "two way traffic sign brazil",
                    "no pedestrians sign brazil",
                    "pedestrians left sign brazil",
                    "pedestrians right sign brazil",
                    "buses only sign brazil",
                    "roundabout sign brazil",
                    "bicycles only sign brazil",
                    "cyclists left sign brazil",
                    "cyclists right sign brazil",
                    "cyclists pedestrians sign brazil",
                    "no motorcycles sign brazil",
                    "no buses sign brazil",
                    "trucks only sign brazil",
                    "no hand carts sign brazil",
                    "no hand carts sign brazil",
                    "no hand carts sign brazil",
                    "no hand carts sign brazil",
                    "no hand carts sign brazil",
                    "no hand carts sign brazil",
                    "no hand carts sign brazil",
                    "no hand carts sign brazil",
                    "no hand carts sign brazil"
                ],
            },
            "vehicle_plates": {
                "google_images": [
                    "mercosul padrão brasil",
                    "mercosul moto brasil",
                    "mercosul caminhão brasil",
                    "padrão antiga brasil",
                    "padrão antiga moto brasil",
                    "padrão antiga caminhão brasil",
                    "diplomática brasil",
                    "oficial governo brasil",
                    "oficial polícia brasil",
                    "oficial exército brasil",
                    "oficial marinha brasil",
                    "oficial aeronáutica brasil",
                    "temporária brasil",
                    "temporária moto brasil",
                    "temporária caminhão brasil",
                    "comercial brasil",
                    "comercial moto brasil",
                    "comercial caminhão brasil",
                    "especial brasil",
                    "especial moto brasil",
                    "especial caminhão brasil",
                    "teste fabricante brasil",
                    "teste concessionária brasil",
                    "exportação brasil",
                    "importação brasil",
                    "carro particular brasil",
                    "moto particular brasil",
                    "caminhão particular brasil",
                    "ônibus urbano brasil",
                    "ônibus rodoviário brasil",
                    "van comercial brasil",
                    "trator agrícola brasil",
                    "trator de obras brasil"
                ],
            }
        }
    
    def collect_google_images(self, query: str, category: str, max_images: int = 100):
        logger.info(f"Coletando imagens reais do Google para: {query}")
        
        try:
            api_key = "AIzaSyDAFvNVY8BP2Vw7IIxBkKA3jJNXCJISHmE"
            search_engine_id = "b482e980c4b39432f"
            search_engine_id_signal = "017576662512468239146:omuauf_lfve"
            
            url = "https://www.googleapis.com/customsearch/v1"
            
            params = {
                "key": api_key,
                "cx": search_engine_id,
                "q": query,
                "searchType": "image",
                "num": min(max_images, 10),
                "imgType": "photo",
                "imgSize": "large",
                "safe": "active",
                "rights": "cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial|cc_nonderived"
            }
            
            headers = {
                "User-Agent": self.config["user_agent"]
            }
            
            logger.info(f"Fazendo consulta à API do Google para: {query}")
            
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if "items" in data:
                    images_found = len(data["items"])
                    logger.info(f"Encontradas {images_found} imagens reais para '{query}'")
                    
                    for i, item in enumerate(data["items"][:max_images]):
                        try:
                            image_url = item["link"]
                            image_title = item.get("title", f"image_{i}")
                            
                            img_response = requests.get(image_url, headers=headers, timeout=10)
                            if img_response.status_code == 200:
                                filename = f"{category}_{query.replace(' ', '_')}_{i:03d}.jpg"
                                image_path = self._get_output_dir(query, category) / filename
                                
                                with open(image_path, 'wb') as f:
                                    f.write(img_response.content)
                                
                                logger.info(f"Imagem real baixada: {filename}")
                                
                                time.sleep(self.config["delay_between_requests"])
                            
                        except Exception as e:
                            logger.warning(f"Erro ao baixar imagem {i}: {e}")
                            continue
                    
                    if images_found == 0:
                        logger.warning("Nenhuma imagem real encontrada, criando sintéticas...")
                        self._create_sample_images(query, category, max_images)
                else:
                    logger.warning("Nenhum resultado encontrado, criando imagens sintéticas...")
                    self._create_sample_images(query, category, max_images)
                    
            else:
                logger.error(f"Erro na API do Google: {response.status_code}")
                logger.info("Criando imagens sintéticas como fallback...")
                self._create_sample_images(query, category, max_images)
            
        except Exception as e:
            logger.error(f"Erro ao coletar imagens do Google: {e}")
            logger.info("Criando imagens sintéticas como fallback...")
            self._create_sample_images(query, category, max_images)
    
        
            
            
            
            
            
            
                
                    
                            
                                
                                
                                
                            
                    
                    
            
    
    def _get_output_dir(self, query: str, category: str):
