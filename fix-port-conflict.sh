#!/bin/bash

# Script para corrigir conflito de porta 5000
echo "🔧 Corrigindo conflito de porta 5000..."

# Fazer backup do arquivo original
cp docker-compose.yml docker-compose.yml.backup

# Substituir porta 5000 por 5001 no docker-compose.yml
sed -i 's/5000:5000/5001:5000/g' docker-compose.yml

echo "✅ Porta alterada de 5000 para 5001"
echo "📋 Backup salvo em docker-compose.yml.backup"
echo ""
echo "🚀 Agora execute:"
echo "   docker-compose up -d"