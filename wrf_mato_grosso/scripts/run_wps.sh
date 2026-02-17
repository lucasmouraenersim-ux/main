#!/bin/bash

# Script para executar o WPS (WRF Preprocessing System)
# Processa dados GFS para grade de Mato Grosso

# Verificar se WRF/WPS está instalado
WRF_DIR="/opt/WRF"
WPS_DIR="/opt/WPS"

if [ ! -d "$WPS_DIR" ]; then
    echo "Erro: WPS não encontrado em $WPS_DIR"
    echo "Por favor, instale o WPS primeiro"
    exit 1
fi

# Diretório de trabalho
WORK_DIR=$(pwd)
DATA_DIR="$WORK_DIR/../data"
NAMELIST_DIR="$WORK_DIR/../namelists"

echo "=== Executando WPS para Mato Grosso ==="
echo "Diretório de trabalho: $WORK_DIR"
echo "Dados GFS: $DATA_DIR"

# Copiar namelist.wps
cp $NAMELIST_DIR/namelist.wps .

# 1. GEOGRID - Criar grade geográfica
echo "1. Executando geogrid.exe..."
$WPS_DIR/geogrid.exe
if [ $? -ne 0 ]; then
    echo "Erro no geogrid!"
    exit 1
fi

# 2. UNGRIB - Processar dados GFS
echo "2. Executando ungrib.exe..."

# Link dos arquivos GFS
$WPS_DIR/link_grib.csh $DATA_DIR/gfs.t12z.pgrb2.0p25.f*

# Usar Vtable para GFS
ln -sf $WPS_DIR/ungrib/Variable_Tables/Vtable.GFS Vtable

$WPS_DIR/ungrib.exe
if [ $? -ne 0 ]; then
    echo "Erro no ungrib!"
    exit 1
fi

# 3. METGRID - Interpolar dados meteorológicos para a grade
echo "3. Executando metgrid.exe..."
$WPS_DIR/metgrid.exe
if [ $? -ne 0 ]; then
    echo "Erro no metgrid!"
    exit 1
fi

echo "=== WPS concluído com sucesso! ==="
echo "Arquivos met_em.d01.* criados para o WRF"

# Mover arquivos para diretório de saída
mkdir -p ../output/wps_output
mv met_em.d01.* ../output/wps_output/
mv geo_em.d01.nc ../output/wps_output/

echo "Arquivos WPS salvos em ../output/wps_output/"