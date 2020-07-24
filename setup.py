#!/usr/bin/env python
#############################################
##   Filename: setup.py
##
##    Copyright (C) 2011 Marcus C. Newton
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
import os, datetime
from sys import argv
from sys import platform
from sys import executable
from sys import exec_prefix
from distutils.version import StrictVersion
from distutils.file_util import copy_file
import numpy
# Change compiler if needed
# os.environ["CC"] = "icc"
# Change fftw3 path if needed
# fftw_include_path = ''
from numpy.distutils.system_info import get_info
fftw_include_path = get_info('fftw3')['include_dirs'][0]
DEBUG = True
args = argv[1:]
if args[0].startswith('bdist_wheel'):
	from setuptools import setup, Extension
else:
	from distutils.core import setup, Extension
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
from bonsu.interface.bonsu import __version__
sourcelist = ['bonsu/lib/prfftwmodule.cxx', 'bonsu/lib/prfftwhiomask.cxx', 'bonsu/lib/prfftwhio.cxx',
										'bonsu/lib/prfftwhioplus.cxx', 'bonsu/lib/prfftwpchiomask.cxx', 'bonsu/lib/prfftwpgchiomask.cxx','bonsu/lib/prfftwer.cxx',
										'bonsu/lib/prfftwermask.cxx','bonsu/lib/prfftwpoermask.cxx','bonsu/lib/prfftwraar.cxx','bonsu/lib/prfftwhpr.cxx',
										'bonsu/lib/prfftwermaskpc.cxx','bonsu/lib/prfftwhprmaskpc.cxx','bonsu/lib/prfftwraarmaskpc.cxx','bonsu/lib/prfftwso2d.cxx',
										'bonsu/lib/prfftwcshio.cxx','bonsu/lib/prfftwhiomaskpc.cxx','bonsu/lib/median.cxx', 'bonsu/lib/blanklinereplace.cxx' ]
if 'sdist' == args[0]:
	package_data_dict={'bonsu.licence': ['gpl.txt'], 'bonsu.interface': ['cms.npy'], 'bonsu.image': ['bonsu.ico'], 'bonsu.lib':['prfftwmodule.h'], 'bonsu.macos':['*'], 'bonsu.docs': ['*.*', '_images/*.*', '_images/math/*.*', '_static/*.*']}
else:
	if platform.startswith('win'):
		package_data_dict={'bonsu.licence': ['gpl.txt'], 'bonsu.interface': ['cms.npy'], 'bonsu.image': ['bonsu.ico'],'bonsu.docs': ['*.*', '_images/*.*', '_images/math/*.*', '_static/*.*'], 'bonsu.lib': ['libfftw3-3.dll']}
	else:
		package_data_dict={'bonsu.licence': ['gpl.txt'], 'bonsu.interface': ['cms.npy'], 'bonsu.image': ['bonsu.ico'],'bonsu.docs': ['*.*', '_images/*.*', '_images/math/*.*', '_static/*.*']}
try:
	from distutils.sysconfig import get_config_vars
	(opt,) = get_config_vars('OPT')
	os.environ['OPT'] = " ".join(flag for flag in opt.split() if flag != '-Wstrict-prototypes')
except:
	pass
if DEBUG:
	debug_compile_args = "-Wall"
else:
	debug_compile_args = ""
if platform.startswith('win'):
	scripts=['bonsu/bonsu', 'bonsupost']
else:
	scripts=['bonsu/bonsu']
if platform.startswith('linux'):
	iconfolder_old='share/pixmaps'
	iconfolder='share/icons/hicolor/48x48/apps'
	data_files=[('share/applications', ['bonsu/image/bonsu.desktop']), (iconfolder, ['bonsu/image/bonsu.png']), (iconfolder, ['bonsu/image/bonsu.xpm'])]
	modprfftw_lib = ['fftw3', 'fftw3_threads']
	sourcelist.append('bonsu/lib/libphase-pthread.cxx')
	sourcelist.append('bonsu/lib/prfftwrs-pthread.cxx')
	if 'sdist' == args[0]:
		sourcelist.append('bonsu/lib/libphase.cxx')
		sourcelist.append('bonsu/lib/prfftwrs.cxx')
elif platform.startswith('win'):
	data_files=[]
	modprfftw_lib = ['fftw3']
	sourcelist.append('bonsu/lib/libphase.cxx')
	sourcelist.append('bonsu/lib/prfftwrs.cxx')
	if 'sdist' == args[0]:
		sourcelist.append('bonsu/lib/libphase-pthread.cxx')
		sourcelist.append('bonsu/lib/prfftwrs-pthread.cxx')
elif platform.startswith('darwin'):
	if not args[0].startswith('bdist'):
		binstr = executable
		binstrbonsu = os.path.join(exec_prefix,'bin','bonsu')
		appenv = '#!/usr/bin/env bash'
		approot = os.path.join(os.environ['HOME'],'Desktop')
		apppath = os.path.join(approot,'bonsu.app/Contents/MacOS')
		apppathcont = os.path.join(approot,'bonsu.app/Contents')
		apppathres = os.path.join(approot,'bonsu.app/Contents/Resources')
		fname='bonsu/macos/bonsu'
		f = open(fname,'w')
		f.write(appenv)
		f.write(os.linesep)
		f.write(binstr+' '+binstrbonsu)
		f.close()
		data_files=[(apppath, [fname]),(apppathcont, ['bonsu/macos/Info.plist']),(apppathres, ['bonsu/macos/bonsu.icns'])]
	else:
		data_files=[]
	modprfftw_lib = ['fftw3', 'fftw3_threads']
	sourcelist.append('bonsu/lib/libphase.cxx')
	sourcelist.append('bonsu/lib/prfftwrs.cxx')
	if 'sdist' == args[0]:
		sourcelist.append('bonsu/lib/libphase-pthread.cxx')
		sourcelist.append('bonsu/lib/prfftwrs-pthread.cxx')
else:
	data_files=[]
	modprfftw_lib = ['fftw3']
	sourcelist.append('bonsu/lib/libphase.cxx')
	sourcelist.append('bonsu/lib/prfftwrs.cxx')
	if 'sdist' == args[0]:
		sourcelist.append('bonsu/lib/libphase-pthread.cxx')
		sourcelist.append('bonsu/lib/prfftwrs-pthread.cxx')
modprfftw = Extension('prfftw',
					include_dirs=['include', numpy.get_include(), os.path.join(numpy.get_include(), 'numpy'), fftw_include_path],
					libraries=modprfftw_lib,
					extra_compile_args = [debug_compile_args],
					sources = sourcelist)
setup\
(
	name='Bonsu',
	version=__version__,
	license='GPL3',
	description='Bonsu - The Interactive Phase Retrieval Suite',
	author='Marcus C. Newton',
	maintainer='Marcus C. Newton',
	author_email='Bonsu.Devel@gmail.com',
	url='https://github.com/bonsudev/bonsu',
	packages=['bonsu',
						'bonsu.interface',
						'bonsu.operations',
						'bonsu.lib',
						'bonsu.sequences',
						'bonsu.phasing',
						'bonsu.licence',
						'bonsu.image',
						'bonsu.macos',
						'bonsu.docs'],
	ext_package='bonsu.lib',
	ext_modules=[modprfftw],
	scripts=scripts,
	package_data=package_data_dict,
	data_files=data_files,
	requires=['wx (>=2.8.10)', 'numpy (>=1.4.1)', 'vtk (>=5.4.2)', 'h5py'],
	long_description='Bonsu is a collection of tools and algorithms primarily for the reconstruction of phase information from diffraction intensity measurements.'
)
