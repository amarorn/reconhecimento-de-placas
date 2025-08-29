#!/usr/bin/env python3
"""
Processador de Placas Reais - Pasta imagens_exemplo
==================================================

Este script processa especificamente as placas da pasta imagens_exemplo
e gera um relatório detalhado.
"""

import os
import cv2
from plate_recognition_brasil import BrasilPlateRecognizer
from pdf_report_generator import PDFReportGenerator
from datetime import datetime

def process_real_plates():
    """Processa as placas reais da pasta imagens_exemplo"""
    print("🔍 PROCESSANDO PLACAS REAIS DA PASTA imagens_exemplo/")
    print("=" * 60)
    
    # Lista das imagens de placas reais
    real_plate_images = ['placa 1.jpg', 'placa 2.jpg', 'placa 1 2.jpg']
    
    recognizer = BrasilPlateRecognizer()
    results = []
    
    for i, img_file in enumerate(real_plate_images, 1):
        if os.path.exists(img_file):
            print(f"\n[{i}/{len(real_plate_images)}] Processando: {img_file}")
            
            try:
                # Carregar e verificar imagem
                image = cv2.imread(img_file)
                if image is not None:
                    height, width = image.shape[:2]
                    print(f"   📏 Dimensões: {width}x{height} pixels")
                    print(f"   💾 Tamanho: {os.path.getsize(img_file)} bytes")
                    
                    # Processar com o reconhecedor
                    result = recognizer.detect_plate_brazil(img_file)
                    results.append(result)
                    
                    if 'plates_found' in result and result['plates_found']:
                        plate = result['plates_found'][0]
                        analysis = plate.get('analysis', {})
                        print(f"   ✅ Placa detectada: {plate['text']}")
                        print(f"      📍 Região: {analysis.get('region_name', 'N/A')}")
                        print(f"      🔢 Número: {analysis.get('plate_number', 'N/A')}")
                        print(f"      🏷️  Tipo: {analysis.get('plate_type', 'N/A')}")
                        print(f"      🎯 Confiança: {plate['confidence']:.2f}")
                    else:
                        print(f"   ❌ Nenhuma placa detectada")
                else:
                    print(f"   ❌ Erro ao carregar imagem")
            except Exception as e:
                print(f"   ❌ Erro: {e}")
                results.append({'error': str(e), 'image': img_file})
        else:
            print(f"   ❌ Arquivo não encontrado: {img_file}")
            results.append({'error': 'Arquivo não encontrado', 'image': img_file})
        
        print("-" * 40)
    
    return results

def generate_real_plates_report(results):
    """Gera relatório específico para as placas reais"""
    print(f"\n📊 GERANDO RELATÓRIO DAS PLACAS REAIS")
    print("-" * 50)
    
    # Gerar dados do relatório
    report_data = {
        'title': 'Relatório de Placas Reais - Pasta imagens_exemplo',
        'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'summary': {
            'total_images': len(results),
            'successful_processings': len([r for r in results if 'error' not in r]),
            'total_plates_found': sum(len(r.get('plates_found', [])) for r in results),
            'errors': len([r for r in results if 'error' in r])
        },
        'plates_details': [],
        'regions_summary': {},
        'plate_types_summary': {}
    }
    
    # Processar detalhes das placas
    for result in results:
        if 'plates_found' in result:
            for plate in result['plates_found']:
                analysis = plate.get('analysis', {})
                
                plate_detail = {
                    'image': result['image_path'],
                    'plate_text': plate['text'],
                    'region_code': analysis.get('region_code'),
                    'region_name': analysis.get('region_name'),
                    'plate_type': analysis.get('plate_type'),
                    'plate_number': analysis.get('plate_number'),
                    'confidence': plate['confidence']
                }
                
                report_data['plates_details'].append(plate_detail)
                
                # Contar regiões
                region = analysis.get('region_name', 'Desconhecida')
                report_data['regions_summary'][region] = report_data['regions_summary'].get(region, 0) + 1
                
                # Contar tipos de placa
                plate_type = analysis.get('plate_type', 'Desconhecido')
                report_data['plate_types_summary'][plate_type] = report_data['plate_types_summary'].get(plate_type, 0) + 1
    
    return report_data

def main():
    """Função principal"""
    print("🚗 PROCESSADOR DE PLACAS REAIS")
    print("   Pasta: imagens_exemplo/")
    print("=" * 60)
    
    # Processar placas reais
    results = process_real_plates()
    
    # Resumo do processamento
    total_plates = sum(len(r.get('plates_found', [])) for r in results)
    successful = len([r for r in results if 'error' not in r])
    
    print(f"\n🎯 RESUMO DO PROCESSAMENTO")
    print(f"   • Imagens processadas: {len(results)}")
    print(f"   • Processamentos bem-sucedidos: {successful}")
    print(f"   • Total de placas encontradas: {total_plates}")
    
    if total_plates > 0:
        print(f"\n🚗 PLACAS DETECTADAS:")
        for result in results:
            if 'plates_found' in result:
                for plate in result['plates_found']:
                    analysis = plate.get('analysis', {})
                    print(f"   • {plate['text']} - {analysis.get('region_name', 'N/A')}")
                    print(f"     Tipo: {analysis.get('plate_type', 'N/A')}")
                    print(f"     Número: {analysis.get('plate_number', 'N/A')}")
                    print(f"     Imagem: {os.path.basename(result['image_path'])}")
        
        # Gerar relatório PDF
        print(f"\n📄 Gerando relatório PDF...")
        try:
            report_data = generate_real_plates_report(results)
            
            generator = PDFReportGenerator()
            pdf_filename = f"relatorio_placas_reais_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf_filename = generator.generate_pdf_report(report_data, pdf_filename)
            
            print(f"✅ Relatório gerado com sucesso!")
            print(f"📁 Arquivo: {pdf_filename}")
            print(f"📏 Tamanho: {os.path.getsize(pdf_filename)} bytes")
            
        except Exception as e:
            print(f"❌ Erro ao gerar PDF: {e}")
    else:
        print("❌ Nenhuma placa foi detectada nas imagens")
    
    print(f"\n🎯 Processamento concluído!")

if __name__ == "__main__":
    main()
