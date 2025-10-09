#!/usr/bin/env python3
"""
Script para visualização dos resultados do WRF
Mato Grosso - Chapada dos Guimarães
"""

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from netCDF4 import Dataset
import os
import sys
from datetime import datetime, timedelta

def plot_wrf_variable(wrfout_file, variable='T2', time_idx=0, level=None):
    """
    Plota uma variável do WRF
    
    Parameters:
    -----------
    wrfout_file : str
        Caminho para o arquivo wrfout
    variable : str
        Nome da variável (T2, U10, V10, RAINC, etc.)
    time_idx : int
        Índice temporal
    level : int
        Nível vertical (para variáveis 3D)
    """
    
    # Abrir arquivo NetCDF
    try:
        nc = Dataset(wrfout_file, 'r')
    except:
        print(f"Erro ao abrir arquivo: {wrfout_file}")
        return
    
    # Ler coordenadas
    lats = nc.variables['XLAT'][0, :, :]
    lons = nc.variables['XLONG'][0, :, :]
    
    # Ler variável
    if variable in nc.variables:
        if len(nc.variables[variable].shape) == 4:  # 4D (time, level, lat, lon)
            if level is not None:
                data = nc.variables[variable][time_idx, level, :, :]
            else:
                print(f"Variável {variable} é 4D. Especifique o nível.")
                return
        elif len(nc.variables[variable].shape) == 3:  # 3D (time, lat, lon)
            data = nc.variables[variable][time_idx, :, :]
        else:
            print(f"Dimensões não suportadas para {variable}")
            return
    else:
        print(f"Variável {variable} não encontrada no arquivo")
        print("Variáveis disponíveis:", list(nc.variables.keys()))
        return
    
    # Configurar projeção
    fig = plt.figure(figsize=(12, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())
    
    # Adicionar características geográficas
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS)
    ax.add_feature(cfeature.STATES)
    ax.add_feature(cfeature.RIVERS)
    
    # Plot da variável
    if variable == 'T2':
        # Temperatura em Celsius
        data_plot = data - 273.15
        levels = np.arange(15, 40, 2)
        cmap = 'RdYlBu_r'
        units = '°C'
        title = 'Temperatura a 2m'
    elif variable in ['U10', 'V10']:
        data_plot = data
        levels = np.arange(-10, 11, 1)
        cmap = 'RdBu_r'
        units = 'm/s'
        title = f'Vento {variable}'
    elif variable in ['RAINC', 'RAINNC']:
        data_plot = data
        levels = np.arange(0, 50, 2)
        cmap = 'Blues'
        units = 'mm'
        title = 'Precipitação'
    else:
        data_plot = data
        levels = 20
        cmap = 'viridis'
        units = nc.variables[variable].units if hasattr(nc.variables[variable], 'units') else ''
        title = variable
    
    # Contour plot
    cs = ax.contourf(lons, lats, data_plot, levels=levels, cmap=cmap, transform=ccrs.PlateCarree())
    
    # Colorbar
    cbar = plt.colorbar(cs, ax=ax, orientation='horizontal', pad=0.05, shrink=0.8)
    cbar.set_label(f'{title} ({units})')
    
    # Título
    time_str = nc.variables['Times'][time_idx].tobytes().decode('utf-8')
    plt.title(f'{title} - {time_str}\nMato Grosso - Resolução 3km')
    
    # Marcar Chapada dos Guimarães
    ax.plot(-55.75, -15.46, 'ro', markersize=8, transform=ccrs.PlateCarree())
    ax.text(-55.75, -15.46, ' Chapada dos Guimarães', transform=ccrs.PlateCarree(), 
            fontsize=10, fontweight='bold')
    
    # Definir extensão do mapa
    ax.set_extent([lons.min(), lons.max(), lats.min(), lats.max()], ccrs.PlateCarree())
    
    # Gridlines
    gl = ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
    gl.top_labels = False
    gl.right_labels = False
    
    plt.tight_layout()
    
    # Salvar figura
    output_file = f"{variable}_time_{time_idx:02d}.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Figura salva: {output_file}")
    
    nc.close()
    plt.close()

def create_wind_plot(wrfout_file, time_idx=0):
    """Cria um plot de vetores de vento"""
    
    nc = Dataset(wrfout_file, 'r')
    
    lats = nc.variables['XLAT'][0, :, :]
    lons = nc.variables['XLONG'][0, :, :]
    u10 = nc.variables['U10'][time_idx, :, :]
    v10 = nc.variables['V10'][time_idx, :, :]
    
    # Velocidade do vento
    wind_speed = np.sqrt(u10**2 + v10**2)
    
    fig = plt.figure(figsize=(12, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())
    
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS)
    ax.add_feature(cfeature.STATES)
    
    # Plot velocidade do vento
    cs = ax.contourf(lons, lats, wind_speed, levels=np.arange(0, 20, 1), 
                     cmap='viridis', transform=ccrs.PlateCarree())
    
    # Vetores de vento (subsample para clareza)
    skip = 5
    ax.quiver(lons[::skip, ::skip], lats[::skip, ::skip], 
              u10[::skip, ::skip], v10[::skip, ::skip],
              transform=ccrs.PlateCarree(), scale=200)
    
    cbar = plt.colorbar(cs, ax=ax, orientation='horizontal', pad=0.05, shrink=0.8)
    cbar.set_label('Velocidade do Vento (m/s)')
    
    time_str = nc.variables['Times'][time_idx].tobytes().decode('utf-8')
    plt.title(f'Vento a 10m - {time_str}\nMato Grosso - Resolução 3km')
    
    # Marcar Chapada dos Guimarães
    ax.plot(-55.75, -15.46, 'ro', markersize=8, transform=ccrs.PlateCarree())
    ax.text(-55.75, -15.46, ' Chapada dos Guimarães', transform=ccrs.PlateCarree())
    
    ax.set_extent([lons.min(), lons.max(), lats.min(), lats.max()], ccrs.PlateCarree())
    
    gl = ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
    gl.top_labels = False
    gl.right_labels = False
    
    plt.tight_layout()
    plt.savefig(f"wind_vectors_time_{time_idx:02d}.png", dpi=150, bbox_inches='tight')
    print(f"Figura salva: wind_vectors_time_{time_idx:02d}.png")
    
    nc.close()
    plt.close()

def main():
    """Função principal"""
    
    # Diretório com arquivos WRF
    wrf_output_dir = "../output/wrf_output"
    
    if not os.path.exists(wrf_output_dir):
        print(f"Diretório não encontrado: {wrf_output_dir}")
        print("Execute primeiro a simulação WRF")
        return
    
    # Encontrar arquivos wrfout
    wrfout_files = [f for f in os.listdir(wrf_output_dir) if f.startswith('wrfout_d01')]
    
    if not wrfout_files:
        print("Nenhum arquivo wrfout encontrado")
        return
    
    wrfout_files.sort()
    print(f"Encontrados {len(wrfout_files)} arquivos wrfout")
    
    # Processar primeiro arquivo
    wrfout_file = os.path.join(wrf_output_dir, wrfout_files[0])
    print(f"Processando: {wrfout_file}")
    
    # Criar diretório para figuras
    os.makedirs("../output/figures", exist_ok=True)
    os.chdir("../output/figures")
    
    # Gerar plots para diferentes horários
    nc = Dataset(wrfout_file, 'r')
    ntimes = nc.dimensions['Time'].size
    nc.close()
    
    print(f"Gerando plots para {ntimes} horários...")
    
    for t in range(min(ntimes, 12)):  # Máximo 12 horários
        print(f"Processando horário {t+1}/{ntimes}")
        
        # Temperatura
        plot_wrf_variable(wrfout_file, 'T2', t)
        
        # Vento
        create_wind_plot(wrfout_file, t)
        
        # Precipitação (se disponível)
        try:
            plot_wrf_variable(wrfout_file, 'RAINC', t)
        except:
            pass
    
    print("Visualização concluída!")
    print("Figuras salvas em: ../output/figures/")

if __name__ == "__main__":
    main()