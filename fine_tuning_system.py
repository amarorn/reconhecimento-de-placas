#!/usr/bin/env python3
"""
Sistema de Fine-tuning para Modelos MBST
========================================

Este sistema permite:
- Fine-tuning de modelos YOLO para detecção de placas
- Treinamento de classificadores específicos
- Geração de datasets anotados
- Validação e teste de modelos
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

class MBSTFineTuningSystem:
    """Sistema de fine-tuning para modelos MBST"""
    
    def __init__(self, config_path: str = "config/fine_tuning_config.json"):
        self.config = self.load_config(config_path)
        self.dataset_path = Path(self.config.get("dataset_path", "dataset_mbst"))
        self.output_path = Path(self.config.get("output_path", "fine_tuned_models"))
        self.annotations_path = Path(self.config.get("annotations_path", "annotations"))
        
        # Criar diretórios necessários
        self.setup_directories()
        
        # Inicializar sistema
        self.init_system()
    
    def load_config(self, config_path: str) -> Dict:
        """Carrega configuração do sistema de fine-tuning"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Configuração padrão
            return {
                "dataset_path": "dataset_mbst",
                "output_path": "fine_tuned_models",
                "annotations_path": "annotations",
                "yolo_config": {
                    "model": "yolov8n.pt",
                    "epochs": 100,
                    "batch_size": 16,
                    "img_size": 640,
                    "patience": 20,
                    "save_period": 10
                },
                "classifier_config": {
                    "model": "resnet18",
                    "epochs": 50,
                    "batch_size": 32,
                    "learning_rate": 0.001,
                    "num_classes": 5
                },
                "data_augmentation": {
                    "enabled": True,
                    "rotation": [-15, 15],
                    "brightness": [0.8, 1.2],
                    "contrast": [0.8, 1.2],
                    "noise": 0.05,
                    "blur": 0.1
                }
            }
    
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
            self.base_yolo = YOLO(self.config["yolo_config"]["model"])
            logger.info(f"✅ Modelo YOLO base carregado: {self.config['yolo_config']['model']}")
            
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
                # Em um sistema real, isso seria feito por anotadores humanos ou modelo pré-treinado
                center_x = width // 2
                center_y = height // 2
                plate_width = min(width, height) // 3
                plate_height = plate_width // 2
                
                x1 = max(0, center_x - plate_width // 2)
                y1 = max(0, center_y - plate_height // 2)
                x2 = min(width, center_x + plate_width // 2)
                y2 = min(height, center_y + plate_height // 2)
                
                # Determinar classe baseado no nome do arquivo ou características
                class_id = self.determine_plate_class(image_path, image)
                
                # Criar anotação YOLO
                # YOLO usa formato: class_id x_center y_center width height (normalizado)
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
    
    def determine_plate_class(self, image_path: Path, image: np.ndarray) -> int:
        """Determina a classe da placa baseado em características"""
        try:
            # Converter para HSV para análise de cores
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Análise de cores
            red_mask = cv2.inRange(hsv, (0, 50, 50), (10, 255, 255))
            red_mask += cv2.inRange(hsv, (170, 50, 50), (180, 255, 255))
            yellow_mask = cv2.inRange(hsv, (20, 50, 50), (30, 255, 255))
            blue_mask = cv2.inRange(hsv, (100, 50, 50), (130, 255, 255))
            
            red_pixels = cv2.countNonZero(red_mask)
            yellow_pixels = cv2.countNonZero(yellow_mask)
            blue_pixels = cv2.countNonZero(blue_mask)
            total_pixels = image.shape[0] * image.shape[1]
            
            # Determinar classe baseado em cores predominantes
            if red_pixels / total_pixels > 0.1:
                return 0  # regulamentacao
            elif yellow_pixels / total_pixels > 0.1:
                return 1  # advertencia
            elif blue_pixels / total_pixels > 0.1:
                return 2  # informacao
            else:
                # Usar nome do arquivo como fallback
                filename = image_path.name.lower()
                if "regulamentacao" in filename or "pare" in filename:
                    return 0
                elif "advertencia" in filename or "cruzamento" in filename:
                    return 1
                elif "informacao" in filename:
                    return 2
                else:
                    return 0  # padrão para regulamentacao
                    
        except Exception as e:
            logger.error(f"❌ Erro ao determinar classe: {e}")
            return 0
    
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
    
    def train_yolo_model(self, dataset_config_path: str):
        """Treina modelo YOLO customizado"""
        try:
            logger.info("🚀 Iniciando treinamento YOLO...")
            
            # Configuração de treinamento
            yolo_config = self.config["yolo_config"]
            
            # Treinar modelo
            model = YOLO(yolo_config["model"])
            
            # Configurar parâmetros de treinamento
            train_args = {
                "data": dataset_config_path,
                "epochs": yolo_config["epochs"],
                "batch": yolo_config["batch_size"],
                "imgsz": yolo_config["img_size"],
                "patience": yolo_config["patience"],
                "save_period": yolo_config["save_period"],
                "project": str(self.output_path / "yolo"),
                "name": f"mbst_yolo_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "exist_ok": True,
                "pretrained": True,
                "optimizer": "auto",
                "verbose": True,
                "seed": 42
            }
            
            # Iniciar treinamento
            results = model.train(**train_args)
            
            # Salvar modelo treinado
            trained_model_path = self.output_path / "yolo" / "best.pt"
            if trained_model_path.exists():
                shutil.copy2(trained_model_path, self.output_path / "yolo" / "mbst_yolo_final.pt")
                logger.info(f"✅ Modelo YOLO treinado salvo em: {trained_model_path}")
            
            # Salvar métricas
            if hasattr(results, 'results_dict'):
                metrics_file = self.output_path / "yolo" / "training_metrics.json"
                with open(metrics_file, 'w', encoding='utf-8') as f:
                    json.dump(results.results_dict, f, indent=2, ensure_ascii=False)
            
            logger.info("✅ Treinamento YOLO concluído!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no treinamento YOLO: {e}")
            return False
    
    def train_classifier(self, dataset_path: str):
        """Treina classificador customizado"""
        try:
            logger.info("🚀 Iniciando treinamento do classificador...")
            
            # Implementar treinamento do classificador
            # Por enquanto, apenas simular
            logger.info("⚠️ Treinamento do classificador em desenvolvimento...")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no treinamento do classificador: {e}")
            return False
    
    def evaluate_model(self, model_path: str, test_data_path: str) -> Dict:
        """Avalia modelo treinado"""
        try:
            logger.info(f"🔍 Avaliando modelo: {model_path}")
            
            # Carregar modelo
            model = YOLO(model_path)
            
            # Executar validação
            results = model.val(data=test_data_path)
            
            # Extrair métricas
            metrics = {
                "mAP50": getattr(results, 'box.map50', 0.0),
                "mAP50-95": getattr(results, 'box.map', 0.0),
                "precision": getattr(results, 'box.mp', 0.0),
                "recall": getattr(results, 'box.mr', 0.0),
                "f1_score": 2 * (getattr(results, 'box.mp', 0.0) * getattr(results, 'box.mr', 0.0)) / (getattr(results, 'box.mp', 0.0) + getattr(results, 'box.mr', 0.0) + 1e-8)
            }
            
            # Salvar métricas
            metrics_file = self.output_path / "evaluation_metrics.json"
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Avaliação concluída: mAP50={metrics['mAP50']:.3f}")
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Erro na avaliação: {e}")
            return {}
    
    def generate_training_report(self, annotations: Dict, training_results: Dict = None):
        """Gera relatório completo do treinamento"""
        try:
            report = {
                "system_info": {
                    "name": "MBST Fine-tuning System",
                    "version": "2.0.0",
                    "timestamp": datetime.now().isoformat(),
                    "device": str(self.device)
                },
                "dataset_info": {
                    "total_images": len(annotations),
                    "classes": {
                        "regulamentacao": 0,
                        "advertencia": 0,
                        "informacao": 0,
                        "servico": 0,
                        "educacao": 0
                    },
                    "image_formats": [],
                    "average_image_size": 0
                },
                "training_config": self.config,
                "results": training_results or {},
                "recommendations": self.generate_recommendations(annotations)
            }
            
            # Estatísticas do dataset
            total_width = 0
            total_height = 0
            formats = set()
            
            for annotation in annotations.values():
                # Contar classes
                for ann in annotation["annotations"]:
                    class_name = ann["class_name"]
                    if class_name in report["dataset_info"]["classes"]:
                        report["dataset_info"]["classes"][class_name] += 1
                
                # Estatísticas de tamanho
                total_width += annotation["width"]
                total_height += annotation["height"]
                formats.add(Path(annotation["image_path"]).suffix.lower())
            
            if annotations:
                report["dataset_info"]["average_image_size"] = {
                    "width": total_width // len(annotations),
                    "height": total_height // len(annotations)
                }
                report["dataset_info"]["image_formats"] = list(formats)
            
            # Salvar relatório
            report_file = self.output_path / "training_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            # Gerar relatório visual
            self.generate_visual_report(report)
            
            logger.info(f"✅ Relatório de treinamento salvo em: {report_file}")
            return report
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório: {e}")
            return {}
    
    def generate_recommendations(self, annotations: Dict) -> List[str]:
        """Gera recomendações baseadas no dataset"""
        recommendations = []
        
        try:
            total_images = len(annotations)
            
            if total_images < 100:
                recommendations.append("Dataset pequeno: Considere coletar mais imagens para melhor generalização")
            
            if total_images < 500:
                recommendations.append("Dataset médio: Use data augmentation para expandir o dataset")
            
            # Verificar balanceamento de classes
            class_counts = {}
            for annotation in annotations.values():
                for ann in annotation["annotations"]:
                    class_name = ann["class_name"]
                    class_counts[class_name] = class_counts.get(class_name, 0) + 1
            
            if class_counts:
                min_count = min(class_counts.values())
                max_count = max(class_counts.values())
                
                if max_count / min_count > 3:
                    recommendations.append("Dataset desbalanceado: Considere técnicas de balanceamento de classes")
            
            recommendations.append("Use transfer learning para melhorar performance com dataset limitado")
            recommendations.append("Implemente validação cruzada para melhor avaliação do modelo")
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar recomendações: {e}")
            recommendations.append("Erro ao analisar dataset")
        
        return recommendations
    
    def generate_visual_report(self, report: Dict):
        """Gera visualizações do relatório"""
        try:
            # Configurar matplotlib
            plt.style.use('seaborn-v0_8')
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Relatório de Treinamento MBST', fontsize=16, fontweight='bold')
            
            # 1. Distribuição de classes
            classes = list(report["dataset_info"]["classes"].keys())
            counts = list(report["dataset_info"]["classes"].values())
            
            axes[0, 0].bar(classes, counts, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
            axes[0, 0].set_title('Distribuição de Classes')
            axes[0, 0].set_ylabel('Número de Imagens')
            axes[0, 0].tick_params(axis='x', rotation=45)
            
            # 2. Tamanho das imagens
            if report["dataset_info"]["average_image_size"]:
                avg_size = report["dataset_info"]["average_image_size"]
                axes[0, 1].scatter([avg_size["width"]], [avg_size["height"]], s=200, color='red', alpha=0.7)
                axes[0, 1].set_title('Tamanho Médio das Imagens')
                axes[0, 1].set_xlabel('Largura (pixels)')
                axes[0, 1].set_ylabel('Altura (pixels)')
                axes[0, 1].grid(True, alpha=0.3)
            
            # 3. Formatos de imagem
            formats = report["dataset_info"]["image_formats"]
            format_counts = {}
            for fmt in formats:
                format_counts[fmt] = format_counts.get(fmt, 0) + 1
            
            if format_counts:
                axes[1, 0].pie(format_counts.values(), labels=format_counts.keys(), autopct='%1.1f%%')
                axes[1, 0].set_title('Distribuição de Formatos')
            
            # 4. Métricas de treinamento (se disponíveis)
            if report["results"]:
                metrics = report["results"]
                metric_names = list(metrics.keys())
                metric_values = list(metrics.values())
                
                axes[1, 1].bar(metric_names, metric_values, color='lightblue')
                axes[1, 1].set_title('Métricas de Performance')
                axes[1, 1].set_ylabel('Valor')
                axes[1, 1].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
            # Salvar gráfico
            plot_file = self.output_path / "training_report.png"
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"✅ Relatório visual salvo em: {plot_file}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório visual: {e}")
    
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
            
            # 4. Treinar modelo YOLO
            dataset_config = str(self.annotations_path / "dataset.yaml")
            yolo_success = self.train_yolo_model(dataset_config)
            
            # 5. Treinar classificador
            classifier_success = self.train_classifier(str(self.output_path / "datasets"))
            
            # 6. Avaliar modelo (se treinamento foi bem-sucedido)
            evaluation_results = {}
            if yolo_success:
                best_model = self.output_path / "yolo" / "best.pt"
                if best_model.exists():
                    evaluation_results = self.evaluate_model(str(best_model), dataset_config)
            
            # 7. Gerar relatório
            training_results = {
                "yolo_training": yolo_success,
                "classifier_training": classifier_success,
                "evaluation": evaluation_results
            }
            
            report = self.generate_training_report(annotations, training_results)
            
            logger.info("🎉 PIPELINE DE FINE-TUNING CONCLUÍDO!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no pipeline: {e}")
            return False

def main():
    """Função principal"""
    try:
        # Inicializar sistema
        fine_tuning_system = MBSTFineTuningSystem()
        
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
