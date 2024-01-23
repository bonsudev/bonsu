#!/usr/bin/env python
#############################################
##   Filename: setup.py
##
##    Copyright (C) 2011 - 2024 Marcus C. Newton
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
##
## Contact: Bonsu.Devel@gmail.com
#############################################
from setuptools import setup
from setuptools import Extension
from Cython.Build import cythonize
import os, datetime
from sys import argv
from sys import platform
from sys import prefix
import numpy
args = argv[1:]
def SetBuildDate():
	filename_bonsu = os.path.join(os.path.dirname(__file__), 'bonsu', 'interface', 'bonsu.py')
	f1_bonsu = open(filename_bonsu, 'r')
	lines = f1_bonsu.readlines()
	for i in range(len(lines)):
		if lines[i].startswith("__builddate__"):
			if 'sdist' == args[0]:
				lines[i] = "__builddate__ = ''"+os.linesep
			else:
				lines[i] = "__builddate__ = '"+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"'"+os.linesep
	f2_bonsu = open(filename_bonsu, 'w')
	f2_bonsu.writelines(lines)
	f1_bonsu.close()
	f2_bonsu.close()
def GetPkgData( type=args[0] ):
	SetBuildDate()
	package_data = {
		'bonsu.licence': ['gpl.txt'],
		'bonsu.changelog': ['CHANGELOG.md'],
		'bonsu.interface': ['cms.npy'],
		'bonsu.image': ['bonsu.ico', 'bonsu.icns'],
		'bonsu.docs': ['*.*', '_images/*.*', '_images/math/*.*', '_static/*.*']}
	if platform.startswith('win'):
		extra_package_data = {'bonsu.lib': ['libfftw3-3.dll', 'libfftw3f-3.dll']}
		package_data.update(extra_package_data)
	if type == 'sdist':
		lib_pkg_data = {
		'bonsu.lib':['fftwlib.pxd', 'fftwlib.pyx', 'prutillib.pyx']
		}
		package_data.update(lib_pkg_data)
	return package_data
def GetExtMods():
	debug_compile_args = '-Wall'
	openmp_compile_args = ''
	openmp_link_args = ''
	extra_links = []
	libraries_fftw = ['fftw3', 'fftw3f']
	if platform.startswith('linux'):
		openmp_compile_args = '-fopenmp'
		openmp_link_args = '-fopenmp'
		extra_links.append(openmp_link_args)
		libraries_fftw.append('fftw3_threads')
		libraries_fftw.append('fftw3f_threads')
	elif platform.startswith('darwin'):
		openmp_compile_args = '-fopenmp'
		openmp_link_args = '-fopenmp'
		libraries_fftw.append('fftw3_threads')
		libraries_fftw.append('fftw3f_threads')
	elif platform.startswith('win'):
		openmp_compile_args = '/openmp'
		openmp_link_args = ''
	else:
		openmp_compile_args = '-fopenmp'
		openmp_link_args = '-fopenmp'
		extra_links.append(openmp_link_args)
	fftwlib = Extension(
		'bonsu.lib.fftwlib',
		include_dirs = ['include', numpy.get_include()],
		libraries = libraries_fftw,
		language="c++",
		extra_compile_args = [debug_compile_args, openmp_compile_args],
		extra_link_args=extra_links,
		define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
		sources = [os.path.join('bonsu', 'lib', 'fftwlib.pyx')])
	prutillib = Extension(
		'bonsu.lib.prutillib',
		include_dirs = ['include', numpy.get_include()],
		language="c++",
		extra_compile_args = [debug_compile_args, openmp_compile_args],
		extra_link_args=extra_links,
		define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
		sources = [os.path.join('bonsu', 'lib', 'prutillib.pyx')])
	ext_modules_lst = [*cythonize(fftwlib, compiler_directives={'language_level' : "3"}),\
						*cythonize(prutillib, compiler_directives={'language_level' : "3"})]
	return ext_modules_lst
setup(
	ext_modules = GetExtMods(),
	package_data = GetPkgData()
)
