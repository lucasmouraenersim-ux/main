# Simulação WRF - Mato Grosso
## Configuração: 06/03/2021, 12z, Zoom em Chapada dos Guimarães

### 📋 Especificações da Simulação

- **Região**: Mato Grosso com zoom em Chapada dos Guimarães
- **Data**: 06 de Março de 2021
- **Rodada**: 12z (meio-dia UTC)
- **Período de Previsão**: 15z até 00z (12 horas)
- **Resolução**: 
  - Domínio 1 (d01): 9km
  - Domínio 2 (d02): 3km (nested, zoom em Chapada dos Guimarães)
- **Centro do domínio**: -15.46°S, -55.75°W (Chapada dos Guimarães)

### 🗂️ Estrutura dos Domínios

**Domínio 1 (9km)**:
- Pontos de grade: 150 x 120
- Cobre grande parte de Mato Grosso

**Domínio 2 (3km)**:
- Pontos de grade: 181 x 181
- Nested 3:1 dentro do domínio 1
- Foco em Chapada dos Guimarães e região

### 🚀 Como Executar

#### Pré-requisitos

1. WRF e WPS instalados na VM
2. Dados geográficos (WPS_GEOG) baixados
3. Conexão com internet para download dos dados GFS

#### Passo 1: Download dos Dados GFS

```bash
./download_gfs.sh
```

Este script irá baixar os dados GFS de análise para 06/03/2021, rodada 12z.

#### Passo 2: Executar a Simulação

```bash
# Opção 1: Usando configurações padrão
./run_wrf.sh

# Opção 2: Personalizando diretórios e número de processadores
export WRF_DIR=/caminho/para/WRF
export WPS_DIR=/caminho/para/WPS
export NPROCS=8
./run_wrf.sh
```

### 📊 Configurações Físicas do Modelo

- **Microfísica**: WSM6 (mp_physics = 6)
- **Cumulus**: Kain-Fritsch (apenas domínio 1 - cu_physics = 1)
- **Radiação**: RRTMG (ra_lw_physics = 4, ra_sw_physics = 4)
- **Camada Limite**: YSU (bl_pbl_physics = 1)
- **Superfície**: Noah LSM (sf_surface_physics = 2)

### 📁 Arquivos Principais

- `namelist.wps` - Configuração do WPS (domínios, geografia)
- `namelist.input` - Configuração do WRF (física, dinâmica, tempo)
- `download_gfs.sh` - Script para baixar dados GFS
- `run_wrf.sh` - Script principal de execução

### 🔍 Verificando os Resultados

Após a execução bem-sucedida, os arquivos de saída estarão em:
```
${WRF_DIR}/run/wrfout_d01_*
${WRF_DIR}/run/wrfout_d02_*
```

Para visualizar:

#### Usando Python (recomendado):
```python
import xarray as xr
import matplotlib.pyplot as plt

# Abrir arquivo
ds = xr.open_dataset('wrfout_d02_2021-03-06_15:00:00', engine='netcdf4')

# Ver variáveis disponíveis
print(ds.variables.keys())

# Plotar temperatura, por exemplo
temp = ds['T2'] - 273.15  # Converter K para C
temp.plot()
plt.show()
```

#### Usando NCL:
```bash
ncl_filedump wrfout_d02_2021-03-06_15:00:00
```

### ⚙️ Ajustes e Personalizações

#### Alterar o número de processadores:
Edite a variável `NPROCS` no `run_wrf.sh` ou exporte antes de executar:
```bash
export NPROCS=16
./run_wrf.sh
```

#### Alterar a resolução temporal dos outputs:
No `namelist.input`, modifique:
```
history_interval = 60,  60,  ! Saída a cada 60 minutos
```

#### Mudar física de cumulus:
No `namelist.input`, seção `&physics`:
```
cu_physics = 1,   0,  ! 1=Kain-Fritsch, 2=BMJ, 3=Grell-Freitas, etc.
```

### 📝 Logs e Debugging

Se houver problemas, verifique os seguintes arquivos de log:

**WPS**:
- `${WPS_DIR}/geogrid.log`
- `${WPS_DIR}/ungrib.log`
- `${WPS_DIR}/metgrid.log`

**WRF**:
- `${WRF_DIR}/run/rsl.error.0000` (erros do processo mestre)
- `${WRF_DIR}/run/rsl.out.0000` (saída do processo mestre)

### 🐛 Problemas Comuns

1. **"Segmentation fault" no real.exe ou wrf.exe**
   - Verifique se há memória suficiente
   - Reduza o número de níveis verticais ou o tamanho do domínio

2. **"CFL error" durante a simulação**
   - Reduza o time_step no namelist.input
   - Valor recomendado: 6 * dx (em km)

3. **Arquivos GFS não baixam**
   - Os dados históricos do GFS podem estar em arquivos diferentes
   - Verifique URLs alternativas ou use dados de reanálise (ERA5, CFSR)

### 💡 Dicas

- A simulação de 12 horas com domínio de 3km pode levar várias horas
- Use `screen` ou `tmux` para manter a simulação rodando mesmo se desconectar:
  ```bash
  screen -S wrf_run
  ./run_wrf.sh
  # Ctrl+A, D para desconectar
  # screen -r wrf_run para reconectar
  ```

### 📧 Informações Adicionais

Para mais informações sobre WRF:
- [WRF Users Guide](https://www2.mmm.ucar.edu/wrf/users/)
- [WRF Online Tutorial](https://www2.mmm.ucar.edu/wrf/OnLineTutorial/)
