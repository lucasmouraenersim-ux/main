#!/bin/bash

# Script para download dos dados GFS para WRF
# Data: 06/03/2021, rodada 12z
# Período: 15z até 00z (próximo dia)

# Configurações
DATE="20210306"
CYCLE="12"
OUTPUT_DIR="../data"

# Criar diretório se não existir
mkdir -p $OUTPUT_DIR

echo "Baixando dados GFS para $DATE ciclo ${CYCLE}z..."

# URLs base para dados GFS
BASE_URL="https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs.$DATE/$CYCLE/atmos"

# Horários de previsão necessários (em horas após a inicialização)
# 15z = +03h, 18z = +06h, 21z = +09h, 00z = +12h
HOURS=("003" "006" "009" "012")

for hour in "${HOURS[@]}"; do
    filename="gfs.t${CYCLE}z.pgrb2.0p25.f${hour}"
    echo "Baixando $filename..."
    
    # Tentar download com wget
    wget -c -P $OUTPUT_DIR "${BASE_URL}/${filename}" || {
        echo "Erro ao baixar $filename"
        echo "Tentando URL alternativa..."
        # URL alternativa (arquivo histórico)
        ALT_URL="https://www.ncei.noaa.gov/data/global-forecast-system/access/grid-004-0.5-degree/forecast/$DATE/$CYCLE/gfs_4_${DATE}_${CYCLE}00_${hour}.grb2"
        wget -c -P $OUTPUT_DIR -O "${OUTPUT_DIR}/${filename}" "$ALT_URL" || {
            echo "Falha no download de $filename"
        }
    }
done

echo "Download concluído!"
echo "Arquivos salvos em: $OUTPUT_DIR"
ls -la $OUTPUT_DIR/