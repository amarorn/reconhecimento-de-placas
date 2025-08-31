

import time
import smtplib
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import json
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import defaultdict

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    EXPIRED = "expired"

@dataclass
class Alert:
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def acknowledge(self, user: str):
        self.status = AlertStatus.RESOLVED
        self.resolved_by = user
        self.resolved_at = datetime.now()
        logger.info(f"Alerta {self.id} resolvido por {user}")
    
    def to_dict(self) -> Dict[str, Any]:
    
    def __init__(self, name: str, condition: Callable, 
                 severity: AlertSeverity = AlertSeverity.WARNING,
                 category: str = "general", 
                 cooldown_minutes: int = 5):
        self.name = name
        self.condition = condition
        self.severity = severity
        self.category = category
        self.cooldown_minutes = cooldown_minutes
        self.last_triggered: Optional[datetime] = None
    
    def should_trigger(self, data: Any) -> bool:
        self.last_triggered = datetime.now()

class AlertSystem:
        self.rules.append(rule)
        logger.info(f"Regra de alerta adicionada: {rule.name}")
    
    def add_notifier(self, notifier: Callable):
        self.alert_callbacks[alert_type].append(callback)
        logger.info(f"Callback adicionado para alertas do tipo: {alert_type}")
    
    def create_alert(self, title: str, message: str, severity: AlertSeverity,
                     category: str, source: str, metadata: Dict[str, Any] = None,
                     expires_in_hours: Optional[int] = None) -> Alert:
        for rule in self.rules:
            if rule.should_trigger(data):
                alert = self.create_alert(
                    title=f"Regra disparada: {rule.name}",
                    message=f"Condição da regra '{rule.name}' foi atendida",
                    severity=rule.severity,
                    category=rule.category,
                    source="rule_system",
                    metadata={'rule_name': rule.name, 'trigger_data': data}
                )
                
                rule.mark_triggered()
                
                logger.info(f"Regra '{rule.name}' disparou alerta: {alert.id}")
    
    def get_active_alerts(self, category: Optional[str] = None, 
                         severity: Optional[AlertSeverity] = None) -> List[Alert]:
        total_alerts = len(self.alerts)
        active_alerts = len(self.get_active_alerts())
        
        severity_counts = defaultdict(int)
        for alert in self.alerts.values():
            severity_counts[alert.severity.value] += 1
        
        category_counts = defaultdict(int)
        for alert in self.alerts.values():
            category_counts[alert.category] += 1
        
        status_counts = defaultdict(int)
        for alert in self.alerts.values():
            status_counts[alert.status.value] += 1
        
        return {
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'severity_distribution': dict(severity_counts),
            'category_distribution': dict(category_counts),
            'status_distribution': dict(status_counts),
            'rules_count': len(self.rules),
            'notifiers_count': len(self.notifiers)
        }
    
    def acknowledge_alert(self, alert_id: str, user: str) -> bool:
        if alert_id not in self.alerts:
            logger.warning(f"Tentativa de resolver alerta inexistente: {alert_id}")
            return False
        
        alert = self.alerts[alert_id]
        alert.resolve(user)
        return True
    
    def delete_alert(self, alert_id: str) -> bool:
        if self.cleanup_active:
            return
        
        self.cleanup_active = True
        self.cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True
        )
        self.cleanup_thread.start()
        logger.info("Thread de limpeza iniciada")
    
    def stop_cleanup_thread(self):
        while self.cleanup_active:
            try:
                self._cleanup_old_alerts()
                time.sleep(self.cleanup_interval_minutes * 60)
            except Exception as e:
                logger.error(f"Erro no loop de limpeza: {e}")
    
    def _cleanup_old_alerts(self):
        for notifier in self.notifiers:
            try:
                notifier(alert)
            except Exception as e:
                logger.error(f"Erro no notificador: {e}")
    
    def _execute_alert_callbacks(self, alert: Alert):
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'alert_summary': self.get_alert_summary(),
                'active_alerts': [alert.to_dict() for alert in self.get_active_alerts()],
                'all_alerts': [alert.to_dict() for alert in self.alerts.values()]
            }
            
            if format_type == 'json':
                with open(filepath, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
            else:
                raise ValueError(f"Formato não suportado: {format_type}")
            
            logger.info(f"Alertas exportados para {filepath}")
            
        except Exception as e:
            logger.error(f"Erro ao exportar alertas: {e}")
            raise

class EmailNotifier:
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.title}"
            
            body = f"""
            Alerta do Sistema de Visão Computacional
            
            Título: {alert.title}
            Mensagem: {alert.message}
            Severidade: {alert.severity.value}
            Categoria: {alert.category}
            Fonte: {alert.source}
            Timestamp: {alert.timestamp}
            
            ID do Alerta: {alert.id}
    
    def __init__(self, log_level: int = logging.WARNING):
        self.log_level = log_level
    
    def __call__(self, alert: Alert):
