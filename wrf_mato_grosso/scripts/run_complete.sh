#!/bin/bash

# Script completo para executar toda a cadeia WRF
# Mato Grosso - 06/03/2021 12z

echo "=========================================="
echo "  SIMULAÇÃO WRF - MATO GROSSO"
echo "=========================================="
echo "Data: 06/03/2021"
echo "Ciclo: 12z"
echo "Período: 15z - 00z (12 horas)"
echo "Resolução: 3km"
echo "Domínio: Chapada dos Guimarães e região"
echo "=========================================="
echo ""

# Verificar dependências
echo "Verificando dependências..."

# Verificar se wget está disponível
if ! command -v wget &> /dev/null; then
    echo "Instalando wget..."
    sudo apt-get update && sudo apt-get install -y wget
fi

# Verificar se WRF/WPS estão instalados
if [ ! -d "/opt/WRF" ] || [ ! -d "/opt/WPS" ]; then
    echo "ATENÇÃO: WRF/WPS não encontrados em /opt/"
    echo "Você precisa instalar o WRF e WPS primeiro."
    echo "Deseja continuar mesmo assim? (s/n)"
    read -r response
    if [[ ! "$response" =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

# Criar diretórios necessários
mkdir -p ../data ../output/{wps_output,wrf_output}

# Tornar scripts executáveis
chmod +x *.sh

echo "1. Baixando dados GFS..."
./download_gfs.sh
if [ $? -ne 0 ]; then
    echo "Erro no download dos dados!"
    exit 1
fi

echo ""
echo "2. Executando WPS..."
./run_wps.sh
if [ $? -ne 0 ]; then
    echo "Erro no WPS!"
    exit 1
fi

echo ""
echo "3. Executando WRF..."
./run_wrf.sh
if [ $? -ne 0 ]; then
    echo "Erro no WRF!"
    exit 1
fi

echo ""
echo "=========================================="
echo "  SIMULAÇÃO CONCLUÍDA COM SUCESSO!"
echo "=========================================="
echo ""
echo "Arquivos de saída disponíveis em:"
echo "- WPS: ../output/wps_output/"
echo "- WRF: ../output/wrf_output/"
echo ""
echo "Para visualizar os resultados, use ferramentas como:"
echo "- NCL (NCAR Command Language)"
echo "- Python com xarray/matplotlib"
echo "- GrADS"
echo "- VAPOR"