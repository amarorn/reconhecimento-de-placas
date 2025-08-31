

import os
import json
import shutil
import random
from pathlib import Path
from typing import List, Dict, Any
import cv2
import numpy as np
from PIL import Image
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrainingDataPreparer:
    
    def __init__(self, base_dir: str = "datasets"):
        self.base_dir = Path(base_dir)
        self.signal_dir = self.base_dir / "signal_plates"
        self.vehicle_dir = self.base_dir / "vehicle_plates"
        
        self._create_directories()
        
        self.dataset_configs = {
            "signal_plates": {
                "train_ratio": 0.7,
                "val_ratio": 0.2,
                "test_ratio": 0.1,
                "classes": [
                    "stop_sign", "yield_sign", "speed_limit", "no_parking",
                    "one_way", "pedestrian_crossing", "school_zone", "construction",
                    "warning", "information", "street_sign", "building_sign",
                    "traffic_light", "railroad_crossing", "bicycle_lane", "bus_lane"
                ]
            },
            "vehicle_plates": {
                "train_ratio": 0.7,
                "val_ratio": 0.2,
                "test_ratio": 0.1,
                "vehicle_classes": [
                    "car", "truck", "motorcycle", "bus", "van", "tractor"
                ],
                "plate_classes": [
                    "mercosul_plate", "mercosul_motorcycle_plate", "old_standard_plate",
                    "diplomatic_plate", "official_plate", "temporary_plate"
                ]
            }
        }
    
    def _create_directories(self):
        directories = [
            self.signal_dir / "images" / "train",
            self.signal_dir / "images" / "val",
            self.signal_dir / "images" / "test",
            self.signal_dir / "labels" / "train",
            self.signal_dir / "labels" / "val",
            self.signal_dir / "labels" / "test",
            self.vehicle_dir / "images" / "train",
            self.vehicle_dir / "images" / "val",
            self.vehicle_dir / "images" / "test",
            self.vehicle_dir / "labels" / "train",
            self.vehicle_dir / "labels" / "val",
            self.vehicle_dir / "labels" / "test"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Diretório criado: {directory}")
    
    def prepare_signal_plates_dataset(self, source_dir: str):
        logger.info("Preparando dataset de placas de sinalização...")
        
        source_path = Path(source_dir)
        if not source_path.exists():
            logger.error(f"Diretório fonte não encontrado: {source_dir}")
            return
        
        image_files = list(source_path.glob("*.jpg")) + list(source_path.glob("*.png"))
        random.shuffle(image_files)
        
        total_images = len(image_files)
        train_count = int(total_images * self.dataset_configs["signal_plates"]["train_ratio"])
        val_count = int(total_images * self.dataset_configs["signal_plates"]["val_ratio"])
        
        train_files = image_files[:train_count]
        val_files = image_files[train_count:train_count + val_count]
        test_files = image_files[train_count + val_count:]
        
        self._process_signal_files(train_files, "train")
        self._process_signal_files(val_files, "val")
        self._process_signal_files(test_files, "test")
        
        self._create_yolo_config("signal_plates")
        
        logger.info(f"Dataset de placas de sinalização preparado: {total_images} imagens")
    
    def prepare_vehicle_plates_dataset(self, source_dir: str):
        logger.info("Preparando dataset de placas de veículos...")
        
        source_path = Path(source_dir)
        if not source_path.exists():
            logger.error(f"Diretório fonte não encontrado: {source_dir}")
            return
        
        image_files = list(source_path.glob("*.jpg")) + list(source_path.glob("*.png"))
        random.shuffle(image_files)
        
        total_images = len(image_files)
        train_count = int(total_images * self.dataset_configs["vehicle_plates"]["train_ratio"])
        val_count = int(total_images * self.dataset_configs["vehicle_plates"]["val_ratio"])
        
        train_files = image_files[:train_count]
        val_files = image_files[train_count:train_count + val_count]
        test_files = image_files[train_count + val_count:]
        
        self._process_vehicle_files(train_files, "train")
        self._process_vehicle_files(val_files, "val")
        self._process_vehicle_files(test_files, "test")
        
        self._create_yolo_config("vehicle_plates")
        
        logger.info(f"Dataset de placas de veículos preparado: {total_images} imagens")
    
    def _process_signal_files(self, files: List[Path], split: str):
        for i, image_file in enumerate(files):
            try:
                dest_image = self.signal_dir / "images" / split / f"{split}_{i:04d}.jpg"
                shutil.copy2(image_file, dest_image)
                
                annotation_file = image_file.with_suffix(".txt")
                if annotation_file.exists():
                    dest_label = self.signal_dir / "labels" / split / f"{split}_{i:04d}.txt"
                    self._convert_annotation_format(annotation_file, dest_label, "signal")
                
                logger.debug(f"Processado: {image_file.name} -> {split}")
                
            except Exception as e:
                logger.warning(f"Erro ao processar {image_file}: {e}")
    
    def _process_vehicle_files(self, files: List[Path], split: str):
        for i, image_file in enumerate(files):
            try:
                dest_image = self.vehicle_dir / "images" / split / f"{split}_{i:04d}.jpg"
                shutil.copy2(image_file, dest_image)
                
                annotation_file = image_file.with_suffix(".txt")
                if annotation_file.exists():
                    dest_label = self.vehicle_dir / "labels" / split / f"{split}_{i:04d}.txt"
                    self._convert_annotation_format(annotation_file, dest_label, "vehicle")
                
                logger.debug(f"Processado: {image_file.name} -> {split}")
                
            except Exception as e:
                logger.warning(f"Erro ao processar {image_file}: {e}")
    
    def _convert_annotation_format(self, source_file: Path, dest_file: Path, dataset_type: str):
        try:
            with open(source_file, 'r') as f:
                lines = f.readlines()
            
            yolo_lines = []
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 5:
                    class_id = int(parts[0])
                    x_center = float(parts[1])
                    y_center = float(parts[2])
                    width = float(parts[3])
                    height = float(parts[4])
                    
                    yolo_lines.append(f"{class_id} {x_center} {y_center} {width} {height}")
            
            with open(dest_file, 'w') as f:
                f.write('\n'.join(yolo_lines))
                
        except Exception as e:
            logger.warning(f"Erro ao converter anotação {source_file}: {e}")
    
    def _create_yolo_config(self, dataset_type: str):
        if dataset_type == "signal_plates":
            config = {
                "path": str(self.signal_dir.absolute()),
                "train": "images/train",
                "val": "images/val",
                "test": "images/test",
                "nc": len(self.dataset_configs["signal_plates"]["classes"]),
                "names": self.dataset_configs["signal_plates"]["classes"]
            }
            config_file = self.signal_dir / "dataset.yaml"
        else:
            config = {
                "path": str(self.vehicle_dir.absolute()),
                "train": "images/train",
                "val": "images/val",
                "test": "images/test",
                "nc": len(self.dataset_configs["vehicle_plates"]["vehicle_classes"]) + 
                      len(self.dataset_configs["vehicle_plates"]["plate_classes"]),
                "names": (self.dataset_configs["vehicle_plates"]["vehicle_classes"] + 
                         self.dataset_configs["vehicle_plates"]["plate_classes"])
            }
            config_file = self.vehicle_dir / "dataset.yaml"
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Configuração YOLO criada: {config_file}")
    
    def create_sample_dataset(self):
        logger.info("Criando dataset de exemplo...")
        
        self._create_sample_images("signal_plates", 50)
        self._create_sample_images("vehicle_plates", 50)
        
        logger.info("Dataset de exemplo criado com sucesso!")
    
    def _create_sample_images(self, dataset_type: str, count: int):
        if dataset_type == "signal_plates":
            base_dir = self.signal_dir
            classes = self.dataset_configs["signal_plates"]["classes"]
        else:
            base_dir = self.vehicle_dir
            classes = (self.dataset_configs["vehicle_plates"]["vehicle_classes"] + 
                      self.dataset_configs["vehicle_plates"]["plate_classes"])
        
        for i in range(count):
            img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
            
            cv2.putText(img, f"Sample {i+1}", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            image_path = base_dir / "images" / "train" / f"sample_{i:04d}.jpg"
            cv2.imwrite(str(image_path), img)
            
            label_path = base_dir / "labels" / "train" / f"sample_{i:04d}.txt"
            class_id = random.randint(0, len(classes) - 1)
            with open(label_path, 'w') as f:
                f.write(f"{class_id} 0.5 0.5 0.3 0.2")

def main():
    print("🚀 Preparador de Dados para Treinamento YOLO")
    print("=" * 50)
    
    preparer = TrainingDataPreparer()
    
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "sample":
            preparer.create_sample_dataset()
        elif sys.argv[1] == "signal" and len(sys.argv) > 2:
            preparer.prepare_signal_plates_dataset(sys.argv[2])
        elif sys.argv[1] == "vehicle" and len(sys.argv) > 2:
            preparer.prepare_vehicle_plates_dataset(sys.argv[2])
        else:
            print("Uso:")
            print("  python prepare_training_data.py sample
            print("  python prepare_training_data.py signal <source_dir>
            print("  python prepare_training_data.py vehicle <source_dir>
    else:
        print("Criando dataset de exemplo...")
        preparer.create_sample_dataset()

if __name__ == "__main__":
    main()
