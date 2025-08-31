#!/usr/bin/env python3

import cv2
import numpy as np
import yaml
import time
import json
from pathlib import Path
import logging
from datetime import datetime

from vision.detection.pothole_detector import PotholeDetector

def load_config(config_path: str = "config/specialized_detectors.yaml") -> dict:
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        print(f"Arquivo de configuração não encontrado: {config_path}")
        return {}

def create_sample_video(output_path: str = "sample_road_video.mp4", duration: int = 10):
    """Cria um vídeo de exemplo para demonstração"""
    
    print(f"🎬 Criando vídeo de exemplo: {output_path}")
    
    # Configurações do vídeo
    fps = 30
    width, height = 1280, 720
    total_frames = fps * duration
    
    # Codec e writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    try:
        for frame_num in range(total_frames):
            # Criar frame base
            frame = np.ones((height, width, 3), dtype=np.uint8) * 255
            
            # Simular estrada
            cv2.rectangle(frame, (0, height//2), (width, height), (128, 128, 128), -1)
            
            # Simular movimento da câmera (efeito de estrada)
            offset = int(frame_num * 2) % 100
            
            # Simular placas de sinalização
            cv2.rectangle(frame, (50 + offset, 50), (150 + offset, 150), (0, 0, 255), -1)
            cv2.putText(frame, "PARE", (60 + offset, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Simular buracos que se movem (efeito de câmera em movimento)
            for i in range(5):
                x_pos = (150 + i * 200 + offset * 3) % width
                y_pos = height//2 + 50 + (i * 30)
                
                # Variação no tamanho dos buracos
                size_factor = 1 + 0.5 * np.sin(frame_num * 0.1 + i)
                ellipse_width = int(30 * size_factor)
                ellipse_height = int(20 * size_factor)
                
                cv2.ellipse(frame, (x_pos, y_pos), (ellipse_width, ellipse_height), 
                           0, 0, 360, (0, 0, 0), -1)
            
            # Adicionar informações do frame
            cv2.putText(frame, f"Frame: {frame_num}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            cv2.putText(frame, f"Tempo: {frame_num/fps:.1f}s", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            # Escrever frame
            out.write(frame)
            
            # Progresso
            if frame_num % (fps * 2) == 0:
                progress = (frame_num / total_frames) * 100
                print(f"   Progresso: {progress:.1f}%")
    
    finally:
        out.release()
    
    print(f"✅ Vídeo de exemplo criado: {output_path}")
    print(f"   Duração: {duration}s, FPS: {fps}, Resolução: {width}x{height}")

def analyze_video_with_pothole_detector(video_path: str, config: dict):
    """Analisa vídeo usando o PotholeDetector"""
    
    print(f"\n🔍 Analisando vídeo: {video_path}")
    
    try:
        # Inicializar detector
        pothole_config = config.get('pothole_detector', {})
        detector = PotholeDetector(pothole_config)
        
        print("✅ PotholeDetector inicializado")
        
        # Configurar caminho de saída
        output_dir = Path("video_analysis_results")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_video_path = output_dir / f"annotated_video_{timestamp}.mp4"
        report_path = output_dir / f"analysis_report_{timestamp}.json"
        
        # Processar vídeo
        print("\n🎬 Iniciando processamento do vídeo...")
        start_time = time.time()
        
        video_report = detector.process_video(
            video_path=video_path,
            output_path=str(output_video_path)
        )
        
        processing_time = time.time() - start_time
        print(f"✅ Processamento concluído em {processing_time:.2f}s")
        
        # Salvar relatório
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(video_report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"💾 Relatório salvo: {report_path}")
        print(f"🎬 Vídeo anotado salvo: {output_video_path}")
        
        # Exibir resultados
        display_video_analysis_results(video_report)
        
        # Estatísticas de tracking
        tracking_stats = detector.get_tracking_statistics()
        display_tracking_statistics(tracking_stats)
        
        return video_report, output_video_path, report_path
        
    except Exception as e:
        print(f"❌ Erro na análise do vídeo: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None
    
    finally:
        if 'detector' in locals():
            detector.cleanup()

def display_video_analysis_results(report: dict):
    """Exibe resultados da análise do vídeo"""
    
    print("\n📊 RESULTADOS DA ANÁLISE DO VÍDEO:")
    print("=" * 50)
    
    # Informações do vídeo
    video_info = report.get('video_info', {})
    print(f"🎬 VÍDEO:")
    print(f"   FPS: {video_info.get('fps', 'N/A')}")
    print(f"   Total de frames: {video_info.get('total_frames', 'N/A')}")
    print(f"   Duração: {video_info.get('duration', 'N/A'):.2f}s")
    print(f"   Frames processados: {video_info.get('processed_frames', 'N/A')}")
    
    # Resumo de detecções
    detection_summary = report.get('detection_summary', {})
    print(f"\n🔍 DETECÇÕES:")
    print(f"   Total de buracos: {detection_summary.get('total_detections', 0)}")
    print(f"   Frames com detecções: {detection_summary.get('frames_with_detections', 0)}")
    print(f"   Taxa de detecção: {detection_summary.get('detection_rate', 0):.2%}")
    
    # Análise de qualidade
    quality_analysis = report.get('quality_analysis', {})
    print(f"\n📈 QUALIDADE DOS FRAMES:")
    print(f"   Qualidade média: {quality_analysis.get('average_frame_quality', 0):.3f}")
    
    quality_dist = quality_analysis.get('quality_distribution', {})
    if quality_dist:
        print(f"   Distribuição:")
        for quality, count in quality_dist.items():
            print(f"      {quality.capitalize()}: {count}")
    
    # Condição da estrada
    road_condition = report.get('road_condition_analysis', {})
    print(f"\n🛣️ CONDIÇÃO DA ESTRADA:")
    print(f"   Condição geral: {road_condition.get('overall_condition', 'N/A')}")
    
    condition_dist = road_condition.get('condition_distribution', {})
    if condition_dist:
        print(f"   Distribuição:")
        for condition, count in condition_dist.items():
            print(f"      {condition.capitalize()}: {count}")
    
    # Prioridade de manutenção
    maintenance = report.get('maintenance_analysis', {})
    print(f"\n🔧 MANUTENÇÃO:")
    print(f"   Prioridade geral: {maintenance.get('overall_priority', 'N/A')}")
    
    priority_dist = maintenance.get('priority_distribution', {})
    if priority_dist:
        print(f"   Distribuição:")
        for priority, count in priority_dist.items():
            print(f"      {priority.capitalize()}: {count}")
    
    # Análise de tracking
    tracking = report.get('tracking_analysis', {})
    print(f"\n🎯 TRACKING:")
    print(f"   Total de tracks: {tracking.get('total_tracks', 0)}")
    print(f"   Tracks estáveis: {tracking.get('stable_tracks', 0)}")
    
    # Recomendações
    recommendations = report.get('recommendations', [])
    if recommendations:
        print(f"\n💡 RECOMENDAÇÕES:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")

def display_tracking_statistics(tracking_stats: dict):
    """Exibe estatísticas de tracking"""
    
    print(f"\n📊 ESTATÍSTICAS DE TRACKING:")
    print("=" * 40)
    
    print(f"   Total de tracks: {tracking_stats.get('total_tracks', 0)}")
    print(f"   Tracks estáveis: {tracking_stats.get('stable_tracks', 0)}")
    print(f"   Comprimento médio: {tracking_stats.get('average_track_length', 0):.1f} frames")
    print(f"   Comprimento máximo: {tracking_stats.get('max_track_length', 0)} frames")
    
    track_dist = tracking_stats.get('track_distribution', {})
    if track_dist:
        print(f"   Distribuição:")
        print(f"      Curtos (< {tracking_stats.get('min_track_length', 3)}): {track_dist.get('short', 0)}")
        print(f"      Estáveis: {track_dist.get('stable', 0)}")
        print(f"      Longos: {track_dist.get('long', 0)}")

def main():
    print("🎬 Análise de Vídeo com PotholeDetector")
    print("=" * 50)
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Carregar configuração
    config = load_config()
    if not config:
        print("❌ Falha ao carregar configuração")
        return
    
    print("✅ Configuração carregada com sucesso")
    
    # Criar vídeo de exemplo se não existir
    sample_video_path = "sample_road_video.mp4"
    if not Path(sample_video_path).exists():
        print("\n🎬 Criando vídeo de exemplo...")
        create_sample_video(sample_video_path, duration=10)
    else:
        print(f"✅ Vídeo de exemplo já existe: {sample_video_path}")
    
    # Analisar vídeo
    print(f"\n🔍 Iniciando análise do vídeo...")
    
    try:
        video_report, output_video, report_path = analyze_video_with_pothole_detector(
            sample_video_path, config
        )
        
        if video_report:
            print("\n🎉 Análise de vídeo concluída com sucesso!")
            print(f"\n📁 Arquivos gerados:")
            print(f"   • {output_video}")
            print(f"   • {report_path}")
            
            # Sugestões de uso
            print(f"\n💡 SUGESTÕES DE USO:")
            print(f"   1. Visualize o vídeo anotado para ver as detecções em tempo real")
            print(f"   2. Analise o relatório JSON para estatísticas detalhadas")
            print(f"   3. Use as configurações para ajustar sensibilidade e tracking")
            print(f"   4. Processe vídeos reais de estradas para análise em produção")
        
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
