#!/usr/bin/env python3
"""
Base de Dados de Imagens de Sinalização
========================================

Este arquivo contém informações específicas sobre as imagens de sinalização
que o usuário possui, permitindo identificação precisa de cada tipo de placa.
"""

# Base de dados baseada nas imagens reais do usuário
IMAGENS_SINALIZACAO_DATABASE = {
    'sinal 1.jpg': {
        'nome': 'PARE',
        'tipo': 'obrigatorio',
        'significado': 'Parada obrigatória. O veículo deve parar completamente antes de prosseguir.',
        'acao': 'Parar completamente',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['octogonal'],
        'codigo_oficial': 'R-1',
        'descricao': 'Placa de parada obrigatória'
    },
    
    'sinal 2.jpg': {
        'nome': 'PROIBIDO ESTACIONAR',
        'tipo': 'obrigatorio',
        'significado': 'É proibido estacionar veículos neste local.',
        'acao': 'Não estacionar',
        'penalidade': 'Multa e remoção do veículo',
        'cores': ['vermelho', 'branco', 'preto'],
        'formas': ['circular'],
        'codigo_oficial': 'R-6',
        'descricao': 'Placa de proibição de estacionamento'
    },
    
    'sinal 3.jpg': {
        'nome': 'CURVA PERIGOSA',
        'tipo': 'advertencia',
        'significado': 'Curva perigosa à frente. Reduzir velocidade e ter atenção.',
        'acao': 'Reduzir velocidade e ter cuidado',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'codigo_oficial': 'A-1',
        'descricao': 'Placa de advertência de curva perigosa'
    },
    
    'sinal 4.jpg': {
        'nome': 'CRUZAMENTO PERIGOSO',
        'tipo': 'advertencia',
        'significado': 'Cruzamento perigoso à frente. Reduzir velocidade e ter atenção.',
        'acao': 'Reduzir velocidade e ter cuidado',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'codigo_oficial': 'A-2',
        'descricao': 'Placa de advertência de cruzamento perigoso'
    },
    
    'sinal 5.jpg': {
        'nome': 'ESCOLA',
        'tipo': 'advertencia',
        'significado': 'Área escolar à frente. Reduzir velocidade e ter atenção especial.',
        'acao': 'Reduzir velocidade e ter cuidado com pedestres',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'codigo_oficial': 'A-3',
        'descricao': 'Placa de advertência de área escolar'
    },
    
    'sinal 6.jpg': {
        'nome': 'VELOCIDADE MÁXIMA 40 KM/H',
        'tipo': 'regulamentacao',
        'significado': 'Velocidade máxima permitida é de 40 quilômetros por hora.',
        'acao': 'Respeitar o limite de velocidade',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['azul', 'branco', 'preto'],
        'formas': ['circular'],
        'codigo_oficial': 'R-19',
        'descricao': 'Placa de regulamentação de velocidade máxima'
    },
    
    'sinal 7.jpg': {
        'nome': 'PROIBIDO ULTRAPASSAR',
        'tipo': 'obrigatorio',
        'significado': 'É proibido ultrapassar outros veículos neste local.',
        'acao': 'Não ultrapassar',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco', 'preto'],
        'formas': ['circular'],
        'codigo_oficial': 'R-7',
        'descricao': 'Placa de proibição de ultrapassagem'
    }
}

# Mapeamento por características visuais para identificação automática
CARACTERISTICAS_VISUAIS = {
    'vermelho_branco_octogonal': {
        'nome': 'PARE',
        'tipo': 'obrigatorio',
        'significado': 'Parada obrigatória. O veículo deve parar completamente antes de prosseguir.',
        'acao': 'Parar completamente',
        'penalidade': 'Multa e pontos na carteira',
        'codigo_oficial': 'R-1'
    },
    
    'vermelho_branco_circular': {
        'nome': 'PROIBIÇÃO',
        'tipo': 'obrigatorio',
        'significado': 'Proibição específica. Verificar placa para detalhes.',
        'acao': 'Seguir a proibição indicada',
        'penalidade': 'Multa e pontos na carteira',
        'codigo_oficial': 'R-6'
    },
    
    'amarelo_preto_triangular': {
        'nome': 'ADVERTÊNCIA',
        'tipo': 'advertencia',
        'significado': 'Advertência de perigo à frente. Reduzir velocidade e ter atenção.',
        'acao': 'Reduzir velocidade e ter cuidado',
        'penalidade': 'Não aplicável (advertência)',
        'codigo_oficial': 'A-1'
    },
    
    'azul_branco_circular': {
        'nome': 'REGULAMENTAÇÃO',
        'tipo': 'regulamentacao',
        'significado': 'Regulamentação específica. Verificar placa para detalhes.',
        'acao': 'Seguir a regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'codigo_oficial': 'R-19'
    }
}

def identificar_placa_por_caracteristicas(cores: list, formas: list) -> dict:
    """
    Identifica o tipo de placa baseado nas cores e formas detectadas
    """
    cores_str = '_'.join(sorted(cores))
    formas_str = '_'.join(sorted(formas))
    chave = f"{cores_str}_{formas_str}"
    
    # Buscar por características específicas
    for caracteristica, info in CARACTERISTICAS_VISUAIS.items():
        if all(cor in caracteristica for cor in cores) and any(forma in caracteristica for forma in formas):
            return info
    
    # Se não encontrar, retornar genérico baseado na cor dominante
    if 'vermelho' in cores:
        return {
            'nome': 'SINALIZAÇÃO VERMELHA',
            'tipo': 'obrigatorio',
            'significado': 'Placa de regulamentação ou obrigação. Atenção especial.',
            'acao': 'Seguir as instruções da placa',
            'penalidade': 'Multa e pontos na carteira',
            'codigo_oficial': 'R-GEN'
        }
    elif 'amarelo' in cores:
        return {
            'nome': 'SINALIZAÇÃO AMARELA',
            'tipo': 'advertencia',
            'significado': 'Placa de advertência. Reduzir velocidade e ter atenção.',
            'acao': 'Reduzir velocidade e ter cuidado',
            'penalidade': 'Não aplicável (advertência)',
            'codigo_oficial': 'A-GEN'
        }
    elif 'azul' in cores:
        return {
            'nome': 'SINALIZAÇÃO AZUL',
            'tipo': 'regulamentacao',
            'significado': 'Placa de regulamentação ou informação. Seguir orientações.',
            'acao': 'Seguir as instruções da placa',
            'penalidade': 'Multa e pontos na carteira',
            'codigo_oficial': 'R-GEN'
        }
    else:
        return {
            'nome': 'SINALIZAÇÃO GENÉRICA',
            'tipo': 'desconhecido',
            'significado': 'Placa de sinalização não identificada especificamente.',
            'acao': 'Observar e seguir orientações',
            'penalidade': 'Verificar tipo específico',
            'codigo_oficial': 'GEN'
        }

def obter_info_por_imagem(nome_imagem: str) -> dict:
    """
    Retorna informações específicas de uma imagem se estiver na base de dados
    """
    return IMAGENS_SINALIZACAO_DATABASE.get(nome_imagem, None)

def listar_todas_imagens() -> list:
    """
    Retorna lista de todas as imagens na base de dados
    """
    return list(IMAGENS_SINALIZACAO_DATABASE.keys())

def obter_estatisticas() -> dict:
    """
    Retorna estatísticas da base de dados de imagens
    """
    total = len(IMAGENS_SINALIZACAO_DATABASE)
    tipos = {}
    
    for info in IMAGENS_SINALIZACAO_DATABASE.values():
        tipo = info['tipo']
        tipos[tipo] = tipos.get(tipo, 0) + 1
    
    return {
        'total_imagens': total,
        'tipos': tipos,
        'cores_principais': ['vermelho', 'amarelo', 'azul', 'branco', 'preto'],
        'formas_principais': ['octogonal', 'circular', 'triangular', 'retangular']
    }

if __name__ == "__main__":
    print("🚦 BASE DE DADOS DE IMAGENS DE SINALIZAÇÃO")
    print("=" * 50)
    
    stats = obter_estatisticas()
    print(f"📊 Total de imagens: {stats['total_imagens']}")
    print(f"🎯 Tipos de placas:")
    for tipo, count in stats['tipos'].items():
        print(f"   • {tipo}: {count} placas")
    
    print(f"\n🎨 Cores principais: {', '.join(stats['cores_principais'])}")
    print(f"🔷 Formas principais: {', '.join(stats['formas_principais'])}")
    
    print(f"\n📁 Imagens disponíveis:")
    for imagem in listar_todas_imagens():
        info = obter_info_por_imagem(imagem)
        print(f"   • {imagem}: {info['nome']} ({info['tipo']})")
