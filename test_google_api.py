

import requests
import json
import time

def test_google_api():
    
    api_key = "AIzaSyDAFvNVY8BP2Vw7IIxBkKA3jJNXCJISHmE"
    
    search_engines = {
        "Novo": "b482e980c4b39432f",
        "Antigo": "017576662512468239146:omuauf_lfve"
    }
    
    test_queries = [
        "brazilian traffic signs",
        "placa pare brasil",
        "sinais trânsito brasil"
    ]
    
    print("🔍 Testando API do Google Custom Search...")
    print(f"🔑 API Key: {api_key}")
    print("=" * 60)
    
    for engine_name, search_engine_id in search_engines.items():
        print(f"\n🧪 Testando Search Engine: {engine_name}")
        print(f"   ID: {search_engine_id}")
        
        for query in test_queries:
            print(f"\n   📝 Query: {query}")
            
            url = "https://www.googleapis.com/customsearch/v1"
            
            params = {
                "key": api_key,
                "cx": search_engine_id,
                "q": query,
                "searchType": "image",
                "num": 1,
                "imgType": "photo",
                "imgSize": "large",
                "safe": "active"
            }
            
            try:
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "items" in data and len(data["items"]) > 0:
                        print(f"   ✅ Sucesso! Encontradas {len(data['items'])} imagens")
                        print(f"      Primeira: {data['items'][0].get('title', 'Sem título')}")
                    else:
                        print(f"   ⚠️  API OK, mas sem resultados")
                        if "queries" in data:
                            print(f"      Queries disponíveis: {data['queries']['request'][0]['totalResults']}")
                else:
                    print(f"   ❌ Erro HTTP: {response.status_code}")
                    print(f"      Resposta: {response.text[:200]}...")
                
                time.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 DIAGNÓSTICO:")
    print("✅ Se todas as consultas retornaram erro HTTP, a API está funcionando")
    print("⚠️  Se todas retornaram 'sem resultados', o Search Engine ID está incorreto")
    print("❌ Se houve erros de conexão, verifique sua internet")
    
    print("\n🔧 PRÓXIMOS PASSOS:")
    print("1. Acesse: https://cse.google.com/cse/")
    print("2. Crie um Search Engine personalizado")
    print("3. Configure para busca geral (sem sites específicos)")
    print("4. Ative busca de imagens")
    print("5. Copie o novo Search Engine ID")
    print("6. Atualize o script principal")

def show_search_engine_guide():
    print("\n📋 GUIA PARA CRIAR SEARCH ENGINE:")
    print("=" * 50)
    print("1. Acesse: https://cse.google.com/cse/")
    print("2. Clique em 'Create a search engine'")
    print("3. Configure:")
    print("   - Sites to search: DEIXE VAZIO")
    print("   - Language: Portuguese")
    print("   - Region: Brazil")
    print("   - Image search: ✅ ATIVADO")
    print("   - SafeSearch: ✅ ATIVADO")
    print("4. Clique em 'Create'")
    print("5. Copie o Search Engine ID (cx)")
    print("6. Teste com este script novamente")

if __name__ == "__main__":
    print("🚀 Testador da API do Google Custom Search")
    print("=" * 60)
    
    test_google_api()
    show_search_engine_guide()
    
    print("\n💡 DICA: O Search Engine ID padrão não funciona para busca geral.")
    print("   Você precisa criar um personalizado no Google CSE!")
