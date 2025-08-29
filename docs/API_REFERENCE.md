# 📚 Referência da API - Arquitetura Refatorada de Visão Computacional

## 📋 **VISÃO GERAL**

Esta documentação descreve a API completa da arquitetura refatorada de visão computacional para reconhecimento de placas de trânsito e veículos.

## 🏗️ **ESTRUTURA DA API**

### **🧩 Componentes Principais**

```
vision/
├── core/                    # Componentes principais
│   ├── base_processor.py   # Interface base
│   └── vision_pipeline.py  # Pipeline principal
├── preprocessing/           # Pré-processamento de imagens
│   └── image_preprocessor.py
├── detection/              # Detecção de objetos
│   └── yolo_detector.py
├── ocr/                    # Reconhecimento de texto
│   └── text_extractor.py
└── __init__.py             # Inicialização do módulo

config/
└── vision_architecture.py  # Configurações centralizadas
```

## 🔧 **CONFIGURAÇÃO**

### **⚙️ ConfigPresets**

#### **Desenvolvimento**
```python
from config.vision_architecture import ConfigPresets

config = ConfigPresets.development()
# - YOLOv8n (CPU)
# - PaddleOCR (CPU)
# - Logging detalhado
# - Cache desabilitado
```

#### **Produção**
```python
config = ConfigPresets.production()
# - YOLOv8x (GPU)
# - PaddleOCR (GPU)
# - Cache habilitado
# - Logging otimizado
```

#### **Edge Computing**
```python
config = ConfigPresets.edge()
# - YOLOv8n (CPU)
# - Tesseract (CPU)
# - Half precision
# - Cache otimizado
```

### **🔧 Configuração Customizada**
```python
from config.vision_architecture import (
    VisionArchitectureConfig, 
    ModelConfig, 
    OCRConfig,
    PreprocessingConfig
)

config = VisionArchitectureConfig(
    detection_model=ModelConfig(
        name="yolov8x",
        confidence_threshold=0.7,
        device="cuda"
    ),
    ocr_model=OCRConfig(
        type="paddleocr",
        confidence_threshold=0.8,
        use_gpu=True
    ),
    preprocessing=PreprocessingConfig(
        type="ai_enhanced",
        denoising=True,
        contrast_enhancement=True
    )
)
```

## 🚀 **PIPELINE PRINCIPAL**

### **🔧 VisionPipeline**

#### **Inicialização**
```python
from vision.core.vision_pipeline import VisionPipeline

# Usar configuração padrão
pipeline = VisionPipeline()

# Ou configuração customizada
pipeline = VisionPipeline(config_dict)
```

#### **Métodos Principais**

##### **process_image_advanced(image_path: str) → PipelineResult**
Processa uma imagem com pipeline completo.

**Parâmetros:**
- `image_path` (str): Caminho para a imagem

**Retorna:**
- `PipelineResult`: Resultado completo do processamento

**Exemplo:**
```python
result = pipeline.process_image_advanced("imagem.jpg")

if result.success:
    print(f"✅ Processamento bem-sucedido em {result.processing_time:.2f}s")
    print(f"🔍 Detecções: {result.metadata['total_detections']}")
    print(f"📝 Textos: {result.metadata['total_texts']}")
    
    for final_result in result.final_results:
        detection = final_result['detection']
        text = final_result['primary_text']
        confidence = final_result['confidence_score']
        
        print(f"  - {detection['class_name']}: {text} (conf: {confidence:.3f})")
```

##### **process_batch(image_paths: List[str], output_dir: str = None) → List[PipelineResult]**
Processa múltiplas imagens em lote.

**Parâmetros:**
- `image_paths` (List[str]): Lista de caminhos para imagens
- `output_dir` (str, opcional): Diretório para salvar resultados

**Retorna:**
- `List[PipelineResult]`: Lista de resultados

**Exemplo:**
```python
image_paths = ["img1.jpg", "img2.jpg", "img3.jpg"]
results = pipeline.process_batch(image_paths, "output_dir")

successful = sum(1 for r in results if r.success)
print(f"✅ Processadas {successful}/{len(results)} imagens com sucesso")
```

##### **get_pipeline_statistics() → Dict[str, Any]**
Retorna estatísticas do pipeline.

**Retorna:**
- `Dict[str, Any]`: Estatísticas completas

**Exemplo:**
```python
stats = pipeline.get_pipeline_statistics()
print(f"Versão: {stats['pipeline_version']}")
print(f"Componentes: {stats['components']}")
print(f"Inicializado em: {stats['initialized_at']}")
```

##### **cleanup()**
Limpa recursos do pipeline.

**Exemplo:**
```python
pipeline.cleanup()
# Pipeline não pode mais ser usado após cleanup
```

## 📸 **PRÉ-PROCESSAMENTO**

### **🔧 ImagePreprocessor**

#### **Inicialização**
```python
from vision.preprocessing.image_preprocessor import ImagePreprocessor

config = {
    'resize_enabled': True,
    'target_size': (640, 640),
    'denoising_enabled': True,
    'contrast_enhancement': True,
    'normalization': True
}

preprocessor = ImagePreprocessor(config)
```

#### **Métodos Principais**

##### **preprocess(image: np.ndarray) → PreprocessingResult**
Aplica pipeline completo de pré-processamento.

**Parâmetros:**
- `image` (np.ndarray): Imagem de entrada

**Retorna:**
- `PreprocessingResult`: Resultado do pré-processamento

**Exemplo:**
```python
result = preprocessor.preprocess(image)
processed_image = result.processed_image
enhancements = result.enhancement_applied

print(f"Melhorias aplicadas: {enhancements}")
```

##### **resize_image(image: np.ndarray, target_size: Tuple[int, int]) → np.ndarray**
Redimensiona imagem para tamanho específico.

**Parâmetros:**
- `image` (np.ndarray): Imagem de entrada
- `target_size` (Tuple[int, int]): Tamanho alvo (largura, altura)

**Retorna:**
- `np.ndarray`: Imagem redimensionada

##### **apply_denoising(image: np.ndarray) → np.ndarray**
Aplica técnicas de redução de ruído.

**Métodos disponíveis:**
- `DenoisingMethod.GAUSSIAN`
- `DenoisingMethod.BILATERAL`
- `DenoisingMethod.MEDIAN`
- `DenoisingMethod.NON_LOCAL_MEANS`

##### **enhance_contrast(image: np.ndarray) → np.ndarray**
Melhora o contraste da imagem.

**Métodos disponíveis:**
- `EnhancementMethod.HISTOGRAM_EQUALIZATION`
- `EnhancementMethod.CLAHE`
- `EnhancementMethod.ADAPTIVE_THRESHOLD`

##### **get_preprocessing_summary() → Dict[str, Any]**
Retorna resumo das configurações.

## 🔍 **DETECÇÃO**

### **🔧 YOLODetector**

#### **Inicialização**
```python
from vision.detection.yolo_detector import YOLODetector

config = {
    'weights_path': 'yolov8n.pt',
    'confidence_threshold': 0.5,
    'nms_threshold': 0.4,
    'input_size': (640, 640),
    'device': 'auto'
}

detector = YOLODetector(config)
```

#### **Métodos Principais**

##### **detect(image: np.ndarray) → DetectionBatchResult**
Executa detecção na imagem.

**Parâmetros:**
- `image` (np.ndarray): Imagem de entrada

**Retorna:**
- `DetectionBatchResult`: Resultado da detecção

**Exemplo:**
```python
result = detector.detect(image)
print(f"Detectados {len(result.detections)} objetos")

for detection in result.detections:
    print(f"  - {detection.class_name}: {detection.confidence:.3f}")
    print(f"    BBox: {detection.bbox}")
    print(f"    Área: {detection.area}")
```

##### **detect_traffic_signs(image: np.ndarray) → List[DetectionResult]**
Detecta especificamente placas de trânsito.

##### **detect_vehicle_plates(image: np.ndarray) → List[DetectionResult]**
Detecta especificamente placas de veículos.

##### **detect_vehicles(image: np.ndarray) → List[DetectionResult]**
Detecta especificamente veículos.

##### **filter_detections_by_size(detections: List[DetectionResult], min_area: float, max_area: float) → List[DetectionResult]**
Filtra detecções por tamanho.

##### **filter_detections_by_confidence(detections: List[DetectionResult], min_confidence: float) → List[DetectionResult]**
Filtra detecções por confiança.

##### **get_detection_statistics(detections: List[DetectionResult]) → Dict[str, Any]**
Retorna estatísticas das detecções.

##### **draw_detections(image: np.ndarray, detections: List[DetectionResult], show_labels: bool = True, show_confidence: bool = True) → np.ndarray**
Desenha detecções na imagem.

## 📝 **OCR**

### **🔧 TextExtractor**

#### **Inicialização**
```python
from vision.ocr.text_extractor import TextExtractor, OCRType

config = {
    'type': OCRType.PADDLEOCR,
    'language': 'pt',
    'confidence_threshold': 0.7,
    'use_gpu': False,
    'apply_plate_rules': True
}

extractor = TextExtractor(config)
```

#### **Métodos Principais**

##### **extract_text(image: np.ndarray, regions: List[Dict[str, Any]] = None) → OCRBatchResult**
Extrai texto da imagem ou regiões específicas.

**Parâmetros:**
- `image` (np.ndarray): Imagem de entrada
- `regions` (List[Dict[str, Any]], opcional): Regiões para processar

**Retorna:**
- `OCRBatchResult`: Resultado da extração de texto

**Exemplo:**
```python
# Extrair texto de toda a imagem
result = extractor.extract_text(image)

# Extrair texto de regiões específicas
regions = [{'bbox': (100, 100, 200, 150)}]
result = extractor.extract_text(image, regions)

for text_result in result.text_results:
    print(f"Texto: {text_result.text}")
    print(f"Confiança: {text_result.confidence:.3f}")
    print(f"BBox: {text_result.bbox}")
```

##### **postprocess_text(text: str) → str**
Pós-processa texto extraído.

##### **get_ocr_statistics(results: OCRBatchResult) → Dict[str, Any]**
Retorna estatísticas do OCR.

## 📊 **ESTRUTURAS DE DADOS**

### **🔧 ProcessingResult**
```python
@dataclass
class ProcessingResult:
    success: bool
    image_path: str
    processing_time: float
    detections: List[Dict[str, Any]]
    ocr_results: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    error_message: Optional[str] = None
    timestamp: datetime = None
```

### **🔧 PipelineResult**
```python
@dataclass
class PipelineResult:
    success: bool
    image_path: str
    processing_time: float
    preprocessing_result: Optional[Dict[str, Any]] = None
    detection_result: Optional[Dict[str, Any]] = None
    ocr_result: Optional[Dict[str, Any]] = None
    final_results: List[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None
    error_message: Optional[str] = None
    timestamp: datetime = None
```

### **🔧 DetectionResult**
```python
@dataclass
class DetectionResult:
    bbox: Tuple[int, int, int, int]  # x, y, w, h
    confidence: float
    class_id: int
    class_name: str
    area: float
    center: Tuple[int, int]
```

### **🔧 TextResult**
```python
@dataclass
class TextResult:
    text: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x, y, w, h
    language: str
    processing_time: float
```

## 🎯 **EXEMPLOS DE USO COMPLETOS**

### **🚀 Exemplo Básico**
```python
from config.vision_architecture import ConfigPresets
from vision.core.vision_pipeline import VisionPipeline

# Configuração de desenvolvimento
config = ConfigPresets.development()
pipeline = VisionPipeline(config)

# Processar imagem
result = pipeline.process_image_advanced("imagem.jpg")

if result.success:
    print(f"✅ Processamento concluído em {result.processing_time:.2f}s")
    
    for final_result in result.final_results:
        detection = final_result['detection']
        text = final_result['primary_text']
        confidence = final_result['confidence_score']
        
        print(f"🔍 {detection['class_name']}: {text} (conf: {confidence:.3f})")
else:
    print(f"❌ Erro: {result.error_message}")

# Limpeza
pipeline.cleanup()
```

### **🔄 Exemplo de Processamento em Lote**
```python
from config.vision_architecture import ConfigPresets
from vision.core.vision_pipeline import VisionPipeline
from pathlib import Path

# Configuração de produção
config = ConfigPresets.production()
pipeline = VisionPipeline(config)

# Encontrar todas as imagens em um diretório
image_dir = Path("imagens")
image_paths = list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.png"))

# Processar em lote
results = pipeline.process_batch([str(p) for p in image_paths], "resultados")

# Análise dos resultados
successful = sum(1 for r in results if r.success)
total_time = sum(r.processing_time for r in results)
total_detections = sum(r.metadata['total_detections'] for r in results if r.success)

print(f"📊 Resumo do Processamento:")
print(f"  ✅ Sucessos: {successful}/{len(results)}")
print(f"  ⏱️  Tempo total: {total_time:.2f}s")
print(f"  🔍 Total de detecções: {total_detections}")

# Limpeza
pipeline.cleanup()
```

### **⚙️ Exemplo com Configuração Customizada**
```python
from config.vision_architecture import (
    VisionArchitectureConfig, 
    ModelConfig, 
    OCRConfig,
    PreprocessingConfig
)
from vision.core.vision_pipeline import VisionPipeline

# Configuração personalizada para alta precisão
config = VisionArchitectureConfig(
    detection_model=ModelConfig(
        name="yolov8x",
        confidence_threshold=0.7,
        device="cuda",
        input_size=(1024, 1024)
    ),
    ocr_model=OCRConfig(
        type="paddleocr",
        confidence_threshold=0.85,
        use_gpu=True,
        language="pt"
    ),
    preprocessing=PreprocessingConfig(
        type="ai_enhanced",
        denoising=True,
        contrast_enhancement=True,
        normalization=True,
        additional_filters=True
    )
)

pipeline = VisionPipeline(config.__dict__)

# Processar com configuração otimizada
result = pipeline.process_image_advanced("imagem_alta_qualidade.jpg")

# Limpeza
pipeline.cleanup()
```

## 🧪 **TESTES**

### **🔬 Executar Testes**
```bash
# Testes unitários
pytest tests/test_preprocessing.py -v
pytest tests/test_detection.py -v
pytest tests/test_ocr.py -v

# Testes de integração
pytest tests/test_pipeline.py -v
pytest tests/test_integration.py -v

# Todos os testes com cobertura
pytest tests/ --cov=vision --cov=config --cov-report=html
```

### **📊 Cobertura de Testes**
```bash
# Gerar relatório HTML
pytest --cov=vision --cov=config --cov-report=html:htmlcov

# Abrir relatório
open htmlcov/index.html
```

## 🚀 **DEPLOYMENT**

### **🐳 Docker**
```dockerfile
FROM python:3.9-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    tesseract-ocr \
    tesseract-ocr-por

# Copiar código
COPY . /app
WORKDIR /app

# Instalar dependências Python
RUN pip install -r requirements_refatorado.txt

# Executar
CMD ["python", "examples/refactored_vision_example.py"]
```

### **☁️ Cloud Deployment**
```bash
# Google Cloud Run
gcloud run deploy vision-pipeline \
  --source . \
  --platform managed \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2

# AWS Lambda
serverless deploy

# Azure Functions
func azure functionapp publish vision-pipeline
```

## 📈 **MONITORAMENTO E MÉTRICAS**

### **📊 Estatísticas do Pipeline**
```python
# Obter estatísticas completas
stats = pipeline.get_pipeline_statistics()

print(f"📦 Versão: {stats['pipeline_version']}")
print(f"🧩 Componentes ativos: {stats['components']}")
print(f"🕐 Inicializado em: {stats['initialized_at']}")
print(f"💾 Cache: {stats['cache_size']} itens")
```

### **🔍 Logging Estruturado**
```python
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Logs automáticos para cada componente
# - Pré-processamento
# - Detecção
# - OCR
# - Integração
# - Validação
```

## 🚨 **TRATAMENTO DE ERROS**

### **🔧 Tratamento de Exceções**
```python
try:
    result = pipeline.process_image_advanced("imagem.jpg")
    
    if result.success:
        print("✅ Processamento bem-sucedido")
    else:
        print(f"❌ Falha: {result.error_message}")
        
except Exception as e:
    print(f"💥 Erro inesperado: {e}")
    logging.error(f"Erro no pipeline: {e}", exc_info=True)
```

### **🔄 Fallback Automático**
```python
# O sistema OCR tem fallback automático entre motores
# Se PaddleOCR falhar, tenta EasyOCR, depois Tesseract

# O detector YOLO tem fallback automático de dispositivo
# Se CUDA falhar, tenta CPU automaticamente
```

## 🔮 **ROADMAP FUTURO**

### **🚀 Versão 2.1 (Q1 2025)**
- [ ] Suporte a DETR e EfficientDet
- [ ] Pipeline de fine-tuning automático
- [ ] API REST integrada
- [ ] Dashboard de monitoramento

### **🚀 Versão 2.2 (Q2 2025)**
- [ ] Suporte a vídeo em tempo real
- [ ] Modelos de segmentação
- [ ] Análise de comportamento
- [ ] Integração com sistemas de trânsito

### **🌟 Versão 3.0 (Q4 2025)**
- [ ] Arquitetura distribuída
- [ ] AutoML para seleção de modelos
- [ ] Edge AI otimizado
- [ ] Suporte a múltiplas línguas

## 🤝 **SUPORTE E CONTRIBUIÇÃO**

### **📧 Suporte**
- **Issues**: [GitHub Issues]
- **Documentação**: [Wiki do Projeto]
- **Email**: [seu-email@exemplo.com]

### **🔧 Contribuição**
1. Fork o projeto
2. Crie uma branch para sua feature
3. Implemente seguindo os padrões da arquitetura
4. Adicione testes
5. Abra um Pull Request

### **📋 Padrões de Código**
- **Black**: Formatação automática
- **Flake8**: Linting
- **MyPy**: Verificação de tipos
- **Docstrings**: Documentação obrigatória

---

## 🎉 **CONCLUSÃO**

Esta API fornece uma interface completa e flexível para reconhecimento de placas de trânsito e veículos, com:

✅ **Modularidade**: Componentes independentes e intercambiáveis  
✅ **Escalabilidade**: Suporte a diferentes cenários de uso  
✅ **Testabilidade**: Arquitetura orientada a testes  
✅ **Extensibilidade**: Fácil adição de novas funcionalidades  
✅ **Performance**: Otimizações para diferentes hardwares  
✅ **Manutenibilidade**: Código limpo e bem documentado  

**🚀 A API está pronta para uso em produção e desenvolvimento!**

---

*Última atualização: Janeiro 2025*