#!/usr/bin/env python3
"""
Script para treinar modelo YOLO com dataset personalizado
"""

import os
import sys
from ultralytics import YOLO
import yaml

def train_yolo_model(dataset_name, epochs=50, batch_size=16):
    """Treina modelo YOLO com dataset personalizado"""
    print(f"🚀 Iniciando treinamento do modelo YOLO para: {dataset_name}")
    
    dataset_path = f"datasets/{dataset_name}/dataset.yaml"
    
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset não encontrado: {dataset_path}")
        return False
    
    try:
        # Carregar modelo base
        model = YOLO('yolov8n.pt')
        
        # Treinar modelo
        print("📚 Iniciando treinamento...")
        results = model.train(
            data=dataset_path,
            epochs=epochs,
            imgsz=640,
            batch=batch_size,
            name=f'{dataset_name}_trained',
            project='models',
            exist_ok=True,
            save=True,
            plots=True,
            verbose=True
        )
        
        # Salvar modelo final
        final_model_path = f"models/{dataset_name}_yolo.pt"
        model.save(final_model_path)
        
        print(f"✅ Treinamento concluído!")
        print(f"📁 Modelo salvo em: {final_model_path}")
        
        # Mostrar métricas finais
        print(f"\n📊 Métricas do treinamento:")
        print(f"   - Epochs: {epochs}")
        print(f"   - Batch size: {batch_size}")
        print(f"   - Dataset: {dataset_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o treinamento: {e}")
        return False

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("❌ Uso: python train_yolo_model.py <nome_do_dataset> [epochs] [batch_size]")
        print("   Exemplo: python train_yolo_model.py signal_plates_pdf 50 16")
        return False
    
    dataset_name = sys.argv[1]
    epochs = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    batch_size = int(sys.argv[3]) if len(sys.argv) > 3 else 16
    
    success = train_yolo_model(dataset_name, epochs, batch_size)
    
    if success:
        print(f"\n🎉 Modelo treinado com sucesso!")
        print(f"📝 Para usar o modelo, atualize o caminho em:")
        print(f"   - vision/detection/signal_plate_detector.py")
        print(f"   - vision/detection/vehicle_plate_detector.py")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
