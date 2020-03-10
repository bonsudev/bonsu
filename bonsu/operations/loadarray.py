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
from .memory import GetVirtualMemory
def FreeSpace(path):
	if platform.startswith('win'):
		free = ctypes.c_ulonglong(0)
		ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(path), None, None, ctypes.pointer(free))
		return free.value
	else:
		stat = os.statvfs(path)
		free = stat.f_frsize * stat.f_bavail
		return free
def ArTo3DNpy(array):
	from numpy import newaxis
	if numpy.any(array):
		if array.ndim == 2:
			array = array[:, :, newaxis]
		if array.ndim == 1:
			array = array[:, newaxis, newaxis]
		if array.ndim > 3:
			raise TypeError
		else:
			return array
	else:
		raise TypeError
def NameIsMem(name):
	if name == 'memorysequence' or name == 'memoryprivate':
		return True
	elif name.startswith('memory'):
		idxpart = name.replace('memory', '')
		try:
			idx = int(idxpart)
		except:
			return False
		else:
			return True
	else:
		return False
def NewArray(self,x,y,z, type=0, val=0):
	try:
		if type == 0:
			array = numpy.zeros((x,y,z), dtype=numpy.cdouble, order='C')
		elif type == 1:
			if val == 1:
				array = numpy.ones((x,y,z), dtype=numpy.double, order='C')
			else:
				array = numpy.zeros((x,y,z), dtype=numpy.double, order='C')
	except MemoryError:
		self.ancestor.GetPage(0).queue_info.put("Could not create array. Insufficient memory.")
		raise MemoryError
	else:
		return array
def LoadArray(self, filename):
	if NameIsMem(filename):
		if filename in self.memory:
			array = ArTo3DNpy(self.memory[filename])
			return array
		else:
			raise NameError
	else:
		try:
			f = open(filename, 'rb')
			numpy.lib.npyio.format.read_magic(f)
			head = numpy.lib.npyio.format.read_array_header_1_0(f)
			f.close()
			shape = head[0]
			dt = numpy.dtype(numpy.complex128)
			memsize = dt.itemsize
			for i in shape:
				memsize *= i
			totalmem = GetVirtualMemory()
			if 2*memsize > totalmem and self.citer_flow[10] == 0:
				raise MemoryError
		except:
			self.ancestor.GetPage(0).queue_info.put("Could not load array. Array is greater than half of the total memory. You can remove this restriction in the main menu.")
			raise MemoryError
		else:
			try:
				array = numpy.array(numpy.load(filename), dtype=numpy.cdouble, copy=True, order='C')
			except MemoryError:
				self.ancestor.GetPage(0).queue_info.put("Could not load array. Insufficient memory.")
				raise MemoryError
			else:
				array = ArTo3DNpy(array)
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
	if NameIsMem(filename):
		if filename in self.memory:
			self.memory[filename+"_tmp"] = array
			del self.memory[filename]
			self.memory[filename] = self.memory.pop(filename+"_tmp")
		else:
			self.memory[filename] = array
		panelscript = self.ancestor.GetPage(3)
		panelscript.shell.interp.locals[filename] = array
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
