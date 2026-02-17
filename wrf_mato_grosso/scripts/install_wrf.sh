#!/bin/bash

# Script de instalação do WRF e WPS no Ubuntu/Debian
# Para VM do Google Cloud

echo "=========================================="
echo "  INSTALAÇÃO WRF/WPS - UBUNTU"
echo "=========================================="

# Atualizar sistema
echo "Atualizando sistema..."
sudo apt-get update

# Instalar dependências básicas
echo "Instalando dependências básicas..."
sudo apt-get install -y \
    build-essential \
    gfortran \
    gcc \
    g++ \
    libtool \
    automake \
    autoconf \
    make \
    m4 \
    wget \
    curl \
    git \
    vim \
    csh \
    tcsh \
    ksh \
    python3 \
    python3-pip

# Instalar bibliotecas científicas
echo "Instalando bibliotecas científicas..."
sudo apt-get install -y \
    libnetcdf-dev \
    libnetcdff-dev \
    netcdf-bin \
    libhdf5-dev \
    libpng-dev \
    libjpeg-dev \
    zlib1g-dev \
    libcurl4-openssl-dev

# Instalar MPI
echo "Instalando OpenMPI..."
sudo apt-get install -y openmpi-bin openmpi-common libopenmpi-dev

# Criar diretórios
sudo mkdir -p /opt/{WRF,WPS,WPS_GEOG}
sudo chown -R $USER:$USER /opt/{WRF,WPS,WPS_GEOG}

# Definir variáveis de ambiente
export DIR=/opt
export CC=gcc
export CXX=g++
export FC=gfortran
export FCFLAGS=-m64
export F77=gfortran
export FFLAGS=-m64
export NETCDF=/usr
export LDFLAGS=-L/usr/lib/x86_64-linux-gnu
export CPPFLAGS=-I/usr/include

# Salvar variáveis no bashrc
echo "# WRF Environment" >> ~/.bashrc
echo "export DIR=/opt" >> ~/.bashrc
echo "export CC=gcc" >> ~/.bashrc
echo "export CXX=g++" >> ~/.bashrc
echo "export FC=gfortran" >> ~/.bashrc
echo "export FCFLAGS=-m64" >> ~/.bashrc
echo "export F77=gfortran" >> ~/.bashrc
echo "export FFLAGS=-m64" >> ~/.bashrc
echo "export NETCDF=/usr" >> ~/.bashrc
echo "export LDFLAGS=-L/usr/lib/x86_64-linux-gnu" >> ~/.bashrc
echo "export CPPFLAGS=-I/usr/include" >> ~/.bashrc

# Baixar e compilar WRF
echo "Baixando WRF..."
cd /opt
wget -c https://github.com/wrf-model/WRF/releases/download/v4.4.2/v4.4.2.tar.gz
tar -xzf v4.4.2.tar.gz
mv WRFV4.4.2 WRF
cd WRF

echo "Configurando WRF..."
echo "Escolha a opção 34 (GNU gfortran/gcc dmpar) quando solicitado"
./configure

echo "Compilando WRF (isso pode demorar bastante)..."
./compile em_real >& compile.log &

# Baixar e compilar WPS
echo "Baixando WPS..."
cd /opt
wget -c https://github.com/wrf-model/WPS/releases/download/v4.4/v4.4.tar.gz
tar -xzf v4.4.tar.gz
mv WPS-4.4 WPS
cd WPS

echo "Configurando WPS..."
echo "Escolha a opção 1 (GNU gfortran/gcc serial) quando solicitado"
./configure

echo "Compilando WPS..."
./compile >& compile.log

# Baixar dados geográficos (versão mínima)
echo "Baixando dados geográficos..."
cd /opt/WPS_GEOG
wget -c https://www2.mmm.ucar.edu/wrf/src/wps_files/geog_minimum.tar.bz2
tar -xjf geog_minimum.tar.bz2

echo "=========================================="
echo "  INSTALAÇÃO CONCLUÍDA!"
echo "=========================================="
echo ""
echo "Verifique se a compilação foi bem-sucedida:"
echo "- WRF executáveis: ls -la /opt/WRF/main/*.exe"
echo "- WPS executáveis: ls -la /opt/WPS/*.exe"
echo ""
echo "Reinicie o terminal ou execute: source ~/.bashrc"