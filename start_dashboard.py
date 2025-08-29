#!/usr/bin/env python3
"""
Inicializador do Dashboard - Visão Computacional
===============================================
"""

import sys
import os
import threading
import time
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

def start_dashboard():
    """Inicia o dashboard web"""
    try:
        print("🚀 Iniciando dashboard web...")
        
        from vision.dashboard.dashboard_server import start_dashboard
        start_dashboard(host="0.0.0.0", port=8080)
        
    except ImportError as e:
        print(f"❌ Erro ao importar dashboard: {e}")
        print("Verifique se as dependências estão instaladas")
    except Exception as e:
        print(f"❌ Erro ao iniciar dashboard: {e}")

def start_api():
    """Inicia a API REST"""
    try:
        print("🌐 Iniciando API REST...")
        
        from vision.api.api_server import VisionAPI
        import uvicorn
        
        # Criar API
        api = VisionAPI(debug=True)
        
        # Iniciar servidor
        uvicorn.run(api.app, host="0.0.0.0", port=8000)
        
    except ImportError as e:
        print(f"❌ Erro ao importar API: {e}")
    except Exception as e:
        print(f"❌ Erro ao iniciar API: {e}")

def main():
    """Função principal"""
    print("🎯 Iniciando Sistema Completo - Visão Computacional")
    print("=" * 60)
    
    # Iniciar API em thread separada
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()
    
    # Aguardar API inicializar
    time.sleep(5)
    
    # Iniciar dashboard
    start_dashboard()

if __name__ == "__main__":
    main()
