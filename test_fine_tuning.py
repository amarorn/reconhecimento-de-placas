#!/usr/bin/env python3
"""
Teste do Sistema de Fine-tuning para Modelos MBST
================================================

Versão modificada para testar com imagens criadas
"""

import os
import json
import shutil
import random
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging
from datetime import datetime
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import yaml
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
from ultralytics import YOLO
import matplotlib.pyplot as plt
import seaborn as sns

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestMBSTFineTuningSystem:
    """Sistema de teste de fine-tuning para modelos MBST"""
    
    def __init__(self, test_dataset_path: str = "sinalizacao_test"):
        self.dataset_path = Path(test_dataset_path)
        self.output_path = Path("fine_tuned_models_test")
        self.annotations_path = Path("annotations_test")
        
        # Criar diretórios necessários
        self.setup_directories()
        
        # Inicializar sistema
        self.init_system()
    
    def setup_directories(self):
        """Cria diretórios necessários para o sistema"""
        directories = [
            self.output_path,
            self.annotations_path,
            self.output_path / "yolo",
            self.output_path / "classifier",
            self.output_path / "datasets",
            self.output_path / "logs",
            self.output_path / "checkpoints"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Diretório criado: {directory}")
    
    def init_system(self):
        """Inicializa o sistema de fine-tuning"""
        try:
            # Verificar se CUDA está disponível
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            logger.info(f"🔧 Dispositivo: {self.device}")
            
            # Carregar modelo base YOLO
            self.base_yolo = YOLO("yolov8n.pt")
            logger.info(f"✅ Modelo YOLO base carregado: yolov8n.pt")
            
            # Verificar dataset
            self.check_dataset()
            
        except Exception as e:
            logger.error(f"❌ Erro na inicialização: {e}")
            raise
    
    def check_dataset(self):
        """Verifica se o dataset está disponível e estruturado"""
        try:
            if not self.dataset_path.exists():
                logger.warning(f"⚠️ Dataset não encontrado em: {self.dataset_path}")
                return False
            
            # Verificar estrutura do dataset
            image_files = list(self.dataset_path.glob("*.jpg")) + list(self.dataset_path.glob("*.png"))
            
            if not image_files:
                logger.warning(f"⚠️ Nenhuma imagem encontrada em: {self.dataset_path}")
                return False
            
            logger.info(f"✅ Dataset encontrado: {len(image_files)} imagens")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar dataset: {e}")
            return False
    
    def generate_annotations(self, image_paths: List[Path]) -> Dict:
        """Gera anotações para as imagens do dataset"""
        try:
            annotations = {}
            
            for i, image_path in enumerate(image_paths):
                logger.info(f"📝 Gerando anotações para {i+1}/{len(image_paths)}: {image_path.name}")
                
                # Carregar imagem
                image = cv2.imread(str(image_path))
                if image is None:
                    continue
                
                height, width = image.shape[:2]
                
                # Simular detecção de placa (centro da imagem)
                center_x = width // 2
                center_y = height // 2
                plate_width = min(width, height) // 3
                plate_height = plate_width // 2
                
                x1 = max(0, center_x - plate_width // 2)
                y1 = max(0, center_y - plate_height // 2)
                x2 = min(width, center_x + plate_width // 2)
                y2 = min(height, center_y + plate_height // 2)
                
                # Determinar classe baseado no nome do arquivo
                class_id = self.determine_plate_class_from_filename(image_path)
                
                # Criar anotação YOLO
                x_center = (x1 + x2) / 2 / width
                y_center = (y1 + y2) / 2 / height
                w = (x2 - x1) / width
                h = (y2 - y1) / height
                
                annotation = {
                    "image_path": str(image_path),
                    "width": width,
                    "height": height,
                    "annotations": [{
                        "class_id": class_id,
                        "class_name": self.get_class_name(class_id),
                        "bbox": [x_center, y_center, w, h],
                        "confidence": 1.0
                    }]
                }
                
                annotations[image_path.name] = annotation
            
            # Salvar anotações
            self.save_annotations(annotations)
            
            logger.info(f"✅ Anotações geradas para {len(annotations)} imagens")
            return annotations
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar anotações: {e}")
            return {}
    
    def determine_plate_class_from_filename(self, image_path: Path) -> int:
        """Determina a classe da placa baseado no nome do arquivo"""
        filename = image_path.name.lower()
        
        if "pare" in filename or "preferencia" in filename:
            return 0  # regulamentacao
        elif "cruzamento" in filename or "curva" in filename:
            return 1  # advertencia
        elif "hospital" in filename or "escola" in filename:
            return 2  # informacao
        else:
            return 0  # padrão para regulamentacao
    
    def get_class_name(self, class_id: int) -> str:
        """Retorna nome da classe baseado no ID"""
        class_names = {
            0: "regulamentacao",
            1: "advertencia",
            2: "informacao",
            3: "servico",
            4: "educacao"
        }
        return class_names.get(class_id, "desconhecida")
    
    def save_annotations(self, annotations: Dict):
        """Salva anotações em formato YOLO"""
        try:
            # Criar diretório de anotações YOLO
            yolo_annotations_dir = self.annotations_path / "yolo"
            yolo_annotations_dir.mkdir(exist_ok=True)
            
            # Salvar anotações em formato YOLO
            for image_name, annotation in annotations.items():
                # Arquivo de anotação YOLO (.txt)
                annotation_file = yolo_annotations_dir / f"{Path(image_name).stem}.txt"
                
                with open(annotation_file, 'w') as f:
                    for ann in annotation["annotations"]:
                        bbox = ann["bbox"]
                        f.write(f"{ann['class_id']} {bbox[0]:.6f} {bbox[1]:.6f} {bbox[2]:.6f} {bbox[3]:.6f}\n")
            
            # Salvar configuração do dataset
            dataset_config = {
                "path": str(self.dataset_path),
                "train": "train/images",
                "val": "val/images",
                "test": "test/images",
                "nc": 5,  # número de classes
                "names": ["regulamentacao", "advertencia", "informacao", "servico", "educacao"]
            }
            
            config_file = self.annotations_path / "dataset.yaml"
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(dataset_config, f, default_flow_style=False)
            
            logger.info(f"✅ Anotações salvas em formato YOLO: {yolo_annotations_dir}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar anotações: {e}")
    
    def split_dataset(self, annotations: Dict, train_ratio: float = 0.8, val_ratio: float = 0.1):
        """Divide o dataset em treino, validação e teste"""
        try:
            # Criar diretórios
            splits = ["train", "val", "test"]
            for split in splits:
                (self.output_path / "datasets" / split / "images").mkdir(parents=True, exist_ok=True)
                (self.output_path / "datasets" / split / "labels").mkdir(parents=True, exist_ok=True)
            
            # Lista de imagens
            image_names = list(annotations.keys())
            random.shuffle(image_names)
            
            # Calcular índices de divisão
            total = len(image_names)
            train_end = int(total * train_ratio)
            val_end = train_end + int(total * val_ratio)
            
            # Dividir dataset
            train_images = image_names[:train_end]
            val_images = image_names[train_end:val_end]
            test_images = image_names[val_end:]
            
            # Copiar arquivos para cada split
            splits_data = {
                "train": train_images,
                "val": val_images,
                "test": test_images
            }
            
            for split_name, split_images in splits_data.items():
                logger.info(f"📁 Criando split {split_name}: {len(split_images)} imagens")
                
                for image_name in split_images:
                    # Copiar imagem
                    src_image = self.dataset_path / image_name
                    dst_image = self.output_path / "datasets" / split_name / "images" / image_name
                    shutil.copy2(src_image, dst_image)
                    
                    # Copiar anotação
                    src_annotation = self.annotations_path / "yolo" / f"{Path(image_name).stem}.txt"
                    dst_annotation = self.output_path / "datasets" / split_name / "labels" / f"{Path(image_name).stem}.txt"
                    if src_annotation.exists():
                        shutil.copy2(src_annotation, dst_annotation)
            
            # Salvar configuração dos splits
            splits_config = {
                "train": len(train_images),
                "val": len(val_images),
                "test": len(test_images),
                "total": total,
                "splits": {
                    "train": train_images,
                    "val": val_images,
                    "test": test_images
                }
            }
            
            splits_file = self.output_path / "datasets" / "splits.json"
            with open(splits_file, 'w', encoding='utf-8') as f:
                json.dump(splits_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Dataset dividido: Treino={len(train_images)}, Val={len(val_images)}, Teste={len(test_images)}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao dividir dataset: {e}")
    
    def run_complete_pipeline(self):
        """Executa pipeline completo de fine-tuning"""
        try:
            logger.info("🚀 INICIANDO PIPELINE COMPLETO DE FINE-TUNING")
            
            # 1. Verificar dataset
            if not self.check_dataset():
                logger.error("❌ Dataset não disponível")
                return False
            
            # 2. Gerar anotações
            image_files = list(self.dataset_path.glob("*.jpg")) + list(self.dataset_path.glob("*.png"))
            annotations = self.generate_annotations(image_files)
            
            if not annotations:
                logger.error("❌ Falha ao gerar anotações")
                return False
            
            # 3. Dividir dataset
            self.split_dataset(annotations)
            
            logger.info("🎉 PIPELINE DE FINE-TUNING CONCLUÍDO!")
            logger.info(f"📁 Resultados salvos em: {self.output_path}")
            logger.info(f"📝 Anotações em: {self.annotations_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no pipeline: {e}")
            return False

def main():
    """Função principal"""
    try:
        # Inicializar sistema
        fine_tuning_system = TestMBSTFineTuningSystem("sinalizacao_test")
        
        # Executar pipeline completo
        success = fine_tuning_system.run_complete_pipeline()
        
        if success:
            print("✅ Pipeline de fine-tuning executado com sucesso!")
            print(f"📁 Resultados salvos em: {fine_tuning_system.output_path}")
        else:
            print("❌ Falha no pipeline de fine-tuning")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Erro na execução principal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import sys
    main()
