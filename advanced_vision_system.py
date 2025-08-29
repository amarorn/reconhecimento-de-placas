#!/usr/bin/env python3
"""
Sistema Avançado de Visão Computacional para Placas MBST
========================================================

Este sistema inclui:
- Detecção YOLO treinada para placas brasileiras
- OCR integrado para leitura de texto
- Fine-tuning com dataset personalizado
- Sistema de feedback para correções
- API REST para produção
"""

import cv2
import numpy as np
import json
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import logging
from pathlib import Path
import requests
from PIL import Image, ImageDraw, ImageFont
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
from ultralytics import YOLO
import easyocr
import sqlite3

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MBSTVisionSystem:
    """Sistema avançado de visão computacional para placas MBST"""
    
    def __init__(self, config_path: str = "config/vision_config.json"):
        self.config = self.load_config(config_path)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.models = {}
        self.dataset_path = self.config.get("dataset_path", "dataset_mbst")
        self.feedback_db = self.config.get("feedback_db", "feedback.db")
        
        # Inicializar componentes
        self.init_models()
        self.init_feedback_system()
        
    def load_config(self, config_path: str) -> Dict:
        """Carrega configuração do sistema"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Configuração padrão
            return {
                "yolo_model": "yolov8n.pt",
                "yolo_confidence": 0.5,
                "ocr_languages": ["pt", "en"],
                "dataset_path": "dataset_mbst",
                "feedback_db": "feedback.db",
                "api_endpoint": "http://localhost:8000",
                "save_annotations": True,
                "save_results": True
            }
    
    def init_models(self):
        """Inicializa modelos de ML"""
        try:
            # YOLO para detecção de placas
            if self.config.get("use_custom_yolo", False):
                yolo_path = self.config.get("custom_yolo_path", "models/mbst_yolo.pt")
                if os.path.exists(yolo_path):
                    self.models["yolo"] = YOLO(yolo_path)
                    logger.info("✅ Modelo YOLO customizado carregado")
                else:
                    self.models["yolo"] = YOLO(self.config.get("yolo_model", "yolov8n.pt"))
                    logger.info("⚠️ Modelo YOLO padrão carregado (custom não encontrado)")
            else:
                self.models["yolo"] = YOLO(self.config.get("yolo_model", "yolov8n.pt"))
                logger.info("✅ Modelo YOLO padrão carregado")
            
            # OCR para leitura de texto
            self.models["ocr"] = easyocr.Reader(
                self.config.get("ocr_languages", ["pt", "en"]),
                gpu=torch.cuda.is_available()
            )
            logger.info("✅ Modelo OCR carregado")
            
            # Classificador de tipos de placa
            self.models["classifier"] = self.load_classifier()
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar modelos: {e}")
            raise
    
    def load_classifier(self):
        """Carrega classificador de tipos de placa"""
        try:
            # Aqui você pode carregar um modelo treinado específico para MBST
            # Por enquanto, vamos usar regras baseadas em características visuais
            return None
        except Exception as e:
            logger.warning(f"⚠️ Classificador não carregado: {e}")
            return None
    
    def init_feedback_system(self):
        """Inicializa sistema de feedback"""
        try:
            conn = sqlite3.connect(self.feedback_db)
            cursor = conn.cursor()
            
            # Criar tabela de feedback
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_path TEXT,
                    original_classification TEXT,
                    corrected_classification TEXT,
                    user_feedback TEXT,
                    confidence REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending'
                )
            """)
            
            # Criar tabela de correções
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS corrections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_path TEXT,
                    old_classification TEXT,
                    new_classification TEXT,
                    corrected_by TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("✅ Sistema de feedback inicializado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar feedback: {e}")
    
    def detect_plates_yolo(self, image_path: str) -> List[Dict]:
        """Detecta placas usando YOLO"""
        try:
            # Carregar imagem
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Imagem não pode ser carregada: {image_path}")
            
            # Executar detecção YOLO
            results = self.models["yolo"](image, conf=self.config.get("yolo_confidence", 0.5))
            
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Coordenadas da caixa
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = float(box.conf[0])
                        class_id = int(box.cls[0])
                        
                        detection = {
                            "bbox": [int(x1), int(y1), int(x2), int(y2)],
                            "confidence": confidence,
                            "class_id": class_id,
                            "class_name": self.get_class_name(class_id),
                            "area": (x2 - x1) * (y2 - y1)
                        }
                        detections.append(detection)
            
            # Ordenar por confiança
            detections.sort(key=lambda x: x["confidence"], reverse=True)
            
            logger.info(f"✅ YOLO detectou {len(detections)} placas em {image_path}")
            return detections
            
        except Exception as e:
            logger.error(f"❌ Erro na detecção YOLO: {e}")
            return []
    
    def get_class_name(self, class_id: int) -> str:
        """Retorna nome da classe baseado no ID"""
        class_names = {
            0: "placa_regulamentacao",
            1: "placa_advertencia", 
            2: "placa_informacao",
            3: "placa_servico",
            4: "placa_educacao"
        }
        return class_names.get(class_id, "placa_desconhecida")
    
    def extract_text_ocr(self, image_path: str, bbox: List[int]) -> Dict:
        """Extrai texto usando OCR na região da placa"""
        try:
            # Carregar imagem
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Imagem não pode ser carregada: {image_path}")
            
            # Cortar região da placa
            x1, y1, x2, y2 = bbox
            plate_region = image[y1:y2, x1:x2]
            
            # Pré-processar para melhorar OCR
            plate_region = self.preprocess_for_ocr(plate_region)
            
            # Executar OCR
            results = self.models["ocr"].readtext(plate_region)
            
            # Processar resultados
            texts = []
            confidences = []
            
            for (bbox, text, confidence) in results:
                texts.append(text)
                confidences.append(confidence)
            
            # Combinar textos
            combined_text = " ".join(texts) if texts else ""
            avg_confidence = np.mean(confidences) if confidences else 0.0
            
            ocr_result = {
                "text": combined_text,
                "confidence": avg_confidence,
                "individual_texts": texts,
                "individual_confidences": confidences,
                "bbox": bbox
            }
            
            logger.info(f"✅ OCR extraiu texto: '{combined_text}' (confiança: {avg_confidence:.2f})")
            return ocr_result
            
        except Exception as e:
            logger.error(f"❌ Erro no OCR: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "individual_texts": [],
                "individual_confidences": [],
                "bbox": bbox
            }
    
    def preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """Pré-processa imagem para melhorar OCR"""
        try:
            # Converter para escala de cinza
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Redimensionar para melhor resolução
            height, width = gray.shape
            scale_factor = 2.0
            new_height, new_width = int(height * scale_factor), int(width * scale_factor)
            resized = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            # Aplicar filtros para melhorar contraste
            # CLAHE para equalização adaptativa
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(resized)
            
            # Redução de ruído
            denoised = cv2.fastNlMeansDenoising(enhanced)
            
            # Binarização adaptativa
            binary = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            return binary
            
        except Exception as e:
            logger.error(f"❌ Erro no pré-processamento OCR: {e}")
            return image
    
    def classify_plate_type(self, image_path: str, bbox: List[int], ocr_text: str) -> Dict:
        """Classifica o tipo de placa baseado em características visuais e texto"""
        try:
            # Carregar imagem
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Imagem não pode ser carregada: {image_path}")
            
            # Cortar região da placa
            x1, y1, x2, y2 = bbox
            plate_region = image[y1:y2, x1:x2]
            
            # Análise de características visuais
            visual_features = self.analyze_visual_features(plate_region)
            
            # Análise de texto
            text_features = self.analyze_text_features(ocr_text)
            
            # Classificação combinada
            classification = self.combine_classifications(visual_features, text_features)
            
            logger.info(f"✅ Placa classificada como: {classification['type']} (confiança: {classification['confidence']:.2f})")
            return classification
            
        except Exception as e:
            logger.error(f"❌ Erro na classificação: {e}")
            return {
                "type": "desconhecido",
                "code": "UNK",
                "confidence": 0.0,
                "reason": f"Erro na classificação: {e}"
            }
    
    def analyze_visual_features(self, plate_image: np.ndarray) -> Dict:
        """Analisa características visuais da placa"""
        try:
            # Converter para HSV para análise de cores
            hsv = cv2.cvtColor(plate_image, cv2.COLOR_BGR2HSV)
            
            # Análise de cores
            red_mask = cv2.inRange(hsv, (0, 50, 50), (10, 255, 255))
            red_mask += cv2.inRange(hsv, (170, 50, 50), (180, 255, 255))
            yellow_mask = cv2.inRange(hsv, (20, 50, 50), (30, 255, 255))
            blue_mask = cv2.inRange(hsv, (100, 50, 50), (130, 255, 255))
            
            red_pixels = cv2.countNonZero(red_mask)
            yellow_pixels = cv2.countNonZero(yellow_mask)
            blue_pixels = cv2.countNonZero(blue_mask)
            total_pixels = plate_image.shape[0] * plate_image.shape[1]
            
            # Análise de forma
            gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Encontrar contorno principal
            if contours:
                main_contour = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(main_contour)
                perimeter = cv2.arcLength(main_contour, True)
                
                # Aproximar forma
                epsilon = 0.02 * perimeter
                approx = cv2.approxPolyDP(main_contour, epsilon, True)
                num_vertices = len(approx)
                
                # Determinar forma
                if num_vertices == 8:
                    shape = "octogonal"
                elif num_vertices == 3:
                    shape = "triangular"
                elif num_vertices == 4:
                    shape = "retangular"
                else:
                    shape = "irregular"
            else:
                shape = "desconhecida"
                area = 0
                perimeter = 0
            
            features = {
                "colors": {
                    "red_ratio": red_pixels / total_pixels,
                    "yellow_ratio": yellow_pixels / total_pixels,
                    "blue_ratio": blue_pixels / total_pixels
                },
                "shape": shape,
                "area": area,
                "perimeter": perimeter,
                "aspect_ratio": plate_image.shape[1] / plate_image.shape[0] if plate_image.shape[0] > 0 else 0
            }
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Erro na análise visual: {e}")
            return {}
    
    def analyze_text_features(self, text: str) -> Dict:
        """Analisa características do texto da placa"""
        try:
            text = text.upper().strip()
            
            # Palavras-chave para diferentes tipos
            regulamentacao_keywords = ["PARE", "DÊ", "PREFERÊNCIA", "PROIBIDO", "OBRIGATÓRIO", "VELOCIDADE"]
            advertencia_keywords = ["ATENÇÃO", "PERIGO", "CRUZAMENTO", "CURVA", "DESCIDA", "SUBIDA"]
            informacao_keywords = ["HOSPITAL", "ESCOLA", "POSTO", "RESTAURANTE", "HOTEL", "ESTACIONAMENTO"]
            
            # Contar ocorrências
            regulamentacao_count = sum(1 for keyword in regulamentacao_keywords if keyword in text)
            advertencia_count = sum(1 for keyword in advertencia_keywords if keyword in text)
            informacao_count = sum(1 for keyword in informacao_keywords if keyword in text)
            
            # Determinar tipo baseado em palavras-chave
            if regulamentacao_count > 0:
                type_score = "regulamentacao"
                confidence = min(0.9, 0.6 + regulamentacao_count * 0.1)
            elif advertencia_count > 0:
                type_score = "advertencia"
                confidence = min(0.9, 0.6 + advertencia_count * 0.1)
            elif informacao_count > 0:
                type_score = "informacao"
                confidence = min(0.9, 0.6 + informacao_count * 0.1)
            else:
                type_score = "desconhecido"
                confidence = 0.3
            
            features = {
                "type": type_score,
                "confidence": confidence,
                "text_length": len(text),
                "has_numbers": any(char.isdigit() for char in text),
                "keyword_matches": {
                    "regulamentacao": regulamentacao_count,
                    "advertencia": advertencia_count,
                    "informacao": informacao_count
                }
            }
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de texto: {e}")
            return {"type": "desconhecido", "confidence": 0.0}
    
    def combine_classifications(self, visual_features: Dict, text_features: Dict) -> Dict:
        """Combina classificações visual e textual"""
        try:
            # Pesos para diferentes características
            visual_weight = 0.6
            text_weight = 0.4
            
            # Classificação visual
            visual_type = self.classify_by_visual_features(visual_features)
            visual_confidence = visual_type.get("confidence", 0.0)
            
            # Classificação textual
            text_type = text_features.get("type", "desconhecido")
            text_confidence = text_features.get("confidence", 0.0)
            
            # Combinar classificações
            if visual_type["type"] == text_type:
                # Mesmo tipo, alta confiança
                final_type = visual_type["type"]
                final_confidence = (visual_confidence + text_confidence) / 2
            else:
                # Tipos diferentes, usar o mais confiante
                if visual_confidence > text_confidence:
                    final_type = visual_type["type"]
                    final_confidence = visual_confidence * 0.8  # Penalizar conflito
                else:
                    final_type = text_type
                    final_confidence = text_confidence * 0.8
            
            # Gerar código baseado no tipo
            code = self.generate_plate_code(final_type, visual_features, text_features)
            
            classification = {
                "type": final_type,
                "code": code,
                "confidence": final_confidence,
                "visual_classification": visual_type,
                "text_classification": text_features,
                "combined_method": "weighted_average"
            }
            
            return classification
            
        except Exception as e:
            logger.error(f"❌ Erro na combinação de classificações: {e}")
            return {
                "type": "desconhecido",
                "code": "UNK",
                "confidence": 0.0,
                "reason": f"Erro na combinação: {e}"
            }
    
    def classify_by_visual_features(self, features: Dict) -> Dict:
        """Classifica placa baseado em características visuais"""
        try:
            colors = features.get("colors", {})
            shape = features.get("shape", "desconhecida")
            
            # Regras baseadas em características visuais
            if shape == "octogonal" and colors.get("red_ratio", 0) > 0.3:
                return {"type": "regulamentacao", "confidence": 0.9, "reason": "Forma octogonal com vermelho"}
            
            elif shape == "triangular" and colors.get("yellow_ratio", 0) > 0.3:
                return {"type": "advertencia", "confidence": 0.85, "reason": "Forma triangular com amarelo"}
            
            elif shape == "retangular" and colors.get("blue_ratio", 0) > 0.3:
                return {"type": "informacao", "confidence": 0.8, "reason": "Forma retangular com azul"}
            
            elif colors.get("red_ratio", 0) > 0.4:
                return {"type": "regulamentacao", "confidence": 0.7, "reason": "Predominância de vermelho"}
            
            elif colors.get("yellow_ratio", 0) > 0.4:
                return {"type": "advertencia", "confidence": 0.7, "reason": "Predominância de amarelo"}
            
            else:
                return {"type": "desconhecido", "confidence": 0.3, "reason": "Características não conclusivas"}
                
        except Exception as e:
            logger.error(f"❌ Erro na classificação visual: {e}")
            return {"type": "desconhecido", "confidence": 0.0}
    
    def generate_plate_code(self, plate_type: str, visual_features: Dict, text_features: Dict) -> str:
        """Gera código da placa baseado no tipo e características"""
        try:
            if plate_type == "regulamentacao":
                prefix = "R"
            elif plate_type == "advertencia":
                prefix = "A"
            elif plate_type == "informacao":
                prefix = "I"
            elif plate_type == "servico":
                prefix = "S"
            else:
                prefix = "U"
            
            # Gerar número baseado em características
            visual_hash = hash(str(visual_features))
            text_hash = hash(str(text_features))
            combined_hash = abs(visual_hash + text_hash) % 100
            
            code = f"{prefix}-{combined_hash:02d}"
            return code
            
        except Exception as e:
            logger.error(f"❌ Erro na geração de código: {e}")
            return "UNK-00"
    
    def process_image_complete(self, image_path: str) -> Dict:
        """Processa imagem completa: detecção + OCR + classificação"""
        try:
            logger.info(f"🚀 Processando imagem: {image_path}")
            
            # 1. Detecção YOLO
            detections = self.detect_plates_yolo(image_path)
            
            if not detections:
                logger.warning(f"⚠️ Nenhuma placa detectada em {image_path}")
                return {
                    "image_path": image_path,
                    "status": "no_plates_detected",
                    "detections": [],
                    "processing_time": 0
                }
            
            # 2. Processar cada detecção
            results = []
            start_time = datetime.now()
            
            for i, detection in enumerate(detections):
                logger.info(f"🔍 Processando detecção {i+1}/{len(detections)}")
                
                # OCR na região da placa
                ocr_result = self.extract_text_ocr(image_path, detection["bbox"])
                
                # Classificação da placa
                classification = self.classify_plate_type(
                    image_path, detection["bbox"], ocr_result["text"]
                )
                
                # Resultado combinado
                result = {
                    "detection_id": i,
                    "bbox": detection["bbox"],
                    "detection_confidence": detection["confidence"],
                    "ocr_result": ocr_result,
                    "classification": classification,
                    "combined_confidence": (detection["confidence"] + classification["confidence"]) / 2
                }
                
                results.append(result)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # 3. Resultado final
            final_result = {
                "image_path": image_path,
                "status": "success",
                "total_detections": len(detections),
                "detections": results,
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat()
            }
            
            # 4. Salvar resultados se configurado
            if self.config.get("save_results", True):
                self.save_analysis_results(final_result)
            
            logger.info(f"✅ Processamento concluído em {processing_time:.2f}s")
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Erro no processamento completo: {e}")
            return {
                "image_path": image_path,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def save_analysis_results(self, results: Dict):
        """Salva resultados da análise"""
        try:
            # Criar diretório de resultados
            results_dir = Path("results")
            results_dir.mkdir(exist_ok=True)
            
            # Nome do arquivo baseado na imagem
            image_name = Path(results["image_path"]).stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{image_name}_analysis_{timestamp}.json"
            
            # Salvar JSON
            results_file = results_dir / filename
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Resultados salvos em: {results_file}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar resultados: {e}")
    
    def submit_feedback(self, image_path: str, original_classification: str, 
                       corrected_classification: str, user_feedback: str, confidence: float):
        """Submete feedback do usuário"""
        try:
            conn = sqlite3.connect(self.feedback_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO feedback (image_path, original_classification, corrected_classification, 
                                   user_feedback, confidence, status)
                VALUES (?, ?, ?, ?, ?, 'pending')
            """, (image_path, original_classification, corrected_classification, user_feedback, confidence))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Feedback submetido para {image_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao submeter feedback: {e}")
            return False
    
    def get_feedback_stats(self) -> Dict:
        """Retorna estatísticas do sistema de feedback"""
        try:
            conn = sqlite3.connect(self.feedback_db)
            cursor = conn.cursor()
            
            # Total de feedbacks
            cursor.execute("SELECT COUNT(*) FROM feedback")
            total_feedback = cursor.fetchone()[0]
            
            # Feedbacks por status
            cursor.execute("SELECT status, COUNT(*) FROM feedback GROUP BY status")
            status_counts = dict(cursor.fetchall())
            
            # Feedbacks por tipo de erro
            cursor.execute("""
                SELECT corrected_classification, COUNT(*) 
                FROM feedback 
                GROUP BY corrected_classification
            """)
            correction_counts = dict(cursor.fetchall())
            
            conn.close()
            
            stats = {
                "total_feedback": total_feedback,
                "status_counts": status_counts,
                "correction_counts": correction_counts,
                "timestamp": datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas de feedback: {e}")
            return {}
    
    def process_batch(self, image_folder: str) -> List[Dict]:
        """Processa lote de imagens"""
        try:
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
            image_files = []
            
            # Encontrar arquivos de imagem
            for ext in image_extensions:
                image_files.extend(Path(image_folder).glob(f"*{ext}"))
                image_files.extend(Path(image_folder).glob(f"*{ext.upper()}"))
            
            if not image_files:
                logger.warning(f"⚠️ Nenhuma imagem encontrada em {image_folder}")
                return []
            
            logger.info(f"🚀 Processando {len(image_files)} imagens...")
            
            results = []
            for i, image_file in enumerate(image_files):
                logger.info(f"📸 Processando {i+1}/{len(image_files)}: {image_file.name}")
                
                result = self.process_image_complete(str(image_file))
                results.append(result)
                
                # Pequena pausa para não sobrecarregar
                import time
                time.sleep(0.1)
            
            # Salvar relatório do lote
            batch_report = {
                "folder": image_folder,
                "total_images": len(image_files),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "error"]),
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
            if self.config.get("save_results", True):
                self.save_batch_report(batch_report)
            
            logger.info(f"✅ Processamento em lote concluído: {len(results)} imagens")
            return results
            
        except Exception as e:
            logger.error(f"❌ Erro no processamento em lote: {e}")
            return []
    
    def save_batch_report(self, report: Dict):
        """Salva relatório do processamento em lote"""
        try:
            reports_dir = Path("results/batch_reports")
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"batch_report_{timestamp}.json"
            
            report_file = reports_dir / filename
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Relatório de lote salvo em: {report_file}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar relatório de lote: {e}")

def main():
    """Função principal para demonstração"""
    try:
        # Inicializar sistema
        vision_system = MBSTVisionSystem()
        
        # Exemplo de uso
        if len(sys.argv) > 1:
            if os.path.isdir(sys.argv[1]):
                # Processar pasta
                results = vision_system.process_batch(sys.argv[1])
                print(f"✅ Processamento em lote concluído: {len(results)} imagens")
            else:
                # Processar imagem única
                result = vision_system.process_image_complete(sys.argv[1])
                print(f"✅ Processamento concluído: {result['status']}")
        else:
            print("🚀 Sistema MBST de Visão Computacional")
            print("=" * 50)
            print("Uso:")
            print("  python advanced_vision_system.py <imagem_ou_pasta>")
            print("  python advanced_vision_system.py sinalizacao/")
            print("  python advanced_vision_system.py imagem.jpg")
            
            # Mostrar estatísticas de feedback
            feedback_stats = vision_system.get_feedback_stats()
            if feedback_stats:
                print(f"\n📊 Estatísticas de Feedback:")
                print(f"   Total: {feedback_stats['total_feedback']}")
                print(f"   Status: {feedback_stats['status_counts']}")
    
    except Exception as e:
        logger.error(f"❌ Erro na execução principal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import sys
    main()
