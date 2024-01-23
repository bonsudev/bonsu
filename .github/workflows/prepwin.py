#!/usr/bin/env python
#############################################
##   Filename: prepare.py
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
import sys
import os
import urllib.request
import io
from zipfile import ZipFile
import subprocess
PATH = sys.path
PYTHONPATH = PATH[4]
FFTWPATH = 'fftw3_tmp'
PYTHONLIBSPATH = os.path.join(PYTHONPATH, 'libs')
PYTHONINCPATH = os.path.join(PYTHONPATH, 'include')
fftwurl = 'https://fftw.org/pub/fftw/fftw-3.3.5-dll64.zip'
r = urllib.request.urlopen(fftwurl)
f = io.BytesIO(r.read())
zf = ZipFile(f)
zf.extractall(path = FFTWPATH)
zf.close()
# os.system("echo %cd%")
# os.system("dir")
# cmd = ["where", "/r", r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Enterprise", "lib.exe"]
# process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,stdin=subprocess.PIPE, close_fds=False)
# print(process.communicate())
#lib = r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Enterprise\VC\Tools\MSVC\14.29.30133\bin\Hostx64\x64\lib.exe"
lib = r"C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Tools\MSVC\14.38.33130\bin\Hostx64\x64\lib.exe"
wcmd = [lib, "/machine:x64", "/def:"+os.path.join(FFTWPATH, "libfftw3-3.def")]
process = subprocess.Popen(wcmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,stdin=subprocess.PIPE, close_fds=False)
print(process.communicate())
wcmd = [lib, "/machine:x64", "/def:"+os.path.join(FFTWPATH, "libfftw3f-3.def")]
process = subprocess.Popen(wcmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,stdin=subprocess.PIPE, close_fds=False)
print(process.communicate())
headerfile = os.path.join(FFTWPATH, 'fftw3.h')
cpheader = "copy "+headerfile+" "+PYTHONINCPATH
dllfile = os.path.join(FFTWPATH, 'libfftw3-3.dll')
cpdll = "copy "+dllfile+" "+PYTHONLIBSPATH
cpdll2 = "copy "+dllfile+" "+os.path.join('bonsu', 'lib')
dllfilef = os.path.join(FFTWPATH, 'libfftw3f-3.dll')
cpdllf = "copy "+dllfilef+" "+PYTHONLIBSPATH
cpdll2f = "copy "+dllfilef+" "+os.path.join('bonsu', 'lib')
libfile_old = 'libfftw3-3.lib'
libfile = 'fftw3.lib'
os.system('rename '+libfile_old+' '+libfile)
cplib = "copy "+libfile+" "+PYTHONLIBSPATH
expfile = 'libfftw3-3.exp'
cpexp = "copy "+expfile+" "+PYTHONLIBSPATH
libfile_oldf = 'libfftw3f-3.lib'
libfilef = 'fftw3f.lib'
os.system('rename '+libfile_oldf+' '+libfilef)
cplibf = "copy "+libfilef+" "+PYTHONLIBSPATH
expfilef = 'libfftw3f-3.exp'
cpexpf = "copy "+expfilef+" "+PYTHONLIBSPATH
os.system(cpheader)
os.system(cpdll)
os.system(cpdll2)
os.system(cpdllf)
os.system(cpdll2f)
os.system(cplib)
os.system(cpexp)
os.system(cplibf)
os.system(cpexpf)
os.system("del "+libfile)
os.system("del "+expfile)
os.system("del "+libfilef)
os.system("del "+expfilef)
os.system("rmdir /s/q "+FFTWPATH)
