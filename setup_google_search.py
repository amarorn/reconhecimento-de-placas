#!/usr/bin/env python3
"""
Script para configurar o Google Custom Search Engine
===================================================

Este script ajuda a configurar um Search Engine personalizado para a API do Google.
"""

import requests
import json

def create_search_engine():
    """Cria um Search Engine personalizado"""
    print("🔧 Configurando Google Custom Search Engine...")
    
    # Sua chave de API
    api_key = "AIzaSyDAFvNVY8BP2Vw7IIxBkKA3jJNXCJISHmE"
    
    # URL para criar Search Engine
    url = "https://www.googleapis.com/customsearch/v1/siterestrict"
    
    print("\n📋 Para criar um Search Engine personalizado:")
    print("1. Acesse: https://cse.google.com/cse/")
    print("2. Clique em 'Create a search engine'")
    print("3. Configure:")
    print("   - Sites to search: Deixe vazio (busca geral)")
    print("   - Language: Portuguese")
    print("   - Region: Brazil")
    print("4. Clique em 'Create'")
    print("5. Copie o Search Engine ID (cx)")
    
    print(f"\n🔑 Sua API Key: {api_key}")
    print("💡 Use esta chave no script principal")
    
    # Testar a API com um Search Engine existente
    print("\n🧪 Testando API com Search Engine padrão...")
    
    test_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": "017576662512468239146:omuauf_lfve",  # Search Engine padrão
        "q": "brazilian traffic signs",
        "searchType": "image",
        "num": 1
    }
    
    try:
        response = requests.get(test_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if "items" in data:
                print("✅ API funcionando! Encontradas imagens.")
                print(f"   Primeira imagem: {data['items'][0]['title']}")
            else:
                print("⚠️  API funcionando, mas sem resultados.")
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(f"   Resposta: {response.text}")
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")

def show_usage_examples():
    """Mostra exemplos de uso da API"""
    print("\n📚 Exemplos de uso da API:")
    
    examples = [
        "placa pare brasil",
        "placa dê preferência brasil", 
        "placa limite velocidade brasil",
        "placa proibido estacionar brasil",
        "placa mercosul brasil",
        "placa padrão antigo brasil",
        "sinais trânsito brasil",
        "placas veículos brasil"
    ]
    
    for example in examples:
        print(f"   • {example}")
    
    print("\n💡 Dicas:")
    print("   - Use termos em português brasileiro")
    print("   - Inclua 'brasil' ou 'brasileiro' na busca")
    print("   - Combine 'placa' + tipo + 'brasil'")

if __name__ == "__main__":
    print("🚀 Configurador do Google Custom Search Engine")
    print("=" * 50)
    
    create_search_engine()
    show_usage_examples()
    
    print("\n🎯 Próximos passos:")
    print("1. Configure o Search Engine no Google CSE")
    print("2. Atualize o Search Engine ID no script principal")
    print("3. Teste a coleta de imagens reais")
    print("4. Ajuste os parâmetros conforme necessário")
