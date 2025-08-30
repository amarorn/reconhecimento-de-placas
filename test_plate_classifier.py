

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from vision.ocr.plate_classifier import PlateClassifier

def test_plate_examples():
    
    classifier = PlateClassifier()
    
    print("🧪 Testando Classificador de Placas")
    print("=" * 40)
    
    print("\n📋 Teste 1: Placa Convencional")
    ocr_results_1 = [
        {"text": "MS CAMPO GRANDE", "confidence": 0.85},
        {"text": "HQW-5678", "confidence": 0.92},
        {"text": "HQW 5678", "confidence": 0.88}
    ]
    
    plate_info_1 = classifier.classify_plate(ocr_results_1)
    details_1 = classifier.get_plate_details(plate_info_1)
    
    print(f"Número: {plate_info_1.number}")
    print(f"Tipo: {plate_info_1.type}")
    print(f"Estado: {plate_info_1.state}")
    print("Detalhes:")
    for key, value in details_1.items():
        print(f"  {key}: {value}")
    
    print("\n📋 Teste 2: Placa Mercosul")
    ocr_results_2 = [
        {"text": "BRASIL", "confidence": 0.90},
        {"text": "FJB4E12", "confidence": 0.94},
        {"text": "BR", "confidence": 0.78}
    ]
    
    plate_info_2 = classifier.classify_plate(ocr_results_2)
    details_2 = classifier.get_plate_details(plate_info_2)
    
    print(f"Número: {plate_info_2.number}")
    print(f"Tipo: {plate_info_2.type}")
    print(f"Estado: {plate_info_2.state}")
    print("Detalhes:")
    for key, value in details_2.items():
        print(f"  {key}: {value}")
    
    print("\n📋 Teste 3: Outros Exemplos")
    test_cases = [
        {"text": "ABC1234", "expected": "convencional"},
        {"text": "ABC-1234", "expected": "convencional"}, 
        {"text": "ABC1D23", "expected": "mercosul"},
        {"text": "BRA2E19", "expected": "mercosul"},
        {"text": "SP SAO PAULO", "expected": "estado_sp"}
    ]
    
    for i, test_case in enumerate(test_cases):
        ocr_test = [{"text": test_case["text"], "confidence": 0.85}]
        result = classifier.classify_plate(ocr_test)
        print(f"  {i+1}. '{test_case['text']}' → {result.type} ({result.state})")

def test_patterns():
    classifier = PlateClassifier()
    
    print("\n🔍 Testando Padrões")
    print("=" * 20)
    
    test_patterns = [
        "HQW-5678",
        "FJB4E12",
        "ABC1234",
        "XYZ9W87",
        "INVALID",
    ]
    
    for pattern in test_patterns:
        plate_type = classifier.identify_plate_type(pattern)
        print(f"  {pattern} → {plate_type}")

if __name__ == "__main__":
    test_plate_examples()
    test_patterns()
