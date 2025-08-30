

import sys
import os
import threading
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

def start_dashboard():
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
    try:
        print("🌐 Iniciando API REST...")
        
        from vision.api.api_server import VisionAPI
        import uvicorn
        
        api = VisionAPI(debug=True)
        
        uvicorn.run(api.app, host="0.0.0.0", port=8000)
        
    except ImportError as e:
        print(f"❌ Erro ao importar API: {e}")
    except Exception as e:
        print(f"❌ Erro ao iniciar API: {e}")

def main():
    print("🎯 Iniciando Sistema Completo - Visão Computacional")
    print("=" * 60)
    
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()
    
    time.sleep(5)
    
    start_dashboard()

if __name__ == "__main__":
    main()
