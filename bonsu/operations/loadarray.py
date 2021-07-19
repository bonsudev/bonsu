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
	if isinstance(array, numpy.ndarray):
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
def ByteAlignedArray(x, y, z, alignment=32, dtype=numpy.cdouble, order='C', type=0):
	size = x*y*z
	pad = alignment // numpy.dtype(dtype).itemsize
	if type == 0:
		buffer = numpy.zeros(size + pad, dtype=dtype, order=order)
	else:
		buffer = numpy.ones(size + pad, dtype=dtype, order=order)
	offset = (-buffer.ctypes.data % alignment) // numpy.dtype(dtype).itemsize
	ar_align = buffer[offset:offset+size].reshape(x,y,z)
	assert (ar_align.ctypes.data % alignment) == 0
	assert ar_align.flags['C_CONTIGUOUS'] == True
	return ar_align
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
			array = ByteAlignedArray(x,y,z)
		elif type == 1:
			if val == 1:
				array = ByteAlignedArray(x,y,z, dtype=numpy.double, type=1)
			else:
				array = ByteAlignedArray(x,y,z, dtype=numpy.double)
	except MemoryError:
		self.ancestor.GetPage(0).queue_info.put("Could not create array. Insufficient memory.")
		raise MemoryError
	else:
		return array
def _NewArrayPair(x,y,z, type=0, alignment=32, order='C'):
	size = x*y*z
	size2 = size*2
	if type == 0:
		dtype=numpy.cdouble
		pad = alignment // numpy.dtype(dtype).itemsize
		buffer = numpy.empty(size2 + pad, dtype=dtype, order=order)
		offset = (-buffer.ctypes.data % alignment) // numpy.dtype(dtype).itemsize
		ar_align1 = buffer[offset:offset+size].reshape(x,y,z)
		ar_align2 = buffer[offset+size:offset+size2].reshape(x,y,z)
	elif type == 1:
		dtype=numpy.double
		pad = alignment // numpy.dtype(dtype).itemsize
		buffer = numpy.empty(size2 + pad, dtype=dtype, order=order)
		offset = (-buffer.ctypes.data % alignment) // numpy.dtype(dtype).itemsize
		ar_align1 = buffer[offset:offset+size].reshape(x,y,z)
		ar_align2 = buffer[offset+size:offset+size2].reshape(x,y,z)
	return ar_align1,ar_align2
def NewArrayPair(self,x,y,z, type=0, alignment=32, order='C'):
	try:
		ar_align1,ar_align2 = _NewArrayPair(x,y,z, type=type, alignment=alignment, order=order)
	except MemoryError:
		self.ancestor.GetPage(0).queue_info.put("Could not create array. Insufficient memory.")
		raise MemoryError
	else:
		return ar_align1,ar_align2
def LoadArray(self, filename):
	if NameIsMem(filename):
		if filename in self.memory:
			array = ArTo3DNpy(self.memory[filename])
			return array
		else:
			raise NameError
	else:
		try:
			array_mm = numpy.load(filename, mmap_mode='r')
			shape = array_mm.shape
			if array_mm.ndim == 2:
				shape = (*shape, 1)
			elif array_mm.ndim == 1:
				shape = (*shape, 1, 1)
			elif array_mm.ndim > 3:
				self.ancestor.GetPage(0).queue_info.put("Could not load array. Too many dimensions.")
				self.ancestor.GetPage(4).UpdateLog(None)
				raise TypeError
			elif array_mm.ndim < 1:
				self.ancestor.GetPage(0).queue_info.put("Could not load array. Too few dimensions.")
				self.ancestor.GetPage(4).UpdateLog(None)
				raise TypeError
		except:
			self.ancestor.GetPage(0).queue_info.put("Could not load array. Please check the input fields.")
			self.ancestor.GetPage(4).UpdateLog(None)
			raise IOError
		else:
			try:
				dt = numpy.dtype(numpy.complex128)
				memsize = dt.itemsize
				for i in shape:
					memsize *= i
				totalmem = GetVirtualMemory()
				if 2*memsize > totalmem and self.citer_flow[10] == 0:
					self.ancestor.GetPage(0).queue_info.put("Array is greater than half of the total memory. You can remove this restriction in the main menu.")
					self.ancestor.GetPage(4).UpdateLog(None)
					raise MemoryError
			except MemoryError:
				raise MemoryError
			else:
				try:
					x,y,z = shape
					array = ByteAlignedArray(x,y,z)
					numpy.copyto(array, ArTo3DNpy(array_mm))
				except MemoryError:
					self.ancestor.GetPage(0).queue_info.put("Could not load array. Insufficient memory.")
					self.ancestor.GetPage(4).UpdateLog(None)
					raise MemoryError
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
