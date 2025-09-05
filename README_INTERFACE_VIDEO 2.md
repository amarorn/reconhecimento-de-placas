# 🎬 Interface de Vídeo - PotholeDetector

## 📋 Visão Geral

A interface foi atualizada para suportar **análise de vídeo** usando o PotholeDetector. Agora você pode:

- 📤 **Fazer upload de vídeos** (MP4, AVI, MOV, MPEG)
- 🎯 **Processar vídeos completos** com detecção de buracos
- 🎬 **Visualizar resultados** com análise temporal
- 📊 **Gerar relatórios** de condição da estrada
- 🎯 **Acompanhar tracking** de buracos ao longo do tempo

## 🚀 Como Usar

### 1. **Abrir a Interface**

```bash
# Abrir no navegador
open vision_interface.html
# ou
firefox vision_interface.html
# ou
google-chrome vision_interface.html
```

### 2. **Fazer Login**

- **Usuário**: `admin`
- **Senha**: `admin123`
- Clique em "Fazer Login"

### 3. **Selecionar Tipo de Arquivo**

- Clique no botão **"🎬 Vídeo"** para análise de vídeo
- Ou **"📷 Imagem"** para análise de imagem (funcionalidade original)

### 4. **Fazer Upload do Vídeo**

- **Clique** na área de upload ou **arraste** o arquivo
- Formatos suportados: MP4, AVI, MOV, MPEG
- Tamanho máximo: 500MB
- O vídeo será exibido com controles de reprodução

### 5. **Processar o Vídeo**

- Clique em **"🔍 Processar Arquivo"**
- A interface mostrará progresso em tempo real
- O processamento pode levar alguns minutos dependendo do tamanho do vídeo

### 6. **Visualizar Resultados**

Após o processamento, você verá:

#### 🎬 **Análise de Vídeo**
- **Informações do vídeo**: FPS, total de frames, duração
- **Resumo de detecções**: Total de buracos, frames com detecções
- **Análise de qualidade**: Qualidade média dos frames
- **Condição da estrada**: Avaliação geral da estrada
- **Prioridade de manutenção**: Recomendações de manutenção

#### 🎯 **Tracking Temporal**
- **Total de tracks**: Número de buracos rastreados
- **Tracks estáveis**: Buracos detectados consistentemente
- **Análise de estabilidade**: Qualidade do tracking

#### 💡 **Recomendações**
- Sugestões baseadas na análise do vídeo
- Prioridades de manutenção
- Condições críticas identificadas

## 🔧 Funcionalidades Técnicas

### **Processamento de Vídeo**

```python
# O PotholeDetector processa:
# 1. Frame por frame (configurável)
# 2. Detecção de buracos em cada frame
# 3. Tracking temporal entre frames
# 4. Análise de qualidade dos frames
# 5. Geração de relatório completo
```

### **Sistema de Tracking**

- **Identificação de buracos** em frames consecutivos
- **Cálculo de sobreposição** entre detecções
- **Filtro de estabilidade** para remover detecções falsas
- **Histórico temporal** de cada buraco detectado

### **Análise de Qualidade**

- **Variância da imagem** (detalhes)
- **Gradiente** (bordas e contornos)
- **Score de qualidade** normalizado (0.0 a 1.0)
- **Distribuição** por níveis de qualidade

## 📊 Resultados Gerados

### **Arquivos de Saída**

1. **Vídeo Anotado**: `annotated_video_{ID}_{timestamp}.mp4`
   - Frames com detecções desenhadas
   - Informações de tracking em tempo real
   - Estatísticas por frame

2. **Relatório JSON**: `analysis_report_{ID}_{timestamp}.json`
   - Análise completa do vídeo
   - Estatísticas de detecção
   - Dados de tracking
   - Recomendações

### **Estrutura do Relatório**

```json
{
  "video_info": {
    "fps": 30.0,
    "total_frames": 900,
    "duration": 30.0,
    "processed_frames": 900
  },
  "detection_summary": {
    "total_detections": 45,
    "frames_with_detections": 67,
    "detection_rate": 0.074
  },
  "quality_analysis": {
    "average_frame_quality": 0.723,
    "quality_distribution": {...}
  },
  "road_condition_analysis": {
    "condition_distribution": {...},
    "overall_condition": "fair"
  },
  "maintenance_analysis": {
    "priority_distribution": {...},
    "overall_priority": "medium"
  },
  "tracking_analysis": {
    "total_tracks": 12,
    "stable_tracks": 8,
    "track_details": [...]
  },
  "recommendations": [...]
}
```

## ⚙️ Configuração

### **Parâmetros de Vídeo**

```yaml
pothole_detector:
  video_analysis:
    frame_skip: 1                    # Processar todos os frames
    min_track_length: 3              # Mínimo de frames para track estável
    tracking_threshold: 0.7          # Threshold de sobreposição (0.0 a 1.0)
    max_tracks: 50                   # Máximo de tracks simultâneos
    enable_frame_quality_assessment: true
    enable_temporal_analysis: true
    enable_stability_scoring: true
    output_annotated_video: true     # Gerar vídeo com detecções
    save_frame_analyses: true        # Salvar análises de cada frame
    generate_tracking_report: true   # Gerar relatório de tracking
```

### **Ajustes de Performance**

- **`frame_skip`**: Aumentar para processar menos frames (mais rápido)
- **`min_track_length`**: Aumentar para tracks mais estáveis
- **`tracking_threshold`**: Ajustar sensibilidade do tracking
- **`max_tracks`**: Limitar número de tracks simultâneos

## 🔌 API REST

### **Endpoint de Vídeo**

```http
POST /vision/process_video
Authorization: Bearer {token}
Content-Type: multipart/form-data

Body:
- video_file: arquivo de vídeo
```

### **Resposta da API**

```json
{
  "result": {
    "success": true,
    "video_id": "uuid",
    "processing_time": 45.2,
    "video_info": {...},
    "detection_summary": {...},
    "quality_analysis": {...},
    "road_condition_analysis": {...},
    "maintenance_analysis": {...},
    "tracking_analysis": {...},
    "recommendations": [...],
    "output_files": {
      "annotated_video": "path/to/video.mp4",
      "analysis_report": "path/to/report.json"
    }
  },
  "timestamp": "2024-01-01T12:00:00",
  "api_version": "1.0.0"
}
```

## 🧪 Testes

### **Executar Testes**

```bash
# Teste completo da interface
python3 test_video_interface.py

# Teste específico dos detectores
python3 test_specialized_detectors.py

# Exemplo de análise de vídeo
python3 examples/video_pothole_analysis_example.py
```

### **Verificar Funcionamento**

1. **Interface HTML**: Todas as funcionalidades de vídeo presentes
2. **Endpoints API**: Endpoint `/vision/process_video` configurado
3. **Modelos**: `ImageRequest` e `ProcessResponse` definidos
4. **Servidor**: Endpoints de vídeo incluídos no servidor

## 🚨 Solução de Problemas

### **Erros Comuns**

#### **"Arquivo deve ser um vídeo"**
- Verifique se o arquivo é um formato de vídeo válido
- Formatos suportados: MP4, AVI, MOV, MPEG

#### **"Arquivo muito grande"**
- Limite atual: 500MB
- Comprima o vídeo ou reduza a resolução

#### **"Pipeline de visão não disponível"**
- Verifique se o arquivo de configuração existe
- Instale as dependências necessárias

#### **"Erro ao processar vídeo"**
- Verifique se o modelo YOLO está disponível
- Confirme se há espaço em disco suficiente

### **Dependências**

```bash
# Instalar dependências básicas
pip install ultralytics opencv-python pyyaml numpy

# Para processamento de vídeo completo
pip install fastapi uvicorn python-multipart
```

## 📈 Próximos Passos

### **Melhorias Planejadas**

1. **Progresso em Tempo Real**: WebSocket para atualizações de progresso
2. **Streaming de Vídeo**: Processamento de vídeos muito longos
3. **Múltiplos Formatos**: Suporte a mais codecs de vídeo
4. **Análise Comparativa**: Comparar vídeos de diferentes épocas
5. **Exportação Avançada**: Relatórios em PDF, Excel, etc.

### **Integrações**

1. **Sistema de Notificações**: Alertas para condições críticas
2. **Dashboard em Tempo Real**: Monitoramento contínuo
3. **API de Terceiros**: Integração com sistemas de manutenção
4. **Machine Learning**: Melhoria contínua dos modelos

## 📚 Recursos Adicionais

- [Documentação dos Detectores Especializados](README_DETECTORES_ESPECIALIZADOS.md)
- [Exemplo de Análise de Vídeo](examples/video_pothole_analysis_example.py)
- [Configuração dos Detectores](config/specialized_detectors.yaml)
- [Arquitetura Atualizada](ARQUITETURA_ATUALIZADA.md)

---

## 🎯 Resumo

A interface de vídeo implementa:

✅ **Upload de Vídeos** - Suporte a múltiplos formatos
✅ **Processamento Completo** - Análise frame por frame
✅ **Tracking Temporal** - Acompanhamento de buracos ao longo do tempo
✅ **Análise de Qualidade** - Avaliação da qualidade dos frames
✅ **Relatórios Completos** - Análise abrangente da estrada
✅ **API REST** - Endpoint dedicado para processamento de vídeo
✅ **Interface Web** - Interface amigável para usuários
✅ **Configurabilidade** - Parâmetros ajustáveis para diferentes cenários

**🎬 Comece fazendo upload de um vídeo e veja a análise em ação!**
