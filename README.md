# 🚀 **ARQUITETURA DE VISÃO COMPUTACIONAL - REFATORADA**

## 📋 **VISÃO GERAL**

Este projeto implementa uma **arquitetura moderna e escalável** para reconhecimento de placas de sinalização de trânsito e veículos usando **OCR**, **YOLO** e **fine-tuning**. A arquitetura foi completamente refatorada seguindo as melhores práticas de engenharia de software.

## 🎯 **FASES IMPLEMENTADAS**

### ✅ **FASE 1: QUALIDADE E AUTOMAÇÃO**

- **Testes unitários e de integração** com pytest
- **CI/CD pipeline** com GitHub Actions
- **Ferramentas de qualidade** (Black, Flake8, MyPy)
- **Documentação automática** da API
- **Cobertura de código** e relatórios

### ✅ **FASE 2: DASHBOARD E MONITORAMENTO**

- **Dashboard web em tempo real** com FastAPI
- **Sistema de métricas** avançado
- **Alertas automáticos** configuráveis
- **Monitoramento de pipeline** de visão
- **WebSockets** para atualizações em tempo real

### ✅ **FASE 3: API REST E INTEGRAÇÃO**

- **API REST completa** com FastAPI
- **Autenticação JWT** com refresh tokens
- **Documentação Swagger/OpenAPI** automática
- **Validação de dados** com Pydantic
- **Integração** com sistemas externos

### ✅ **FASE 4: DEPLOY E INFRAESTRUTURA**

- **Containerização Docker** otimizada
- **Orquestração** com Docker Compose
- **Monitoramento** com Prometheus/Grafana
- **Logs centralizados** com ELK Stack
- **CI/CD pipeline** completo
- **Scripts de deploy** automatizados

## 🏗️ **ARQUITETURA**

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND / CLIENTES                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    NGINX (PROXY REVERSO)                    │
│              Rate Limiting + Security Headers               │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    VISION API (FASTAPI)                     │
│              Autenticação + Validação + Roteamento          │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    VISION PIPELINE                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │Preprocessor │ │YOLO Detector│ │Text Extractor│          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    INFRAESTRUTURA                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ PostgreSQL │ │    Redis    │ │   Storage   │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    MONITORAMENTO                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Prometheus  │ │   Grafana   │ │  ELK Stack  │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 **INÍCIO RÁPIDO**

### **1. Pré-requisitos**

```bash
# Docker e Docker Compose
docker --version
docker-compose --version

# Python 3.9+
python --version

# Git
git --version
```

### **2. Clone e Setup**

```bash
# Clone o repositório
git clone https://github.com/amarorn/reconhecimento-de-placas.git
cd reconhecimento-de-placas

# Mude para a branch refatorada
git checkout refactor-vision-architecture

# Configure variáveis de ambiente
cp .env.dev .env
```

### **3. Deploy Automatizado**

```bash
# Torne o script executável
chmod +x scripts/deploy.sh

# Deploy para desenvolvimento
./scripts/deploy.sh

# Deploy para produção
./scripts/deploy.sh prod
```

### **4. Acessar Serviços**

```
🌐 API: http://localhost:8000
📊 Dashboard: http://localhost:8080
📈 Prometheus: http://localhost:9090
📊 Grafana: http://localhost:3000 (admin/admin)
📝 Kibana: http://localhost:5601
🔍 Elasticsearch: http://localhost:9200
🗄️ PostgreSQL: localhost:5432
🚀 Redis: localhost:6379
```

## 🔧 **CONFIGURAÇÃO**

### **Variáveis de Ambiente**

#### **Desenvolvimento (`.env.dev`)**

```bash
ENVIRONMENT=development
API_RELOAD=true
SECRET_KEY=dev-secret-key-change-in-production
POSTGRES_DB=vision_dev_db
REDIS_PASSWORD=dev-redis-password
GRAFANA_ADMIN_PASSWORD=admin
DEBUG=true
```

#### **Produção (`.env.prod`)**

```bash
ENVIRONMENT=production
API_RELOAD=false
SECRET_KEY=CHANGE_THIS_TO_A_VERY_SECURE_SECRET_KEY
POSTGRES_DB=vision_prod_db
REDIS_PASSWORD=CHANGE_THIS_TO_A_VERY_SECURE_REDIS_PASSWORD
GRAFANA_ADMIN_PASSWORD=CHANGE_THIS_TO_A_VERY_SECURE_GRAFANA_PASSWORD
DEBUG=false
ENABLE_HTTPS=true
```

### **Comandos Úteis**

```bash
# Gerenciar serviços
./scripts/deploy.sh          # Deploy desenvolvimento
./scripts/deploy.sh prod     # Deploy produção
./scripts/deploy.sh stop     # Parar serviços
./scripts/deploy.sh restart  # Reiniciar serviços
./scripts/deploy.sh logs     # Ver logs
./scripts/deploy.sh help     # Ajuda

# Docker Compose
docker-compose up -d         # Desenvolvimento
docker-compose -f docker-compose.prod.yml up -d  # Produção
docker-compose logs -f       # Ver logs
docker-compose down          # Parar serviços
```

## 📚 **DOCUMENTAÇÃO**

### **Fases Implementadas**

- [📖 **Fase 1**](docs/FASE1_IMPLEMENTADA.md) - Qualidade e Automação
- [📖 **Fase 2**](docs/FASE2_DASHBOARD_MONITORAMENTO.md) - Dashboard e Monitoramento
- [📖 **Fase 3**](docs/FASE3_API_REST_INTEGRACAO.md) - API REST e Integração
- [📖 **Fase 4**](docs/FASE4_DEPLOY_INFRAESTRUTURA.md) - Deploy e Infraestrutura

### **Referências da API**

- [📖 **API Reference**](docs/API_REFERENCE.md) - Documentação completa da API
- [📖 **Requirements**](README_REQUIREMENTS.md) - Gestão de dependências

### **Exemplos de Uso**

- [🧪 **API Example**](examples/api_example.py) - Cliente completo da API
- [🧪 **Dashboard Example**](examples/dashboard_example.py) - Uso do dashboard
- [🧪 **Vision Example**](examples/refactored_vision_example.py) - Pipeline de visão

## 🧪 **TESTES**

### **Executar Testes**

```bash
# Instalar dependências de teste
pip install -r requirements-dev.txt

# Executar todos os testes
python -m pytest tests/ -v

# Executar com cobertura
python -m pytest tests/ -v --cov=vision --cov-report=html

# Executar testes específicos
python -m pytest tests/test_api.py -v
python -m pytest tests/test_vision.py -v
```

### **Qualidade de Código**

```bash
# Formatação
black vision/

# Linting
flake8 vision/

# Type checking
mypy vision/

# Segurança
bandit -r vision/
safety check
```

## 📊 **MONITORAMENTO**

### **Métricas Disponíveis**

- **Sistema**: CPU, memória, disco, rede
- **Aplicação**: requisições, tempo de resposta, erros
- **Pipeline**: detecções, OCR, performance
- **Infraestrutura**: containers, serviços, conectividade

### **Alertas Configuráveis**

- **Performance**: tempo de resposta alto, uso de recursos
- **Disponibilidade**: serviços down, health checks falhando
- **Segurança**: tentativas de login, rate limiting
- **Negócio**: volume de processamento, qualidade dos resultados

## 🔒 **SEGURANÇA**

### **Configurações Implementadas**

- **Usuários não-root** nos containers
- **Secrets** gerenciados via variáveis de ambiente
- **Rate limiting** configurável
- **Headers de segurança** (HSTS, X-Frame-Options, etc.)
- **CORS** restrito para domínios específicos
- **HTTPS** obrigatório em produção
- **Autenticação JWT** com refresh tokens

### **Usuários Padrão**

```
👑 Admin: admin/admin123 (acesso completo)
🧪 Test: test/test123 (leitura e escrita)
📊 Monitor: monitor/monitor123 (leitura e monitoramento)
```

## 🚀 **DEPLOY EM PRODUÇÃO**

### **1. Preparação**

```bash
# Configurar variáveis de ambiente
cp .env.prod .env
# Editar .env com valores reais e seguros

# Configurar secrets
export SECRET_KEY="sua-chave-secreta-muito-segura"
export POSTGRES_PASSWORD="sua-senha-postgres-muito-segura"
export REDIS_PASSWORD="sua-senha-redis-muito-segura"
```

### **2. Deploy**

```bash
# Deploy completo
./scripts/deploy.sh prod

# Verificar status
./scripts/deploy.sh status

# Ver logs
./scripts/deploy.sh logs
```

### **3. Verificação**

```bash
# Health checks
curl https://seu-dominio.com/health

# Métricas
curl https://seu-dominio.com/metrics

# Logs
docker-compose -f docker-compose.prod.yml logs -f
```

## 🔍 **TROUBLESHOOTING**

### **Problemas Comuns**

1. **Container não inicia**

   ```bash
   docker-compose logs vision-api
   docker stats
   docker-compose config
   ```
2. **Serviços não se comunicam**

   ```bash
   docker network ls
   docker network inspect vision-network
   docker exec vision-api ping postgres
   ```
3. **Performance lenta**

   ```bash
   docker stats
   curl http://localhost:9090/api/v1/query?query=up
   docker-compose logs -f
   ```

### **Logs e Debugging**

```bash
# Logs em tempo real
docker-compose logs -f --tail=100

# Logs de um serviço específico
docker-compose logs -f vision-api

# Logs de produção
docker-compose -f docker-compose.prod.yml logs -f
```

## 📈 **ROADMAP FUTURO**

### **Fase 5: Otimizações Avançadas**

- [ ] Kubernetes para orquestração em escala
- [ ] Service mesh (Istio) para comunicação entre serviços
- [ ] Auto-scaling baseado em métricas
- [ ] Multi-region deployment
- [ ] Disaster recovery automatizado

### **Fase 6: Inteligência Operacional**

- [ ] Machine Learning para detecção de anomalias
- [ ] Predictive maintenance
- [ ] Auto-healing de serviços
- [ ] Otimização automática de recursos
- [ ] ChatOps para operações

## 🤝 **CONTRIBUIÇÃO**

### **Como Contribuir**

1. **Fork** o repositório
2. **Crie** uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. **Commit** suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. **Push** para a branch (`git push origin feature/nova-funcionalidade`)
5. **Abra** um Pull Request

### **Padrões de Código**

- **Python**: PEP 8, type hints, docstrings
- **Testes**: pytest, cobertura mínima de 80%
- **Qualidade**: Black, Flake8, MyPy
- **Commits**: Conventional Commits
- **Documentação**: Markdown, docstrings

## 📄 **LICENÇA**

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 **EQUIPE**

- **Desenvolvimento**: Equipe de Desenvolvimento
- **Arquitetura**: Refatoração completa com melhores práticas
- **Infraestrutura**: Containerização e orquestração
- **Monitoramento**: Observabilidade completa

## 📞 **SUPORTE**

### **Canais de Ajuda**

- **Issues**: [GitHub Issues](https://github.com/amarorn/reconhecimento-de-placas/issues)
- **Documentação**: [docs/](docs/) - Documentação completa
- **Exemplos**: [examples/](examples/) - Exemplos de uso
- **Scripts**: [scripts/](scripts/) - Scripts de deploy e gerenciamento

### **Informações do Sistema**

```bash
# Ver informações da API
curl http://localhost:8000/info

# Ver informações do dashboard
curl http://localhost:8080/info

# Ver status dos serviços
./scripts/deploy.sh status
```

---

## 🎉 **STATUS DO PROJETO**

### **✅ Fases Completas (100%)**

- **Fase 1**: Qualidade e Automação ✅
- **Fase 2**: Dashboard e Monitoramento ✅
- **Fase 3**: API REST e Integração ✅
- **Fase 4**: Deploy e Infraestrutura ✅

### **🚀 Sistema Pronto para Produção**

- **Arquitetura moderna** e escalável
- **Testes abrangentes** e automatizados
- **Monitoramento completo** e alertas
- **Deploy automatizado** e seguro
- **Documentação completa** e atualizada

---

**🎯 O projeto está 100% implementado e pronto para uso em produção! 🎯**


docker-compose -f docker-compose.prod.yml config --services



lasticsearch

kibana

redis

postgres

vision-api

nginx

prometheus

grafana

logstash

backup
