#!/bin/bash
#
mkdir fftw_build
cd fftw_build
wget http://fftw.org/fftw-3.3.10.tar.gz
tar -xvf fftw-3.3.10.tar.gz
cd fftw-3.3.10
./configure --enable-threads --enable-shared CFLAGS='-arch x86_64 -arch arm64' CXXFLAGS='-arch x86_64 -arch arm64'
make -j2
make install
make clean
./configure --enable-float --enable-threads --enable-shared CFLAGS='-arch x86_64 -arch arm64' CXXFLAGS='-arch x86_64 -arch arm64'
make -j2
make install
cd ..
cd ..

