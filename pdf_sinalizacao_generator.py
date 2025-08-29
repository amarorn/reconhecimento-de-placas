#!/usr/bin/env python3
"""
Gerador de Relatório PDF - Placas de Sinalização Brasileiras
============================================================

Este script gera um relatório completo em PDF com:
- Informações das placas de sinalização detectadas
- Análise de cores e formas
- Tipos de sinalização identificados
- Estatísticas detalhadas
"""

import os
from datetime import datetime
from plate_recognition_sinalizacao import SinalizacaoBrasilRecognizer
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️  ReportLab não disponível. Instalando...")
    import subprocess
    subprocess.run(['pip', 'install', 'reportlab'])
    
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from reportlab.pdfgen import canvas
        REPORTLAB_AVAILABLE = True
    except ImportError:
        REPORTLAB_AVAILABLE = False

class SinalizacaoPDFGenerator:
    """Gerador de relatórios PDF para placas de sinalização"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Configura estilos customizados"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkred
        )
        
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_LEFT,
            textColor=colors.darkblue
        )
        
        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=15,
            alignment=TA_LEFT,
            textColor=colors.darkgreen
        )
    
    def create_summary_table(self, report_data: dict) -> Table:
        """Cria tabela de resumo"""
        summary_data = [
            ['Métrica', 'Valor'],
            ['Total de Imagens', str(report_data['summary']['total_images'])],
            ['Processamentos Bem-sucedidos', str(report_data['summary']['successful_processings'])],
            ['Total de Placas Encontradas', str(report_data['summary']['total_plates_found'])],
            ['Erros', str(report_data['summary']['errors'])],
            ['Data/Hora', report_data['timestamp']]
        ]
        
        table = Table(summary_data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightcoral),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table
    
    def create_sinalizacao_table(self, sinalizacao_details: list) -> Table:
        """Cria tabela detalhada das placas de sinalização"""
        if not sinalizacao_details:
            return Paragraph("Nenhuma placa de sinalização encontrada", self.styles['Normal'])
        
        # Cabeçalho da tabela
        headers = ['Imagem', 'Tipo', 'Cores', 'Formas', 'Texto', 'Confiança']
        table_data = [headers]
        
        # Dados das placas
        for plate in sinalizacao_details:
            row = [
                os.path.basename(plate['image']),
                plate['type'],
                ', '.join(plate.get('colors', [])),
                ', '.join(plate.get('shapes', [])),
                plate.get('text', 'N/A'),
                f"{plate['confidence']:.2f}"
            ]
            table_data.append(row)
        
        # Criar tabela
        col_widths = [1.5*inch, 1.5*inch, 1*inch, 1*inch, 1.5*inch, 0.8*inch]
        table = Table(table_data, colWidths=col_widths)
        
        # Estilizar tabela
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        return table
    
    def create_colors_summary(self, colors_summary: dict) -> Table:
        """Cria tabela de resumo por cores"""
        if not colors_summary:
            return Paragraph("Nenhuma cor identificada", self.styles['Normal'])
        
        # Ordenar por quantidade
        sorted_colors = sorted(colors_summary.items(), key=lambda x: x[1], reverse=True)
        
        table_data = [['Cor', 'Quantidade de Placas']]
        for color, count in sorted_colors:
            table_data.append([color, str(count)])
        
        table = Table(table_data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table
    
    def create_shapes_summary(self, shapes_summary: dict) -> Table:
        """Cria tabela de resumo por formas"""
        if not shapes_summary:
            return Paragraph("Nenhuma forma identificada", self.styles['Normal'])
        
        table_data = [['Forma', 'Quantidade']]
        for shape, count in shapes_summary.items():
            table_data.append([shape, str(count)])
        
        table = Table(table_data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkorange),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table
    
    def generate_pdf_report(self, report_data: dict, output_filename: str = None) -> str:
        """Gera relatório completo em PDF"""
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"relatorio_sinalizacao_brasileira_{timestamp}.pdf"
        
        # Criar documento
        doc = SimpleDocTemplate(output_filename, pagesize=A4)
        story = []
        
        # Título principal
        story.append(Paragraph(report_data['title'], self.title_style))
        story.append(Spacer(1, 20))
        
        # Informações gerais
        story.append(Paragraph(f"Data/Hora: {report_data['timestamp']}", self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Resumo executivo
        story.append(Paragraph("📊 RESUMO EXECUTIVO", self.subtitle_style))
        story.append(Spacer(1, 10))
        
        summary_table = self.create_summary_table(report_data)
        story.append(summary_table)
        story.append(Spacer(1, 30))
        
        # Detalhes das placas de sinalização
        story.append(Paragraph("🚦 DETALHES DAS PLACAS DE SINALIZAÇÃO", self.subtitle_style))
        story.append(Spacer(1, 10))
        
        sinalizacao_table = self.create_sinalizacao_table(report_data['sinalizacao_details'])
        story.append(sinalizacao_table)
        story.append(Spacer(1, 30))
        
        # Resumo por cores
        story.append(Paragraph("🎨 RESUMO POR CORES", self.subtitle_style))
        story.append(Spacer(1, 10))
        
        colors_table = self.create_colors_summary(report_data['colors_summary'])
        story.append(colors_table)
        story.append(Spacer(1, 30))
        
        # Resumo por formas
        story.append(Paragraph("🔷 RESUMO POR FORMAS", self.subtitle_style))
        story.append(Spacer(1, 10))
        
        shapes_table = self.create_shapes_summary(report_data['shapes_summary'])
        story.append(shapes_table)
        story.append(Spacer(1, 30))
        
        # Análise técnica
        story.append(Paragraph("🔧 ANÁLISE TÉCNICA", self.subtitle_style))
        story.append(Spacer(1, 10))
        
        analysis_text = f"""
        Este relatório foi gerado automaticamente pelo sistema de reconhecimento de placas de sinalização brasileiras.
        
        • Total de imagens processadas: {report_data['summary']['total_images']}
        • Taxa de sucesso: {(report_data['summary']['successful_processings']/report_data['summary']['total_images']*100):.1f}%
        • Placas de sinalização detectadas: {report_data['summary']['total_plates_found']}
        • Erros encontrados: {report_data['summary']['errors']}
        
        O sistema identifica automaticamente:
        - Cores das placas (vermelho, azul, amarelo, verde, branco)
        - Formas das placas (triangular, circular, retangular, octogonal)
        - Tipos de sinalização (PARE, PROIBIDO, velocidade, nomes de rua)
        - Padrões brasileiros de trânsito e sinalização
        """
        
        story.append(Paragraph(analysis_text, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Rodapé
        story.append(Paragraph("--- Relatório de Sinalização Brasileira ---", self.styles['Normal']))
        story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}", self.styles['Normal']))
        
        # Construir PDF
        doc.build(story)
        
        return output_filename

def generate_sinalizacao_report_data(results: list) -> dict:
    """Gera dados para relatório de sinalização"""
    report_data = {
        'title': 'Relatório de Placas de Sinalização Brasileiras',
        'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'summary': {
            'total_images': len(results),
            'successful_processings': len([r for r in results if 'error' not in r]),
            'total_plates_found': sum(len(r.get('sinalizacao_detected', [])) for r in results),
            'errors': len([r for r in results if 'error' in r])
        },
        'sinalizacao_details': [],
        'colors_summary': {},
        'shapes_summary': {}
    }
    
    # Processar detalhes das placas
    for result in results:
        if 'sinalizacao_detected' in result:
            for plate in result['sinalizacao_detected']:
                analysis = result.get('analysis', {})
                
                plate_detail = {
                    'image': result['image_path'],
                    'text': plate['text'],
                    'type': plate['type'],
                    'confidence': plate['confidence'],
                    'colors': list(analysis.get('colors', {}).keys()),
                    'shapes': list(analysis.get('shapes', {}).keys()),
                    'text': analysis.get('text', {}).get('text', 'N/A')
                }
                
                report_data['sinalizacao_details'].append(plate_detail)
                
                # Contar cores
                for color in plate_detail['colors']:
                    report_data['colors_summary'][color] = report_data['colors_summary'].get(color, 0) + 1
                
                # Contar formas
                for shape in plate_detail['shapes']:
                    report_data['shapes_summary'][shape] = report_data['shapes_summary'].get(shape, 0) + 1
    
    return report_data

def main():
    """Função principal para gerar relatório de sinalização"""
    print("🚦 GERADOR DE RELATÓRIO PDF - SINALIZAÇÃO BRASILEIRA")
    print("=" * 60)
    
    if not REPORTLAB_AVAILABLE:
        print("❌ ReportLab não está disponível. Instalando...")
        try:
            import subprocess
            subprocess.run(['pip', 'install', 'reportlab'], check=True)
            print("✅ ReportLab instalado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao instalar ReportLab: {e}")
            return
    
    # Criar reconhecedor de sinalização
    recognizer = SinalizacaoBrasilRecognizer()
    
    print("\n🔍 Processando imagens para gerar relatório de sinalização...")
    
    # Processar todas as imagens
    results = recognizer.process_batch_sinalizacao()
    
    # Gerar dados do relatório
    report_data = generate_sinalizacao_report_data(results)
    
    print(f"\n📋 DADOS COLETADOS:")
    print(f"   • Total de imagens: {report_data['summary']['total_images']}")
    print(f"   • Placas encontradas: {report_data['summary']['total_plates_found']}")
    print(f"   • Cores identificadas: {len(report_data['colors_summary'])}")
    print(f"   • Formas identificadas: {len(report_data['shapes_summary'])}")
    
    # Gerar PDF
    print(f"\n📄 Gerando relatório PDF de sinalização...")
    
    try:
        generator = SinalizacaoPDFGenerator()
        pdf_filename = generator.generate_pdf_report(report_data)
        
        print(f"✅ Relatório de sinalização gerado com sucesso!")
        print(f"📁 Arquivo: {pdf_filename}")
        print(f"📏 Tamanho: {os.path.getsize(pdf_filename)} bytes")
        
        # Mostrar detalhes das placas
        if report_data['sinalizacao_details']:
            print(f"\n🚦 PLACAS DE SINALIZAÇÃO DETECTADAS:")
            for plate in report_data['sinalizacao_details']:
                print(f"   • {plate['text']} - {plate['type']}")
                print(f"     Cores: {', '.join(plate['colors'])}")
                print(f"     Formas: {', '.join(plate['shapes'])}")
        
        print(f"\n🎯 Relatório de sinalização completo salvo em: {pdf_filename}")
        
    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {e}")

if __name__ == "__main__":
    main()
