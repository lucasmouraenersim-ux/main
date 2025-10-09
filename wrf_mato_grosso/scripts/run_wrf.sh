#!/bin/bash

# Script para executar o modelo WRF
# Simulação para Mato Grosso - 06/03/2021

# Configurações
WRF_DIR="/opt/WRF"
WORK_DIR=$(pwd)
NAMELIST_DIR="$WORK_DIR/../namelists"
WPS_OUTPUT="../output/wps_output"

if [ ! -d "$WRF_DIR" ]; then
    echo "Erro: WRF não encontrado em $WRF_DIR"
    echo "Por favor, instale o WRF primeiro"
    exit 1
fi

echo "=== Executando WRF para Mato Grosso ==="
echo "Data: 06/03/2021 12z"
echo "Período: 15z - 00z (12 horas)"
echo "Resolução: 3km"

# Verificar se arquivos WPS existem
if [ ! -f "$WPS_OUTPUT/met_em.d01.2021-03-06_12:00:00.nc" ]; then
    echo "Erro: Arquivos WPS não encontrados!"
    echo "Execute primeiro o run_wps.sh"
    exit 1
fi

# Copiar arquivos necessários
cp $NAMELIST_DIR/namelist.input .
cp $WPS_OUTPUT/met_em.d01.* .

# 1. REAL - Inicialização do modelo
echo "1. Executando real.exe..."
mpirun -np 4 $WRF_DIR/main/real.exe
if [ $? -ne 0 ]; then
    echo "Erro no real.exe!"
    exit 1
fi

# Verificar se arquivos de inicialização foram criados
if [ ! -f "wrfinput_d01" ] || [ ! -f "wrfbdy_d01" ]; then
    echo "Erro: Arquivos de inicialização não foram criados!"
    exit 1
fi

# 2. WRF - Execução do modelo
echo "2. Executando wrf.exe..."
echo "Início: $(date)"

# Executar WRF com MPI (ajustar número de processos conforme sua VM)
mpirun -np 4 $WRF_DIR/main/wrf.exe

if [ $? -ne 0 ]; then
    echo "Erro na execução do WRF!"
    exit 1
fi

echo "Fim: $(date)"
echo "=== WRF concluído com sucesso! ==="

# Mover arquivos de saída
mkdir -p ../output/wrf_output
mv wrfout_d01_* ../output/wrf_output/
mv rsl.* ../output/wrf_output/

echo "Arquivos de saída salvos em ../output/wrf_output/"
echo ""
echo "Arquivos gerados:"
ls -la ../output/wrf_output/wrfout_d01_*