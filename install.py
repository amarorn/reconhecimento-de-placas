#!/usr/bin/env python3
"""
Script de Instalação - Aplicação de Reconhecimento de Placas
============================================================

Este script automatiza a instalação e configuração da aplicação
de reconhecimento de placas de trânsito.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def print_banner():
    """Imprime o banner da aplicação"""
    print("🚗" + "="*60 + "🚗")
    print("    APLICAÇÃO DE RECONHECIMENTO DE PLACAS DE TRÂNSITO")
    print("    Instalador Automatizado")
    print("🚗" + "="*60 + "🚗")
    print()

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    print("🐍 Verificando versão do Python...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} não é suportado!")
        print("   Requer Python 3.8 ou superior")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatível!")
    return True

def check_pip():
    """Verifica se o pip está disponível"""
    print("\n📦 Verificando pip...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print("✅ pip está disponível!")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pip não encontrado!")
        print("   Instale o pip primeiro: https://pip.pypa.io/en/stable/installation/")
        return False

def create_virtual_environment():
    """Cria um ambiente virtual"""
    print("\n🔧 Criando ambiente virtual...")
    
    venv_name = "venv"
    
    if os.path.exists(venv_name):
        print(f"⚠️  Ambiente virtual '{venv_name}' já existe")
        response = input("   Deseja recriar? (s/N): ").strip().lower()
        if response == 's':
            shutil.rmtree(venv_name)
        else:
            print("   Usando ambiente virtual existente")
            return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", venv_name], check=True)
        print(f"✅ Ambiente virtual '{venv_name}' criado com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao criar ambiente virtual: {e}")
        return False

def get_activate_script():
    """Retorna o caminho para o script de ativação do ambiente virtual"""
    venv_name = "venv"
    
    if platform.system() == "Windows":
        return os.path.join(venv_name, "Scripts", "activate.bat")
    else:
        return os.path.join(venv_name, "bin", "activate")

def install_dependencies():
    """Instala as dependências do projeto"""
    print("\n📚 Instalando dependências...")
    
    # Verificar se requirements.txt existe
    if not os.path.exists("requirements.txt"):
        print("❌ Arquivo requirements.txt não encontrado!")
        return False
    
    # Determinar comando de instalação
    if platform.system() == "Windows":
        pip_cmd = os.path.join("venv", "Scripts", "pip.exe")
    else:
        pip_cmd = os.path.join("venv", "bin", "pip")
    
    try:
        # Atualizar pip primeiro
        print("   Atualizando pip...")
        subprocess.run([pip_cmd, "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # Instalar dependências
        print("   Instalando dependências do requirements.txt...")
        result = subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], 
                              check=True, capture_output=True, text=True)
        
        print("✅ Dependências instaladas com sucesso!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        if e.stderr:
            print(f"   Detalhes: {e.stderr}")
        return False

def create_directories():
    """Cria diretórios necessários"""
    print("\n📁 Criando diretórios...")
    
    directories = [
        "exemplo_imagens",
        "temp",
        "logs"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"   ✅ Criado: {directory}/")
        else:
            print(f"   ⚠️  Já existe: {directory}/")

def test_installation():
    """Testa se a instalação foi bem-sucedida"""
    print("\n🧪 Testando instalação...")
    
    try:
        # Testar import das bibliotecas principais
        import cv2
        print("   ✅ OpenCV importado com sucesso")
        
        import numpy
        print("   ✅ NumPy importado com sucesso")
        
        # Testar se a classe principal pode ser importada
        from plate_recognition import PlateRecognizer
        print("   ✅ Classe PlateRecognizer importada com sucesso")
        
        print("✅ Todos os testes passaram!")
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def create_launcher_scripts():
    """Cria scripts de lançamento para diferentes sistemas"""
    print("\n🚀 Criando scripts de lançamento...")
    
    if platform.system() == "Windows":
        # Script batch para Windows
        batch_content = """@echo off
echo Iniciando Aplicacao de Reconhecimento de Placas...
call venv\\Scripts\\activate.bat
python main.py %*
pause
"""
        with open("run_app.bat", "w") as f:
            f.write(batch_content)
        print("   ✅ Criado: run_app.bat")
        
    else:
        # Script shell para Linux/Mac
        shell_content = """#!/bin/bash
echo "Iniciando Aplicacao de Reconhecimento de Placas..."
source venv/bin/activate
python main.py "$@"
"""
        with open("run_app.sh", "w") as f:
            f.write(shell_content)
        
        # Tornar executável
        os.chmod("run_app.sh", 0o755)
        print("   ✅ Criado: run_app.sh")

def print_usage_instructions():
    """Imprime instruções de uso"""
    print("\n" + "="*60)
    print("🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*60)
    
    print("\n📖 COMO USAR:")
    
    if platform.system() == "Windows":
        print("   Windows: Execute 'run_app.bat' ou:")
        print("   venv\\Scripts\\activate")
        print("   python main.py --help")
    else:
        print("   Linux/Mac: Execute './run_app.sh' ou:")
        print("   source venv/bin/activate")
        print("   python main.py --help")
    
    print("\n🚀 EXEMPLOS DE USO:")
    print("   python main.py --image foto_carro.jpg")
    print("   python main.py --folder imagens_carros/")
    print("   python main.py --webcam")
    
    print("\n🧪 TESTES:")
    print("   python test_app.py")
    print("   python example.py")
    
    print("\n🔧 CONFIGURAÇÕES:")
    print("   python config.py")
    
    print("\n📚 DOCUMENTAÇÃO:")
    print("   Leia o arquivo README.md para mais detalhes")
    
    print("\n" + "="*60)

def main():
    """Função principal do instalador"""
    print_banner()
    
    # Verificações iniciais
    if not check_python_version():
        sys.exit(1)
    
    if not check_pip():
        sys.exit(1)
    
    # Instalação
    if not create_virtual_environment():
        sys.exit(1)
    
    if not install_dependencies():
        print("\n❌ Falha na instalação das dependências!")
        print("   Verifique se você tem conexão com a internet")
        print("   e permissões de escrita no diretório atual")
        sys.exit(1)
    
    # Configuração
    create_directories()
    
    # Testes
    if not test_installation():
        print("\n❌ Falha nos testes de instalação!")
        print("   Verifique se todas as dependências foram instaladas")
        sys.exit(1)
    
    # Scripts de lançamento
    create_launcher_scripts()
    
    # Instruções finais
    print_usage_instructions()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Instalação interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado durante a instalação: {e}")
        sys.exit(1)
