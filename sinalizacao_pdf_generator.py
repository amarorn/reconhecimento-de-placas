#!/usr/bin/env python3
"""
Gerador de Relatório PDF Independente - Placas de Sinalização
============================================================

Este arquivo é COMPLETAMENTE SEPARADO do processamento de placas de veículos.
Gera relatórios específicos para placas de sinalização brasileiras.

Funcionalidades:
- Relatórios PDF especializados em sinalização
- Análise detalhada de cores e formas
- Estatísticas específicas para trânsito
- Formatação profissional independente
"""

import os
from datetime import datetime
from sinalizacao_processor import SinalizacaoProcessor

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️  ReportLab não disponível. Instalando...")
    import subprocess
    subprocess.run(['pip', 'install', 'reportlab'])
    
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        REPORTLAB_AVAILABLE = True
    except ImportError:
        REPORTLAB_AVAILABLE = False

class SinalizacaoPDFGenerator:
    """Gerador independente de relatórios PDF para placas de sinalização"""
    
    def __init__(self):
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab não está disponível")
        
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Configura estilos customizados para sinalização"""
        self.title_style = ParagraphStyle(
            'SinalizacaoTitle',
            parent=self.styles['Heading1'],
            fontSize=26,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkred,
            fontName='Helvetica-Bold'
        )
        
        self.subtitle_style = ParagraphStyle(
            'SinalizacaoSubtitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_LEFT,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        
        self.header_style = ParagraphStyle(
            'SinalizacaoHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=15,
            alignment=TA_LEFT,
            textColor=colors.darkgreen,
            fontName='Helvetica-Bold'
        )
        
        self.normal_style = ParagraphStyle(
            'SinalizacaoNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_LEFT,
            fontName='Helvetica'
        )
    
    def create_summary_table(self, summary: dict) -> Table:
        """Cria tabela de resumo executivo"""
        summary_data = [
            ['Métrica', 'Valor'],
            ['Total de Imagens', str(summary['total_images'])],
            ['Detecções Bem-sucedidas', str(summary['successful_detections'])],
            ['Taxa de Sucesso', f"{(summary['successful_detections']/summary['total_images']*100):.1f}%"],
            ['Erros', str(summary['errors'])],
            ['Confiança Média', f"{summary['confidence_stats']['avg']:.2f}"],
            ['Confiança Mínima', f"{summary['confidence_stats']['min']:.2f}"],
            ['Confiança Máxima', f"{summary['confidence_stats']['max']:.2f}"],
            ['Data/Hora', datetime.now().strftime('%d/%m/%Y %H:%M:%S')]
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
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        return table
    
    def create_colors_summary_table(self, colors_summary: dict) -> Table:
        """Cria tabela de resumo por cores"""
        if not colors_summary:
            return Paragraph("Nenhuma cor identificada", self.normal_style)
        
        # Ordenar por quantidade
        sorted_colors = sorted(colors_summary.items(), key=lambda x: x[1], reverse=True)
        
        table_data = [['Cor', 'Quantidade', 'Descrição']]
        color_descriptions = {
            'vermelho': 'Pare, Proibido, Obrigatório',
            'azul': 'Regulamentação, Informação, Direção',
            'amarelo': 'Advertência, Perigo',
            'verde': 'Informação, Direção',
            'branco': 'Texto, Fundo'
        }
        
        for color_name, count in sorted_colors:
            description = color_descriptions.get(color_name, 'Desconhecida')
            table_data.append([color_name.title(), str(count), description])
        
        table = Table(table_data, colWidths=[1.5*inch, 1.5*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        return table
    
    def create_shapes_summary_table(self, shapes_summary: dict) -> Table:
        """Cria tabela de resumo por formas"""
        if not shapes_summary:
            return Paragraph("Nenhuma forma identificada", self.normal_style)
        
        table_data = [['Forma', 'Quantidade', 'Tipo de Sinalização']]
        shape_types = {
            'triangular': 'Advertência',
            'circular': 'Regulamentação',
            'retangular': 'Informação',
            'octogonal': 'Obrigatório',
            'quadrado': 'Informação',
            'diamante': 'Advertência'
        }
        
        for shape, count in shapes_summary.items():
            shape_type = shape_types.get(shape, 'Desconhecido')
            table_data.append([shape.title(), str(count), shape_type])
        
        table = Table(table_data, colWidths=[1.5*inch, 1.5*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkorange),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        return table
    
    def create_types_summary_table(self, types_summary: dict) -> Table:
        """Cria tabela de resumo por tipos de sinalização"""
        if not types_summary:
            return Paragraph("Nenhum tipo identificado", self.normal_style)
        
        table_data = [['Tipo Primário', 'Quantidade', 'Descrição']]
        type_descriptions = {
            'obrigatorio': 'Placas que impõem obrigações (PARE, PROIBIDO)',
            'regulamentacao': 'Placas que regulamentam o trânsito (velocidade, direção)',
            'advertencia': 'Placas que advertem sobre perigos (curva, escola)',
            'informacao': 'Placas que informam (nomes de ruas, direções)'
        }
        
        for type_name, count in types_summary.items():
            description = type_descriptions.get(type_name, 'Tipo não especificado')
            table_data.append([type_name.title(), str(count), description])
        
        table = Table(table_data, colWidths=[2*inch, 1*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        return table
    
    def create_significados_summary_table(self, significados_summary: dict) -> Table:
        """Cria tabela de resumo por significados das placas"""
        if not significados_summary:
            return Paragraph("Nenhum significado identificado", self.normal_style)
        
        table_data = [['Placa de Sinalização', 'Quantidade', 'Tipo', 'Ação Principal']]
        
        for significado, count in significados_summary.items():
            # Determinar tipo baseado no nome
            if 'PARE' in significado or 'STOP' in significado:
                tipo = 'Obrigatório'
                acao = 'Parar'
            elif 'PROIBIDO' in significado:
                tipo = 'Obrigatório'
                acao = 'Não fazer'
            elif 'VELOCIDADE' in significado:
                tipo = 'Regulamentação'
                acao = 'Respeitar limite'
            elif 'DIREÇÃO' in significado:
                tipo = 'Regulamentação'
                acao = 'Seguir direção'
            elif 'CURVA' in significado or 'ESCOLA' in significado:
                tipo = 'Advertência'
                acao = 'Reduzir velocidade'
            elif 'RUA' in significado or 'AVENIDA' in significado:
                tipo = 'Informação'
                acao = 'Orientação'
            else:
                tipo = 'Genérico'
                acao = 'Observar'
            
            table_data.append([significado, str(count), tipo, acao])
        
        table = Table(table_data, colWidths=[2*inch, 1*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        return table
    
    def create_detailed_results_table(self, results: list) -> Table:
        """Cria tabela detalhada dos resultados (APENAS sinalização)"""
        if not results:
            return Paragraph("Nenhum resultado disponível", self.normal_style)
        
        # Filtrar apenas resultados de sinalização
        sinalizacao_results = [r for r in results if r.get('is_sinalizacao')]
        
        if not sinalizacao_results:
            return Paragraph("Nenhuma placa de sinalização encontrada", self.normal_style)
        
        # Cabeçalho da tabela
        headers = ['Imagem', 'Nome da Placa', 'Significado', 'Ação', 'Penalidade', 'Confiança']
        table_data = [headers]
        
        # Dados dos resultados
        for result in sinalizacao_results:
            if result.get('sinalizacao_detected'):
                sinalizacao_info = result['sinalizacao_info']
                
                # Truncar texto longo
                significado = sinalizacao_info['significado']
                if len(significado) > 40:
                    significado = significado[:37] + '...'
                
                acao = sinalizacao_info['acao']
                if len(acao) > 25:
                    acao = acao[:22] + '...'
                
                row = [
                    os.path.basename(result['image_path']),
                    sinalizacao_info['nome'],
                    significado,
                    acao,
                    sinalizacao_info['penalidade'][:20] + '...' if len(sinalizacao_info['penalidade']) > 20 else sinalizacao_info['penalidade'],
                    f"{result['confidence']:.2f}"
                ]
                table_data.append(row)
        
        # Criar tabela
        col_widths = [1.2*inch, 1.5*inch, 2*inch, 1.5*inch, 1.5*inch, 0.8*inch]
        table = Table(table_data, colWidths=col_widths)
        
        # Estilizar tabela
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightblue, colors.lightcyan])
        ]))
        
        return table
    
    def generate_pdf_report(self, results: list, output_filename: str = None) -> str:
        """Gera relatório completo em PDF para sinalização"""
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"relatorio_sinalizacao_independente_{timestamp}.pdf"
        
        # Criar documento
        doc = SimpleDocTemplate(output_filename, pagesize=A4)
        story = []
        
        # Título principal
        story.append(Paragraph("🚦 RELATÓRIO DE PLACAS DE SINALIZAÇÃO BRASILEIRAS", self.title_style))
        story.append(Spacer(1, 20))
        
        # Informações gerais
        story.append(Paragraph(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}", self.normal_style))
        story.append(Paragraph("Sistema Independente de Processamento de Sinalização", self.normal_style))
        story.append(Spacer(1, 20))
        
        # Resumo executivo
        story.append(Paragraph("📊 RESUMO EXECUTIVO", self.subtitle_style))
        story.append(Spacer(1, 10))
        
        # Gerar resumo dos resultados
        processor = SinalizacaoProcessor()
        summary = processor.generate_summary(results)
        
        summary_table = self.create_summary_table(summary)
        story.append(summary_table)
        story.append(Spacer(1, 30))
        
        # Resumo por cores
        story.append(Paragraph("🎨 ANÁLISE POR CORES", self.subtitle_style))
        story.append(Spacer(1, 10))
        
        colors_table = self.create_colors_summary_table(summary['colors_summary'])
        story.append(colors_table)
        story.append(Spacer(1, 30))
        
        # Resumo por formas
        story.append(Paragraph("🔷 ANÁLISE POR FORMAS", self.subtitle_style))
        story.append(Spacer(1, 10))
        
        shapes_table = self.create_shapes_summary_table(summary['shapes_summary'])
        story.append(shapes_table)
        story.append(Spacer(1, 30))
        
        # Resumo por tipos
        story.append(Paragraph("🚦 ANÁLISE POR TIPOS DE SINALIZAÇÃO", self.subtitle_style))
        story.append(Spacer(1, 10))
        
        types_table = self.create_types_summary_table(summary['types_summary'])
        story.append(types_table)
        story.append(Spacer(1, 30))

        # Resumo por significados
        story.append(Paragraph("💬 ANÁLISE POR SIGNIFICADOS DAS PLACAS", self.subtitle_style))
        story.append(Spacer(1, 10))

        significados_table = self.create_significados_summary_table(summary['significados_summary'])
        story.append(significados_table)
        story.append(Spacer(1, 30))
        
        # Resultados detalhados
        story.append(Paragraph("📋 RESULTADOS DETALHADOS", self.subtitle_style))
        story.append(Spacer(1, 10))
        
        detailed_table = self.create_detailed_results_table(results)
        story.append(detailed_table)
        story.append(Spacer(1, 30))
        
        # Análise técnica
        story.append(Paragraph("🔧 ANÁLISE TÉCNICA", self.subtitle_style))
        story.append(Spacer(1, 10))
        
        analysis_text = f"""
        Este relatório foi gerado pelo sistema independente de reconhecimento de placas de sinalização brasileiras.
        
        <b>Características do Sistema:</b>
        • <b>Independência:</b> Sistema completamente separado do processamento de placas de veículos
        • <b>Especialização:</b> Otimizado especificamente para placas de sinalização de trânsito
        • <b>Precisão:</b> Algoritmos especializados em cores e formas de sinalização brasileira
        
        <b>Métricas de Performance:</b>
        • Total de imagens processadas: {summary['total_images']}
        • Taxa de sucesso: {(summary['successful_detections']/summary['total_images']*100):.1f}%
        • Confiança média: {summary['confidence_stats']['avg']:.2f}
        • Erros encontrados: {summary['errors']}
        
        <b>Tipos de Sinalização Identificados:</b>
        • <b>Obrigatório:</b> Placas que impõem obrigações (PARE, PROIBIDO)
        • <b>Regulamentação:</b> Placas que regulamentam o trânsito (velocidade, direção)
        • <b>Advertência:</b> Placas que advertem sobre perigos (curva, escola)
        • <b>Informação:</b> Placas que informam (nomes de ruas, direções)
        """
        
        story.append(Paragraph(analysis_text, self.normal_style))
        story.append(Spacer(1, 20))
        
        # Rodapé
        story.append(Paragraph("--- Sistema Independente de Sinalização Brasileira ---", self.normal_style))
        story.append(Paragraph(f"Relatório gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}", self.normal_style))
        story.append(Paragraph("🚦 Especializado em placas de trânsito, ruas, direções e sinalização", self.normal_style))
        
        # Construir PDF
        doc.build(story)
        
        return output_filename

def main():
    """Função principal para gerar relatório independente de sinalização"""
    print("🚦 GERADOR INDEPENDENTE DE RELATÓRIO PDF - SINALIZAÇÃO")
    print("=" * 60)
    print("📋 Este arquivo é COMPLETAMENTE SEPARADO do processamento de placas de veículos!")
    print("🎯 Gera relatórios específicos para placas de sinalização brasileiras")
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
    
    # Criar processador de sinalização
    processor = SinalizacaoProcessor()
    
    print("\n🔍 Processando imagens para gerar relatório independente de sinalização...")
    
    # Processar todas as imagens
    results = processor.process_batch_sinalizacao()
    
    # Gerar resumo
    summary = processor.generate_summary(results)
    
    print(f"\n📋 DADOS COLETADOS:")
    print(f"   • Total de imagens: {summary['total_images']}")
    print(f"   • Detecções bem-sucedidas: {summary['successful_detections']}")
    print(f"   • Cores identificadas: {len(summary['colors_summary'])}")
    print(f"   • Formas identificadas: {len(summary['shapes_summary'])}")
    print(f"   • Tipos identificados: {len(summary['types_summary'])}")
    print(f"   • Significados identificados: {len(summary['significados_summary'])}")
    
    # Gerar PDF
    print(f"\n📄 Gerando relatório PDF independente de sinalização...")
    
    try:
        generator = SinalizacaoPDFGenerator()
        pdf_filename = generator.generate_pdf_report(results)
        
        print(f"✅ Relatório independente de sinalização gerado com sucesso!")
        print(f"📁 Arquivo: {pdf_filename}")
        print(f"📏 Tamanho: {os.path.getsize(pdf_filename)} bytes")
        
        # Mostrar detalhes
        if summary['colors_summary']:
            print(f"\n🎨 CORES DETECTADAS:")
            for color, count in summary['colors_summary'].items():
                print(f"   • {color}: {count} placas")
        
        if summary['shapes_summary']:
            print(f"\n🔷 FORMAS DETECTADAS:")
            for shape, count in summary['shapes_summary'].items():
                print(f"   • {shape}: {count} placas")
        
        if summary['types_summary']:
            print(f"\n🚦 TIPOS DE SINALIZAÇÃO:")
            for type_name, count in summary['types_summary'].items():
                print(f"   • {type_name}: {count} placas")
        
        if summary['significados_summary']:
            print(f"\n💬 SIGNIFICADOS DETECTADOS:")
            for significado, count in summary['significados_summary'].items():
                print(f"   • {significado}: {count} placas")
        
        print(f"\n🎯 Relatório independente completo salvo em: {pdf_filename}")
        print(f"🚦 Sistema 100% independente de placas de veículos!")
        
    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {e}")

if __name__ == "__main__":
    main()
