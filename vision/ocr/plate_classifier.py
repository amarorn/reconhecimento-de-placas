"""
Classificador de Placas - Mercosul vs Convencional
================================================

Sistema para identificar tipo, estado e número das placas brasileiras.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PlateInfo:
    """Informações da placa identificada"""
    number: str
    type: str  # 'mercosul' ou 'convencional'
    state: Optional[str] = None
    city: Optional[str] = None
    confidence: float = 0.0
    pattern_match: bool = False

class PlateClassifier:
    """Classificador de placas brasileiras"""
    
    def __init__(self):
        # Estados brasileiros
        self.estados = {
            'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
            'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 
            'ES': 'Espírito Santo', 'GO': 'Goiás', 'MA': 'Maranhão',
            'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul', 'MG': 'Minas Gerais',
            'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná', 'PE': 'Pernambuco',
            'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
            'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima',
            'SC': 'Santa Catarina', 'SP': 'São Paulo', 'SE': 'Sergipe',
            'TO': 'Tocantins'
        }
        
        # Padrões de placas
        self.pattern_mercosul = re.compile(r'^[A-Z]{3}[0-9][A-Z][0-9]{2}$')
        self.pattern_convencional = re.compile(r'^[A-Z]{3}[-\s]?[0-9]{4}$')
        
        # Cidades por estado (algumas principais)
        self.cidades_estados = {
            'CAMPO GRANDE': 'MS',
            'SAO PAULO': 'SP', 'SANTOS': 'SP', 'CAMPINAS': 'SP',
            'RIO DE JANEIRO': 'RJ', 'NITEROI': 'RJ',
            'BELO HORIZONTE': 'MG', 'UBERLANDIA': 'MG',
            'BRASILIA': 'DF',
            'CURITIBA': 'PR', 'LONDRINA': 'PR',
            'PORTO ALEGRE': 'RS', 'CAXIAS DO SUL': 'RS',
            'SALVADOR': 'BA', 'FEIRA DE SANTANA': 'BA',
            'FORTALEZA': 'CE', 'SOBRAL': 'CE',
            'RECIFE': 'PE', 'OLINDA': 'PE',
            'GOIANIA': 'GO', 'ANAPOLIS': 'GO'
        }

    def clean_text(self, text: str) -> str:
        """Limpa e normaliza texto extraído"""
        if not text:
            return ""
        
        # Remover caracteres especiais e espaços extras
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip().upper()
        
        return text

    def extract_plate_number(self, text: str) -> Optional[str]:
        """Extrai número da placa do texto"""
        text = self.clean_text(text)
        
        # Tentar padrão Mercosul (ABC1D23)
        mercosul_match = re.search(r'([A-Z]{3}[0-9][A-Z][0-9]{2})', text)
        if mercosul_match:
            return mercosul_match.group(1)
        
        # Tentar padrão convencional (ABC-1234 ou ABC 1234)
        conv_match = re.search(r'([A-Z]{3})[-\s]*([0-9]{4})', text)
        if conv_match:
            return f"{conv_match.group(1)}-{conv_match.group(2)}"
        
        # Tentar extrair qualquer sequência que pareça placa
        generic_match = re.search(r'([A-Z]{2,3}[-\s]*[0-9A-Z]{3,4})', text)
        if generic_match:
            return generic_match.group(1)
        
        return None

    def identify_plate_type(self, plate_number: str) -> str:
        """Identifica se é placa Mercosul ou convencional"""
        if not plate_number:
            return "unknown"
        
        # Remover hífens e espaços para análise
        clean_plate = re.sub(r'[-\s]', '', plate_number)
        
        # Padrão Mercosul: ABC1D23 (3 letras, 1 número, 1 letra, 2 números)
        if self.pattern_mercosul.match(clean_plate):
            return "mercosul"
        
        # Padrão convencional: ABC1234 (3 letras, 4 números)
        clean_conventional = re.sub(r'[-\s]', '', plate_number)
        if re.match(r'^[A-Z]{3}[0-9]{4}$', clean_conventional):
            return "convencional"
        
        return "unknown"

    def identify_state_from_city(self, text: str) -> Optional[str]:
        """Identifica estado pela cidade mencionada"""
        text_upper = text.upper()
        
        for cidade, estado in self.cidades_estados.items():
            if cidade in text_upper:
                return estado
        
        return None

    def identify_state_from_text(self, text: str) -> Optional[str]:
        """Identifica estado pelo texto da placa"""
        text_upper = self.clean_text(text)
        
        # Procurar por siglas de estados
        for sigla, nome in self.estados.items():
            if sigla in text_upper or nome.upper() in text_upper:
                return sigla
        
        # Procurar por cidades
        state_from_city = self.identify_state_from_city(text_upper)
        if state_from_city:
            return state_from_city
        
        return None

    def analyze_plate_context(self, all_texts: List[str]) -> Dict[str, str]:
        """Analisa contexto completo da imagem para extrair informações"""
        context = {
            'state': None,
            'city': None,
            'additional_info': []
        }
        
        for text in all_texts:
            text_clean = self.clean_text(text)
            
            # Identificar estado
            if not context['state']:
                context['state'] = self.identify_state_from_text(text_clean)
            
            # Identificar cidade
            city_found = self.identify_state_from_city(text_clean)
            if city_found and not context['city']:
                for cidade, estado in self.cidades_estados.items():
                    if cidade in text_clean.upper():
                        context['city'] = cidade
                        break
            
            # Coletar informações adicionais
            if len(text_clean) > 3 and text_clean not in context['additional_info']:
                context['additional_info'].append(text_clean)
        
        return context

    def classify_plate(self, ocr_results: List[Dict]) -> PlateInfo:
        """Classifica placa com base nos resultados de OCR"""
        
        if not ocr_results:
            return PlateInfo(
                number="",
                type="unknown",
                confidence=0.0
            )
        
        # Extrair todos os textos
        all_texts = []
        plate_candidates = []
        
        for result in ocr_results:
            text = result.get('text', '').strip()
            confidence = result.get('confidence', 0.0)
            
            if text:
                all_texts.append(text)
                
                # Tentar extrair número da placa
                plate_number = self.extract_plate_number(text)
                if plate_number:
                    plate_candidates.append({
                        'number': plate_number,
                        'confidence': confidence,
                        'original_text': text
                    })
        
        # Analisar contexto
        context = self.analyze_plate_context(all_texts)
        
        # Selecionar melhor candidato a placa
        best_plate = None
        if plate_candidates:
            # Ordenar por confiança
            plate_candidates.sort(key=lambda x: x['confidence'], reverse=True)
            best_plate = plate_candidates[0]
        
        if not best_plate:
            # Tentar encontrar qualquer sequência alfanumérica que pareça placa
            for text in all_texts:
                clean = self.clean_text(text)
                if len(clean) >= 6 and re.search(r'[A-Z].*[0-9]|[0-9].*[A-Z]', clean):
                    best_plate = {
                        'number': clean,
                        'confidence': 0.5,
                        'original_text': text
                    }
                    break
        
        if not best_plate:
            return PlateInfo(
                number="",
                type="unknown",
                confidence=0.0
            )
        
        # Classificar tipo da placa
        plate_type = self.identify_plate_type(best_plate['number'])
        
        # Identificar estado
        state = context['state']
        if not state and 'original_text' in best_plate:
            state = self.identify_state_from_text(best_plate['original_text'])
        
        return PlateInfo(
            number=best_plate['number'],
            type=plate_type,
            state=state,
            city=context['city'],
            confidence=best_plate['confidence'],
            pattern_match=plate_type != "unknown"
        )

    def get_plate_details(self, plate_info: PlateInfo) -> Dict[str, str]:
        """Retorna detalhes completos da placa"""
        details = {
            'numero': plate_info.number,
            'tipo': plate_info.type,
            'confianca': f"{plate_info.confidence:.1%}",
            'padrao_valido': "Sim" if plate_info.pattern_match else "Não"
        }
        
        if plate_info.state:
            details['estado'] = f"{plate_info.state} ({self.estados.get(plate_info.state, 'Desconhecido')})"
        else:
            details['estado'] = "Não identificado"
        
        if plate_info.city:
            details['cidade'] = plate_info.city
        
        # Informações sobre o tipo
        if plate_info.type == "mercosul":
            details['formato'] = "Mercosul (ABC1D23)"
            details['caracteristicas'] = "Padrão atual brasileiro desde 2018"
        elif plate_info.type == "convencional":
            details['formato'] = "Convencional (ABC-1234)"
            details['caracteristicas'] = "Padrão brasileiro até 2018"
        else:
            details['formato'] = "Não identificado"
            details['caracteristicas'] = "Formato não reconhecido"
        
        return details

# Instância global do classificador
plate_classifier = PlateClassifier()
