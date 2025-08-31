# 🚀 Arquitetura Atualizada - Sistema de Reconhecimento de Placas

## 📋 Visão Geral

A arquitetura foi **completamente refatorada** para implementar um sistema **modular e especializado** com detectores YOLO dedicados para diferentes tipos de detecção:

1. **🚗 VehiclePlateDetector** - Detecção especializada de placas de veículos
2. **🚦 SignalPlateDetector** - Detecção especializada de sinalização de trânsito
3. **🕳️ PotholeDetector** - Detecção multimodal de buracos na estrada
4. **🔗 SpecializedDetector** - Orquestrador unificado dos detectores especializados
5. **⚙️ VisionPipeline** - Pipeline principal integrado com todos os componentes

## 🏗️ Arquitetura da Solução

```
┌─────────────────────────────────────────────────────────────────┐
│                    VISÃO COMPUTACIONAL                         │
├─────────────────────────────────────────────────────────────────┤
│  🖼️ ImagePreprocessor  │  🔍 YOLODetector  │  📝 TextExtractor  │
│     (Pré-processamento) │   (Detecção Geral) │      (OCR)        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 SPECIALIZED DETECTOR SYSTEM                    │
├─────────────────────────────────────────────────────────────────┤
│  🚗 VehiclePlateDetector  │  🚦 SignalPlateDetector  │  🕳️ PotholeDetector  │
│   • Veículos (car, truck) │   • Regulamentação (R-1) │   • Análise multimodal │
│   • Placas (Mercosul)     │   • Avisos (curvas)      │   • Severidade         │
│   • Classificação automática│   • Informação (80km/h) │   • Score de risco     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VISION PIPELINE                             │
│  • Integração de todos os componentes                         │
│  • Processamento sequencial otimizado                         │
│  • Resultados unificados e estruturados                       │
│  • Exportação em múltiplos formatos                           │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Componentes Principais

### 1. **VehiclePlateDetector** - Detector de Placas de Veículos

**Funcionalidades:**
- Detecção de veículos (carros, caminhões, motos, etc.)
- Detecção de placas (Mercosul, padrão antigo, diplomáticas)
- Classificação automática de tipo de veículo e placa
- Estatísticas detalhadas de detecção

**Classes Suportadas:**
```python
vehicle_classes = [
    'car', 'truck', 'bus', 'motorcycle', 'bicycle', 'van', 'pickup'
]

plate_classes = [
    'mercosul_plate', 'old_plate', 'diplomatic_plate', 'official_plate',
    'motorcycle_plate', 'truck_plate', 'trailer_plate'
]
```

**Exemplo de Uso:**
```python
from vision.detection.vehicle_plate_detector import VehiclePlateDetector

config = {'model_path': 'models/vehicle_plates_yolo.pt'}
detector = VehiclePlateDetector(config)

detections = detector.detect(image)
for det in detections:
    if det.vehicle_type:
        print(f"Veículo: {det.vehicle_type}")
    if det.plate_type:
        print(f"Placa: {det.plate_type}")
```

### 2. **SignalPlateDetector** - Detector de Sinalização de Trânsito

**Funcionalidades:**
- Detecção de placas de sinalização de trânsito
- Classificação por categoria (regulamentação, aviso, informação)
- Códigos CONTRAN automáticos (R-1 a R-15)
- Estatísticas por tipo de sinal

**Categorias Suportadas:**
```python
regulatory_signs = [
    'stop_sign', 'yield_sign', 'no_entry', 'no_left_turn', 'no_right_turn',
    'no_u_turn', 'no_parking', 'no_stopping', 'no_overtaking', 'speed_limit',
    'weight_limit', 'height_limit', 'width_limit', 'customs', 'chains_required'
]

warning_signs = [
    'curve_left', 'curve_right', 'double_curve', 'intersection', 'roundabout',
    'pedestrian_crossing', 'school_zone', 'construction', 'animals', 'falling_rocks'
]

information_signs = [
    'one_way', 'two_way', 'priority_road', 'keep_right', 'keep_left',
    'buses_only', 'bicycles_only', 'pedestrians_only', 'parking', 'hospital'
]
```

**Exemplo de Uso:**
```python
from vision.detection.signal_plate_detector import SignalPlateDetector

config = {'model_path': 'models/signal_plates_yolo.pt'}
detector = SignalPlateDetector(config)

detections = detector.detect(image)
for det in detections:
    print(f"Sinal: {det.signal_type}")
    print(f"Categoria: {det.signal_category}")
    if det.regulatory_code:
        print(f"Código: {det.regulatory_code}")
```

### 3. **PotholeDetector** - Detector Multimodal de Buracos

**Funcionalidades:**
- Detecção de buracos e danos na estrada
- **Análise multimodal**: combina detecção visual com análise de profundidade
- Estimativa de profundidade baseada em intensidade da imagem
- Classificação de severidade (baixa, média, alta, crítica)
- Cálculo de risco baseado em múltiplos fatores
- Geração de relatórios de condição da estrada

**Tipos Detectados:**
```python
pothole_types = [
    'small_pothole', 'medium_pothole', 'large_pothole', 'crack',
    'sinkhole', 'road_damage', 'surface_deterioration', 'edge_drop'
]

severity_levels = {
    'low': {'depth_range': (0.01, 0.05), 'risk_score': (0.1, 0.3)},
    'medium': {'depth_range': (0.05, 0.15), 'risk_score': (0.3, 0.6)},
    'high': {'depth_range': (0.15, 0.30), 'risk_score': (0.6, 0.8)},
    'critical': {'depth_range': (0.30, 1.0), 'risk_score': (0.8, 1.0)}
}
```

**Análise Multimodal:**
```python
# O detector combina:
# 1. Detecção visual (YOLO)
# 2. Análise de profundidade (intensidade da imagem)
# 3. Cálculo de área
# 4. Classificação de severidade
# 5. Score de risco

detection = pothole_detector.detect(image)[0]
print(f"Tipo: {detection.pothole_type}")
print(f"Profundidade estimada: {detection.depth_estimate:.3f}")
print(f"Severidade: {detection.severity_level}")
print(f"Score de risco: {detection.risk_score:.3f}")
```

**Relatório da Estrada:**
```python
road_report = pothole_detector.generate_road_report(detections)
print(f"Condição: {road_report['summary']['road_condition']}")
print(f"Prioridade: {road_report['summary']['maintenance_priority']}")
print("Recomendações:")
for rec in road_report['recommendations']:
    print(f"  • {rec}")
```

### 4. **SpecializedDetector** - Orquestrador Unificado

**Funcionalidades:**
- Gerencia todos os detectores especializados
- Detecção simultânea de todos os tipos
- Resultados unificados e estruturados
- Estatísticas agregadas
- Exportação em múltiplos formatos (JSON, CSV, XML)

**Exemplo Completo:**
```python
from vision.detection.specialized_detector import SpecializedDetector

# Configuração completa
config = {
    'enabled_detectors': ['vehicle', 'signal', 'pothole'],
    'vehicle_detector': {'model_path': 'models/vehicle_plates_yolo.pt'},
    'signal_detector': {'model_path': 'models/signal_plates_yolo.pt'},
    'pothole_detector': {'model_path': 'models/pothole_yolo.pt'}
}

detector = SpecializedDetector(config)

# Detecção completa
result = detector.detect_all(image)

# Estatísticas unificadas
stats = detector.get_comprehensive_statistics(result)
print(f"Total de detecções: {stats['overview']['total_detections']}")

# Filtros
high_confidence = detector.filter_by_confidence(result, min_confidence=0.8)

# Exportação
json_data = detector.export_detections(result, 'json')
csv_data = detector.export_detections(result, 'csv')

# Visualização
annotated_image = detector.draw_all_detections(image, result)
```

### 5. **VisionPipeline** - Pipeline Principal Integrado

**Funcionalidades:**
- Integra todos os componentes (pré-processamento, detecção, OCR, detectores especializados)
- Processamento sequencial otimizado
- Resultados unificados e estruturados
- Cache inteligente
- Monitoramento de performance
- Processamento em lote

**Exemplo de Uso:**
```python
from vision.core.vision_pipeline import VisionPipeline
import yaml

# Carregar configuração
with open('config/pipeline_with_specialized.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Inicializar pipeline
pipeline = VisionPipeline(config)

# Processar imagem
result = pipeline.process_image("image.jpg")

# Acessar resultados
print(f"Detecções: {len(result.detections)}")
print(f"OCR: {len(result.ocr_results)}")
print(f"Integrados: {len(result.integrated_results)}")
print(f"Especializados: {result.specialized_results.total_detections if result.specialized_results else 0}")

# Processar lote
results = pipeline.process_batch(["img1.jpg", "img2.jpg", "img3.jpg"])

# Estatísticas
stats = pipeline.get_statistics()
print(f"Total processado: {stats['total_processed']}")
print(f"Tempo médio: {stats['average_processing_time']:.3f}s")
```

## ⚙️ Configuração

### Arquivo de Configuração Principal

```yaml
# config/pipeline_with_specialized.yaml

# Detectores especializados
specialized_detector:
  enabled: true
  enabled_detectors: ["vehicle", "signal", "pothole"]
  
  vehicle_detector:
    model_path: "models/vehicle_plates_yolo.pt"
    confidence_threshold: 0.6
    iou_threshold: 0.45
  
  signal_detector:
    model_path: "models/signal_plates_yolo.pt"
    confidence_threshold: 0.6
    iou_threshold: 0.45
  
  pothole_detector:
    model_path: "models/pothole_yolo.pt"
    confidence_threshold: 0.6
    analysis:
      enable_depth_estimation: true
      enable_area_calculation: true
      enable_risk_scoring: true

# Pipeline
pipeline:
  enable_preprocessing: true
  enable_detection: true
  enable_specialized_detection: true
  enable_ocr: true
  enable_integration: true
  batch_size: 8
  cache_results: true
```

### Configurações por Ambiente

```python
from config.vision_architecture import ConfigPresets

# Desenvolvimento
dev_config = ConfigPresets.development()

# Produção
prod_config = ConfigPresets.production()

# Edge/Dispositivos limitados
edge_config = ConfigPresets.edge()
```

## 📊 Análise de Resultados

### Estatísticas Detalhadas

```python
stats = detector.get_comprehensive_statistics(result)

# Análise de veículos
vehicle_stats = stats['vehicle_analysis']
print(f"Veículos detectados: {vehicle_stats['vehicle_count']}")
print(f"Placas detectadas: {vehicle_stats['plate_count']}")

# Análise de sinalização
signal_stats = stats['signal_analysis']
print(f"Sinais regulamentares: {signal_stats['regulatory_count']}")

# Análise de buracos
pothole_stats = stats['pothole_analysis']
print(f"Severidade crítica: {pothole_stats['severity_distribution'].get('critical', 0)}")
```

### Filtros Avançados

```python
# Filtrar por confiança
high_conf = detector.filter_by_confidence(result, min_confidence=0.8)

# Filtrar buracos por severidade
if detector.pothole_detector:
    critical_potholes = detector.pothole_detector.filter_by_severity(
        result.potholes, 'critical'
    )
    
    high_risk = detector.pothole_detector.filter_high_risk(
        result.potholes, threshold=0.7
    )
```

## 🎨 Visualização

### Desenho de Detecções

```python
# Desenhar todas as detecções
annotated_image = detector.draw_all_detections(image, result)

# Desenhar tipos específicos
if detector.vehicle_detector:
    vehicle_image = detector.vehicle_detector.draw_detections(image, result.vehicle_plates)

if detector.signal_detector:
    signal_image = detector.signal_detector.draw_detections(image, result.signal_plates)

if detector.pothole_detector:
    pothole_image = detector.pothole_detector.draw_detections(image, result.potholes)
```

### Cores por Categoria

- **🚗 Veículos**: Azul (255, 0, 0)
- **🚦 Sinalização**: 
  - Regulamentação: Vermelho (0, 0, 255)
  - Aviso: Laranja (0, 165, 255)
  - Informação: Verde (0, 255, 0)
- **🕳️ Buracos**:
  - Baixa severidade: Verde (0, 255, 0)
  - Média severidade: Amarelo (0, 255, 255)
  - Alta severidade: Laranja (0, 165, 255)
  - Crítica: Vermelho (0, 0, 255)

## 📤 Exportação de Dados

### Formato JSON

```python
json_data = detector.export_detections(result, 'json')
# Estrutura:
{
    "vehicle_plates": [
        {
            "bbox": [x1, y1, x2, y2],
            "confidence": 0.85,
            "class_name": "car",
            "plate_type": "mercosul_plate",
            "vehicle_type": "car"
        }
    ],
    "signal_plates": [...],
    "potholes": [...],
    "metadata": {...}
}
```

### Formato CSV

```python
csv_data = detector.export_detections(result, 'csv')
# Cabeçalho: Type,Bbox,Confidence,Class,Details
# Linhas: Vehicle,"(100,100,200,150)",0.85,car,Plate:mercosul_plate,Vehicle:car
```

## 🧪 Testes e Exemplos

### Executar Testes

```bash
# Teste básico dos detectores especializados
python test_specialized_detectors.py

# Exemplo dos detectores especializados
python examples/specialized_detectors_example.py

# Exemplo do pipeline integrado
python examples/integrated_pipeline_example.py
```

### Verificar Funcionamento

```python
# Teste de importação
from vision.detection import (
    VehiclePlateDetector, SignalPlateDetector, 
    PotholeDetector, SpecializedDetector
)

# Teste de configuração
import yaml
config = yaml.safe_load(open('config/specialized_detectors.yaml'))

# Teste de inicialização
detector = SpecializedDetector(config)
print(f"Detectores ativos: {detector.enabled_detectors}")
```

## 🚀 Próximos Passos

1. **Baixar Modelos YOLO** para cada detector especializado
2. **Treinar Modelos Customizados** para seu domínio específico
3. **Integrar com Pipeline Principal** de visão computacional
4. **Implementar API REST** para os detectores especializados
5. **Adicionar Novos Tipos** de detecção conforme necessário
6. **Otimizar Performance** com TensorRT e outras técnicas
7. **Implementar Monitoramento** em tempo real
8. **Criar Dashboards** de análise e visualização

## 📚 Recursos Adicionais

- [README dos Detectores Especializados](README_DETECTORES_ESPECIALIZADOS.md)
- [Exemplos de Uso](examples/)
- [Configurações](config/)
- [Documentação YOLO](https://docs.ultralytics.com/)
- [Arquitetura Original](ARQUITETURA_YOLO_ESPECIALIZADO.md)

---

## 🎯 Resumo da Arquitetura

A nova arquitetura implementa:

✅ **Modularidade**: Cada detector é independente e especializado
✅ **Escalabilidade**: Fácil adicionar novos tipos de detecção
✅ **Performance**: Otimizações específicas para cada domínio
✅ **Integração**: Pipeline unificado que orquestra todos os componentes
✅ **Configurabilidade**: Configurações flexíveis por ambiente
✅ **Monitoramento**: Estatísticas detalhadas e métricas de performance
✅ **Exportação**: Múltiplos formatos de saída
✅ **Manutenibilidade**: Código limpo e bem estruturado

**🚀 Comece testando os detectores especializados e depois integre ao pipeline principal!**
