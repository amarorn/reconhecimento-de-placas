#!/usr/bin/env python3
"""
Exemplo de Uso do Dashboard - Arquitetura de Visão Computacional
================================================================

Demonstra como usar o dashboard e sistema de monitoramento.
"""

import time
import threading
import random
from pathlib import Path
import sys

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from vision.dashboard.dashboard_server import start_dashboard
from vision.monitoring import (
    setup_monitoring,
    stop_monitoring,
    pipeline_monitor,
    metrics_collector,
    alert_system,
    export_monitoring_data
)

def simulate_pipeline_activity():
    """Simula atividade do pipeline para demonstrar o dashboard"""
    print("🚀 Iniciando simulação de atividade do pipeline...")
    
    # Simular processamento de imagens
    image_paths = [
        "imagem1.jpg", "imagem2.jpg", "imagem3.jpg", "imagem4.jpg", "imagem5.jpg",
        "imagem6.jpg", "imagem7.jpg", "imagem8.jpg", "imagem9.jpg", "imagem10.jpg"
    ]
    
    for i, image_path in enumerate(image_paths):
        try:
            # Simular tempo de processamento
            processing_time = random.uniform(0.5, 3.0)
            
            # Simular sucesso/falha
            success = random.random() > 0.1  # 90% de sucesso
            
            # Simular detecções
            detections = random.randint(1, 5) if success else 0
            detection_confidence = random.uniform(0.7, 0.95) if success else 0.0
            
            # Simular OCR
            texts = random.randint(1, 3) if success else 0
            ocr_confidence = random.uniform(0.8, 0.98) if success else 0.0
            
            # Rastrear processamento
            pipeline_monitor.track_image_processing(
                image_path=image_path,
                success=success,
                processing_time=processing_time,
                detections=detections,
                texts=texts,
                detection_confidence=detection_confidence,
                ocr_confidence=ocr_confidence,
                error_message="Erro simulado" if not success else None
            )
            
            print(f"📸 Processada {image_path}: {'✅' if success else '❌'} em {processing_time:.2f}s")
            
            # Aguardar entre processamentos
            time.sleep(random.uniform(0.5, 2.0))
            
        except Exception as e:
            print(f"❌ Erro ao processar {image_path}: {e}")
    
    print("✅ Simulação de atividade concluída!")

def simulate_system_load():
    """Simula carga do sistema para demonstrar métricas"""
    print("🖥️ Iniciando simulação de carga do sistema...")
    
    # Simular variações de CPU e memória
    for _ in range(20):
        try:
            # Simular uso de CPU
            cpu_usage = random.uniform(20, 90)
            
            # Simular uso de memória
            memory_usage = random.uniform(30, 85)
            
            # Atualizar métricas do sistema
            metrics_collector.current_metrics['system'].update({
                'cpu_percent': cpu_usage,
                'memory_percent': memory_usage,
                'timestamp': time.time()
            })
            
            # Aguardar
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Erro na simulação de carga: {e}")
    
    print("✅ Simulação de carga concluída!")

def create_sample_alerts():
    """Cria alertas de exemplo para demonstrar o sistema"""
    print("🚨 Criando alertas de exemplo...")
    
    # Alerta de performance
    alert_system.create_alert(
        title="Tempo de Processamento Alto",
        message="Imagem processada em 8.5 segundos (limite: 5.0s)",
        severity="warning",
        category="performance",
        source="simulation",
        metadata={'processing_time': 8.5, 'threshold': 5.0}
    )
    
    # Alerta de qualidade
    alert_system.create_alert(
        title="Taxa de Erro Alta",
        message="Taxa de erro atual: 25% (limite: 20%)",
        severity="error",
        category="quality",
        source="simulation",
        metadata={'error_rate': 0.25, 'threshold': 0.20}
    )
    
    # Alerta de sistema
    alert_system.create_alert(
        title="Uso de Memória Alto",
        message="Uso de memória: 87% (limite: 85%)",
        severity="warning",
        category="system",
        source="simulation",
        metadata={'memory_percent': 87, 'threshold': 85}
    )
    
    print("✅ Alertas de exemplo criados!")

def monitor_dashboard_activity():
    """Monitora atividade do dashboard"""
    print("📊 Monitorando atividade do dashboard...")
    
    for i in range(10):
        try:
            # Obter status do monitoramento
            status = pipeline_monitor.get_pipeline_summary()
            
            # Mostrar métricas principais
            pipeline_metrics = status.get('pipeline', {})
            print(f"📈 Métricas ({i+1}/10):")
            print(f"   - Imagens processadas: {pipeline_metrics.get('total_images_processed', 0)}")
            print(f"   - Taxa de sucesso: {pipeline_metrics.get('success_rate', 0):.2%}")
            print(f"   - Tempo médio: {pipeline_metrics.get('average_processing_time', 0):.3f}s")
            print(f"   - Total de detecções: {pipeline_metrics.get('total_detections', 0)}")
            print(f"   - Total de textos: {pipeline_metrics.get('total_texts_extracted', 0)}")
            
            # Mostrar alertas ativos
            alerts = status.get('alerts', {}).get('active_alerts', [])
            if alerts:
                print(f"   - Alertas ativos: {len(alerts)}")
            
            print()
            
            # Aguardar
            time.sleep(5)
            
        except Exception as e:
            print(f"❌ Erro ao monitorar dashboard: {e}")
    
    print("✅ Monitoramento concluído!")

def export_monitoring_data_example():
    """Demonstra exportação de dados de monitoramento"""
    print("💾 Exportando dados de monitoramento...")
    
    try:
        # Exportar dados completos
        export_path = "monitoring_data_export.json"
        export_monitoring_data(
            filepath=export_path,
            include_metrics=True,
            include_alerts=True,
            include_pipeline=True
        )
        
        print(f"✅ Dados exportados para {export_path}")
        
        # Mostrar recomendações de performance
        recommendations = pipeline_monitor.get_performance_recommendations()
        print("\n💡 Recomendações de Performance:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
    except Exception as e:
        print(f"❌ Erro ao exportar dados: {e}")

def main():
    """Função principal"""
    print("🚀 EXEMPLO DO DASHBOARD E SISTEMA DE MONITORAMENTO")
    print("=" * 60)
    
    try:
        # Configurar monitoramento
        print("\n🔧 Configurando sistema de monitoramento...")
        setup_monitoring(
            enable_metrics=True,
            enable_alerts=True,
            enable_pipeline_monitoring=True,
            metrics_interval=3,
            alert_cleanup_interval=15
        )
        
        # Criar alertas de exemplo
        create_sample_alerts()
        
        # Iniciar simulações em threads separadas
        print("\n🔄 Iniciando simulações...")
        
        # Thread para simulação do pipeline
        pipeline_thread = threading.Thread(target=simulate_pipeline_activity)
        pipeline_thread.daemon = True
        pipeline_thread.start()
        
        # Thread para simulação de carga do sistema
        system_thread = threading.Thread(target=simulate_system_load)
        system_thread.daemon = True
        system_thread.start()
        
        # Thread para monitoramento
        monitor_thread = threading.Thread(target=monitor_dashboard_activity)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Aguardar simulações
        pipeline_thread.join()
        system_thread.join()
        monitor_thread.join()
        
        # Exportar dados
        print("\n📊 Exportando dados de monitoramento...")
        export_monitoring_data_example()
        
        # Mostrar resumo final
        print("\n📋 RESUMO FINAL:")
        print("=" * 40)
        
        # Status do monitoramento
        status = pipeline_monitor.get_pipeline_summary()
        pipeline_metrics = status.get('pipeline', {})
        
        print(f"✅ Imagens processadas: {pipeline_metrics.get('total_images_processed', 0)}")
        print(f"✅ Taxa de sucesso: {pipeline_metrics.get('success_rate', 0):.2%}")
        print(f"✅ Tempo médio: {pipeline_metrics.get('average_processing_time', 0):.3f}s")
        print(f"✅ Total de detecções: {pipeline_metrics.get('total_detections', 0)}")
        print(f"✅ Total de textos: {pipeline_metrics.get('total_texts_extracted', 0)}")
        
        # Alertas
        alerts_summary = status.get('alerts', {}).get('summary', {})
        print(f"🚨 Total de alertas: {alerts_summary.get('total_alerts', 0)}")
        print(f"🚨 Alertas ativos: {alerts_summary.get('active_alerts', 0)}")
        
        print("\n🎉 Exemplo concluído com sucesso!")
        print("\n🌐 Para acessar o dashboard, execute:")
        print("   python -m vision.dashboard.dashboard_server")
        print("\n📊 O dashboard estará disponível em: http://localhost:8080")
        
    except KeyboardInterrupt:
        print("\n⏹️ Exemplo interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro no exemplo: {e}")
    finally:
        # Parar monitoramento
        print("\n🛑 Parando sistema de monitoramento...")
        stop_monitoring()
        print("✅ Sistema parado")

if __name__ == "__main__":
    main()