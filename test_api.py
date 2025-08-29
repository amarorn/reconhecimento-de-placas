#!/usr/bin/env python3
"""
Script de teste para API MBST
=============================

Testa todos os endpoints da API para verificar funcionamento
"""

import requests
import json
import time
from datetime import datetime

# Configuração da API
API_BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint: str, method: str = "GET", data: dict = None):
    """Testa um endpoint específico"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            print(f"❌ Método {method} não suportado")
            return False
        
        if response.status_code == 200:
            print(f"✅ {method} {endpoint} - OK")
            return True
        else:
            print(f"❌ {method} {endpoint} - Status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {endpoint} - API não está rodando")
        return False
    except Exception as e:
        print(f"❌ {method} {endpoint} - Erro: {e}")
        return False

def test_all_endpoints():
    """Testa todos os endpoints da API"""
    print("🧪 TESTANDO API MBST")
    print("=" * 40)
    
    tests = [
        # Endpoints básicos
        ("/", "GET"),
        ("/health", "GET"),
        ("/stats", "GET"),
        ("/download", "GET"),
        
        # Endpoints de placas
        ("/placas", "GET"),
        ("/placas?limit=5", "GET"),
        ("/placas/R-1", "GET"),
        ("/placas/A-6", "GET"),
        ("/placas/tipo/regulamentacao", "GET"),
        ("/placas/tipo/advertencia", "GET"),
        
        # Busca avançada
        ("/placas/buscar", "POST", {
            "query": "cruzamento",
            "tipo": "advertencia"
        }),
        ("/placas/buscar", "POST", {
            "query": "vermelho",
            "cores": ["vermelho"]
        }),
        ("/placas/buscar", "POST", {
            "query": "triangular",
            "formas": ["triangular"]
        })
    ]
    
    passed = 0
    total = len(tests)
    
    for endpoint, method, *args in tests:
        data = args[0] if args else None
        if test_endpoint(endpoint, method, data):
            passed += 1
        time.sleep(0.1)  # Pequena pausa entre testes
    
    print("\n📊 RESULTADO DOS TESTES:")
    print(f"   ✅ Passou: {passed}")
    print(f"   ❌ Falhou: {total - passed}")
    print(f"   📈 Taxa de sucesso: {(passed/total)*100:.1f}%")
    
    return passed == total

def test_specific_queries():
    """Testa consultas específicas"""
    print("\n🔍 TESTANDO CONSULTAS ESPECÍFICAS")
    print("=" * 40)
    
    try:
        # Testar busca por código
        response = requests.get(f"{API_BASE_URL}/placas/R-1")
        if response.status_code == 200:
            placa = response.json()
            print(f"✅ Placa R-1: {placa['nome']}")
            print(f"   Tipo: {placa['tipo']}")
            print(f"   Cores: {', '.join(placa['cores'])}")
        
        # Testar estatísticas
        response = requests.get(f"{API_BASE_URL}/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Estatísticas:")
            print(f"   Total de placas: {stats['total_placas']}")
            print(f"   Por tipo: {stats['por_tipo']}")
        
        # Testar busca avançada
        response = requests.post(f"{API_BASE_URL}/placas/buscar", json={
            "query": "cruzamento",
            "tipo": "advertencia"
        })
        if response.status_code == 200:
            resultados = response.json()
            print(f"✅ Busca por 'cruzamento': {len(resultados)} resultados")
            for placa in resultados[:3]:
                print(f"   - {placa['codigo']}: {placa['nome']}")
        
    except Exception as e:
        print(f"❌ Erro nos testes específicos: {e}")

def main():
    """Função principal"""
    print("🚀 TESTE COMPLETO DA API MBST")
    print("=" * 50)
    print(f"🌐 URL da API: {API_BASE_URL}")
    print(f"⏰ Início: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # Verificar se a API está rodando
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"🏥 Status da API: {health['status']}")
            print(f"📊 Total de placas: {health['total_placas']}")
            print(f"🔢 Versão: {health['version']}")
            print()
        else:
            print("❌ API não está respondendo corretamente")
            return
    except:
        print("❌ API não está rodando. Execute: python3 main.py")
        return
    
    # Executar testes
    success = test_all_endpoints()
    
    if success:
        test_specific_queries()
    
    print(f"\n⏰ Fim: {datetime.now().strftime('%H:%M:%S')}")
    
    if success:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sua API MBST está funcionando perfeitamente!")
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM!")
        print("🔧 Verifique os logs da API para mais detalhes")

if __name__ == "__main__":
    main()
