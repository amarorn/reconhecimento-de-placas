#!/usr/bin/env python3
"""
Monitor do Pipeline - Arquitetura de Visão Computacional
========================================================

Sistema de monitoramento integrado com o pipeline principal.
"""

import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

# Importar sistemas de monitoramento
from .metrics_collector import metrics_collector, track_performance
from .alert_system import alert_system, AlertSeverity, AlertRule

logger = logging.getLogger(__name__)

@dataclass
class PipelineMetrics:
    """Métricas específicas do pipeline"""
    total_images_processed: int = 0
    successful_processing: int = 0
    failed_processing: int = 0
    average_processing_time: float = 0.0
    total_detections: int = 0
    total_texts_extracted: int = 0
    average_detection_confidence: float = 0.0
    average_ocr_confidence: float = 0.0
    last_processing_time: Optional[datetime] = None
    processing_errors: List[str] = None
    
    def __post_init__(self):
        if self.processing_errors is None:
            self.processing_errors = []
    
    def update_processing_result(self, success: bool, processing_time: float, 
                               detections: int = 0, texts: int = 0,
                               detection_confidence: float = 0.0, 
                               ocr_confidence: float = 0.0,
                               error_message: str = None):
        """Atualiza métricas com resultado do processamento"""
        self.total_images_processed += 1
        
        if success:
            self.successful_processing += 1
        else:
            self.failed_processing += 1
            if error_message:
                self.processing_errors.append(error_message)
        
        # Atualizar tempo médio
        if self.total_images_processed == 1:
            self.average_processing_time = processing_time
        else:
            self.average_processing_time = (
                (self.average_processing_time * (self.total_images_processed - 1) + processing_time) 
                / self.total_images_processed
            )
        
        # Atualizar métricas de detecção e OCR
        self.total_detections += detections
        self.total_texts_extracted += texts
        
        # Atualizar confianças médias
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
        """Calcula taxa de sucesso"""
        if self.total_images_processed == 0:
            return 0.0
        return self.successful_processing / self.total_images_processed
    
    def get_error_rate(self) -> float:
        """Calcula taxa de erro"""
        return 1 - self.get_success_rate()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'total_images_processed': self.total_images_processed,
            'successful_processing': self.successful_processing,
            'failed_processing': self.failed_processing,
            'success_rate': self.get_success_rate(),
            'error_rate': self.get_error_rate(),
            'average_processing_time': self.average_processing_time,
            'total_detections': self.total_detections,
            'total_texts_extracted': self.total_texts_extracted,
            'average_detection_confidence': self.average_detection_confidence,
            'average_ocr_confidence': self.average_ocr_confidence,
            'last_processing_time': self.last_processing_time.isoformat() if self.last_processing_time else None,
            'processing_errors': self.processing_errors[-10:] if self.processing_errors else [],  # Últimos 10 erros
            'timestamp': datetime.now().isoformat()
        }

class PipelineMonitor:
    """Monitor principal do pipeline"""
    
    def __init__(self):
        self.pipeline_metrics = PipelineMetrics()
        self.component_metrics: Dict[str, Dict[str, Any]] = {}
        self.performance_thresholds = {
            'max_processing_time': 10.0,  # 10 segundos
            'min_success_rate': 0.8,      # 80%
            'max_error_rate': 0.2,        # 20%
            'max_memory_usage': 85.0,     # 85%
            'max_cpu_usage': 80.0         # 80%
        }
        
        # Configurar regras de alerta
        self._setup_alert_rules()
        
        # Callbacks para notificações
        self.notification_callbacks: List[callable] = []
        
        logger.info("PipelineMonitor inicializado")
    
    def _setup_alert_rules(self):
        """Configura regras de alerta automáticas"""
        
        # Regra para tempo de processamento alto
        def high_processing_time(data):
            return data.get('processing_time', 0) > self.performance_thresholds['max_processing_time']
        
        alert_rule = AlertRule(
            name="Tempo de Processamento Alto",
            condition=high_processing_time,
            severity=AlertSeverity.WARNING,
            category="performance",
            cooldown_minutes=2
        )
        alert_system.add_rule(alert_rule)
        
        # Regra para taxa de erro alta
        def high_error_rate(data):
            return data.get('error_rate', 0) > self.performance_thresholds['max_error_rate']
        
        alert_rule = AlertRule(
            name="Taxa de Erro Alta",
            condition=high_error_rate,
            severity=AlertSeverity.ERROR,
            category="quality",
            cooldown_minutes=5
        )
        alert_system.add_rule(alert_rule)
        
        # Regra para uso de memória alto
        def high_memory_usage(data):
            return data.get('memory_percent', 0) > self.performance_thresholds['max_memory_usage']
        
        alert_rule = AlertRule(
            name="Uso de Memória Alto",
            condition=high_memory_usage,
            severity=AlertSeverity.WARNING,
            category="system",
            cooldown_minutes=3
        )
        alert_system.add_rule(alert_rule)
        
        # Regra para uso de CPU alto
        def high_cpu_usage(data):
            return data.get('cpu_percent', 0) > self.performance_thresholds['max_cpu_usage']
        
        alert_rule = AlertRule(
            name="Uso de CPU Alto",
            condition=high_cpu_usage,
            severity=AlertSeverity.WARNING,
            category="system",
            cooldown_minutes=3
        )
        alert_system.add_rule(alert_rule)
        
        logger.info("Regras de alerta configuradas")
    
    def add_notification_callback(self, callback: callable):
        """Adiciona callback para notificações"""
        self.notification_callbacks.append(callback)
        logger.info("Callback de notificação adicionado")
    
    @track_performance("pipeline_monitor", "track_image_processing")
    def track_image_processing(self, image_path: str, success: bool, processing_time: float,
                              detections: int = 0, texts: int = 0,
                              detection_confidence: float = 0.0, ocr_confidence: float = 0.0,
                              error_message: str = None):
        """Rastreia processamento de uma imagem"""
        try:
            # Atualizar métricas do pipeline
            self.pipeline_metrics.update_processing_result(
                success=success,
                processing_time=processing_time,
                detections=detections,
                texts=texts,
                detection_confidence=detection_confidence,
                ocr_confidence=ocr_confidence,
                error_message=error_message
            )
            
            # Coletar métricas de qualidade
            if success:
                metrics_collector.collect_quality_metric(
                    total_processed=1,
                    successful_processing=1,
                    average_confidence=(detection_confidence + ocr_confidence) / 2 if (detection_confidence + ocr_confidence) > 0 else 0,
                    detection_accuracy=detection_confidence,
                    ocr_accuracy=ocr_confidence
                )
            else:
                metrics_collector.collect_quality_metric(
                    total_processed=1,
                    successful_processing=0,
                    average_confidence=0.0,
                    detection_accuracy=0.0,
                    ocr_accuracy=0.0
                )
            
            # Verificar regras de alerta
            self._check_performance_alerts(processing_time, success)
            
            # Notificar callbacks
            self._notify_processing_result(image_path, success, processing_time, error_message)
            
            logger.debug(f"Processamento rastreado: {image_path} - Sucesso: {success} - Tempo: {processing_time:.3f}s")
            
        except Exception as e:
            logger.error(f"Erro ao rastrear processamento: {e}")
    
    @track_performance("pipeline_monitor", "track_batch_processing")
    def track_batch_processing(self, image_paths: List[str], results: List[Dict[str, Any]]):
        """Rastreia processamento em lote"""
        try:
            batch_start_time = time.time()
            total_images = len(image_paths)
            successful = sum(1 for r in results if r.get('success', False))
            failed = total_images - successful
            
            # Calcular métricas agregadas
            total_processing_time = sum(r.get('processing_time', 0) for r in results)
            total_detections = sum(len(r.get('detections', [])) for r in results)
            total_texts = sum(len(r.get('ocr_results', [])) for r in results)
            
            # Calcular confianças médias
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
            
            # Atualizar métricas
            self.pipeline_metrics.update_processing_result(
                success=True,  # Lote considerado bem-sucedido se pelo menos uma imagem foi processada
                processing_time=total_processing_time,
                detections=total_detections,
                texts=total_texts,
                detection_confidence=avg_detection_confidence,
                ocr_confidence=avg_ocr_confidence
            )
            
            # Coletar métricas de qualidade para o lote
            metrics_collector.collect_quality_metric(
                total_processed=total_images,
                successful_processing=successful,
                average_confidence=(avg_detection_confidence + avg_ocr_confidence) / 2,
                detection_accuracy=avg_detection_confidence,
                ocr_accuracy=avg_ocr_confidence
            )
            
            # Verificar alertas de qualidade
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
        """Rastreia performance de um componente específico"""
        try:
            # Coletar métrica de performance
            metrics_collector.collect_performance_metric(
                component_name=component_name,
                operation_name=operation_name,
                execution_time=execution_time,
                success=success,
                metadata=metadata or {}
            )
            
            # Atualizar métricas do componente
            if component_name not in self.component_metrics:
                self.component_metrics[component_name] = {}
            
            if operation_name not in self.component_metrics[component_name]:
                self.component_metrics[component_name][operation_name] = {
                    'total_calls': 0,
                    'successful_calls': 0,
                    'total_execution_time': 0.0,
                    'average_execution_time': 0.0,
                    'last_call': None
                }
            
            comp_metrics = self.component_metrics[component_name][operation_name]
            comp_metrics['total_calls'] += 1
            comp_metrics['total_execution_time'] += execution_time
            comp_metrics['average_execution_time'] = comp_metrics['total_execution_time'] / comp_metrics['total_calls']
            comp_metrics['last_call'] = datetime.now().isoformat()
            
            if success:
                comp_metrics['successful_calls'] += 1
            
            logger.debug(f"Performance do componente rastreada: {component_name}.{operation_name} = {execution_time:.3f}s")
            
        except Exception as e:
            logger.error(f"Erro ao rastrear performance do componente: {e}")
    
    def _check_performance_alerts(self, processing_time: float, success: bool):
        """Verifica alertas de performance"""
        try:
            # Verificar tempo de processamento
            if processing_time > self.performance_thresholds['max_processing_time']:
                alert_system.create_alert(
                    title="Tempo de Processamento Alto",
                    message=f"Imagem processada em {processing_time:.2f}s (limite: {self.performance_thresholds['max_processing_time']}s)",
                    severity=AlertSeverity.WARNING,
                    category="performance",
                    source="image_processing",
                    metadata={'processing_time': processing_time, 'threshold': self.performance_thresholds['max_processing_time']}
                )
            
            # Verificar taxa de erro
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
        """Notifica resultado do processamento para callbacks registrados"""
        notification_data = {
            'image_path': image_path,
            'success': success,
            'processing_time': processing_time,
            'error_message': error_message,
            'timestamp': datetime.now().isoformat(),
            'pipeline_metrics': self.pipeline_metrics.to_dict()
        }
        
        for callback in self.notification_callbacks:
            try:
                callback(notification_data)
            except Exception as e:
                logger.error(f"Erro no callback de notificação: {e}")
    
    def get_pipeline_summary(self) -> Dict[str, Any]:
        """Obtém resumo completo do pipeline"""
        try:
            # Métricas do pipeline
            pipeline_summary = self.pipeline_metrics.to_dict()
            
            # Métricas dos componentes
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
            
            # Métricas do sistema
            system_metrics = metrics_collector.get_current_metrics()
            
            # Alertas ativos
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
        """Exporta métricas para arquivo"""
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'pipeline_summary': self.get_pipeline_summary(),
                'pipeline_metrics': self.pipeline_metrics.to_dict(),
                'component_metrics': self.component_metrics,
                'performance_thresholds': self.performance_thresholds
            }
            
            if format_type == 'json':
                import json
                with open(filepath, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
            else:
                raise ValueError(f"Formato não suportado: {format_type}")
            
            logger.info(f"Métricas do pipeline exportadas para {filepath}")
            
        except Exception as e:
            logger.error(f"Erro ao exportar métricas do pipeline: {e}")
            raise
    
    def reset_metrics(self):
        """Reseta todas as métricas"""
        try:
            self.pipeline_metrics = PipelineMetrics()
            self.component_metrics.clear()
            
            # Limpar métricas do coletor
            metrics_collector.clear_history()
            
            # Limpar alertas
            alert_system.export_alerts("/tmp/alerts_backup.json")
            
            logger.info("Métricas do pipeline resetadas")
            
        except Exception as e:
            logger.error(f"Erro ao resetar métricas: {e}")
    
    def get_performance_recommendations(self) -> List[str]:
        """Obtém recomendações de performance baseadas nas métricas"""
        recommendations = []
        
        try:
            # Verificar taxa de sucesso
            success_rate = self.pipeline_metrics.get_success_rate()
            if success_rate < 0.9:
                recommendations.append(f"Taxa de sucesso baixa ({success_rate:.2%}). Considere revisar pré-processamento ou modelos.")
            
            # Verificar tempo de processamento
            if self.pipeline_metrics.average_processing_time > 5.0:
                recommendations.append(f"Tempo de processamento alto ({self.pipeline_metrics.average_processing_time:.2f}s). Considere otimizar pipeline ou usar modelos menores.")
            
            # Verificar confiança das detecções
            if self.pipeline_metrics.average_detection_confidence < 0.7:
                recommendations.append(f"Confiança média das detecções baixa ({self.pipeline_metrics.average_detection_confidence:.2%}). Considere ajustar thresholds ou treinar modelos.")
            
            # Verificar confiança do OCR
            if self.pipeline_metrics.average_ocr_confidence < 0.7:
                recommendations.append(f"Confiança média do OCR baixa ({self.pipeline_metrics.average_ocr_confidence:.2%}). Considere melhorar pré-processamento ou usar motores OCR alternativos.")
            
            # Verificar erros recentes
            if len(self.pipeline_metrics.processing_errors) > 5:
                recommendations.append(f"Muitos erros recentes ({len(self.pipeline_metrics.processing_errors)}). Considere investigar causas raiz.")
            
            if not recommendations:
                recommendations.append("Performance está dentro dos parâmetros esperados. Continue monitorando.")
            
        except Exception as e:
            logger.error(f"Erro ao gerar recomendações: {e}")
            recommendations.append("Erro ao gerar recomendações de performance.")
        
        return recommendations

# Instância global do monitor do pipeline
pipeline_monitor = PipelineMonitor()

# Decorator para rastrear performance de funções do pipeline
def monitor_pipeline_operation(component_name: str, operation_name: str):
    """Decorator para monitorar operações do pipeline"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Rastrear performance
                pipeline_monitor.track_component_performance(
                    component_name, operation_name, execution_time, True
                )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                # Rastrear falha
                pipeline_monitor.track_component_performance(
                    component_name, operation_name, execution_time, False,
                    {'error': str(e)}
                )
                
                raise
        
        return wrapper
    return decorator