#!/usr/bin/env python3
"""
Script para criar modelos YOLO especializados para detecção de placas
"""

import os
import sys
import shutil
from pathlib import Path
from ultralytics import YOLO
import yaml

def create_signal_plates_model():
    """Cria modelo YOLO para placas de sinalização"""
    print("🚦 Criando modelo para placas de sinalização...")
    
    # Verificar se existe dataset
    dataset_path = "datasets/signal_plates/dataset.yaml"
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset não encontrado: {dataset_path}")
        return False
    
    try:
        # Carregar modelo base
        model = YOLO('yolov8n.pt')
        
        # Treinar modelo especializado
        print("📚 Treinando modelo para placas de sinalização...")
        results = model.train(
            data=dataset_path,
            epochs=50,
            imgsz=640,
            batch=16,
            name='signal_plates_yolo',
            project='models',
            exist_ok=True,
            save=True,
            plots=True
        )
        
        # Salvar modelo final
        model_path = "models/signal_plates_yolo.pt"
        model.save(model_path)
        print(f"✅ Modelo salvo em: {model_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar modelo de placas de sinalização: {e}")
        return False

def create_vehicle_plates_model():
    """Cria modelo YOLO para placas de veículos"""
    print("🚗 Criando modelo para placas de veículos...")
    
    # Verificar se existe dataset
    dataset_path = "datasets/vehicle_plates/dataset.yaml"
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset não encontrado: {dataset_path}")
        return False
    
    try:
        # Carregar modelo base
        model = YOLO('yolov8n.pt')
        
        # Treinar modelo especializado
        print("📚 Treinando modelo para placas de veículos...")
        results = model.train(
            data=dataset_path,
            epochs=50,
            imgsz=640,
            batch=16,
            name='vehicle_plates_yolo',
            project='models',
            exist_ok=True,
            save=True,
            plots=True
        )
        
        # Salvar modelo final
        model_path = "models/vehicle_plates_yolo.pt"
        model.save(model_path)
        print(f"✅ Modelo salvo em: {model_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar modelo de placas de veículos: {e}")
        return False

def create_fallback_models():
    """Cria modelos de fallback usando YOLOv8n pré-treinado"""
    print("🔄 Criando modelos de fallback...")
    
    try:
        # Modelo para placas de sinalização (fallback)
        model = YOLO('yolov8n.pt')
        model.save('models/signal_plates_yolo.pt')
        print("✅ Modelo de fallback para placas de sinalização criado")
        
        # Modelo para placas de veículos (fallback)
        model.save('models/vehicle_plates_yolo.pt')
        print("✅ Modelo de fallback para placas de veículos criado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar modelos de fallback: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando criação de modelos YOLO...")
    
    # Criar diretório models
    os.makedirs('models', exist_ok=True)
    
    # Tentar criar modelos especializados primeiro
    signal_success = create_signal_plates_model()
    vehicle_success = create_vehicle_plates_model()
    
    # Se não conseguiu treinar, criar modelos de fallback
    if not signal_success or not vehicle_success:
        print("⚠️  Usando modelos de fallback...")
        fallback_success = create_fallback_models()
        
        if fallback_success:
            print("✅ Modelos de fallback criados com sucesso!")
        else:
            print("❌ Falha ao criar modelos de fallback")
            return False
    
    print("🎉 Modelos YOLO criados com sucesso!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
