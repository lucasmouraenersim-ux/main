#!/usr/bin/env python3
"""
Modelo Meteorológico Python para Mato Grosso
Alternativa ao WRF usando dados GFS e processamento Python
"""

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from datetime import datetime, timedelta
import os
import sys
import requests
import warnings
warnings.filterwarnings('ignore')

class MatoGrossoWeatherModel:
    def __init__(self):
        self.domain = {
            'lat_min': -18.0,
            'lat_max': -13.0, 
            'lon_min': -58.0,
            'lon_max': -53.0
        }
        
        # Chapada dos Guimarães
        self.chapada_lat = -15.46
        self.chapada_lon = -55.75
        
        self.data_dir = "../data"
        self.output_dir = "../output"
        
        # Criar diretórios
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/gfs_output", exist_ok=True)
        os.makedirs(f"{self.output_dir}/figures", exist_ok=True)
    
    def download_gfs_data(self, date_str="20210306", cycle="12"):
        """Download dados GFS do NOMADS"""
        
        print(f"Baixando dados GFS para {date_str} ciclo {cycle}z...")
        
        # URLs para dados GFS
        base_url = f"https://nomads.ncep.noaa.gov/dods/gfs_0p25/gfs{date_str}/gfs_0p25_{cycle}z"
        
        # Tentar diferentes fontes
        urls = [
            base_url,
            f"https://nomads.ncep.noaa.gov/dods/gfs_0p25_1hr/gfs{date_str}/gfs_0p25_1hr_{cycle}z"
        ]
        
        for url in urls:
            try:
                print(f"Tentando: {url}")
                
                # Abrir dataset
                ds = xr.open_dataset(url)
                
                # Selecionar região de Mato Grosso
                ds_region = ds.sel(
                    lat=slice(self.domain['lat_max'], self.domain['lat_min']),
                    lon=slice(self.domain['lon_min'], self.domain['lon_max']),
                    time=slice(f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}T15:00:00",
                              f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}T23:59:59")
                )
                
                # Salvar dados
                output_file = f"{self.data_dir}/gfs_{date_str}_{cycle}z_mato_grosso.nc"
                ds_region.to_netcdf(output_file)
                print(f"Dados salvos em: {output_file}")
                
                return ds_region
                
            except Exception as e:
                print(f"Erro com {url}: {e}")
                continue
        
        # Se não conseguir baixar, criar dados sintéticos para demonstração
        print("Criando dados sintéticos para demonstração...")
        return self.create_synthetic_data(date_str, cycle)
    
    def create_synthetic_data(self, date_str="20210306", cycle="12"):
        """Criar dados sintéticos realistas para Mato Grosso"""
        
        print("Gerando dados meteorológicos sintéticos...")
        
        # Grade de coordenadas
        lats = np.linspace(self.domain['lat_min'], self.domain['lat_max'], 50)
        lons = np.linspace(self.domain['lon_min'], self.domain['lon_max'], 50)
        
        # Horários (15z até 00z = 9 horários)
        start_time = datetime.strptime(f"{date_str} {cycle}", "%Y%m%d %H")
        times = [start_time + timedelta(hours=h) for h in range(3, 12)]  # 15z até 23z
        
        # Criar dataset
        ds = xr.Dataset()
        
        # Coordenadas
        ds = ds.assign_coords({
            'lat': lats,
            'lon': lons, 
            'time': times
        })
        
        # Gerar dados realistas para março em MT
        np.random.seed(42)  # Para reprodutibilidade
        
        for i, time in enumerate(times):
            hour = time.hour
            
            # Temperatura (padrão diurno/noturno)
            base_temp = 25 + 8 * np.sin((hour - 6) * np.pi / 12)  # Ciclo diário
            
            # Variação espacial (mais quente no norte, mais frio na chapada)
            temp_2d = np.zeros((len(lats), len(lons)))
            for j, lat in enumerate(lats):
                for k, lon in enumerate(lons):
                    # Efeito da altitude (Chapada dos Guimarães é mais fria)
                    altitude_effect = -5 if abs(lat - self.chapada_lat) < 0.5 and abs(lon - self.chapada_lon) < 0.5 else 0
                    # Gradiente latitudinal
                    lat_effect = (lat - self.domain['lat_min']) * 2
                    # Ruído
                    noise = np.random.normal(0, 2)
                    
                    temp_2d[j, k] = base_temp + lat_effect + altitude_effect + noise
            
            # Adicionar ao dataset
            if i == 0:
                ds['tmp2m'] = (['time', 'lat', 'lon'], np.zeros((len(times), len(lats), len(lons))))
                ds['ugrd10m'] = (['time', 'lat', 'lon'], np.zeros((len(times), len(lats), len(lons))))
                ds['vgrd10m'] = (['time', 'lat', 'lon'], np.zeros((len(times), len(lats), len(lons))))
                ds['prmslmsl'] = (['time', 'lat', 'lon'], np.zeros((len(times), len(lats), len(lons))))
                ds['apcpsfc'] = (['time', 'lat', 'lon'], np.zeros((len(times), len(lats), len(lons))))
            
            ds['tmp2m'][i, :, :] = temp_2d + 273.15  # Converter para Kelvin
            
            # Vento (padrão de brisa e convergência)
            u_wind = 5 * np.sin(hour * np.pi / 12) + np.random.normal(0, 2, (len(lats), len(lons)))
            v_wind = 3 * np.cos(hour * np.pi / 12) + np.random.normal(0, 2, (len(lats), len(lons)))
            
            ds['ugrd10m'][i, :, :] = u_wind
            ds['vgrd10m'][i, :, :] = v_wind
            
            # Pressão
            pressure = 1013.25 + np.random.normal(0, 5, (len(lats), len(lons)))
            ds['prmslmsl'][i, :, :] = pressure * 100  # Pa
            
            # Precipitação (mais provável à tarde/noite)
            precip_prob = max(0, (hour - 15) / 8) if hour >= 15 else 0
            precip = np.random.exponential(2, (len(lats), len(lons))) * precip_prob
            precip[precip < 0.1] = 0  # Threshold mínimo
            ds['apcpsfc'][i, :, :] = precip
        
        # Adicionar atributos
        ds.attrs['title'] = 'Dados Meteorológicos Sintéticos - Mato Grosso'
        ds.attrs['source'] = 'Modelo Python - Chapada dos Guimarães'
        ds.attrs['date'] = date_str
        ds.attrs['cycle'] = f"{cycle}z"
        
        # Salvar
        output_file = f"{self.data_dir}/synthetic_{date_str}_{cycle}z_mato_grosso.nc"
        ds.to_netcdf(output_file)
        print(f"Dados sintéticos salvos em: {output_file}")
        
        return ds
    
    def process_data(self, ds):
        """Processar e analisar dados meteorológicos"""
        
        print("Processando dados meteorológicos...")
        
        # Calcular variáveis derivadas
        if 'tmp2m' in ds.variables:
            # Temperatura em Celsius
            ds['temp_celsius'] = ds['tmp2m'] - 273.15
        
        if 'ugrd10m' in ds.variables and 'vgrd10m' in ds.variables:
            # Velocidade do vento
            ds['wind_speed'] = np.sqrt(ds['ugrd10m']**2 + ds['vgrd10m']**2)
            # Direção do vento
            ds['wind_dir'] = np.arctan2(ds['vgrd10m'], ds['ugrd10m']) * 180 / np.pi
        
        # Estatísticas para Chapada dos Guimarães
        chapada_data = ds.sel(
            lat=self.chapada_lat, 
            lon=self.chapada_lon, 
            method='nearest'
        )
        
        print(f"\n=== PREVISÃO PARA CHAPADA DOS GUIMARÃES ===")
        if 'temp_celsius' in chapada_data.variables:
            temp_min = float(chapada_data['temp_celsius'].min())
            temp_max = float(chapada_data['temp_celsius'].max())
            print(f"Temperatura: {temp_min:.1f}°C a {temp_max:.1f}°C")
        
        if 'wind_speed' in chapada_data.variables:
            wind_max = float(chapada_data['wind_speed'].max())
            print(f"Vento máximo: {wind_max:.1f} m/s")
        
        if 'apcpsfc' in chapada_data.variables:
            precip_total = float(chapada_data['apcpsfc'].sum())
            print(f"Precipitação total: {precip_total:.1f} mm")
        
        return ds
    
    def create_plots(self, ds):
        """Criar gráficos meteorológicos"""
        
        print("Gerando gráficos...")
        
        # Configurar matplotlib para não usar display
        plt.switch_backend('Agg')
        
        times = ds.time.values
        
        for i, time in enumerate(times):
            time_str = str(time)[:16].replace('T', ' ')
            
            # Plot 1: Temperatura
            if 'temp_celsius' in ds.variables:
                self.plot_temperature(ds, i, time_str)
            
            # Plot 2: Vento
            if 'wind_speed' in ds.variables:
                self.plot_wind(ds, i, time_str)
            
            # Plot 3: Precipitação
            if 'apcpsfc' in ds.variables:
                self.plot_precipitation(ds, i, time_str)
        
        # Plot de série temporal para Chapada
        self.plot_time_series(ds)
        
        print(f"Gráficos salvos em: {self.output_dir}/figures/")
    
    def plot_temperature(self, ds, time_idx, time_str):
        """Plot de temperatura"""
        
        fig = plt.figure(figsize=(12, 8))
        ax = plt.axes(projection=ccrs.PlateCarree())
        
        # Dados
        temp = ds['temp_celsius'][time_idx, :, :]
        lats = ds.lat.values
        lons = ds.lon.values
        
        # Plot
        levels = np.arange(15, 40, 2)
        cs = ax.contourf(lons, lats, temp, levels=levels, cmap='RdYlBu_r', 
                        transform=ccrs.PlateCarree(), extend='both')
        
        # Características geográficas
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS)
        ax.add_feature(cfeature.STATES, alpha=0.5)
        
        # Marcar Chapada dos Guimarães
        ax.plot(self.chapada_lon, self.chapada_lat, 'ro', markersize=8, 
                transform=ccrs.PlateCarree())
        ax.text(self.chapada_lon, self.chapada_lat + 0.1, 'Chapada dos Guimarães', 
                transform=ccrs.PlateCarree(), ha='center', fontweight='bold')
        
        # Configurações
        ax.set_extent([self.domain['lon_min'], self.domain['lon_max'],
                      self.domain['lat_min'], self.domain['lat_max']], 
                     ccrs.PlateCarree())
        
        gl = ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
        gl.top_labels = False
        gl.right_labels = False
        
        # Colorbar
        cbar = plt.colorbar(cs, ax=ax, orientation='horizontal', pad=0.05, shrink=0.8)
        cbar.set_label('Temperatura (°C)')
        
        plt.title(f'Temperatura a 2m - {time_str}\nMato Grosso - Resolução ~25km')
        plt.tight_layout()
        
        filename = f"{self.output_dir}/figures/temperatura_{time_idx:02d}.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
    
    def plot_wind(self, ds, time_idx, time_str):
        """Plot de vento"""
        
        fig = plt.figure(figsize=(12, 8))
        ax = plt.axes(projection=ccrs.PlateCarree())
        
        # Dados
        wind_speed = ds['wind_speed'][time_idx, :, :]
        u_wind = ds['ugrd10m'][time_idx, :, :]
        v_wind = ds['vgrd10m'][time_idx, :, :]
        lats = ds.lat.values
        lons = ds.lon.values
        
        # Plot velocidade
        levels = np.arange(0, 20, 1)
        cs = ax.contourf(lons, lats, wind_speed, levels=levels, cmap='viridis',
                        transform=ccrs.PlateCarree(), extend='max')
        
        # Vetores de vento (subsample)
        skip = 3
        ax.quiver(lons[::skip], lats[::skip], 
                 u_wind[::skip, ::skip], v_wind[::skip, ::skip],
                 transform=ccrs.PlateCarree(), scale=200, alpha=0.7)
        
        # Características geográficas
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS)
        ax.add_feature(cfeature.STATES, alpha=0.5)
        
        # Marcar Chapada dos Guimarães
        ax.plot(self.chapada_lon, self.chapada_lat, 'ro', markersize=8,
                transform=ccrs.PlateCarree())
        ax.text(self.chapada_lon, self.chapada_lat + 0.1, 'Chapada dos Guimarães',
                transform=ccrs.PlateCarree(), ha='center', fontweight='bold')
        
        # Configurações
        ax.set_extent([self.domain['lon_min'], self.domain['lon_max'],
                      self.domain['lat_min'], self.domain['lat_max']],
                     ccrs.PlateCarree())
        
        gl = ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
        gl.top_labels = False
        gl.right_labels = False
        
        # Colorbar
        cbar = plt.colorbar(cs, ax=ax, orientation='horizontal', pad=0.05, shrink=0.8)
        cbar.set_label('Velocidade do Vento (m/s)')
        
        plt.title(f'Vento a 10m - {time_str}\nMato Grosso')
        plt.tight_layout()
        
        filename = f"{self.output_dir}/figures/vento_{time_idx:02d}.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
    
    def plot_precipitation(self, ds, time_idx, time_str):
        """Plot de precipitação"""
        
        fig = plt.figure(figsize=(12, 8))
        ax = plt.axes(projection=ccrs.PlateCarree())
        
        # Dados
        precip = ds['apcpsfc'][time_idx, :, :]
        lats = ds.lat.values
        lons = ds.lon.values
        
        # Plot apenas onde há precipitação
        precip_masked = precip.where(precip > 0.1)
        
        levels = [0.1, 0.5, 1, 2, 5, 10, 20, 50]
        cs = ax.contourf(lons, lats, precip_masked, levels=levels, cmap='Blues',
                        transform=ccrs.PlateCarree(), extend='max')
        
        # Características geográficas
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS)
        ax.add_feature(cfeature.STATES, alpha=0.5)
        
        # Marcar Chapada dos Guimarães
        ax.plot(self.chapada_lon, self.chapada_lat, 'ro', markersize=8,
                transform=ccrs.PlateCarree())
        ax.text(self.chapada_lon, self.chapada_lat + 0.1, 'Chapada dos Guimarães',
                transform=ccrs.PlateCarree(), ha='center', fontweight='bold')
        
        # Configurações
        ax.set_extent([self.domain['lon_min'], self.domain['lon_max'],
                      self.domain['lat_min'], self.domain['lat_max']],
                     ccrs.PlateCarree())
        
        gl = ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
        gl.top_labels = False
        gl.right_labels = False
        
        # Colorbar
        if len(cs.collections) > 0:
            cbar = plt.colorbar(cs, ax=ax, orientation='horizontal', pad=0.05, shrink=0.8)
            cbar.set_label('Precipitação (mm)')
        
        plt.title(f'Precipitação - {time_str}\nMato Grosso')
        plt.tight_layout()
        
        filename = f"{self.output_dir}/figures/precipitacao_{time_idx:02d}.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
    
    def plot_time_series(self, ds):
        """Plot de série temporal para Chapada dos Guimarães"""
        
        # Dados para Chapada dos Guimarães
        chapada_data = ds.sel(
            lat=self.chapada_lat,
            lon=self.chapada_lon,
            method='nearest'
        )
        
        times = ds.time.values
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Previsão Meteorológica - Chapada dos Guimarães\n06/03/2021', fontsize=16)
        
        # Temperatura
        if 'temp_celsius' in chapada_data.variables:
            axes[0, 0].plot(times, chapada_data['temp_celsius'], 'r-o', linewidth=2)
            axes[0, 0].set_title('Temperatura')
            axes[0, 0].set_ylabel('°C')
            axes[0, 0].grid(True, alpha=0.3)
        
        # Vento
        if 'wind_speed' in chapada_data.variables:
            axes[0, 1].plot(times, chapada_data['wind_speed'], 'b-o', linewidth=2)
            axes[0, 1].set_title('Velocidade do Vento')
            axes[0, 1].set_ylabel('m/s')
            axes[0, 1].grid(True, alpha=0.3)
        
        # Pressão
        if 'prmslmsl' in chapada_data.variables:
            pressure_hpa = chapada_data['prmslmsl'] / 100
            axes[1, 0].plot(times, pressure_hpa, 'g-o', linewidth=2)
            axes[1, 0].set_title('Pressão')
            axes[1, 0].set_ylabel('hPa')
            axes[1, 0].grid(True, alpha=0.3)
        
        # Precipitação
        if 'apcpsfc' in chapada_data.variables:
            axes[1, 1].bar(range(len(times)), chapada_data['apcpsfc'], color='skyblue')
            axes[1, 1].set_title('Precipitação')
            axes[1, 1].set_ylabel('mm')
            axes[1, 1].set_xticks(range(len(times)))
            axes[1, 1].set_xticklabels([str(t)[:13] for t in times], rotation=45)
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        filename = f"{self.output_dir}/figures/serie_temporal_chapada.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"Série temporal salva: {filename}")
    
    def run_simulation(self, date_str="20210306", cycle="12"):
        """Executar simulação completa"""
        
        print("="*50)
        print("  MODELO METEOROLÓGICO PYTHON - MATO GROSSO")
        print("="*50)
        print(f"Data: {date_str}")
        print(f"Ciclo: {cycle}z")
        print(f"Região: Mato Grosso (Chapada dos Guimarães)")
        print("="*50)
        
        # 1. Download/criação de dados
        ds = self.download_gfs_data(date_str, cycle)
        
        # 2. Processamento
        ds = self.process_data(ds)
        
        # 3. Visualização
        self.create_plots(ds)
        
        print("\n" + "="*50)
        print("  SIMULAÇÃO CONCLUÍDA!")
        print("="*50)
        print(f"Dados: {self.data_dir}/")
        print(f"Gráficos: {self.output_dir}/figures/")
        print("="*50)
        
        return ds

def main():
    """Função principal"""
    
    model = MatoGrossoWeatherModel()
    
    # Executar simulação para 06/03/2021 12z
    ds = model.run_simulation("20210306", "12")
    
    return ds

if __name__ == "__main__":
    main()