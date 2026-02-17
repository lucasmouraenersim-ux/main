#!/usr/bin/env python3
"""
Modelo Meteorológico Simplificado para Mato Grosso
Versão sem dependências de mapas geográficos
"""

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
import sys

class SimpleMatoGrossoModel:
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
        os.makedirs(f"{self.output_dir}/simple_output", exist_ok=True)
        os.makedirs(f"{self.output_dir}/figures", exist_ok=True)
    
    def create_weather_data(self, date_str="20210306", cycle="12"):
        """Criar dados meteorológicos realistas para Mato Grosso"""
        
        print("Gerando dados meteorológicos para Mato Grosso...")
        
        # Grade de coordenadas (resolução ~3km simulada)
        lats = np.linspace(self.domain['lat_min'], self.domain['lat_max'], 167)  # ~3km
        lons = np.linspace(self.domain['lon_min'], self.domain['lon_max'], 167)  # ~3km
        
        # Horários (15z até 00z = 9 horários)
        start_time = datetime.strptime(f"{date_str} {cycle}", "%Y%m%d %H")
        times = [start_time + timedelta(hours=h) for h in range(3, 12)]  # 15z até 23z
        
        # Dados meteorológicos
        weather_data = {
            'lats': lats,
            'lons': lons,
            'times': times,
            'temperature': np.zeros((len(times), len(lats), len(lons))),
            'u_wind': np.zeros((len(times), len(lats), len(lons))),
            'v_wind': np.zeros((len(times), len(lats), len(lons))),
            'pressure': np.zeros((len(times), len(lats), len(lons))),
            'precipitation': np.zeros((len(times), len(lats), len(lons)))
        }
        
        # Gerar dados realistas para março em MT
        np.random.seed(42)  # Para reprodutibilidade
        
        for i, time in enumerate(times):
            hour = time.hour
            
            print(f"  Processando horário {hour}:00 UTC...")
            
            # Temperatura (padrão diurno/noturno típico de março em MT)
            base_temp = 26 + 7 * np.sin((hour - 6) * np.pi / 12)  # Ciclo diário
            
            # Variação espacial
            for j, lat in enumerate(lats):
                for k, lon in enumerate(lons):
                    # Efeito da altitude (Chapada dos Guimarães é mais fria)
                    altitude_effect = -4 if abs(lat - self.chapada_lat) < 0.3 and abs(lon - self.chapada_lon) < 0.3 else 0
                    
                    # Gradiente latitudinal (mais quente ao norte)
                    lat_effect = (lat - self.domain['lat_min']) * 1.5
                    
                    # Efeito de continentalidade
                    continental_effect = abs(lon - self.domain['lon_min']) * 0.5
                    
                    # Ruído meteorológico
                    noise = np.random.normal(0, 1.5)
                    
                    weather_data['temperature'][i, j, k] = base_temp + lat_effect + altitude_effect + continental_effect + noise
            
            # Vento (padrões típicos de MT - brisa, convergência)
            # Vento de leste predominante com variações diárias
            base_u = -3 + 4 * np.sin((hour - 12) * np.pi / 12)  # Componente zonal
            base_v = 1 + 2 * np.cos((hour - 15) * np.pi / 12)   # Componente meridional
            
            for j in range(len(lats)):
                for k in range(len(lons)):
                    # Efeito topográfico na Chapada
                    topo_u = 2 if abs(lats[j] - self.chapada_lat) < 0.2 and abs(lons[k] - self.chapada_lon) < 0.2 else 0
                    topo_v = 1 if abs(lats[j] - self.chapada_lat) < 0.2 and abs(lons[k] - self.chapada_lon) < 0.2 else 0
                    
                    weather_data['u_wind'][i, j, k] = base_u + topo_u + np.random.normal(0, 1)
                    weather_data['v_wind'][i, j, k] = base_v + topo_v + np.random.normal(0, 1)
            
            # Pressão (padrão típico com variação diária)
            base_pressure = 1012 + 2 * np.sin((hour - 14) * np.pi / 12)
            weather_data['pressure'][i, :, :] = base_pressure + np.random.normal(0, 2, (len(lats), len(lons)))
            
            # Precipitação (mais provável à tarde/noite - padrão amazônico)
            if hour >= 15:  # Após 15z (12h local)
                precip_prob = (hour - 15) / 8  # Aumenta até a noite
                for j in range(len(lats)):
                    for k in range(len(lons)):
                        # Mais chuva na Chapada (efeito orográfico)
                        orographic_factor = 2 if abs(lats[j] - self.chapada_lat) < 0.3 else 1
                        
                        if np.random.random() < precip_prob * 0.3:  # 30% de chance máxima
                            weather_data['precipitation'][i, j, k] = np.random.exponential(3) * orographic_factor
                        else:
                            weather_data['precipitation'][i, j, k] = 0
            else:
                weather_data['precipitation'][i, :, :] = 0
        
        return weather_data
    
    def analyze_data(self, weather_data):
        """Analisar dados meteorológicos"""
        
        print("\nAnalisando dados meteorológicos...")
        
        # Encontrar índices da Chapada dos Guimarães
        lat_idx = np.argmin(np.abs(weather_data['lats'] - self.chapada_lat))
        lon_idx = np.argmin(np.abs(weather_data['lons'] - self.chapada_lon))
        
        # Extrair dados para Chapada
        chapada_temp = weather_data['temperature'][:, lat_idx, lon_idx]
        chapada_u = weather_data['u_wind'][:, lat_idx, lon_idx]
        chapada_v = weather_data['v_wind'][:, lat_idx, lon_idx]
        chapada_pressure = weather_data['pressure'][:, lat_idx, lon_idx]
        chapada_precip = weather_data['precipitation'][:, lat_idx, lon_idx]
        
        # Calcular estatísticas
        wind_speed = np.sqrt(chapada_u**2 + chapada_v**2)
        
        print(f"\n=== PREVISÃO PARA CHAPADA DOS GUIMARÃES ===")
        print(f"Coordenadas: {self.chapada_lat:.2f}°S, {abs(self.chapada_lon):.2f}°W")
        print(f"Temperatura: {chapada_temp.min():.1f}°C a {chapada_temp.max():.1f}°C")
        print(f"Vento: {wind_speed.min():.1f} a {wind_speed.max():.1f} m/s")
        print(f"Pressão: {chapada_pressure.min():.1f} a {chapada_pressure.max():.1f} hPa")
        print(f"Precipitação total: {chapada_precip.sum():.1f} mm")
        
        # Horário de temperatura máxima e mínima
        max_temp_idx = np.argmax(chapada_temp)
        min_temp_idx = np.argmin(chapada_temp)
        
        max_temp_time = weather_data['times'][max_temp_idx]
        min_temp_time = weather_data['times'][min_temp_idx]
        
        print(f"Temp. máxima: {chapada_temp[max_temp_idx]:.1f}°C às {max_temp_time.strftime('%H:%M')} UTC")
        print(f"Temp. mínima: {chapada_temp[min_temp_idx]:.1f}°C às {min_temp_time.strftime('%H:%M')} UTC")
        
        return {
            'chapada_temp': chapada_temp,
            'chapada_wind_speed': wind_speed,
            'chapada_pressure': chapada_pressure,
            'chapada_precip': chapada_precip,
            'lat_idx': lat_idx,
            'lon_idx': lon_idx
        }
    
    def create_plots(self, weather_data, analysis):
        """Criar gráficos meteorológicos"""
        
        print("\nGerando gráficos...")
        
        # Configurar matplotlib
        plt.style.use('default')
        
        # 1. Série temporal para Chapada dos Guimarães
        self.plot_time_series(weather_data, analysis)
        
        # 2. Mapas de temperatura para alguns horários
        self.plot_temperature_maps(weather_data)
        
        # 3. Mapa de precipitação acumulada
        self.plot_precipitation_map(weather_data)
        
        # 4. Perfil de vento
        self.plot_wind_profile(weather_data, analysis)
        
        print(f"Gráficos salvos em: {self.output_dir}/figures/")
    
    def plot_time_series(self, weather_data, analysis):
        """Plot de série temporal para Chapada dos Guimarães"""
        
        times = weather_data['times']
        time_labels = [t.strftime('%H:%M') for t in times]
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Previsão Meteorológica - Chapada dos Guimarães\n06 de Março de 2021', fontsize=16, fontweight='bold')
        
        # Temperatura
        axes[0, 0].plot(time_labels, analysis['chapada_temp'], 'r-o', linewidth=2, markersize=6)
        axes[0, 0].set_title('Temperatura', fontweight='bold')
        axes[0, 0].set_ylabel('°C')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Vento
        axes[0, 1].plot(time_labels, analysis['chapada_wind_speed'], 'b-o', linewidth=2, markersize=6)
        axes[0, 1].set_title('Velocidade do Vento', fontweight='bold')
        axes[0, 1].set_ylabel('m/s')
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Pressão
        axes[1, 0].plot(time_labels, analysis['chapada_pressure'], 'g-o', linewidth=2, markersize=6)
        axes[1, 0].set_title('Pressão Atmosférica', fontweight='bold')
        axes[1, 0].set_ylabel('hPa')
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Precipitação
        bars = axes[1, 1].bar(time_labels, analysis['chapada_precip'], color='skyblue', edgecolor='navy', alpha=0.7)
        axes[1, 1].set_title('Precipitação', fontweight='bold')
        axes[1, 1].set_ylabel('mm')
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        # Adicionar valores nas barras de precipitação
        for bar, precip in zip(bars, analysis['chapada_precip']):
            if precip > 0.1:
                axes[1, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                               f'{precip:.1f}', ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        
        filename = f"{self.output_dir}/figures/serie_temporal_chapada.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Série temporal salva: {filename}")
    
    def plot_temperature_maps(self, weather_data):
        """Plot de mapas de temperatura para horários selecionados"""
        
        # Selecionar horários: 15z, 18z, 21z
        selected_hours = [0, 3, 6]  # Índices correspondentes
        
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle('Temperatura a 2m - Mato Grosso (Resolução 3km)', fontsize=16, fontweight='bold')
        
        for i, hour_idx in enumerate(selected_hours):
            time = weather_data['times'][hour_idx]
            temp_data = weather_data['temperature'][hour_idx, :, :]
            
            # Plot
            im = axes[i].imshow(temp_data, cmap='RdYlBu_r', aspect='auto',
                              extent=[self.domain['lon_min'], self.domain['lon_max'],
                                     self.domain['lat_min'], self.domain['lat_max']],
                              vmin=15, vmax=35)
            
            # Marcar Chapada dos Guimarães
            axes[i].plot(self.chapada_lon, self.chapada_lat, 'ko', markersize=8, markerfacecolor='white', markeredgewidth=2)
            axes[i].text(self.chapada_lon, self.chapada_lat - 0.3, 'Chapada dos\nGuimarães', 
                        ha='center', va='top', fontweight='bold', fontsize=10,
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
            
            axes[i].set_title(f'{time.strftime("%H:%M")} UTC\n({time.strftime("%H:%M")} local - 3h)', fontweight='bold')
            axes[i].set_xlabel('Longitude')
            if i == 0:
                axes[i].set_ylabel('Latitude')
            
            # Grid
            axes[i].grid(True, alpha=0.3)
            
            # Colorbar
            cbar = plt.colorbar(im, ax=axes[i])
            cbar.set_label('°C')
        
        plt.tight_layout()
        
        filename = f"{self.output_dir}/figures/mapas_temperatura.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Mapas de temperatura salvos: {filename}")
    
    def plot_precipitation_map(self, weather_data):
        """Plot de precipitação acumulada"""
        
        # Calcular precipitação total
        total_precip = np.sum(weather_data['precipitation'], axis=0)
        
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))
        
        # Plot apenas onde há precipitação significativa
        precip_masked = np.where(total_precip > 0.1, total_precip, np.nan)
        
        im = ax.imshow(precip_masked, cmap='Blues', aspect='auto',
                      extent=[self.domain['lon_min'], self.domain['lon_max'],
                             self.domain['lat_min'], self.domain['lat_max']],
                      vmin=0, vmax=20)
        
        # Marcar Chapada dos Guimarães
        ax.plot(self.chapada_lon, self.chapada_lat, 'ro', markersize=10, markerfacecolor='red', markeredgewidth=2)
        ax.text(self.chapada_lon, self.chapada_lat - 0.3, 'Chapada dos Guimarães', 
                ha='center', va='top', fontweight='bold', fontsize=12,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
        
        ax.set_title('Precipitação Acumulada (15z - 23z)\n06 de Março de 2021', fontsize=14, fontweight='bold')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.grid(True, alpha=0.3)
        
        # Colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('mm')
        
        plt.tight_layout()
        
        filename = f"{self.output_dir}/figures/precipitacao_acumulada.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Mapa de precipitação salvo: {filename}")
    
    def plot_wind_profile(self, weather_data, analysis):
        """Plot de perfil de vento"""
        
        times = weather_data['times']
        time_labels = [t.strftime('%H:%M') for t in times]
        
        lat_idx = analysis['lat_idx']
        lon_idx = analysis['lon_idx']
        
        u_wind = weather_data['u_wind'][:, lat_idx, lon_idx]
        v_wind = weather_data['v_wind'][:, lat_idx, lon_idx]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        fig.suptitle('Perfil de Vento - Chapada dos Guimarães', fontsize=14, fontweight='bold')
        
        # Componentes do vento
        ax1.plot(time_labels, u_wind, 'b-o', label='Componente U (Zonal)', linewidth=2)
        ax1.plot(time_labels, v_wind, 'r-o', label='Componente V (Meridional)', linewidth=2)
        ax1.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        ax1.set_ylabel('m/s')
        ax1.set_title('Componentes do Vento')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # Rosa dos ventos simplificada
        wind_speed = analysis['chapada_wind_speed']
        wind_dir = np.arctan2(v_wind, u_wind) * 180 / np.pi
        
        ax2.plot(time_labels, wind_speed, 'g-o', linewidth=2, markersize=6)
        ax2.set_ylabel('Velocidade (m/s)')
        ax2.set_xlabel('Horário (UTC)')
        ax2.set_title('Velocidade do Vento')
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        
        # Adicionar direção como texto
        for i, (speed, direction) in enumerate(zip(wind_speed, wind_dir)):
            if i % 2 == 0:  # Mostrar apenas alguns para não poluir
                ax2.annotate(f'{direction:.0f}°', 
                           (time_labels[i], speed), 
                           textcoords="offset points", 
                           xytext=(0,10), 
                           ha='center', fontsize=8)
        
        plt.tight_layout()
        
        filename = f"{self.output_dir}/figures/perfil_vento.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Perfil de vento salvo: {filename}")
    
    def save_data_summary(self, weather_data, analysis):
        """Salvar resumo dos dados"""
        
        summary_file = f"{self.output_dir}/simple_output/resumo_simulacao.txt"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("  SIMULAÇÃO METEOROLÓGICA - MATO GROSSO\n")
            f.write("="*60 + "\n")
            f.write("Data: 06 de Março de 2021\n")
            f.write("Ciclo: 12z\n")
            f.write("Período: 15z - 23z (9 horas)\n")
            f.write("Resolução: ~3km (167x167 pontos)\n")
            f.write("Foco: Chapada dos Guimarães, MT\n")
            f.write("="*60 + "\n\n")
            
            f.write("PREVISÃO PARA CHAPADA DOS GUIMARÃES:\n")
            f.write("-"*40 + "\n")
            f.write(f"Coordenadas: {self.chapada_lat:.2f}°S, {abs(self.chapada_lon):.2f}°W\n")
            f.write(f"Temperatura: {analysis['chapada_temp'].min():.1f}°C a {analysis['chapada_temp'].max():.1f}°C\n")
            f.write(f"Vento: {analysis['chapada_wind_speed'].min():.1f} a {analysis['chapada_wind_speed'].max():.1f} m/s\n")
            f.write(f"Pressão: {analysis['chapada_pressure'].min():.1f} a {analysis['chapada_pressure'].max():.1f} hPa\n")
            f.write(f"Precipitação total: {analysis['chapada_precip'].sum():.1f} mm\n\n")
            
            f.write("HORÁRIO DETALHADO:\n")
            f.write("-"*40 + "\n")
            f.write("Hora(UTC) | Temp(°C) | Vento(m/s) | Press(hPa) | Precip(mm)\n")
            f.write("-"*60 + "\n")
            
            for i, time in enumerate(weather_data['times']):
                f.write(f"{time.strftime('%H:%M')}     | "
                       f"{analysis['chapada_temp'][i]:6.1f}   | "
                       f"{analysis['chapada_wind_speed'][i]:8.1f}   | "
                       f"{analysis['chapada_pressure'][i]:8.1f}   | "
                       f"{analysis['chapada_precip'][i]:8.1f}\n")
            
            f.write("\n" + "="*60 + "\n")
            f.write("Simulação gerada pelo Modelo Python - Mato Grosso\n")
            f.write("Dados sintéticos baseados em padrões climatológicos\n")
            f.write("="*60 + "\n")
        
        print(f"  ✓ Resumo salvo: {summary_file}")
    
    def run_simulation(self, date_str="20210306", cycle="12"):
        """Executar simulação completa"""
        
        print("="*60)
        print("  MODELO METEOROLÓGICO PYTHON - MATO GROSSO")
        print("="*60)
        print(f"Data: 06 de Março de 2021")
        print(f"Ciclo: {cycle}z")
        print(f"Período: 15z - 23z (9 horas)")
        print(f"Resolução: ~3km")
        print(f"Região: Mato Grosso (foco em Chapada dos Guimarães)")
        print("="*60)
        
        # 1. Gerar dados meteorológicos
        weather_data = self.create_weather_data(date_str, cycle)
        
        # 2. Analisar dados
        analysis = self.analyze_data(weather_data)
        
        # 3. Criar visualizações
        self.create_plots(weather_data, analysis)
        
        # 4. Salvar resumo
        self.save_data_summary(weather_data, analysis)
        
        print("\n" + "="*60)
        print("  SIMULAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        print(f"Dados: {self.data_dir}/")
        print(f"Gráficos: {self.output_dir}/figures/")
        print(f"Resumo: {self.output_dir}/simple_output/")
        print("="*60)
        
        return weather_data, analysis

def main():
    """Função principal"""
    
    model = SimpleMatoGrossoModel()
    
    # Executar simulação para 06/03/2021 12z
    weather_data, analysis = model.run_simulation("20210306", "12")
    
    return weather_data, analysis

if __name__ == "__main__":
    main()