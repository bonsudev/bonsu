#############################################
##   Filename: loadarray.py
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
import numpy
import os
from sys import platform
import ctypes
MEMARRAY = ['memory0', 'memory1', 'memory2', 'memory3', 'memory4', 'memory5', 'memory6', 'memory7', 'memory8', 'memory9', 'memorysequence']
def FreeSpace(path):
	if platform.startswith('win'):
		free = ctypes.c_ulonglong(0)
		ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(path), None, None, ctypes.pointer(free))
		return free.value
	else:
		stat = os.statvfs(path)
		free = stat.f_frsize * stat.f_bavail
		return free
def LoadArray(self, filename):
	from numpy import newaxis
	if filename in MEMARRAY:
		if filename == 'memory0':
			if numpy.any(self.memory0):
				return self.memory0
			else:
				raise TypeError
		elif filename == 'memory1':
			if numpy.any(self.memory1):
				return self.memory1
			else:
				raise TypeError
		elif filename == 'memory2':
			if numpy.any(self.memory2):
				return self.memory2
			else:
				raise TypeError
		elif filename == 'memory3':
			if numpy.any(self.memory3):
				return self.memory3
			else:
				raise TypeError
		elif filename == 'memory4':
			if numpy.any(self.memory4):
				return self.memory4
			else:
				raise TypeError
		elif filename == 'memory5':
			if numpy.any(self.memory5):
				return self.memory5
			else:
				raise TypeError
		elif filename == 'memory6':
			if numpy.any(self.memory6):
				return self.memory6
			else:
				raise TypeError
		elif filename == 'memory7':
			if numpy.any(self.memory7):
				return self.memory7
			else:
				raise TypeError
		elif filename == 'memory8':
			if numpy.any(self.memory8):
				return self.memory8
			else:
				raise TypeError
		elif filename == 'memory9':
			if numpy.any(self.memory9):
				return self.memory9
			else:
				raise TypeError
		elif filename == 'memorysequence':
			if numpy.any(self.seqdata):
				return self.seqdata
			else:
				raise TypeError
	else:
		try:
			array = numpy.array(numpy.load(filename), dtype=numpy.cdouble, copy=True, order='C')
		except MemoryError:
			self.ancestor.GetPage(0).queue_info.put("Could not load array. Insufficient memory.")
			raise MemoryError
		if array.ndim == 2:
			array = array[:, :, newaxis]
		if array.ndim == 1:
			array = array[:, newaxis, newaxis]
		if array.ndim > 3:
			raise TypeError
		else:
			return array
def LoadCoordsArray(self, filename):
	if filename == 'memorycoords':
		if numpy.any(self.coordarray):
			return self.coordarray
		else:
			raise TypeError
	else:
		array = numpy.load(filename)
		if array.ndim > 2:
			raise TypeError
		elif array.ndim < 2:
			raise TypeError
		elif array.shape[1] != 3:
			raise TypeError
		else:
			return array
def SaveArray(self, filename, array):
	if filename in MEMARRAY:
		if filename == 'memory0':
			self.memory0 = array
		elif filename == 'memory1':
			self.memory1 = array
		elif filename == 'memory2':
			self.memory2 = array
		elif filename == 'memory3':
			self.memory3 = array
		elif filename == 'memory4':
			self.memory4 = array
		elif filename == 'memory5':
			self.memory5 = array
		elif filename == 'memory6':
			self.memory6 = array
		elif filename == 'memory7':
			self.memory7 = array
		elif filename == 'memory8':
			self.memory8 = array
		elif filename == 'memory9':
			self.memory9 = array
	else:
		pathname = os.path.dirname(filename)
		base = os.path.basename(filename)
		cwd = os.getcwd()
		if not pathname:
			path = cwd
		else:
			path = pathname
		if os.access(path, os.W_OK):
			free = FreeSpace(path)
			fsize = array.nbytes
			if free > fsize:
				numpy.save(filename, array)
			else:
				self.ancestor.GetPage(0).queue_info.put("Could not save array: "+base+". Insufficient storage space.")
		else:
			self.ancestor.GetPage(0).queue_info.put("Could not save array: "+base+". Write access denied to "+path+".")
