#!/bin/bash

echo "🇧🇷 Iniciando Treinamento dos Modelos YOLO Especializados para Brasil"
echo "=================================================================="

if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Execute este script no diretório raiz do projeto"
    exit 1
fi

show_menu() {
    echo ""
    echo "🎯 Escolha uma opção:"
    echo "1) 🚦 Treinar modelo de placas de sinalização"
    echo "2) 🚗 Treinar modelo de placas de veículos"
    echo "3) 🔄 Treinar ambos os modelos"
    echo "4) 📊 Preparar dados de treinamento"
    echo "5) 🔍 Coletar dados brasileiros"
    echo "6) ✅ Validar modelos treinados"
    echo "7) 🚀 Iniciar sistema completo"
    echo "8) 📚 Mostrar documentação"
    echo "0) ❌ Sair"
    echo ""
    read -p "Digite sua opção: " choice
}

check_dependencies() {
    echo "🔍 Verificando dependências..."
    
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python3 não encontrado. Instale Python 3.8+"
        exit 1
    fi
    
    if ! command -v pip3 &> /dev/null; then
        echo "❌ pip3 não encontrado. Instale pip"
        exit 1
    fi
    
    if ! python3 -c "import ultralytics" &> /dev/null; then
        echo "⚠️ Ultralytics não encontrado. Instalando..."
        pip3 install ultralytics
    fi
    
    if ! python3 -c "import cv2" &> /dev/null; then
        echo "⚠️ OpenCV não encontrado. Instalando..."
        pip3 install opencv-python
    fi
    
    echo "✅ Dependências verificadas!"
}

prepare_data() {
    echo "📊 Preparando dados de treinamento..."
    
    python3 scripts/prepare_training_data.py sample
    
    echo "✅ Dados preparados com sucesso!"
}

collect_data() {
    echo "🔍 Coletando dados brasileiros..."
    
    python3 scripts/collect_brazilian_data.py --create-structure
    
    python3 scripts/collect_brazilian_data.py --source all --max-images 100
    
    echo "✅ Coleta de dados concluída!"
}

train_signal() {
    echo "🚦 Treinando modelo de placas de sinalização..."
    
    if [ ! -d "datasets/signal_plates/images/train" ]; then
        echo "⚠️ Dataset não encontrado. Preparando dados primeiro..."
        prepare_data
    fi
    
    python3 scripts/train_yolo_models.py --model signal --epochs 50
    
    echo "✅ Treinamento de sinalização concluído!"
}

train_vehicle() {
    echo "🚗 Treinando modelo de placas de veículos..."
    
    if [ ! -d "datasets/vehicle_plates/images/train" ]; then
        echo "⚠️ Dataset não encontrado. Preparando dados primeiro..."
        prepare_data
    fi
    
    python3 scripts/train_yolo_models.py --model vehicle --epochs 50
    
    echo "✅ Treinamento de veículos concluído!"
}

train_both() {
    echo "🔄 Treinando ambos os modelos..."
    
    if [ ! -d "datasets/signal_plates/images/train" ] || [ ! -d "datasets/vehicle_plates/images/train" ]; then
        echo "⚠️ Datasets não encontrados. Preparando dados primeiro..."
        prepare_data
    fi
    
    python3 scripts/train_yolo_models.py --model both --epochs 50
    
    echo "✅ Treinamento de ambos os modelos concluído!"
}

validate_models() {
    echo "✅ Validando modelos treinados..."
    
    if [ -f "models/signal_plates_yolo.pt" ]; then
        echo "🔍 Validando modelo de sinalização..."
        python3 scripts/train_yolo_models.py --model signal --validate --test-image datasets/signal_plates/images/train/train_0000.jpg
    else
        echo "⚠️ Modelo de sinalização não encontrado"
    fi
    
    if [ -f "models/vehicle_plates_yolo.pt" ]; then
        echo "🔍 Validando modelo de veículos..."
        python3 scripts/train_yolo_models.py --model vehicle --validate --test-image datasets/vehicle_plates/images/train/train_0000.jpg
    else
        echo "⚠️ Modelo de veículos não encontrado"
    fi
    
    echo "✅ Validação concluída!"
}

start_system() {
    echo "🚀 Iniciando sistema completo..."
    
    if ! docker info &> /dev/null; then
        echo "❌ Docker não está rodando. Inicie o Docker Desktop"
        exit 1
    fi
    
    docker-compose -f docker-compose.prod.yml up -d
    
    echo "✅ Sistema iniciado!"
    echo "🌐 Interface: http://localhost/interface/"
    echo "🔌 API: http://localhost:8000/api/v1/"
    echo "📊 Dashboard: http://localhost:8080/"
}

show_docs() {
    echo "📚 Documentação disponível:"
    echo ""
    echo "📖 GUIA_TREINAMENTO_YOLO.md - Guia completo de treinamento"
    echo "🏗️ ARQUITETURA_YOLO_ESPECIALIZADO.md - Arquitetura dos modelos"
    echo "📁 scripts/ - Scripts de treinamento e coleta"
    echo "⚙️ config/ - Configurações dos modelos"
    echo ""
    echo "💡 Dica: Use 'cat GUIA_TREINAMENTO_YOLO.md | less' para ler o guia"
}

main() {
    echo "🎉 Bem-vindo ao Sistema de Treinamento YOLO para Brasil!"
    
    check_dependencies
    
    while true; do
        show_menu
        
        case $choice in
            1)
                train_signal
                ;;
            2)
                train_vehicle
                ;;
            3)
                train_both
                ;;
            4)
                prepare_data
                ;;
            5)
                collect_data
                ;;
            6)
                validate_models
                ;;
            7)
                start_system
                ;;
            8)
                show_docs
                ;;
            0)
                echo "👋 Até logo!"
                exit 0
                ;;
            *)
                echo "❌ Opção inválida. Tente novamente."
                ;;
        esac
        
        echo ""
        read -p "Pressione Enter para continuar..."
    done
}

if [ "$1" = "signal" ]; then
    train_signal
elif [ "$1" = "vehicle" ]; then
    train_vehicle
elif [ "$1" = "both" ]; then
    train_both
elif [ "$1" = "prepare" ]; then
    prepare_data
elif [ "$1" = "collect" ]; then
    collect_data
elif [ "$1" = "validate" ]; then
    validate_models
elif [ "$1" = "start" ]; then
    start_system
elif [ "$1" = "help" ]; then
    echo "Uso: $0 [opção]"
    echo ""
    echo "Opções:"
    echo "  signal    - Treinar modelo de sinalização"
    echo "  vehicle   - Treinar modelo de veículos"
    echo "  both      - Treinar ambos os modelos"
    echo "  prepare   - Preparar dados de treinamento"
    echo "  collect   - Coletar dados brasileiros"
    echo "  validate  - Validar modelos treinados"
    echo "  start     - Iniciar sistema completo"
    echo "  help      - Mostrar esta ajuda"
    echo ""
    echo "Sem argumentos: Menu interativo"
    exit 0
else
    main
fi
