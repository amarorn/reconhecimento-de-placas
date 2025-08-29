#!/usr/bin/env python3
"""
Script para extrair informações detalhadas das placas de sinalização
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

def parse_sinalizacao_regulamentacao(text):
    """Extrai informações detalhadas das placas de regulamentação"""
    # Padrão para encontrar placas: R-XX + Nome + Página
    pattern = r'R-(\d+[a-z]?)\s+([^\n]+?)\s+(\d+)'
    matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
    
    placas = {}
    
    for match in matches:
        codigo = f"R-{match[0]}"
        nome = match[1].strip()
        pagina = int(match[2])
        
        # Limpa o nome da placa
        nome = re.sub(r'\s+', ' ', nome).strip()
        
        placas[codigo] = {
            'nome': nome,
            'pagina': pagina,
            'codigo': codigo
        }
    
    return placas

def parse_sinalizacao_advertencia(text):
    """Extrai informações das placas de advertência"""
    # Padrão para placas de advertência: A-XX + Nome + Página
    pattern = r'A-(\d+[a-z]?)\s+([^\n]+?)\s+(\d+)'
    matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
    
    placas = {}
    
    for match in matches:
        codigo = f"A-{match[0]}"
        nome = match[1].strip()
        pagina = int(match[2])
        
        # Limpa o nome da placa
        nome = re.sub(r'\s+', ' ', nome).strip()
        
        placas[codigo] = {
            'nome': nome,
            'pagina': pagina,
            'codigo': codigo
        }
    
    return placas

def enrich_placas_data(placas_reg, placas_adv):
    """Enriquece os dados das placas com informações adicionais"""
    
    # Dicionário de enriquecimento baseado nos nomes das placas
    enrichment_data = {
        'pare': {
            'significado': 'Parada obrigatória. O veículo deve parar completamente antes de prosseguir.',
            'acao': 'Parar completamente',
            'penalidade': 'Multa e pontos na carteira',
            'cores': ['vermelho'],
            'formas': ['octogonal'],
            'tipo': 'obrigatorio'
        },
        'preferencia': {
            'significado': 'Ceder passagem aos veículos que vêm pela via preferencial.',
            'acao': 'Ceder passagem',
            'penalidade': 'Multa e pontos na carteira',
            'cores': ['vermelho', 'branco'],
            'formas': ['triangular'],
            'tipo': 'obrigatorio'
        },
        'sentido proibido': {
            'significado': 'Proíbe o trânsito de veículos no sentido indicado.',
            'acao': 'Não entrar na via',
            'penalidade': 'Multa e pontos na carteira',
            'cores': ['vermelho', 'branco'],
            'formas': ['circular'],
            'tipo': 'obrigatorio'
        },
        'proibido virar à esquerda': {
            'significado': 'Proíbe virar à esquerda na próxima interseção.',
            'acao': 'Não virar à esquerda',
            'penalidade': 'Multa e pontos na carteira',
            'cores': ['vermelho', 'branco'],
            'formas': ['circular'],
            'tipo': 'obrigatorio'
        },
        'proibido virar à direita': {
            'significado': 'Proíbe virar à direita na próxima interseção.',
            'acao': 'Não virar à direita',
            'penalidade': 'Multa e pontos na carteira',
            'cores': ['vermelho', 'branco'],
            'formas': ['circular'],
            'tipo': 'obrigatorio'
        },
        'proibido retornar à esquerda': {
            'significado': 'Proíbe fazer retorno para a esquerda.',
            'acao': 'Não fazer retorno à esquerda',
            'penalidade': 'Multa e pontos na carteira',
            'cores': ['vermelho', 'branco'],
            'formas': ['circular'],
            'tipo': 'obrigatorio'
        },
        'proibido retornar à direita': {
            'significado': 'Proíbe fazer retorno para a direita.',
            'acao': 'Não fazer retorno à direita',
            'penalidade': 'Multa e pontos na carteira',
            'cores': ['vermelho', 'branco'],
            'formas': ['circular'],
            'tipo': 'obrigatorio'
        },
        'proibido estacionar': {
            'significado': 'Proíbe estacionar o veículo no local.',
            'acao': 'Não estacionar',
            'penalidade': 'Multa e remoção do veículo',
            'cores': ['vermelho', 'branco'],
            'formas': ['circular'],
            'tipo': 'obrigatorio'
        },
        'estacionamento regulamentado': {
            'significado': 'Indica área permitida para estacionamento com regulamentação.',
            'acao': 'Estacionar seguindo regulamentação',
            'penalidade': 'Multa se não seguir regras',
            'cores': ['azul', 'branco'],
            'formas': ['circular'],
            'tipo': 'regulamentacao'
        },
        'proibido parar e estacionar': {
            'significado': 'Proíbe parar e estacionar o veículo no local.',
            'acao': 'Não parar nem estacionar',
            'penalidade': 'Multa e remoção do veículo',
            'cores': ['vermelho', 'branco'],
            'formas': ['circular'],
            'tipo': 'obrigatorio'
        },
        'proibido ultrapassar': {
            'significado': 'Proíbe ultrapassar outros veículos na via.',
            'acao': 'Não ultrapassar',
            'penalidade': 'Multa e pontos na carteira',
            'cores': ['vermelho', 'branco'],
            'formas': ['circular'],
            'tipo': 'obrigatorio'
        },
        'velocidade máxima permitida': {
            'significado': 'Indica a velocidade máxima permitida na via.',
            'acao': 'Respeitar o limite de velocidade',
            'penalidade': 'Multa e pontos na carteira',
            'cores': ['vermelho', 'branco'],
            'formas': ['circular'],
            'tipo': 'regulamentacao'
        }
    }
    
    # Enriquece as placas de regulamentação
    for codigo, placa in placas_reg.items():
        nome_lower = placa['nome'].lower()
        
        # Procura por correspondências no dicionário de enriquecimento
        for key, data in enrichment_data.items():
            if key in nome_lower:
                placa.update(data)
                break
        
        # Se não encontrou correspondência, adiciona dados padrão
        if 'significado' not in placa:
            placa.update({
                'significado': f'Placa de regulamentação: {placa["nome"]}',
                'acao': 'Seguir regulamentação indicada',
                'penalidade': 'Multa e pontos na carteira',
                'cores': ['vermelho', 'branco'],
                'formas': ['circular'],
                'tipo': 'regulamentacao'
            })
    
    # Enriquece as placas de advertência
    for codigo, placa in placas_adv.items():
        placa.update({
            'significado': f'Advertência: {placa["nome"]}',
            'acao': 'Reduzir velocidade e atenção',
            'penalidade': 'Não aplicável (advertência)',
            'cores': ['amarelo', 'preto'],
            'formas': ['triangular'],
            'tipo': 'advertencia'
        })
    
    return placas_reg, placas_adv

def main():
    """Função principal"""
    print("🚦 EXTRAÇÃO DETALHADA DE PLACAS DE SINALIZAÇÃO")
    print("=" * 60)
    
    # Arquivos PDF
    pdf_regulamentacao = "copy_of___01___MBST_Vol_I___Sin_Vert_Regulamentacao_F_pages_deleted (1).pdf"
    pdf_advertencia = "(Microsoft Word - - 02 - MBST Vol. II - Sin. Vert. Advert_352ncia).pdf"
    
    # Extrai conteúdo dos PDFs
    print(f"\n📖 Extraindo conteúdo de: {pdf_regulamentacao}")
    content_reg = extract_pdf_content(pdf_regulamentacao)
    
    print(f"📖 Extraindo conteúdo de: {pdf_advertencia}")
    content_adv = extract_pdf_content(pdf_advertencia)
    
    if not content_reg and not content_adv:
        print("❌ Falha ao extrair conteúdo dos PDFs")
        return
    
    # Parse das placas
    print("\n🔍 Analisando placas de regulamentação...")
    placas_reg = parse_sinalizacao_regulamentacao(content_reg)
    
    print("🔍 Analisando placas de advertência...")
    placas_adv = parse_sinalizacao_advertencia(content_adv)
    
    # Enriquece os dados
    print("✨ Enriquecendo dados das placas...")
    placas_reg, placas_adv = enrich_placas_data(placas_reg, placas_adv)
    
    # Salva resultados
    resultados = {
        'regulamentacao': placas_reg,
        'advertencia': placas_adv,
        'total_regulamentacao': len(placas_reg),
        'total_advertencia': len(placas_adv)
    }
    
    with open('placas_detalhadas.json', 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ RESULTADOS:")
    print(f"   🚦 Placas de Regulamentação: {len(placas_reg)}")
    print(f"   ⚠️  Placas de Advertência: {len(placas_adv)}")
    print(f"   💾 Dados salvos em 'placas_detalhadas.json'")
    
    # Mostra algumas placas como exemplo
    print(f"\n📋 EXEMPLOS DE PLACAS ENCONTRADAS:")
    
    print(f"\n🚦 REGULAMENTAÇÃO (primeiras 5):")
    for i, (codigo, placa) in enumerate(list(placas_reg.items())[:5]):
        print(f"   {i+1}. {codigo}: {placa['nome']}")
        print(f"      📄 Página: {placa['pagina']}")
        print(f"      🎨 Cores: {', '.join(placa.get('cores', []))}")
        print(f"      🔷 Formas: {', '.join(placa.get('formas', []))}")
    
    if placas_adv:
        print(f"\n⚠️  ADVERTÊNCIA (primeiras 5):")
        for i, (codigo, placa) in enumerate(list(placas_adv.items())[:5]):
            print(f"   {i+1}. {codigo}: {placa['nome']}")
            print(f"      📄 Página: {placa['pagina']}")
            print(f"      🎨 Cores: {', '.join(placa.get('cores', []))}")
            print(f"      🔷 Formas: {', '.join(placa.get('formas', []))}")
    
    return resultados

if __name__ == "__main__":
    main()
