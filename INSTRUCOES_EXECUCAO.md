# Instruções para Rodar o Modelo WRF - Mato Grosso

## Configuração da Simulação
- **Região**: Mato Grosso - Chapada dos Guimarães
- **Data**: 06/03/2021
- **Rodada**: 12Z
- **Período de simulação**: 15Z até 00Z (9 horas)
- **Resolução**: 3 km
- **Grade**: 200x200 pontos
- **Centro do domínio**: -15.45°S, -55.75°W

## Passo a Passo para Execução na VM Google Cloud

### 1. Conectar na VM via SSH
```bash
# Se você já está conectado, pule este passo
gcloud compute ssh <nome-da-sua-vm> --zone=<sua-zona>
```

### 2. Transferir os arquivos para a VM
```bash
# Na sua máquina local (não na VM), execute:
gcloud compute scp /workspace/*.sh <nome-da-vm>:/tmp/ --zone=<sua-zona>
gcloud compute scp /workspace/namelist.* <nome-da-vm>:/tmp/ --zone=<sua-zona>
gcloud compute scp /workspace/visualizar_resultados.py <nome-da-vm>:/tmp/ --zone=<sua-zona>
```

### 3. Na VM, executar o modelo

#### Opção A: Execução Rápida (Recomendado)
```bash
# Copiar e executar o script rápido
cp /tmp/quick_run.sh ~/
chmod +x ~/quick_run.sh
cd ~
./quick_run.sh
```

#### Opção B: Execução Manual Detalhada
```bash
# Copiar arquivos
cp /tmp/run_wrf_mt.sh ~/
cp /tmp/namelist.* ~/
chmod +x ~/run_wrf_mt.sh

# Executar o modelo
./run_wrf_mt.sh
```

### 4. Monitorar o Progresso

Durante a execução, você pode monitorar o progresso com:

```bash
# Ver log principal do WRF
tail -f /home/wrf_run/MT_*/wrf.log

# Ver erros (se houver)
tail -f /home/wrf_run/MT_*/rsl.error.0000

# Verificar se os arquivos de saída estão sendo criados
ls -lah /home/wrf_run/MT_*/wrfout_d01_*
```

### 5. Tempo Estimado de Execução

- **Download dos dados GFS**: ~5-10 minutos
- **WPS (geogrid, ungrib, metgrid)**: ~5-10 minutos
- **WRF real.exe**: ~2-5 minutos
- **WRF wrf.exe**: ~1-3 horas (depende dos recursos da VM)

**Total estimado**: 1.5 - 3.5 horas

### 6. Verificar Resultados

Após a conclusão, os arquivos de saída estarão em:
```bash
/home/wrf_run/MT_*/wrfout_d01_*
```

Haverá um arquivo para cada hora de simulação:
- wrfout_d01_2021-03-06_15:00:00
- wrfout_d01_2021-03-06_16:00:00
- wrfout_d01_2021-03-06_17:00:00
- ... até ...
- wrfout_d01_2021-03-07_00:00:00

### 7. Visualizar Resultados

```bash
# Instalar dependências Python (se necessário)
pip install netCDF4 matplotlib cartopy numpy

# Copiar script de visualização
cp /tmp/visualizar_resultados.py /home/wrf_run/MT_*/

# Executar visualização
cd /home/wrf_run/MT_*/
python visualizar_resultados.py wrfout_d01_2021-03-06_15:00:00
```

## Solução de Problemas

### Erro: WRF/WPS não encontrado
```bash
# Verificar instalação
ls -la /home/WRF
ls -la /home/WPS
ls -la /home/WPS_GEOG
```

### Erro: Dados GFS não baixados
```bash
# Tentar fonte alternativa
cd /home/wrf_run/MT_*/gfs_data
# Baixar manualmente de:
# https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/
```

### Erro: MPI não encontrado
```bash
# Instalar OpenMPI
sudo apt-get update
sudo apt-get install -y openmpi-bin libopenmpi-dev
```

### Memória insuficiente
```bash
# Reduzir número de processadores
# Editar run_wrf_mt.sh e mudar:
# mpirun -np 8 ./wrf.exe  →  mpirun -np 4 ./wrf.exe
```

## Recursos da VM Recomendados

### Mínimo
- **vCPUs**: 4
- **Memória**: 16 GB
- **Disco**: 50 GB

### Recomendado
- **vCPUs**: 8-16
- **Memória**: 32-64 GB
- **Disco**: 100 GB
- **Tipo de máquina GCP**: n2-standard-8 ou n2-standard-16

## Comandos Úteis

```bash
# Ver uso de CPU e memória
htop

# Ver espaço em disco
df -h

# Ver processos WRF rodando
ps aux | grep wrf

# Parar execução do WRF (se necessário)
pkill wrf.exe

# Limpar arquivos temporários
rm -rf /home/wrf_run/MT_*/FILE:*
rm -rf /home/wrf_run/MT_*/gfs_data
```

## Arquivos Gerados

Após a execução bem-sucedida, você terá:

1. **Arquivos WPS**:
   - geo_em.d01.nc (grade geográfica)
   - met_em.d01.*.nc (dados meteorológicos interpolados)

2. **Arquivos WRF**:
   - wrfinput_d01 (condições iniciais)
   - wrfbdy_d01 (condições de contorno)
   - wrfout_d01_* (saídas horárias)

3. **Logs**:
   - geogrid.log, ungrib.log, metgrid.log
   - real.log, wrf.log
   - rsl.error.*, rsl.out.*

## Contato e Suporte

Se encontrar problemas, verifique:
1. Os logs de erro em `/home/wrf_run/MT_*/rsl.error.0000`
2. O espaço em disco disponível
3. A memória disponível na VM

Boa simulação! 🌦️