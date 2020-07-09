#############################################
##   Filename: memory.py
##
##    Copyright (C) 2018 Marcus C. Newton
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
import ctypes
from sys import platform
class MemoryStatusEx(ctypes.Structure):
	_fields_ = [
		("dwLength", ctypes.c_ulong),
		("dwMemoryLoad", ctypes.c_ulong),
		("ullTotalPhys", ctypes.c_ulonglong),
		("ullAvailPhys", ctypes.c_ulonglong),
		("ullTotalPageFile", ctypes.c_ulonglong),
		("ullAvailPageFile", ctypes.c_ulonglong),
		("ullTotalVirtual", ctypes.c_ulonglong),
		("ullAvailVirtual", ctypes.c_ulonglong),
		("sullAvailExtendedVirtual", ctypes.c_ulonglong),
		]
	def __init__(self):
		self.dwLength = ctypes.sizeof(self)
		super(MemoryStatusEx, self).__init__()
def GetVirtualMemory():
	WINDOWS = platform.startswith("win")
	LINUX = platform.startswith("linux")
	MACOS = platform.startswith("darwin")
	AIX = platform.startswith("aix")
	if WINDOWS:
		stat = MemoryStatusEx()
		ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
		return stat.ullTotalPhys
	elif LINUX:
		mems = {}
		with open('/proc/meminfo',"rb") as f:
			for line in f:
				fields = line.split()
				mems[fields[0]] = int(fields[1]) * 1024
		total = mems[b'MemTotal:']
		return total
	elif MACOS:
		from subprocess import check_output
		total = check_output(['sysctl', '-n', 'hw.memsize'])
		total = int(total)
		return total
	else:
		return 0
