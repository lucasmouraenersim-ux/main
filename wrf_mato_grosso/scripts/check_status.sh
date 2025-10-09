#!/bin/bash

# Script para verificar o status da simulação WRF

echo "=========================================="
echo "  STATUS DA SIMULAÇÃO WRF - MATO GROSSO"
echo "=========================================="
echo ""

# Verificar se WRF/WPS estão instalados
echo "1. VERIFICANDO INSTALAÇÃO:"
if [ -d "/opt/WRF" ]; then
    echo "   ✓ WRF instalado em /opt/WRF"
    if [ -f "/opt/WRF/main/wrf.exe" ]; then
        echo "   ✓ wrf.exe encontrado"
    else
        echo "   ✗ wrf.exe não encontrado - compilação necessária"
    fi
else
    echo "   ✗ WRF não instalado"
fi

if [ -d "/opt/WPS" ]; then
    echo "   ✓ WPS instalado em /opt/WPS"
    if [ -f "/opt/WPS/geogrid.exe" ]; then
        echo "   ✓ Executáveis WPS encontrados"
    else
        echo "   ✗ Executáveis WPS não encontrados - compilação necessária"
    fi
else
    echo "   ✗ WPS não instalado"
fi

echo ""

# Verificar dados GFS
echo "2. VERIFICANDO DADOS GFS:"
data_dir="../data"
if [ -d "$data_dir" ]; then
    gfs_files=$(ls $data_dir/gfs.t12z.* 2>/dev/null | wc -l)
    if [ $gfs_files -gt 0 ]; then
        echo "   ✓ $gfs_files arquivos GFS encontrados"
        echo "   Arquivos:"
        ls -la $data_dir/gfs.t12z.* 2>/dev/null | awk '{print "     " $9 " (" $5 " bytes)"}'
    else
        echo "   ✗ Nenhum arquivo GFS encontrado"
        echo "   Execute: ./download_gfs.sh"
    fi
else
    echo "   ✗ Diretório de dados não existe"
fi

echo ""

# Verificar saída WPS
echo "3. VERIFICANDO SAÍDA WPS:"
wps_dir="../output/wps_output"
if [ -d "$wps_dir" ]; then
    met_files=$(ls $wps_dir/met_em.d01.* 2>/dev/null | wc -l)
    if [ $met_files -gt 0 ]; then
        echo "   ✓ $met_files arquivos met_em encontrados"
        echo "   Arquivos:"
        ls -la $wps_dir/met_em.d01.* 2>/dev/null | awk '{print "     " $9 " (" $5 " bytes)"}'
    else
        echo "   ✗ Nenhum arquivo met_em encontrado"
        echo "   Execute: ./run_wps.sh"
    fi
    
    if [ -f "$wps_dir/geo_em.d01.nc" ]; then
        echo "   ✓ Arquivo geo_em.d01.nc encontrado"
    else
        echo "   ✗ Arquivo geo_em.d01.nc não encontrado"
    fi
else
    echo "   ✗ Diretório WPS output não existe"
fi

echo ""

# Verificar saída WRF
echo "4. VERIFICANDO SAÍDA WRF:"
wrf_dir="../output/wrf_output"
if [ -d "$wrf_dir" ]; then
    wrfout_files=$(ls $wrf_dir/wrfout_d01_* 2>/dev/null | wc -l)
    if [ $wrfout_files -gt 0 ]; then
        echo "   ✓ $wrfout_files arquivos wrfout encontrados"
        echo "   Arquivos:"
        ls -la $wrf_dir/wrfout_d01_* 2>/dev/null | awk '{print "     " $9 " (" $5 " bytes)"}'
        
        # Verificar se simulação está completa
        expected_files=13  # 12 horas + inicial
        if [ $wrfout_files -eq $expected_files ]; then
            echo "   ✓ Simulação completa (12 horas)"
        else
            echo "   ⚠ Simulação incompleta ($wrfout_files/$expected_files arquivos)"
        fi
    else
        echo "   ✗ Nenhum arquivo wrfout encontrado"
        echo "   Execute: ./run_wrf.sh"
    fi
    
    # Verificar logs
    if [ -f "$wrf_dir/rsl.out.0000" ]; then
        echo "   ✓ Logs WRF encontrados"
        # Verificar se há erros
        errors=$(grep -i "error\|fail" $wrf_dir/rsl.* 2>/dev/null | wc -l)
        if [ $errors -gt 0 ]; then
            echo "   ⚠ $errors possíveis erros encontrados nos logs"
        fi
    fi
else
    echo "   ✗ Diretório WRF output não existe"
fi

echo ""

# Verificar figuras
echo "5. VERIFICANDO VISUALIZAÇÃO:"
fig_dir="../output/figures"
if [ -d "$fig_dir" ]; then
    png_files=$(ls $fig_dir/*.png 2>/dev/null | wc -l)
    if [ $png_files -gt 0 ]; then
        echo "   ✓ $png_files figuras geradas"
    else
        echo "   ✗ Nenhuma figura encontrada"
        echo "   Execute: python3 visualize_results.py"
    fi
else
    echo "   ✗ Diretório de figuras não existe"
fi

echo ""

# Verificar recursos do sistema
echo "6. RECURSOS DO SISTEMA:"
echo "   CPU: $(nproc) cores"
echo "   RAM: $(free -h | awk '/^Mem:/ {print $2}') total, $(free -h | awk '/^Mem:/ {print $7}') disponível"
echo "   Disco: $(df -h . | awk 'NR==2 {print $4}') livres"

echo ""

# Próximos passos
echo "7. PRÓXIMOS PASSOS:"
if [ ! -d "/opt/WRF" ]; then
    echo "   → Execute: ./install_wrf.sh"
elif [ $gfs_files -eq 0 ]; then
    echo "   → Execute: ./download_gfs.sh"
elif [ $met_files -eq 0 ]; then
    echo "   → Execute: ./run_wps.sh"
elif [ $wrfout_files -eq 0 ]; then
    echo "   → Execute: ./run_wrf.sh"
elif [ $png_files -eq 0 ]; then
    echo "   → Execute: python3 visualize_results.py"
else
    echo "   → Simulação completa! Verifique os resultados em ../output/"
fi

echo ""
echo "=========================================="