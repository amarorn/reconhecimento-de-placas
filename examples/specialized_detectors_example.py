#!/usr/bin/env python3

import cv2
import numpy as np
import yaml
import time
from pathlib import Path
import logging

from vision.detection.specialized_detector import SpecializedDetector

def load_config(config_path: str = "config/specialized_detectors.yaml") -> dict:
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        print(f"Arquivo de configuração não encontrado: {config_path}")
        return {}

def create_sample_image(width: int = 800, height: int = 600) -> np.ndarray:
    image = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Simular estrada
    cv2.rectangle(image, (0, height//2), (width, height), (128, 128, 128), -1)
    
    # Simular placas de sinalização
    cv2.rectangle(image, (50, 50), (150, 150), (0, 0, 255), -1)
    cv2.putText(image, "PARE", (60, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    cv2.rectangle(image, (200, 50), (300, 150), (0, 165, 255), -1)
    cv2.putText(image, "DÊ", (220, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Simular veículos
    cv2.rectangle(image, (400, 100), (600, 200), (255, 0, 0), -1)
    cv2.rectangle(image, (420, 120), (580, 180), (0, 255, 0), -1)
    cv2.putText(image, "ABC1234", (430, 155), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    
    # Simular buracos
    cv2.ellipse(image, (150, height//2 + 50), (30, 20), 0, 0, 360, (0, 0, 0), -1)
    cv2.ellipse(image, (400, height//2 + 100), (40, 25), 0, 0, 360, (0, 0, 0), -1)
    cv2.ellipse(image, (600, height//2 + 75), (35, 22), 0, 0, 360, (0, 0, 0), -1)
    
    return image

def main():
    print("🚀 Exemplo dos Detectores Especializados")
    print("=" * 50)
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Carregar configuração
    config = load_config()
    if not config:
        print("❌ Falha ao carregar configuração")
        return
    
    print("✅ Configuração carregada com sucesso")
    
    try:
        # Inicializar detector especializado
        print("\n🔧 Inicializando detectores especializados...")
        detector = SpecializedDetector(config)
        print("✅ Detectores inicializados")
        
        # Criar imagem de exemplo
        print("\n🖼️ Criando imagem de exemplo...")
        sample_image = create_sample_image()
        print(f"✅ Imagem criada: {sample_image.shape}")
        
        # Salvar imagem original
        cv2.imwrite("sample_image_original.jpg", sample_image)
        print("💾 Imagem original salva como 'sample_image_original.jpg'")
        
        # Detecção completa
        print("\n🔍 Executando detecção completa...")
        start_time = time.time()
        
        result = detector.detect_all(sample_image)
        
        total_time = time.time() - start_time
        print(f"✅ Detecção concluída em {total_time:.3f}s")
        
        # Exibir resultados
        print("\n📊 RESULTADOS DA DETECÇÃO:")
        print(f"   🚗 Placas/Veículos: {len(result.vehicle_plates)}")
        print(f"   🚦 Sinalização: {len(result.signal_plates)}")
        print(f"   🕳️ Buracos: {len(result.potholes)}")
        print(f"   📈 Total: {result.total_detections}")
        print(f"   ⏱️ Tempo: {result.processing_time:.3f}s")
        
        # Estatísticas detalhadas
        print("\n📈 ESTATÍSTICAS DETALHADAS:")
        stats = detector.get_comprehensive_statistics(result)
        
        if stats['vehicle_analysis']:
            vehicle_stats = stats['vehicle_analysis']
            print(f"   🚗 Veículos: {vehicle_stats.get('vehicle_count', 0)}")
            print(f"   🏷️ Placas: {vehicle_stats.get('plate_count', 0)}")
            print(f"   🎯 Confiança média: {vehicle_stats.get('average_confidence', 0):.3f}")
        
        if stats['signal_analysis']:
            signal_stats = stats['signal_analysis']
            print(f"   🚦 Regulamentação: {signal_stats.get('regulatory_count', 0)}")
            print(f"   ⚠️ Avisos: {signal_stats.get('warning_count', 0)}")
            print(f"   ℹ️ Informação: {signal_stats.get('information_count', 0)}")
        
        if stats['pothole_analysis']:
            pothole_stats = stats['pothole_analysis']
            print(f"   🕳️ Total de buracos: {pothole_stats.get('total_detections', 0)}")
            print(f"   📏 Área total: {pothole_stats.get('total_area', 0):.0f} pixels²")
            print(f"   ⚠️ Risco médio: {pothole_stats.get('average_risk_score', 0):.3f}")
            
            severity_dist = pothole_stats.get('severity_distribution', {})
            if severity_dist:
                print("   📊 Distribuição por severidade:")
                for severity, count in severity_dist.items():
                    print(f"      {severity.capitalize()}: {count}")
        
        # Relatório da estrada (se houver buracos)
        if stats['road_condition']:
            road_report = stats['road_condition']
            print(f"\n🛣️ RELATÓRIO DA ESTRADA:")
            print(f"   📊 Condição: {road_report['summary']['road_condition']}")
            print(f"   🔧 Prioridade: {road_report['summary']['maintenance_priority']}")
            
            if road_report['recommendations']:
                print("   💡 Recomendações:")
                for rec in road_report['recommendations']:
                    print(f"      • {rec}")
        
        # Desenhar detecções
        print("\n🎨 Desenhando detecções na imagem...")
        annotated_image = detector.draw_all_detections(sample_image, result)
        
        # Salvar imagem com detecções
        cv2.imwrite("sample_image_detected.jpg", annotated_image)
        print("💾 Imagem com detecções salva como 'sample_image_detected.jpg'")
        
        # Exportar resultados
        print("\n📤 Exportando resultados...")
        
        # Exportar para JSON
        json_data = detector.export_detections(result, 'json')
        with open("detections_result.json", "w", encoding="utf-8") as f:
            import json
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        print("💾 Resultados exportados para 'detections_result.json'")
        
        # Exportar para CSV
        csv_data = detector.export_detections(result, 'csv')
        with open("detections_result.csv", "w", encoding="utf-8") as f:
            f.write(csv_data)
        print("💾 Resultados exportados para 'detections_result.csv'")
        
        # Filtros de exemplo
        print("\n🔍 Aplicando filtros de exemplo...")
        
        # Filtrar por confiança alta
        high_confidence_result = detector.filter_by_confidence(result, min_confidence=0.7)
        print(f"   🎯 Detecções com confiança > 70%: {high_confidence_result.total_detections}")
        
        # Filtrar buracos de alto risco
        if result.potholes and detector.pothole_detector:
            high_risk_potholes = detector.pothole_detector.filter_high_risk(result.potholes, threshold=0.8)
            print(f"   ⚠️ Buracos de alto risco: {len(high_risk_potholes)}")
        
        print("\n🎉 Exemplo executado com sucesso!")
        print("\n📁 Arquivos gerados:")
        print("   • sample_image_original.jpg - Imagem original")
        print("   • sample_image_detected.jpg - Imagem com detecções")
        print("   • detections_result.json - Resultados em JSON")
        print("   • detections_result.csv - Resultados em CSV")
        
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if 'detector' in locals():
            detector.cleanup()
            print("\n🧹 Recursos liberados")

if __name__ == "__main__":
    main()
