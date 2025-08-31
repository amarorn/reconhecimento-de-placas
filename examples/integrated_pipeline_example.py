#!/usr/bin/env python3

import cv2
import numpy as np
import yaml
import time
import json
from pathlib import Path
import logging

from vision.core.vision_pipeline import VisionPipeline, PipelineResult
from vision.detection.specialized_detector import SpecializedDetector

def load_config(config_path: str = "config/pipeline_with_specialized.yaml") -> dict:
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        print(f"Arquivo de configuração não encontrado: {config_path}")
        return {}

def create_sample_image(width: int = 1024, height: int = 768) -> np.ndarray:
    image = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Simular estrada
    cv2.rectangle(image, (0, height//2), (width, height), (128, 128, 128), -1)
    
    # Simular placas de sinalização
    cv2.rectangle(image, (50, 50), (150, 150), (0, 0, 255), -1)
    cv2.putText(image, "PARE", (60, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    cv2.rectangle(image, (200, 50), (300, 150), (0, 165, 255), -1)
    cv2.putText(image, "DÊ", (220, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    cv2.rectangle(image, (350, 50), (450, 150), (0, 255, 0), -1)
    cv2.putText(image, "80", (370, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    # Simular veículos com placas
    cv2.rectangle(image, (400, 200), (700, 300), (255, 0, 0), -1)
    cv2.rectangle(image, (420, 220), (680, 280), (0, 255, 0), -1)
    cv2.putText(image, "ABC1234", (430, 255), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    
    cv2.rectangle(image, (100, 200), (350, 300), (0, 0, 255), -1)
    cv2.rectangle(image, (120, 220), (330, 280), (0, 255, 0), -1)
    cv2.putText(image, "XYZ7890", (130, 255), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    
    # Simular buracos na estrada
    cv2.ellipse(image, (150, height//2 + 50), (40, 25), 0, 0, 360, (0, 0, 0), -1)
    cv2.ellipse(image, (400, height//2 + 100), (50, 30), 0, 0, 360, (0, 0, 0), -1)
    cv2.ellipse(image, (600, height//2 + 75), (45, 28), 0, 0, 360, (0, 0, 0), -1)
    cv2.ellipse(image, (800, height//2 + 120), (35, 22), 0, 0, 360, (0, 0, 0), -1)
    
    return image

def analyze_pipeline_results(result: PipelineResult):
    print("\n📊 ANÁLISE DOS RESULTADOS DO PIPELINE:")
    print("=" * 50)
    
    print(f"✅ Sucesso: {result.success}")
    print(f"🖼️ Imagem: {result.image_path}")
    print(f"⏱️ Tempo de processamento: {result.processing_time:.3f}s")
    
    # Análise das detecções principais
    print(f"\n🔍 Detecções principais: {len(result.detections)}")
    if result.detections:
        confidences = [det.get('confidence', 0) for det in result.detections]
        print(f"   Confiança média: {np.mean(confidences):.3f}")
        print(f"   Confiança mínima: {np.min(confidences):.3f}")
        print(f"   Confiança máxima: {np.max(confidences):.3f}")
    
    # Análise dos resultados OCR
    print(f"\n📝 Resultados OCR: {len(result.ocr_results)}")
    if result.ocr_results:
        ocr_confidences = [ocr.get('confidence', 0) for ocr in result.ocr_results]
        print(f"   Confiança média OCR: {np.mean(ocr_confidences):.3f}")
    
    # Análise dos resultados integrados
    print(f"\n🔗 Resultados integrados: {len(result.integrated_results)}")
    if result.integrated_results:
        integrated_confidences = [res.get('confidence_score', 0) for res in result.integrated_results]
        print(f"   Confiança integrada média: {np.mean(integrated_confidences):.3f}")
    
    # Análise dos detectores especializados
    if result.specialized_results:
        print(f"\n🚀 DETECTORES ESPECIALIZADOS:")
        print(f"   🚗 Placas/Veículos: {len(result.specialized_results.vehicle_plates)}")
        print(f"   🚦 Sinalização: {len(result.specialized_results.signal_plates)}")
        print(f"   🕳️ Buracos: {len(result.specialized_results.potholes)}")
        print(f"   📈 Total especializado: {result.specialized_results.total_detections}")
        
        # Análise detalhada por tipo
        if result.specialized_results.vehicle_plates:
            vehicle_confidences = [det.confidence for det in result.specialized_results.vehicle_plates]
            print(f"      Confiança média veículos: {np.mean(vehicle_confidences):.3f}")
        
        if result.specialized_results.signal_plates:
            signal_confidences = [det.confidence for det in result.specialized_results.signal_plates]
            print(f"      Confiança média sinalização: {np.mean(signal_confidences):.3f}")
        
        if result.specialized_results.potholes:
            pothole_confidences = [det.confidence for det in result.specialized_results.potholes]
            risk_scores = [det.risk_score for det in result.specialized_results.potholes if det.risk_score]
            print(f"      Confiança média buracos: {np.mean(pothole_confidences):.3f}")
            if risk_scores:
                print(f"      Score de risco médio: {np.mean(risk_scores):.3f}")
    
    # Metadados
    if result.metadata:
        print(f"\n📋 METADADOS:")
        print(f"   Versão do pipeline: {result.metadata.get('pipeline_version', 'N/A')}")
        
        components = result.metadata.get('components', {})
        print(f"   Componentes ativos:")
        for component, active in components.items():
            status = "✅" if active else "❌"
            print(f"      {component}: {status}")
        
        if 'specialized_detection' in result.metadata:
            spec_stats = result.metadata['specialized_detection']
            print(f"   Estatísticas especializadas:")
            for key, value in spec_stats.items():
                print(f"      {key}: {value}")

def export_comprehensive_results(result: PipelineResult, output_dir: str = "results"):
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    timestamp = int(time.time())
    
    # Exportar resultados principais
    main_results = {
        'timestamp': timestamp,
        'success': result.success,
        'image_path': result.image_path,
        'processing_time': result.processing_time,
        'detections': result.detections,
        'ocr_results': result.ocr_results,
        'integrated_results': result.integrated_results,
        'metadata': result.metadata
    }
    
    with open(output_path / f"pipeline_results_{timestamp}.json", 'w', encoding='utf-8') as f:
        json.dump(main_results, f, indent=2, ensure_ascii=False, default=str)
    
    # Exportar resultados especializados
    if result.specialized_results:
        from vision.detection.specialized_detector import SpecializedDetector
        
        # Criar detector temporário para exportação
        temp_detector = SpecializedDetector({})
        specialized_data = temp_detector.export_detections(result.specialized_results, 'json')
        
        with open(output_path / f"specialized_results_{timestamp}.json", 'w', encoding='utf-8') as f:
            json.dump(specialized_data, f, indent=2, ensure_ascii=False, default=str)
        
        # Exportar CSV
        csv_data = temp_detector.export_detections(result.specialized_results, 'csv')
        with open(output_path / f"specialized_results_{timestamp}.csv", 'w', encoding='utf-8') as f:
            f.write(csv_data)
    
    print(f"\n💾 Resultados exportados para: {output_path}")

def main():
    print("🚀 Pipeline Integrado com Detectores Especializados")
    print("=" * 60)
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Carregar configuração
    config = load_config()
    if not config:
        print("❌ Falha ao carregar configuração")
        return
    
    print("✅ Configuração carregada com sucesso")
    
    try:
        # Inicializar pipeline integrado
        print("\n🔧 Inicializando pipeline integrado...")
        pipeline = VisionPipeline(config)
        print("✅ Pipeline inicializado")
        
        # Criar imagem de exemplo
        print("\n🖼️ Criando imagem de exemplo...")
        sample_image = create_sample_image()
        print(f"✅ Imagem criada: {sample_image.shape}")
        
        # Salvar imagem original
        cv2.imwrite("integrated_sample_original.jpg", sample_image)
        print("💾 Imagem original salva como 'integrated_sample_original.jpg'")
        
        # Processar imagem através do pipeline completo
        print("\n🔍 Executando pipeline completo...")
        start_time = time.time()
        
        result = pipeline.process_image("integrated_sample_original.jpg")
        
        total_time = time.time() - start_time
        print(f"✅ Pipeline executado em {total_time:.3f}s")
        
        # Analisar resultados
        analyze_pipeline_results(result)
        
        # Exportar resultados
        print("\n📤 Exportando resultados...")
        export_comprehensive_results(result)
        
        # Estatísticas do pipeline
        print("\n📈 ESTATÍSTICAS DO PIPELINE:")
        stats = pipeline.get_statistics()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\n🎉 Pipeline integrado executado com sucesso!")
        print("\n📁 Arquivos gerados:")
        print("   • integrated_sample_original.jpg - Imagem original")
        print("   • results/ - Diretório com resultados exportados")
        
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if 'pipeline' in locals():
            pipeline.cleanup()
            print("\n🧹 Recursos liberados")

if __name__ == "__main__":
    main()
