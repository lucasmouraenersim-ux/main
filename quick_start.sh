#!/bin/bash
#
# Script de início rápido - Executar tudo de uma vez
#

set -e

echo "=========================================="
echo "   SIMULAÇÃO WRF - MATO GROSSO"
echo "   Chapada dos Guimarães - 3km"
echo "   06/03/2021 12z - Previsão 15z-00z"
echo "=========================================="
echo ""

# Verificar se WRF está configurado
if [ -z "$WRF_DIR" ]; then
    echo "⚠️  Variável WRF_DIR não está configurada!"
    echo "Por favor, configure as variáveis de ambiente:"
    echo ""
    echo "export WRF_DIR=/caminho/para/WRF"
    echo "export WPS_DIR=/caminho/para/WPS"
    echo "export NPROCS=4  # Número de processadores"
    echo ""
    read -p "Deseja continuar mesmo assim? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Etapa 1/2: Baixando dados GFS..."
./download_gfs.sh

echo ""
echo "Etapa 2/2: Executando WRF..."
./run_wrf.sh

echo ""
echo "=========================================="
echo "✓ Processo completo finalizado!"
echo "=========================================="
