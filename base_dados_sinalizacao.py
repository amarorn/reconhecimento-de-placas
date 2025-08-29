#!/usr/bin/env python3
"""
Base de Dados Completa das Placas de Sinalização Brasileiras
============================================================

Este arquivo contém a base de dados oficial com códigos R-1, R-2, etc.
e A-1, A-2, etc. baseada nas tabelas oficiais do Código de Trânsito Brasileiro.
Atualizada com dados extraídos dos PDFs oficiais do MBST.
"""

# Base de dados oficial das placas de sinalização brasileiras
SINALIZACAO_DATABASE = {
    'a_10_a': {
        'nome': 'Entroncamento oblíquo à esquerda',
        'codigo': 'A-10a',
        'significado': 'Advertência: Entroncamento oblíquo à esquerda',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 54
    },
    'a_10_b': {
        'nome': 'Entroncamento oblíquo à direita',
        'codigo': 'A-10b',
        'significado': 'Advertência: Entroncamento oblíquo à direita',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 54
    },
    'a_12': {
        'nome': 'Interseção em círculo',
        'codigo': 'A-12',
        'significado': 'Advertência: Interseção em círculo',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 63
    },
    'a_13_a': {
        'nome': 'Confluência à esquerda',
        'codigo': 'A-13a',
        'significado': 'Advertência: Confluência à esquerda',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 56
    },
    'a_13_b': {
        'nome': 'Confluência à direita',
        'codigo': 'A-13b',
        'significado': 'Advertência: Confluência à direita',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 56
    },
    'a_14': {
        'nome': 'Semáforo à frente',
        'codigo': 'A-14',
        'significado': 'Advertência: Semáforo à frente',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 65
    },
    'a_15': {
        'nome': 'Parada obrigatória à frente',
        'codigo': 'A-15',
        'significado': 'Advertência: Parada obrigatória à frente',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 67
    },
    'a_16': {
        'nome': 'Bonde / VLT',
        'codigo': 'A-16',
        'significado': 'Advertência: Bonde / VLT',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 69
    },
    'a_17': {
        'nome': 'Pista irregular',
        'codigo': 'A-17',
        'significado': 'Advertência: Pista irregular',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 76
    },
    'a_18': {
        'nome': 'Saliência ou lombada',
        'codigo': 'A-18',
        'significado': 'Advertência: Saliência ou lombada',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 77
    },
    'a_19': {
        'nome': 'Depressão',
        'codigo': 'A-19',
        'significado': 'Advertência: Depressão',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 78
    },
    'a_1_a': {
        'nome': 'Curva acentuada à esquerda',
        'codigo': 'A-1a',
        'significado': 'Advertência: Curva acentuada à esquerda',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 34
    },
    'a_1_b': {
        'nome': 'Curva acentuada à direita',
        'codigo': 'A-1b',
        'significado': 'Advertência: Curva acentuada à direita',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 34
    },
    'a_20_a': {
        'nome': 'Declive acentuado',
        'codigo': 'A-20a',
        'significado': 'Advertência: Declive acentuado',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 79
    },
    'a_20_b': {
        'nome': 'Aclive acentuado',
        'codigo': 'A-20b',
        'significado': 'Advertência: Aclive acentuado',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 79
    },
    'a_21_a': {
        'nome': 'Estreitamento de pista ao centro',
        'codigo': 'A-21a',
        'significado': 'Advertência: Estreitamento de pista ao centro',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 82
    },
    'a_21_b': {
        'nome': 'Estreitamento de pista à esquerda',
        'codigo': 'A-21b',
        'significado': 'Advertência: Estreitamento de pista à esquerda',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 82
    },
    'a_21_c': {
        'nome': 'Estreitamento de pista à direita',
        'codigo': 'A-21c',
        'significado': 'Advertência: Estreitamento de pista à direita',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 82
    },
    'a_21d': {
        'nome': 'Alargamento de pista à esquerda',
        'codigo': 'A-21d',
        'significado': 'Advertência: Alargamento de pista à esquerda',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 84
    },
    'a_21e': {
        'nome': 'Alargamento de pista à direita',
        'codigo': 'A-21e',
        'significado': 'Advertência: Alargamento de pista à direita',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 84
    },
    'a_22': {
        'nome': 'Ponte estreita',
        'codigo': 'A-22',
        'significado': 'Advertência: Ponte estreita',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 86
    },
    'a_23': {
        'nome': 'Ponte móvel',
        'codigo': 'A-23',
        'significado': 'Advertência: Ponte móvel',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 70
    },
    'a_24': {
        'nome': 'Obras',
        'codigo': 'A-24',
        'significado': 'Advertência: Obras',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 92
    },
    'a_25': {
        'nome': 'Mão dupla adiante',
        'codigo': 'A-25',
        'significado': 'Advertência: Mão dupla adiante',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 94
    },
    'a_26_a': {
        'nome': 'Sentido único',
        'codigo': 'A-26a',
        'significado': 'Advertência: Sentido único',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 95
    },
    'a_26_b': {
        'nome': 'Sentido duplo',
        'codigo': 'A-26b',
        'significado': 'Advertência: Sentido duplo',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 95
    },
    'a_27': {
        'nome': 'Área com desmoronamento',
        'codigo': 'A-27',
        'significado': 'Advertência: Área com desmoronamento',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 98
    },
    'a_28': {
        'nome': 'Pista escorregadia',
        'codigo': 'A-28',
        'significado': 'Advertência: Pista escorregadia',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 100
    },
    'a_29': {
        'nome': 'Projeção de cascalho',
        'codigo': 'A-29',
        'significado': 'Advertência: Projeção de cascalho',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 102
    },
    'a_2_a': {
        'nome': 'Curva esquerda',
        'codigo': 'A-2a',
        'significado': 'Advertência: Curva esquerda',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 37
    },
    'a_2_b': {
        'nome': 'Curva à direita',
        'codigo': 'A-2b',
        'significado': 'Advertência: Curva à direita',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 37
    },
    'a_30_a': {
        'nome': 'Trânsito de ciclistas',
        'codigo': 'A-30a',
        'significado': 'Advertência: Trânsito de ciclistas',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 108
    },
    'a_30_b': {
        'nome': 'Passagem sinalizada de ciclistas',
        'codigo': 'A-30b',
        'significado': 'Advertência: Passagem sinalizada de ciclistas',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 109
    },
    'a_31': {
        'nome': 'Trânsito de tratores ou maquinária agrícola',
        'codigo': 'A-31',
        'significado': 'Advertência: Trânsito de tratores ou maquinária agrícola',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 103
    },
    'a_32_a': {
        'nome': 'Trânsito de pedestres',
        'codigo': 'A-32a',
        'significado': 'Advertência: Trânsito de pedestres',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 111
    },
    'a_32_b': {
        'nome': 'Passagem sinalizada de pedestres',
        'codigo': 'A-32b',
        'significado': 'Advertência: Passagem sinalizada de pedestres',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 112
    },
    'a_33_a': {
        'nome': 'Área escolar',
        'codigo': 'A-33a',
        'significado': 'Advertência: Área escolar',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 113
    },
    'a_33_b': {
        'nome': 'Passagem sinalizada de escolares',
        'codigo': 'A-33b',
        'significado': 'Advertência: Passagem sinalizada de escolares',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 114
    },
    'a_34': {
        'nome': 'Crianças',
        'codigo': 'A-34',
        'significado': 'Advertência: Crianças',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 115
    },
    'a_35': {
        'nome': 'Animais',
        'codigo': 'A-35',
        'significado': 'Advertência: Animais',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 104
    },
    'a_36': {
        'nome': 'Animais selvagens',
        'codigo': 'A-36',
        'significado': 'Advertência: Animais selvagens',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 104
    },
    'a_37': {
        'nome': 'Altura limitada',
        'codigo': 'A-37',
        'significado': 'Advertência: Altura limitada',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 117
    },
    'a_38': {
        'nome': 'Largura limitada',
        'codigo': 'A-38',
        'significado': 'Advertência: Largura limitada',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 118
    },
    'a_39': {
        'nome': 'Passagem de nível sem barreira',
        'codigo': 'A-39',
        'significado': 'Advertência: Passagem de nível sem barreira',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 71
    },
    'a_3_a': {
        'nome': 'Pista sinuosa à esquerda',
        'codigo': 'A-3a',
        'significado': 'Advertência: Pista sinuosa à esquerda',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 41
    },
    'a_3_b': {
        'nome': 'Pista sinuosa à direita',
        'codigo': 'A-3b',
        'significado': 'Advertência: Pista sinuosa à direita',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 41
    },
    'a_40': {
        'nome': 'Passagem de nível com barreira',
        'codigo': 'A-40',
        'significado': 'Advertência: Passagem de nível com barreira',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 71
    },
    'a_41': {
        'nome': 'Cruz de Santo André',
        'codigo': 'A-41',
        'significado': 'Advertência: Cruz de Santo André',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 73
    },
    'a_42_a': {
        'nome': 'Início de pista dupla',
        'codigo': 'A-42a',
        'significado': 'Advertência: Início de pista dupla',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 87
    },
    'a_42_b': {
        'nome': 'Fim de pista dupla',
        'codigo': 'A-42b',
        'significado': 'Advertência: Fim de pista dupla',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 87
    },
    'a_42_c': {
        'nome': 'Pista dividida',
        'codigo': 'A-42c',
        'significado': 'Advertência: Pista dividida',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 89
    },
    'a_43': {
        'nome': 'Aeroporto',
        'codigo': 'A-43',
        'significado': 'Advertência: Aeroporto',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 105
    },
    'a_44': {
        'nome': 'Vento lateral',
        'codigo': 'A-44',
        'significado': 'Advertência: Vento lateral',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 106
    },
    'a_45': {
        'nome': 'Rua sem saída',
        'codigo': 'A-45',
        'significado': 'Advertência: Rua sem saída',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 91
    },
    'a_46': {
        'nome': 'Peso bruto total limitado',
        'codigo': 'A-46',
        'significado': 'Advertência: Peso bruto total limitado',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 119
    },
    'a_47': {
        'nome': 'Peso limitado por eixo',
        'codigo': 'A-47',
        'significado': 'Advertência: Peso limitado por eixo',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 121
    },
    'a_48': {
        'nome': 'Comprimento limitado',
        'codigo': 'A-48',
        'significado': 'Advertência: Comprimento limitado',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 123
    },
    'a_4_a': {
        'nome': 'Curva acentuada em “S” à esquerda',
        'codigo': 'A-4a',
        'significado': 'Advertência: Curva acentuada em “S” à esquerda',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 43
    },
    'a_4_b': {
        'nome': 'Curva acentuada em “S” à direita',
        'codigo': 'A-4b',
        'significado': 'Advertência: Curva acentuada em “S” à direita',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 43
    },
    'a_5_a': {
        'nome': 'Curva em “S” à esquerda',
        'codigo': 'A-5a',
        'significado': 'Advertência: Curva em “S” à esquerda',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 45
    },
    'a_5_b': {
        'nome': 'Curva em “S” à direita',
        'codigo': 'A-5b',
        'significado': 'Advertência: Curva em “S” à direita',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 45
    },
    'a_6': {
        'nome': 'Cruzamento de vias',
        'codigo': 'A-6',
        'significado': 'Advertência: Cruzamento de vias',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 49
    },
    'a_7_a': {
        'nome': 'Via lateral à esquerda',
        'codigo': 'A-7a',
        'significado': 'Advertência: Via lateral à esquerda',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 52
    },
    'a_7_b': {
        'nome': 'Via lateral à direita',
        'codigo': 'A-7b',
        'significado': 'Advertência: Via lateral à direita',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 52
    },
    'a_8': {
        'nome': 'Interseção em “T”',
        'codigo': 'A-8',
        'significado': 'Advertência: Interseção em “T”',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 58
    },
    'a_9': {
        'nome': 'Bifurcação em “Y”',
        'codigo': 'A-9',
        'significado': 'Advertência: Bifurcação em “Y”',
        'acao': 'Reduzir velocidade e atenção',
        'penalidade': 'Não aplicável (advertência)',
        'cores': ['amarelo', 'preto'],
        'formas': ['triangular'],
        'tipo': 'advertencia',
        'pagina': 58
    },
    'r_1': {
        'nome': 'Parada obrigatória',
        'codigo': 'R-1',
        'significado': 'Placa de regulamentação: Parada obrigatória',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 43
    },
    'r_10': {
        'nome': 'Sinais Regulamentação – Pref. Pass.',
        'codigo': 'R-10',
        'significado': 'Placa de regulamentação: Sinais Regulamentação – Pref. Pass.',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 41
    },
    'r_11': {
        'nome': 'Proibido trânsito de veículos de tração animal',
        'codigo': 'R-11',
        'significado': 'Placa de regulamentação: Proibido trânsito de veículos de tração animal',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 111
    },
    'r_12': {
        'nome': 'Proibido trânsito de bicicletas',
        'codigo': 'R-12',
        'significado': 'Placa de regulamentação: Proibido trânsito de bicicletas',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 113
    },
    'r_14': {
        'nome': 'Peso bruto total máximo permitido',
        'codigo': 'R-14',
        'significado': 'Placa de regulamentação: Peso bruto total máximo permitido',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 131
    },
    'r_15': {
        'nome': 'Largura máxima permitida R-16',
        'codigo': 'R-15',
        'significado': 'Placa de regulamentação: Largura máxima permitida R-16',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 42
    },
    'r_16': {
        'nome': 'Largura máxima permitida',
        'codigo': 'R-16',
        'significado': 'Placa de regulamentação: Largura máxima permitida',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 135
    },
    'r_17': {
        'nome': 'Comprimento máximo permitido R-18',
        'codigo': 'R-17',
        'significado': 'Placa de regulamentação: Comprimento máximo permitido R-18',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 4
    },
    'r_18': {
        'nome': 'Comprimento máximo permitido',
        'codigo': 'R-18',
        'significado': 'Placa de regulamentação: Comprimento máximo permitido',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 139
    },
    'r_19': {
        'nome': 'Velocidade máxima permitida',
        'codigo': 'R-19',
        'significado': 'Indica a velocidade máxima permitida na via.',
        'acao': 'Respeitar o limite de velocidade',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 45
    },
    'r_2': {
        'nome': 'Dê a preferência',
        'codigo': 'R-2',
        'significado': 'Placa de regulamentação: Dê a preferência',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 46
    },
    'r_20': {
        'nome': 'Proibido acionar buzina ou sinal sonoro',
        'codigo': 'R-20',
        'significado': 'Placa de regulamentação: Proibido acionar buzina ou sinal sonoro',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 128
    },
    'r_21': {
        'nome': 'Uso obrigatório de corrente R-22',
        'codigo': 'R-21',
        'significado': 'Placa de regulamentação: Uso obrigatório de corrente R-22',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 4
    },
    'r_22': {
        'nome': 'Uso obrigatório de corrente',
        'codigo': 'R-22',
        'significado': 'Placa de regulamentação: Uso obrigatório de corrente',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 130
    },
    'r_23': {
        'nome': 'Conserve-se à direita',
        'codigo': 'R-23',
        'significado': 'Placa de regulamentação: Conserve-se à direita',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 102
    },
    'r_24_a': {
        'nome': 'Sentido de circulação da via/pista',
        'codigo': 'R-24a',
        'significado': 'Placa de regulamentação: Sentido de circulação da via/pista',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 61
    },
    'r_24_b': {
        'nome': 'Passagem obrigatória',
        'codigo': 'R-24b',
        'significado': 'Placa de regulamentação: Passagem obrigatória',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 81
    },
    'r_25_a': {
        'nome': 'Vire à esquerda',
        'codigo': 'R-25a',
        'significado': 'Placa de regulamentação: Vire à esquerda',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 83
    },
    'r_25_b': {
        'nome': 'Vire à direita',
        'codigo': 'R-25b',
        'significado': 'Placa de regulamentação: Vire à direita',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 85
    },
    'r_25_c': {
        'nome': 'Siga em frente ou à esquerda',
        'codigo': 'R-25c',
        'significado': 'Placa de regulamentação: Siga em frente ou à esquerda',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 87
    },
    'r_25d': {
        'nome': 'Siga em frente R-26',
        'codigo': 'R-25d',
        'significado': 'Placa de regulamentação: Siga em frente R-26',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 4
    },
    'r_26': {
        'nome': 'Siga em frente',
        'codigo': 'R-26',
        'significado': 'Placa de regulamentação: Siga em frente',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 93
    },
    'r_28': {
        'nome': 'Duplo sentido de circulação',
        'codigo': 'R-28',
        'significado': 'Placa de regulamentação: Duplo sentido de circulação',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 66
    },
    'r_29': {
        'nome': 'Proibido trânsito de pedestres',
        'codigo': 'R-29',
        'significado': 'Placa de regulamentação: Proibido trânsito de pedestres',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 154
    },
    'r_3': {
        'nome': 'Sentido proibido',
        'codigo': 'R-3',
        'significado': 'Proíbe o trânsito de veículos no sentido indicado.',
        'acao': 'Não entrar na via',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'obrigatorio',
        'pagina': 70
    },
    'r_30': {
        'nome': 'Pedestre, ande pela esquerda',
        'codigo': 'R-30',
        'significado': 'Placa de regulamentação: Pedestre, ande pela esquerda',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 155
    },
    'r_31': {
        'nome': 'Pedestre, ande pela direita',
        'codigo': 'R-31',
        'significado': 'Placa de regulamentação: Pedestre, ande pela direita',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 156
    },
    'r_32': {
        'nome': 'Circulação exclusiva de ônibus',
        'codigo': 'R-32',
        'significado': 'Placa de regulamentação: Circulação exclusiva de ônibus',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 117
    },
    'r_33': {
        'nome': 'Sentido de circulação na rotatória',
        'codigo': 'R-33',
        'significado': 'Placa de regulamentação: Sentido de circulação na rotatória',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 68
    },
    'r_34': {
        'nome': 'Circulação exclusiva de bicicletas',
        'codigo': 'R-34',
        'significado': 'Placa de regulamentação: Circulação exclusiva de bicicletas',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 119
    },
    'r_35_a': {
        'nome': 'Ciclista, transite à esquerda',
        'codigo': 'R-35a',
        'significado': 'Placa de regulamentação: Ciclista, transite à esquerda',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 157
    },
    'r_35_b': {
        'nome': 'Ciclista, transite à direita',
        'codigo': 'R-35b',
        'significado': 'Placa de regulamentação: Ciclista, transite à direita',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 158
    },
    'r_36_a': {
        'nome': 'Ciclistas à esquerda, pedestres à direita',
        'codigo': 'R-36a',
        'significado': 'Placa de regulamentação: Ciclistas à esquerda, pedestres à direita',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 159
    },
    'r_36_b': {
        'nome': 'Pedestres à esquerda, ciclistas à direita',
        'codigo': 'R-36b',
        'significado': 'Placa de regulamentação: Pedestres à esquerda, ciclistas à direita',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 160
    },
    'r_38': {
        'nome': 'Proibido trânsito de ônibus',
        'codigo': 'R-38',
        'significado': 'Placa de regulamentação: Proibido trânsito de ônibus',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 123
    },
    'r_39': {
        'nome': 'Circulação exclusiva de caminhão',
        'codigo': 'R-39',
        'significado': 'Placa de regulamentação: Circulação exclusiva de caminhão',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 125
    },
    'r_40': {
        'nome': '',
        'codigo': 'R-40',
        'significado': 'Placa de regulamentação: ',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 4
    },
    'r_44': {
        'nome': 'R-45',
        'codigo': 'R-44',
        'significado': 'Placa de regulamentação: R-45',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 4
    },
    'r_4_a': {
        'nome': 'Proibido virar à esquerda',
        'codigo': 'R-4a',
        'significado': 'Proíbe virar à esquerda na próxima interseção.',
        'acao': 'Não virar à esquerda',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'obrigatorio',
        'pagina': 73
    },
    'r_4_b': {
        'nome': 'Proibido virar à direita',
        'codigo': 'R-4b',
        'significado': 'Proíbe virar à direita na próxima interseção.',
        'acao': 'Não virar à direita',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'obrigatorio',
        'pagina': 75
    },
    'r_5_a': {
        'nome': 'Proibido retornar à esquerda',
        'codigo': 'R-5a',
        'significado': 'Proíbe fazer retorno para a esquerda.',
        'acao': 'Não fazer retorno à esquerda',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'obrigatorio',
        'pagina': 77
    },
    'r_5_b': {
        'nome': 'Proibido retornar à direita',
        'codigo': 'R-5b',
        'significado': 'Proíbe fazer retorno para a direita.',
        'acao': 'Não fazer retorno à direita',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'obrigatorio',
        'pagina': 79
    },
    'r_6_a': {
        'nome': 'Proibido estacionar',
        'codigo': 'R-6a',
        'significado': 'Proíbe estacionar o veículo no local.',
        'acao': 'Não estacionar',
        'penalidade': 'Multa e remoção do veículo',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'obrigatorio',
        'pagina': 141
    },
    'r_6_b': {
        'nome': 'Proibido parar e estacionar R-6c',
        'codigo': 'R-6b',
        'significado': 'Proíbe parar e estacionar o veículo no local.',
        'acao': 'Não parar nem estacionar',
        'penalidade': 'Multa e remoção do veículo',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'obrigatorio',
        'pagina': 4
    },
    'r_6_c': {
        'nome': 'Proibido parar e estacionar',
        'codigo': 'R-6c',
        'significado': 'Proíbe parar e estacionar o veículo no local.',
        'acao': 'Não parar nem estacionar',
        'penalidade': 'Multa e remoção do veículo',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'obrigatorio',
        'pagina': 151
    },
    'r_7': {
        'nome': 'Proibido ultrapassar',
        'codigo': 'R-7',
        'significado': 'Proíbe ultrapassar outros veículos na via.',
        'acao': 'Não ultrapassar',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'obrigatorio',
        'pagina': 95
    },
    'r_8_a': {
        'nome': '',
        'codigo': 'R-8a',
        'significado': 'Placa de regulamentação: ',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 4
    },
    'r_9': {
        'nome': 'Proibido trânsito de caminhões',
        'codigo': 'R-9',
        'significado': 'Placa de regulamentação: Proibido trânsito de caminhões',
        'acao': 'Seguir regulamentação indicada',
        'penalidade': 'Multa e pontos na carteira',
        'cores': ['vermelho', 'branco'],
        'formas': ['circular'],
        'tipo': 'regulamentacao',
        'pagina': 107
    },
}


# Base de dados por código oficial
CODIGOS_OFICIAIS = {
    'A-10a': SINALIZACAO_DATABASE['a_10_a'],
    'A-10b': SINALIZACAO_DATABASE['a_10_b'],
    'A-12': SINALIZACAO_DATABASE['a_12'],
    'A-13a': SINALIZACAO_DATABASE['a_13_a'],
    'A-13b': SINALIZACAO_DATABASE['a_13_b'],
    'A-14': SINALIZACAO_DATABASE['a_14'],
    'A-15': SINALIZACAO_DATABASE['a_15'],
    'A-16': SINALIZACAO_DATABASE['a_16'],
    'A-17': SINALIZACAO_DATABASE['a_17'],
    'A-18': SINALIZACAO_DATABASE['a_18'],
    'A-19': SINALIZACAO_DATABASE['a_19'],
    'A-1a': SINALIZACAO_DATABASE['a_1_a'],
    'A-1b': SINALIZACAO_DATABASE['a_1_b'],
    'A-20a': SINALIZACAO_DATABASE['a_20_a'],
    'A-20b': SINALIZACAO_DATABASE['a_20_b'],
    'A-21a': SINALIZACAO_DATABASE['a_21_a'],
    'A-21b': SINALIZACAO_DATABASE['a_21_b'],
    'A-21c': SINALIZACAO_DATABASE['a_21_c'],
    'A-21d': SINALIZACAO_DATABASE['a_21d'],
    'A-21e': SINALIZACAO_DATABASE['a_21e'],
    'A-22': SINALIZACAO_DATABASE['a_22'],
    'A-23': SINALIZACAO_DATABASE['a_23'],
    'A-24': SINALIZACAO_DATABASE['a_24'],
    'A-25': SINALIZACAO_DATABASE['a_25'],
    'A-26a': SINALIZACAO_DATABASE['a_26_a'],
    'A-26b': SINALIZACAO_DATABASE['a_26_b'],
    'A-27': SINALIZACAO_DATABASE['a_27'],
    'A-28': SINALIZACAO_DATABASE['a_28'],
    'A-29': SINALIZACAO_DATABASE['a_29'],
    'A-2a': SINALIZACAO_DATABASE['a_2_a'],
    'A-2b': SINALIZACAO_DATABASE['a_2_b'],
    'A-30a': SINALIZACAO_DATABASE['a_30_a'],
    'A-30b': SINALIZACAO_DATABASE['a_30_b'],
    'A-31': SINALIZACAO_DATABASE['a_31'],
    'A-32a': SINALIZACAO_DATABASE['a_32_a'],
    'A-32b': SINALIZACAO_DATABASE['a_32_b'],
    'A-33a': SINALIZACAO_DATABASE['a_33_a'],
    'A-33b': SINALIZACAO_DATABASE['a_33_b'],
    'A-34': SINALIZACAO_DATABASE['a_34'],
    'A-35': SINALIZACAO_DATABASE['a_35'],
    'A-36': SINALIZACAO_DATABASE['a_36'],
    'A-37': SINALIZACAO_DATABASE['a_37'],
    'A-38': SINALIZACAO_DATABASE['a_38'],
    'A-39': SINALIZACAO_DATABASE['a_39'],
    'A-3a': SINALIZACAO_DATABASE['a_3_a'],
    'A-3b': SINALIZACAO_DATABASE['a_3_b'],
    'A-40': SINALIZACAO_DATABASE['a_40'],
    'A-41': SINALIZACAO_DATABASE['a_41'],
    'A-42a': SINALIZACAO_DATABASE['a_42_a'],
    'A-42b': SINALIZACAO_DATABASE['a_42_b'],
    'A-42c': SINALIZACAO_DATABASE['a_42_c'],
    'A-43': SINALIZACAO_DATABASE['a_43'],
    'A-44': SINALIZACAO_DATABASE['a_44'],
    'A-45': SINALIZACAO_DATABASE['a_45'],
    'A-46': SINALIZACAO_DATABASE['a_46'],
    'A-47': SINALIZACAO_DATABASE['a_47'],
    'A-48': SINALIZACAO_DATABASE['a_48'],
    'A-4a': SINALIZACAO_DATABASE['a_4_a'],
    'A-4b': SINALIZACAO_DATABASE['a_4_b'],
    'A-5a': SINALIZACAO_DATABASE['a_5_a'],
    'A-5b': SINALIZACAO_DATABASE['a_5_b'],
    'A-6': SINALIZACAO_DATABASE['a_6'],
    'A-7a': SINALIZACAO_DATABASE['a_7_a'],
    'A-7b': SINALIZACAO_DATABASE['a_7_b'],
    'A-8': SINALIZACAO_DATABASE['a_8'],
    'A-9': SINALIZACAO_DATABASE['a_9'],
    'R-1': SINALIZACAO_DATABASE['r_1'],
    'R-10': SINALIZACAO_DATABASE['r_10'],
    'R-11': SINALIZACAO_DATABASE['r_11'],
    'R-12': SINALIZACAO_DATABASE['r_12'],
    'R-14': SINALIZACAO_DATABASE['r_14'],
    'R-15': SINALIZACAO_DATABASE['r_15'],
    'R-16': SINALIZACAO_DATABASE['r_16'],
    'R-17': SINALIZACAO_DATABASE['r_17'],
    'R-18': SINALIZACAO_DATABASE['r_18'],
    'R-19': SINALIZACAO_DATABASE['r_19'],
    'R-2': SINALIZACAO_DATABASE['r_2'],
    'R-20': SINALIZACAO_DATABASE['r_20'],
    'R-21': SINALIZACAO_DATABASE['r_21'],
    'R-22': SINALIZACAO_DATABASE['r_22'],
    'R-23': SINALIZACAO_DATABASE['r_23'],
    'R-24a': SINALIZACAO_DATABASE['r_24_a'],
    'R-24b': SINALIZACAO_DATABASE['r_24_b'],
    'R-25a': SINALIZACAO_DATABASE['r_25_a'],
    'R-25b': SINALIZACAO_DATABASE['r_25_b'],
    'R-25c': SINALIZACAO_DATABASE['r_25_c'],
    'R-25d': SINALIZACAO_DATABASE['r_25d'],
    'R-26': SINALIZACAO_DATABASE['r_26'],
    'R-28': SINALIZACAO_DATABASE['r_28'],
    'R-29': SINALIZACAO_DATABASE['r_29'],
    'R-3': SINALIZACAO_DATABASE['r_3'],
    'R-30': SINALIZACAO_DATABASE['r_30'],
    'R-31': SINALIZACAO_DATABASE['r_31'],
    'R-32': SINALIZACAO_DATABASE['r_32'],
    'R-33': SINALIZACAO_DATABASE['r_33'],
    'R-34': SINALIZACAO_DATABASE['r_34'],
    'R-35a': SINALIZACAO_DATABASE['r_35_a'],
    'R-35b': SINALIZACAO_DATABASE['r_35_b'],
    'R-36a': SINALIZACAO_DATABASE['r_36_a'],
    'R-36b': SINALIZACAO_DATABASE['r_36_b'],
    'R-38': SINALIZACAO_DATABASE['r_38'],
    'R-39': SINALIZACAO_DATABASE['r_39'],
    'R-40': SINALIZACAO_DATABASE['r_40'],
    'R-44': SINALIZACAO_DATABASE['r_44'],
    'R-4a': SINALIZACAO_DATABASE['r_4_a'],
    'R-4b': SINALIZACAO_DATABASE['r_4_b'],
    'R-5a': SINALIZACAO_DATABASE['r_5_a'],
    'R-5b': SINALIZACAO_DATABASE['r_5_b'],
    'R-6a': SINALIZACAO_DATABASE['r_6_a'],
    'R-6b': SINALIZACAO_DATABASE['r_6_b'],
    'R-6c': SINALIZACAO_DATABASE['r_6_c'],
    'R-7': SINALIZACAO_DATABASE['r_7'],
    'R-8a': SINALIZACAO_DATABASE['r_8_a'],
    'R-9': SINALIZACAO_DATABASE['r_9'],
}


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
        print("\n📋 MENU DE CONSULTA")
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
                    print(f"\n✅ PLACA ENCONTRADA:")
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
                    print(f"\n✅ {len(resultados)} PLACA(S) ENCONTRADA(S):")
                    for i, resultado in enumerate(resultados, 1):
                        print(f"\n{i}. 🚦 {resultado['nome']} ({resultado['codigo']})")
                        print(f"   💡 {resultado['significado']}")
                        print(f"   ⚠️  {resultado['acao']}")
                        print(f"   💰 {resultado['penalidade']}")
                else:
                    print(f"❌ Nenhuma placa encontrada para '{nome}'")
                
            elif choice == '3':
                print(f"\n📋 TODOS OS CÓDIGOS OFICIAIS ({len(CODIGOS_OFICIAIS)} placas):")
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
                    print(f"\n✅ {len(resultados)} PLACA(S) DO TIPO '{tipo.upper()}':")
                    for i, resultado in enumerate(resultados, 1):
                        print(f"\n{i}. 🚦 {resultado['nome']} ({resultado['codigo']})")
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
                    print(f"\n✅ {len(resultados)} PLACA(S) COM COR '{cor.upper()}':")
                    for i, resultado in enumerate(resultados, 1):
                        print(f"\n{i}. 🚦 {resultado['nome']} ({resultado['codigo']})")
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
                    print(f"\n✅ {len(resultados)} PLACA(S) COM FORMA '{forma.upper()}':")
                    for i, resultado in enumerate(resultados, 1):
                        print(f"\n{i}. 🚦 {resultado['nome']} ({resultado['codigo']})")
                        print(f"   🔷 Formas: {', '.join(resultado['formas'])}")
                        print(f"   💡 {resultado['significado']}")
                else:
                    print(f"❌ Nenhuma placa com forma '{forma}' encontrada")
                
            elif choice == '0':
                print("\n👋 Obrigado por usar a Base de Dados de Sinalização!")
                print("   🚦 Até logo! 📖")
                break
                
            else:
                print("❌ Opção inválida! Escolha de 0 a 6.")
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Aplicação interrompida")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
        
        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()
