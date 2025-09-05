# 🚀 Detectores Especializados - YOLO Multimodal

## 📋 Visão Geral

Este módulo implementa uma **arquitetura de detectores especializados** usando YOLO para diferentes tipos de detecção:

1. **🚗 VehiclePlateDetector** - Detecção de placas de veículos
2. **🚦 SignalPlateDetector** - Detecção de sinalização de trânsito  
3. **🕳️ PotholeDetector** - Detecção de buracos na estrada (modelo multimodal + análise de vídeo)
4. **🔗 SpecializedDetector** - Detector unificado que gerencia todos os especializados

## 🏗️ Arquitetura

```
SpecializedDetector (Unificado)
├── VehiclePlateDetector
│   ├── Detecção de veículos (car, truck, bus, etc.)
│   └── Detecção de placas (Mercosul, padrão antigo, etc.)
├── SignalPlateDetector
│   ├── Sinais de regulamentação (CONTRAN R-1 a R-15)
│   ├── Sinais de aviso
│   └── Sinais de informação
└── PotholeDetector (Multimodal + Vídeo)
    ├── Análise de profundidade
    ├── Classificação de severidade
    ├── Cálculo de risco
    ├── 🎬 Análise de vídeo
    ├── 🎯 Tracking temporal
    └── 📊 Relatórios de estrada
```

## 🚀 Início Rápido

### 1. Instalação das Dependências

```bash
pip install ultralytics opencv-python pyyaml numpy
```

### 2. Configuração

Crie o arquivo `config/specialized_detectors.yaml`:

```yaml
enabled_detectors:
  - vehicle
  - signal
  - pothole

vehicle_detector:
  model_path: "models/vehicle_plates_yolo.pt"
  confidence_threshold: 0.5

signal_detector:
  model_path: "models/signal_plates_yolo.pt"
  confidence_threshold: 0.5

pothole_detector:
  model_path: "models/pothole_yolo.pt"
  confidence_threshold: 0.5
  
  # Configurações para análise de vídeo
  video_analysis:
    frame_skip: 1                    # Processar todos os frames
    min_track_length: 3              # Mínimo de frames para track estável
    tracking_threshold: 0.7          # Threshold de sobreposição
    max_tracks: 50                   # Máximo de tracks simultâneos
    enable_frame_quality_assessment: true
    enable_temporal_analysis: true
    output_annotated_video: true     # Gerar vídeo com detecções
```

### 3. Uso Básico

```python
from vision.detection.specialized_detector import SpecializedDetector
import yaml

# Carregar configuração
with open('config/specialized_detectors.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Inicializar detector
detector = SpecializedDetector(config)

# Detecção completa
result = detector.detect_all(image)

# Acessar resultados
print(f"Veículos: {len(result.vehicle_plates)}")
print(f"Sinalização: {len(result.signal_plates)}")
print(f"Buracos: {len(result.potholes)}")

# Cleanup
detector.cleanup()
```

## 🔧 Componentes Detalhados

### 🚗 VehiclePlateDetector

**Funcionalidades:**
- Detecção de veículos (carros, caminhões, motos, etc.)
- Detecção de placas (Mercosul, padrão antigo, diplomáticas)
- Classificação automática de tipo de veículo e placa
- Estatísticas detalhadas de detecção

**Classes Suportadas:**
- **Veículos**: car, truck, bus, motorcycle, bicycle, van, pickup
- **Placas**: mercosul_plate, old_plate, diplomatic_plate, official_plate

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

### 🚦 SignalPlateDetector

**Funcionalidades:**
- Detecção de placas de sinalização de trânsito
- Classificação por categoria (regulamentação, aviso, informação)
- Códigos CONTRAN automáticos (R-1 a R-15)
- Estatísticas por tipo de sinal

**Categorias Suportadas:**
- **Regulamentação**: PARE, DÊ PREFERÊNCIA, PROIBIDO, etc.
- **Aviso**: Curvas, interseções, zonas escolares, etc.
- **Informação**: Mão única, estacionamento, hospitais, etc.

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

### 🕳️ PotholeDetector (Multimodal + Análise de Vídeo)

**Funcionalidades:**
- Detecção de buracos e danos na estrada
- **Análise multimodal**: combina detecção visual com análise de profundidade
- Estimativa de profundidade baseada em intensidade da imagem
- Classificação de severidade (baixa, média, alta, crítica)
- Cálculo de risco baseado em múltiplos fatores
- **🎬 Análise de vídeo completo** com tracking temporal
- **🎯 Sistema de tracking** para acompanhar buracos ao longo do tempo
- **📊 Relatórios de condição da estrada** baseados em análise temporal

**Tipos Detectados:**
- small_pothole, medium_pothole, large_pothole
- crack, sinkhole, road_damage
- surface_deterioration, edge_drop

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

**🎬 Análise de Vídeo:**
```python
# Processar vídeo completo
video_report = pothole_detector.process_video(
    video_path="road_video.mp4",
    output_path="annotated_video.mp4"
)

# O detector gera:
# 1. Vídeo anotado com detecções em tempo real
# 2. Relatório completo da análise
# 3. Estatísticas de tracking temporal
# 4. Análise de qualidade dos frames
# 5. Recomendações baseadas na análise temporal
```

**🎯 Sistema de Tracking:**
```python
# Estatísticas de tracking
tracking_stats = pothole_detector.get_tracking_statistics()
print(f"Total de tracks: {tracking_stats['total_tracks']}")
print(f"Tracks estáveis: {tracking_stats['stable_tracks']}")
print(f"Comprimento médio: {tracking_stats['average_track_length']:.1f} frames")

# Distribuição dos tracks
track_dist = tracking_stats['track_distribution']
print(f"Tracks curtos: {track_dist['short']}")
print(f"Tracks estáveis: {track_dist['stable']}")
print(f"Tracks longos: {track_dist['long']}")
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

## 🔗 SpecializedDetector (Unificado)

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

## 🎬 Análise de Vídeo

### Configuração para Vídeo

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

### Processamento de Vídeo

```python
# Processar vídeo completo
video_report = pothole_detector.process_video(
    video_path="road_video.mp4",
    output_path="annotated_video.mp4"
)

# O detector gera:
# 1. Vídeo anotado com detecções em tempo real
# 2. Relatório completo da análise
# 3. Estatísticas de tracking temporal
# 4. Análise de qualidade dos frames
# 5. Recomendações baseadas na análise temporal
```

### Relatório de Vídeo

```python
# Estrutura do relatório de vídeo
video_report = {
    'video_info': {
        'fps': 30.0,
        'total_frames': 900,
        'duration': 30.0,
        'processed_frames': 900
    },
    'detection_summary': {
        'total_detections': 45,
        'frames_with_detections': 67,
        'detection_rate': 0.074
    },
    'quality_analysis': {
        'average_frame_quality': 0.723,
        'quality_distribution': {...}
    },
    'road_condition_analysis': {
        'condition_distribution': {...},
        'overall_condition': 'fair'
    },
    'maintenance_analysis': {
        'priority_distribution': {...},
        'overall_priority': 'medium'
    },
    'tracking_analysis': {
        'total_tracks': 12,
        'stable_tracks': 8,
        'track_details': [...]
    },
    'recommendations': [...]
}
```

## ⚙️ Configuração Avançada

### Configuração Detalhada

```yaml
# Configurações de performance
global_settings:
  performance:
    enable_half_precision: true
    enable_tensorrt: false
    max_processing_time: 30.0
  
  # Processamento em lote
  batch_processing:
    enabled: true
    max_batch_size: 8
  
  # Cache
  caching:
    enabled: true
    max_cache_size: 1000
    ttl_seconds: 3600

# Configurações específicas por detector
vehicle_detector:
  confidence_threshold: 0.6
  iou_threshold: 0.4
  device: "cuda"  # Forçar GPU

pothole_detector:
  analysis:
    enable_depth_estimation: true
    enable_area_calculation: true
    min_area_threshold: 200
  
  video_analysis:
    frame_skip: 2                    # Processar a cada 2 frames
    min_track_length: 5              # Tracks mais estáveis
    tracking_threshold: 0.8          # Tracking mais preciso
    max_tracks: 100                  # Mais tracks simultâneos
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

# 🎬 Exemplo de análise de vídeo
python examples/video_pothole_analysis_example.py
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
9. **🎬 Processar Vídeos Reais** de estradas para análise em produção
10. **🎯 Refinar Sistema de Tracking** para melhor estabilidade temporal

## 📚 Recursos Adicionais

- [Documentação YOLO](https://docs.ultralytics.com/)
- [Arquitetura de Visão Computacional](ARQUITETURA_YOLO_ESPECIALIZADO.md)
- [Exemplos de Uso](examples/)
- [Configurações](config/)
- [🎬 Exemplo de Análise de Vídeo](examples/video_pothole_analysis_example.py)

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
✅ **🎬 Análise de Vídeo**: Processamento completo de vídeos com tracking temporal
✅ **🎯 Tracking Temporal**: Sistema robusto para acompanhar objetos ao longo do tempo

**🚀 Comece testando os detectores especializados e depois integre ao pipeline principal!**

**🎬 Para análise de vídeo, use o exemplo específico: `python examples/video_pothole_analysis_example.py`**
