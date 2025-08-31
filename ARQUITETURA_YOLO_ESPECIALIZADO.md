# 🚀 Arquitetura com YOLOs Especializados

## 📋 Visão Geral

Esta arquitetura implementa **YOLOs especializados** para diferentes cenários de detecção, seguindo o fluxo:

```
OpenCV + Numpy (pré-processamento) 
    ↓
YOLO Detecção do OBJ 
    ↓
OCR (VEÍCULO) + RNN CONVOLUCIONAL (PLACA) 
    ↓
SAÍDA
```

## 🏗️ Estrutura da Arquitetura

### 1. **Endpoints Separados**
- **`/api/v1/detect/signal-plates`** - Detecção de placas de sinalização
- **`/api/v1/detect/vehicle-plates`** - Detecção de placas de veículos
- **`/api/v1/detect/general`** - Detecção geral (compatibilidade)

### 2. **YOLOs Especializados**

#### 🔴 **SignalPlateDetector** - Placas de Sinalização
- **Modelo**: `models/signal_plates_yolo.pt`
- **Classes**: 16 tipos de sinalização
- **Aplicações**:
  - Sinais de trânsito (PARE, DÊ PREFERÊNCIA)
  - Placas de rua e construção
  - Sinais de aviso e informação
  - Placas de zona escolar, pedestres, etc.

#### 🚗 **VehiclePlateDetector** - Placas de Veículos
- **Modelo**: `models/vehicle_plates_yolo.pt`
- **Classes**: 12 tipos de veículos + 8 tipos de placas
- **Aplicações**:
  - Carros, caminhões, motos, ônibus
  - Placas Mercosul, padrão antigo, diplomáticas
  - Agrupamento veículo-placa inteligente

### 3. **Fluxo de Processamento**

```
Imagem de Entrada
    ↓
Pré-processamento (OpenCV + Numpy)
    ↓
Seleção do YOLO Especializado
    ↓
Detecção YOLO
    ↓
Validação e Filtragem
    ↓
OCR/Classificação Especializada
    ↓
Resultado Estruturado
```

## 🎯 Vantagens da Arquitetura

### ✅ **Especialização**
- Cada YOLO otimizado para seu domínio
- Maior precisão em cenários específicos
- Redução de falsos positivos

### ✅ **Flexibilidade**
- Endpoints independentes
- Configuração por cenário
- Fallback para modelo geral

### ✅ **Performance**
- Modelos menores e mais rápidos
- Inferência otimizada por tipo
- Cache inteligente de resultados

### ✅ **Manutenibilidade**
- Código modular e organizado
- Configuração centralizada
- Fácil atualização de modelos

## 🔧 Configuração

### Arquivo de Configuração
```json
{
  "yolo_models": {
    "signal_plates": {
      "model_path": "models/signal_plates_yolo.pt",
      "confidence_threshold": 0.5,
      "classes": ["stop_sign", "yield_sign", ...]
    },
    "vehicle_plates": {
      "model_path": "models/vehicle_plates_yolo.pt",
      "confidence_threshold": 0.5,
      "vehicle_classes": ["car", "truck", ...],
      "plate_classes": ["mercosul_plate", ...]
    }
  }
}
```

### Variáveis de Ambiente
```bash
# Modelos YOLO
SIGNAL_PLATES_MODEL_PATH=models/signal_plates_yolo.pt
VEHICLE_PLATES_MODEL_PATH=models/vehicle_plates_yolo.pt

# Thresholds
DEFAULT_CONFIDENCE_THRESHOLD=0.5
DEFAULT_IOU_THRESHOLD=0.45

# Dispositivo
YOLO_DEVICE=auto  # cpu, cuda, auto
```

## 📊 Uso da API

### 1. **Detecção de Placas de Sinalização**
```bash
curl -X POST "http://localhost:8000/api/v1/detect/signal-plates" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "image": "data:image/jpeg;base64,...",
    "confidence_threshold": 0.6,
    "signal_types": ["stop", "yield", "speed_limit"]
  }'
```

### 2. **Detecção de Placas de Veículos**
```bash
curl -X POST "http://localhost:8000/api/v1/detect/vehicle-plates" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "image": "data:image/jpeg;base64,...",
    "vehicle_type": "car",
    "confidence_threshold": 0.7,
    "plate_types": ["mercosul", "old_standard"]
  }'
```

### 3. **Detecção Geral**
```bash
curl -X POST "http://localhost:8000/api/v1/detect/general" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "image": "data:image/jpeg;base64,...",
    "detection_type": "both",
    "confidence_threshold": 0.5
  }'
```

## 🚀 Implementação

### 1. **Instalação de Dependências**
```bash
pip install ultralytics opencv-python numpy torch
```

### 2. **Download dos Modelos**
```bash
# Modelo padrão (fallback)
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

# Modelos especializados (treinar ou baixar)
# models/signal_plates_yolo.pt
# models/vehicle_plates_yolo.pt
```

### 3. **Execução**
```bash
# Desenvolvimento
python -m vision.api.api_server

# Produção
docker-compose -f docker-compose.prod.yml up -d
```

## 📈 Métricas e Monitoramento

### **Estatísticas de Detecção**
- Total de detecções por tipo
- Confiança média
- Distribuição de classes
- Tamanhos das bounding boxes

### **Performance**
- Tempo de processamento
- Uso de memória e CPU
- Taxa de sucesso por endpoint
- Latência de resposta

## 🔮 Roadmap

### **Fase 1** ✅
- [x] Endpoints separados
- [x] YOLOs especializados
- [x] Configuração centralizada
- [x] Validação e filtragem

### **Fase 2** 🚧
- [ ] Treinamento dos modelos especializados
- [ ] Dataset de placas brasileiras
- [ ] Fine-tuning para cenários específicos
- [ ] A/B testing de modelos

### **Fase 3** 📋
- [ ] RNN Convolucional para classificação
- [ ] OCR otimizado para placas
- [ ] Reconhecimento de caracteres
- [ ] Validação de formato de placa

### **Fase 4** 🎯
- [ ] Modelos quantizados
- [ ] Inferência em edge devices
- [ ] Real-time processing
- [ ] API GraphQL

## 🐛 Troubleshooting

### **Problemas Comuns**

1. **Modelo não encontrado**
   ```bash
   # Verificar caminho dos modelos
   ls -la models/
   
   # Usar modelo padrão como fallback
   export SIGNAL_PLATES_MODEL_PATH=yolov8n.pt
   ```

2. **Baixa precisão**
   ```bash
   # Ajustar thresholds
   export DEFAULT_CONFIDENCE_THRESHOLD=0.7
   export DEFAULT_IOU_THRESHOLD=0.3
   ```

3. **Performance lenta**
   ```bash
   # Forçar uso de GPU
   export YOLO_DEVICE=cuda
   
   # Reduzir tamanho da imagem
   export IMAGE_SIZE=416
   ```

## 📚 Referências

- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics)
- [OpenCV Python](https://opencv-python-tutroals.readthedocs.io/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)

## 🤝 Contribuição

1. Fork do projeto
2. Criar branch para feature
3. Implementar mudanças
4. Adicionar testes
5. Criar Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

**Desenvolvido com ❤️ pela Equipe de Visão Computacional**
