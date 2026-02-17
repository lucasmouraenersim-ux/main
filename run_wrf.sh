#!/bin/bash
#
# Script de execução do WRF para Mato Grosso
# Data: 06/03/2021, rodada 12z, previsão 15z-00z
#

set -e

# Configurações de diretórios (ajuste conforme sua instalação)
WRF_DIR="${WRF_DIR:-/home/ubuntu/WRF}"
WPS_DIR="${WPS_DIR:-/home/ubuntu/WPS}"
WORK_DIR="${WORK_DIR:-$(pwd)}"

# Número de processadores
NPROCS="${NPROCS:-4}"

echo "=========================================="
echo "CONFIGURAÇÃO DO WRF - MATO GROSSO"
echo "=========================================="
echo "Diretório de trabalho: ${WORK_DIR}"
echo "WRF instalado em: ${WRF_DIR}"
echo "WPS instalado em: ${WPS_DIR}"
echo "Processadores: ${NPROCS}"
echo "=========================================="
echo ""

# Função para verificar erros
check_error() {
    if [ $? -ne 0 ]; then
        echo "ERRO: $1"
        exit 1
    fi
}

# 1. PREPARAR WPS
echo "Etapa 1: Preparando WPS..."
cd ${WPS_DIR}

# Copiar namelists
cp ${WORK_DIR}/namelist.wps .
check_error "Falha ao copiar namelist.wps"

# Limpar execuções anteriores
rm -f FILE:* met_em.d0* geo_em.d0* GRIBFILE.* ungrib.log* metgrid.log* geogrid.log*

# 2. RODAR GEOGRID
echo "Etapa 2: Executando geogrid.exe..."
./geogrid.exe >& geogrid.log
check_error "Falha no geogrid.exe. Verifique geogrid.log"
echo "✓ geogrid.exe concluído com sucesso!"

# 3. LINK DOS DADOS GFS
echo "Etapa 3: Fazendo link dos dados GFS..."
./link_grib.csh ${WORK_DIR}/gfs_data/gfs_3_*
check_error "Falha ao fazer link dos arquivos GFS"

# 4. RODAR UNGRIB
echo "Etapa 4: Executando ungrib.exe..."
ln -sf ungrib/Variable_Tables/Vtable.GFS Vtable
./ungrib.exe >& ungrib.log
check_error "Falha no ungrib.exe. Verifique ungrib.log"
echo "✓ ungrib.exe concluído com sucesso!"

# 5. RODAR METGRID
echo "Etapa 5: Executando metgrid.exe..."
./metgrid.exe >& metgrid.log
check_error "Falha no metgrid.exe. Verifique metgrid.log"
echo "✓ metgrid.exe concluído com sucesso!"

# 6. PREPARAR WRF
echo "Etapa 6: Preparando WRF..."
cd ${WRF_DIR}/run

# Limpar execuções anteriores
rm -f met_em.d0* wrfinput_d0* wrfbdy_d01 wrfout_d0* rsl.* namelist.input

# Copiar arquivos do WPS
ln -sf ${WPS_DIR}/met_em.d0* .
check_error "Falha ao copiar met_em files"

# Copiar namelist
cp ${WORK_DIR}/namelist.input .
check_error "Falha ao copiar namelist.input"

# 7. RODAR REAL
echo "Etapa 7: Executando real.exe..."
mpirun -np ${NPROCS} ./real.exe
check_error "Falha no real.exe. Verifique rsl.error.0000"

# Verificar se wrfinput e wrfbdy foram criados
if [ ! -f wrfinput_d01 ] || [ ! -f wrfbdy_d01 ]; then
    echo "ERRO: real.exe não criou os arquivos de entrada necessários"
    echo "Verifique rsl.error.0000 para detalhes"
    exit 1
fi
echo "✓ real.exe concluído com sucesso!"

# 8. RODAR WRF
echo "Etapa 8: Executando wrf.exe..."
echo "Iniciando simulação às $(date)"
echo "Este processo pode demorar várias horas..."

mpirun -np ${NPROCS} ./wrf.exe
check_error "Falha no wrf.exe. Verifique rsl.error.0000"

# Verificar se a simulação foi completada com sucesso
if grep -q "SUCCESS COMPLETE WRF" rsl.error.0000; then
    echo "=========================================="
    echo "✓✓✓ SIMULAÇÃO CONCLUÍDA COM SUCESSO! ✓✓✓"
    echo "=========================================="
    echo "Arquivos de saída:"
    ls -lh wrfout_d0*
    echo ""
    echo "Arquivos salvos em: ${WRF_DIR}/run"
else
    echo "=========================================="
    echo "AVISO: wrf.exe finalizou mas não encontrou"
    echo "mensagem de sucesso. Verifique rsl.error.0000"
    echo "=========================================="
fi

echo ""
echo "Simulação finalizada às $(date)"
echo ""
echo "Para visualizar os resultados, use NCL, Python, ou GrADS"
echo "Localização dos outputs: ${WRF_DIR}/run/wrfout_d0*"
