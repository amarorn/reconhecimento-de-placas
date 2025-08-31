

import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from .metrics_collector import metrics_collector, track_performance
from .alert_system import alert_system, AlertSeverity, AlertRule

logger = logging.getLogger(__name__)

@dataclass
class PipelineMetrics:
        self.total_images_processed += 1
        
        if success:
            self.successful_processing += 1
        else:
            self.failed_processing += 1
            if error_message:
                self.processing_errors.append(error_message)
        
        if self.total_images_processed == 1:
            self.average_processing_time = processing_time
        else:
            self.average_processing_time = (
                (self.average_processing_time * (self.total_images_processed - 1) + processing_time) 
                / self.total_images_processed
            )
        
        self.total_detections += detections
        self.total_texts_extracted += texts
        
        if detections > 0:
            if self.average_detection_confidence == 0.0:
                self.average_detection_confidence = detection_confidence
            else:
                self.average_detection_confidence = (
                    (self.average_detection_confidence * (self.total_detections - detections) + detection_confidence * detections)
                    / self.total_detections
                )
        
        if texts > 0:
            if self.average_ocr_confidence == 0.0:
                self.average_ocr_confidence = ocr_confidence
            else:
                self.average_ocr_confidence = (
                    (self.average_ocr_confidence * (self.total_texts_extracted - texts) + ocr_confidence * texts)
                    / self.total_texts_extracted
                )
        
        self.last_processing_time = datetime.now()
    
    def get_success_rate(self) -> float:
        return 1 - self.get_success_rate()
    
    def to_dict(self) -> Dict[str, Any]:
    
    def __init__(self):
        self.pipeline_metrics = PipelineMetrics()
        self.component_metrics: Dict[str, Dict[str, Any]] = {}
        self.performance_thresholds = {
            'max_processing_time': 10.0,
            'min_success_rate': 0.8,
            'max_error_rate': 0.2,
            'max_memory_usage': 85.0,
            'max_cpu_usage': 80.0
        }
        
        self._setup_alert_rules()
        
        self.notification_callbacks: List[callable] = []
        
        logger.info("PipelineMonitor inicializado")
    
    def _setup_alert_rules(self):
        self.notification_callbacks.append(callback)
        logger.info("Callback de notificação adicionado")
    
    @track_performance("pipeline_monitor", "track_image_processing")
    def track_image_processing(self, image_path: str, success: bool, processing_time: float,
                              detections: int = 0, texts: int = 0,
                              detection_confidence: float = 0.0, ocr_confidence: float = 0.0,
                              error_message: str = None):
        try:
            batch_start_time = time.time()
            total_images = len(image_paths)
            successful = sum(1 for r in results if r.get('success', False))
            failed = total_images - successful
            
            total_processing_time = sum(r.get('processing_time', 0) for r in results)
            total_detections = sum(len(r.get('detections', [])) for r in results)
            total_texts = sum(len(r.get('ocr_results', [])) for r in results)
            
            detection_confidences = []
            ocr_confidences = []
            
            for result in results:
                if result.get('success', False):
                    for detection in result.get('detections', []):
                        detection_confidences.append(detection.get('confidence', 0.0))
                    
                    for ocr_result in result.get('ocr_results', []):
                        ocr_confidences.append(ocr_result.get('confidence', 0.0))
            
            avg_detection_confidence = sum(detection_confidences) / len(detection_confidences) if detection_confidences else 0.0
            avg_ocr_confidence = sum(ocr_confidences) / len(ocr_confidences) if ocr_confidences else 0.0
            
            self.pipeline_metrics.update_processing_result(
                success=True,
                processing_time=total_processing_time,
                detections=total_detections,
                texts=total_texts,
                detection_confidence=avg_detection_confidence,
                ocr_confidence=avg_ocr_confidence
            )
            
            metrics_collector.collect_quality_metric(
                total_processed=total_images,
                successful_processing=successful,
                average_confidence=(avg_detection_confidence + avg_ocr_confidence) / 2,
                detection_accuracy=avg_detection_confidence,
                ocr_accuracy=avg_ocr_confidence
            )
            
            error_rate = failed / total_images if total_images > 0 else 0
            if error_rate > self.performance_thresholds['max_error_rate']:
                alert_system.create_alert(
                    title="Taxa de Erro Alta no Processamento em Lote",
                    message=f"Taxa de erro de {error_rate:.2%} no processamento de {total_images} imagens",
                    severity=AlertSeverity.WARNING,
                    category="quality",
                    source="batch_processing",
                    metadata={
                        'total_images': total_images,
                        'successful': successful,
                        'failed': failed,
                        'error_rate': error_rate
                    }
                )
            
            logger.info(f"Lote rastreado: {total_images} imagens - Sucessos: {successful} - Falhas: {failed}")
            
        except Exception as e:
            logger.error(f"Erro ao rastrear processamento em lote: {e}")
    
    def track_component_performance(self, component_name: str, operation_name: str,
                                   execution_time: float, success: bool, metadata: Dict[str, Any] = None):
        try:
            if processing_time > self.performance_thresholds['max_processing_time']:
                alert_system.create_alert(
                    title="Tempo de Processamento Alto",
                    message=f"Imagem processada em {processing_time:.2f}s (limite: {self.performance_thresholds['max_processing_time']}s)",
                    severity=AlertSeverity.WARNING,
                    category="performance",
                    source="image_processing",
                    metadata={'processing_time': processing_time, 'threshold': self.performance_thresholds['max_processing_time']}
                )
            
            current_error_rate = self.pipeline_metrics.get_error_rate()
            if current_error_rate > self.performance_thresholds['max_error_rate']:
                alert_system.create_alert(
                    title="Taxa de Erro Alta",
                    message=f"Taxa de erro atual: {current_error_rate:.2%} (limite: {self.performance_thresholds['max_error_rate']:.2%})",
                    severity=AlertSeverity.ERROR,
                    category="quality",
                    source="pipeline_monitor",
                    metadata={'error_rate': current_error_rate, 'threshold': self.performance_thresholds['max_error_rate']}
                )
            
        except Exception as e:
            logger.error(f"Erro ao verificar alertas de performance: {e}")
    
    def _notify_processing_result(self, image_path: str, success: bool, processing_time: float, error_message: str = None):
        try:
            pipeline_summary = self.pipeline_metrics.to_dict()
            
            component_summary = {}
            for comp_name, comp_ops in self.component_metrics.items():
                component_summary[comp_name] = {}
                for op_name, op_metrics in comp_ops.items():
                    component_summary[comp_name][op_name] = {
                        'total_calls': op_metrics['total_calls'],
                        'success_rate': op_metrics['successful_calls'] / op_metrics['total_calls'] if op_metrics['total_calls'] > 0 else 0,
                        'average_execution_time': op_metrics['average_execution_time'],
                        'last_call': op_metrics['last_call']
                    }
            
            system_metrics = metrics_collector.get_current_metrics()
            
            active_alerts = alert_system.get_active_alerts()
            alert_summary = alert_system.get_alert_summary()
            
            return {
                'pipeline': pipeline_summary,
                'components': component_summary,
                'system': system_metrics,
                'alerts': {
                    'active_alerts': [alert.to_dict() for alert in active_alerts],
                    'summary': alert_summary
                },
                'performance_thresholds': self.performance_thresholds,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter resumo do pipeline: {e}")
            return {}
    
    def export_metrics(self, filepath: str, format_type: str = 'json'):
        try:
            self.pipeline_metrics = PipelineMetrics()
            self.component_metrics.clear()
            
            metrics_collector.clear_history()
            
            alert_system.export_alerts("/tmp/alerts_backup.json")
            
            logger.info("Métricas do pipeline resetadas")
            
        except Exception as e:
            logger.error(f"Erro ao resetar métricas: {e}")
    
    def get_performance_recommendations(self) -> List[str]:
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                pipeline_monitor.track_component_performance(
                    component_name, operation_name, execution_time, True
                )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                pipeline_monitor.track_component_performance(
                    component_name, operation_name, execution_time, False,
                    {'error': str(e)}
                )
                
                raise
        
        return wrapper
    return decorator