
import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PlateInfo:
    
    def __init__(self):
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
        
        self.pattern_mercosul = re.compile(r'^[A-Z]{3}[0-9][A-Z][0-9]{2}$')
        self.pattern_convencional = re.compile(r'^[A-Z]{3}[-\s]?[0-9]{4}$')
        
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
        text = self.clean_text(text)
        
        mercosul_match = re.search(r'([A-Z]{3}[0-9][A-Z][0-9]{2})', text)
        if mercosul_match:
            return mercosul_match.group(1)
        
        conv_match = re.search(r'([A-Z]{3})[-\s]*([0-9]{4})', text)
        if conv_match:
            return f"{conv_match.group(1)}-{conv_match.group(2)}"
        
        generic_match = re.search(r'([A-Z]{2,3}[-\s]*[0-9A-Z]{3,4})', text)
        if generic_match:
            return generic_match.group(1)
        
        return None

    def identify_plate_type(self, plate_number: str) -> str:
        text_upper = text.upper()
        
        for cidade, estado in self.cidades_estados.items():
            if cidade in text_upper:
                return estado
        
        return None

    def identify_state_from_text(self, text: str) -> Optional[str]:
        context = {
            'state': None,
            'city': None,
            'additional_info': []
        }
        
        for text in all_texts:
            text_clean = self.clean_text(text)
            
            if not context['state']:
                context['state'] = self.identify_state_from_text(text_clean)
            
            city_found = self.identify_state_from_city(text_clean)
            if city_found and not context['city']:
                for cidade, estado in self.cidades_estados.items():
                    if cidade in text_clean.upper():
                        context['city'] = cidade
                        break
            
            if len(text_clean) > 3 and text_clean not in context['additional_info']:
                context['additional_info'].append(text_clean)
        
        return context

    def classify_plate(self, ocr_results: List[Dict]) -> PlateInfo:
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

plate_classifier = PlateClassifier()
