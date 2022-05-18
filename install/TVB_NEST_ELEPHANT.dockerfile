#Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
#Licensed to the Apache Software Foundation (ASF) under one
#or more contributor license agreements.  See the NOTICE file
#distributed with this work for additional information
#regarding copyright ownership.  The ASF licenses this file
#to you under the Apache License, Version 2.0 (the
#"License"); you may not use this file except in compliance
#with the License.  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing,
#software distributed under the License is distributed on an
#"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#KIND, either express or implied.  See the License for the
#specific language governing permissions and limitations
#under the License.

FROM debian:buster-slim

# get compiler and access to web interface
RUN apt-get update;\
    apt-get install -y g++ gcc gfortran make strace wget git

# install python
RUN  apt-get install -y build-essential cmake zlib1g-dev libltdl-dev libncurses5-dev libgdbm-dev libreadline-dev \
     libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev libgsl-dev libbz2-dev curl;\
     cd /root ;\
     curl -O https://www.python.org/ftp/python/3.8.10/Python-3.8.10.tar.xz ;\
     tar -xf Python-3.8.10.tar.xz ;\
     cd Python-3.8.10 ;\
     ./configure --enable-optimizations --enable-shared ;\
     make ;\
     make altinstall ;\
     cd .. ;\
     rm -rdf  Python-3.8.10.tar.xz Python-3.8.10

ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib/

# install pip
RUN cd /root ;\
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py;\
    python3.8 get-pip.py;\
    rm get-pip.py;\
    pip install --upgrade pip

# install MPI
RUN wget -q http://www.mpich.org/static/downloads/3.1.4/mpich-3.1.4.tar.gz;\
    tar xf mpich-3.1.4.tar.gz;\
    cd mpich-3.1.4;\
    ./configure --disable-fortran --enable-fast=all,O3 --prefix=/usr;\
    make -j$(nproc);\
    make install

# Install the dependance for Nest
RUN pip install nose;\
    pip install numpy cython Pillow;\
    pip install matplotlib;\
    pip install mpi4py;\
    apt-get install -y liblapack-dev;\
    pip install scipy ;\
    pip install elephant

# install TVB
RUN apt-get install -y llvm-dev llvm;\
    export LLVM_CONFIG=/usr/bin/llvm-config;\
    pip install requests;\
    pip install tvb-data==2.0 tvb-gdist==2.1.0 tvb-library==2.2 tvb-contrib==2.2

# Compile and Install package for Nest
RUN cd /home/;\
    wget https://zenodo.org/record/4739103/files/nest-simulator-3.0.tar.gz;\
    tar -xf nest-simulator-3.0.tar.gz;\
    rm nest-simulator-3.0.tar.gz;\
    mv nest-simulator-3.0 nest-io-dev

RUN cd /home/;\
    NAME_SOURCE_NEST=/home/nest-io-dev;\
    PATH_INSTALATION=/usr/lib/nest/;\
    PATH_BUILD=/home/nest-simulator-build;\
    export PATH_INSTALATION;\
    export PATH_BUILD	;\
    export NAME_SOURCE_NEST;\
    export NEST_DATA_PATH=$PATH_BUILD/pynest;\
    export PYTHONPATH=$PATH_INSTALATION/lib/python3.8/site-packages:$PYTHONPATH;\
    export PATH=$PATH:$PATH_INSTALATION/bin;\
    mkdir $PATH_BUILD;\
    cd $PATH_BUILD;\
    cmake -DCMAKE_INSTALL_PREFIX:PATH=$PATH_INSTALATION $NAME_SOURCE_NEST -Dwith-mpi=ON -Dwith-openmp=ON -Dwith-readline=On -Dwith-ltdl=ON -Dwith-python=ON -Dcythonize-pynest=ON ;\
    make;\
    make install
    #make installcheck

# Copy files of the project
COPY  ./nest_elephant_tvb /home/nest_elephant_tvb

# create python3 executable
RUN ln -s /usr/local/bin/python3.8 /usr/local/bin/python3

ENV PYTHONPATH=/usr/lib/nest/lib/python3.8/site-packages/:/home/:$PYTHONPATH

