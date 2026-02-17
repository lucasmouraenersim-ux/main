#!/bin/bash
#
# Script para download de dados GFS para rodar WRF
# Data: 06/03/2021, rodada 12z
# Previsão: 15z até 00z do dia seguinte (12 horas)
#

# Configurações
DATA_DIR="./gfs_data"
START_DATE="20210306"
CYCLE="12"

# Criar diretório de dados
mkdir -p ${DATA_DIR}
cd ${DATA_DIR}

echo "=========================================="
echo "Baixando dados GFS para ${START_DATE} ${CYCLE}z"
echo "=========================================="

# URLs base do NCEP
BASE_URL="https://www.ncei.noaa.gov/data/global-forecast-system/access/historical/analysis/${START_DATE:0:6}/${START_DATE}"

# Baixar arquivos de 12z até 00z do dia seguinte (horas 00, 03, 06, 09, 12)
# Para a rodada de 12z, precisamos dos horários: 12z, 15z, 18z, 21z, 00z
for hour in 00 03 06 09 12; do
    FILE="gfs_3_${START_DATE}_${CYCLE}00_${hour}00.grb2"
    
    echo "Baixando: $FILE"
    wget -c "${BASE_URL}/${FILE}" -O ${FILE}
    
    if [ $? -ne 0 ]; then
        echo "Erro ao baixar $FILE"
        echo "Tentando URL alternativo..."
        # URL alternativo (NOMADS Archive)
        ALT_URL="https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs.${START_DATE}/${CYCLE}/atmos"
        wget -c "${ALT_URL}/gfs.t${CYCLE}z.pgrb2.0p25.f0${hour}" -O ${FILE}
    fi
done

echo "=========================================="
echo "Download concluído!"
echo "=========================================="
echo ""
echo "Arquivos baixados em: ${DATA_DIR}"
ls -lh

cd ..
