#!/usr/bin/env python3
"""
Sistema de Alertas - Arquitetura de Visão Computacional
=======================================================

Sistema de alertas inteligente para monitoramento e notificações.
"""

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
    """Níveis de severidade de alertas"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertStatus(Enum):
    """Status dos alertas"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    EXPIRED = "expired"

@dataclass
class Alert:
    """Representa um alerta do sistema"""
    id: str
    title: str
    message: str
    severity: AlertSeverity
    category: str
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    status: AlertStatus = AlertStatus.ACTIVE
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    
    def is_expired(self) -> bool:
        """Verifica se o alerta expirou"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def acknowledge(self, user: str):
        """Marca alerta como reconhecido"""
        self.status = AlertStatus.ACKNOWLEDGED
        self.acknowledged_by = user
        self.acknowledged_at = datetime.now()
        logger.info(f"Alerta {self.id} reconhecido por {user}")
    
    def resolve(self, user: str):
        """Marca alerta como resolvido"""
        self.status = AlertStatus.RESOLVED
        self.resolved_by = user
        self.resolved_at = datetime.now()
        logger.info(f"Alerta {self.id} resolvido por {user}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte alerta para dicionário"""
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'severity': self.severity.value,
            'category': self.category,
            'source': self.source,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status.value,
            'acknowledged_by': self.acknowledged_by,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_by': self.resolved_by,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'metadata': self.metadata,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': self.is_expired()
        }

class AlertRule:
    """Regra para geração de alertas"""
    
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
        """Verifica se a regra deve ser disparada"""
        if self.last_triggered:
            cooldown_end = self.last_triggered + timedelta(minutes=self.cooldown_minutes)
            if datetime.now() < cooldown_end:
                return False
        
        return self.condition(data)
    
    def mark_triggered(self):
        """Marca que a regra foi disparada"""
        self.last_triggered = datetime.now()

class AlertSystem:
    """Sistema principal de alertas"""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.rules: List[AlertRule] = []
        self.notifiers: List[Callable] = []
        self.alert_counter = 0
        
        # Configurações
        self.max_alerts = 1000
        self.alert_expiry_hours = 24
        self.cleanup_interval_minutes = 30
        
        # Thread de limpeza
        self.cleanup_thread: Optional[threading.Thread] = None
        self.cleanup_active = False
        
        # Callbacks para diferentes tipos de alerta
        self.alert_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        
        logger.info("Sistema de alertas inicializado")
    
    def add_rule(self, rule: AlertRule):
        """Adiciona regra de alerta"""
        self.rules.append(rule)
        logger.info(f"Regra de alerta adicionada: {rule.name}")
    
    def add_notifier(self, notifier: Callable):
        """Adiciona notificador"""
        self.notifiers.append(notifier)
        logger.info("Notificador adicionado")
    
    def add_alert_callback(self, alert_type: str, callback: Callable):
        """Adiciona callback para tipo específico de alerta"""
        self.alert_callbacks[alert_type].append(callback)
        logger.info(f"Callback adicionado para alertas do tipo: {alert_type}")
    
    def create_alert(self, title: str, message: str, severity: AlertSeverity,
                     category: str, source: str, metadata: Dict[str, Any] = None,
                     expires_in_hours: Optional[int] = None) -> Alert:
        """Cria um novo alerta"""
        # Gerar ID único
        self.alert_counter += 1
        alert_id = f"alert_{self.alert_counter}_{int(time.time())}"
        
        # Calcular expiração
        expires_at = None
        if expires_in_hours:
            expires_at = datetime.now() + timedelta(hours=expires_in_hours)
        elif self.alert_expiry_hours:
            expires_at = datetime.now() + timedelta(hours=self.alert_expiry_hours)
        
        # Criar alerta
        alert = Alert(
            id=alert_id,
            title=title,
            message=message,
            severity=severity,
            category=category,
            source=source,
            metadata=metadata or {},
            expires_at=expires_at
        )
        
        # Adicionar ao sistema
        self.alerts[alert_id] = alert
        
        # Limpar alertas antigos se necessário
        if len(self.alerts) > self.max_alerts:
            self._cleanup_old_alerts()
        
        # Notificar
        self._notify_alert(alert)
        
        # Executar callbacks específicos
        self._execute_alert_callbacks(alert)
        
        logger.info(f"Alerta criado: {alert_id} - {severity.value} - {title}")
        
        return alert
    
    def evaluate_rules(self, data: Any):
        """Avalia todas as regras com dados fornecidos"""
        for rule in self.rules:
            if rule.should_trigger(data):
                # Criar alerta baseado na regra
                alert = self.create_alert(
                    title=f"Regra disparada: {rule.name}",
                    message=f"Condição da regra '{rule.name}' foi atendida",
                    severity=rule.severity,
                    category=rule.category,
                    source="rule_system",
                    metadata={'rule_name': rule.name, 'trigger_data': data}
                )
                
                # Marcar regra como disparada
                rule.mark_triggered()
                
                logger.info(f"Regra '{rule.name}' disparou alerta: {alert.id}")
    
    def get_active_alerts(self, category: Optional[str] = None, 
                         severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Obtém alertas ativos filtrados"""
        active_alerts = []
        
        for alert in self.alerts.values():
            # Verificar se está ativo
            if alert.status != AlertStatus.ACTIVE:
                continue
            
            # Verificar se expirou
            if alert.is_expired():
                alert.status = AlertStatus.EXPIRED
                continue
            
            # Aplicar filtros
            if category and alert.category != category:
                continue
            
            if severity and alert.severity != severity:
                continue
            
            active_alerts.append(alert)
        
        # Ordenar por severidade e timestamp
        severity_order = {
            AlertSeverity.CRITICAL: 0,
            AlertSeverity.ERROR: 1,
            AlertSeverity.WARNING: 2,
            AlertSeverity.INFO: 3
        }
        
        active_alerts.sort(key=lambda x: (severity_order[x.severity], x.timestamp))
        
        return active_alerts
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Obtém resumo dos alertas"""
        total_alerts = len(self.alerts)
        active_alerts = len(self.get_active_alerts())
        
        # Contar por severidade
        severity_counts = defaultdict(int)
        for alert in self.alerts.values():
            severity_counts[alert.severity.value] += 1
        
        # Contar por categoria
        category_counts = defaultdict(int)
        for alert in self.alerts.values():
            category_counts[alert.category] += 1
        
        # Contar por status
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
        """Reconhece um alerta"""
        if alert_id not in self.alerts:
            logger.warning(f"Tentativa de reconhecer alerta inexistente: {alert_id}")
            return False
        
        alert = self.alerts[alert_id]
        alert.acknowledge(user)
        return True
    
    def resolve_alert(self, alert_id: str, user: str) -> bool:
        """Resolve um alerta"""
        if alert_id not in self.alerts:
            logger.warning(f"Tentativa de resolver alerta inexistente: {alert_id}")
            return False
        
        alert = self.alerts[alert_id]
        alert.resolve(user)
        return True
    
    def delete_alert(self, alert_id: str) -> bool:
        """Remove um alerta"""
        if alert_id not in self.alerts:
            return False
        
        del self.alerts[alert_id]
        logger.info(f"Alerta removido: {alert_id}")
        return True
    
    def start_cleanup_thread(self):
        """Inicia thread de limpeza automática"""
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
        """Para thread de limpeza"""
        self.cleanup_active = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
        logger.info("Thread de limpeza parada")
    
    def _cleanup_loop(self):
        """Loop de limpeza automática"""
        while self.cleanup_active:
            try:
                self._cleanup_old_alerts()
                time.sleep(self.cleanup_interval_minutes * 60)
            except Exception as e:
                logger.error(f"Erro no loop de limpeza: {e}")
    
    def _cleanup_old_alerts(self):
        """Remove alertas antigos e expirados"""
        current_time = datetime.now()
        alerts_to_remove = []
        
        for alert_id, alert in self.alerts.items():
            # Remover alertas expirados
            if alert.is_expired():
                alerts_to_remove.append(alert_id)
                continue
            
            # Remover alertas muito antigos (mais de 7 dias)
            if (current_time - alert.timestamp).days > 7:
                alerts_to_remove.append(alert_id)
                continue
        
        # Remover alertas marcados
        for alert_id in alerts_to_remove:
            del self.alerts[alert_id]
        
        if alerts_to_remove:
            logger.info(f"Removidos {len(alerts_to_remove)} alertas antigos")
    
    def _notify_alert(self, alert: Alert):
        """Notifica sobre novo alerta"""
        for notifier in self.notifiers:
            try:
                notifier(alert)
            except Exception as e:
                logger.error(f"Erro no notificador: {e}")
    
    def _execute_alert_callbacks(self, alert: Alert):
        """Executa callbacks específicos para o alerta"""
        # Callbacks para categoria
        for callback in self.alert_callbacks.get(alert.category, []):
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Erro no callback de categoria {alert.category}: {e}")
        
        # Callbacks para severidade
        for callback in self.alert_callbacks.get(alert.severity.value, []):
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Erro no callback de severidade {alert.severity.value}: {e}")
    
    def export_alerts(self, filepath: str, format_type: str = 'json'):
        """Exporta alertas para arquivo"""
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

# Notificadores predefinidos
class EmailNotifier:
    """Notificador por email"""
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, 
                 password: str, from_email: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
    
    def __call__(self, alert: Alert):
        """Envia notificação por email"""
        try:
            # Criar mensagem
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.title}"
            
            # Corpo da mensagem
            body = f"""
            Alerta do Sistema de Visão Computacional
            
            Título: {alert.title}
            Mensagem: {alert.message}
            Severidade: {alert.severity.value}
            Categoria: {alert.category}
            Fonte: {alert.source}
            Timestamp: {alert.timestamp}
            
            ID do Alerta: {alert.id}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Enviar email (implementar lógica de envio)
            logger.info(f"Notificação por email preparada para: {alert.id}")
            
        except Exception as e:
            logger.error(f"Erro ao preparar notificação por email: {e}")

class LogNotifier:
    """Notificador para logs"""
    
    def __init__(self, log_level: int = logging.WARNING):
        self.log_level = log_level
    
    def __call__(self, alert: Alert):
        """Registra alerta no log"""
        log_message = f"ALERTA [{alert.severity.value.upper()}] {alert.title}: {alert.message}"
        
        if alert.severity == AlertSeverity.CRITICAL:
            logging.critical(log_message)
        elif alert.severity == AlertSeverity.ERROR:
            logging.error(log_message)
        elif alert.severity == AlertSeverity.WARNING:
            logging.warning(log_message)
        else:
            logging.info(log_message)

# Instância global do sistema de alertas
alert_system = AlertSystem()

# Adicionar notificadores padrão
alert_system.add_notifier(LogNotifier())