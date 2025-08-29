#!/usr/bin/env python3
"""
Script para debugar a API do Google e ver exatamente o que está retornando
"""

import requests
import json

def debug_google_api():
    """Debuga a API do Google para entender o problema"""
    
    api_key = "AIzaSyDAFvNVY8BP2Vw7IIxBkKA3jJNXCJISHmE"
    search_engine_id = "b482e980c4b39432f"
    
    # Query que sabemos que funcionou no teste
    query = "stop sign brazil"
    
    print(f"🔍 Debugando query: {query}")
    print(f"🔑 API Key: {api_key}")
    print(f"🔧 Search Engine ID: {search_engine_id}")
    print("=" * 60)
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": search_engine_id,
        "q": query,
        "searchType": "image",
        "num": 3,
        "imgType": "photo",
        "imgSize": "large",
        "safe": "active",
        "rights": "cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial|cc_nonderived"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
    try:
        print("📡 Fazendo requisição...")
        response = requests.get(url, params=params, headers=headers)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resposta JSON recebida")
            print(f"📋 Chaves na resposta: {list(data.keys())}")
            
            if "items" in data:
                items = data["items"]
                print(f"🎯 Items encontrados: {len(items)}")
                
                for i, item in enumerate(items):
                    print(f"\n📸 Item {i}:")
                    print(f"   Título: {item.get('title', 'Sem título')}")
                    print(f"   Link: {item.get('link', 'Sem link')}")
                    print(f"   Snippet: {item.get('snippet', 'Sem snippet')}")
                    print(f"   Chaves: {list(item.keys())}")
            else:
                print("❌ Nenhum 'items' na resposta")
                print(f"📄 Resposta completa: {json.dumps(data, indent=2)}")
                
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    debug_google_api()
