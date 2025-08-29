#!/usr/bin/env python3
"""
Criador de Imagens de Teste para Sistema MBST
=============================================

Este script cria imagens de teste para validar o sistema de visão computacional
"""

import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
from pathlib import Path

def create_test_images():
    """Cria imagens de teste para o sistema MBST"""
    
    # Criar diretório de imagens de teste
    test_dir = Path("sinalizacao_test")
    test_dir.mkdir(exist_ok=True)
    
    print(f"📁 Criando imagens de teste em: {test_dir}")
    
    # Configurações das imagens
    width, height = 800, 600
    background_color = (240, 240, 240)  # Cinza claro
    
    # Tipos de placas para criar
    test_plates = [
        {
            "name": "placa_pare.jpg",
            "text": "PARE",
            "color": (255, 0, 0),  # Vermelho
            "shape": "octogonal",
            "type": "regulamentacao"
        },
        {
            "name": "placa_dê_preferencia.jpg",
            "text": "DÊ A\nPREFERÊNCIA",
            "color": (255, 0, 0),  # Vermelho
            "shape": "octogonal",
            "type": "regulamentacao"
        },
        {
            "name": "placa_cruzamento.jpg",
            "text": "CRUZAMENTO",
            "color": (255, 255, 0),  # Amarelo
            "shape": "triangular",
            "type": "advertencia"
        },
        {
            "name": "placa_curva.jpg",
            "text": "CURVA\nPERIGOSA",
            "color": (255, 255, 0),  # Amarelo
            "shape": "triangular",
            "type": "advertencia"
        },
        {
            "name": "placa_hospital.jpg",
            "text": "HOSPITAL",
            "color": (0, 0, 255),  # Azul
            "shape": "retangular",
            "type": "informacao"
        },
        {
            "name": "placa_escola.jpg",
            "text": "ESCOLA",
            "color": (0, 0, 255),  # Azul
            "shape": "retangular",
            "type": "informacao"
        }
    ]
    
    created_images = []
    
    for plate_info in test_plates:
        try:
            # Criar imagem base
            img = Image.new('RGB', (width, height), background_color)
            draw = ImageDraw.Draw(img)
            
            # Determinar posição e tamanho da placa
            if plate_info["shape"] == "octogonal":
                # Placa octogonal (regulamentação)
                plate_size = 200
                center_x, center_y = width // 2, height // 2
                points = create_octagon(center_x, center_y, plate_size)
                
            elif plate_info["shape"] == "triangular":
                # Placa triangular (advertência)
                plate_size = 200
                center_x, center_y = width // 2, height // 2
                points = create_triangle(center_x, center_y, plate_size)
                
            else:
                # Placa retangular (informação)
                plate_size = 300
                center_x, center_y = width // 2, height // 2
                points = create_rectangle(center_x, center_y, plate_size)
            
            # Desenhar placa
            draw.polygon(points, fill=plate_info["color"], outline=(0, 0, 0), width=3)
            
            # Adicionar texto
            text = plate_info["text"]
            lines = text.split('\n')
            
            # Calcular posição do texto
            bbox = draw.textbbox((0, 0), text, font=None)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Tentar usar fonte do sistema
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 36)
            except:
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
                except:
                    font = ImageFont.load_default()
            
            # Desenhar texto centralizado
            for i, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                line_height = bbox[3] - bbox[1]
                
                x = center_x - line_width // 2
                y = center_y - (len(lines) * line_height) // 2 + i * line_height
                
                # Desenhar texto com contorno para melhor visibilidade
                draw.text((x, y), line, fill=(255, 255, 255), font=font)
            
            # Adicionar informações de teste
            info_text = f"Tipo: {plate_info['type']}"
            draw.text((10, 10), info_text, fill=(0, 0, 0), font=font)
            
            # Salvar imagem
            image_path = test_dir / plate_info["name"]
            img.save(image_path, "JPEG", quality=95)
            
            created_images.append(str(image_path))
            print(f"✅ Criada: {plate_info['name']} ({plate_info['type']})")
            
        except Exception as e:
            print(f"❌ Erro ao criar {plate_info['name']}: {e}")
    
    # Criar arquivo de metadados
    metadata = {
        "total_images": len(created_images),
        "images": created_images,
        "types": {
            "regulamentacao": len([p for p in test_plates if p["type"] == "regulamentacao"]),
            "advertencia": len([p for p in test_plates if p["type"] == "advertencia"]),
            "informacao": len([p for p in test_plates if p["type"] == "informacao"])
        }
    }
    
    metadata_file = test_dir / "metadata.json"
    import json
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 Criação concluída!")
    print(f"📊 Total de imagens: {len(created_images)}")
    print(f"📁 Pasta: {test_dir}")
    print(f"📋 Metadados: {metadata_file}")
    
    return test_dir

def create_octagon(center_x, center_y, size):
    """Cria pontos para um octógono"""
    points = []
    for i in range(8):
        angle = i * 45 * np.pi / 180
        x = center_x + size * np.cos(angle)
        y = center_y + size * np.sin(angle)
        points.append((x, y))
    return points

def create_triangle(center_x, center_y, size):
    """Cria pontos para um triângulo"""
    points = [
        (center_x, center_y - size // 2),
        (center_x - size // 2, center_y + size // 2),
        (center_x + size // 2, center_y + size // 2)
    ]
    return points

def create_rectangle(center_x, center_y, size):
    """Cria pontos para um retângulo"""
    half_width = size // 2
    half_height = size // 4
    points = [
        (center_x - half_width, center_y - half_height),
        (center_x + half_width, center_y - half_height),
        (center_x + half_width, center_y + half_height),
        (center_x - half_width, center_y + half_height)
    ]
    return points

if __name__ == "__main__":
    test_dir = create_test_images()
    print(f"\n🚀 Agora você pode testar o sistema com:")
    print(f"python3 advanced_vision_system.py {test_dir}")
