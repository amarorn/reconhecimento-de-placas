#!/usr/bin/env python3
"""
Gerador de Relatório PDF - Placas Brasileiras
=============================================

Este script gera um relatório completo em PDF com:
- Informações das placas detectadas
- Regiões (estados) identificados
- Números das placas
- Estatísticas e gráficos
"""

import os
from datetime import datetime
from plate_recognition_brasil import BrasilPlateRecognizer
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Usar backend não-interativo para servidor

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
    
    # Tentar importar novamente após instalação
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

class PDFReportGenerator:
    """Gerador de relatórios em PDF"""
    
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
            textColor=colors.darkblue
        )
        
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_LEFT,
            textColor=colors.darkgreen
        )
        
        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=15,
            alignment=TA_LEFT,
            textColor=colors.darkred
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
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table
    
    def create_plates_table(self, plates_details: list) -> Table:
        """Cria tabela detalhada das placas"""
        if not plates_details:
            return Paragraph("Nenhuma placa encontrada", self.styles['Normal'])
        
        # Cabeçalho da tabela
        headers = ['Imagem', 'Placa', 'Região', 'Tipo', 'Número', 'Confiança']
        table_data = [headers]
        
        # Dados das placas
        for plate in plates_details:
            row = [
                os.path.basename(plate['image']),
                plate['plate_text'],
                plate['region_name'] or 'N/A',
                plate['plate_type'] or 'N/A',
                plate['plate_number'] or 'N/A',
                f"{plate['confidence']:.2f}"
            ]
            table_data.append(row)
        
        # Criar tabela
        col_widths = [1.5*inch, 1*inch, 1.5*inch, 1.5*inch, 1*inch, 0.8*inch]
        table = Table(table_data, colWidths=col_widths)
        
        # Estilizar tabela
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        return table
    
    def create_regions_summary(self, regions_summary: dict) -> Table:
        """Cria tabela de resumo por região"""
        if not regions_summary:
            return Paragraph("Nenhuma região identificada", self.styles['Normal'])
        
        # Ordenar por quantidade
        sorted_regions = sorted(regions_summary.items(), key=lambda x: x[1], reverse=True)
        
        table_data = [['Região (Estado)', 'Quantidade de Placas']]
        for region, count in sorted_regions:
            table_data.append([region, str(count)])
        
        table = Table(table_data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table
    
    def create_plate_types_summary(self, plate_types_summary: dict) -> Table:
        """Cria tabela de resumo por tipo de placa"""
        if not plate_types_summary:
            return Paragraph("Nenhum tipo de placa identificado", self.styles['Normal'])
        
        table_data = [['Tipo de Placa', 'Quantidade']]
        for plate_type, count in plate_types_summary.items():
            table_data.append([plate_type, str(count)])
        
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
            output_filename = f"relatorio_placas_brasileiras_{timestamp}.pdf"
        
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
        
        # Detalhes das placas
        story.append(Paragraph("🚗 DETALHES DAS PLACAS DETECTADAS", self.subtitle_style))
        story.append(Spacer(1, 10))
        
        plates_table = self.create_plates_table(report_data['plates_details'])
        story.append(plates_table)
        story.append(Spacer(1, 30))
        
        # Resumo por região
        story.append(Paragraph("📍 RESUMO POR REGIÃO (ESTADO)", self.subtitle_style))
        story.append(Spacer(1, 10))
        
        regions_table = self.create_regions_summary(report_data['regions_summary'])
        story.append(regions_table)
        story.append(Spacer(1, 30))
        
        # Resumo por tipo de placa
        story.append(Paragraph("🏷️ RESUMO POR TIPO DE PLACA", self.subtitle_style))
        story.append(Spacer(1, 10))
        
        types_table = self.create_plate_types_summary(report_data['plate_types_summary'])
        story.append(types_table)
        story.append(Spacer(1, 30))
        
        # Análise técnica
        story.append(Paragraph("🔧 ANÁLISE TÉCNICA", self.subtitle_style))
        story.append(Spacer(1, 10))
        
        analysis_text = f"""
        Este relatório foi gerado automaticamente pelo sistema de reconhecimento de placas brasileiras.
        
        • Total de imagens processadas: {report_data['summary']['total_images']}
        • Taxa de sucesso: {(report_data['summary']['successful_processings']/report_data['summary']['total_images']*100):.1f}%
        • Placas detectadas com sucesso: {report_data['summary']['total_plates_found']}
        • Erros encontrados: {report_data['summary']['errors']}
        
        O sistema identifica automaticamente:
        - Padrão antigo (Mercosul): ABC1234
        - Padrão novo (Mercosul): ABC1D23
        - Região/Estado de origem
        - Número da placa
        - Tipo de padronização
        """
        
        story.append(Paragraph(analysis_text, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Rodapé
        story.append(Paragraph("--- Relatório gerado automaticamente ---", self.styles['Normal']))
        story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}", self.styles['Normal']))
        
        # Construir PDF
        doc.build(story)
        
        return output_filename

def main():
    """Função principal para gerar relatório"""
    print("📊 GERADOR DE RELATÓRIO PDF - PLACAS BRASILEIRAS")
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
    
    # Criar reconhecedor brasileiro
    recognizer = BrasilPlateRecognizer()
    
    print("\n🔍 Processando imagens para gerar relatório...")
    
    # Processar todas as imagens
    results = recognizer.process_batch_brazil()
    
    # Gerar dados do relatório
    report_data = recognizer.generate_report_data(results)
    
    print(f"\n📋 DADOS COLETADOS:")
    print(f"   • Total de imagens: {report_data['summary']['total_images']}")
    print(f"   • Placas encontradas: {report_data['summary']['total_plates_found']}")
    print(f"   • Regiões identificadas: {len(report_data['regions_summary'])}")
    print(f"   • Tipos de placa: {len(report_data['plate_types_summary'])}")
    
    # Gerar PDF
    print(f"\n📄 Gerando relatório em PDF...")
    
    try:
        generator = PDFReportGenerator()
        pdf_filename = generator.generate_pdf_report(report_data)
        
        print(f"✅ Relatório gerado com sucesso!")
        print(f"📁 Arquivo: {pdf_filename}")
        print(f"📏 Tamanho: {os.path.getsize(pdf_filename)} bytes")
        
        # Mostrar detalhes das placas
        if report_data['plates_details']:
            print(f"\n🚗 PLACAS DETECTADAS:")
            for plate in report_data['plates_details']:
                print(f"   • {plate['plate_text']} - {plate['region_name']} ({plate['plate_type']})")
                print(f"     Número: {plate['plate_number']} | Confiança: {plate['confidence']:.2f}")
        
        print(f"\n🎯 Relatório completo salvo em: {pdf_filename}")
        
    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {e}")

if __name__ == "__main__":
    main()
