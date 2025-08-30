

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path

from ..monitoring.metrics_collector import metrics_collector
from ..monitoring.alert_system import alert_system, AlertSeverity

logger = logging.getLogger(__name__)

class DashboardServer:
        
        @self.app.get("/", response_class=HTMLResponse)
        async def get_dashboard():
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        
        @self.app.get("/api/metrics/current")
        async def get_current_metrics():
            try:
                time_window = None
                if time_window_minutes:
                    time_window = timedelta(minutes=time_window_minutes)
                
                return {
                    "status": "success",
                    "data": metrics_collector.get_performance_summary(component, time_window),
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Erro ao obter métricas de performance: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/metrics/system")
        async def get_system_metrics(time_window_minutes: Optional[int] = None):
            try:
                time_window = None
                if time_window_minutes:
                    time_window = timedelta(minutes=time_window_minutes)
                
                return {
                    "status": "success",
                    "data": metrics_collector.get_quality_summary(time_window),
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Erro ao obter métricas de qualidade: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/alerts")
        async def get_alerts(category: Optional[str] = None, 
                           severity: Optional[str] = None,
                           status: Optional[str] = None):
            try:
                success = alert_system.acknowledge_alert(alert_id, user)
                if success:
                    return {"status": "success", "message": "Alerta reconhecido"}
                else:
                    raise HTTPException(status_code=404, detail="Alerta não encontrado")
            except Exception as e:
                logger.error(f"Erro ao reconhecer alerta: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/alerts/{alert_id}/resolve")
        async def resolve_alert(alert_id: str, user: str = "dashboard_user"):
            try:
                current_metrics = metrics_collector.get_current_metrics()
                performance_summary = metrics_collector.get_performance_summary()
                system_summary = metrics_collector.get_system_summary()
                quality_summary = metrics_collector.get_quality_summary()
                alert_summary = alert_system.get_alert_summary()
                
                total_operations = performance_summary.get('total_operations', 0)
                success_rate = performance_summary.get('success_rate', 0)
                avg_response_time = performance_summary.get('average_execution_time', 0)
                
                cpu_usage = system_summary.get('cpu', {}).get('current', 0)
                memory_usage = system_summary.get('memory', {}).get('current', 0)
                
                active_alerts = alert_summary.get('active_alerts', 0)
                critical_alerts = alert_summary.get('severity_distribution', {}).get('critical', 0)
                
                return {
                    "status": "success",
                    "data": {
                        "overview": {
                            "total_operations": total_operations,
                            "success_rate": f"{success_rate:.2%}",
                            "average_response_time": f"{avg_response_time:.3f}s",
                            "cpu_usage": f"{cpu_usage:.1f}%",
                            "memory_usage": f"{memory_usage:.1f}%",
                            "active_alerts": active_alerts,
                            "critical_alerts": critical_alerts
                        },
                        "performance": performance_summary,
                        "system": system_summary,
                        "quality": quality_summary,
                        "alerts": alert_summary,
                        "timestamp": datetime.now().isoformat()
                    }
                }
            except Exception as e:
                logger.error(f"Erro ao obter resumo do dashboard: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
        static_dir = Path(__file__).parent / "static"
        if static_dir.exists():
            self.app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
            logger.info("Arquivos estáticos configurados")
        else:
            logger.warning("Diretório de arquivos estáticos não encontrado")
    
    async def _send_initial_data(self, websocket: WebSocket):
        try:
            command_type = command.get("type")
            
            if command_type == "get_metrics":
                metrics_data = {
                    "type": "metrics_update",
                    "data": metrics_collector.get_current_metrics(),
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send_text(json.dumps(metrics_data))
            
            elif command_type == "get_alerts":
                alerts_data = {
                    "type": "alerts_update",
                    "data": {
                        "alerts": [alert.to_dict() for alert in alert_system.get_active_alerts()],
                        "summary": alert_system.get_alert_summary()
                    },
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send_text(json.dumps(alerts_data))
            
            elif command_type == "subscribe":
                subscription_type = command.get("subscription_type", "all")
                
                response = {
                    "type": "subscription_confirmed",
                    "subscription_type": subscription_type,
                    "message": "Inscrição confirmada para atualizações em tempo real"
                }
                await websocket.send_text(json.dumps(response))
            
            else:
                response = {
                    "type": "error",
                    "message": f"Comando desconhecido: {command_type}"
                }
                await websocket.send_text(json.dumps(response))
                
        except Exception as e:
            logger.error(f"Erro ao processar comando WebSocket: {e}")
            
            error_response = {
                "type": "error",
                "message": f"Erro interno: {str(e)}"
            }
            await websocket.send_text(json.dumps(error_response))
    
    async def broadcast_update(self, update_type: str, data: Dict[str, Any]):
        return """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Dashboard - Visão Computacional</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background:
                .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
                .header { background:
                .header h1 { font-size: 2.5em; margin-bottom: 10px; }
                .header p { font-size: 1.1em; opacity: 0.9; }
                .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px; }
                .metric-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .metric-card h3 { color:
                .metric-value { font-size: 2em; font-weight: bold; color:
                .metric-label { color:
                .charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
                .chart-container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .chart-container h3 { color:
                .alerts-section { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .alerts-section h3 { color:
                .alert-item { padding: 10px; margin: 10px 0; border-radius: 5px; border-left: 4px solid; }
                .alert-critical { background: #ffebee; border-left-color:
                .alert-error { background: #fff3e0; border-left-color:
                .alert-warning { background: #fff8e1; border-left-color:
                .alert-info { background: #e3f2fd; border-left-color:
                .status-indicator { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 10px; }
                .status-healthy { background:
                .status-warning { background:
                .status-critical { background:
                .refresh-btn { background:
                .refresh-btn:hover { background:
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Dashboard de Visão Computacional</h1>
                    <p>Monitoramento em tempo real do sistema de reconhecimento de placas</p>
                </div>
                
                <button class="refresh-btn" onclick="refreshDashboard()">🔄 Atualizar Dashboard</button>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>📊 Operações</h3>
                        <div class="metric-value" id="total-operations">0</div>
                        <div class="metric-label">Total de operações processadas</div>
                    </div>
                    
                    <div class="metric-card">
                        <h3>✅ Taxa de Sucesso</h3>
                        <div class="metric-value" id="success-rate">0.00%</div>
                        <div class="metric-label">Operações bem-sucedidas</div>
                    </div>
                    
                    <div class="metric-card">
                        <h3>⚡ Tempo de Resposta</h3>
                        <div class="metric-value" id="avg-response-time">0.000s</div>
                        <div class="metric-label">Tempo médio de processamento</div>
                    </div>
                    
                    <div class="metric-card">
                        <h3>🖥️ CPU</h3>
                        <div class="metric-value" id="cpu-usage">0.0%</div>
                        <div class="metric-label">Uso atual do processador</div>
                    </div>
                    
                    <div class="metric-card">
                        <h3>💾 Memória</h3>
                        <div class="metric-value" id="memory-usage">0.0%</div>
                        <div class="metric-label">Uso atual da memória</div>
                        <div class="status-indicator status-healthy" id="memory-status"></div>
                    </div>
                    
                    <div class="metric-card">
                        <h3>🚨 Alertas Ativos</h3>
                        <div class="metric-value" id="active-alerts">0</div>
                        <div class="metric-label">Alertas não resolvidos</div>
                    </div>
                </div>
                
                <div class="charts-grid">
                    <div class="chart-container">
                        <h3>📈 Performance ao Longo do Tempo</h3>
                        <canvas id="performance-chart"></canvas>
                    </div>
                    
                    <div class="chart-container">
                        <h3>🔍 Distribuição de Detecções</h3>
                        <canvas id="detection-chart"></canvas>
                    </div>
                </div>
                
                <div class="alerts-section">
                    <h3>🚨 Alertas Recentes</h3>
                    <div id="alerts-container">
                        <p>Nenhum alerta ativo no momento.</p>
                    </div>
                </div>
            </div>
            
            <script>
                // Configuração do WebSocket
                let ws = null;
                let performanceChart = null;
                let detectionChart = null;
                
                // Inicializar dashboard
                document.addEventListener('DOMContentLoaded', function() {
                    initializeCharts();
                    connectWebSocket();
                    refreshDashboard();
                    
                    // Atualizar a cada 5 segundos
                    setInterval(refreshDashboard, 5000);
                });
                
                function initializeCharts() {
                    // Gráfico de performance
                    const performanceCtx = document.getElementById('performance-chart').getContext('2d');
                    performanceChart = new Chart(performanceCtx, {
                        type: 'line',
                        data: {
                            labels: [],
                            datasets: [{
                                label: 'Tempo de Resposta (s)',
                                data: [],
                                borderColor: '
                                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                                tension: 0.4
                            }]
                        },
                        options: {
                            responsive: true,
                            scales: {
                                y: { beginAtZero: true }
                            }
                        }
                    });
                    
                    // Gráfico de detecções
                    const detectionCtx = document.getElementById('detection-chart').getContext('2d');
                    detectionChart = new Chart(detectionCtx, {
                        type: 'doughnut',
                        data: {
                            labels: ['Placas de Trânsito', 'Placas de Veículos', 'Veículos'],
                            datasets: [{
                                data: [0, 0, 0],
                                backgroundColor: ['#e74c3c', '#3498db', '
                            }]
                        },
                        options: {
                            responsive: true
                        }
                    });
                }
                
                function connectWebSocket() {
                    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                    const wsUrl = `${protocol}//${window.location.host}/ws`;
                    
                    ws = new WebSocket(wsUrl);
                    
                    ws.onopen = function() {
                        console.log('WebSocket conectado');
                        // Inscrever para atualizações
                        ws.send(JSON.stringify({
                            type: 'subscribe',
                            subscription_type: 'all'
                        }));
                    };
                    
                    ws.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        handleWebSocketMessage(data);
                    };
                    
                    ws.onclose = function() {
                        console.log('WebSocket desconectado');
                        // Tentar reconectar em 5 segundos
                        setTimeout(connectWebSocket, 5000);
                    };
                    
                    ws.onerror = function(error) {
                        console.error('Erro no WebSocket:', error);
                    };
                }
                
                function handleWebSocketMessage(data) {
                    switch(data.type) {
                        case 'dashboard_summary':
                            updateDashboardOverview(data.data);
                            break;
                        case 'metrics_update':
                            updateMetrics(data.data);
                            break;
                        case 'alerts_update':
                            updateAlerts(data.data);
                            break;
                    }
                }
                
                function updateDashboardOverview(data) {
                    const overview = data.overview;
                    document.getElementById('total-operations').textContent = overview.total_operations;
                    document.getElementById('success-rate').textContent = overview.success_rate;
                    document.getElementById('avg-response-time').textContent = overview.average_response_time;
                    document.getElementById('cpu-usage').textContent = overview.cpu_usage;
                    document.getElementById('memory-usage').textContent = overview.memory_usage;
                    document.getElementById('active-alerts').textContent = overview.active_alerts;
                    
                    // Atualizar indicadores de status
                    updateStatusIndicators(overview);
                }
                
                function updateMetrics(data) {
                    // Atualizar métricas em tempo real
                    if (data.system) {
                        document.getElementById('cpu-usage').textContent = data.system.cpu_percent.toFixed(1) + '%';
                        document.getElementById('memory-usage').textContent = data.system.memory_percent.toFixed(1) + '%';
                    }
                }
                
                function updateAlerts(data) {
                    const alertsContainer = document.getElementById('alerts-container');
                    const alerts = data.alerts;
                    
                    if (alerts.length === 0) {
                        alertsContainer.innerHTML = '<p>Nenhum alerta ativo no momento.</p>';
                        return;
                    }
                    
                    let alertsHtml = '';
                    alerts.forEach(alert => {
                        const alertClass = `alert-${alert.severity}`;
                        alertsHtml += `
                            <div class="alert-item ${alertClass}">
                                <strong>${alert.title}</strong><br>
                                ${alert.message}<br>
                                <small>${new Date(alert.timestamp).toLocaleString()}</small>
                            </div>
                        `;
                    });
                    
                    alertsContainer.innerHTML = alertsHtml;
                }
                
                function updateStatusIndicators(overview) {
                    const memoryStatus = document.getElementById('memory-status');
                    const memoryUsage = parseFloat(overview.memory_usage);
                    
                    if (memoryUsage < 70) {
                        memoryStatus.className = 'status-indicator status-healthy';
                    } else if (memoryUsage < 90) {
                        memoryStatus.className = 'status-indicator status-warning';
                    } else {
                        memoryStatus.className = 'status-indicator status-critical';
                    }
                }
                
                function refreshDashboard() {
                    fetch('/api/dashboard/summary')
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === 'success') {
                                updateDashboardOverview(data.data);
                            }
                        })
                        .catch(error => {
                            console.error('Erro ao atualizar dashboard:', error);
                        });
                }
            </script>
        </body>
        </html>
        try:
            metrics_collector.start_monitoring()
            
            alert_system.start_cleanup_thread()
            
            uvicorn.run(self.app, host=self.host, port=self.port)
            
        except KeyboardInterrupt:
            logger.info("Servidor interrompido pelo usuário")
        except Exception as e:
            logger.error(f"Erro ao iniciar servidor: {e}")
        finally:
            metrics_collector.stop_monitoring()
            alert_system.stop_cleanup_thread()
    
    def stop(self):
    dashboard = DashboardServer(host, port)
    dashboard.start()

if __name__ == "__main__":
    start_dashboard()