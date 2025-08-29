#!/usr/bin/env python3
"""
Script para extrair e analisar conteúdo dos PDFs de sinalização
"""

import PyPDF2
import re
import json

def extract_pdf_content(pdf_path):
    """Extrai o conteúdo textual de um PDF"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
                
            return text
    except Exception as e:
        print(f"Erro ao ler PDF {pdf_path}: {e}")
        return ""

def analyze_sinalizacao_content(text):
    """Analisa o conteúdo extraído em busca de placas de sinalização"""
    # Padrões para identificar placas de sinalização
    patterns = {
        'codigos_r': r'R-\d+[a-z]?',  # R-1, R-4a, etc.
        'nomes_placas': r'[A-Z\s]+(?:PROIBIDO|PERMITIDO|OBRIGATÓRIO|EXCLUSIVO|MÁXIMA|MÍNIMA)',
        'velocidades': r'\d+\s*km/h',
        'cores': r'(?:VERMELHO|AZUL|AMARELO|BRANCO|PRETO)',
        'formas': r'(?:CÍRCULO|TRIÂNGULO|OCTÓGONO|RETÂNGULO|QUADRADO)',
        'penalidades': r'(?:MULTA|PONTOS|REMOÇÃO|APREENSÃO)',
    }
    
    results = {}
    
    for pattern_name, pattern in patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        results[pattern_name] = list(set(matches))  # Remove duplicatas
    
    return results

def main():
    """Função principal"""
    pdf_files = [
        "copy_of___01___MBST_Vol_I___Sin_Vert_Regulamentacao_F_pages_deleted (1).pdf",
        "(Microsoft Word - - 02 - MBST Vol. II - Sin. Vert. Advert_352ncia).pdf"
    ]
    
    all_content = {}
    
    for pdf_file in pdf_files:
        print(f"\n📖 Analisando: {pdf_file}")
        print("=" * 60)
        
        content = extract_pdf_content(pdf_file)
        if content:
            print(f"✅ Conteúdo extraído: {len(content)} caracteres")
            
            # Analisa o conteúdo
            analysis = analyze_sinalizacao_content(content)
            
            # Salva o conteúdo e análise
            all_content[pdf_file] = {
                'raw_content': content[:2000] + "..." if len(content) > 2000 else content,
                'analysis': analysis
            }
            
            # Mostra resultados da análise
            print("\n🔍 ANÁLISE DO CONTEÚDO:")
            for pattern_name, matches in analysis.items():
                if matches:
                    print(f"   {pattern_name.upper()}: {len(matches)} encontrados")
                    for match in matches[:5]:  # Mostra apenas os primeiros 5
                        print(f"     - {match}")
                    if len(matches) > 5:
                        print(f"     ... e mais {len(matches) - 5}")
                else:
                    print(f"   {pattern_name.upper()}: Nenhum encontrado")
        else:
            print(f"❌ Falha ao extrair conteúdo de {pdf_file}")
    
    # Salva os resultados em um arquivo JSON para análise posterior
    with open('pdf_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_content, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Resultados salvos em 'pdf_analysis_results.json'")
    
    # Mostra um resumo dos códigos R encontrados
    all_codigos = set()
    for pdf_data in all_content.values():
        if 'analysis' in pdf_data and 'codigos_r' in pdf_data['analysis']:
            all_codigos.update(pdf_data['analysis']['codigos_r'])
    
    if all_codigos:
        print(f"\n🚦 CÓDIGOS R ENCONTRADOS ({len(all_codigos)}):")
        for codigo in sorted(all_codigos):
            print(f"   - {codigo}")
    
    return all_content

if __name__ == "__main__":
    main()
