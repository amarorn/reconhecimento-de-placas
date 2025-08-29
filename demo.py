#!/usr/bin/env python3
"""
Demonstração Interativa - Aplicação de Reconhecimento de Placas
===============================================================

Este script demonstra todas as funcionalidades da aplicação
de forma interativa e visual.
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from plate_recognition_simple import SimplePlateRecognizer
import os
import time

def print_menu():
    """Imprime o menu principal"""
    print("\n" + "="*60)
    print("🚗 APLICAÇÃO DE RECONHECIMENTO DE PLACAS")
    print("="*60)
    print("1. 🔍 Processar imagem única")
    print("2. 📁 Processar pasta de imagens")
    print("3. 📸 Criar imagens de teste")
    print("4. 🎥 Modo webcam (simulado)")
    print("5. 📊 Mostrar estatísticas")
    print("6. 🧪 Executar testes")
    print("0. ❌ Sair")
    print("="*60)

def process_single_image():
    """Processa uma imagem única"""
    print("\n🔍 PROCESSAMENTO DE IMAGEM ÚNICA")
    print("-" * 40)
    
    # Listar imagens disponíveis
    image_files = [f for f in os.listdir('.') if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    if not image_files:
        print("❌ Nenhuma imagem encontrada no diretório atual")
        return
    
    print("📁 Imagens disponíveis:")
    for i, img in enumerate(image_files):
        print(f"   {i+1}. {img}")
    
    try:
        choice = int(input("\nEscolha uma imagem (número): ")) - 1
        if 0 <= choice < len(image_files):
            selected_image = image_files[choice]
            print(f"\n✅ Processando: {selected_image}")
            
            # Processar imagem
            recognizer = SimplePlateRecognizer()
            results = recognizer.process_image(selected_image)
            
            print(f"\n🎯 Resultados:")
            print(f"   Imagem: {selected_image}")
            print(f"   Regiões detectadas: {results['total_regions']}")
            print(f"   Placas encontradas: {len(results['plates_found'])}")
            
        else:
            print("❌ Escolha inválida!")
    except ValueError:
        print("❌ Entrada inválida!")

def process_folder():
    """Processa uma pasta de imagens"""
    print("\n📁 PROCESSAMENTO EM LOTE")
    print("-" * 40)
    
    # Listar diretórios
    directories = [d for d in os.listdir('.') if os.path.isdir(d)]
    print("📁 Diretórios disponíveis:")
    for i, dir_name in enumerate(directories):
        print(f"   {i+1}. {dir_name}/")
    
    try:
        choice = int(input("\nEscolha um diretório (número): ")) - 1
        if 0 <= choice < len(directories):
            selected_dir = directories[choice]
            print(f"\n✅ Processando diretório: {selected_dir}")
            
            # Processar pasta
            recognizer = SimplePlateRecognizer()
            results = recognizer.batch_process(selected_dir)
            
            total_plates = sum(len(r['plates_found']) for r in results)
            print(f"\n📊 Resumo do processamento:")
            print(f"   Diretório: {selected_dir}")
            print(f"   Imagens processadas: {len(results)}")
            print(f"   Total de placas encontradas: {total_plates}")
            
        else:
            print("❌ Escolha inválida!")
    except ValueError:
        print("❌ Entrada inválida!")

def create_test_images():
    """Cria imagens de teste"""
    print("\n📸 CRIAÇÃO DE IMAGENS DE TESTE")
    print("-" * 40)
    
    # Placas de exemplo
    test_plates = [
        "ABC1234",  # Padrão brasileiro antigo
        "XYZ1A23",  # Padrão brasileiro novo
        "DEF5678",  # Padrão brasileiro antigo
        "GHI9B01",  # Padrão brasileiro novo
        "JKL2C45",  # Padrão brasileiro novo
        "MNO6789"   # Padrão brasileiro antigo
    ]
    
    print("🔧 Criando imagens de teste...")
    recognizer = SimplePlateRecognizer()
    
    created_images = []
    for plate in test_plates:
        filename = recognizer.create_test_image(plate)
        created_images.append(filename)
        print(f"   ✅ Criada: {filename}")
    
    print(f"\n🎯 Total de imagens criadas: {len(created_images)}")
    print("💡 Use a opção 2 para processar a pasta 'exemplo_imagens'")

def webcam_simulation():
    """Simula o modo webcam"""
    print("\n🎥 MODO WEBCAM (SIMULAÇÃO)")
    print("-" * 40)
    print("⚠️  Esta é uma simulação do modo webcam")
    print("   Em uma implementação real, seria usado:")
    print("   - cv2.VideoCapture(0) para acessar a câmera")
    print("   - Processamento de frames em tempo real")
    print("   - Detecção contínua de placas")
    
    print("\n🔧 Criando frame simulado...")
    
    # Criar frame simulado
    frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
    
    # Adicionar elementos simulados
    cv2.rectangle(frame, (100, 200), (300, 250), (128, 128, 128), -1)
    cv2.putText(frame, "ABC1234", (120, 230), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    # Adicionar texto de status
    cv2.putText(frame, "WEBCAM SIMULADA", (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(frame, "Placa detectada: ABC1234", (50, 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    # Salvar frame
    cv2.imwrite("webcam_simulada.jpg", frame)
    print("   ✅ Frame salvo: webcam_simulada.jpg")
    
    # Mostrar frame
    plt.figure(figsize=(12, 8))
    plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    plt.title("Modo Webcam Simulado")
    plt.axis('off')
    plt.show()

def show_statistics():
    """Mostra estatísticas do sistema"""
    print("\n📊 ESTATÍSTICAS DO SISTEMA")
    print("-" * 40)
    
    # Contar arquivos
    image_files = [f for f in os.listdir('.') if f.endswith(('.jpg', '.jpeg', '.png'))]
    test_images = [f for f in image_files if f.startswith('teste_placa_')]
    
    print(f"📸 Total de imagens: {len(image_files)}")
    print(f"🧪 Imagens de teste: {len(test_images)}")
    print(f"📁 Diretórios: {len([d for d in os.listdir('.') if os.path.isdir(d)])}")
    
    # Mostrar imagens de teste
    if test_images:
        print(f"\n📋 Imagens de teste disponíveis:")
        for img in test_images:
            print(f"   • {img}")
    
    # Mostrar outras imagens
    other_images = [f for f in image_files if not f.startswith('teste_placa_')]
    if other_images:
        print(f"\n🖼️  Outras imagens:")
        for img in other_images:
            print(f"   • {img}")

def run_tests():
    """Executa testes básicos"""
    print("\n🧪 EXECUTANDO TESTES")
    print("-" * 40)
    
    try:
        # Testar import das bibliotecas
        print("🔍 Testando import das bibliotecas...")
        import cv2
        print("   ✅ OpenCV importado")
        
        import numpy as np
        print("   ✅ NumPy importado")
        
        import matplotlib.pyplot as plt
        print("   ✅ Matplotlib importado")
        
        # Testar criação do reconhecedor
        print("\n🔧 Testando criação do reconhecedor...")
        recognizer = SimplePlateRecognizer()
        print("   ✅ Reconhecedor criado")
        
        # Testar criação de imagem
        print("\n📸 Testando criação de imagem...")
        test_img = recognizer.create_test_image("TEST123")
        print(f"   ✅ Imagem criada: {test_img}")
        
        # Testar processamento
        print("\n🔍 Testando processamento...")
        results = recognizer.process_image(test_img, show_results=False)
        print(f"   ✅ Processamento concluído")
        print(f"   📊 Resultados: {len(results['plates_found'])} placas encontradas")
        
        print("\n✅ Todos os testes passaram!")
        
    except Exception as e:
        print(f"❌ Erro nos testes: {e}")

def main():
    """Função principal"""
    print("🚗 BEM-VINDO À APLICAÇÃO DE RECONHECIMENTO DE PLACAS!")
    print("   Versão de Demonstração - Funcionalidades Completas")
    
    while True:
        print_menu()
        
        try:
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == '1':
                process_single_image()
            elif choice == '2':
                process_folder()
            elif choice == '3':
                create_test_images()
            elif choice == '4':
                webcam_simulation()
            elif choice == '5':
                show_statistics()
            elif choice == '6':
                run_tests()
            elif choice == '0':
                print("\n👋 Obrigado por usar a aplicação!")
                print("   Até logo! 🚗")
                break
            else:
                print("❌ Opção inválida! Escolha de 0 a 6.")
            
            input("\nPressione Enter para continuar...")
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Aplicação interrompida pelo usuário")
            break
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
            input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()
