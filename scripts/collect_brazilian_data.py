#!/usr/bin/env python3

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
                    # Placas de Regulamentação CONTRAN (R-1 a R-40) - Queries em Inglês
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
                # "flickr": [
                #     "CONTRAN placas regulamentação brasil",
                #     "placas trânsito oficiais CONTRAN brasil",
                #     "códigos R-1 R-40 placas brasil",
                #     "sinais trânsito regulamentação CONTRAN"
                # ]
            },
            "vehicle_plates": {
                "google_images": [
                    # Placas de Veículos - Padrões Oficiais Brasileiros
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
                # "flickr": [
                #     "placas veículos oficiais brasil",
                #     "placas mercosul brasil",
                #     "placas veículos padrão brasil",
                #     "placas veículos especiais brasil"
                # ]
            }
        }
    
    def collect_google_images(self, query: str, category: str, max_images: int = 100):
        logger.info(f"Coletando imagens reais do Google para: {query}")
        
        try:
            # Usar Google Custom Search API
            api_key = "AIzaSyDAFvNVY8BP2Vw7IIxBkKA3jJNXCJISHmE"
            # Search Engine ID para busca geral de imagens
            search_engine_id = "b482e980c4b39432f"
            # Search Engine ID para busca de placas de sinalização
            search_engine_id_signal = "017576662512468239146:omuauf_lfve"
            
            # URL da API do Google Custom Search
            url = "https://www.googleapis.com/customsearch/v1"
            
            params = {
                "key": api_key,
                "cx": search_engine_id,
                "q": query,
                "searchType": "image",
                "num": min(max_images, 10),  # Máximo 10 por consulta
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
                    
                    # Baixar imagens reais
                    for i, item in enumerate(data["items"][:max_images]):
                        try:
                            image_url = item["link"]
                            image_title = item.get("title", f"image_{i}")
                            
                            # Baixar imagem
                            img_response = requests.get(image_url, headers=headers, timeout=10)
                            if img_response.status_code == 200:
                                # Salvar imagem real
                                filename = f"{category}_{query.replace(' ', '_')}_{i:03d}.jpg"
                                image_path = self._get_output_dir(query, category) / filename
                                
                                with open(image_path, 'wb') as f:
                                    f.write(img_response.content)
                                
                                logger.info(f"Imagem real baixada: {filename}")
                                
                                # Aguardar entre downloads
                                time.sleep(self.config["delay_between_requests"])
                            
                        except Exception as e:
                            logger.warning(f"Erro ao baixar imagem {i}: {e}")
                            continue
                    
                    # Se não conseguiu baixar imagens reais, criar sintéticas
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
    
    # def collect_flickr_images(self, query: str, category: str, max_images: int = 100):
    #     logger.info(f"Coletando imagens reais do Flickr para: {query}")
        
    #     try:
    #         # API Key do Flickr (você precisa criar em https://www.flickr.com/services/apps/create/)
    #         flickr_api_key = "SUA_FLICKR_API_KEY"  # Substitua pela sua chave
            
    #         if flickr_api_key == "SUA_FLICKR_API_KEY":
    #             logger.warning("Flickr API Key não configurada, criando imagens sintéticas...")
    #             self._create_sample_images(query, category, max_images // 2)
    #             return
            
    #         # URL da API do Flickr
    #         url = "https://www.flickr.com/services/rest/"
            
    #         params = {
    #             "method": "flickr.photos.search",
    #             "api_key": flickr_api_key,
    #             "text": query,
    #             "per_page": min(max_images, 100),
    #             "format": "json",
    #             "nojsoncallback": 1,
    #             "sort": "relevance",
    #             "content_type": 1,  # Apenas fotos
    #             "safe_search": 1
    #         }
            
    #         logger.info(f"Fazendo consulta à API do Flickr para: {query}")
            
    #         response = requests.get(url, params=params, timeout=10)
            
    #         if response.status_code == 200:
    #             data = response.json()
                
    #             if data.get("stat") == "ok" and "photos" in data:
    #                 photos = data["photos"]["photo"]
    #                 photos_found = len(photos)
    #                 logger.info(f"Encontradas {photos_found} fotos no Flickr para '{query}'")
                    
    #                 # Baixar fotos reais
    #                 for i, photo in enumerate(photos[:max_images]):
    #                     try:
    #                         # Construir URL da foto
    #                         photo_url = f"https://live.staticflickr.com/{photo['server']}/{photo['id']}_{photo['secret']}_b.jpg"
                            
    #                         # Baixar foto
    #                         img_response = requests.get(photo_url, timeout=10)
    #                         if img_response.status_code == 200:
    #                             # Salvar foto real
    #                             filename = f"{category}_{query.replace(' ', '_')}_{i:03d}.jpg"
    #                             image_path = self._get_output_dir(query, category) / filename
                                
    #                             with open(image_path, 'wb') as f:
    #                                 f.write(img_response.content)
                                
    #                             logger.info(f"Foto real baixada do Flickr: {filename}")
                                
    #                             # Aguardar entre downloads
    #                             time.sleep(self.config["delay_between_requests"])
                            
    #                     except Exception as e:
    #                         logger.warning(f"Erro ao baixar foto {i}: {e}")
    #                         continue
                    
    #                 # Se não conseguiu baixar fotos reais, criar sintéticas
    #                 if photos_found == 0:
    #                     logger.warning("Nenhuma foto encontrada no Flickr, criando sintéticas...")
    #                     self._create_sample_images(query, category, max_images // 2)
    #             else:
    #                 logger.warning("Nenhum resultado encontrado no Flickr, criando sintéticas...")
    #                 self._create_sample_images(query, category, max_images // 2)
                    
    #         else:
    #             logger.error(f"Erro na API do Flickr: {response.status_code}")
    #             logger.info("Criando imagens sintéticas como fallback...")
    #             self._create_sample_images(query, category, max_images // 2)
            
    #     except Exception as e:
    #         logger.error(f"Erro ao coletar imagens do Flickr: {e}")
    #         logger.info("Criando imagens sintéticas como fallback...")
    #         self._create_sample_images(query, category, max_images // 2)
    
    def _get_output_dir(self, query: str, category: str):
        """Determina o diretório de saída baseado no tipo de query"""
        # Reconhecer placas de sinalização CONTRAN (R-1 a R-40)
        signal_keywords = [
            "R-1", "R-2", "R-3", "R-4a", "R-4b", "R-5a", "R-5b", "R-6a", "R-6b", "R-6c",
            "R-7", "R-8a", "R-8b", "R-9", "R-10", "R-11", "R-12", "R-13", "R-14", "R-15",
            "R-16", "R-17", "R-18", "R-19", "R-20", "R-21", "R-22", "R-23", "R-24a", "R-24b",
            "R-25a", "R-25b", "R-25c", "R-25d", "R-26", "R-27", "R-28", "R-29", "R-30", "R-31",
            "R-32", "R-33", "R-34", "R-35a", "R-35b", "R-36a", "R-36b", "R-37", "R-38", "R-39", "R-40",
            "parada", "preferência", "proibido", "sentido", "estacionar", "ultrapassar", "virar",
            "retornar", "mudar", "faixa", "trânsito", "bicicletas", "pedestres", "motocicletas",
            "velocidade", "peso", "altura", "largura", "comprimento", "buzina", "alfândega",
            "corrente", "direita", "esquerda", "frente", "circulação", "rotatória", "exclusiva"
        ]
        
        # Reconhecer placas de veículos
        vehicle_keywords = [
            "mercosul", "padrão", "antiga", "diplomática", "oficial", "temporária", "comercial",
            "especial", "teste", "exportação", "importação", "particular", "urbano", "rodoviário",
            "agrícola", "obras", "carro", "caminhão", "moto", "ônibus", "van", "trator"
        ]
        
        if any(keyword in query.lower() for keyword in signal_keywords):
            output_dir = self.signal_dir
        elif any(keyword in query.lower() for keyword in vehicle_keywords):
            output_dir = self.vehicle_dir
        else:
            # Fallback baseado na categoria
            if category == "signal":
                output_dir = self.signal_dir
            elif category == "vehicle":
                output_dir = self.vehicle_dir
            else:
                output_dir = self.output_dir
                
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def _create_sample_images(self, query: str, category: str, count: int):
        try:
            import cv2
            import numpy as np
            
            output_dir = self._get_output_dir(query, category)
            
            for i in range(min(count, 10)):
                # Criar fundo mais realista
                img = np.ones((640, 640, 3), dtype=np.uint8) * 240  # Fundo cinza claro
                
                # Adicionar gradiente sutil
                for y in range(640):
                    for x in range(640):
                        gradient = int(240 - (y / 640) * 40)
                        img[y, x] = [gradient, gradient, gradient]
                
                # Criar placa mais realista
                if "veículo" in query.lower():
                    # Placa de veículo
                    plate_width = 200
                    plate_height = 60
                    x1 = 320 - plate_width // 2
                    y1 = 320 - plate_height // 2
                    x2 = x1 + plate_width
                    y2 = y1 + plate_height
                    
                    # Fundo da placa (verde Mercosul ou cinza padrão)
                    plate_color = (0, 100, 0) if "mercosul" in query.lower() else (100, 100, 100)
                    cv2.rectangle(img, (x1, y1), (x2, y2), plate_color, -1)
                    
                    # Borda da placa
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 0), 2)
                    
                    # Texto da placa
                    plate_text = "ABC1234" if "mercosul" in query.lower() else "ABC-1234"
                    font_scale = 0.8
                    thickness = 2
                    text_size = cv2.getTextSize(plate_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
                    text_x = x1 + (plate_width - text_size[0]) // 2
                    text_y = y1 + (plate_height + text_size[1]) // 2
                    cv2.putText(img, plate_text, (text_x, text_y), 
                               cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)
                    
                    # Adicionar veículo sutil ao fundo
                    if "carro" in query.lower():
                        car_x1, car_y1 = 200, 400
                        car_x2, car_y2 = 440, 500
                        cv2.rectangle(img, (car_x1, car_y1), (car_x2, car_y2), (50, 50, 150), -1)
                        cv2.rectangle(img, (car_x1, car_y1), (car_x2, car_y2), (0, 0, 0), 2)
                
                elif "sinal" in query.lower() or any(keyword in query.lower() for keyword in ["pare", "preferência", "velocidade", "proibido", "sentido", "travessia", "zona", "obras", "atenção", "informação", "nome", "prédio", "semáforo", "passagem", "ciclovia", "faixa"]):
                    # Placa de sinalização
                    sign_size = 120
                    x1 = 320 - sign_size // 2
                    y1 = 320 - sign_size // 2
                    x2 = x1 + sign_size
                    y2 = y1 + sign_size
                    
                    # Cor base da placa baseada no tipo
                    if "pare" in query.lower():
                        sign_color = (0, 0, 255)  # Vermelho
                        sign_text = "PARE"
                        sign_shape = "circle"
                    elif "preferência" in query.lower():
                        sign_color = (255, 165, 0)  # Laranja
                        sign_text = "DÊ"
                        sign_shape = "triangle"
                    elif "velocidade" in query.lower():
                        sign_color = (0, 150, 255)  # Azul vibrante
                        sign_text = "40"
                        sign_shape = "circle"
                    elif "atenção" in query.lower() or "cuidado" in query.lower():
                        sign_color = (255, 255, 0)  # Amarelo
                        sign_text = "!"
                        sign_shape = "diamond"
                    elif "proibido" in query.lower():
                        sign_color = (255, 0, 0)  # Vermelho
                        sign_text = "X"
                        sign_shape = "circle"
                    else:
                        sign_color = (0, 100, 200)  # Azul
                        sign_text = "INFO"
                        sign_shape = "square"
                    
                    # Desenhar placa baseada na forma
                    if sign_shape == "circle":
                        center = (320, 320)
                        cv2.circle(img, center, sign_size // 2, sign_color, -1)
                        cv2.circle(img, center, sign_size // 2, (0, 0, 0), 3)
                    elif sign_shape == "triangle":
                        pts = np.array([[320, 280], [280, 360], [360, 360]], np.int32)
                        cv2.fillPoly(img, [pts], sign_color)
                        cv2.polylines(img, [pts], True, (0, 0, 0), 3)
                    elif sign_shape == "diamond":
                        pts = np.array([[320, 280], [280, 320], [320, 360], [360, 320]], np.int32)
                        cv2.fillPoly(img, [pts], sign_color)
                        cv2.polylines(img, [pts], True, (0, 0, 0), 3)
                    else:  # square
                        cv2.rectangle(img, (x1, y1), (x2, y2), sign_color, -1)
                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 0), 3)
                    
                    # Texto da placa
                    font_scale = 1.5 if len(sign_text) == 1 else 1.0
                    thickness = 3
                    text_size = cv2.getTextSize(sign_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
                    text_x = 320 - text_size[0] // 2
                    text_y = 320 + text_size[1] // 2
                    cv2.putText(img, sign_text, (text_x, text_y), 
                               cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness)
                
                # Adicionar ruído muito sutil para realismo
                noise = np.random.normal(0, 2, (640, 640, 3)).astype(np.uint8)
                img = cv2.add(img, noise)
                
                # Aplicar blur muito sutil para suavizar
                img = cv2.GaussianBlur(img, (3, 3), 0.3)
                
                # Salvar imagem com alta qualidade
                filename = f"{category}_{query.replace(' ', '_')}_{i:03d}.jpg"
                image_path = output_dir / filename
                cv2.imwrite(str(image_path), img, [cv2.IMWRITE_JPEG_QUALITY, 98])
                
                logger.debug(f"Imagem de exemplo criada: {image_path}")
                
        except ImportError:
            logger.warning("OpenCV não disponível, pulando criação de imagens de exemplo")
        except Exception as e:
            logger.warning(f"Erro ao criar imagem de exemplo: {e}")
    
    def collect_from_local_sources(self, source_dir: str):
        logger.info(f"Coletando dados de fonte local: {source_dir}")
        
        source_path = Path(source_dir)
        if not source_path.exists():
            logger.error(f"Diretório fonte não encontrado: {source_dir}")
            return
        
        image_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(source_path.rglob(f"*{ext}"))
            image_files.extend(source_path.rglob(f"*{ext.upper()}"))
        
        logger.info(f"Encontradas {len(image_files)} imagens em {source_dir}")
        
        for i, image_file in enumerate(image_files):
            try:
                if any(keyword in image_file.name.lower() for keyword in ["sinal", "trânsito", "pare", "preferência"]):
                    dest_dir = self.signal_dir
                elif any(keyword in image_file.name.lower() for keyword in ["placa", "veículo", "carro", "moto"]):
                    dest_dir = self.vehicle_dir
                else:
                    dest_dir = self.output_dir
                
                dest_path = dest_dir / f"local_{i:04d}_{image_file.name}"
                import shutil
                shutil.copy2(image_file, dest_path)
                
                logger.debug(f"Copiado: {image_file.name} -> {dest_path}")
                
            except Exception as e:
                logger.warning(f"Erro ao copiar {image_file}: {e}")
    
    def collect_from_api_sources(self):
        logger.info("Coletando dados de APIs públicas...")
        
        logger.info("Para usar APIs oficiais")
    
    def create_dataset_structure(self):
        logger.info("Criando estrutura de diretórios...")
        
        yolo_structure = [
            "signal_plates/images/train",
            "signal_plates/images/val", 
            "signal_plates/images/test",
            "signal_plates/labels/train",
            "signal_plates/labels/val",
            "signal_plates/labels/test",
            "vehicle_plates/images/train",
            "vehicle_plates/images/val",
            "vehicle_plates/images/test", 
            "vehicle_plates/labels/train",
            "vehicle_plates/labels/val",
            "vehicle_plates/labels/test"
        ]
        
        for dir_path in yolo_structure:
            full_path = self.output_dir.parent / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Diretório criado: {full_path}")
        
        logger.info("Estrutura de diretórios criada com sucesso!")
    
    def generate_annotations(self):
        logger.info("Gerando anotações YOLO com códigos CONTRAN...")
        
        # Mapeamento de códigos CONTRAN para classes
        contran_classes = {
            # Placas de Regulamentação (R-1 a R-40)
            "R-1": 0,   # Parada obrigatória
            "R-2": 1,   # Dê a preferência
            "R-3": 2,   # Sentido proibido
            "R-4a": 3,  # Proibido virar à esquerda
            "R-4b": 4,  # Proibido virar à direita
            "R-5a": 5,  # Proibido retornar à esquerda
            "R-5b": 6,  # Proibido retornar à direita
            "R-6a": 7,  # Proibido estacionar
            "R-6b": 8,  # Estacionamento regulamentado
            "R-6c": 9,  # Proibido parar e estacionar
            "R-7": 10,  # Proibido ultrapassar
            "R-8a": 11, # Proibido mudar de faixa (esq->dir)
            "R-8b": 12, # Proibido mudar de faixa (dir->esq)
            "R-9": 13,  # Proibido trânsito de caminhões
            "R-10": 14, # Proibido trânsito de veículos automotores
            "R-11": 15, # Proibido trânsito de veículos de tração animal
            "R-12": 16, # Proibido trânsito de bicicletas
            "R-13": 17, # Proibido trânsito de tratores e máquinas
            "R-14": 18, # Peso bruto total máximo permitido
            "R-15": 19, # Altura máxima permitida
            "R-16": 20, # Largura máxima permitida
            "R-17": 21, # Peso máximo permitido por eixo
            "R-18": 22, # Comprimento máximo permitido
            "R-19": 23, # Velocidade máxima permitida
            "R-20": 24, # Proibido acionar buzina
            "R-21": 25, # Alfândega
            "R-22": 26, # Uso obrigatório de corrente
            "R-23": 27, # Conserve-se à direita
            "R-24a": 28, # Sentido de circulação da via/pista
            "R-24b": 29, # Passagem obrigatória
            "R-25a": 30, # Vire à esquerda
            "R-25b": 31, # Vire à direita
            "R-25c": 32, # Siga em frente ou à esquerda
            "R-25d": 33, # Siga em frente ou à direita
            "R-26": 34, # Siga em frente
            "R-27": 35, # Ônibus, caminhões mantenham-se à direita
            "R-28": 36, # Duplo sentido de circulação
            "R-29": 37, # Proibido trânsito de pedestres
            "R-30": 38, # Pedestre, ande pela esquerda
            "R-31": 39, # Pedestre, ande pela direita
            "R-32": 40, # Circulação exclusiva de ônibus
            "R-33": 41, # Sentido de circulação na rotatória
            "R-34": 42, # Circulação exclusiva de bicicletas
            "R-35a": 43, # Ciclista, transite à esquerda
            "R-35b": 44, # Ciclista, transite à direita
            "R-36a": 45, # Ciclistas à esquerda, pedestres à direita
            "R-36b": 46, # Pedestres à esquerda, ciclistas à direita
            "R-37": 47, # Proibido trânsito de motocicletas
            "R-38": 48, # Proibido trânsito de ônibus
            "R-39": 49, # Circulação exclusiva de caminhão
            "R-40": 50, # Trânsito proibido a carros de mão
        }
        
        # Para imagens de sinalização
        signal_images = list(self.signal_dir.glob("*.jpg"))
        for i, image_path in enumerate(signal_images):
            label_path = image_path.with_suffix(".txt")
            
            # Determinar classe baseada no código CONTRAN na imagem
            class_id = 0  # Default para R-1 (Parada obrigatória)
            for code, cid in contran_classes.items():
                if code in image_path.name:
                    class_id = cid
                    break
            
            # Anotação para placa de sinalização (centro da imagem)
            x_center = 0.5
            y_center = 0.5
            width = 0.2
            height = 0.2
            
            with open(label_path, 'w') as f:
                f.write(f"{class_id} {x_center} {y_center} {width} {height}")
        
        # Para imagens de veículos
        vehicle_images = list(self.vehicle_dir.glob("*.jpg"))
        for i, image_path in enumerate(vehicle_images):
            label_path = image_path.with_suffix(".txt")
            
            # Classe 51: placa de veículo (centro da imagem)
            x_center = 0.5
            y_center = 0.5
            width = 0.3
            height = 0.1
            
            with open(label_path, 'w') as f:
                f.write(f"51 {x_center} {y_center} {width} {height}")
            
            # Se a imagem contém veículo, adicionar anotação para o veículo
            if any(keyword in image_path.name.lower() for keyword in ["carro", "caminhão", "moto", "ônibus", "van", "trator"]):
                # Classe 52: veículo (abaixo da placa)
                vehicle_x_center = 0.5
                vehicle_y_center = 0.7
                vehicle_width = 0.4
                vehicle_height = 0.2
                
                with open(label_path, 'a') as f:
                    f.write(f"\n52 {vehicle_x_center} {vehicle_y_center} {vehicle_width} {vehicle_height}")
        
        logger.info(f"Anotações geradas: {len(signal_images)} sinalização, {len(vehicle_images)} veículos")
        logger.info(f"Classes CONTRAN: 0-50 (sinalização), 51 (placa veículo), 52 (veículo)")
    
    def create_collection_report(self):
        logger.info("Criando relatório de coleta...")
        
        report = {
            "collection_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_images": 0,
            "signal_plates": 0,
            "vehicle_plates": 0,
            "categories": {}
        }
        
        for category_dir in [self.signal_dir, self.vehicle_dir]:
            category_name = category_dir.name
            image_count = len(list(category_dir.glob("*.jpg")))
            report[category_name] = image_count
            report["total_images"] += image_count
        
        report_path = self.output_dir / "collection_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Relatório salvo em: {report_path}")
        logger.info(f"Total de imagens coletadas: {report['total_images']}")
        
        return report

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Coletor de Dados Brasileiros para Treinamento")
    parser.add_argument("--source", choices=["google", "flickr", "local", "all"], 
                       default="all", help="Fonte de dados para coletar")
    parser.add_argument("--local-dir", type=str, help="Diretório local com imagens")
    parser.add_argument("--max-images", type=int, default=100, help="Máximo de imagens por categoria")
    parser.add_argument("--create-structure", action="store_true", help="Criar estrutura de diretórios YOLO")
    parser.add_argument("--generate-annotations", action="store_true", help="Gerar anotações básicas")
    
    args = parser.parse_args()
    
    print("Coletor de Dados Brasileiros para ver se esse porra de YOLO funciona")
    print("=" * 60)
    
    collector = BrazilianDataCollector()
    
    if args.create_structure:
        collector.create_dataset_structure()
    
    if args.source in ["google", "all"]:
        logger.info("Coletando dados do Google Images...")
        for query in collector.data_sources["signal_plates"]["google_images"]:
            collector.collect_google_images(query, "signal", args.max_images)
        
        for query in collector.data_sources["vehicle_plates"]["google_images"]:
            collector.collect_google_images(query, "vehicle", args.max_images)
    
    if args.source in ["flickr", "all"]:
        logger.info("Coletando dados do Flickr...")
        for query in collector.data_sources["signal_plates"]["flickr"]:
            collector.collect_flickr_images(query, "signal", args.max_images)
        
        for query in collector.data_sources["vehicle_plates"]["flickr"]:
            collector.collect_flickr_images(query, "vehicle", args.max_images)
    
    if args.source in ["local", "all"] or args.local_dir:
        local_dir = args.local_dir or "data/local_images"
        collector.collect_from_local_sources(local_dir)
    
    if args.source == "all":
        collector.collect_from_api_sources()
    
    if args.generate_annotations:
        collector.generate_annotations()
    
    report = collector.create_collection_report()
    
    print("\nColeta de dados terminada amem!")
    print(f"Total de imagens: {report['total_images']}")
    print(f"Placas de sinalização: {report['signal_plates']}")
    print(f"Placas de veículos: {report['vehicle_plates']}")
    print(f"Vou salvar essa merda em: {collector.output_dir}")

if __name__ == "__main__":
    main()
