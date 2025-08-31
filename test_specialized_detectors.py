#!/usr/bin/env python3

import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

def test_imports():
    print("🔍 Testando importações dos detectores especializados...")
    
    try:
        from vision.detection.vehicle_plate_detector import VehiclePlateDetector, VehiclePlateDetection
        print("✅ VehiclePlateDetector importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar VehiclePlateDetector: {e}")
    
    try:
        from vision.detection.signal_plate_detector import SignalPlateDetector, SignalPlateDetection
        print("✅ SignalPlateDetector importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar SignalPlateDetector: {e}")
    
    try:
        from vision.detection.pothole_detector import PotholeDetector, PotholeDetection
        print("✅ PotholeDetector importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar PotholeDetector: {e}")
    
    try:
        from vision.detection.specialized_detector import SpecializedDetector, UnifiedDetectionResult
        print("✅ SpecializedDetector importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar SpecializedDetector: {e}")

def test_config_loading():
    print("\n📋 Testando carregamento de configuração...")
    
    try:
        import yaml
        config_path = Path("config/specialized_detectors.yaml")
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            
            print("✅ Configuração carregada com sucesso")
            print(f"   Detectores habilitados: {config.get('enabled_detectors', [])}")
            
            if 'vehicle_detector' in config:
                print(f"   Modelo de veículos: {config['vehicle_detector'].get('model_path', 'N/A')}")
            
            if 'signal_detector' in config:
                print(f"   Modelo de sinalização: {config['signal_detector'].get('model_path', 'N/A')}")
            
            if 'pothole_detector' in config:
                print(f"   Modelo de buracos: {config['pothole_detector'].get('model_path', 'N/A')}")
            
            return config
        else:
            print(f"❌ Arquivo de configuração não encontrado: {config_path}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao carregar configuração: {e}")
        return None

def test_detector_initialization(config):
    if not config:
        print("❌ Configuração não disponível para teste")
        return
    
    print("\n🔧 Testando inicialização dos detectores...")
    
    try:
        from vision.detection.specialized_detector import SpecializedDetector
        
        detector = SpecializedDetector(config)
        print("✅ SpecializedDetector inicializado com sucesso")
        
        print(f"   Detectores ativos: {detector.enabled_detectors}")
        print(f"   Vehicle detector: {'✅' if detector.vehicle_detector else '❌'}")
        print(f"   Signal detector: {'✅' if detector.signal_detector else '❌'}")
        print(f"   Pothole detector: {'✅' if detector.pothole_detector else '❌'}")
        
        detector.cleanup()
        print("✅ Cleanup executado com sucesso")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar detector: {e}")
        import traceback
        traceback.print_exc()

def test_data_structures():
    print("\n🏗️ Testando estruturas de dados...")
    
    try:
        from vision.detection.vehicle_plate_detector import VehiclePlateDetection
        from vision.detection.signal_plate_detector import SignalPlateDetection
        from vision.detection.pothole_detector import PotholeDetection
        from vision.detection.specialized_detector import UnifiedDetectionResult
        
        # Testar VehiclePlateDetection
        vehicle_detection = VehiclePlateDetection(
            bbox=(100, 100, 200, 150),
            confidence=0.85,
            class_name="car",
            plate_type="mercosul_plate",
            vehicle_type="car"
        )
        print("✅ VehiclePlateDetection criado com sucesso")
        
        # Testar SignalPlateDetection
        signal_detection = SignalPlateDetection(
            bbox=(50, 50, 150, 150),
            confidence=0.92,
            class_name="stop_sign",
            signal_type="stop_sign",
            signal_category="regulatory",
            regulatory_code="R-1"
        )
        print("✅ SignalPlateDetection criado com sucesso")
        
        # Testar PotholeDetection
        pothole_detection = PotholeDetection(
            bbox=(300, 300, 400, 350),
            confidence=0.78,
            class_name="medium_pothole",
            pothole_type="medium_pothole",
            severity_level="medium",
            depth_estimate=0.10,
            area_estimate=5000,
            risk_score=0.65
        )
        print("✅ PotholeDetection criado com sucesso")
        
        # Testar UnifiedDetectionResult
        unified_result = UnifiedDetectionResult(
            vehicle_plates=[vehicle_detection],
            signal_plates=[signal_detection],
            potholes=[pothole_detection],
            processing_time=0.5,
            total_detections=3,
            metadata={'test': True}
        )
        print("✅ UnifiedDetectionResult criado com sucesso")
        
        print(f"   Total de detecções: {unified_result.total_detections}")
        print(f"   Tempo de processamento: {unified_result.processing_time}s")
        
    except Exception as e:
        print(f"❌ Erro ao testar estruturas de dados: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("🧪 Teste dos Detectores Especializados")
    print("=" * 50)
    
    test_imports()
    config = test_config_loading()
    test_detector_initialization(config)
    test_data_structures()
    
    print("\n🎉 Teste concluído!")
    print("\n📋 Próximos passos:")
    print("   1. Instalar dependências: pip install ultralytics opencv-python pyyaml")
    print("   2. Baixar modelos YOLO para cada detector")
    print("   3. Executar exemplo: python examples/specialized_detectors_example.py")

if __name__ == "__main__":
    main()
