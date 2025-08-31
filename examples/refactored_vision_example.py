

import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from config.vision_architecture import ConfigPresets
from vision.core.vision_pipeline import VisionPipeline
import logging

def setup_logging():
    config = ConfigPresets.development()
    
    pipeline_config = {
        'preprocessing': {
            'resize_enabled': True,
            'target_size': (640, 640),
            'denoising_enabled': True,
            'denoising_method': 'bilateral',
            'contrast_enhancement': True,
            'contrast_method': 'clahe',
            'normalization': True,
            'additional_filters': True,
            'sharpen_enabled': True
        },
        'detection': {
            'weights_path': 'yolov8n.pt',
            'confidence_threshold': 0.5,
            'nms_threshold': 0.4,
            'input_size': (640, 640),
            'device': 'auto'
        },
        'ocr': {
            'type': 'paddleocr',
            'language': 'pt',
            'confidence_threshold': 0.7,
            'use_gpu': False,
            'apply_plate_rules': True
        },
        'validation_rules': {
            'min_plate_size': (50, 50),
            'max_plate_size': (800, 400),
            'min_text_length': 3,
            'max_text_length': 20,
            'min_confidence': 0.3
        },
        'log_level': 'INFO',
        'enable_cache': True,
        'enable_async': False
    }
    
    return pipeline_config

def process_single_image(pipeline: VisionPipeline, image_path: str):
    print(f"\n📁 Processando diretório: {image_dir}")
    print("=" * 60)
    
    try:
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        image_paths = []
        
        for ext in image_extensions:
            image_paths.extend(Path(image_dir).glob(f"*{ext}"))
            image_paths.extend(Path(image_dir).glob(f"*{ext.upper()}"))
        
        if not image_paths:
            print(f"❌ Nenhuma imagem encontrada em {image_dir}")
            return
        
        print(f"📸 Encontradas {len(image_paths)} imagens")
        
        output_dir = Path(image_dir) / "results"
        output_dir.mkdir(exist_ok=True)
        
        results = pipeline.process_batch([str(p) for p in image_paths], str(output_dir))
        
        successful = sum(1 for r in results if r.success)
        total_time = sum(r.processing_time for r in results)
        
        print(f"\n📊 Resumo do Processamento em Lote:")
        print(f"✅ Sucessos: {successful}/{len(results)}")
        print(f"⏱️  Tempo total: {total_time:.2f}s")
        print(f"📁 Resultados salvos em: {output_dir}")
        
    except Exception as e:
        print(f"❌ Erro no processamento em lote: {e}")

def show_pipeline_info(pipeline: VisionPipeline):
    print("🚀 EXEMPLO DA ARQUITETURA REFATORADA DE VISÃO COMPUTACIONAL")
    print("=" * 80)
    
    setup_logging()
    
    try:
        print("⚙️  Criando configuração...")
        config = create_pipeline_config()
        
        print("🚀 Inicializando pipeline...")
        pipeline = VisionPipeline(config)
        
        show_pipeline_info(pipeline)
        
        print("\n🎯 EXEMPLOS DE USO")
        print("=" * 60)
        
        example_image = "sinalizacao_exemplo/placa_pare.jpg"
        if os.path.exists(example_image):
            process_single_image(pipeline, example_image)
        else:
            print(f"⚠️  Imagem de exemplo não encontrada: {example_image}")
            print("   Crie uma imagem de teste ou use uma imagem existente")
        
        example_dir = "sinalizacao_exemplo"
        if os.path.exists(example_dir) and os.path.isdir(example_dir):
            process_batch_images(pipeline, example_dir)
        else:
            print(f"⚠️  Diretório de exemplo não encontrado: {example_dir}")
        
        print("\n🧹 Limpando recursos...")
        pipeline.cleanup()
        print("✅ Pipeline finalizado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro no exemplo: {e}")
        logging.error(f"Erro no exemplo: {e}", exc_info=True)
    
    print("\n" + "=" * 80)
    print("🎉 Exemplo concluído!")

if __name__ == "__main__":
    main()