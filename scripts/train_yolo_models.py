#!/usr/bin/env python3

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging
import argparse

sys.path.append(str(Path(__file__).parent.parent))

try:
    from ultralytics import YOLO
    from ultralytics.utils import LOGGER
except ImportError:
    print("❌ Ultralytics não encontrado. Instale com: pip install ultralytics")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YOLOModelTrainer:
    
    def __init__(self, config_file: str = "config/yolo_models.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
        
        self.base_dir = Path("datasets")
        self.signal_dir = self.base_dir / "signal_plates"
        self.vehicle_dir = self.base_dir / "vehicle_plates"
        
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        
        self.training_configs = {
            "signal_plates": {
                "model": "yolov8n.pt",
                "epochs": 100,
                "batch_size": 16,
                "imgsz": 640,
                "patience": 20,
                "save_period": 10,
                "device": "auto",
                "workers": 4,
                "project": "runs/signal_plates",
                "name": "train"
            },
            "vehicle_plates": {
                "model": "yolov8n.pt",
                "epochs": 150,
                "batch_size": 16,
                "imgsz": 640,
                "patience": 25,
                "save_period": 15,
                "device": "auto",
                "workers": 4,
                "project": "runs/vehicle_plates",
                "name": "train"
            }
        }
    
    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Arquivo de configuração não encontrado: {self.config_file}")
            return {}
        except json.JSONDecodeError:
            logger.error(f"Erro ao decodificar JSON: {self.config_file}")
            return {}
    
    def check_dataset_ready(self, dataset_type: str) -> bool:
        if dataset_type == "signal_plates":
            dataset_dir = self.signal_dir
        else:
            dataset_dir = self.vehicle_dir
        
        required_dirs = [
            dataset_dir / "images" / "train",
            dataset_dir / "images" / "val",
            dataset_dir / "labels" / "train",
            dataset_dir / "labels" / "val"
        ]
        
        for dir_path in required_dirs:
            if not dir_path.exists():
                logger.error(f"Diretório não encontrado: {dir_path}")
                return False
        
        train_images = list((dataset_dir / "images" / "train").glob("*.jpg"))
        train_labels = list((dataset_dir / "labels" / "train").glob("*.txt"))
        
        if len(train_images) == 0:
            logger.error(f"Nenhuma imagem de treinamento encontrada em {dataset_dir}")
            return False
        
        if len(train_labels) == 0:
            logger.error(f"Nenhuma anotação de treinamento encontrada em {dataset_dir}")
            return False
        
        logger.info(f"Dataset {dataset_type} está pronto: {len(train_images)} imagens, {len(train_labels)} anotações")
        return True
    
    def train_signal_plates_model(self, custom_config: Optional[Dict[str, Any]] = None):
        logger.info("🚦 Iniciando treinamento do modelo de placas de sinalização...")
        
        if not self.check_dataset_ready("signal_plates"):
            logger.error("Dataset de placas de sinalização não está pronto")
            return False
        
        try:
            config = self.training_configs["signal_plates"].copy()
            if custom_config:
                config.update(custom_config)
            
            model = YOLO(config["model"])
            
            dataset_yaml = self.signal_dir / "dataset.yaml"
            if not dataset_yaml.exists():
                logger.error(f"Arquivo de configuração do dataset não encontrado: {dataset_yaml}")
                return False
            
            logger.info(f"Configuração de treinamento: {config}")
            logger.info(f"Dataset: {dataset_yaml}")
            
            results = model.train(
                data=str(dataset_yaml),
                epochs=config["epochs"],
                batch=config["batch_size"],
                imgsz=config["imgsz"],
                patience=config["patience"],
                save_period=config["save_period"],
                device=config["device"],
                workers=config["workers"],
                project=config["project"],
                name=config["name"]
            )
            
            best_model_path = results.save_dir / "weights" / "best.pt"
            if best_model_path.exists():
                dest_path = self.models_dir / "signal_plates_yolo.pt"
                import shutil
                shutil.copy2(best_model_path, dest_path)
                logger.info(f"✅ Modelo treinado salvo em: {dest_path}")
                
                self._update_model_config("signal_plates", str(dest_path))
                return True
            else:
                logger.error("Modelo treinado não encontrado")
                return False
                
        except Exception as e:
            logger.error(f"Erro durante treinamento: {e}")
            return False
    
    def train_vehicle_plates_model(self, custom_config: Optional[Dict[str, Any]] = None):
        logger.info("🚗 Iniciando treinamento do modelo de placas de veículos...")
        
        if not self.check_dataset_ready("vehicle_plates"):
            logger.error("Dataset de placas de veículos não está pronto")
            return False
        
        try:
            config = self.training_configs["vehicle_plates"].copy()
            if custom_config:
                config.update(custom_config)
            
            model = YOLO(config["model"])
            
            dataset_yaml = self.vehicle_dir / "dataset.yaml"
            if not dataset_yaml.exists():
                logger.error(f"Arquivo de configuração do dataset não encontrado: {dataset_yaml}")
                return False
            
            logger.info(f"Configuração de treinamento: {config}")
            logger.info(f"Dataset: {dataset_yaml}")
            
            results = model.train(
                data=str(dataset_yaml),
                epochs=config["epochs"],
                batch=config["batch_size"],
                imgsz=config["imgsz"],
                patience=config["patience"],
                save_period=config["save_period"],
                device=config["device"],
                workers=config["workers"],
                project=config["project"],
                name=config["name"]
            )
            
            best_model_path = results.save_dir / "weights" / "best.pt"
            if best_model_path.exists():
                dest_path = self.models_dir / "vehicle_plates_yolo.pt"
                import shutil
                shutil.copy2(best_model_path, dest_path)
                logger.info(f"✅ Modelo treinado salvo em: {dest_path}")
                
                self._update_model_config("vehicle_plates", str(dest_path))
                return True
            else:
                logger.error("Modelo treinado não encontrado")
                return False
                
        except Exception as e:
            logger.error(f"Erro durante treinamento: {e}")
            return False
    
    def _update_model_config(self, model_type: str, model_path: str):
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                if "yolo_models" in config and model_type in config["yolo_models"]:
                    config["yolo_models"][model_type]["model_path"] = model_path
                    config["yolo_models"][model_type]["last_updated"] = "2025-08-29"
                    
                    with open(self.config_file, 'w') as f:
                        json.dump(config, f, indent=2)
                    
                    logger.info(f"Configuração atualizada para {model_type}")
                    
        except Exception as e:
            logger.warning(f"Erro ao atualizar configuração: {e}")
    
    def validate_model(self, model_path: str, test_image: str):
        try:
            model = YOLO(model_path)
            
            if not Path(test_image).exists():
                logger.warning(f"Imagem de teste não encontrada: {test_image}")
                return False
            
            results = model(test_image)
            
            for result in results:
                if result.boxes is not None:
                    logger.info(f"Detecções encontradas: {len(result.boxes)}")
                    for box in result.boxes:
                        confidence = float(box.conf[0].cpu().numpy())
                        class_id = int(box.cls[0].cpu().numpy())
                        logger.info(f"  Classe {class_id}: {confidence:.3f}")
                else:
                    logger.info("Nenhuma detecção encontrada")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na validação do modelo: {e}")
            return False
    
    def create_training_report(self, model_type: str):
        try:
            if model_type == "signal_plates":
                project_dir = Path("runs/signal_plates/train")
            else:
                project_dir = Path("runs/vehicle_plates/train")
            
            if not project_dir.exists():
                logger.warning(f"Diretório de resultados não encontrado: {project_dir}")
                return
            
            results_file = project_dir / "results.csv"
            if results_file.exists():
                import pandas as pd
                results = pd.read_csv(results_file)
                
                logger.info(f"📊 Relatório de treinamento - {model_type}")
                logger.info(f"Total de épocas: {len(results)}")
                logger.info(f"Melhor mAP50: {results['metrics/mAP50(B)'].max():.3f}")
                logger.info(f"Melhor mAP50-95: {results['metrics/mAP50-95(B)'].max():.3f}")
                logger.info(f"Menor loss: {results['train/box_loss'].min():.3f}")
            
        except Exception as e:
            logger.warning(f"Erro ao criar relatório: {e}")

def main():
    parser = argparse.ArgumentParser(description="Treinador de Modelos YOLO Especializados")
    parser.add_argument("--model", choices=["signal", "vehicle", "both"], 
                       default="both", help="Tipo de modelo para treinar")
    parser.add_argument("--epochs", type=int, help="Número de épocas personalizado")
    parser.add_argument("--batch-size", type=int, help="Tamanho do batch personalizado")
    parser.add_argument("--device", default="auto", help="Dispositivo para treinamento")
    parser.add_argument("--validate", action="store_true", help="Validar modelo após treinamento")
    parser.add_argument("--test-image", type=str, help="Imagem para validação")
    
    args = parser.parse_args()
    
    print("🚀 Treinador de Modelos YOLO Especializados")
    print("=" * 50)
    
    trainer = YOLOModelTrainer()
    
    custom_config = {}
    if args.epochs:
        custom_config["epochs"] = args.epochs
    if args.batch_size:
        custom_config["batch_size"] = args.batch_size
    if args.device:
        custom_config["device"] = args.device
    
    success = True
    
    if args.model in ["signal", "both"]:
        if not trainer.train_signal_plates_model(custom_config):
            success = False
        else:
            trainer.create_training_report("signal_plates")
    
    if args.model in ["vehicle", "both"]:
        if not trainer.train_vehicle_plates_model(custom_config):
            success = False
        else:
            trainer.create_training_report("vehicle_plates")
    
    if args.validate and args.test_image:
        if args.model in ["signal", "both"]:
            model_path = "models/signal_plates_yolo.pt"
            if Path(model_path).exists():
                logger.info("🔍 Validando modelo de placas de sinalização...")
                trainer.validate_model(model_path, args.test_image)
        
        if args.model in ["vehicle", "both"]:
            model_path = "models/vehicle_plates_yolo.pt"
            if Path(model_path).exists():
                logger.info("🔍 Validando modelo de placas de veículos...")
                trainer.validate_model(model_path, args.test_image)
    
    if success:
        print("✅ Treinamento concluído com sucesso!")
    else:
        print("❌ Alguns modelos falharam no treinamento")
        sys.exit(1)

if __name__ == "__main__":
    main()
