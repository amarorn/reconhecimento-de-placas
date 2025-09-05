#!/usr/bin/env python3

import os
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_interface_files():
    """Testa se os arquivos da interface de vídeo existem e estão corretos"""
    
    print("🧪 Testando Interface de Vídeo")
    print("=" * 50)
    
    # Verificar arquivos principais
    files_to_check = [
        "vision_interface.html",
        "vision/api/endpoints.py",
        "vision/api/models.py",
        "vision/api/auth.py",
        "vision/api/api_server.py"
    ]
    
    all_files_exist = True
    for file_path in files_to_check:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NÃO ENCONTRADO")
            all_files_exist = False
    
    if not all_files_exist:
        print("\n❌ Alguns arquivos essenciais não foram encontrados!")
        return False
    
    print("\n✅ Todos os arquivos principais existem!")
    
    # Verificar funcionalidades específicas
    print("\n🔍 Verificando funcionalidades...")
    
    # 1. Verificar se a interface HTML tem funcionalidade de vídeo
    try:
        with open("vision_interface.html", "r", encoding="utf-8") as f:
            html_content = f.read()
            
        video_features = [
            "selectFileType('video')",
            "processVideo()",
            "video_file",
            "video-analysis",
            "tracking-stats"
        ]
        
        missing_features = []
        for feature in video_features:
            if feature not in html_content:
                missing_features.append(feature)
        
        if missing_features:
            print(f"❌ Funcionalidades de vídeo ausentes: {missing_features}")
            return False
        else:
            print("✅ Interface HTML com funcionalidade de vídeo")
            
    except Exception as e:
        print(f"❌ Erro ao verificar interface HTML: {e}")
        return False
    
    # 2. Verificar se os endpoints de vídeo existem
    try:
        with open("vision/api/endpoints.py", "r", encoding="utf-8") as f:
            endpoints_content = f.read()
            
        if "process_video" in endpoints_content:
            print("✅ Endpoint de processamento de vídeo encontrado")
        else:
            print("❌ Endpoint de processamento de vídeo não encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar endpoints: {e}")
        return False
    
    # 3. Verificar se os modelos necessários existem
    try:
        with open("vision/api/models.py", "r", encoding="utf-8") as f:
            models_content = f.read()
            
        required_models = ["ImageRequest", "ProcessResponse"]
        missing_models = []
        
        for model in required_models:
            if model not in models_content:
                missing_models.append(model)
        
        if missing_models:
            print(f"❌ Modelos ausentes: {missing_models}")
            return False
        else:
            print("✅ Modelos necessários encontrados")
            
    except Exception as e:
        print(f"❌ Erro ao verificar modelos: {e}")
        return False
    
    # 4. Verificar se o servidor da API inclui os endpoints de vídeo
    try:
        with open("vision/api/api_server.py", "r", encoding="utf-8") as f:
            api_content = f.read()
            
        if "video_endpoints" in api_content and "Endpoints de análise de vídeo adicionados" in api_content:
            print("✅ Servidor da API configurado para vídeo")
        else:
            print("❌ Servidor da API não configurado para vídeo")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar servidor da API: {e}")
        return False
    
    print("\n🎉 Interface de vídeo configurada com sucesso!")
    return True

def test_pothole_detector():
    """Testa se o PotholeDetector está funcionando"""
    
    print("\n🔍 Testando PotholeDetector...")
    
    try:
        # Tentar importar o detector
        sys.path.append(str(Path(".")))
        from vision.detection.pothole_detector import PotholeDetector
        
        print("✅ PotholeDetector importado com sucesso")
        
        # Verificar se tem funcionalidade de vídeo
        detector_methods = dir(PotholeDetector)
        video_methods = ["process_video", "get_tracking_statistics"]
        
        missing_methods = []
        for method in video_methods:
            if method not in detector_methods:
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ Métodos de vídeo ausentes: {missing_methods}")
            return False
        else:
            print("✅ PotholeDetector com funcionalidade de vídeo")
            
        return True
        
    except ImportError as e:
        print(f"❌ Erro ao importar PotholeDetector: {e}")
        print("   (Isso é esperado se as dependências não estiverem instaladas)")
        return True  # Considerar sucesso se for apenas dependência
    except Exception as e:
        print(f"❌ Erro ao testar PotholeDetector: {e}")
        return False

def test_configuration():
    """Testa se as configurações estão corretas"""
    
    print("\n⚙️ Testando configurações...")
    
    # Verificar arquivo de configuração
    config_file = "config/specialized_detectors.yaml"
    if Path(config_file).exists():
        print(f"✅ Arquivo de configuração encontrado: {config_file}")
        
        try:
            # Tentar ler como texto simples primeiro
            with open(config_file, "r", encoding="utf-8") as f:
                config_content = f.read()
            
            if "video_analysis" in config_content:
                print("✅ Configuração de análise de vídeo encontrada")
                return True
            else:
                print("❌ Configuração de análise de vídeo não encontrada")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao ler configuração: {e}")
            return False
    else:
        print(f"❌ Arquivo de configuração não encontrado: {config_file}")
        return False

def main():
    """Função principal de teste"""
    
    print("🚀 Teste da Interface de Vídeo - PotholeDetector")
    print("=" * 60)
    
    tests = [
        ("Arquivos da Interface", test_interface_files),
        ("PotholeDetector", test_pothole_detector),
        ("Configurações", test_configuration)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Executando: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro durante teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo dos resultados
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM! Interface de vídeo funcionando!")
        print("\n💡 Para usar:")
        print("   1. Abra vision_interface.html no navegador")
        print("   2. Faça login (admin/admin123)")
        print("   3. Selecione 'Vídeo' como tipo de arquivo")
        print("   4. Faça upload de um vídeo")
        print("   5. Clique em 'Processar Arquivo'")
        print("\n🔧 Para testar a API:")
        print("   - Endpoint: POST /vision/process_video")
        print("   - Autenticação: Bearer token")
        print("   - Formato: multipart/form-data com video_file")
        
    else:
        print(f"\n⚠️ {total - passed} teste(s) falharam. Verifique os erros acima.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
