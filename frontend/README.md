# Frontend React - Sistema de Visão Computacional

## 🚀 Visão Geral

Frontend moderno desenvolvido em React com TypeScript para o Sistema de Reconhecimento de Placas. Interface intuitiva e responsiva para upload de arquivos, análise de imagens e visualização de resultados.

## 🛠️ Tecnologias

- **React 18** - Biblioteca principal
- **TypeScript** - Tipagem estática
- **Material-UI (MUI)** - Componentes de interface
- **React Router** - Roteamento
- **Axios** - Cliente HTTP
- **React Dropzone** - Upload de arquivos
- **Docker** - Containerização

## 📁 Estrutura do Projeto

```
frontend/
├── public/                 # Arquivos estáticos
├── src/
│   ├── components/         # Componentes reutilizáveis
│   │   ├── FileUpload.tsx  # Upload de arquivos
│   │   ├── ResultsDisplay.tsx # Exibição de resultados
│   │   ├── Layout.tsx      # Layout principal
│   │   └── AppRouter.tsx   # Roteamento
│   ├── pages/              # Páginas da aplicação
│   │   ├── LoginPage.tsx   # Página de login
│   │   └── AnalysisPage.tsx # Página principal
│   ├── services/           # Serviços de API
│   │   └── api.ts          # Cliente da API
│   ├── contexts/           # Contextos React
│   │   └── AuthContext.tsx # Contexto de autenticação
│   ├── types/              # Tipos TypeScript
│   │   └── api.ts          # Tipos da API
│   ├── config/             # Configurações
│   │   └── environment.ts  # Configurações de ambiente
│   └── App.tsx             # Componente principal
├── nginx.conf              # Configuração Nginx
├── package.json            # Dependências
└── README.md               # Este arquivo
```

## 🚀 Como Executar

### Desenvolvimento Local

```bash
# Instalar dependências
npm install

# Executar em modo desenvolvimento
npm start

# Build para produção
npm run build

# Executar testes
npm test
```

### Docker

```bash
# Build da imagem
docker build -f Dockerfile.frontend -t vision-frontend .

# Executar container
docker run -p 3000:3000 vision-frontend
```

### Docker Compose

```bash
# Executar com todos os serviços
docker-compose up vision-frontend

# Executar em background
docker-compose up -d vision-frontend
```

## 🔧 Configurações

### Variáveis de Ambiente

```bash
# URL da API
REACT_APP_API_URL=http://localhost:8000

# Ambiente
REACT_APP_ENVIRONMENT=development

# Versão
REACT_APP_VERSION=2.0.0

# Timeout da API
REACT_APP_API_TIMEOUT=30000

# Tamanho máximo de arquivo (bytes)
REACT_APP_MAX_FILE_SIZE=10485760

# Tipos de arquivo permitidos
REACT_APP_ALLOWED_IMAGE_TYPES=image/jpeg,image/png,image/bmp,image/gif
REACT_APP_ALLOWED_VIDEO_TYPES=video/mp4,video/avi,video/mov,video/mpeg

# Limiar de confiança
REACT_APP_DEFAULT_CONFIDENCE_THRESHOLD=0.5
```

## 🎨 Funcionalidades

### ✅ Implementadas

- **Autenticação JWT** - Login seguro com tokens
- **Upload de Arquivos** - Drag & drop com validação
- **Análise de Imagens** - Integração com API de visão computacional
- **Visualização de Resultados** - Interface rica para resultados
- **Design Responsivo** - Funciona em desktop e mobile
- **Tema Personalizado** - Material-UI customizado
- **Roteamento** - Navegação entre páginas
- **Tratamento de Erros** - Feedback visual para erros
- **Loading States** - Indicadores de carregamento

### 🔄 Tipos de Análise

1. **Placas de Sinalização** - Detecta sinais de trânsito
2. **Placas de Veículos** - Identifica placas Mercosul e convencionais
3. **Detecção Geral** - Análise geral de objetos

## 🔗 Integração com API

O frontend se integra completamente com a API existente:

- **Endpoints de Autenticação** - Login e perfil
- **Endpoints de Detecção** - Análise de imagens
- **Endpoints de Monitoramento** - Status do sistema
- **Proxy Nginx** - Evita problemas de CORS

## 🐳 Docker

### Dockerfile

```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/build /usr/share/nginx/html
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
```

### Nginx

- **SPA Support** - Suporte a Single Page Application
- **Proxy API** - Redirecionamento para API backend
- **Compressão** - Gzip para otimização
- **Cache** - Cache de assets estáticos
- **CORS** - Configuração de CORS
- **CSP** - Content Security Policy

## 📱 Responsividade

- **Desktop** - Layout completo com sidebar
- **Tablet** - Layout adaptado
- **Mobile** - Interface otimizada para touch

## 🔒 Segurança

- **JWT Authentication** - Tokens seguros
- **CSP Headers** - Content Security Policy
- **CORS Configuration** - Cross-Origin Resource Sharing
- **Input Validation** - Validação de entrada
- **File Type Validation** - Validação de tipos de arquivo

## 🧪 Testes

```bash
# Executar testes
npm test

# Executar testes com coverage
npm run test:coverage

# Executar testes em modo watch
npm run test:watch
```

## 📦 Build e Deploy

```bash
# Build para produção
npm run build

# Analisar bundle
npm run analyze

# Deploy para produção
docker-compose -f docker-compose.prod.yml up -d vision-frontend
```

## 🐛 Troubleshooting

### Problemas Comuns

1. **CORS Errors** - Verificar configuração do proxy Nginx
2. **API Connection** - Verificar URL da API
3. **File Upload** - Verificar tamanho e tipo do arquivo
4. **Authentication** - Verificar token JWT

### Logs

```bash
# Logs do container
docker logs vision-frontend-dev

# Logs do Nginx
docker exec vision-frontend-dev cat /var/log/nginx/frontend_error.log
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 📞 Suporte

Para suporte, entre em contato com a equipe de desenvolvimento ou abra uma issue no repositório.