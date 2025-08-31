# 🚀 **Guia Completo: Treinamento dos Modelos YOLO Especializados**

## 📋 **Visão Geral**

Este guia te ensina como treinar os modelos YOLO especializados para placas brasileiras:

- **🚦 Signal Plates YOLO**: Placas de sinalização de trânsito
- **🚗 Vehicle Plates YOLO**: Placas de veículos (Mercosul, padrão antigo, etc.)

## 🎯 **Por que Treinar com Dados Brasileiros?**

### ✅ **Vantagens:**
- **Contexto local**: Placas e sinais específicos do Brasil
- **Maior precisão**: Modelos adaptados à realidade brasileira
- **Regulamentações**: Conformidade com leis de trânsito brasileiras
- **Performance**: Melhor detecção em cenários reais brasileiros

### 🌍 **Dados Brasileiros Específicos:**
- **Placas Mercosul**: Padrão atual de veículos
- **Sinais de trânsito**: Conforme CTB (Código de Trânsito Brasileiro)
- **Placas de rua**: Nomenclatura e padrões brasileiros
- **Placas de construção**: Padrões locais de segurança

## 🛠️ **Pré-requisitos**

### **1. Instalação de Dependências**
```bash
# Dependências principais
pip install ultralytics opencv-python numpy torch torchvision

# Dependências adicionais
pip install pillow matplotlib pandas requests

# Para GPU (recomendado)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### **2. Verificar GPU (Opcional)**
```bash
# Verificar se CUDA está disponível
python -c "import torch; print(f'CUDA disponível: {torch.cuda.is_available()}')"
python -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU\"}')"
```

## 📊 **Estrutura do Dataset**

### **Organização dos Diretórios**
```
datasets/
├── signal_plates/
│   ├── images/
│   │   ├── train/     # 70% das imagens
│   │   ├── val/       # 20% das imagens
│   │   └── test/      # 10% das imagens
│   └── labels/
│       ├── train/     # Anotações de treinamento
│       ├── val/       # Anotações de validação
│       └── test/      # Anotações de teste
└── vehicle_plates/
    ├── images/
    │   ├── train/
    │   ├── val/
    │   └── test/
    └── labels/
        ├── train/
        ├── val/
        └── test/
```

### **Formato das Anotações (YOLO)**
```
# Formato: class_id x_center y_center width height
# Todas as coordenadas são normalizadas (0-1)

0 0.5 0.5 0.3 0.2    # Classe 0, centro (0.5, 0.5), largura 0.3, altura 0.2
1 0.2 0.8 0.4 0.3    # Classe 1, centro (0.2, 0.8), largura 0.4, altura 0.3
```

## 🔍 **Coleta de Dados Brasileiros**

### **1. Coleta Automática**
```bash
# Criar estrutura de diretórios
python scripts/collect_brazilian_data.py --create-structure

# Coletar dados de múltiplas fontes
python scripts/collect_brazilian_data.py --source all --max-images 500

# Coletar apenas de fonte local
python scripts/collect_brazilian_data.py --source local --local-dir ./minhas_imagens

# Gerar anotações básicas
python scripts/collect_brazilian_data.py --generate-annotations
```

### **2. Fontes de Dados Recomendadas**

#### **🌐 Fontes Online:**
- **Google Images**: Busca por termos específicos brasileiros
- **Flickr**: Imagens com licenças Creative Commons
- **Instagram**: Hashtags relacionados a trânsito brasileiro
- **YouTube**: Frames de vídeos de trânsito

#### **📱 Fontes Locais:**
- **Fotos próprias**: Capturas de placas reais
- **Departamentos de trânsito**: Imagens oficiais
- **Empresas de engenharia**: Projetos de sinalização
- **Universidades**: Pesquisas acadêmicas

### **3. Termos de Busca Brasileiros**

#### **🚦 Placas de Sinalização:**
```bash
# Sinais de trânsito
"placa pare brasil"
"placa dê preferência brasil"
"placa limite velocidade brasil"
"placa proibido estacionar brasil"
"placa sentido único brasil"
"placa travessia pedestres brasil"
"placa zona escolar brasil"
"placa obras construção brasil"
"placa atenção cuidado brasil"
"placa informação brasil"
"placa nome rua brasil"
"placa prédio edifício brasil"
"semáforo trânsito brasil"
"placa passagem nível brasil"
"placa ciclovia brasil"
"placa faixa ônibus brasil"
```

#### **🚗 Placas de Veículos:**
```bash
# Tipos de placas
"placa mercosul brasil"
"placa moto mercosul brasil"
"placa padrão antigo brasil"
"placa diplomática brasil"
"placa oficial brasil"
"placa temporária brasil"
"placa comercial brasil"
"placa especial brasil"

# Tipos de veículos
"carro placa brasil"
"caminhão placa brasil"
"moto placa brasil"
"ônibus placa brasil"
"van placa brasil"
"trator placa brasil"
```

## ✏️ **Anotação dos Dados**

### **1. Ferramentas de Anotação**

#### **🖱️ LabelImg (Recomendado para iniciantes)**
```bash
# Instalação
pip install labelImg

# Execução
labelImg

# Configuração para YOLO
# View -> Auto Save Mode
# View -> Display Labels
# File -> Change Save Dir -> labels/
```

#### **🌐 CVAT (Online, colaborativo)**
- Acesso: https://cvat.org/
- Interface web moderna
- Suporte a múltiplos usuários
- Exportação para formato YOLO

#### **💻 Roboflow (Online, com IA)**
- Acesso: https://roboflow.com/
- Anotação automática com IA
- Pré-processamento de imagens
- Integração com YOLO

### **2. Processo de Anotação**

#### **📋 Checklist de Anotação:**
- [ ] **Bounding Box**: Caixa delimitadora precisa
- [ ] **Classe Correta**: ID da classe correspondente
- [ ] **Coordenadas Normalizadas**: Valores entre 0 e 1
- [ ] **Qualidade da Imagem**: Resolução adequada
- [ ] **Diversidade**: Diferentes ângulos e condições

#### **🎯 Dicas de Anotação:**
- **Consistência**: Use sempre o mesmo padrão
- **Precisão**: Bounding boxes devem ser justas
- **Validação**: Revise anotações regularmente
- **Documentação**: Mantenha registro das classes

## 🚀 **Preparação para Treinamento**

### **1. Preparar Dataset**
```bash
# Criar dataset de exemplo (para teste)
python scripts/prepare_training_data.py sample

# Preparar dataset real de sinalização
python scripts/prepare_training_data.py signal ./datasets/raw_brazilian/signal_plates

# Preparar dataset real de veículos
python scripts/prepare_training_data.py vehicle ./datasets/raw_brazilian/vehicle_plates
```

### **2. Verificar Estrutura**
```bash
# Verificar se os diretórios estão corretos
ls -la datasets/signal_plates/
ls -la datasets/vehicle_plates/

# Verificar se há imagens e anotações
find datasets/signal_plates/images/train -name "*.jpg" | wc -l
find datasets/signal_plates/labels/train -name "*.txt" | wc -l
```

## 🎓 **Treinamento dos Modelos**

### **1. Treinamento Básico**
```bash
# Treinar ambos os modelos
python scripts/train_yolo_models.py --model both

# Treinar apenas modelo de sinalização
python scripts/train_yolo_models.py --model signal

# Treinar apenas modelo de veículos
python scripts/train_yolo_models.py --model vehicle
```

### **2. Treinamento Personalizado**
```bash
# Configurações personalizadas
python scripts/train_yolo_models.py \
    --model both \
    --epochs 200 \
    --batch-size 32 \
    --device cuda

# Treinar com validação
python scripts/train_yolo_models.py \
    --model signal \
    --validate \
    --test-image ./test_image.jpg
```

### **3. Configurações de Treinamento**

#### **⚙️ Parâmetros Recomendados:**
```yaml
# Placas de Sinalização
epochs: 100
batch_size: 16
imgsz: 640
patience: 20
save_period: 10

# Placas de Veículos
epochs: 150
batch_size: 16
imgsz: 640
patience: 25
save_period: 15
```

#### **🖥️ Configurações por Hardware:**
```bash
# CPU (mais lento, mas funciona)
--device cpu --batch-size 8

# GPU (recomendado)
--device cuda --batch-size 16

# Múltiplas GPUs
--device 0,1 --batch-size 32
```

## 📈 **Monitoramento do Treinamento**

### **1. Métricas Importantes**
- **mAP50**: Precisão média a 50% IoU
- **mAP50-95**: Precisão média a múltiplos IoUs
- **Precision**: Precisão das detecções
- **Recall**: Taxa de detecção correta
- **Loss**: Perda de treinamento

### **2. Visualização dos Resultados**
```bash
# Abrir TensorBoard
tensorboard --logdir runs/

# Ver resultados no navegador
# http://localhost:6006
```

### **3. Detecção de Overfitting**
- **Training Loss**: Diminui continuamente
- **Validation Loss**: Para de diminuir ou aumenta
- **Gap**: Diferença entre training e validation
- **Solução**: Early stopping, data augmentation

## 🔧 **Otimizações e Fine-tuning**

### **1. Data Augmentation**
```python
# Configurações de aumento de dados
augmentation_config = {
    "hsv_h": 0.015,      # Variação de matiz
    "hsv_s": 0.7,        # Variação de saturação
    "hsv_v": 0.4,        # Variação de valor
    "degrees": 0.0,       # Rotação
    "translate": 0.1,     # Translação
    "scale": 0.5,         # Escala
    "shear": 0.0,         # Cisalhamento
    "perspective": 0.0,   # Perspectiva
    "flipud": 0.0,        # Flip vertical
    "fliplr": 0.5,        # Flip horizontal
    "mosaic": 1.0,        # Mosaico
    "mixup": 0.0,         # Mixup
    "copy_paste": 0.0     # Copy-paste
}
```

### **2. Transfer Learning**
```bash
# Usar modelo pré-treinado
--model yolov8n.pt

# Fine-tuning com learning rate baixo
--lr0 0.001 --lrf 0.01

# Congelar camadas iniciais
--freeze 10
```

### **3. Hyperparameter Tuning**
```bash
# Usar YOLO built-in tuning
yolo tune data=dataset.yaml model=yolov8n.pt epochs=100

# Ou tuning manual
for lr in [0.001, 0.01, 0.1]:
    for batch in [8, 16, 32]:
        python train.py --lr0 $lr --batch $batch
```

## 📊 **Avaliação dos Modelos**

### **1. Validação Automática**
```bash
# Validar modelo treinado
yolo val model=models/signal_plates_yolo.pt data=datasets/signal_plates/dataset.yaml

# Validar com imagens de teste
yolo val model=models/vehicle_plates_yolo.pt data=datasets/vehicle_plates/dataset.yaml
```

### **2. Teste Manual**
```bash
# Testar com imagem específica
python scripts/train_yolo_models.py \
    --validate \
    --test-image ./minha_placa.jpg
```

### **3. Métricas de Avaliação**
```python
# Exemplo de análise de resultados
import pandas as pd

results = pd.read_csv("runs/signal_plates/train/results.csv")

print(f"Melhor mAP50: {results['metrics/mAP50(B)'].max():.3f}")
print(f"Melhor mAP50-95: {results['metrics/mAP50-95(B)'].max():.3f}")
print(f"Menor loss: {results['train/box_loss'].min():.3f}")
```

## 🚀 **Deploy dos Modelos Treinados**

### **1. Salvar Modelo Final**
```bash
# O script salva automaticamente em:
models/signal_plates_yolo.pt
models/vehicle_plates_yolo.pt
```

### **2. Atualizar Configuração**
```json
{
  "yolo_models": {
    "signal_plates": {
      "model_path": "models/signal_plates_yolo.pt",
      "last_updated": "2025-08-29"
    },
    "vehicle_plates": {
      "model_path": "models/vehicle_plates_yolo.pt", 
      "last_updated": "2025-08-29"
    }
  }
}
```

### **3. Testar na API**
```bash
# Reiniciar sistema
docker-compose -f docker-compose.prod.yml restart

# Testar endpoints
curl -X POST "http://localhost:8000/api/v1/detect/signal-plates" \
  -H "Content-Type: application/json" \
  -d '{"image": "base64...", "confidence_threshold": 0.6}'
```

## 🐛 **Solução de Problemas**

### **1. Problemas Comuns**

#### **❌ Dataset muito pequeno**
```bash
# Soluções:
# - Coletar mais dados
# - Usar data augmentation
# - Transfer learning
# - Fine-tuning
```

#### **❌ Overfitting**
```bash
# Soluções:
# - Reduzir complexidade do modelo
# - Aumentar dados de validação
# - Early stopping
# - Regularização
```

#### **❌ Baixa precisão**
```bash
# Soluções:
# - Verificar qualidade das anotações
# - Aumentar dataset
# - Ajustar thresholds
# - Usar modelo maior
```

### **2. Logs e Debugging**
```bash
# Ver logs de treinamento
tail -f runs/signal_plates/train/train.log

# Ver configuração do dataset
cat datasets/signal_plates/dataset.yaml

# Ver anotações
head -5 datasets/signal_plates/labels/train/train_0000.txt
```

## 📚 **Recursos Adicionais**

### **1. Documentação Oficial**
- [Ultralytics YOLO](https://docs.ultralytics.com/)
- [YOLO v8 Guide](https://docs.ultralytics.com/models/yolo/)
- [Training Guide](https://docs.ultralytics.com/modes/train/)

### **2. Datasets Brasileiros**
- [Open Images Brasil](https://storage.googleapis.com/openimages/web/index.html)
- [Kaggle Brazilian Traffic Signs](https://www.kaggle.com/datasets)
- [GitHub Brazilian Datasets](https://github.com/topics/brazilian-dataset)

### **3. Ferramentas de Anotação**
- [LabelImg](https://github.com/tzutalin/labelImg)
- [CVAT](https://cvat.org/)
- [Roboflow](https://roboflow.com/)
- [VGG Image Annotator](http://www.robots.ox.ac.uk/~vgg/software/via/)

## 🎯 **Próximos Passos**

### **1. Fase Atual** ✅
- [x] Estrutura da arquitetura
- [x] Scripts de preparação
- [x] Scripts de treinamento
- [x] Coleta de dados brasileiros

### **2. Fase Próxima** 🚧
- [ ] Coletar dataset real brasileiro
- [ ] Anotar dados com precisão
- [ ] Treinar modelos iniciais
- [ ] Validar performance

### **3. Fase Futura** 📋
- [ ] Fine-tuning com dados específicos
- [ ] Otimização de hiperparâmetros
- [ ] Teste em cenários reais
- [ ] Deploy em produção

## 🤝 **Suporte e Comunidade**

### **📧 Contato**
- **Issues**: GitHub Issues do projeto
- **Discussões**: GitHub Discussions
- **Wiki**: Documentação colaborativa

### **💡 Contribuições**
- **Datasets**: Compartilhar dados brasileiros
- **Anotações**: Ajudar com labeling
- **Testes**: Validar modelos em cenários reais
- **Documentação**: Melhorar este guia

---

**🎉 Parabéns! Você está pronto para treinar modelos YOLO especializados para o Brasil!**

**Lembre-se**: A qualidade dos dados é fundamental para o sucesso do treinamento. Invista tempo na coleta e anotação de dados brasileiros de qualidade!
