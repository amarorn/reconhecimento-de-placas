#!/usr/bin/env python3
"""
Sistema de Coleta de Métricas - Arquitetura de Visão Computacional
==================================================================

Coleta e gerencia métricas de performance, uso e qualidade do sistema.
"""

import time
import psutil
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Métricas de performance de um componente"""
    component_name: str
    operation_name: str
    execution_time: float
    success: bool
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SystemMetrics:
    """Métricas do sistema"""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_usage_percent: float
    network_io: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class QualityMetrics:
    """Métricas de qualidade dos resultados"""
    total_processed: int
    successful_processing: int
    average_confidence: float
    detection_accuracy: float
    ocr_accuracy: float
    timestamp: datetime = field(default_factory=datetime.now)

class MetricsCollector:
    """Coletor principal de métricas do sistema"""
    
    def __init__(self, max_history_size: int = 1000):
        self.max_history_size = max_history_size
        
        # Histórico de métricas
        self.performance_history: deque = deque(maxlen=max_history_size)
        self.system_history: deque = deque(maxlen=max_history_size)
        self.quality_history: deque = deque(maxlen=max_history_size)
        
        # Métricas em tempo real
        self.current_metrics: Dict[str, Any] = defaultdict(dict)
        
        # Estatísticas agregadas
        self.aggregated_stats: Dict[str, Any] = defaultdict(dict)
        
        # Thread de monitoramento do sistema
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_active = False
        
        # Callbacks para alertas
        self.alert_callbacks: List[callable] = []
        
        # Configurações de alertas
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'error_rate': 0.1,  # 10%
            'response_time': 5.0  # 5 segundos
        }
        
        logger.info("MetricsCollector inicializado")
    
    def start_monitoring(self, interval_seconds: int = 5):
        """Inicia monitoramento automático do sistema"""
        if self.monitoring_active:
            logger.warning("Monitoramento já está ativo")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.monitoring_thread.start()
        logger.info(f"Monitoramento iniciado com intervalo de {interval_seconds}s")
    
    def stop_monitoring(self):
        """Para o monitoramento automático"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Monitoramento parado")
    
    def _monitoring_loop(self, interval_seconds: int):
        """Loop principal de monitoramento"""
        while self.monitoring_active:
            try:
                self.collect_system_metrics()
                self.check_alerts()
                time.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
    
    def collect_performance_metric(self, component_name: str, operation_name: str, 
                                 execution_time: float, success: bool, 
                                 metadata: Dict[str, Any] = None):
        """Coleta métrica de performance de um componente"""
        metric = PerformanceMetrics(
            component_name=component_name,
            operation_name=operation_name,
            execution_time=execution_time,
            success=success,
            metadata=metadata or {}
        )
        
        self.performance_history.append(metric)
        
        # Atualizar métricas em tempo real
        key = f"{component_name}_{operation_name}"
        self.current_metrics['performance'][key] = {
            'last_execution_time': execution_time,
            'last_success': success,
            'last_timestamp': metric.timestamp.isoformat(),
            'metadata': metadata or {}
        }
        
        # Verificar alertas de performance
        if execution_time > self.alert_thresholds['response_time']:
            self._trigger_alert('performance', {
                'component': component_name,
                'operation': operation_name,
                'execution_time': execution_time,
                'threshold': self.alert_thresholds['response_time']
            })
        
        logger.debug(f"Métrica de performance coletada: {component_name}.{operation_name} = {execution_time:.3f}s")
    
    def collect_system_metrics(self):
        """Coleta métricas do sistema"""
        try:
            # CPU e memória
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Rede
            network = psutil.net_io_counters()
            network_io = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
            
            metric = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / (1024 * 1024),
                disk_usage_percent=disk.percent,
                network_io=network_io
            )
            
            self.system_history.append(metric)
            
            # Atualizar métricas em tempo real
            self.current_metrics['system'] = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_mb': metric.memory_used_mb,
                'disk_usage_percent': disk.percent,
                'network_io': network_io,
                'timestamp': metric.timestamp.isoformat()
            }
            
            # Verificar alertas do sistema
            if cpu_percent > self.alert_thresholds['cpu_percent']:
                self._trigger_alert('system', {
                    'metric': 'cpu_percent',
                    'value': cpu_percent,
                    'threshold': self.alert_thresholds['cpu_percent']
                })
            
            if memory.percent > self.alert_thresholds['memory_percent']:
                self._trigger_alert('system', {
                    'metric': 'memory_percent',
                    'value': memory.percent,
                    'threshold': self.alert_thresholds['memory_percent']
                })
                
        except Exception as e:
            logger.error(f"Erro ao coletar métricas do sistema: {e}")
    
    def collect_quality_metric(self, total_processed: int, successful_processing: int,
                              average_confidence: float, detection_accuracy: float,
                              ocr_accuracy: float):
        """Coleta métricas de qualidade"""
        metric = QualityMetrics(
            total_processed=total_processed,
            successful_processing=successful_processing,
            average_confidence=average_confidence,
            detection_accuracy=detection_accuracy,
            ocr_accuracy=ocr_accuracy
        )
        
        self.quality_history.append(metric)
        
        # Calcular taxa de erro
        error_rate = 1 - (successful_processing / total_processed) if total_processed > 0 else 0
        
        # Atualizar métricas em tempo real
        self.current_metrics['quality'] = {
            'total_processed': total_processed,
            'successful_processing': successful_processing,
            'error_rate': error_rate,
            'average_confidence': average_confidence,
            'detection_accuracy': detection_accuracy,
            'ocr_accuracy': ocr_accuracy,
            'timestamp': metric.timestamp.isoformat()
        }
        
        # Verificar alertas de qualidade
        if error_rate > self.alert_thresholds['error_rate']:
            self._trigger_alert('quality', {
                'error_rate': error_rate,
                'threshold': self.alert_thresholds['error_rate'],
                'total_processed': total_processed,
                'successful_processing': successful_processing
            })
        
        logger.debug(f"Métrica de qualidade coletada: taxa de erro = {error_rate:.2%}")
    
    def add_alert_callback(self, callback: callable):
        """Adiciona callback para alertas"""
        self.alert_callbacks.append(callback)
        logger.info("Callback de alerta adicionado")
    
    def _trigger_alert(self, alert_type: str, alert_data: Dict[str, Any]):
        """Dispara alerta para todos os callbacks registrados"""
        alert = {
            'type': alert_type,
            'timestamp': datetime.now().isoformat(),
            'data': alert_data
        }
        
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Erro no callback de alerta: {e}")
        
        logger.warning(f"Alerta disparado: {alert_type} - {alert_data}")
    
    def get_performance_summary(self, component_name: str = None, 
                               time_window: timedelta = None) -> Dict[str, Any]:
        """Obtém resumo de performance"""
        if not self.performance_history:
            return {}
        
        # Filtrar por componente e janela de tempo
        metrics = self.performance_history
        if component_name:
            metrics = [m for m in metrics if m.component_name == component_name]
        
        if time_window:
            cutoff_time = datetime.now() - time_window
            metrics = [m for m in metrics if m.timestamp > cutoff_time]
        
        if not metrics:
            return {}
        
        # Calcular estatísticas
        execution_times = [m.execution_time for m in metrics]
        success_count = sum(1 for m in metrics if m.success)
        total_count = len(metrics)
        
        return {
            'total_operations': total_count,
            'successful_operations': success_count,
            'success_rate': success_count / total_count if total_count > 0 else 0,
            'average_execution_time': sum(execution_times) / len(execution_times),
            'min_execution_time': min(execution_times),
            'max_execution_time': max(execution_times),
            'execution_time_percentiles': {
                '50': sorted(execution_times)[len(execution_times) // 2],
                '90': sorted(execution_times)[int(len(execution_times) * 0.9)],
                '95': sorted(execution_times)[int(len(execution_times) * 0.95)],
                '99': sorted(execution_times)[int(len(execution_times) * 0.99)]
            }
        }
    
    def get_system_summary(self, time_window: timedelta = None) -> Dict[str, Any]:
        """Obtém resumo do sistema"""
        if not self.system_history:
            return {}
        
        # Filtrar por janela de tempo
        metrics = self.system_history
        if time_window:
            cutoff_time = datetime.now() - time_window
            metrics = [m for m in metrics if m.timestamp > cutoff_time]
        
        if not metrics:
            return {}
        
        # Calcular estatísticas
        cpu_values = [m.cpu_percent for m in metrics]
        memory_values = [m.memory_percent for m in metrics]
        
        return {
            'cpu': {
                'current': cpu_values[-1] if cpu_values else 0,
                'average': sum(cpu_values) / len(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values)
            },
            'memory': {
                'current': memory_values[-1] if memory_values else 0,
                'average': sum(memory_values) / len(memory_values),
                'max': max(memory_values),
                'min': min(memory_values)
            },
            'sample_count': len(metrics),
            'time_window': str(time_window) if time_window else 'all'
        }
    
    def get_quality_summary(self, time_window: timedelta = None) -> Dict[str, Any]:
        """Obtém resumo de qualidade"""
        if not self.quality_history:
            return {}
        
        # Filtrar por janela de tempo
        metrics = self.quality_history
        if time_window:
            cutoff_time = datetime.now() - time_window
            metrics = [m for m in metrics if m.timestamp > cutoff_time]
        
        if not metrics:
            return {}
        
        # Calcular estatísticas
        total_processed = sum(m.total_processed for m in metrics)
        total_successful = sum(m.successful_processing for m in metrics)
        avg_confidence = sum(m.average_confidence for m in metrics) / len(metrics)
        avg_detection_acc = sum(m.detection_accuracy for m in metrics) / len(metrics)
        avg_ocr_acc = sum(m.ocr_accuracy for m in metrics) / len(metrics)
        
        return {
            'total_processed': total_processed,
            'total_successful': total_successful,
            'overall_success_rate': total_successful / total_processed if total_processed > 0 else 0,
            'average_confidence': avg_confidence,
            'average_detection_accuracy': avg_detection_acc,
            'average_ocr_accuracy': avg_ocr_acc,
            'sample_count': len(metrics),
            'time_window': str(time_window) if time_window else 'all'
        }
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Obtém métricas atuais em tempo real"""
        return dict(self.current_metrics)
    
    def export_metrics(self, filepath: str, format_type: str = 'json'):
        """Exporta métricas para arquivo"""
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'performance_summary': self.get_performance_summary(),
                'system_summary': self.get_system_summary(),
                'quality_summary': self.get_quality_summary(),
                'current_metrics': self.get_current_metrics()
            }
            
            if format_type == 'json':
                with open(filepath, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
            else:
                raise ValueError(f"Formato não suportado: {format_type}")
            
            logger.info(f"Métricas exportadas para {filepath}")
            
        except Exception as e:
            logger.error(f"Erro ao exportar métricas: {e}")
            raise
    
    def clear_history(self):
        """Limpa histórico de métricas"""
        self.performance_history.clear()
        self.system_history.clear()
        self.quality_history.clear()
        logger.info("Histórico de métricas limpo")
    
    def get_metrics_info(self) -> Dict[str, Any]:
        """Obtém informações sobre o coletor de métricas"""
        return {
            'max_history_size': self.max_history_size,
            'current_history_size': {
                'performance': len(self.performance_history),
                'system': len(self.system_history),
                'quality': len(self.quality_history)
            },
            'monitoring_active': self.monitoring_active,
            'alert_callbacks_count': len(self.alert_callbacks),
            'alert_thresholds': self.alert_thresholds,
            'uptime': (datetime.now() - self._start_time).total_seconds() if hasattr(self, '_start_time') else 0
        }

# Instância global do coletor de métricas
metrics_collector = MetricsCollector()

# Decorator para métricas de performance
def track_performance(component_name: str, operation_name: str):
    """Decorator para rastrear performance de funções"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                metrics_collector.collect_performance_metric(
                    component_name, operation_name, execution_time, True
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                metrics_collector.collect_performance_metric(
                    component_name, operation_name, execution_time, False,
                    {'error': str(e)}
                )
                raise
        return wrapper
    return decorator