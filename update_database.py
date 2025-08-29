#!/usr/bin/env python3
"""
Script para atualizar a base de dados de sinalização com novas placas
"""

import json
import re

def load_placas_data():
    """Carrega os dados das placas extraídas dos PDFs"""
    try:
        with open('placas_detalhadas.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo 'placas_detalhadas.json' não encontrado!")
        print("💡 Execute primeiro o script 'extract_detailed_sinalizacao.py'")
        return None

def create_database_entry(placa_data):
    """Cria uma entrada para a base de dados baseada nos dados da placa"""
    
    # Mapeia o tipo para o formato da base de dados
    tipo_mapping = {
        'obrigatorio': 'obrigatorio',
        'regulamentacao': 'regulamentacao',
        'advertencia': 'advertencia'
    }
    
    # Determina o tipo correto
    tipo = tipo_mapping.get(placa_data.get('tipo', 'regulamentacao'), 'regulamentacao')
    
    # Cria a entrada da base de dados
    entry = {
        'nome': placa_data['nome'],
        'codigo': placa_data['codigo'],
        'significado': placa_data.get('significado', f'Placa de {tipo}: {placa_data["nome"]}'),
        'acao': placa_data.get('acao', 'Seguir regulamentação indicada'),
        'penalidade': placa_data.get('penalidade', 'Multa e pontos na carteira'),
        'cores': placa_data.get('cores', ['vermelho', 'branco']),
        'formas': placa_data.get('formas', ['circular']),
        'tipo': tipo,
        'pagina': placa_data.get('pagina', 0)
    }
    
    return entry

def update_base_dados_sinalizacao():
    """Atualiza o arquivo base_dados_sinalizacao.py com as novas placas"""
    
    # Carrega os dados das placas
    placas_data = load_placas_data()
    if not placas_data:
        return False
    
    print("🚦 ATUALIZANDO BASE DE DADOS DE SINALIZAÇÃO")
    print("=" * 60)
    
    # Combina placas de regulamentação e advertência
    all_placas = {}
    
    # Adiciona placas de regulamentação
    for codigo, placa in placas_data['regulamentacao'].items():
        all_placas[codigo] = placa
    
    # Adiciona placas de advertência
    for codigo, placa in placas_data['advertencia'].items():
        all_placas[codigo] = placa
    
    print(f"📊 Total de placas encontradas: {len(all_placas)}")
    print(f"   🚦 Regulamentação: {len(placas_data['regulamentacao'])}")
    print(f"   ⚠️  Advertência: {len(placas_data['advertencia'])}")
    
    # Cria as entradas da base de dados
    database_entries = {}
    codigos_oficiais = {}
    
    for codigo, placa in all_placas.items():
        # Cria chave para a base de dados
        key = codigo.lower().replace('-', '_').replace('a', '_a').replace('b', '_b').replace('c', '_c')
        
        # Cria entrada da base de dados
        entry = create_database_entry(placa)
        database_entries[key] = entry
        
        # Adiciona ao dicionário de códigos oficiais
        codigos_oficiais[codigo] = entry
    
    print(f"\n✨ Entradas da base de dados criadas: {len(database_entries)}")
    
    # Gera o código Python para o arquivo atualizado
    python_code = generate_python_code(database_entries, codigos_oficiais)
    
    # Salva o arquivo atualizado
    with open('base_dados_sinalizacao_atualizada.py', 'w', encoding='utf-8') as f:
        f.write(python_code)
    
    print(f"💾 Base de dados atualizada salva em 'base_dados_sinalizacao_atualizada.py'")
    
    # Mostra algumas estatísticas
    print(f"\n📋 ESTATÍSTICAS DA NOVA BASE:")
    
    tipos_count = {}
    cores_count = {}
    formas_count = {}
    
    for entry in database_entries.values():
        # Conta tipos
        tipo = entry['tipo']
        tipos_count[tipo] = tipos_count.get(tipo, 0) + 1
        
        # Conta cores
        for cor in entry['cores']:
            cores_count[cor] = cores_count.get(cor, 0) + 1
        
        # Conta formas
        for forma in entry['formas']:
            formas_count[forma] = formas_count.get(forma, 0) + 1
    
    print(f"   🏷️  Tipos:")
    for tipo, count in sorted(tipos_count.items()):
        print(f"      {tipo}: {count}")
    
    print(f"   🎨 Cores:")
    for cor, count in sorted(cores_count.items()):
        print(f"      {cor}: {count}")
    
    print(f"   🔷 Formas:")
    for forma, count in sorted(formas_count.items()):
        print(f"      {forma}: {count}")
    
    return True

def generate_python_code(database_entries, codigos_oficiais):
    """Gera o código Python para o arquivo atualizado"""
    
    # Cabeçalho do arquivo
    header = '''#!/usr/bin/env python3
"""
Base de Dados Completa das Placas de Sinalização Brasileiras
============================================================

Este arquivo contém a base de dados oficial com códigos R-1, R-2, etc.
e A-1, A-2, etc. baseada nas tabelas oficiais do Código de Trânsito Brasileiro.
Atualizada com dados extraídos dos PDFs oficiais do MBST.
"""

# Base de dados oficial das placas de sinalização brasileiras
SINALIZACAO_DATABASE = {
'''
    
    # Corpo da base de dados
    body = ""
    for key, entry in sorted(database_entries.items()):
        body += f"    '{key}': {{\n"
        body += f"        'nome': '{entry['nome']}',\n"
        body += f"        'codigo': '{entry['codigo']}',\n"
        body += f"        'significado': '{entry['significado']}',\n"
        body += f"        'acao': '{entry['acao']}',\n"
        body += f"        'penalidade': '{entry['penalidade']}',\n"
        body += f"        'cores': {entry['cores']},\n"
        body += f"        'formas': {entry['formas']},\n"
        body += f"        'tipo': '{entry['tipo']}',\n"
        body += f"        'pagina': {entry['pagina']}\n"
        body += f"    }},\n"
    
    # Dicionário de códigos oficiais
    codigos_section = '''

# Base de dados por código oficial
CODIGOS_OFICIAIS = {
'''
    
    for codigo, entry in sorted(codigos_oficiais.items()):
        codigos_section += f"    '{codigo}': SINALIZACAO_DATABASE['{entry['codigo'].lower().replace('-', '_').replace('a', '_a').replace('b', '_b').replace('c', '_c')}'],\n"
    
    # Funções de busca
    functions = '''

def buscar_por_codigo(codigo: str):
    """Busca placa de sinalização por código oficial (ex: R-1, R-4a, A-1a)"""
    codigo = codigo.upper().strip()
    
    if codigo in CODIGOS_OFICIAIS:
        return CODIGOS_OFICIAIS[codigo]
    
    # Busca por código similar
    for cod, info in CODIGOS_OFICIAIS.items():
        if codigo in cod or cod in codigo:
            return info
    
    return None

def buscar_por_nome(nome: str):
    """Busca placas de sinalização por nome ou parte do nome"""
    nome = nome.lower().strip()
    resultados = []
    
    for key, info in SINALIZACAO_DATABASE.items():
        if (nome in info['nome'].lower() or 
            nome in info['significado'].lower() or
            nome in info['acao'].lower()):
            resultados.append(info)
    
    return resultados

def listar_todos_codigos():
    """Lista todas as placas com seus códigos oficiais"""
    return list(CODIGOS_OFICIAIS.values())

def buscar_por_tipo(tipo: str):
    """Busca placas por tipo (obrigatorio, regulamentacao, advertencia)"""
    tipo = tipo.lower().strip()
    resultados = []
    
    for info in SINALIZACAO_DATABASE.values():
        if tipo in info['tipo']:
            resultados.append(info)
    
    return resultados

def main():
    """Função principal para demonstração da base de dados"""
    print("🚦 BASE DE DADOS OFICIAL DAS PLACAS DE SINALIZAÇÃO BRASILEIRAS")
    print("=" * 70)
    print("📋 Códigos oficiais R-1, R-2, etc. e A-1, A-2, etc. baseados no CTB")
    print("📖 Significados completos com ações e penalidades")
    print("=" * 70)
    
    while True:
        print("\\n📋 MENU DE CONSULTA")
        print("1. 🔍 Buscar por código (ex: R-1, R-4a, A-1a)")
        print("2. 📖 Buscar por nome ou descrição")
        print("3. 📋 Listar todos os códigos")
        print("4. 🎯 Buscar por tipo (obrigatório, regulamentação, advertência)")
        print("5. 🎨 Buscar por cor")
        print("6. 🔷 Buscar por forma")
        print("0. ❌ Sair")
        print("-" * 40)
        
        try:
            choice = input("Escolha uma opção: ").strip()
            
            if choice == '1':
                codigo = input("Digite o código (ex: R-1, A-1a): ").strip()
                resultado = buscar_por_codigo(codigo)
                
                if resultado:
                    print(f"\\n✅ PLACA ENCONTRADA:")
                    print(f"   🚦 Código: {resultado['codigo']}")
                    print(f"   📖 Nome: {resultado['nome']}")
                    print(f"   💡 Significado: {resultado['significado']}")
                    print(f"   ⚠️  Ação: {resultado['acao']}")
                    print(f"   💰 Penalidade: {resultado['penalidade']}")
                    print(f"   🎨 Cores: {', '.join(resultado['cores'])}")
                    print(f"   🔷 Formas: {', '.join(resultado['formas'])}")
                    print(f"   🏷️  Tipo: {resultado['tipo']}")
                    print(f"   📄 Página: {resultado['pagina']}")
                else:
                    print(f"❌ Código '{codigo}' não encontrado!")
                    print("💡 Dicas: Use formato R-1, R-4a, A-1a, etc.")
                
            elif choice == '2':
                nome = input("Digite o nome ou descrição: ").strip()
                resultados = buscar_por_nome(nome)
                
                if resultados:
                    print(f"\\n✅ {len(resultados)} PLACA(S) ENCONTRADA(S):")
                    for i, resultado in enumerate(resultados, 1):
                        print(f"\\n{i}. 🚦 {resultado['nome']} ({resultado['codigo']})")
                        print(f"   💡 {resultado['significado']}")
                        print(f"   ⚠️  {resultado['acao']}")
                        print(f"   💰 {resultado['penalidade']}")
                else:
                    print(f"❌ Nenhuma placa encontrada para '{nome}'")
                
            elif choice == '3':
                print(f"\\n📋 TODOS OS CÓDIGOS OFICIAIS ({len(CODIGOS_OFICIAIS)} placas):")
                print("-" * 50)
                
                for codigo, info in sorted(CODIGOS_OFICIAIS.items()):
                    print(f"🚦 {codigo}: {info['nome']}")
                    print(f"   💡 {info['significado'][:60]}...")
                    print(f"   ⚠️  {info['acao']}")
                    print(f"   💰 {info['penalidade']}")
                    print(f"   🎨 Cores: {', '.join(info['cores'])}")
                    print(f"   🔷 Formas: {', '.join(info['formas'])}")
                    print(f"   🏷️  Tipo: {info['tipo']}")
                    print(f"   📄 Página: {info['pagina']}")
                    print("-" * 30)
                
            elif choice == '4':
                tipo = input("Digite o tipo (obrigatorio/regulamentacao/advertencia): ").strip()
                resultados = buscar_por_tipo(tipo)
                
                if resultados:
                    print(f"\\n✅ {len(resultados)} PLACA(S) DO TIPO '{tipo.upper()}':")
                    for i, resultado in enumerate(resultados, 1):
                        print(f"\\n{i}. 🚦 {resultado['nome']} ({resultado['codigo']})")
                        print(f"   💡 {resultado['significado']}")
                        print(f"   ⚠️  {resultado['acao']}")
                else:
                    print(f"❌ Nenhuma placa do tipo '{tipo}' encontrada")
                
            elif choice == '5':
                cor = input("Digite a cor (vermelho/azul/amarelo/branco/preto): ").strip()
                resultados = []
                
                for info in SINALIZACAO_DATABASE.values():
                    if cor.lower() in [c.lower() for c in info['cores']]:
                        resultados.append(info)
                
                if resultados:
                    print(f"\\n✅ {len(resultados)} PLACA(S) COM COR '{cor.upper()}':")
                    for i, resultado in enumerate(resultados, 1):
                        print(f"\\n{i}. 🚦 {resultado['nome']} ({resultado['codigo']})")
                        print(f"   🎨 Cores: {', '.join(resultado['cores'])}")
                        print(f"   💡 {resultado['significado']}")
                else:
                    print(f"❌ Nenhuma placa com cor '{cor}' encontrada")
                
            elif choice == '6':
                forma = input("Digite a forma (circular/triangular/octogonal/retangular): ").strip()
                resultados = []
                
                for info in SINALIZACAO_DATABASE.values():
                    if forma.lower() in [f.lower() for f in info['formas']]:
                        resultados.append(info)
                
                if resultados:
                    print(f"\\n✅ {len(resultados)} PLACA(S) COM FORMA '{forma.upper()}':")
                    for i, resultado in enumerate(resultados, 1):
                        print(f"\\n{i}. 🚦 {resultado['nome']} ({resultado['codigo']})")
                        print(f"   🔷 Formas: {', '.join(resultado['formas'])}")
                        print(f"   💡 {resultado['significado']}")
                else:
                    print(f"❌ Nenhuma placa com forma '{forma}' encontrada")
                
            elif choice == '0':
                print("\\n👋 Obrigado por usar a Base de Dados de Sinalização!")
                print("   🚦 Até logo! 📖")
                break
                
            else:
                print("❌ Opção inválida! Escolha de 0 a 6.")
            
        except KeyboardInterrupt:
            print("\\n\\n⏹️  Aplicação interrompida")
            break
        except Exception as e:
            print(f"\\n❌ Erro: {e}")
        
        input("\\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()
'''
    
    # Combina todas as partes
    full_code = header + body + "}\n" + codigos_section + "}\n" + functions
    
    return full_code

if __name__ == "__main__":
    update_base_dados_sinalizacao()
