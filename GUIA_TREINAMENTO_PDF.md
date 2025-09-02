# 📄 Guia: Treinamento com PDF

## 🎯 Como treinar o modelo YOLO com imagens de PDF

### 📋 Pré-requisitos
- PDF com imagens de placas de sinalização
- Python 3.9+ com dependências instaladas

### 🚀 Passo a Passo

#### 1. **Preparar o PDF**
- Coloque seu PDF na pasta raiz do projeto
- Certifique-se de que o PDF contém imagens de placas de sinalização

#### 2. **Extrair Imagens do PDF**
```bash
# Extrair imagens do PDF
python3 scripts/extract_pdf_images.py seu_arquivo.pdf nome_do_dataset

# Exemplo:
python3 scripts/extract_pdf_images.py placas_sinalizacao.pdf signal_plates_pdf
```

#### 3. **Anotar as Imagens** (IMPORTANTE!)
Após extrair as imagens, você precisa anotá-las:

**Opção A: Usar LabelImg (Recomendado)**
```bash
# Instalar LabelImg
pip install labelimg

# Executar LabelImg
labelimg datasets/signal_plates_pdf/images/train/
```

**Opção B: Usar Roboflow (Online)**
1. Acesse: https://roboflow.com
2. Crie um projeto
3. Faça upload das imagens
4. Anote as placas
5. Exporte no formato YOLO

#### 4. **Treinar o Modelo**
```bash
# Treinar com dataset anotado
python3 scripts/train_yolo_model.py signal_plates_pdf 50 16

# Parâmetros:
# - signal_plates_pdf: nome do dataset
# - 50: número de epochs
# - 16: batch size
```

#### 5. **Atualizar o Sistema**
Após o treinamento, atualize os caminhos dos modelos:

**Em `vision/detection/signal_plate_detector.py`:**
```python
self.model_path = config.get('model_path', 'models/signal_plates_pdf_yolo.pt')
```

**Em `vision/detection/vehicle_plate_detector.py`:**
```python
self.model_path = config.get('model_path', 'models/vehicle_plates_pdf_yolo.pt')
```

### 📊 Estrutura do Dataset

```
datasets/signal_plates_pdf/
├── images/
│   ├── train/          # 80% das imagens
│   └── val/            # 20% das imagens
├── labels/
│   ├── train/          # Labels de treino (.txt)
│   └── val/            # Labels de validação (.txt)
└── dataset.yaml        # Configuração do dataset
```

### 🏷️ Formato dos Labels

Cada arquivo `.txt` deve conter uma linha por objeto:
```
class_id center_x center_y width height
```

**Exemplo:**
```
2 0.5 0.5 0.3 0.4
```
- `2`: ID da classe (speed_limit)
- `0.5 0.5`: Centro da bounding box (normalizado)
- `0.3 0.4`: Largura e altura (normalizadas)

### 📝 Classes Disponíveis

```yaml
0: stop_sign
1: yield_sign
2: speed_limit
3: no_parking
4: one_way
5: pedestrian_crossing
6: school_zone
7: construction
8: warning
9: information
10: street_sign
11: building_sign
12: traffic_light
13: railroad_crossing
14: bicycle_lane
15: bus_lane
```

### 🔧 Comandos Úteis

```bash
# Verificar estrutura do dataset
ls -la datasets/signal_plates_pdf/

# Contar imagens
find datasets/signal_plates_pdf/images/train -name "*.jpg" | wc -l
find datasets/signal_plates_pdf/images/val -name "*.jpg" | wc -l

# Verificar labels
find datasets/signal_plates_pdf/labels/train -name "*.txt" | wc -l
```

### ⚠️ Dicas Importantes

1. **Qualidade das Imagens**: Use imagens de alta qualidade
2. **Diversidade**: Inclua diferentes tipos de placas
3. **Anotações Precisas**: Seja preciso nas bounding boxes
4. **Balanceamento**: Tente ter exemplos de todas as classes
5. **Validação**: Use 20% das imagens para validação

### 🎉 Resultado Esperado

Após o treinamento, você terá:
- Modelo treinado: `models/signal_plates_pdf_yolo.pt`
- Métricas de performance
- Gráficos de treinamento
- Sistema funcionando com detecção real

### 🆘 Solução de Problemas

**Erro: "No such file or directory"**
- Verifique se o PDF existe
- Confirme o caminho correto

**Erro: "Dataset not found"**
- Execute primeiro o script de extração
- Verifique a estrutura de diretórios

**Modelo não detecta nada**
- Verifique as anotações
- Ajuste o threshold de confiança
- Treine por mais epochs

### 📞 Suporte

Se encontrar problemas:
1. Verifique os logs de treinamento
2. Confirme a estrutura do dataset
3. Teste com threshold baixo (0.1)
4. Verifique as anotações
