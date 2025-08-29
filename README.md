# 🚦 Dataset MBST - Placas de Sinalização Brasileiras

## 📚 **SOBRE O PROJETO**

Este projeto contém um **dataset completo e oficial** de placas de sinalização brasileiras extraído diretamente do **Manual Brasileiro de Sinalização de Trânsito (MBST)**. O dataset inclui 68 placas oficiais com códigos, nomes, significados, ações, penalidades, cores e formas.

## 🎯 **CARACTERÍSTICAS PRINCIPAIS**

- ✅ **68 placas oficiais** do MBST
- ✅ **Códigos oficiais** brasileiros (R-1, A-6, etc.)
- ✅ **Informações completas** (significado, ação, penalidade)
- ✅ **Características visuais** (cores, formas)
- ✅ **API REST completa** com FastAPI
- ✅ **Múltiplas opções** de hospedagem
- ✅ **Sistema de visão computacional** integrado

## 🚀 **INÍCIO RÁPIDO**

### **1. 📥 Clone o repositório**
```bash
git clone <seu-repositorio>
cd reconhecimento-de-placas
```

### **2. 🐳 Opção 1: Docker Compose (RECOMENDADA)**
```bash
# Iniciar todos os serviços
docker-compose up -d

# Popular banco de dados
python3 populate_database.py

# Acessar API
curl http://localhost:8000/health
```

### **3. 🐍 Opção 2: Python Local**
```bash
# Instalar dependências
pip install -r requirements.txt

# Executar API
python3 main.py

# Em outro terminal, testar
python3 test_api.py
```

## 🌐 **ACESSO AOS SERVIÇOS**

| Serviço | URL | Descrição |
|---------|-----|-----------|
| 🌐 **API REST** | http://localhost:8000 | Interface principal |
| 📖 **Swagger UI** | http://localhost:8000/docs | Documentação interativa |
| 📋 **ReDoc** | http://localhost:8000/redoc | Documentação alternativa |
| 📊 **Kibana** | http://localhost:5601 | Visualizações e dashboards |
| 🗄️ **PostgreSQL** | localhost:5432 | Banco de dados principal |
| 📄 **MongoDB** | localhost:27017 | Banco de dados JSON |

## 📚 **ENDPOINTS DA API**

### **🔍 Consultas Básicas**
- `GET /placas` - Lista todas as placas
- `GET /placas/{codigo}` - Busca por código (ex: R-1)
- `GET /placas/tipo/{tipo}` - Filtra por tipo
- `GET /stats` - Estatísticas do dataset
- `GET /download` - Download completo em JSON

### **🔍 Busca Avançada**
```bash
POST /placas/buscar
{
    "query": "cruzamento",
    "tipo": "advertencia",
    "cores": ["amarelo"],
    "formas": ["triangular"]
}
```

### **🏥 Monitoramento**
- `GET /health` - Status da API
- `GET /` - Página inicial

## 📊 **EXEMPLOS DE USO**

### **🔍 Buscar placa específica**
```bash
curl http://localhost:8000/placas/R-1
```

**Resposta:**
```json
{
    "codigo": "R-1",
    "nome": "PARE",
    "tipo": "regulamentacao",
    "significado": "Parada obrigatória",
    "acao": "Parar completamente",
    "penalidade": "Multa e pontos na carteira",
    "cores": ["vermelho", "branco"],
    "formas": ["octogonal"]
}
```

### **📊 Ver estatísticas**
```bash
curl http://localhost:8000/stats
```

**Resposta:**
```json
{
    "total_placas": 68,
    "por_tipo": {
        "regulamentacao": 36,
        "advertencia": 32
    },
    "por_codigo": {...},
    "data_geracao": "2025-08-29T01:36:34.901310"
}
```

### **🔍 Busca avançada**
```bash
curl -X POST http://localhost:8000/placas/buscar \
  -H "Content-Type: application/json" \
  -d '{"query": "cruzamento", "tipo": "advertencia"}'
```

## 🗄️ **ESTRUTURA DO DATASET**

### **📁 Arquivos principais**
```
dataset_mbst/
├── dataset_completo_mbst.json    # Dataset completo (68 placas)
├── relatorio_dataset_mbst.md     # Relatório detalhado
└── dataset_estruturado.json     # Dataset básico
```

### **🏷️ Tipos de placas**
- **R-*** - Regulamentação (36 placas)
- **A-*** - Advertência (32 placas)
- **I-*** - Informação
- **S-*** - Serviços
- **E-*** - Educação
- **P-*** - Prevenção

### **🎨 Cores disponíveis**
- **Vermelho** - Proibição/Obrigação
- **Amarelo** - Advertência
- **Azul** - Regulamentação/Informação
- **Verde** - Informação/Direção
- **Branco** - Texto/Fundo
- **Preto** - Contorno/Texto

### **🔷 Formas disponíveis**
- **Octogonal** - Pare (obrigatório)
- **Triangular** - Advertência
- **Circular** - Regulamentação
- **Retangular** - Informação
- **Quadrado** - Informação

## 🐳 **DOCKER COMPOSE**

### **🚀 Iniciar serviços**
```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

### **🔧 Serviços incluídos**
- **PostgreSQL** + PostGIS - Banco principal
- **MongoDB** - Banco JSON
- **Redis** - Cache
- **Elasticsearch** - Busca avançada
- **Kibana** - Visualizações
- **FastAPI** - API REST
- **Nginx** - Interface web

## 🗄️ **BANCO DE DADOS**

### **🐘 PostgreSQL**
```bash
# Conectar
psql -h localhost -U mbst_user -d mbst_dataset

# Ver tabelas
\dt

# Consultar placas
SELECT codigo, nome, tipo FROM placas_mbst LIMIT 5;
```

### **🍃 MongoDB**
```bash
# Conectar
mongosh mongodb://localhost:27017

# Usar banco
use mbst_dataset

# Consultar
db.placas_mbst.find({tipo: "advertencia"})
```

## 🧪 **TESTES**

### **🔍 Testar API**
```bash
# Executar testes completos
python3 test_api.py

# Testar endpoint específico
curl http://localhost:8000/health
```

### **📊 Verificar dados**
```bash
# Verificar população do banco
python3 populate_database.py

# Ver estatísticas
curl http://localhost:8000/stats
```

## ☁️ **OPÇÕES DE HOSPEDAGEM**

### **🏠 Desenvolvimento Local**
- **Docker Compose** - Solução completa
- **JSON local** - Simples e direto
- **SQLite** - Banco leve

### **🌐 Produção**
- **PostgreSQL** - Robusto e escalável
- **MongoDB** - Flexível para JSON
- **Elasticsearch** - Busca avançada

### **☁️ Cloud Gratuito**
- **Supabase** - PostgreSQL gratuito
- **MongoDB Atlas** - MongoDB gratuito
- **Railway** - Deploy automático

## 🔧 **CONFIGURAÇÃO**

### **📝 Variáveis de ambiente**
```bash
# Banco de dados
export DATABASE_URL="postgresql://mbst_user:mbst_password@localhost:5432/mbst_dataset"
export MONGODB_URL="mongodb://mbst_admin:mbst_password@localhost:27017"
export REDIS_URL="redis://localhost:6379"
export ELASTICSEARCH_URL="http://localhost:9200"
```

### **⚙️ Configurações da API**
```python
# main.py
app = FastAPI(
    title="API Dataset MBST",
    description="API para placas de sinalização brasileiras",
    version="1.0.0"
)
```

## 📈 **MONITORAMENTO**

### **🏥 Health Check**
```bash
curl http://localhost:8000/health
```

### **📊 Métricas**
```bash
# Estatísticas gerais
curl http://localhost:8000/stats

# Logs da API
docker-compose logs api
```

### **📈 Kibana Dashboard**
- Acesse: http://localhost:5601
- Crie visualizações para:
  - Total de placas por tipo
  - Distribuição de cores
  - Análise de formas
  - Estatísticas de uso

## 🚀 **VISÃO COMPUTACIONAL**

### **🔍 Processar imagens**
```bash
# Processar pasta de imagens
python3 vision_with_mbst.py

# Sistema dinâmico
python3 vision_dynamic.py
```

### **📊 Relatórios gerados**
- `relatorio_visao_mbst.md` - Com dataset MBST
- `relatorio_visao_dinamica.md` - Sistema dinâmico
- `relatorio_visao_simples.md` - Sistema simplificado

## 🤝 **CONTRIBUIÇÃO**

### **🔧 Desenvolvimento**
1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

### **🐛 Reportar bugs**
- Use as Issues do GitHub
- Inclua logs e screenshots
- Descreva os passos para reproduzir

## 📄 **LICENÇA**

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🙏 **AGRADECIMENTOS**

- **DENATRAN** - Manual Brasileiro de Sinalização de Trânsito
- **OpenCV** - Visão computacional
- **FastAPI** - Framework da API
- **PostgreSQL** - Banco de dados
- **Docker** - Containerização

## 📞 **SUPORTE**

- **📧 Email**: [seu-email@exemplo.com]
- **🐛 Issues**: [GitHub Issues]
- **📖 Wiki**: [Documentação completa]

---

## 🎉 **STATUS DO PROJETO**

- ✅ **Dataset MBST** - 68 placas extraídas
- ✅ **API REST** - FastAPI completa
- ✅ **Visão Computacional** - Sistema integrado
- ✅ **Docker Compose** - Ambiente completo
- ✅ **Documentação** - Guias e exemplos
- ✅ **Testes** - Scripts de validação

**🚀 O projeto está pronto para uso em produção!**

---

*Última atualização: 29 de Agosto de 2025*
