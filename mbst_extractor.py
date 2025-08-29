#!/usr/bin/env python3
"""
Extrator de Dataset do MBST - Manual Brasileiro de Sinalização de Trânsito
=======================================================================

Este sistema extrai dados dos PDFs oficiais do MBST para criar um dataset completo
de placas de sinalização brasileiras com códigos, nomes e características.
"""

import PyPDF2
import re
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from pathlib import Path

class MBSTExtractor:
    """Extrator de dados do MBST para criação de dataset"""
    
    def __init__(self):
        self.dataset = {
            "metadata": {
                "total_placas": 0,
                "por_tipo": {},
                "por_codigo": {},
                "data_geracao": datetime.now().isoformat(),
                "fonte": "Manual Brasileiro de Sinalização de Trânsito (MBST)",
                "versao": "3.0",
                "pdfs_processados": []
            },
            "placas": {}
        }
        
        # Padrões de regex para extração
        self.patterns = {
            'codigo_nome': [
                r'([R|A|I|S|E|P]-[\d]+[a-z]?)\s+([^0-9\n]+?)(?=\n|$)',
                r'([^0-9\n]+?)\s+([R|A|I|S|E|P]-[\d]+[a-z]?)(?=\n|$)',
                r'([R|A|I|S|E|P]-[\d]+[a-z]?)\s*[-–]\s*([^0-9\n]+?)(?=\n|$)',
                r'([R|A|I|S|E|P]-[\d]+[a-z]?)\s*:\s*([^0-9\n]+?)(?=\n|$)'
            ],
            'codigo_isolado': [
                r'\b([R|A|I|S|E|P]-[\d]+[a-z]?)\b',
                r'([R|A|I|S|E|P]-[\d]+[a-z]?)\s',
                r'\s([R|A|I|S|E|P]-[\d]+[a-z]?)\s'
            ],
            'nome_isolado': [
                r'([A-Z][A-Z\sÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ]+?)(?=\n|$)',
                r'([A-Z][A-Z\sÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ]+?)(?=\s[R|A|I|S|E|P]-)'
            ]
        }
        
        # Mapeamento de tipos por código
        self.tipo_por_codigo = {
            'R': 'regulamentacao',
            'A': 'advertencia', 
            'I': 'informacao',
            'S': 'servicos',
            'E': 'educacao',
            'P': 'prevencao'
        }
        
        # Mapeamento de cores por tipo
        self.cores_por_tipo = {
            'regulamentacao': ['azul', 'branco'],
            'advertencia': ['amarelo', 'preto'],
            'informacao': ['azul', 'branco'],
            'servicos': ['azul', 'branco'],
            'educacao': ['verde', 'branco'],
            'prevencao': ['vermelho', 'branco']
        }
        
        # Mapeamento de formas por tipo
        self.formas_por_tipo = {
            'regulamentacao': ['circular', 'retangular'],
            'advertencia': ['triangular', 'diamante'],
            'informacao': ['retangular', 'quadrado'],
            'servicos': ['retangular'],
            'educacao': ['retangular'],
            'prevencao': ['octogonal', 'circular']
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extrai texto de um PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                print(f"📄 Processando PDF: {pdf_path}")
                print(f"   📖 Páginas encontradas: {len(pdf_reader.pages)}")
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += f"\n--- PÁGINA {page_num + 1} ---\n"
                            text += page_text
                            text += "\n"
                    except Exception as e:
                        print(f"   ⚠️ Erro na página {page_num + 1}: {e}")
                
                return text
                
        except Exception as e:
            print(f"❌ Erro ao processar PDF {pdf_path}: {e}")
            return ""
    
    def extract_codigo_nome_pairs(self, text: str) -> List[Tuple[str, str]]:
        """Extrai pares de código-nome do texto"""
        pairs = []
        
        # Tentar diferentes padrões
        for pattern in self.patterns['codigo_nome']:
            matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    codigo = match[0].strip().upper()
                    nome = match[1].strip()
                    
                    # Validar código
                    if self.is_valid_code(codigo) and len(nome) > 3:
                        pairs.append((codigo, nome))
        
        # Remover duplicatas
        unique_pairs = []
        seen = set()
        for codigo, nome in pairs:
            if codigo not in seen:
                unique_pairs.append((codigo, nome))
                seen.add(codigo)
        
        return unique_pairs
    
    def is_valid_code(self, code: str) -> bool:
        """Verifica se um código é válido"""
        if not code:
            return False
        
        # Padrão: R-1, A-50B, I-15, etc.
        pattern = r'^[R|A|I|S|E|P]-[\d]+[a-z]?$'
        return bool(re.match(pattern, code))
    
    def extract_codigos_isolados(self, text: str) -> List[str]:
        """Extrai códigos isolados do texto"""
        codigos = []
        
        for pattern in self.patterns['codigo_isolado']:
            matches = re.findall(pattern, text, re.MULTILINE)
            for match in matches:
                if self.is_valid_code(match):
                    codigos.append(match.upper())
        
        return list(set(codigos))
    
    def extract_nomes_isolados(self, text: str) -> List[str]:
        """Extrai nomes isolados do texto"""
        nomes = []
        
        for pattern in self.patterns['nome_isolado']:
            matches = re.findall(pattern, text, re.MULTILINE)
            for match in matches:
                nome = match.strip()
                if len(nome) > 5 and not self.is_valid_code(nome):
                    nomes.append(nome)
        
        return list(set(nomes))
    
    def match_codigos_nomes(self, codigos: List[str], nomes: List[str], text: str) -> List[Tuple[str, str]]:
        """Tenta fazer match entre códigos e nomes baseado na proximidade no texto"""
        pairs = []
        
        for codigo in codigos:
            # Procurar o código no texto
            codigo_pos = text.find(codigo)
            if codigo_pos != -1:
                # Procurar nomes próximos
                best_nome = None
                best_distance = float('inf')
                
                for nome in nomes:
                    nome_pos = text.find(nome)
                    if nome_pos != -1:
                        distance = abs(codigo_pos - nome_pos)
                        if distance < best_distance and distance < 500:  # Máximo 500 caracteres
                            best_distance = distance
                            best_nome = nome
                
                if best_nome:
                    pairs.append((codigo, best_nome))
        
        return pairs
    
    def process_pdf(self, pdf_path: str) -> List[Tuple[str, str]]:
        """Processa um PDF completo"""
        print(f"\n🔍 PROCESSANDO: {pdf_path}")
        
        # Extrair texto
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            return []
        
        # Extrair pares código-nome
        pairs = self.extract_codigo_nome_pairs(text)
        print(f"   ✅ Pares código-nome encontrados: {len(pairs)}")
        
        # Se não encontrou pares, tentar extração isolada
        if not pairs:
            print("   🔄 Tentando extração isolada...")
            codigos = self.extract_codigos_isolados(text)
            nomes = self.extract_nomes_isolados(text)
            
            print(f"      📋 Códigos encontrados: {len(codigos)}")
            print(f"      📝 Nomes encontrados: {len(nomes)}")
            
            # Tentar fazer match
            pairs = self.match_codigos_nomes(codigos, nomes, text)
            print(f"      🔗 Matches feitos: {len(pairs)}")
        
        # Adicionar ao dataset
        for codigo, nome in pairs:
            self.add_placa_to_dataset(codigo, nome, pdf_path)
        
        # Adicionar PDF à lista de processados
        self.dataset['metadata']['pdfs_processados'].append({
            'arquivo': os.path.basename(pdf_path),
            'pares_encontrados': len(pairs),
            'data_processamento': datetime.now().isoformat()
        })
        
        return pairs
    
    def add_placa_to_dataset(self, codigo: str, nome: str, pdf_source: str):
        """Adiciona uma placa ao dataset"""
        # Determinar tipo baseado no código
        tipo_letra = codigo[0]
        tipo = self.tipo_por_codigo.get(tipo_letra, 'desconhecido')
        
        # Gerar informações da placa
        placa_info = {
            "nome": nome,
            "tipo": tipo,
            "significado": self.generate_significado(nome, tipo),
            "acao": self.generate_acao(tipo),
            "penalidade": self.generate_penalidade(tipo),
            "cores": self.cores_por_tipo.get(tipo, []),
            "formas": self.formas_por_tipo.get(tipo, []),
            "aplicacao": "",
            "observacoes": "",
            "pagina": None,
            "pdf_source": os.path.basename(pdf_source),
            "metadata": {
                "data_extracao": datetime.now().isoformat(),
                "metodo": "pdf_extraction",
                "codigo_original": codigo,
                "nome_original": nome
            }
        }
        
        # Adicionar ao dataset
        self.dataset['placas'][codigo] = placa_info
        
        # Atualizar contadores
        self.dataset['metadata']['total_placas'] = len(self.dataset['placas'])
        
        # Atualizar contadores por tipo
        if tipo not in self.dataset['metadata']['por_tipo']:
            self.dataset['metadata']['por_tipo'][tipo] = 0
        self.dataset['metadata']['por_tipo'][tipo] += 1
        
        # Atualizar contadores por código
        if codigo not in self.dataset['metadata']['por_codigo']:
            self.dataset['metadata']['por_codigo'][codigo] = 0
        self.dataset['metadata']['por_codigo'][codigo] += 1
    
    def generate_significado(self, nome: str, tipo: str) -> str:
        """Gera significado baseado no nome e tipo"""
        if tipo == 'regulamentacao':
            return f"Regulamentação específica: {nome}"
        elif tipo == 'advertencia':
            return f"Advertência de perigo: {nome}"
        elif tipo == 'informacao':
            return f"Informação útil: {nome}"
        elif tipo == 'servicos':
            return f"Serviço disponível: {nome}"
        elif tipo == 'educacao':
            return f"Educação e orientação: {nome}"
        elif tipo == 'prevencao':
            return f"Prevenção e segurança: {nome}"
        else:
            return f"Sinalização de trânsito: {nome}"
    
    def generate_acao(self, tipo: str) -> str:
        """Gera ação baseada no tipo"""
        if tipo == 'regulamentacao':
            return "Seguir obrigatoriamente a regulamentação indicada"
        elif tipo == 'advertencia':
            return "Reduzir velocidade e ter atenção especial"
        elif tipo == 'informacao':
            return "Observar e seguir as orientações fornecidas"
        elif tipo == 'servicos':
            return "Utilizar o serviço indicado quando necessário"
        elif tipo == 'educacao':
            return "Atenção especial para educação e orientação"
        elif tipo == 'prevencao':
            return "Tomar medidas de prevenção e segurança"
        else:
            return "Observar e seguir orientações"
    
    def generate_penalidade(self, tipo: str) -> str:
        """Gera penalidade baseada no tipo"""
        if tipo == 'regulamentacao':
            return "Multa e pontos na carteira"
        elif tipo == 'advertencia':
            return "Não aplicável (advertência)"
        elif tipo == 'informacao':
            return "Não aplicável (informação)"
        elif tipo == 'servicos':
            return "Não aplicável (serviço)"
        elif tipo == 'educacao':
            return "Não aplicável (educação)"
        elif tipo == 'prevencao':
            return "Multa e pontos na carteira"
        else:
            return "Verificar tipo específico"
    
    def save_dataset(self, output_path: str):
        """Salva o dataset em arquivo JSON"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.dataset, f, ensure_ascii=False, indent=2)
            
            print(f"\n✅ Dataset salvo em: {output_path}")
            print(f"📊 Total de placas: {self.dataset['metadata']['total_placas']}")
            
        except Exception as e:
            print(f"❌ Erro ao salvar dataset: {e}")
    
    def generate_summary_report(self) -> str:
        """Gera relatório resumido do dataset"""
        metadata = self.dataset['metadata']
        
        report = f"""# 📊 RELATÓRIO DO DATASET MBST

## 📅 Data de Geração: {metadata['data_geracao']}
## 📚 Fonte: {metadata['fonte']}
## 🔢 Versão: {metadata['versao']}

## 📈 ESTATÍSTICAS GERAIS
- **Total de placas**: {metadata['total_placas']}
- **PDFs processados**: {len(metadata['pdfs_processados'])}

## 🏷️ DISTRIBUIÇÃO POR TIPO
"""
        
        for tipo, count in metadata['por_tipo'].items():
            report += f"- **{tipo.title()}**: {count} placas\n"
        
        report += f"""
## 🔢 DISTRIBUIÇÃO POR CÓDIGO
- **Total de códigos únicos**: {len(metadata['por_codigo'])}

## 📄 PDFs PROCESSADOS
"""
        
        for pdf_info in metadata['pdfs_processados']:
            report += f"- **{pdf_info['arquivo']}**: {pdf_info['pares_encontrados']} placas\n"
        
        report += f"""
## 📋 EXEMPLOS DE PLACAS
"""
        
        # Mostrar algumas placas como exemplo
        count = 0
        for codigo, placa in self.dataset['placas'].items():
            if count < 10:
                report += f"""
### {codigo} - {placa['nome']}
- **Tipo**: {placa['tipo']}
- **Significado**: {placa['significado']}
- **Ação**: {placa['acao']}
- **Penalidade**: {placa['penalidade']}
- **Cores**: {', '.join(placa['cores'])}
- **Formas**: {', '.join(placa['formas'])}
"""
                count += 1
            else:
                report += f"\n... e mais {len(self.dataset['placas']) - 10} placas\n"
                break
        
        return report

def main():
    """Função principal"""
    print("🚀 EXTRATOR DE DATASET MBST - MANUAL BRASILEIRO DE SINALIZAÇÃO DE TRÂNSITO")
    print("=" * 80)
    
    # Inicializar extrator
    extractor = MBSTExtractor()
    
    # Lista de PDFs para processar
    pdf_files = [
        "sinalização-dados/(Microsoft Word - - 02 - MBST Vol. II - Sin. Vert. Advert_352ncia).pdf",
        "sinalização-dados/copy_of___01___MBST_Vol_I___Sin_Vert_Regulamentacao_F_pages_deleted (1).pdf"
    ]
    
    total_pairs = 0
    
    # Processar cada PDF
    for pdf_file in pdf_files:
        if os.path.exists(pdf_file):
            pairs = extractor.process_pdf(pdf_file)
            total_pairs += len(pairs)
        else:
            print(f"❌ PDF não encontrado: {pdf_file}")
    
    # Salvar dataset
    output_file = "dataset_mbst/dataset_completo_mbst.json"
    extractor.save_dataset(output_file)
    
    # Gerar relatório
    report = extractor.generate_summary_report()
    
    # Salvar relatório
    report_file = "dataset_mbst/relatorio_dataset_mbst.md"
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ Relatório salvo em: {report_file}")
    except Exception as e:
        print(f"❌ Erro ao salvar relatório: {e}")
    
    print(f"\n🎯 PROCESSAMENTO CONCLUÍDO!")
    print(f"   📊 Total de placas extraídas: {extractor.dataset['metadata']['total_placas']}")
    print(f"   📄 PDFs processados: {len(extractor.dataset['metadata']['pdfs_processados'])}")
    print(f"   💾 Dataset salvo em: {output_file}")
    print(f"   📋 Relatório salvo em: {report_file}")

if __name__ == "__main__":
    main()
