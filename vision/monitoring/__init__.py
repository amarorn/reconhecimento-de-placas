"""
Módulo de Monitoramento - Arquitetura de Visão Computacional
============================================================

Sistema completo de monitoramento, métricas e alertas para o pipeline de visão computacional.
"""

__version__ = "2.0.0"
__author__ = "Equipe de Desenvolvimento"

# Importar componentes principais
from .metrics_collector import (
    MetricsCollector,
    PerformanceMetrics,
    SystemMetrics,
    QualityMetrics,
    metrics_collector,
    track_performance
)

from .alert_system import (
    AlertSystem,
    Alert,
    AlertRule,
    AlertSeverity,
    AlertStatus,
    EmailNotifier,
    LogNotifier,
    alert_system
)

from .pipeline_monitor import (
    PipelineMonitor,
    PipelineMetrics,
    pipeline_monitor,
    monitor_pipeline_operation
)

# Configuração de logging
import logging

# Configurar logging para o módulo de monitoramento
monitoring_logger = logging.getLogger(__name__)
monitoring_logger.setLevel(logging.INFO)

# Handler para console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formato do log
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
console_handler.setFormatter(formatter)

# Adicionar handler se não existir
if not monitoring_logger.handlers:
    monitoring_logger.addHandler(console_handler)

# Função para configurar monitoramento
def setup_monitoring(
    enable_metrics: bool = True,
    enable_alerts: bool = True,
    enable_pipeline_monitoring: bool = True,
    metrics_interval: int = 5,
    alert_cleanup_interval: int = 30
):
    """
    Configura o sistema de monitoramento
    
    Args:
        enable_metrics: Habilita coleta de métricas
        enable_alerts: Habilita sistema de alertas
        enable_pipeline_monitoring: Habilita monitoramento do pipeline
        metrics_interval: Intervalo de coleta de métricas em segundos
        alert_cleanup_interval: Intervalo de limpeza de alertas em minutos
    """
    try:
        if enable_metrics:
            # Iniciar coleta de métricas
            metrics_collector.start_monitoring(metrics_interval)
            monitoring_logger.info("Coleta de métricas iniciada")
        
        if enable_alerts:
            # Iniciar thread de limpeza de alertas
            alert_system.start_cleanup_thread()
            monitoring_logger.info("Sistema de alertas iniciado")
        
        if enable_pipeline_monitoring:
            # Configurar callbacks de notificação
            def log_processing_result(data):
                monitoring_logger.info(
                    f"Processamento: {data['image_path']} - "
                    f"Sucesso: {data['success']} - "
                    f"Tempo: {data['processing_time']:.3f}s"
                )
            
            pipeline_monitor.add_notification_callback(log_processing_result)
            monitoring_logger.info("Monitoramento do pipeline configurado")
        
        monitoring_logger.info("Sistema de monitoramento configurado com sucesso")
        
    except Exception as e:
        monitoring_logger.error(f"Erro ao configurar monitoramento: {e}")
        raise

# Função para parar monitoramento
def stop_monitoring():
    """Para o sistema de monitoramento"""
    try:
        # Parar coleta de métricas
        metrics_collector.stop_monitoring()
        
        # Parar thread de limpeza de alertas
        alert_system.stop_cleanup_thread()
        
        monitoring_logger.info("Sistema de monitoramento parado")
        
    except Exception as e:
        monitoring_logger.error(f"Erro ao parar monitoramento: {e}")

# Função para obter status do monitoramento
def get_monitoring_status() -> dict:
    """Obtém status do sistema de monitoramento"""
    try:
        return {
            'metrics_collector': {
                'active': metrics_collector.monitoring_active,
                'history_size': {
                    'performance': len(metrics_collector.performance_history),
                    'system': len(metrics_collector.system_history),
                    'quality': len(metrics_collector.quality_history)
                }
            },
            'alert_system': {
                'active': alert_system.cleanup_active,
                'total_alerts': len(alert_system.alerts),
                'active_alerts': len(alert_system.get_active_alerts()),
                'rules_count': len(alert_system.rules)
            },
            'pipeline_monitor': {
                'total_images_processed': pipeline_monitor.pipeline_metrics.total_images_processed,
                'success_rate': pipeline_monitor.pipeline_metrics.get_success_rate(),
                'average_processing_time': pipeline_monitor.pipeline_metrics.average_processing_time
            }
        }
    except Exception as e:
        monitoring_logger.error(f"Erro ao obter status do monitoramento: {e}")
        return {'error': str(e)}

# Função para exportar dados de monitoramento
def export_monitoring_data(filepath: str, include_metrics: bool = True, 
                          include_alerts: bool = True, include_pipeline: bool = True):
    """
    Exporta dados de monitoramento para arquivo
    
    Args:
        filepath: Caminho do arquivo de saída
        include_metrics: Incluir métricas do sistema
        include_alerts: Incluir alertas
        include_pipeline: Incluir métricas do pipeline
    """
    try:
        import json
        from datetime import datetime
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'monitoring_status': get_monitoring_status()
        }
        
        if include_metrics:
            export_data['metrics'] = {
                'performance': metrics_collector.get_performance_summary(),
                'system': metrics_collector.get_system_summary(),
                'quality': metrics_collector.get_quality_summary(),
                'current': metrics_collector.get_current_metrics()
            }
        
        if include_alerts:
            export_data['alerts'] = {
                'summary': alert_system.get_alert_summary(),
                'active_alerts': [alert.to_dict() for alert in alert_system.get_active_alerts()]
            }
        
        if include_pipeline:
            export_data['pipeline'] = pipeline_monitor.get_pipeline_summary()
        
        # Salvar arquivo
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        monitoring_logger.info(f"Dados de monitoramento exportados para {filepath}")
        
    except Exception as e:
        monitoring_logger.error(f"Erro ao exportar dados de monitoramento: {e}")
        raise

# Função para limpar dados de monitoramento
def clear_monitoring_data():
    """Limpa todos os dados de monitoramento"""
    try:
        # Limpar métricas
        metrics_collector.clear_history()
        
        # Limpar alertas (fazer backup primeiro)
        alert_system.export_alerts("/tmp/alerts_backup_before_clear.json")
        
        # Resetar métricas do pipeline
        pipeline_monitor.reset_metrics()
        
        monitoring_logger.info("Dados de monitoramento limpos")
        
    except Exception as e:
        monitoring_logger.error(f"Erro ao limpar dados de monitoramento: {e}")

# Configuração automática ao importar o módulo
def _auto_setup():
    """Configuração automática do monitoramento"""
    try:
        # Configurar monitoramento básico
        setup_monitoring(
            enable_metrics=True,
            enable_alerts=True,
            enable_pipeline_monitoring=True,
            metrics_interval=5,
            alert_cleanup_interval=30
        )
        
        monitoring_logger.info("Monitoramento configurado automaticamente")
        
    except Exception as e:
        monitoring_logger.warning(f"Configuração automática falhou: {e}")

# Executar configuração automática
_auto_setup()

# Limpeza ao sair
import atexit
atexit.register(stop_monitoring)

# Informações do módulo
__all__ = [
    # Classes principais
    'MetricsCollector',
    'AlertSystem',
    'PipelineMonitor',
    
    # Instâncias globais
    'metrics_collector',
    'alert_system',
    'pipeline_monitor',
    
    # Decorators
    'track_performance',
    'monitor_pipeline_operation',
    
    # Funções de configuração
    'setup_monitoring',
    'stop_monitoring',
    'get_monitoring_status',
    'export_monitoring_data',
    'clear_monitoring_data'
]