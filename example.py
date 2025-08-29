#!/usr/bin/env python3
"""
Exemplo de Uso da Aplicação de Reconhecimento de Placas
=======================================================

Este arquivo demonstra como usar a classe PlateRecognizer
para diferentes cenários de reconhecimento de placas.
"""

from plate_recognition import PlateRecognizer
import cv2
import numpy as np

def example_basic_usage():
    """Exemplo básico de uso"""
    print("=== EXEMPLO BÁSICO ===")
    
    # Criar instância do reconhecedor
    recognizer = PlateRecognizer()
    
    # Exemplo com uma imagem (substitua pelo caminho real)
    # image_path = "exemplo_placa.jpg"
    # results = recognizer.process_image(image_path)
    
    print("Reconhecedor inicializado com sucesso!")
    print("Use: recognizer.process_image('caminho/para/imagem.jpg')")

def example_custom_processing():
    """Exemplo de processamento customizado"""
    print("\n=== EXEMPLO CUSTOMIZADO ===")
    
    recognizer = PlateRecognizer()
    
    # Criar uma imagem de exemplo (placa fictícia)
    # Em um caso real, você carregaria uma imagem real
    example_image = np.zeros((200, 400, 3), dtype=np.uint8)
    example_image[:] = (255, 255, 255)  # Fundo branco
    
    # Adicionar texto de exemplo (simulando uma placa)
    cv2.putText(example_image, "ABC1234", (50, 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
    
    # Salvar imagem de exemplo
    cv2.imwrite("exemplo_placa.jpg", example_image)
    print("Imagem de exemplo criada: exemplo_placa.jpg")
    
    # Processar a imagem
    try:
        results = recognizer.process_image("exemplo_placa.jpg")
        print(f"Resultados: {results}")
    except Exception as e:
        print(f"Erro ao processar: {e}")

def example_batch_processing():
    """Exemplo de processamento em lote"""
    print("\n=== EXEMPLO DE PROCESSAMENTO EM LOTE ===")
    
    recognizer = PlateRecognizer()
    
    # Criar pasta de exemplo com algumas imagens
    import os
    if not os.path.exists("exemplo_imagens"):
        os.makedirs("exemplo_imagens")
    
    # Criar algumas imagens de exemplo
    for i in range(3):
        img = np.zeros((200, 400, 3), dtype=np.uint8)
        img[:] = (255, 255, 255)
        
        # Texto diferente para cada imagem
        plate_text = f"XYZ{i+1}234"
        cv2.putText(img, plate_text, (50, 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
        
        cv2.imwrite(f"exemplo_imagens/placa_{i+1}.jpg", img)
    
    print("Pasta de exemplo criada: exemplo_imagens/")
    print("Use: recognizer.batch_process('exemplo_imagens')")

def example_advanced_features():
    """Exemplo de recursos avançados"""
    print("\n=== RECURSOS AVANÇADOS ===")
    
    recognizer = PlateRecognizer()
    
    print("Recursos disponíveis:")
    print("1. Pré-processamento de imagem")
    print("2. Detecção de regiões de placas")
    print("3. Extração de imagens de placas")
    print("4. Reconhecimento de texto com OCR")
    print("5. Visualização de resultados")
    print("6. Processamento em lote")
    
    print("\nPara usar recursos específicos:")
    print("- recognizer.preprocess_image(imagem)")
    print("- recognizer.detect_plate_regions(imagem_processada)")
    print("- recognizer.extract_plate_image(imagem, contorno)")
    print("- recognizer.recognize_plate_text(imagem_placa)")

if __name__ == "__main__":
    print("🚗 EXEMPLOS DE USO - RECONHECIMENTO DE PLACAS")
    print("=" * 50)
    
    example_basic_usage()
    example_custom_processing()
    example_batch_processing()
    example_advanced_features()
    
    print("\n" + "=" * 50)
    print("✅ Todos os exemplos foram executados!")
    print("\nPara usar a aplicação completa:")
    print("python main.py --image exemplo_placa.jpg")
    print("python main.py --folder exemplo_imagens/")
    print("python main.py --webcam")
