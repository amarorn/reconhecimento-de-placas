

import time
import threading
import random
from pathlib import Path
import sys

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
    print("🖥️ Iniciando simulação de carga do sistema...")
    
    for _ in range(20):
        try:
            cpu_usage = random.uniform(20, 90)
            
            memory_usage = random.uniform(30, 85)
            
            metrics_collector.current_metrics['system'].update({
                'cpu_percent': cpu_usage,
                'memory_percent': memory_usage,
                'timestamp': time.time()
            })
            
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Erro na simulação de carga: {e}")
    
    print("✅ Simulação de carga concluída!")

def create_sample_alerts():
    print("📊 Monitorando atividade do dashboard...")
    
    for i in range(10):
        try:
            status = pipeline_monitor.get_pipeline_summary()
            
            pipeline_metrics = status.get('pipeline', {})
            print(f"📈 Métricas ({i+1}/10):")
            print(f"   - Imagens processadas: {pipeline_metrics.get('total_images_processed', 0)}")
            print(f"   - Taxa de sucesso: {pipeline_metrics.get('success_rate', 0):.2%}")
            print(f"   - Tempo médio: {pipeline_metrics.get('average_processing_time', 0):.3f}s")
            print(f"   - Total de detecções: {pipeline_metrics.get('total_detections', 0)}")
            print(f"   - Total de textos: {pipeline_metrics.get('total_texts_extracted', 0)}")
            
            alerts = status.get('alerts', {}).get('active_alerts', [])
            if alerts:
                print(f"   - Alertas ativos: {len(alerts)}")
            
            print()
            
            time.sleep(5)
            
        except Exception as e:
            print(f"❌ Erro ao monitorar dashboard: {e}")
    
    print("✅ Monitoramento concluído!")

def export_monitoring_data_example():
    print("🚀 EXEMPLO DO DASHBOARD E SISTEMA DE MONITORAMENTO")
    print("=" * 60)
    
    try:
        print("\n🔧 Configurando sistema de monitoramento...")
        setup_monitoring(
            enable_metrics=True,
            enable_alerts=True,
            enable_pipeline_monitoring=True,
            metrics_interval=3,
            alert_cleanup_interval=15
        )
        
        create_sample_alerts()
        
        print("\n🔄 Iniciando simulações...")
        
        pipeline_thread = threading.Thread(target=simulate_pipeline_activity)
        pipeline_thread.daemon = True
        pipeline_thread.start()
        
        system_thread = threading.Thread(target=simulate_system_load)
        system_thread.daemon = True
        system_thread.start()
        
        monitor_thread = threading.Thread(target=monitor_dashboard_activity)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        pipeline_thread.join()
        system_thread.join()
        monitor_thread.join()
        
        print("\n📊 Exportando dados de monitoramento...")
        export_monitoring_data_example()
        
        print("\n📋 RESUMO FINAL:")
        print("=" * 40)
        
        status = pipeline_monitor.get_pipeline_summary()
        pipeline_metrics = status.get('pipeline', {})
        
        print(f"✅ Imagens processadas: {pipeline_metrics.get('total_images_processed', 0)}")
        print(f"✅ Taxa de sucesso: {pipeline_metrics.get('success_rate', 0):.2%}")
        print(f"✅ Tempo médio: {pipeline_metrics.get('average_processing_time', 0):.3f}s")
        print(f"✅ Total de detecções: {pipeline_metrics.get('total_detections', 0)}")
        print(f"✅ Total de textos: {pipeline_metrics.get('total_texts_extracted', 0)}")
        
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
        print("\n🛑 Parando sistema de monitoramento...")
        stop_monitoring()
        print("✅ Sistema parado")

if __name__ == "__main__":
    main()