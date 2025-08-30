

import http.server
import socketserver
import webbrowser
import threading
import time
import os
from pathlib import Path

PORT = 3000
INTERFACE_FILE = "vision_interface.html"

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/' or self.path == '':
            self.path = f'/{INTERFACE_FILE}'
        
        return super().do_GET()
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

def start_server():
    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print(f"🌐 Servidor iniciado em http://localhost:{PORT}")
            print(f"📁 Servindo arquivo: {INTERFACE_FILE}")
            print("🔗 Abrindo navegador...")
            
            threading.Timer(2.0, lambda: webbrowser.open(f'http://localhost:{PORT}')).start()
            
            print(f"✅ Interface disponível em: http://localhost:{PORT}")
            print("Pressione Ctrl+C para parar")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")

def check_files():
    if not Path(INTERFACE_FILE).exists():
        print(f"❌ Arquivo {INTERFACE_FILE} não encontrado")
        return False
    
    print(f"✅ Arquivo {INTERFACE_FILE} encontrado")
    return True

def main():
    print("🚀 Iniciando Interface Web - Visão Computacional")
    print("=" * 50)
    
    if not check_files():
        print("Certifique-se de que o arquivo vision_interface.html existe")
        return
    
    print(f"📋 Configuração:")
    print(f"  - Porta: {PORT}")
    print(f"  - Interface: {INTERFACE_FILE}")
    print(f"  - API: http://localhost:8000")
    print()
    
    start_server()

if __name__ == "__main__":
    main()
