#!/usr/bin/env python3
"""
Demonstração Simples - Reconhecimento de Placas
===============================================

Versão simplificada que funciona sem matplotlib
e mostra resultados no terminal.
"""

import cv2
import numpy as np
import os
from plate_recognition_simple import SimplePlateRecognizer

def show_image_info(image_path):
    """Mostra informações básicas da imagem"""
    if os.path.exists(image_path):
        image = cv2.imread(image_path)
        if image is not None:
            height, width = image.shape[:2]
            print(f"   📏 Dimensões: {width}x{height} pixels")
            print(f"   💾 Tamanho: {os.path.getsize(image_path)} bytes")
            return True
    return False

def process_image_simple(image_path):
    """Processa imagem sem mostrar gráficos"""
    print(f"\n🔍 Processando: {image_path}")
    
    try:
        recognizer = SimplePlateRecognizer()
        
        # Processar sem mostrar resultados visuais
        results = recognizer.process_image(image_path, show_results=False)
        
        print(f"✅ Processamento concluído!")
        print(f"📊 Resultados:")
        print(f"   • Regiões candidatas: {results['total_regions']}")
        print(f"   • Placas encontradas: {len(results['plates_found'])}")
        
        if results['plates_found']:
            for i, plate in enumerate(results['plates_found']):
                print(f"   • Placa {i+1}: {plate['text']} (Confiança: {plate['confidence']:.2f})")
        else:
            print("   • Nenhuma placa foi detectada")
            
        return results
        
    except Exception as e:
        print(f"❌ Erro ao processar: {e}")
        return None

def create_test_images():
    """Cria imagens de teste"""
    print("\n📸 CRIANDO IMAGENS DE TESTE")
    print("-" * 40)
    
    test_plates = ["ABC1234", "XYZ1A23", "DEF5678", "GHI9B01"]
    
    recognizer = SimplePlateRecognizer()
    created_images = []
    
    for plate in test_plates:
        filename = recognizer.create_test_image(plate)
        created_images.append(filename)
        print(f"   ✅ Criada: {filename}")
    
    print(f"\n🎯 Total criado: {len(created_images)} imagens")
    return created_images

def list_images():
    """Lista todas as imagens disponíveis"""
    print("\n📁 IMAGENS DISPONÍVEIS")
    print("-" * 40)
    
    image_files = [f for f in os.listdir('.') if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    if not image_files:
        print("❌ Nenhuma imagem encontrada")
        return []
    
    for i, img in enumerate(image_files, 1):
        print(f"{i:2d}. {img}")
        show_image_info(img)
    
    return image_files

def batch_process_simple():
    """Processa todas as imagens em lote"""
    print("\n📁 PROCESSAMENTO EM LOTE")
    print("-" * 40)
    
    image_files = [f for f in os.listdir('.') if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    if not image_files:
        print("❌ Nenhuma imagem encontrada para processar")
        return
    
    print(f"🔍 Processando {len(image_files)} imagens...")
    
    recognizer = SimplePlateRecognizer()
    total_plates = 0
    
    for i, image_file in enumerate(image_files, 1):
        print(f"\n[{i}/{len(image_files)}] Processando: {image_file}")
        
        try:
            results = recognizer.process_image(image_file, show_results=False)
            plates_found = len(results['plates_found'])
            total_plates += plates_found
            
            print(f"   ✅ Concluído: {plates_found} placa(s) encontrada(s)")
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    print(f"\n🎯 RESUMO DO PROCESSAMENTO")
    print(f"   • Imagens processadas: {len(image_files)}")
    print(f"   • Total de placas encontradas: {total_plates}")

def main():
    """Função principal"""
    print("🚗 APLICAÇÃO DE RECONHECIMENTO DE PLACAS")
    print("   Versão Simplificada - Sem Interface Gráfica")
    print("=" * 50)
    
    while True:
        print("\n📋 MENU PRINCIPAL")
        print("1. 📸 Criar imagens de teste")
        print("2. 📁 Listar imagens disponíveis")
        print("3. 🔍 Processar imagem específica")
        print("4. 📊 Processar todas as imagens")
        print("5. 🧪 Executar teste rápido")
        print("0. ❌ Sair")
        print("-" * 30)
        
        try:
            choice = input("Escolha uma opção: ").strip()
            
            if choice == '1':
                create_test_images()
                
            elif choice == '2':
                list_images()
                
            elif choice == '3':
                images = [f for f in os.listdir('.') if f.endswith(('.jpg', '.jpeg', '.png'))]
                if not images:
                    print("❌ Nenhuma imagem disponível. Crie algumas primeiro (opção 1).")
                    continue
                
                print("\n📁 Imagens disponíveis:")
                for i, img in enumerate(images, 1):
                    print(f"   {i}. {img}")
                
                try:
                    img_choice = int(input("\nEscolha uma imagem (número): ")) - 1
                    if 0 <= img_choice < len(images):
                        selected_image = images[img_choice]
                        process_image_simple(selected_image)
                    else:
                        print("❌ Escolha inválida!")
                except ValueError:
                    print("❌ Entrada inválida!")
                    
            elif choice == '4':
                batch_process_simple()
                
            elif choice == '5':
                print("\n🧪 TESTE RÁPIDO")
                print("-" * 20)
                
                # Criar uma imagem de teste
                recognizer = SimplePlateRecognizer()
                test_img = recognizer.create_test_image("TEST123")
                print(f"✅ Imagem criada: {test_img}")
                
                # Processar
                results = recognizer.process_image(test_img, show_results=False)
                print(f"✅ Processamento: {len(results['plates_found'])} placas encontradas")
                
            elif choice == '0':
                print("\n👋 Obrigado por usar a aplicação!")
                break
                
            else:
                print("❌ Opção inválida! Escolha de 0 a 5.")
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Aplicação interrompida")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
        
        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()
