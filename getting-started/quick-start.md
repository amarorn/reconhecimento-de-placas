# 🚀 **Início Rápido - 5 Minutos**

## ⚡ **Pré-requisitos**

- **Docker** e **Docker Compose** instalados
- **Git** para clonar o repositório
- **5 minutos** do seu tempo

## 🔧 **Instalação em 5 Passos**

### **1. Clone o repositório**
```bash
git clone https://github.com/amarorn/reconhecimento-de-placas.git
cd reconhecimento-de-placas
```

### **2. Configure o ambiente**
```bash
cp .env.example .env
```

### **3. Execute com Docker**
```bash
docker-compose up -d
sleep 10
```

### **4. Verifique o status**
```bash
docker-compose ps
curl http://localhost:8000/health
```

### **5. Acesse a aplicação**
- 🌐 **API**: http://localhost:8000
- 📊 **Dashboard**: http://localhost:8080
- 📈 **Prometheus**: http://localhost:9090
- 📊 **Grafana**: http://localhost:3000

## 🧪 **Teste Rápido**

### **Verificar API**
```bash
curl http://localhost:8000/health
curl http://localhost:8000/info
```

### **Verificar Dashboard**
```bash
curl http://localhost:8080/health
```

## 🚀 **Próximos Passos**

Agora que o sistema está rodando, você pode:

1. **📖 Ler a [Documentação da API](../api-reference/endpoints.md)**
2. **📊 Explorar o [Dashboard](../user-guides/dashboard-guide.md)**
3. **🔧 Configurar [Autenticação](../api-reference/authentication.md)**
4. **🧪 Executar [Testes](../developer-guides/testing.md)**

## 🔍 **Solução de Problemas Rápidos**

### **Container não inicia**
```bash
docker-compose logs vision-api
docker-compose restart
```

### **Porta já em uso**
```bash
lsof -i :8000
lsof -i :8080
docker-compose down
```

### **Problemas de permissão**
```bash
chmod +x scripts/*.sh
docker-compose up -d
```

## 📋 **Comandos Úteis**

```bash
docker-compose up -d
docker-compose down
docker-compose restart
docker-compose logs -f
docker-compose down -v
docker system prune
```

## 🎯 **O que foi configurado**

- ✅ **API de Visão**: FastAPI rodando na porta 8000
- ✅ **Dashboard**: Interface web na porta 8080
- ✅ **Banco de Dados**: PostgreSQL para persistência
- ✅ **Cache**: Redis para performance
- ✅ **Monitoramento**: Prometheus + Grafana
- ✅ **Logs**: Sistema centralizado de logs

---

**🎉 Parabéns! Seu sistema de reconhecimento de placas está rodando! 🎉**

**Próximo passo**: [Guia de Instalação Detalhada](installation.md) ou [Uso da API](../user-guides/api-usage.md)
