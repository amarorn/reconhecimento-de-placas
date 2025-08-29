#!/usr/bin/env python3
"""
Configurações da Aplicação de Reconhecimento de Placas
======================================================

Este arquivo contém todas as configurações ajustáveis da aplicação,
permitindo personalização sem modificar o código principal.
"""

# Configurações de Detecção
DETECTION_CONFIG = {
    # Área mínima para considerar um contorno como candidato a placa
    'MIN_CONTOUR_AREA': 1000,
    
    # Proporções de aspecto válidas para placas (largura/altura)
    'MIN_ASPECT_RATIO': 2.0,
    'MAX_ASPECT_RATIO': 5.5,
    
    # Parâmetros para detecção de bordas (Canny)
    'CANNY_LOW_THRESHOLD': 50,
    'CANNY_HIGH_THRESHOLD': 200,
    
    # Parâmetros para aproximação de contornos
    'CONTOUR_APPROX_EPSILON': 0.02,
    
    # Número mínimo de vértices para considerar como quadrilátero
    'MIN_VERTICES': 4,
    'MAX_VERTICES': 4
}

# Configurações de Pré-processamento
PREPROCESSING_CONFIG = {
    # Tamanho do kernel para filtro Gaussiano
    'GAUSSIAN_KERNEL_SIZE': (5, 5),
    'GAUSSIAN_SIGMA': 0,
    
    # Parâmetros para filtro bilateral
    'BILATERAL_D': 11,
    'BILATERAL_SIGMA_COLOR': 17,
    'BILATERAL_SIGMA_SPACE': 17,
    
    # Tamanho do kernel para operações morfológicas
    'MORPH_KERNEL_SIZE': (3, 3)
}

# Configurações de OCR
OCR_CONFIG = {
    # Idioma padrão para reconhecimento
    'DEFAULT_LANGUAGE': 'pt',
    
    # Idiomas suportados
    'SUPPORTED_LANGUAGES': ['pt', 'en', 'es'],
    
    # Usar GPU se disponível
    'USE_GPU': False,
    
    # Limiar de confiança mínimo para aceitar resultado
    'MIN_CONFIDENCE': 0.5,
    
    # Tamanho da imagem da placa para OCR
    'PLATE_WIDTH': 300,
    'PLATE_HEIGHT': 100
}

# Configurações de Visualização
VISUALIZATION_CONFIG = {
    # Cores para desenhar contornos
    'CONTOUR_COLOR': (0, 255, 0),  # Verde
    'CONTOUR_THICKNESS': 2,
    
    # Cores para texto das placas
    'TEXT_COLOR': (0, 255, 0),     # Verde
    'TEXT_THICKNESS': 2,
    'TEXT_SCALE': 0.8,
    
    # Tamanho da figura para matplotlib
    'FIGURE_SIZE': (15, 10),
    
    # Mostrar resultados automaticamente
    'AUTO_SHOW_RESULTS': True
}

# Configurações de Webcam
WEBCAM_CONFIG = {
    # Índice da câmera (0 = câmera padrão)
    'CAMERA_INDEX': 0,
    
    # Intervalo entre processamentos (em segundos)
    'PROCESS_INTERVAL': 2.0,
    
    # Resolução da câmera
    'FRAME_WIDTH': 640,
    'FRAME_HEIGHT': 480,
    
    # FPS da câmera
    'FPS': 30
}

# Configurações de Arquivo
FILE_CONFIG = {
    # Formatos de imagem suportados
    'SUPPORTED_FORMATS': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff'],
    
    # Tamanho máximo de arquivo (em MB)
    'MAX_FILE_SIZE': 50,
    
    # Pasta para arquivos temporários
    'TEMP_DIR': 'temp',
    
    # Prefixo para arquivos temporários
    'TEMP_PREFIX': 'temp_'
}

# Configurações de Performance
PERFORMANCE_CONFIG = {
    # Número máximo de imagens para processar em lote
    'MAX_BATCH_SIZE': 100,
    
    # Timeout para operações (em segundos)
    'OPERATION_TIMEOUT': 30,
    
    # Usar multithreading para processamento em lote
    'USE_MULTITHREADING': False,
    
    # Número de threads para processamento paralelo
    'MAX_THREADS': 4
}

# Configurações de Log
LOGGING_CONFIG = {
    # Nível de log
    'LOG_LEVEL': 'INFO',
    
    # Formato do log
    'LOG_FORMAT': '%(asctime)s - %(levelname)s - %(message)s',
    
    # Arquivo de log
    'LOG_FILE': 'plate_recognition.log',
    
    # Mostrar logs no console
    'CONSOLE_OUTPUT': True
}

# Configurações de Padrão de Placas
PLATE_PATTERNS = {
    # Padrão brasileiro antigo (ABC1234)
    'BRAZIL_OLD': r'[A-Z]{3}[0-9]{4}',
    
    # Padrão brasileiro novo (ABC1D23)
    'BRAZIL_NEW': r'[A-Z]{3}[0-9]{1}[A-Z]{1}[0-9]{2}',
    
    # Padrão mercosul (ABC1D23)
    'MERCOSUL': r'[A-Z]{3}[0-9]{1}[A-Z]{1}[0-9]{2}',
    
    # Padrão europeu (AB-123-CD)
    'EUROPEAN': r'[A-Z]{2}-[0-9]{3}-[A-Z]{2}',
    
    # Padrão americano (ABC-123)
    'AMERICAN': r'[A-Z]{3}-[0-9]{3}'
}

# Configurações de Validação
VALIDATION_CONFIG = {
    # Validar padrão de placa antes de aceitar resultado
    'VALIDATE_PLATE_PATTERN': True,
    
    # Padrões de placa aceitos (lista de chaves de PLATE_PATTERNS)
    'ACCEPTED_PATTERNS': ['BRAZIL_OLD', 'BRAZIL_NEW', 'MERCOSUL'],
    
    # Comprimento mínimo e máximo para placa
    'MIN_PLATE_LENGTH': 6,
    'MAX_PLATE_LENGTH': 8,
    
    # Caracteres válidos para placas
    'VALID_CHARACTERS': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
}

def get_config(section_name: str) -> dict:
    """
    Obtém configurações de uma seção específica
    
    Args:
        section_name: Nome da seção de configuração
        
    Returns:
        Dicionário com as configurações da seção
    """
    config_sections = {
        'detection': DETECTION_CONFIG,
        'preprocessing': PREPROCESSING_CONFIG,
        'ocr': OCR_CONFIG,
        'visualization': VISUALIZATION_CONFIG,
        'webcam': WEBCAM_CONFIG,
        'file': FILE_CONFIG,
        'performance': PERFORMANCE_CONFIG,
        'logging': LOGGING_CONFIG,
        'plate_patterns': PLATE_PATTERNS,
        'validation': VALIDATION_CONFIG
    }
    
    return config_sections.get(section_name.lower(), {})

def update_config(section_name: str, key: str, value):
    """
    Atualiza uma configuração específica
    
    Args:
        section_name: Nome da seção
        key: Chave da configuração
        value: Novo valor
    """
    config = get_config(section_name)
    if config and key in config:
        config[key] = value
        print(f"✅ Configuração atualizada: {section_name}.{key} = {value}")

def print_config_summary():
    """Imprime um resumo das configurações principais"""
    print("🔧 CONFIGURAÇÕES DA APLICAÇÃO")
    print("=" * 40)
    
    sections = [
        ('Detecção', DETECTION_CONFIG),
        ('Pré-processamento', PREPROCESSING_CONFIG),
        ('OCR', OCR_CONFIG),
        ('Webcam', WEBCAM_CONFIG),
        ('Validação', VALIDATION_CONFIG)
    ]
    
    for name, config in sections:
        print(f"\n📋 {name}:")
        for key, value in config.items():
            print(f"   {key}: {value}")
    
    print("\n💡 Para modificar configurações, edite este arquivo ou use:")
    print("   from config import update_config")
    print("   update_config('detection', 'MIN_CONTOUR_AREA', 1500)")

if __name__ == "__main__":
    print_config_summary()
