![Build Status](https://github.com/bonsudev/bonsu/actions/workflows/build_wheels.yml/badge.svg) [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) ![Python Versions](https://img.shields.io/badge/Python-3.7%7C3.8%7C3.9-brightgreen) ![PyPI](https://img.shields.io/pypi/v/bonsu) ![PyPI - Wheel](https://img.shields.io/pypi/wheel/bonsu)


# ![Bonsu Logo](/bonsu/image/bonsu.png) Bonsu - The Interactive Phase Retrieval Suite

## Introduction

Bonsu is a collection of tools and algorithms primarily for the reconstruction of phase information from diffraction intensity measurements.

If Bonsu is used within article publications, it is requested that authors cite this publication:

[Newton M. C., Nishino Y. and Robinson I. K., J., Appl. Cryst. (2012). 45, 840-843.](https://dx.doi.org/10.1107/S0021889812026751)

## Installation

Bonsu requires:
* Python >= 3.7
* wxPython >= 4.0.1
* NumPy (FFTW aware) >= 1.4.1
* VTK (with python bindings) >= 5.4.2
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


#### Version 3.4.2 🗓 ️(15/10/2021)

	🔧 Bug fixes.


#### Version 3.4.1 🗓 ️(17/09/2021)

	✨ Concurrent phase retrieval scripting algorithm.
	✨ Arbitrary bounds in Interpolate Object function.
	✨ Affine Transform function on coordinates.


#### Version 3.4.0 🗓 ️(12/08/2021)

	✨ Installation improvements.
	🔧 Bug fixes.

#### Version 3.3.7 🗓 ️(19/07/2021)

	🔧 Bug fixes.

#### Version 3.3.6 🗓 ️(19/07/2021)

	✨ Interface improvements.
	🔧 Bug fixes.

#### Version 3.3.5 🗓 ️(31/03/2021)

	✨ Empty Array Function.
	🔧 Bug fixes.

#### Version 3.3.4 🗓 (17/02/2021)

	🔧 Bug fixes.

#### Version 3.3.3 🗓 (12/02/2021)

	✨ Polyhedron Support Function.
	🔧 Bug fixes.

#### Version 3.3.2 🗓 (11/01/2021)

	✨ Compatibility with h5py 3.x
	🔧 Bug fixes.

#### Version 3.3.1 🗓 (07/09/2020)

	🔧 Bug fixes.

#### Version 3.3.0 🗓 (24/07/2020)

	✨ Posix threading and SIMD AVX2 support.
	🔧 Bug fixes.

#### Version 3.2.2 🗓 (09/06/2020)

	✨ Memory management improvements.
	🔧 Minor interface improvements and bug fixes.

#### Version 3.2.1 🗓 (03/05/2020)

	✨ Compatibility with wxPython 4.1.0
	🔧 Minor interface improvements and bug fixes.

#### Version 3.2.0 🗓 (29/04/2020)

	✨ Custom algorithm design interface.
	✨ Reweighted 2D saddle-point optimisation algorithm.
	🔧 Minor interface improvements and bug fixes.

#### Version 3.1.0 🗓 (10/03/2020)

	✨ Diamond nexus beamline data viewer for I16.
	✨ Concurrent phase reconstruction
	🔧 Rotate Support function now works for large arrays
	🔧 Minor interface improvements and bug fixes.

#### Version 3.0.0 🗓 (01/07/2019)

	✨ Algorithm scripting interface.
	✨ Python script function.
	✨ Memory management for large arrays.
	🔧 Minor interface improvements and bug fixes.

#### Version 2.6.0 🗓 (16/02/2018)

	✨ Scene menu entry for visualisation tools.
	✨ Anti-aliasing menu option.
	✨ Visualisation XYZ orientation widget styling. 
	✨ Visualisation scale bar styling. 
	✨ Specular/diffuse lighting option in visualisation.
	✨ Added Centred Resize function.
	🔧 Fixed byte/string array view bug in HDF viewer with Python 3.
	🔧 Fixed 2D visualisation viewport size correction.  

#### Version 2.5.0 🗓 (04/12/2017)

	✨ Compatibility with Python 3.
	🔧 Minor interface improvements and bug fixes.

#### Version 2.4.0 🗓 (26/09/2017)

	✨ Memory array manipulation in Python shell.
	🔧 Fixed animate scene bug.

#### Version 2.3.1 🗓 (12/08/2017)

	✨ Check box to pipeline items to optionally exempt from execution.
	✨ XYZ orientation widget. 
	✨ Stacked TIFF file support.
	🔧 Fixed load array to memory bugs.
	🔧 Compatibility wxPython 4.  

#### Version 2.2.0 🗓 (04/05/2017)

	✨ ER, HPR and RAAR partial coherence algorithms added.
	✨ Load and save point spread functions added. 
	🔧 Minor interface improvements and bug fixes.
	🔧 Fixed bug in shrink wrap support creation method.

#### Version 2.1.0 🗓 (15/03/2017)

	✨ Added View Support pipeline item.
	✨ Partial coherence algorithm now shows Richardson-Lucy iterations
	🔧 Fixed various interface bugs.

#### Version 2.0.1 🗓 (27/01/2017)

	🔧 Fixed various interface bugs.

#### Version 2.0.0 🗓 (04/01/2017)

	✨ Added Comments pipeline item.
	🔧 Fixed various interface bugs.

#### Version 1.4.2 🗓 (07/04/2016)

	🔧 Added Apple OSX desktop integration.
	🔧 Fixed various interface bugs.

#### Version 1.4.1 🗓 (07/12/2015)

	🔧 Fixed various interface bugs.


#### Version 1.4.0 🗓 (04/10/2015)

	✨ Added a number of new array operations.
	✨ Added support for saving arrays from memory slots.
	✨ Various improvements to the interface.
	🔧 Fixed various interface bugs.


#### Version 1.3.0 🗓 (02/04/2015)

	✨ Added compatibility with VTK 6.
	✨ Added compatibility with wxpython 3.
	✨ Added support for loading of arrays directly into memory slots
	✨ Various improvements to the interface.
	🔧 Fixed various interface bugs.


#### Version 1.2.0 🗓 (04/07/2014)

	🔧 Fixed various bugs for improved stability.
	🔧 Fixed bug in visualisation animation.
	🔧 Improved compatibility with msvc/intel compilers.
	✨ Added partial coherence algorithm.
	
  

#### Version 1.1.0 🗓 (04/07/2013)

	✨ Added support for program wide array manipulation in memory.
	🔧 Fixed sequence data array size change bug.
	✨ Added support for changeable working directory.
	✨ Added support for alternative colour map lookup tables.
	✨ Added array Gaussian fill operation.
	✨ Added array Fourier transform operation.
	✨ Added array convolution operation.
	✨ Added array conjugate and reflect operation.
	✨ Added support for undocking/docking visualisation.
	🔧 Fixed array wrap operation for arrays with odd dimensions.


#### Version 1.0.0 🗓 (04/04/2013)

	✨ First stable release.



## Licence
GNU GPLv3
Copyright 2011 - 2021 - Marcus C. Newton
Registration number 284653218
