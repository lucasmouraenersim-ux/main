#!/usr/bin/env python3
"""
Script para visualizar resultados do WRF para Mato Grosso
Região: Chapada dos Guimarães
"""

import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.colors import LinearSegmentedColormap
import sys
import os
from datetime import datetime, timedelta

def plotar_precipitacao(arquivo_wrf, tempo_idx=0):
    """
    Plota precipitação acumulada do WRF
    """
    # Abrir arquivo
    ncfile = Dataset(arquivo_wrf)
    
    # Extrair variáveis
    lat = ncfile.variables['XLAT'][tempo_idx, :, :]
    lon = ncfile.variables['XLONG'][tempo_idx, :, :]
    
    # Precipitação acumulada
    rainc = ncfile.variables['RAINC'][tempo_idx, :, :]  # Convectiva
    rainnc = ncfile.variables['RAINNC'][tempo_idx, :, :]  # Não-convectiva
    precip = rainc + rainnc
    
    # Temperatura 2m
    t2 = ncfile.variables['T2'][tempo_idx, :, :] - 273.15  # Converter para Celsius
    
    # Vento 10m
    u10 = ncfile.variables['U10'][tempo_idx, :, :]
    v10 = ncfile.variables['V10'][tempo_idx, :, :]
    wspd = np.sqrt(u10**2 + v10**2)
    
    # Tempo
    times = ncfile.variables['Times'][tempo_idx]
    time_str = ''.join([t.decode() for t in times])
    
    # Configurar figura
    fig = plt.figure(figsize=(16, 12))
    
    # Projeção
    proj = ccrs.PlateCarree()
    
    # --- Subplot 1: Precipitação ---
    ax1 = fig.add_subplot(2, 2, 1, projection=proj)
    ax1.set_extent([-57, -54.5, -16.5, -14], crs=proj)
    
    # Cores para precipitação
    levels_precip = [0, 1, 5, 10, 15, 20, 30, 40, 50, 75, 100]
    colors_precip = ['white', 'lightblue', 'blue', 'green', 'yellow', 
                     'orange', 'red', 'darkred', 'purple', 'darkviolet']
    
    cf1 = ax1.contourf(lon, lat, precip, levels=levels_precip, 
                       colors=colors_precip, extend='max', transform=proj)
    
    ax1.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax1.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax1.add_feature(cfeature.STATES, linewidth=0.3)
    
    # Adicionar cidades
    ax1.plot(-55.75, -15.45, 'r*', markersize=10, transform=proj)
    ax1.text(-55.75, -15.35, 'Chapada dos Guimarães', fontsize=10, 
             ha='center', transform=proj)
    
    ax1.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5)
    ax1.set_title(f'Precipitação Acumulada (mm)\n{time_str}')
    
    plt.colorbar(cf1, ax=ax1, label='mm', shrink=0.8)
    
    # --- Subplot 2: Temperatura 2m ---
    ax2 = fig.add_subplot(2, 2, 2, projection=proj)
    ax2.set_extent([-57, -54.5, -16.5, -14], crs=proj)
    
    levels_temp = np.arange(15, 36, 1)
    cf2 = ax2.contourf(lon, lat, t2, levels=levels_temp, 
                       cmap='RdYlBu_r', extend='both', transform=proj)
    
    ax2.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax2.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax2.add_feature(cfeature.STATES, linewidth=0.3)
    
    ax2.plot(-55.75, -15.45, 'r*', markersize=10, transform=proj)
    ax2.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5)
    ax2.set_title(f'Temperatura 2m (°C)\n{time_str}')
    
    plt.colorbar(cf2, ax=ax2, label='°C', shrink=0.8)
    
    # --- Subplot 3: Vento 10m ---
    ax3 = fig.add_subplot(2, 2, 3, projection=proj)
    ax3.set_extent([-57, -54.5, -16.5, -14], crs=proj)
    
    levels_wind = np.arange(0, 20, 2)
    cf3 = ax3.contourf(lon, lat, wspd, levels=levels_wind, 
                       cmap='YlOrRd', extend='max', transform=proj)
    
    # Vetores de vento (subsample para clareza)
    skip = 10
    ax3.quiver(lon[::skip, ::skip], lat[::skip, ::skip], 
               u10[::skip, ::skip], v10[::skip, ::skip], 
               transform=proj, alpha=0.7, scale=100)
    
    ax3.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax3.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax3.add_feature(cfeature.STATES, linewidth=0.3)
    
    ax3.plot(-55.75, -15.45, 'r*', markersize=10, transform=proj)
    ax3.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5)
    ax3.set_title(f'Vento 10m (m/s)\n{time_str}')
    
    plt.colorbar(cf3, ax=ax3, label='m/s', shrink=0.8)
    
    # --- Subplot 4: Informações do domínio ---
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.axis('off')
    
    info_text = f"""
    SIMULAÇÃO WRF - MATO GROSSO
    ============================
    
    Data/Hora: {time_str}
    
    Domínio:
    - Centro: Chapada dos Guimarães (-15.45°, -55.75°)
    - Resolução: 3 km
    - Pontos: 200 x 200
    - Níveis verticais: 45
    
    Estatísticas:
    - Precip. máx: {precip.max():.1f} mm
    - Precip. méd: {precip.mean():.1f} mm
    - Temp. máx: {t2.max():.1f} °C
    - Temp. mín: {t2.min():.1f} °C
    - Temp. méd: {t2.mean():.1f} °C
    - Vento máx: {wspd.max():.1f} m/s
    - Vento méd: {wspd.mean():.1f} m/s
    """
    
    ax4.text(0.1, 0.9, info_text, transform=ax4.transAxes,
             fontsize=12, verticalalignment='top', fontfamily='monospace')
    
    plt.tight_layout()
    
    # Salvar figura
    output_file = f'wrf_mt_{time_str.replace(":", "")}.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Figura salva: {output_file}")
    
    plt.show()
    
    ncfile.close()
    
    return output_file

def main():
    """
    Função principal
    """
    if len(sys.argv) < 2:
        print("Uso: python visualizar_resultados.py <arquivo_wrfout>")
        print("Exemplo: python visualizar_resultados.py wrfout_d01_2021-03-06_15:00:00")
        sys.exit(1)
    
    arquivo = sys.argv[1]
    
    if not os.path.exists(arquivo):
        print(f"Erro: Arquivo {arquivo} não encontrado!")
        sys.exit(1)
    
    print(f"Processando arquivo: {arquivo}")
    
    # Abrir arquivo para verificar número de tempos
    nc = Dataset(arquivo)
    ntimes = len(nc.dimensions['Time'])
    nc.close()
    
    print(f"Arquivo contém {ntimes} tempos")
    
    # Plotar todos os tempos disponíveis
    for t in range(ntimes):
        print(f"\nProcessando tempo {t+1}/{ntimes}...")
        try:
            plotar_precipitacao(arquivo, t)
        except Exception as e:
            print(f"Erro ao processar tempo {t}: {e}")
            continue

if __name__ == "__main__":
    main()