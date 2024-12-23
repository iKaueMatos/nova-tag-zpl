#!/bin/bash

# Atualizar os repositórios
echo "Atualizando os repositórios..."
sudo apt update && sudo apt upgrade -y

# Instalar dependências básicas
echo "Instalando dependências..."
sudo apt install -y python3 python3-pip python3-venv python3-tk

# Criar ambiente virtual
echo "Criando ambiente virtual..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "Ambiente virtual criado."
else
    echo "Ambiente virtual já existe."
fi

# Ativar ambiente virtual
source .venv/bin/activate

# Instalar dependências do projeto
echo "Instalando dependências do projeto..."
pip install --upgrade pip
pip install -r requirements.txt

# Verificar instalação do PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    echo "Instalando PyInstaller..."
    pip install pyinstaller
else
    echo "PyInstaller já está instalado."
fi

# Concluir configuração
echo "Configuração concluída! Execute o projeto com:"
echo "source .venv/bin/activate && python3 main.py"
