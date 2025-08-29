# 📦 **GESTÃO DE DEPENDÊNCIAS - ARQUITETURA REFATORADA**

## 🎯 **VISÃO GERAL**

Este projeto utiliza um sistema de gerenciamento de dependências organizado por **fases de desenvolvimento** e **ambientes de uso**. Cada arquivo de requirements atende a necessidades específicas.

## 📁 **ARQUIVOS DE REQUIREMENTS**

### **1. `requirements.txt` - COMPLETO** ⭐
**Arquivo principal** com todas as dependências necessárias para o projeto completo.

**Inclui:**
- ✅ **Core**: Arquitetura principal de visão computacional
- ✅ **Fase 1**: Testes e qualidade de código
- ✅ **Fase 2**: Dashboard e monitoramento
- ✅ **Desenvolvimento**: Ferramentas de desenvolvimento
- ✅ **Produção**: Dependências de produção

**Uso:**
```bash
# Instalação completa
pip install -r requirements.txt
```

### **2. `requirements-minimal.txt` - MÍNIMO** 🚀
**Dependências essenciais** para funcionamento básico.

**Inclui:**
- ✅ **Core**: Framework web e visão computacional
- ✅ **Essencial**: OCR, ML e processamento básico
- ❌ **Sem**: Testes, desenvolvimento, monitoramento avançado

**Uso:**
```bash
# Instalação mínima para uso básico
pip install -r requirements-minimal.txt
```

### **3. `requirements-dev.txt` - DESENVOLVIMENTO** 🛠️
**Dependências completas** + ferramentas de desenvolvimento.

**Inclui:**
- ✅ **Tudo do requirements.txt**
- ✅ **Ferramentas de desenvolvimento**: pre-commit, ipython, jupyter
- ✅ **Debugging**: debugpy, memory-profiler, line-profiler
- ✅ **Documentação**: mkdocs, sphinx
- ✅ **Linting adicional**: isort, autopep8, pylint
- ✅ **Testes avançados**: pytest-randomly, pytest-repeat, pytest-timeout

**Uso:**
```bash
# Instalação para desenvolvimento completo
pip install -r requirements-dev.txt
```

### **4. `requirements-prod.txt` - PRODUÇÃO** 🚀
**Dependências otimizadas** para ambiente de produção.

**Inclui:**
- ✅ **Core e Fase 2**: Funcionalidades principais
- ❌ **Sem**: Ferramentas de desenvolvimento e testes
- ✅ **Performance**: gunicorn, uvloop
- ✅ **Monitoramento**: prometheus, structlog
- ✅ **Cache**: redis, memcached
- ✅ **Segurança**: cryptography, passlib

**Uso:**
```bash
# Instalação para produção
pip install -r requirements-prod.txt
```

## 🔧 **INSTALAÇÃO POR AMBIENTE**

### **🖥️ Desenvolvimento Local**
```bash
# Opção 1: Desenvolvimento completo
pip install -r requirements-dev.txt

# Opção 2: Funcionalidades básicas
pip install -r requirements.txt

# Opção 3: Mínimo para testes
pip install -r requirements-minimal.txt
```

### **🧪 Ambiente de Testes**
```bash
# Instalar dependências de teste
pip install -r requirements.txt

# Executar testes
python -m pytest tests/
```

### **🚀 Ambiente de Produção**
```bash
# Instalar dependências de produção
pip install -r requirements-prod.txt

# Ou usar requirements.txt (inclui tudo)
pip install -r requirements.txt
```

### **🐳 Docker/Container**
```dockerfile
# Dockerfile exemplo
FROM python:3.9-slim

# Copiar requirements
COPY requirements-prod.txt .

# Instalar dependências
RUN pip install -r requirements-prod.txt

# Copiar código
COPY . .
```

## 📊 **COMPARAÇÃO DE DEPENDÊNCIAS**

| Categoria | Minimal | Complete | Dev | Prod |
|-----------|---------|----------|-----|------|
| **Core** | ✅ | ✅ | ✅ | ✅ |
| **Fase 1 (Testes)** | ❌ | ✅ | ✅ | ❌ |
| **Fase 2 (Dashboard)** | ❌ | ✅ | ✅ | ✅ |
| **Desenvolvimento** | ❌ | ✅ | ✅ | ❌ |
| **Produção** | ❌ | ✅ | ✅ | ✅ |
| **Tamanho** | ~50MB | ~200MB | ~300MB | ~150MB |

## 🚨 **NOTAS IMPORTANTES**

### **⚠️ Compatibilidade de Versões**
- **Python**: 3.8+ (recomendado 3.9+)
- **PyTorch**: 2.0+ (verificar compatibilidade CUDA)
- **OpenCV**: 4.8+ (verificar compatibilidade de sistema)

### **🔒 Segurança**
- **Bandit**: Verificação automática de segurança
- **Safety**: Verificação de vulnerabilidades conhecidas
- **Dependências**: Atualizadas regularmente

### **📈 Performance**
- **Minimal**: Inicialização mais rápida
- **Complete**: Funcionalidades completas
- **Dev**: Ferramentas de otimização
- **Prod**: Otimizado para produção

## 🛠️ **MANUTENÇÃO**

### **Atualizar Dependências**
```bash
# Verificar dependências desatualizadas
pip list --outdated

# Atualizar dependências específicas
pip install --upgrade package_name

# Gerar novo requirements.txt
pip freeze > requirements-new.txt
```

### **Verificar Conflitos**
```bash
# Verificar dependências conflitantes
pip check

# Resolver conflitos
pip install --upgrade --force-reinstall package_name
```

### **Limpeza**
```bash
# Remover pacotes não utilizados
pip uninstall -y package_name

# Limpar cache
pip cache purge
```

## 📚 **RECOMENDAÇÕES**

### **🆕 Novos Desenvolvedores**
```bash
# Começar com desenvolvimento completo
pip install -r requirements-dev.txt
```

### **🧪 Testes e CI/CD**
```bash
# Usar requirements.txt (inclui testes)
pip install -r requirements.txt
```

### **🚀 Deploy em Produção**
```bash
# Usar requirements-prod.txt (otimizado)
pip install -r requirements-prod.txt
```

### **🔍 Investigação e Debug**
```bash
# Usar requirements-dev.txt (ferramentas de debug)
pip install -r requirements-dev.txt
```

---

**📦 Sistema de requirements organizado e flexível para diferentes necessidades de desenvolvimento e produção! 📦**