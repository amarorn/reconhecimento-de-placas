#!/bin/bash

# Script de Execução de Testes - Arquitetura Refatorada de Visão Computacional
# =============================================================================

set -e  # Parar em caso de erro

echo "🧪 INICIANDO EXECUÇÃO DE TESTES"
echo "================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir com cores
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se estamos no diretório correto
if [ ! -f "requirements_refatorado.txt" ]; then
    print_error "Execute este script do diretório raiz do projeto"
    exit 1
fi

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    print_error "Python3 não encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

# Verificar versão do Python
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
print_status "Versão do Python: $PYTHON_VERSION"

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    print_status "Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
print_status "Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
print_status "Atualizando pip..."
pip install --upgrade pip

# Instalar dependências de teste
print_status "Instalando dependências de teste..."
pip install -r requirements_test.txt

# Verificar se pytest está instalado
if ! python -c "import pytest" &> /dev/null; then
    print_error "pytest não foi instalado corretamente"
    exit 1
fi

print_success "Dependências instaladas com sucesso!"

# Executar testes com diferentes níveis de detalhamento
echo ""
echo "🔬 EXECUTANDO TESTES UNITÁRIOS"
echo "==============================="

# Testes unitários
print_status "Executando testes de pré-processamento..."
pytest tests/test_preprocessing.py -v --tb=short

print_status "Executando testes de detecção..."
pytest tests/test_detection.py -v --tb=short

print_status "Executando testes de OCR..."
pytest tests/test_ocr.py -v --tb=short

echo ""
echo "🔗 EXECUTANDO TESTES DE INTEGRAÇÃO"
echo "==================================="

# Testes de integração
print_status "Executando testes de pipeline..."
pytest tests/test_pipeline.py -v --tb=short

print_status "Executando testes de integração..."
pytest tests/test_integration.py -v --tb=short

echo ""
echo "📊 GERANDO RELATÓRIO DE COBERTURA"
echo "=================================="

# Relatório de cobertura
print_status "Executando todos os testes com cobertura..."
pytest tests/ --cov=vision --cov=config --cov-report=term-missing --cov-report=html:htmlcov

# Verificar se o relatório foi gerado
if [ -d "htmlcov" ]; then
    print_success "Relatório de cobertura gerado em htmlcov/"
    print_status "Para visualizar: open htmlcov/index.html"
else
    print_warning "Relatório de cobertura não foi gerado"
fi

echo ""
echo "🧹 LIMPEZA E FINALIZAÇÃO"
echo "========================="

# Desativar ambiente virtual
deactivate

# Verificar resultados
if [ $? -eq 0 ]; then
    print_success "✅ Todos os testes executados com sucesso!"
    echo ""
    echo "📋 RESUMO:"
    echo "  - Testes unitários: ✅"
    echo "  - Testes de integração: ✅"
    echo "  - Cobertura de código: ✅"
    echo "  - Relatórios gerados: ✅"
    echo ""
    echo "🚀 Arquitetura refatorada está funcionando perfeitamente!"
else
    print_error "❌ Alguns testes falharam. Verifique os logs acima."
    exit 1
fi