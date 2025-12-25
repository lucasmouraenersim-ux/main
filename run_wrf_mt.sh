#!/bin/bash
#
# Script para rodar o modelo WRF para Mato Grosso
# Grade de 3km centrada em Chapada dos Guimarães
# Data: 06/03/2021 - Rodada 12Z (15Z-00Z)
#

echo "=========================================="
echo "Iniciando simulação WRF para Mato Grosso"
echo "Data: 06/03/2021 - Rodada 12Z"
echo "Período: 15Z até 00Z"
echo "Resolução: 3km"
echo "Região: Chapada dos Guimarães - MT"
echo "=========================================="

# Configurações de ambiente
export WRF_DIR=/home/WRF
export WPS_DIR=/home/WPS
export DATA_DIR=/home/DATA
export WORK_DIR=/home/wrf_run/MT_2021030612

# Criar diretório de trabalho
mkdir -p $WORK_DIR
cd $WORK_DIR

echo ""
echo "1. Preparando ambiente de trabalho..."
# Copiar namelists
cp /workspace/namelist.wps $WORK_DIR/
cp /workspace/namelist.input $WORK_DIR/

# Links para executáveis do WPS
ln -sf $WPS_DIR/geogrid.exe .
ln -sf $WPS_DIR/ungrib.exe .
ln -sf $WPS_DIR/metgrid.exe .
ln -sf $WPS_DIR/link_grib.csh .

# Links para tabelas do WPS
ln -sf $WPS_DIR/geogrid/GEOGRID.TBL .
ln -sf $WPS_DIR/ungrib/Variable_Tables/Vtable.GFS Vtable
ln -sf $WPS_DIR/metgrid/METGRID.TBL .

echo ""
echo "2. Baixando dados GFS para 06/03/2021 12Z..."
# Criar diretório para dados GFS
mkdir -p gfs_data
cd gfs_data

# Download dos dados GFS (12Z até 00Z+1 = 13 horas)
for hr in 000 003 006 009 012; do
    echo "Baixando GFS f${hr}..."
    wget -q "https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs.20210306/12/atmos/gfs.t12z.pgrb2.0p25.f${hr}" \
         -O gfs.t12z.pgrb2.0p25.f${hr} || \
    wget -q "https://www.ncei.noaa.gov/data/global-forecast-system/access/historical/analysis/202103/20210306/gfs_4_20210306_1200_${hr}.grb2" \
         -O gfs.t12z.pgrb2.0p25.f${hr}
done

cd $WORK_DIR

echo ""
echo "3. Executando WPS..."
echo "3.1 Link dos arquivos GRIB..."
./link_grib.csh gfs_data/gfs.t12z.pgrb2.0p25.f*

echo "3.2 Executando geogrid.exe..."
mpirun -np 4 ./geogrid.exe >& geogrid.log
if [ ! -f geo_em.d01.nc ]; then
    echo "ERRO: geogrid falhou! Verifique geogrid.log"
    exit 1
fi
echo "geogrid.exe concluído com sucesso!"

echo "3.3 Executando ungrib.exe..."
./ungrib.exe >& ungrib.log
if [ ! -f FILE:2021-03-06_12 ]; then
    echo "ERRO: ungrib falhou! Verifique ungrib.log"
    exit 1
fi
echo "ungrib.exe concluído com sucesso!"

echo "3.4 Executando metgrid.exe..."
mpirun -np 4 ./metgrid.exe >& metgrid.log
if [ ! -f met_em.d01.2021-03-06_12:00:00.nc ]; then
    echo "ERRO: metgrid falhou! Verifique metgrid.log"
    exit 1
fi
echo "metgrid.exe concluído com sucesso!"

echo ""
echo "4. Executando WRF..."

# Links para executáveis do WRF
ln -sf $WRF_DIR/run/real.exe .
ln -sf $WRF_DIR/run/wrf.exe .

# Links para tabelas do WRF
ln -sf $WRF_DIR/run/*.TBL .
ln -sf $WRF_DIR/run/*.txt .
ln -sf $WRF_DIR/run/RRTM* .
ln -sf $WRF_DIR/run/CAM* .
ln -sf $WRF_DIR/run/ozone* .

echo "4.1 Executando real.exe..."
mpirun -np 4 ./real.exe >& real.log
if [ ! -f wrfinput_d01 ]; then
    echo "ERRO: real.exe falhou! Verifique real.log"
    exit 1
fi
echo "real.exe concluído com sucesso!"

echo "4.2 Executando wrf.exe..."
echo "Isso pode levar várias horas..."
mpirun -np 8 ./wrf.exe >& wrf.log &

# Monitorar progresso
echo ""
echo "Monitorando progresso da simulação..."
echo "Use 'tail -f $WORK_DIR/wrf.log' para acompanhar"
echo ""

# Aguardar alguns segundos e verificar se iniciou
sleep 10
if [ -f wrf.log ]; then
    tail -20 wrf.log
    echo ""
    echo "Simulação WRF iniciada!"
    echo "Diretório de trabalho: $WORK_DIR"
    echo "Arquivos de saída serão: wrfout_d01_*"
else
    echo "ERRO: WRF não iniciou corretamente!"
fi

echo ""
echo "=========================================="
echo "Script de configuração concluído!"
echo "A simulação está rodando em background"
echo "Para verificar o progresso use:"
echo "  tail -f $WORK_DIR/wrf.log"
echo "  tail -f $WORK_DIR/rsl.error.0000"
echo "=========================================="