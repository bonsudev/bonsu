#!/usr/bin/env python
#############################################
##   Filename: setup.py
##
##    Copyright (C) 2021 Marcus C. Newton
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
from setuptools import setup, Extension
import os, datetime
from sys import argv
from sys import platform
from sys import modules as sysmodules
args = argv[1:]
def CheckPython():
	from sys import version_info
	if version_info < (3,7):
		from sys import exit
		exit('Python < 3.7 is not supported. Please upgrade.')
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
def SetBuiltin(name, value):
	if isinstance(__builtins__, dict):
		__builtins__[name] = value
	else:
		setattr(__builtins__, name, value)
def ExtInclude(pars):
	from setuptools.command.build_ext import build_ext as _build_ext
	class build_ext(_build_ext):
		def finalize_options(self):
			_build_ext.finalize_options(self)
			SetBuiltin("__NUMPY_SETUP__",False)
			import numpy
			from numpy.distutils.system_info import get_info
			self.include_dirs.append(numpy.get_include())
			self.include_dirs.append(os.path.join(numpy.get_include(), 'numpy'))
			fftw_include_path = get_info('fftw3')['include_dirs'][0]
			self.include_dirs.append(fftw_include_path)
	return build_ext(pars)
def Build( type=args[0] ):
	bonsu_description = """ Bonsu is a collection of tools and algorithms primarily for
	the reconstruction of phase information from diffraction intensity measurements.
	"""
	debug_compile_args = "-Wall"
	SETUP_REQUIRES = [
		"wx (>=4.0.0)",
		"numpy (>=1.12.0)",
		"vtk (>=5.4.2)",
		"h5py",
		"pillow"]
	if type == 'develop':
		INSTALL_REQUIRES = []
	else:
		INSTALL_REQUIRES = [
			"wxpython >=4.0.0",
			"numpy >=1.12.0",
			"vtk >=5.4.2",
			"h5py",
			"pillow"]
	sourcelist = [
		'bonsu/lib/prfftwmodule.cxx',
		'bonsu/lib/prfftwhiomask.cxx',
		'bonsu/lib/prfftwhio.cxx',
		'bonsu/lib/prfftwhioplus.cxx',
		'bonsu/lib/prfftwpchiomask.cxx',
		'bonsu/lib/prfftwpgchiomask.cxx',
		'bonsu/lib/prfftwer.cxx',
		'bonsu/lib/prfftwermask.cxx',
		'bonsu/lib/prfftwpoermask.cxx',
		'bonsu/lib/prfftwraar.cxx',
		'bonsu/lib/prfftwhpr.cxx',
		'bonsu/lib/prfftwermaskpc.cxx',
		'bonsu/lib/prfftwhprmaskpc.cxx',
		'bonsu/lib/prfftwraarmaskpc.cxx',
		'bonsu/lib/prfftwso2d.cxx',
		'bonsu/lib/prfftwcshio.cxx',
		'bonsu/lib/prfftwhiomaskpc.cxx',
		'bonsu/lib/median.cxx',
		'bonsu/lib/blanklinereplace.cxx']
	package_data_dict = {
		'bonsu.licence': ['gpl.txt'],
		'bonsu.interface': ['cms.npy'],
		'bonsu.image': ['bonsu.ico'],
		'bonsu.docs': ['*.*', '_images/*.*', '_images/math/*.*', '_static/*.*']}
	data_files = []
	modprfftw_lib =  ['fftw3']
	if type.startswith('bdist_wheel'):
		SETUP_REQUIRES.append("wheel")
	if os.environ.get('BONSU_SETUP_REQUIRES', '1') == '0':
		SETUP_REQUIRES = []
	from sys import executable
	from sys import exec_prefix
	if type == 'sdist':
		extra_package_data = {
		'bonsu.lib':['prfftwmodule.h'],
		'bonsu.macos':['*']}
		package_data_dict.update(extra_package_data)
	elif platform.startswith('win'):
		extra_package_data = {'bonsu.lib': ['libfftw3-3.dll']}
		package_data_dict.update(extra_package_data)
	if platform.startswith('win') and not type.startswith('bdist_wheel'):
		scripts=['bonsu/bonsu', 'bonsupost']
	else:
		scripts=['bonsu/bonsu']
	if platform.startswith('linux'):
		iconfolder_old='share/pixmaps'
		iconfolder='share/icons/hicolor/48x48/apps'
		extra_data_files = [
			('share/applications', ['bonsu/image/bonsu.desktop']),
			(iconfolder, ['bonsu/image/bonsu.png']),
			(iconfolder, ['bonsu/image/bonsu.xpm'])]
		data_files += extra_data_files
		modprfftw_lib.append('fftw3_threads')
		sourcelist.append('bonsu/lib/libphase-pthread.cxx')
		sourcelist.append('bonsu/lib/prfftwrs-pthread.cxx')
		if type == 'sdist':
			sourcelist.append('bonsu/lib/libphase.cxx')
			sourcelist.append('bonsu/lib/prfftwrs.cxx')
	elif platform.startswith('win'):
		sourcelist.append('bonsu/lib/libphase.cxx')
		sourcelist.append('bonsu/lib/prfftwrs.cxx')
		if type == 'sdist':
			sourcelist.append('bonsu/lib/libphase-pthread.cxx')
			sourcelist.append('bonsu/lib/prfftwrs-pthread.cxx')
	elif platform.startswith('darwin'):
		if not type.startswith('bdist'):
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
			extra_data_files = [
				(apppath, [fname]),
				(apppathcont, ['bonsu/macos/Info.plist']),
				(apppathres, ['bonsu/macos/bonsu.icns'])]
			data_files += extra_data_files
		modprfftw_lib.append('fftw3_threads')
		sourcelist.append('bonsu/lib/libphase.cxx')
		sourcelist.append('bonsu/lib/prfftwrs.cxx')
		if type == 'sdist':
			sourcelist.append('bonsu/lib/libphase-pthread.cxx')
			sourcelist.append('bonsu/lib/prfftwrs-pthread.cxx')
	else:
		sourcelist.append('bonsu/lib/libphase.cxx')
		sourcelist.append('bonsu/lib/prfftwrs.cxx')
		if type == 'sdist':
			sourcelist.append('bonsu/lib/libphase-pthread.cxx')
			sourcelist.append('bonsu/lib/prfftwrs-pthread.cxx')
	include_dirs = ['include']
	modprfftw = Extension(
		'prfftw',
		include_dirs = include_dirs,
		libraries = modprfftw_lib,
		extra_compile_args = [debug_compile_args],
		sources = sourcelist)
	setup(
		name = 'Bonsu',
		version = "3.4.2",
		license = 'GPL3',
		description = 'Bonsu - The Interactive Phase Retrieval Suite',
		author = 'Marcus C. Newton',
		maintainer = 'Marcus C. Newton',
		author_email = 'Bonsu.Devel@gmail.com',
		url = 'https://github.com/bonsudev/bonsu',
		packages = ['bonsu',
							'bonsu.interface',
							'bonsu.operations',
							'bonsu.lib',
							'bonsu.sequences',
							'bonsu.phasing',
							'bonsu.licence',
							'bonsu.image',
							'bonsu.macos',
							'bonsu.docs'],
		ext_package = 'bonsu.lib',
		ext_modules = [modprfftw],
		scripts = scripts,
		package_data = package_data_dict,
		data_files = data_files,
		cmdclass={'build_ext' : ExtInclude},
		requires = SETUP_REQUIRES,
		install_requires = INSTALL_REQUIRES,
		python_requires = '>=3.7',
		long_description = bonsu_description
	)
if __name__ == '__main__':
	CheckPython()
	SetBuildDate()
	Build()
