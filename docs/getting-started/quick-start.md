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
# Copie o arquivo de exemplo
cp .env.example .env

# Edite as configurações (opcional para teste)
# nano .env
```

### **3. Execute com Docker**
```bash
# Inicie todos os serviços
docker-compose up -d

# Aguarde alguns segundos para inicialização
sleep 10
```

### **4. Verifique o status**
```bash
# Verifique se todos os containers estão rodando
docker-compose ps

# Teste a API
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
# Health check
curl http://localhost:8000/health

# Informações da API
curl http://localhost:8000/info

# Documentação Swagger
# Abra: http://localhost:8000/docs
```

### **Verificar Dashboard**
```bash
# Status do dashboard
curl http://localhost:8080/health

# Abra no navegador: http://localhost:8080
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
# Ver logs
docker-compose logs vision-api

# Reiniciar
docker-compose restart
```

### **Porta já em uso**
```bash
# Verificar portas
lsof -i :8000
lsof -i :8080

# Parar serviços
docker-compose down
```

### **Problemas de permissão**
```bash
# Dar permissão aos scripts
chmod +x scripts/*.sh

# Executar como usuário atual
docker-compose up -d
```

## 📋 **Comandos Úteis**

```bash
# Gerenciar serviços
docker-compose up -d          # Iniciar
docker-compose down           # Parar
docker-compose restart        # Reiniciar
docker-compose logs -f        # Ver logs em tempo real

# Limpar recursos
docker-compose down -v        # Parar e remover volumes
docker system prune           # Limpar recursos não utilizados
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
