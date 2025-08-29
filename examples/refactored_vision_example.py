#!/usr/bin/env python3
"""
Exemplo de Uso da Arquitetura Refatorada de Visão Computacional
================================================================

Este exemplo demonstra como usar a nova arquitetura modular e escalável
para reconhecimento de placas de trânsito e veículos.
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path para importar os módulos
sys.path.append(str(Path(__file__).parent.parent))

from config.vision_architecture import ConfigPresets
from vision.core.vision_pipeline import VisionPipeline
import logging

def setup_logging():
    """Configura o sistema de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('vision_pipeline.log')
        ]
    )

def create_pipeline_config():
    """Cria configuração para o pipeline"""
    # Usar configuração de desenvolvimento para este exemplo
    config = ConfigPresets.development()
    
    # Configurações específicas para o exemplo
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
    """Processa uma única imagem"""
    print(f"\n🖼️  Processando imagem: {image_path}")
    print("=" * 60)
    
    try:
        # Processar imagem com pipeline avançado
        result = pipeline.process_image_advanced(image_path)
        
        if result.success:
            print(f"✅ Processamento bem-sucedido!")
            print(f"⏱️  Tempo total: {result.processing_time:.2f}s")
            print(f"🔍 Detecções: {result.metadata['total_detections']}")
            print(f"📝 Textos extraídos: {result.metadata['total_texts']}")
            print(f"✅ Resultados validados: {result.metadata['validated_results']}")
            
            # Mostrar resultados detalhados
            if result.final_results:
                print(f"\n📊 Resultados Finais:")
                for i, final_result in enumerate(result.final_results):
                    detection = final_result['detection']
                    primary_text = final_result['primary_text']
                    confidence = final_result['confidence_score']
                    
                    print(f"  {i+1}. Classe: {detection['class_name']}")
                    print(f"     Confiança: {confidence:.3f}")
                    print(f"     Texto: {primary_text or 'N/A'}")
                    print(f"     Área: {detection['area']}")
                    print()
            
            # Mostrar estatísticas de componentes
            if result.preprocessing_result:
                print(f"📸 Pré-processamento: {result.preprocessing_result['enhancement_applied']}")
            
            if result.detection_result:
                print(f"🔍 Detecção - Média confiança: {result.detection_result['average_confidence']:.3f}")
            
            if result.ocr_result:
                print(f"📝 OCR - Média confiança: {result.ocr_result['average_confidence']:.3f}")
                
        else:
            print(f"❌ Falha no processamento: {result.error_message}")
            
    except Exception as e:
        print(f"❌ Erro durante processamento: {e}")

def process_batch_images(pipeline: VisionPipeline, image_dir: str):
    """Processa múltiplas imagens em lote"""
    print(f"\n📁 Processando diretório: {image_dir}")
    print("=" * 60)
    
    try:
        # Encontrar imagens no diretório
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        image_paths = []
        
        for ext in image_extensions:
            image_paths.extend(Path(image_dir).glob(f"*{ext}"))
            image_paths.extend(Path(image_dir).glob(f"*{ext.upper()}"))
        
        if not image_paths:
            print(f"❌ Nenhuma imagem encontrada em {image_dir}")
            return
        
        print(f"📸 Encontradas {len(image_paths)} imagens")
        
        # Criar diretório de saída
        output_dir = Path(image_dir) / "results"
        output_dir.mkdir(exist_ok=True)
        
        # Processar em lote
        results = pipeline.process_batch([str(p) for p in image_paths], str(output_dir))
        
        # Resumo dos resultados
        successful = sum(1 for r in results if r.success)
        total_time = sum(r.processing_time for r in results)
        
        print(f"\n📊 Resumo do Processamento em Lote:")
        print(f"✅ Sucessos: {successful}/{len(results)}")
        print(f"⏱️  Tempo total: {total_time:.2f}s")
        print(f"📁 Resultados salvos em: {output_dir}")
        
    except Exception as e:
        print(f"❌ Erro no processamento em lote: {e}")

def show_pipeline_info(pipeline: VisionPipeline):
    """Mostra informações sobre o pipeline"""
    print("\n🔧 Informações do Pipeline")
    print("=" * 60)
    
    stats = pipeline.get_pipeline_statistics()
    
    print(f"📦 Versão: {stats['pipeline_version']}")
    print(f"🕐 Inicializado em: {stats['initialized_at']}")
    print(f"💾 Cache: {stats['cache_size']} itens")
    
    print(f"\n🧩 Componentes:")
    for component, status in stats['components'].items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {component}")
    
    print(f"\n⚙️  Configurações:")
    config = stats['config']
    print(f"  🔍 Detector: {config['detection']['weights_path']}")
    print(f"  📝 OCR: {config['ocr']['type']}")
    print(f"  📸 Pré-processamento: {config['preprocessing']['type']}")

def main():
    """Função principal"""
    print("🚀 EXEMPLO DA ARQUITETURA REFATORADA DE VISÃO COMPUTACIONAL")
    print("=" * 80)
    
    # Configurar logging
    setup_logging()
    
    try:
        # 1. Criar configuração
        print("⚙️  Criando configuração...")
        config = create_pipeline_config()
        
        # 2. Inicializar pipeline
        print("🚀 Inicializando pipeline...")
        pipeline = VisionPipeline(config)
        
        # 3. Mostrar informações do pipeline
        show_pipeline_info(pipeline)
        
        # 4. Exemplos de uso
        print("\n🎯 EXEMPLOS DE USO")
        print("=" * 60)
        
        # Exemplo 1: Processar imagem única
        example_image = "sinalizacao_exemplo/placa_pare.jpg"
        if os.path.exists(example_image):
            process_single_image(pipeline, example_image)
        else:
            print(f"⚠️  Imagem de exemplo não encontrada: {example_image}")
            print("   Crie uma imagem de teste ou use uma imagem existente")
        
        # Exemplo 2: Processar diretório em lote
        example_dir = "sinalizacao_exemplo"
        if os.path.exists(example_dir) and os.path.isdir(example_dir):
            process_batch_images(pipeline, example_dir)
        else:
            print(f"⚠️  Diretório de exemplo não encontrado: {example_dir}")
        
        # 5. Limpeza
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