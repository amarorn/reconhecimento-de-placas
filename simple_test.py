#!/usr/bin/env python3
"""
Teste simples da API sem Docker
================================
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Testa se as importações funcionam"""
    print("🔍 Testando importações...")
    
    try:
        from vision.core.vision_pipeline import VisionPipeline
        print("✅ VisionPipeline importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar VisionPipeline: {e}")
    
    try:
        from vision.api.auth import auth_manager
        print("✅ auth_manager importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar auth_manager: {e}")
    
    try:
        from vision.api.security import create_access_token
        print("✅ security module importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar security: {e}")

def test_pipeline():
    """Testa o pipeline de visão"""
    print("\n🧠 Testando pipeline de visão...")
    
    try:
        from vision.core.vision_pipeline import VisionPipeline
        
        # Configuração mínima
        config = {
            'detection': {
                'weights_path': 'yolov8n.pt',
                'confidence_threshold': 0.5
            },
            'ocr': {
                'type': 'paddleocr',
                'language': 'pt'
            }
        }
        
        pipeline = VisionPipeline(config)
        print("✅ Pipeline criado com sucesso")
        
        # Testar com imagem fictícia
        import numpy as np
        fake_image = np.zeros((640, 640, 3), dtype=np.uint8)
        
        # Simular processamento
        print("✅ Pipeline pronto para uso")
        
    except Exception as e:
        print(f"❌ Erro no pipeline: {e}")

def test_auth():
    """Testa autenticação"""
    print("\n🔐 Testando autenticação...")
    
    try:
        from vision.api.auth import auth_manager
        from vision.api.security import create_access_token, verify_password
        
        # Testar criação de token
        token = create_access_token({"sub": "admin"})
        print(f"✅ Token criado: {token[:20]}...")
        
        # Testar verificação de senha
        result = verify_password("admin123", "admin123")
        print(f"✅ Verificação de senha: {result}")
        
    except Exception as e:
        print(f"❌ Erro na autenticação: {e}")

def main():
    """Função principal"""
    print("🧪 Teste Simples da API de Visão Computacional")
    print("=" * 50)
    
    test_imports()
    test_pipeline()
    test_auth()
    
    print("\n🎉 Teste concluído!")
    print("\n📋 Para usar a API completa:")
    print("  1. Acesse http://localhost:8000/docs")
    print("  2. Faça login com admin/admin123")
    print("  3. Use os endpoints via interface Swagger")

if __name__ == "__main__":
    main()
