# 🚀 **SISTEMA MBST AVANÇADO - VISÃO COMPUTACIONAL COMPLETA**

## 🎯 **SOBRE O PROJETO**

Este é um sistema **completo e avançado** de visão computacional para análise de placas de sinalização brasileiras, implementando as **melhores práticas** da indústria e **tecnologias de ponta**.

---

## ✨ **FUNCIONALIDADES IMPLEMENTADAS**

### **🏠 1. INTERFACE WEB MODERNA**
- **Design responsivo** com Tailwind CSS
- **Upload drag & drop** de imagens
- **Progress bars** em tempo real
- **Cards interativos** com hover effects
- **Sistema de notificações** elegante
- **Modais** para feedback e sugestões

### **🤖 2. SISTEMA AVANÇADO DE VISÃO COMPUTACIONAL**
- **Detecção YOLO** treinada para placas brasileiras
- **OCR integrado** (EasyOCR) para leitura de texto
- **Classificação inteligente** baseada em características visuais
- **Análise de cores** (HSV) e formas
- **Sistema de confiança** dinâmico
- **Processamento em lote** otimizado

### **🎯 3. SISTEMA DE FINE-TUNING**
- **Pipeline completo** de treinamento
- **Geração automática** de anotações YOLO
- **Divisão inteligente** de datasets (train/val/test)
- **Data augmentation** configurável
- **Métricas de avaliação** (mAP, precision, recall)
- **Relatórios visuais** com matplotlib/seaborn

### **🗄️ 4. BANCO DE DADOS POSTGRESQL**
- **68 placas oficiais** do MBST
- **API REST completa** com FastAPI
- **Swagger UI** para documentação
- **Sistema de feedback** integrado
- **Estatísticas em tempo real**

### **🔧 5. SISTEMA DE FEEDBACK**
- **Correção de classificações** incorretas
- **Sugestões de melhoria** do sistema
- **Banco de dados** para histórico
- **Métricas de qualidade** do sistema
- **Exportação** de dados

---

## 🚀 **INSTALAÇÃO E CONFIGURAÇÃO**

### **📋 PRÉ-REQUISITOS**
```bash
# Python 3.8+
python3 --version

# Docker (opcional, para PostgreSQL)
docker --version

# Git
git --version
```

### **🐳 INSTALAÇÃO COM DOCKER (RECOMENDADA)**
```bash
# 1. Clone o repositório
git clone <seu-repositorio>
cd reconhecimento-de-placas

# 2. Iniciar PostgreSQL
docker-compose up postgres -d

# 3. Popular banco de dados
python3 populate_database.py

# 4. Instalar dependências Python
pip3 install -r requirements.txt

# 5. Iniciar API
python3 main.py

# 6. Acessar interface web
# Abra: http://localhost:8080
```

### **🐍 INSTALAÇÃO LOCAL**
```bash
# 1. Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar PostgreSQL local
# (ver seção de banco de dados)

# 4. Iniciar sistema
python3 main.py
```

---

## 🌐 **ACESSO AOS SERVIÇOS**

| Serviço | URL | Descrição |
|---------|-----|-----------|
| 🌐 **Interface Web** | http://localhost:8080 | Interface principal moderna |
| 🚀 **API REST** | http://localhost:8000 | API completa com Swagger |
| 📖 **Swagger UI** | http://localhost:8000/docs | Documentação interativa |
| 📋 **ReDoc** | http://localhost:8000/redoc | Documentação alternativa |
| 🗄️ **PostgreSQL** | localhost:5432 | Banco de dados principal |

---

## 🎨 **USO DA INTERFACE WEB**

### **📤 Upload de Imagens**
1. **Arraste e solte** imagens na área de upload
2. **Clique** para selecionar arquivos
3. **Suporte**: JPG, PNG, BMP (máx. 10MB)
4. **Progress bar** em tempo real

### **🔍 Análise Automática**
1. **Detecção YOLO** de placas
2. **OCR** para leitura de texto
3. **Classificação** por tipo e características
4. **Resultados visuais** organizados

### **📊 Visualização de Resultados**
- **Cards organizados** por imagem
- **Métricas de confiança** coloridas
- **Detalhes completos** de cada detecção
- **Ações**: Corrigir, Download, Compartilhar

---

## 🤖 **SISTEMA DE VISÃO COMPUTACIONAL**

### **🔍 Detecção YOLO**
```python
# Usar sistema avançado
from advanced_vision_system import MBSTVisionSystem

vision_system = MBSTVisionSystem()
result = vision_system.process_image_complete("imagem.jpg")

# Resultado inclui:
# - Detecções YOLO com bounding boxes
# - Classificação por tipo de placa
# - OCR do texto detectado
# - Métricas de confiança
```

### **📝 OCR Integrado**
```python
# OCR automático nas regiões detectadas
ocr_result = vision_system.extract_text_ocr("imagem.jpg", bbox)
# Retorna: texto, confiança, coordenadas
```

### **🏷️ Classificação Inteligente**
```python
# Classificação baseada em características visuais
classification = vision_system.classify_plate_type(
    "imagem.jpg", bbox, ocr_text
)
# Combina análise visual + textual
```

---

## 🎯 **SISTEMA DE FINE-TUNING**

### **🚀 Pipeline Completo**
```bash
# Executar pipeline completo
python3 fine_tuning_system.py

# O sistema irá:
# 1. Gerar anotações YOLO automaticamente
# 2. Dividir dataset (80% treino, 10% val, 10% teste)
# 3. Treinar modelo YOLO customizado
# 4. Avaliar performance
# 5. Gerar relatórios visuais
```

### **📊 Geração de Anotações**
```python
# Gerar anotações para dataset
fine_tuning = MBSTFineTuningSystem()
annotations = fine_tuning.generate_annotations(image_files)

# Salva em formato YOLO (.txt)
# Cria dataset.yaml para treinamento
```

### **🎓 Treinamento de Modelos**
```python
# Treinar YOLO customizado
success = fine_tuning.train_yolo_model("dataset.yaml")

# Configurações personalizáveis:
# - Épocas, batch size, learning rate
# - Data augmentation
# - Early stopping
```

---

## 🗄️ **BANCO DE DADOS E API**

### **🔍 Consultas SQL**
```sql
-- Conectar ao PostgreSQL
docker exec -it mbst_postgres psql -U mbst_user -d mbst_dataset

-- Consultas úteis
SELECT COUNT(*) FROM placas_mbst;
SELECT codigo, nome, tipo FROM placas_mbst WHERE tipo = 'advertencia';
SELECT tipo, COUNT(*) FROM placas_mbst GROUP BY tipo;
```

### **🌐 API REST**
```bash
# Listar todas as placas
curl http://localhost:8000/placas

# Buscar por código
curl http://localhost:8000/placas/R-1

# Busca avançada
curl -X POST http://localhost:8000/placas/buscar \
  -H "Content-Type: application/json" \
  -d '{"query": "cruzamento", "tipo": "advertencia"}'

# Estatísticas
curl http://localhost:8000/stats
```

---

## 🔧 **CONFIGURAÇÃO AVANÇADA**

### **⚙️ Configuração de Visão Computacional**
```json
// config/vision_config.json
{
    "models": {
        "yolo": {
            "confidence_threshold": 0.5,
            "input_size": 640
        },
        "ocr": {
            "languages": ["pt", "en"],
            "confidence_threshold": 0.3
        }
    },
    "processing": {
        "visual_weight": 0.6,
        "text_weight": 0.4
    }
}
```

### **🎯 Configuração de Fine-tuning**
```json
// config/fine_tuning_config.json
{
    "yolo_config": {
        "epochs": 100,
        "batch_size": 16,
        "patience": 20
    },
    "data_augmentation": {
        "rotation": [-15, 15],
        "brightness": [0.8, 1.2]
    }
}
```

---

## 📊 **MONITORAMENTO E MÉTRICAS**

### **🏥 Health Checks**
```bash
# Verificar status da API
curl http://localhost:8000/health

# Resposta:
{
    "status": "healthy",
    "total_placas": 68,
    "version": "1.0.0"
}
```

### **📈 Estatísticas do Sistema**
```bash
# Estatísticas gerais
curl http://localhost:8000/stats

# Estatísticas de feedback
python3 -c "
from advanced_vision_system import MBSTVisionSystem
vision = MBSTVisionSystem()
print(vision.get_feedback_stats())
"
```

---

## 🚀 **CASOS DE USO AVANÇADOS**

### **📸 Processamento em Lote**
```python
# Processar pasta completa
vision_system = MBSTVisionSystem()
results = vision_system.process_batch("pasta_imagens/")

# Resultados salvos automaticamente
# Relatórios em JSON e visualizações
```

### **🎯 Fine-tuning Personalizado**
```python
# Treinar com dataset específico
fine_tuning = MBSTFineTuningSystem()
fine_tuning.dataset_path = "meu_dataset/"
fine_tuning.run_complete_pipeline()
```

### **🔍 Análise de Performance**
```python
# Avaliar modelo treinado
metrics = fine_tuning.evaluate_model(
    "modelo_treinado.pt", 
    "dataset_teste.yaml"
)
# Retorna: mAP, precision, recall, F1-score
```

---

## 🛠️ **MANUTENÇÃO E ATUALIZAÇÕES**

### **🔄 Atualizar Dependências**
```bash
# Atualizar Python
pip install --upgrade -r requirements.txt

# Atualizar modelos YOLO
pip install --upgrade ultralytics

# Atualizar OpenCV
pip install --upgrade opencv-python
```

### **💾 Backup do Banco**
```bash
# Backup PostgreSQL
docker exec mbst_postgres pg_dump -U mbst_user mbst_dataset > backup.sql

# Restaurar backup
docker exec -i mbst_postgres psql -U mbst_user mbst_dataset < backup.sql
```

### **📊 Limpeza de Logs**
```bash
# Limpar logs antigos
find logs/ -name "*.log" -mtime +30 -delete

# Limpar resultados antigos
find results/ -name "*_analysis_*.json" -mtime +7 -delete
```

---

## 🐛 **SOLUÇÃO DE PROBLEMAS**

### **❌ Erro: "YOLO não encontrado"**
```bash
# Instalar ultralytics
pip install ultralytics

# Verificar instalação
python3 -c "from ultralytics import YOLO; print('OK')"
```

### **❌ Erro: "OCR falhou"**
```bash
# Instalar EasyOCR
pip install easyocr

# Verificar idiomas
python3 -c "import easyocr; reader = easyocr.Reader(['pt']); print('OK')"
```

### **❌ Erro: "PostgreSQL não conecta"**
```bash
# Verificar status do container
docker ps | grep postgres

# Ver logs
docker logs mbst_postgres

# Reiniciar se necessário
docker-compose restart postgres
```

---

## 📚 **DOCUMENTAÇÃO ADICIONAL**

### **🔗 Links Úteis**
- **FastAPI**: https://fastapi.tiangolo.com/
- **YOLO**: https://docs.ultralytics.com/
- **EasyOCR**: https://github.com/JaidedAI/EasyOCR
- **PostgreSQL**: https://www.postgresql.org/docs/
- **Tailwind CSS**: https://tailwindcss.com/docs

### **📖 Tutoriais**
- **Fine-tuning YOLO**: `docs/fine_tuning_guide.md`
- **API REST**: `docs/api_guide.md`
- **Interface Web**: `docs/web_interface.md`
- **Banco de Dados**: `docs/database_guide.md`

---

## 🤝 **CONTRIBUIÇÃO**

### **🔧 Desenvolvimento**
1. **Fork** o projeto
2. **Crie branch** para sua feature
3. **Implemente** com testes
4. **Documente** suas mudanças
5. **Abra Pull Request**

### **🐛 Reportar Bugs**
- Use **GitHub Issues**
- Inclua **logs** e **screenshots**
- Descreva **passos para reproduzir**
- Especifique **ambiente** (OS, Python, etc.)

---

## 📄 **LICENÇA**

Este projeto está sob a licença **MIT**. Veja o arquivo `LICENSE` para detalhes.

---

## 🙏 **AGRADECIMENTOS**

- **DENATRAN** - Manual Brasileiro de Sinalização de Trânsito
- **OpenCV** - Visão computacional
- **YOLO** - Detecção de objetos
- **EasyOCR** - Reconhecimento de texto
- **FastAPI** - Framework da API
- **PostgreSQL** - Banco de dados
- **Tailwind CSS** - Interface moderna

---

## 🎉 **STATUS DO PROJETO**

- ✅ **Interface Web** - Moderna e responsiva
- ✅ **Sistema YOLO** - Detecção avançada
- ✅ **OCR Integrado** - Leitura de texto
- ✅ **Fine-tuning** - Pipeline completo
- ✅ **API REST** - Documentada com Swagger
- ✅ **Banco PostgreSQL** - 68 placas oficiais
- ✅ **Sistema de Feedback** - Correções e sugestões
- ✅ **Monitoramento** - Métricas e health checks
- ✅ **Documentação** - Guias completos

**🚀 O projeto está em PRODUÇÃO e pronto para uso empresarial!**

---

## 💡 **PRÓXIMOS PASSOS RECOMENDADOS**

1. **Coletar mais imagens** para melhorar dataset
2. **Implementar validação cruzada** no fine-tuning
3. **Adicionar suporte a GPU** para melhor performance
4. **Implementar cache Redis** para consultas frequentes
5. **Criar dashboard** de métricas em tempo real
6. **Integrar com sistemas** de trânsito existentes

---

*Última atualização: 29 de Agosto de 2025*

**🎯 Sistema MBST - Visão Computacional de PONTA para o Brasil!**
