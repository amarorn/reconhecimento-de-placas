

import cv2
import numpy as np
from pathlib import Path

def test_image(image_path):
    try:
        img = cv2.imread(str(image_path))
        if img is None:
            print(f"❌ Erro: Não foi possível abrir {image_path}")
            return False
        
        print(f"✅ Imagem aberta com sucesso: {image_path}")
        print(f"   Dimensões: {img.shape}")
        print(f"   Tipo: {img.dtype}")
        print(f"   Valor médio: {np.mean(img):.1f}")
        
        if np.mean(img) < 10:
            print(f"⚠️  Aviso: Imagem muito escura (média: {np.mean(img):.1f})")
        elif np.mean(img) > 250:
            print(f"⚠️  Aviso: Imagem muito clara (média: {np.mean(img):.1f})")
        else:
            print(f"✅ Imagem com brilho normal")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao processar {image_path}: {e}")
        return False

def main():
    print("🔍 Testando imagens geradas...")
    
    speed_img = Path("datasets/raw_brazilian/signal_plates/signal_placa_limite_velocidade_brasil_000.jpg")
    if speed_img.exists():
        print(f"\n📸 Testando: {speed_img.name}")
        test_image(speed_img)
    else:
        print(f"❌ Arquivo não encontrado: {speed_img}")
    
    yield_img = Path("datasets/raw_brazilian/signal_plates/signal_placa_dê_preferência_brasil_000.jpg")
    if yield_img.exists():
        print(f"\n📸 Testando: {yield_img.name}")
        test_image(yield_img)
    else:
        print(f"❌ Arquivo não encontrado: {yield_img}")
    
    parking_img = Path("datasets/raw_brazilian/signal_plates/signal_placa_proibido_estacionar_brasil_000.jpg")
    if parking_img.exists():
        print(f"\n📸 Testando: {parking_img.name}")
        test_image(parking_img)
    else:
        print(f"❌ Arquivo não encontrado: {parking_img}")

if __name__ == "__main__":
    main()
