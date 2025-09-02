#!/usr/bin/env python3
"""
Script para extrair imagens de PDF e preparar dataset para treinamento YOLO
"""

import os
import sys
import fitz  # PyMuPDF
from PIL import Image
import io
import shutil
from pathlib import Path
import yaml

def extract_images_from_pdf(pdf_path, output_dir):
    """Extrai imagens de um PDF"""
    print(f"📄 Extraindo imagens do PDF: {pdf_path}")
    
    # Criar diretório de saída
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Abrir PDF
        pdf_document = fitz.open(pdf_path)
        image_count = 0
        
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                # Obter referência da imagem
                xref = img[0]
                pix = fitz.Pixmap(pdf_document, xref)
                
                # Converter para PNG se necessário
                if pix.n - pix.alpha < 4:  # GRAY ou RGB
                    img_data = pix.tobytes("png")
                else:  # CMYK: converter para RGB primeiro
                    pix1 = fitz.Pixmap(fitz.csRGB, pix)
                    img_data = pix1.tobytes("png")
                    pix1 = None
                
                # Salvar imagem
                img_filename = f"page_{page_num+1}_img_{img_index+1}.png"
                img_path = os.path.join(output_dir, img_filename)
                
                with open(img_path, "wb") as img_file:
                    img_file.write(img_data)
                
                image_count += 1
                print(f"  ✅ Imagem salva: {img_filename}")
                
                pix = None
        
        pdf_document.close()
        print(f"🎉 Total de {image_count} imagens extraídas!")
        return image_count
        
    except Exception as e:
        print(f"❌ Erro ao extrair imagens do PDF: {e}")
        return 0

def create_yolo_dataset_structure(images_dir, dataset_name):
    """Cria estrutura de dataset YOLO"""
    print(f"📁 Criando estrutura de dataset: {dataset_name}")
    
    # Diretórios do dataset
    dataset_dir = f"datasets/{dataset_name}"
    train_dir = f"{dataset_dir}/images/train"
    val_dir = f"{dataset_dir}/images/val"
    train_labels_dir = f"{dataset_dir}/labels/train"
    val_labels_dir = f"{dataset_dir}/labels/val"
    
    # Criar diretórios
    for dir_path in [train_dir, val_dir, train_labels_dir, val_labels_dir]:
        os.makedirs(dir_path, exist_ok=True)
    
    # Mover imagens para treino (80%) e validação (20%)
    images = [f for f in os.listdir(images_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    train_count = int(len(images) * 0.8)
    val_count = len(images) - train_count
    
    print(f"  📊 Distribuição: {train_count} treino, {val_count} validação")
    
    # Mover imagens para treino
    for i, img in enumerate(images[:train_count]):
        src = os.path.join(images_dir, img)
        dst = os.path.join(train_dir, img)
        shutil.copy2(src, dst)
    
    # Mover imagens para validação
    for i, img in enumerate(images[train_count:]):
        src = os.path.join(images_dir, img)
        dst = os.path.join(val_dir, img)
        shutil.copy2(src, dst)
    
    # Criar arquivos de labels vazios (para serem preenchidos manualmente)
    for img in images[:train_count]:
        label_file = os.path.splitext(img)[0] + '.txt'
        with open(os.path.join(train_labels_dir, label_file), 'w') as f:
            f.write('')  # Arquivo vazio para ser preenchido
    
    for img in images[train_count:]:
        label_file = os.path.splitext(img)[0] + '.txt'
        with open(os.path.join(val_labels_dir, label_file), 'w') as f:
            f.write('')  # Arquivo vazio para ser preenchido
    
    # Criar dataset.yaml
    dataset_yaml = {
        'path': f'datasets/{dataset_name}',
        'train': 'images/train',
        'val': 'images/val',
        'test': 'images/test',
        'nc': 16,  # Número de classes
        'names': [
            'stop_sign',
            'yield_sign', 
            'speed_limit',
            'no_parking',
            'one_way',
            'pedestrian_crossing',
            'school_zone',
            'construction',
            'warning',
            'information',
            'street_sign',
            'building_sign',
            'traffic_light',
            'railroad_crossing',
            'bicycle_lane',
            'bus_lane'
        ]
    }
    
    yaml_path = f"{dataset_dir}/dataset.yaml"
    with open(yaml_path, 'w') as f:
        yaml.dump(dataset_yaml, f, default_flow_style=False)
    
    print(f"✅ Dataset criado em: {dataset_dir}")
    print(f"📝 Arquivo de configuração: {yaml_path}")
    
    return dataset_dir

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("❌ Uso: python extract_pdf_images.py <caminho_do_pdf> [nome_do_dataset]")
        print("   Exemplo: python extract_pdf_images.py placas.pdf signal_plates_pdf")
        return False
    
    pdf_path = sys.argv[1]
    dataset_name = sys.argv[2] if len(sys.argv) > 2 else "signal_plates_pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ Arquivo PDF não encontrado: {pdf_path}")
        return False
    
    # Extrair imagens do PDF
    temp_dir = f"temp_pdf_images_{dataset_name}"
    image_count = extract_images_from_pdf(pdf_path, temp_dir)
    
    if image_count == 0:
        print("❌ Nenhuma imagem foi extraída do PDF")
        return False
    
    # Criar estrutura de dataset YOLO
    dataset_dir = create_yolo_dataset_structure(temp_dir, dataset_name)
    
    # Limpar diretório temporário
    shutil.rmtree(temp_dir)
    
    print(f"\n🎉 Processo concluído!")
    print(f"📁 Dataset criado em: {dataset_dir}")
    print(f"📝 Próximos passos:")
    print(f"   1. Anotar as imagens usando ferramentas como LabelImg ou Roboflow")
    print(f"   2. Treinar o modelo com: python scripts/train_yolo_model.py {dataset_name}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
