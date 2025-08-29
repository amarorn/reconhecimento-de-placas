# 🚀 **Guia Completo: APIs para Coleta Real de Dados Brasileiros**

## 📋 **Visão Geral**

Este guia te ensina como configurar as **APIs oficiais** para coletar imagens reais de placas brasileiras, substituindo a geração sintética por dados do mundo real.

## 🔑 **1. Google Custom Search API (Recomendada)**

### **Como Obter:**
1. **Acesse:** https://developers.google.com/custom-search
2. **Crie um projeto** no Google Cloud Console
3. **Ative a Custom Search API**
4. **Crie uma chave de API**
5. **Configure um motor de busca personalizado**

### **Configuração do Search Engine:**
1. **Acesse:** https://cse.google.com/cse/
2. **Clique em:** "Create a search engine"
3. **Configure:**
   - **Sites to search:** Deixe vazio (busca geral)
   - **Language:** Portuguese
   - **Region:** Brazil
   - **Image search:** ✅ Ativado
   - **SafeSearch:** ✅ Ativado
4. **Clique em:** "Create"
5. **Copie o Search Engine ID (cx)**

### **Custo:**
- **Primeiras 100 consultas/dia:** GRATUITAS
- **Consultas adicionais:** $5 por 1000 consultas

### **Exemplo de Uso:**
```python
api_key = "SUA_CHAVE_GOOGLE_API"
search_engine_id = "SEU_SEARCH_ENGINE_ID"

url = "https://www.googleapis.com/customsearch/v1"
params = {
    "key": api_key,
    "cx": search_engine_id,
    "q": "placa pare brasil",
    "searchType": "image",
    "num": 10,
    "imgType": "photo",
    "imgSize": "large"
}
```

---

## 📸 **2. Flickr API (Gratuita)**

### **Como Obter:**
1. **Acesse:** https://www.flickr.com/services/apps/create/
2. **Crie uma aplicação**
3. **Obtenha API Key e Secret**
4. **Configure permissões**

### **Custo:**
- **1000 consultas/hora:** GRATUITAS
- **Sem limite diário**

### **Exemplo de Uso:**
```python
import flickrapi

api_key = "SUA_FLICKR_API_KEY"
api_secret = "SEU_FLICKR_SECRET"

flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json')

photos = flickr.photos.search(
    text="placas trânsito brasil",
    per_page=100,
    sort="relevance"
)
```

---

## 🎨 **3. Unsplash API (Gratuita)**

### **Como Obter:**
1. **Acesse:** https://unsplash.com/developers
2. **Crie uma conta de desenvolvedor**
3. **Obtenha Access Key**

### **Custo:**
- **5000 consultas/hora:** GRATUITAS
- **Sem limite diário**

### **Exemplo de Uso:**
```python
import requests

access_key = "SUA_UNSPLASH_ACCESS_KEY"
url = "https://api.unsplash.com/search/photos"
headers = {"Authorization": f"Client-ID {access_key}"}

params = {
    "query": "brazilian traffic signs",
    "per_page": 30
}

response = requests.get(url, headers=headers, params=params)
```

---

## 🖼️ **4. Pexels API (Gratuita)**

### **Como Obter:**
1. **Acesse:** https://www.pexels.com/api/
2. **Crie uma conta**
3. **Obtenha API Key**

### **Custo:**
- **200 consultas/hora:** GRATUITAS
- **Sem limite diário**

---

## 🇧🇷 **5. Fontes Específicas para Dados Brasileiros**

### **APIs de Órgãos de Trânsito:**
- **DETRAN SP:** https://www.detran.sp.gov.br/
- **DETRAN RJ:** https://www.detran.rj.gov.br/
- **DETRAN MG:** https://www.detran.mg.gov.br/

### **Bancos de Dados Acadêmicos:**
- **Kaggle Datasets:** Brazilian Traffic Sign Recognition
- **GitHub:** Projetos brasileiros de visão computacional

---

## ⚙️ **6. Configuração no Script**

### **Atualizar as Chaves:**
```python
# No arquivo scripts/collect_brazilian_data.py

# Google API
api_key = "SUA_CHAVE_GOOGLE_API"
search_engine_id = "SEU_SEARCH_ENGINE_ID"

# Flickr API
flickr_api_key = "SUA_FLICKR_API_KEY"

# Unsplash API
unsplash_access_key = "SUA_UNSPLASH_ACCESS_KEY"

# Pexels API
pexels_api_key = "SUA_PEXELS_API_KEY"
```

### **Variáveis de Ambiente (Recomendado):**
```bash
# .env
GOOGLE_API_KEY=sua_chave_aqui
GOOGLE_SEARCH_ENGINE_ID=seu_id_aqui
FLICKR_API_KEY=sua_chave_aqui
UNSPLASH_ACCESS_KEY=sua_chave_aqui
PEXELS_API_KEY=sua_chave_aqui
```

---

## 🎯 **7. Termos de Busca Recomendados**

### **Placas de Sinalização:**
```
- "placa pare brasil"
- "placa dê preferência brasil"
- "placa limite velocidade brasil"
- "placa proibido estacionar brasil"
- "sinais trânsito brasil"
- "placas trânsito brasileiras"
```

### **Placas de Veículos:**
```
- "placa mercosul brasil"
- "placa padrão antigo brasil"
- "placa diplomática brasil"
- "placa oficial brasil"
- "placas veículos brasil"
- "carros brasil placas"
```

---

## 🚀 **8. Como Usar**

### **1. Configure as APIs:**
```bash
# Edite o arquivo de configuração
nano scripts/collect_brazilian_data.py

# Ou use variáveis de ambiente
export GOOGLE_API_KEY="sua_chave"
```

### **2. Teste a Coleta:**
```bash
# Teste com Google API
python scripts/collect_brazilian_data.py --source google --max-images 10

# Teste com Flickr API
python scripts/collect_brazilian_data.py --source flickr --max-images 10
```

### **3. Coleta Completa:**
```bash
# Coleta de todas as fontes
python scripts/collect_brazilian_data.py --source all --max-images 100
```

---

## ⚠️ **9. Limitações e Considerações**

### **Direitos Autorais:**
- **Respeite** os termos de uso das APIs
- **Use** filtros de licença (Creative Commons)
- **Atribua** créditos quando necessário

### **Rate Limiting:**
- **Google:** 100 consultas/dia gratuitas
- **Flickr:** 1000 consultas/hora
- **Unsplash:** 5000 consultas/hora
- **Pexels:** 200 consultas/hora

### **Qualidade dos Dados:**
- **Verifique** a relevância das imagens
- **Filtre** por tamanho e qualidade
- **Valide** as anotações geradas

---

## 💡 **10. Dicas de Otimização**

### **Busca Eficiente:**
- Use termos específicos em português
- Combine palavras-chave relevantes
- Teste diferentes variações

### **Download Inteligente:**
- Implemente retry automático
- Use timeouts apropriados
- Salve metadados das imagens

### **Processamento:**
- Valide formato das imagens
- Redimensione se necessário
- Gere anotações automáticas

---

## 🎉 **11. Resultado Esperado**

Com as APIs configuradas, você terá:

✅ **Imagens reais** de placas brasileiras
✅ **Variedade** de cenários e condições
✅ **Qualidade** profissional para treinamento
✅ **Dados autênticos** do mundo real
✅ **Melhor performance** dos modelos YOLO

---

## 📞 **12. Suporte e Recursos**

### **Documentação Oficial:**
- **Google:** https://developers.google.com/custom-search
- **Flickr:** https://www.flickr.com/services/api/
- **Unsplash:** https://unsplash.com/developers
- **Pexels:** https://www.pexels.com/api/

### **Comunidade:**
- **Stack Overflow:** Tags específicas das APIs
- **GitHub:** Exemplos e implementações
- **Fóruns:** Discussões sobre visão computacional

---

**🚀 Agora você tem tudo para coletar dados reais de placas brasileiras e treinar modelos YOLO de alta qualidade!**
