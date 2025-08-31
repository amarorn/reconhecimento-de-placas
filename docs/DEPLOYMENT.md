# 🚀 **Guia de Deploy da Documentação**

## 📋 **Visão Geral**

Este guia explica como publicar a documentação do projeto em diferentes plataformas, com foco na solução recomendada: **GitHub Pages + CI/CD automático**.

## 🌐 **Opções de Publicação**

### **1. 🚀 GitHub Pages (RECOMENDADO)**

**Vantagens:**
- ✅ **Gratuito** e integrado ao GitHub
- ✅ **Atualização automática** via GitHub Actions
- ✅ **Suporte nativo** a Markdown e Jekyll
- ✅ **Domínio personalizado** possível
- ✅ **Busca integrada** e SEO otimizado

**URL da documentação:**
```
https://amarorn.github.io/reconhecimento-de-placas/
```

### **2. 📚 Read the Docs**

**Vantagens:**
- ✅ **Especializado** em documentação técnica
- ✅ **Suporte a versões** múltiplas
- ✅ **Busca avançada** e indexação
- ✅ **Integração** com GitHub
- ✅ **Gratuito** para projetos open source

**URL da documentação:**
```
https://reconhecimento-de-placas.readthedocs.io/
```

### **3. 🔧 Vercel**

**Vantagens:**
- ✅ **Deploy automático** e preview de PRs
- ✅ **Domínio personalizado** gratuito
- ✅ **Integração** com GitHub
- ✅ **Performance** otimizada
- ✅ **Gratuito** para projetos pessoais

### **4. 📖 Netlify**

**Vantagens:**
- ✅ **Deploy automático** e contínuo
- ✅ **Formulários** integrados
- ✅ **Analytics** gratuitos
- ✅ **Domínio personalizado**
- ✅ **Gratuito** para projetos open source

## 🚀 **Implementação: GitHub Pages + CI/CD**

### **Configuração Automática**

A documentação já está configurada para deploy automático via GitHub Actions. O workflow está em `.github/workflows/docs.yml`.

**O que acontece automaticamente:**
1. **Push para main/develop** → Deploy automático
2. **Validação** da estrutura da documentação
3. **Geração** da documentação da API
4. **Validação** de links internos
5. **Deploy** para GitHub Pages

### **Configuração Manual (se necessário)**

#### **1. Ativar GitHub Pages**
```bash
# No repositório GitHub:
# Settings → Pages → Source: Deploy from a branch
# Branch: gh-pages
# Folder: / (root)
```

#### **2. Configurar domínio personalizado (opcional)**
```bash
echo "docs.seudominio.com" > docs/CNAME
```

#### **3. Configurar HTTPS (automático)**
O GitHub Pages ativa HTTPS automaticamente para domínios personalizados.

## 📊 **Monitoramento e Analytics**

### **GitHub Insights**
- **Traffic**: Visualizações e cliques
- **Referrers**: De onde vêm os visitantes
- **Popular content**: Páginas mais acessadas

### **Google Analytics (opcional)**
```html
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

## 🔧 **Personalização Avançada**

### **Tema Jekyll Personalizado**
```yaml
theme: jekyll-theme-cayman
remote_theme: pages-themes/cayman@v0.2.0
```

### **Layouts Customizados**
```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>{{ page.title }} - {{ site.title }}</title>
    <link rel="stylesheet" href="{{ '/assets/css/style.css' | relative_url }}">
</head>
<body>
    {{ content }}
</body>
</html>
```

### **CSS Personalizado**
```css
:root {
    --primary-color: #0366d6;
    --secondary-color: #586069;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
```

## 📱 **Responsividade e Mobile**

### **Viewport Meta Tag**
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

### **CSS Responsivo**
```css
@media (max-width: 768px) {
    .container {
        padding: 20px;
    }
    
    .nav {
        grid-template-columns: 1fr;
    }
}
```

## 🔍 **SEO e Busca**

### **Meta Tags**
```yaml
seo:
  title: "Reconhecimento de Placas - Documentação"
  description: "Documentação completa do sistema de visão computacional"
  keywords: ["visão computacional", "YOLO", "OCR", "placas", "detecção"]
  author: "Equipe de Desenvolvimento"
  og_image: "/assets/images/og-image.png"
```

### **Sitemap**
```yaml
plugins:
  - jekyll-sitemap

sitemap:
  exclude: ["/404.html", "/robots.txt"]
```

### **Robots.txt**
```txt
User-agent: *
Allow: /

Sitemap: https://amarorn.github.io/reconhecimento-de-placas/sitemap.xml
```

## 🚨 **Solução de Problemas**

### **Deploy não funciona**
```bash
# Verificar status do GitHub Actions
# Actions → Deploy Documentation → Ver logs

# Verificar branch gh-pages
git branch -a | grep gh-pages

# Verificar configurações do GitHub Pages
# Settings → Pages → Status
```

### **Links quebrados**
```bash
python scripts/validate_links.py
tree docs/
```

### **Tema não carrega**
```bash
# Verificar _config.yml
# Verificar dependências do Jekyll
# Verificar logs do GitHub Pages
```

## 📈 **Métricas de Sucesso**

### **KPIs Recomendados**
- **Page Views**: Visualizações mensais
- **Unique Visitors**: Visitantes únicos
- **Bounce Rate**: Taxa de rejeição
- **Time on Page**: Tempo na página
- **Search Queries**: Termos de busca

### **Ferramentas de Monitoramento**
- **GitHub Insights**: Métricas básicas
- **Google Analytics**: Analytics avançado
- **Hotjar**: Heatmaps e gravações
- **Search Console**: Performance de busca

## 🔄 **Atualizações e Manutenção**

### **Atualização Automática**
- **Push para main**: Deploy automático
- **Pull Requests**: Preview automático
- **Validação**: Links e estrutura verificados

### **Manutenção Manual**
```bash
# Atualizar metadados
# docs/_config.yml → last_updated

# Verificar links
# Executar validação local

# Testar localmente
# bundle exec jekyll serve
```

---

**🎯 Próximo passo**: [Configurar domínio personalizado](../custom-domain.md) ou [Implementar analytics avançado](../analytics.md)
