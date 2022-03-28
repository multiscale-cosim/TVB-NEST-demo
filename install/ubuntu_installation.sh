#!/bin/bash

INSTALLATION_FOLDER=/home/kusch/Documents/project/co_simulation/TVB-NEST-demo/venv/

# install MPI
mkdir $INSTALLATION_FOLDER/tmp
cd $INSTALLATION_FOLDER/tmp
wget -q http://www.mpich.org/static/downloads/3.1.4/mpich-3.1.4.tar.gz
tar xf mpich-3.1.4.tar.gz
cd mpich-3.1.4
./configure --disable-fortran --enable-fast=all,O2 --prefix=$INSTALLATION_FOLDER
make -j$(nproc)
make install
cd ..
rm -rdf mpich-3.1.4.tar.gz mpich-3.1.4

# for python library
pip install --upgrade pip
pip install nose==1.3.7
pip install numpy==1.20.3 cython==0.29.23 Pillow==8.2.0
pip install mpi4py==3.0.3
pip install scipy==1.6.3
pip install elephant==0.10.0
pip install tvb-data==2.0 tvb-gdist==2.1.0 tvb-library==2.2 tvb-contrib==2.2 requests==2.25.1

# for python for plotting
pip install jupyter==1.0.0
pip install networkx==2.5.1
pip install matplotlib==3.4.2
pip install h5py==3.2.1
pip install cycler==0.10.0

# Set up environment for Nest installation
NAME_SOURCE_NEST=$INSTALLATION_FOLDER/tmp/nest-simulator-3.0
PATH_NEST_BUILD=$INSTALLATION_FOLDER/tmp/build
export PATH_NEST_BUILD
export NAME_SOURCE_NEST

# Compile and Install Nest
wget https://zenodo.org/record/4739103/files/nest-simulator-3.0.tar.gz
tar -xf nest-simulator-3.0.tar.gz
rm nest-simulator-3.0.tar.gz
mkdir $PATH_NEST_BUILD
cd $PATH_NEST_BUILD
cmake -DCMAKE_INSTALL_PREFIX:PATH=$INSTALLATION_FOLDER $NAME_SOURCE_NEST -Dwith-mpi=ON -Dwith-openmp=ON -Dwith-readline=On -Dwith-ltdl=ON -Dwith-python=ON -Dcythonize-pynest=ON
make -j
make install
#make test
rm -dr $INSTALLATION_FOLDER/tmp
