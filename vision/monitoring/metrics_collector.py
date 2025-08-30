

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
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_usage_percent: float
    network_io: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class QualityMetrics:
    
    def __init__(self, max_history_size: int = 1000):
        self.max_history_size = max_history_size
        
        self.performance_history: deque = deque(maxlen=max_history_size)
        self.system_history: deque = deque(maxlen=max_history_size)
        self.quality_history: deque = deque(maxlen=max_history_size)
        
        self.current_metrics: Dict[str, Any] = defaultdict(dict)
        
        self.aggregated_stats: Dict[str, Any] = defaultdict(dict)
        
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_active = False
        
        self.alert_callbacks: List[callable] = []
        
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'error_rate': 0.1,
            'response_time': 5.0
        }
        
        logger.info("MetricsCollector inicializado")
    
    def start_monitoring(self, interval_seconds: int = 5):
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Monitoramento parado")
    
    def _monitoring_loop(self, interval_seconds: int):
        metric = PerformanceMetrics(
            component_name=component_name,
            operation_name=operation_name,
            execution_time=execution_time,
            success=success,
            metadata=metadata or {}
        )
        
        self.performance_history.append(metric)
        
        key = f"{component_name}_{operation_name}"
        self.current_metrics['performance'][key] = {
            'last_execution_time': execution_time,
            'last_success': success,
            'last_timestamp': metric.timestamp.isoformat(),
            'metadata': metadata or {}
        }
        
        if execution_time > self.alert_thresholds['response_time']:
            self._trigger_alert('performance', {
                'component': component_name,
                'operation': operation_name,
                'execution_time': execution_time,
                'threshold': self.alert_thresholds['response_time']
            })
        
        logger.debug(f"Métrica de performance coletada: {component_name}.{operation_name} = {execution_time:.3f}s")
    
    def collect_system_metrics(self):
        metric = QualityMetrics(
            total_processed=total_processed,
            successful_processing=successful_processing,
            average_confidence=average_confidence,
            detection_accuracy=detection_accuracy,
            ocr_accuracy=ocr_accuracy
        )
        
        self.quality_history.append(metric)
        
        error_rate = 1 - (successful_processing / total_processed) if total_processed > 0 else 0
        
        self.current_metrics['quality'] = {
            'total_processed': total_processed,
            'successful_processing': successful_processing,
            'error_rate': error_rate,
            'average_confidence': average_confidence,
            'detection_accuracy': detection_accuracy,
            'ocr_accuracy': ocr_accuracy,
            'timestamp': metric.timestamp.isoformat()
        }
        
        if error_rate > self.alert_thresholds['error_rate']:
            self._trigger_alert('quality', {
                'error_rate': error_rate,
                'threshold': self.alert_thresholds['error_rate'],
                'total_processed': total_processed,
                'successful_processing': successful_processing
            })
        
        logger.debug(f"Métrica de qualidade coletada: taxa de erro = {error_rate:.2%}")
    
    def add_alert_callback(self, callback: callable):
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
        if not self.system_history:
            return {}
        
        metrics = self.system_history
        if time_window:
            cutoff_time = datetime.now() - time_window
            metrics = [m for m in metrics if m.timestamp > cutoff_time]
        
        if not metrics:
            return {}
        
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
        return dict(self.current_metrics)
    
    def export_metrics(self, filepath: str, format_type: str = 'json'):
        self.performance_history.clear()
        self.system_history.clear()
        self.quality_history.clear()
        logger.info("Histórico de métricas limpo")
    
    def get_metrics_info(self) -> Dict[str, Any]:
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