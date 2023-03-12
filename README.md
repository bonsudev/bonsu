![Build Status](https://github.com/bonsudev/bonsu/actions/workflows/build_wheels.yml/badge.svg) [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) ![Python Versions](https://img.shields.io/badge/Python-3.7%7C3.8%7C3.9%7C3.10-brightgreen) ![PyPI](https://img.shields.io/pypi/v/bonsu) ![PyPI - Wheel](https://img.shields.io/pypi/wheel/bonsu)


# <img src="/bonsu/image/bonsu.ico" alt= "" width="64" height="64"> Bonsu - The Interactive Phase Retrieval Suite

## Introduction

Bonsu is a collection of tools and algorithms primarily for the reconstruction of phase information from diffraction intensity measurements.

## Citation

If your use of this software results in a scientific publication, please cite the following article:

[Newton M. C., Nishino Y. and Robinson I. K., J., Appl. Cryst. (2012). 45, 840-843.](https://dx.doi.org/10.1107/S0021889812026751)

## Installation

Bonsu requires:
* Python >= 3.7
* wxPython >= 4.1.0
* NumPy (FFTW aware) >= 1.4.1
* VTK (with python bindings) >= 8.0.0
* h5py
* Pillow
* FFTW with threading >= 3.0

Installation via pip:
```
$ pip install bonsu
```
 To run:
 ```
$ bonsu 
```

## Reporting Bugs

Please send any bugs, problems, and proposals to: Bonsu.Devel@gmail.com
or visit: http://github.com/bonsudev/bonsu

## Documentation

Online documentation is available [here](https://bonsudev.github.io/bonsu/) and includes installation instructions.
A PDF version of the documentation is available [here](/bonsu/docs/Bonsu.pdf).
Documentation is also available in the application. 

## Version History

Please see the [change log](bonsu/changelog/CHANGELOG.md).


## Licence

GNU GPLv3
Copyright 2011 - 2023 - Marcus C. Newton
Registration number 284653218
