# Simulação WRF - Mato Grosso

Configuração para executar o modelo WRF (Weather Research and Forecasting) para a região de Mato Grosso, com foco na Chapada dos Guimarães.

## Especificações da Simulação

- **Data**: 06/03/2021
- **Ciclo**: 12z 
- **Período**: 15z até 00z (12 horas)
- **Resolução**: 3km
- **Domínio**: Mato Grosso com zoom em Chapada dos Guimarães
- **Dados**: GFS 0.25°

## Estrutura do Projeto

```
wrf_mato_grosso/
├── namelists/          # Arquivos de configuração
│   ├── namelist.wps    # Configuração WPS
│   └── namelist.input  # Configuração WRF
├── scripts/            # Scripts de execução
│   ├── install_wrf.sh      # Instalação WRF/WPS
│   ├── download_gfs.sh     # Download dados GFS
│   ├── run_wps.sh          # Executar WPS
│   ├── run_wrf.sh          # Executar WRF
│   ├── run_complete.sh     # Execução completa
│   └── visualize_results.py # Visualização
├── data/               # Dados meteorológicos (GFS)
└── output/             # Resultados
    ├── wps_output/     # Saída do WPS
    ├── wrf_output/     # Saída do WRF
    └── figures/        # Gráficos gerados
```

## Configuração do Domínio

- **Projeção**: Mercator
- **Centro**: Lat -15.5°, Lon -55.5° (próximo à Chapada dos Guimarães)
- **Pontos de grade**: 150 x 120
- **Resolução**: 3 km
- **Níveis verticais**: 35

## Execução

### 1. Instalação (se necessário)

```bash
cd wrf_mato_grosso/scripts
chmod +x install_wrf.sh
./install_wrf.sh
```

### 2. Execução Completa

```bash
cd wrf_mato_grosso/scripts
chmod +x run_complete.sh
./run_complete.sh
```

### 3. Execução por Etapas

```bash
# 1. Download dos dados
./download_gfs.sh

# 2. Preprocessamento (WPS)
./run_wps.sh

# 3. Simulação (WRF)
./run_wrf.sh
```

### 4. Visualização

```bash
# Instalar dependências Python
pip3 install matplotlib cartopy netcdf4 numpy

# Gerar gráficos
python3 visualize_results.py
```

## Requisitos do Sistema

### Hardware Mínimo
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Disco**: 20 GB livres
- **Rede**: Conexão para download (~2 GB)

### Software
- Ubuntu 18.04+ ou Debian 10+
- GCC/Gfortran
- NetCDF4
- OpenMPI
- Python 3.6+

## Configuração da VM Google Cloud

### Tipo de Instância Recomendada
```bash
# Criar VM
gcloud compute instances create wrf-vm \
    --zone=us-central1-a \
    --machine-type=n1-standard-4 \
    --boot-disk-size=50GB \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud
```

### Conectar via SSH
```bash
gcloud compute ssh wrf-vm --zone=us-central1-a
```

## Variáveis de Saída

O modelo WRF gera diversas variáveis meteorológicas:

- **T2**: Temperatura a 2m (K)
- **U10, V10**: Componentes do vento a 10m (m/s)
- **PSFC**: Pressão à superfície (Pa)
- **Q2**: Umidade específica a 2m (kg/kg)
- **RAINC**: Precipitação convectiva (mm)
- **RAINNC**: Precipitação não-convectiva (mm)
- **SWDOWN**: Radiação solar incidente (W/m²)

## Horários de Saída

A simulação gera saídas horárias das 15z às 00z:
- 15:00 UTC (12:00 local)
- 16:00 UTC (13:00 local)
- ...
- 00:00 UTC (21:00 local do dia anterior)

## Troubleshooting

### Erro de Memória
```bash
# Reduzir número de processos MPI
# Editar run_wrf.sh: mpirun -np 2 (ao invés de 4)
```

### Erro de Download
```bash
# Verificar conectividade
ping nomads.ncep.noaa.gov

# Download manual se necessário
wget https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs.20210306/12/atmos/gfs.t12z.pgrb2.0p25.f003
```

### Erro de Compilação WRF
```bash
# Verificar dependências
sudo apt-get install build-essential gfortran libnetcdf-dev

# Recompilar
cd /opt/WRF
./clean -a
./configure
./compile em_real
```

## Contato

Para dúvidas sobre a configuração específica para Mato Grosso ou ajustes no domínio, consulte a documentação oficial do WRF: https://www2.mmm.ucar.edu/wrf/users/