#############################################
##   Filename: functions.py
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
import wx
import math
import numpy
import os
import vtk
from vtk.util import numpy_support
import sys
import threading
from ..interface.render import wxVTKRenderWindowInteractor
from ..interface.common import CNTR_CLIP
from ..interface.common import IsPy3
from ..interface.common import IsNotVTK6
from ..operations.wrap import WrapArray
from ..operations.loadarray import NewArray
from ..operations.loadarray import LoadArray
from ..operations.loadarray import SaveArray
from ..operations.loadarray import LoadCoordsArray
def Sequence_BlankLineFill(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Preparing blank line fill sequence...")
		filename_in = pipelineitem.input_filename.objectpath.GetValue()
		filename_out = pipelineitem.output_filename.objectpath.GetValue()
		roipath = pipelineitem.objectpath.GetValue()
		kx =  int(pipelineitem.kdims[0].value.GetValue())
		ky =  int(pipelineitem.kdims[1].value.GetValue())
		kz =  int(pipelineitem.kdims[2].value.GetValue())
		try:
			array = LoadArray(self, filename_in)
		except:
			msg = "Could not load array."
			wx.CallAfter(self.UserMessage, title, msg)
			return
		try:
			if ( '[' in roipath and ']' in roipath ):
				roi = roipath.partition('[')[-1].rpartition(']')[0]
				roiids_str = [x.split(":") for x in roi.split(',')]
				if IsPy3():
					roiids = [list(map(int, i)) for i in roiids_str]
				else:
					roiids = [map(int, i) for i in roiids_str]
			else:
				roi = None
		except AttributeError or roi == None:
			msg = "Could not load ROI."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		else:
			shp = array.shape
			if roiids[0][1] > shp[0] or roiids[1][1] > shp[1] or roiids[2][1] > shp[2]:
				msg = "Impossible dimensions."
				wx.CallAfter(self.UserMessage, title, msg)
				self.pipeline_started = False
				return
			try:
				tmparray = NewArray(self,*array.shape)
			except:
				return
			from ..lib.prfftw import blanklinefill
			blanklinefill(array, tmparray, kx,ky,kz, roiids[0][0], roiids[0][1], roiids[1][0], roiids[1][1], roiids[2][0], roiids[2][1])
			del tmparray
			try:
				SaveArray(self, filename_out, array)
			except:
				msg = "Could not save array."
				wx.CallAfter(self.UserMessage, title, msg)
				self.pipeline_started = False
				return
def Sequence_Scale_Array(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Preparing scaled Numpy array...")
		filename_in = pipelineitem.input_filename.objectpath.GetValue()
		filename_out = pipelineitem.output_filename.objectpath.GetValue()
		factor = float(pipelineitem.scale.value.GetValue())
		try:
			array = LoadArray(self, filename_in)
		except:
			msg = "Could not load array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		array2 = factor*array
		try:
			SaveArray(self, filename_out, array2)
		except:
			msg = "Could not save array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
def Sequence_SumDiff_Array(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Preparing sum or difference Numpy array...")
		filename_in1 = pipelineitem.input_filename.objectpath.GetValue()
		filename_in2 = pipelineitem.input_filename1.objectpath.GetValue()
		filename_out = pipelineitem.output_filename.objectpath.GetValue()
		choice = pipelineitem.addsub.GetStringSelection()
		try:
			array1 = LoadArray(self, filename_in1)
			array2 = LoadArray(self, filename_in2)
		except:
			msg = "Could not load array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		if choice == 'Add':
			array3 = array1 + array2
		elif choice == 'Subtract':
			array3 = array1 - array2
		try:
			SaveArray(self, filename_out, array3)
		except:
			msg = "Could not save array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
def Sequence_Rotate_Support(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Preparing rotated Numpy array...")
		filename_in = pipelineitem.input_filename.objectpath.GetValue()
		filename_out = pipelineitem.output_filename.objectpath.GetValue()
		raxis = int(pipelineitem.rotationaxis.value.GetValue())
		rangle = float(pipelineitem.rotationangle.value.GetValue())
		try:
			array = LoadArray(self, filename_in)
		except:
			msg = "Could not load array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		array2 = RotateSupport(array, raxis, rangle) + 0j
		try:
			SaveArray(self, filename_out, array2)
		except:
			msg = "Could not save array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
def RotateSupport(inarray, axis, angle):
	from math import cos,sin,pi,fabs
	if fabs(angle) < 1e-3:
		return inarray
	array = numpy.abs(inarray)
	shape = array.shape
	x,y,z = array.shape
	deg2rad = pi/180.0
	tr = numpy.zeros((2,2), dtype=numpy.double)
	tr[0][0] = cos(angle*deg2rad)
	tr[0][1] = -sin(angle*deg2rad)
	tr[1][0] = sin(angle*deg2rad)
	tr[1][1] = cos(angle*deg2rad)
	coord2d= numpy.zeros((1,2), dtype=numpy.double)
	coord2dcen= numpy.zeros((1,2), dtype=numpy.double)
	newcoord2d= numpy.zeros((1,2), dtype=numpy.double)
	newarray = numpy.zeros(shape, dtype=numpy.double)
	newcoordsnn = numpy.zeros((9,2), dtype=numpy.int)
	d = numpy.zeros((9,2), dtype=numpy.double)
	nn =numpy.arange(-0.5,1.0,0.5)
	for i in range(len(nn)):
		for j in range(len(nn)):
			d[len(nn)*i+j][0], d[len(nn)*i+j][1] = nn[i], nn[j]
	axlen = shape[axis-1]
	if axis == 3:
		axx = shape[0]
		axy = shape[1]
	elif axis == 2:
		axx = shape[0]
		axy = shape[2]
	elif axis == 1:
		axx = shape[1]
		axy = shape[2]
	def RotateObject(array2dflat, newarray2d):
		for jj in numpy.where(array2dflat > 0.5)[0]:
			coord2d[0][0], coord2d[0][1] = numpy.unravel_index(jj,(axx,axy))
			coord2dcen[0][0], coord2dcen[0][1] = coord2d[0][0] - axx/2 ,  coord2d[0][1] - axy/2
			newcoord2d  = numpy.dot(coord2dcen,tr)
			for ii in range(len(nn)*len(nn)):
				newcoordsnn[ii][0], newcoordsnn[ii][1] = int(newcoord2d[0][0] + axx/2 + d[ii][0]), int(newcoord2d[0][1] + axy/2 + d[ii][1])
				newarray2d[newcoordsnn[ii][0]][newcoordsnn[ii][1]] = array2d[int(coord2d[0][0])][int(coord2d[0][1])]
	if axis == 1:
		for i in range(axlen):
			array2d = array[i,:,:]
			array2dflat = array2d.flatten()
			newarray2d = newarray[i,:,:]
			RotateObject(array2dflat, newarray2d)
	if axis == 2:
		for j in range(axlen):
			array2d = array[:,j,:]
			array2dflat = array2d.flatten()
			newarray2d = newarray[:,j,:]
			RotateObject(array2dflat, newarray2d)
	elif axis == 3:
		for k in range(axlen):
			array2d = array[:,:,k]
			array2dflat = array2d.flatten()
			newarray2d = newarray[:,:,k]
			RotateObject(array2dflat, newarray2d)
	return newarray
def Sequence_Transpose_Array(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Preparing transpose Numpy array...")
		filename_in = pipelineitem.input_filename.objectpath.GetValue()
		filename_out = pipelineitem.output_filename.objectpath.GetValue()
		try:
			array = LoadArray(self, filename_in)
		except:
			msg = "Could not load array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		array2 = array.transpose((2,1,0))
		try:
			SaveArray(self, filename_out, array2)
		except:
			msg = "Could not save array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
def Sequence_HDF_to_Numpy(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Preparing HDF to Numpy array...")
		filename_hdf = pipelineitem.input_filename.objectpath.GetValue()
		filename_npy = pipelineitem.output_filename.objectpath.GetValue()
		keypath = pipelineitem.objectpath.GetValue()
		attriberrorstring = 'Could not load HDF key item.'
		try:
			import h5py
		except ImportError:
			msg = "h5py not found."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		try:
			HDF_file = h5py.File(filename_hdf,'r')
		except:
			msg = "Could not load array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		newitem = HDF_file
		try:
			if keypath.replace(" ", "") == "":
				raise AttributeError(attriberrorstring)
			if ( '[' in keypath and ']' in keypath ):
				keypath2 = keypath.partition('[')[0]
				roi = keypath.partition('[')[-1].rpartition(']')[0]
				roiids_str = [x.split(":") for x in roi.split(',')]
				if IsPy3():
					roiids = [lsit(map(int, i)) for i in roiids_str]
				else:
					roiids = [map(int, i) for i in roiids_str]
			else:
				roi = None
				keypath2 = keypath
			splitpath = keypath2.split(",")
			for key in splitpath:
				newitem = newitem.get(key)
				if newitem == None:
					raise AttributeError(attriberrorstring)
					break
			if not any( tp in str(newitem.dtype.name) for tp in ["float", "int"]):
				raise AttributeError(attriberrorstring)
		except AttributeError:
			msg = "Could not load key."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		else:
			if roi == None:
				array = numpy.array(newitem, dtype=numpy.double) + 0j
			else:
				roiids[0][1] +=1
				roiids[1][1] +=1
				roiids[2][1] +=1
				array = numpy.array(newitem[roiids[0][0]:roiids[0][1],roiids[1][0]:roiids[1][1],roiids[2][0]:roiids[2][1]], dtype=numpy.double) + 0j
			SaveArray(self, filename_npy, array)
			HDF_file.close()
			return
def Sequence_SPE_to_Numpy(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Preparing SPE to Numpy array...")
		filename_spe = pipelineitem.input_filename.objectpath.GetValue()
		filename_npy = pipelineitem.output_filename.objectpath.GetValue()
		try:
			SPE_file=open(filename_spe,"rb")
		except:
			msg = "Could not load array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		datatype=[numpy.float32, numpy.int32, numpy.int16, numpy.uint16]
		SPE_file.seek(2) ; acc = int(numpy.fromfile(SPE_file, numpy.int16, 1))
		SPE_file.seek(4) ; exp = int(numpy.fromfile(SPE_file, numpy.int16, 1))
		if acc < 0 or (acc==1 and exp==1):
			SPE_file.seek(668) ; acc = int(numpy.fromfile(SPE_file, numpy.int32, 1))
			SPE_file.seek(660) ; exp = int(numpy.fromfile(SPE_file, numpy.int32, 1))
		SPE_file.seek(10) ; exp_sec = numpy.double(numpy.fromfile(SPE_file, numpy.float32, 1))
		SPE_file.seek(42) ; x = int(numpy.fromfile(SPE_file, numpy.int16, 1))
		SPE_file.seek(108) ; dtype_id = int(numpy.fromfile(SPE_file, numpy.int16, 1))
		SPE_file.seek(656) ; y = int(numpy.fromfile(SPE_file, numpy.int16, 1))
		SPE_file.seek(1446) ; z = int(numpy.fromfile(SPE_file, numpy.int32, 1))
		SPE_file.seek(1516) ; binx = int(numpy.fromfile(SPE_file, numpy.int16, 1))
		SPE_file.seek(1522) ; biny = int(numpy.fromfile(SPE_file, numpy.int16, 1))
		SPE_file.seek(1992) ; filever = int(numpy.fromfile(SPE_file, numpy.float32, 1))
		SPE_file.seek(1510) ; rois = int(numpy.fromfile(SPE_file, numpy.int16, 1))
		SPE_file.seek(1512) ; startx = int(numpy.fromfile(SPE_file, numpy.uint16, 1))
		SPE_file.seek(1514) ; endx = int(numpy.fromfile(SPE_file, numpy.uint16, 1))
		SPE_file.seek(1518) ; starty = int(numpy.fromfile(SPE_file, numpy.uint16, 1))
		SPE_file.seek(1520) ; endy = int(numpy.fromfile(SPE_file, numpy.uint16, 1))
		self.ancestor.GetPage(0).queue_info.put("Size in x: %d" %x)
		self.ancestor.GetPage(0).queue_info.put("Size in y: %d" %y)
		self.ancestor.GetPage(0).queue_info.put("Size in z: %d" %z)
		self.ancestor.GetPage(0).queue_info.put("binning in x: %d" %binx)
		self.ancestor.GetPage(0).queue_info.put("binning in y: %d" %biny)
		self.ancestor.GetPage(0).queue_info.put( "ROI's: %d" %rois)
		self.ancestor.GetPage(0).queue_info.put( "ROI Start x: %d" %startx)
		self.ancestor.GetPage(0).queue_info.put( "ROI End x: %d" %endx)
		self.ancestor.GetPage(0).queue_info.put( "ROI Start y: %d" %starty)
		self.ancestor.GetPage(0).queue_info.put( "ROI End y: %d" %endy)
		self.ancestor.GetPage(0).queue_info.put("Data type: %d" %dtype_id)
		self.ancestor.GetPage(0).queue_info.put( "Accumulations: %d" %acc )
		self.ancestor.GetPage(0).queue_info.put( "File Version: %f" %filever )
		if not exp==0:
			self.ancestor.GetPage(0).queue_info.put("Exposure time: %d (ms)" %exp)
		self.ancestor.GetPage(0).queue_info.put("Alternative exposure time: %f (s)" %exp_sec )
		datasize = numpy.dtype(datatype[dtype_id]).itemsize #bytes
		if z > 0:
			try:
				array = NewArray(self, x, y, z)
			except:
				return
			seekpoint = 4100
			for iz in range(z):
				for iy in range(y):
					SPE_file.seek(seekpoint)
					array[:, iy, iz] = numpy.cdouble( numpy.fromfile( SPE_file, datatype[dtype_id], x ) )
					seekpoint += x*datasize
		else:
			try:
				array = NewArray(self, x, y, 1)
				arraytemp = NewArray(self, x, y, 1)
			except:
				return
			SPE_file.seek(0, os.SEEK_END)
			size = SPE_file.tell()
			seekpoint = 4100
			SPE_file.seek(seekpoint)
			iz = 0
			for iy in range(y):
				array[:, iy, iz] = numpy.cdouble( numpy.fromfile( SPE_file, datatype[dtype_id], x ) )
				seekpoint += x*datasize
				SPE_file.seek(seekpoint)
			while seekpoint < size:
				for iy in range(y):
					arraytemp[:, iy, iz] = numpy.cdouble( numpy.fromfile( SPE_file, datatype[dtype_id], x ) )
					seekpoint += x*datasize
					SPE_file.seek(seekpoint)
				array = numpy.concatenate((array, arraytemp),axis=2)
		SaveArray(self, filename_npy, array)
		SPE_file.close()
		return
class TIFFStackRead():
	def __init__(self,imgfile):
		self.im  = imgfile
		self.im.seek(0)
		self.im_sz = [self.im.tag[0x101][0],
					  self.im.tag[0x100][0]]
		self.cur = self.im.tell()
		j = 0
		while True:
			try:
				j = j+1
				self.im.seek(j)
			except EOFError:
				break
		self.nframes = j
	def get_frame(self,j):
		try:
			self.im.seek(j)
		except EOFError:
			return None
		self.cur = self.im.tell()
		return numpy.reshape(self.im.getdata().convert('L'),self.im_sz)
	def __iter__(self):
		self.im.seek(0)
		self.old = self.cur
		self.cur = self.im.tell()
		return self
	def next(self):
		try:
			self.im.seek(self.cur)
			self.cur = self.im.tell()+1
		except EOFError:
			self.im.seek(self.old)
			self.cur = self.im.tell()
			raise StopIteration
		return numpy.reshape(self.im.getdata().convert('L'),self.im_sz)
def Sequence_Image_to_Numpy(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Preparing Image to Numpy array...")
		filename_Image = pipelineitem.input_filename.objectpath.GetValue()
		filename_npy = pipelineitem.output_filename.objectpath.GetValue()
		from PIL import Image
		try:
			with open(filename_Image, 'rb') as Image_handle:
				Image_file_raw=Image.open(Image_handle)
				type = Image_file_raw.format
				if type == 'TIFF':
					imgobj = TIFFStackRead(Image_file_raw)
					x,y = imgobj.im_sz
					z = imgobj.nframes
					array = NewArray(self,x,y,z)
					for i in range(z):
						array[:,:,i] = imgobj.get_frame(i)[:]
				else:
					Image_file=Image_file_raw.convert('L')
					array = numpy.array(Image_file)
		except:
			msg = "Could not load array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		else:
			SaveArray(self, filename_npy, array)
		return
def Sequence_Array_to_Memory(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Preparing array in memory...")
		filename_in = pipelineitem.input_filename.objectpath.GetValue()
		filename_out = pipelineitem.output_filename.objectpath.GetValue()
		try:
			array = LoadArray(self, filename_in)
		except:
			msg = "Could not load array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		try:
			SaveArray(self, filename_out, array)
		except:
			msg = "Could not save array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
def Sequence_Memory_to_Array(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Saving array in memory...")
		filename_in = pipelineitem.input_filename.objectpath.GetValue()
		filename_out = pipelineitem.output_filename.objectpath.GetValue()
		try:
			array = LoadArray(self, filename_in)
		except:
			msg = "Could not load array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		try:
			SaveArray(self, filename_out, array)
		except:
			msg = "Could not save array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
def Sequence_Load_PSF(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Preparing PSF in memory...")
		filename_in = pipelineitem.input_filename.objectpath.GetValue()
		try:
			array = LoadArray(self, filename_in)
		except:
			msg = "Could not load array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		try:
			self.psf = array
			self.ancestor.GetPage(0).queue_info.put("done.")
		except:
			msg = "Could not save array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
def Sequence_Save_PSF(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Saving PSF data...")
		filename_out = pipelineitem.output_filename.objectpath.GetValue()
		try:
			SaveArray(self, filename_out,self.psf)
		except:
			msg = "Could not save array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
def Sequence_Mask(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Preparing mask array...")
		filename_in = pipelineitem.input_filename.objectpath.GetValue()
		filename_out = pipelineitem.output_filename.objectpath.GetValue()
		frac_max =  float(pipelineitem.max.value.GetValue())
		frac_min =  float(pipelineitem.min.value.GetValue())
		try:
				array = LoadArray(self, filename_in)
		except:
			msg = "Could not load array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		else:
			mask = numpy.asarray(array, dtype=numpy.cdouble, order='C')
			from ..lib.prfftw import rangereplace
			rangereplace(mask, frac_min, frac_max, 0.0, 1.0)
			try:
				SaveArray(self, filename_out,mask)
			except:
				msg = "Could not save array."
				wx.CallAfter(self.UserMessage, title, msg)
				self.pipeline_started = False
				return
def Sequence_Bin(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Preparing bin array...")
		binx =  int(pipelineitem.bdims[0].value.GetValue())
		biny =  int(pipelineitem.bdims[1].value.GetValue())
		binz =  int(pipelineitem.bdims[2].value.GetValue())
		filename_in = pipelineitem.input_filename.objectpath.GetValue()
		filename_out = pipelineitem.output_filename.objectpath.GetValue()
		try:
			array = LoadArray(self, filename_in)
		except:
			msg = "Could not load array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		shp = array.shape
		if (binx) > shp[0] or (biny) > shp[1] or (binz) > shp[2]:
			msg = "Impossible bin dimensions."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		else:
			nx = (shp[0]+binx -1)//binx
			ny = (shp[1]+biny -1)//biny
			nz = (shp[2]+binz -1)//binz
			nshp = numpy.array((nx, ny, nz),dtype=numpy.int)
			try:
				arraybin = NewArray(self,nx,ny,nz)
			except:
				return
			for k in range(binz):
				for j in range(biny):
					for i in range(binx):
						subshp = array[i::binx,j::biny,k::binz].shape
						arraybin[(nx-subshp[0]):nx,(ny-subshp[1]):ny,(nz-subshp[2]):nz] += array[i::binx,j::biny,k::binz]
			SaveArray(self, filename_out,arraybin)
def Sequence_AutoCentre(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Preparing auto centered array...")
		filename_in = pipelineitem.input_filename.objectpath.GetValue()
		filename_out = pipelineitem.output_filename.objectpath.GetValue()
		try:
			array = LoadArray(self, filename_in)
		except:
			msg = "Could not load array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		max = numpy.array( numpy.unravel_index(array.argmax(), array.shape) )
		shp = numpy.array(array.shape)
		centre = numpy.array(array.shape) // 2
		padding = (max - centre)
		extra = numpy.abs(padding)
		try:
			arraycentred = NewArray(self,*(shp+ 2*extra))
		except:
			return
		centre2 = numpy.array(arraycentred.shape) // 2
		x_0 = extra[0] - padding[0]
		x_1 = x_0 + shp[0]
		y_0 = extra[1] - padding[1]
		y_1 = y_0 + shp[1]
		z_0 = extra[2] - padding[2]
		z_1 = z_0 + shp[2]
		arraycentred[x_0:x_1,y_0:y_1,z_0:z_1] = array
		SaveArray(self, filename_out, arraycentred)
def Sequence_Wrap(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Preparing wrapped array...")
		filename_in = pipelineitem.input_filename.objectpath.GetValue()
		filename_out = pipelineitem.output_filename.objectpath.GetValue()
		direction = pipelineitem.rbdirection.GetStringSelection()
		try:
			array = LoadArray(self, filename_in)
		except:
			msg = "Could not load array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		if direction == "Forward":
			arrayfinal = WrapArray(array)
		else:
			arrayfinal = WrapArray(array, direction=-1)
		SaveArray(self, filename_out, arrayfinal)
def Sequence_Median_Filter(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Preparing median filtered array...")
		filename_in = pipelineitem.input_filename.objectpath.GetValue()
		filename_out = pipelineitem.output_filename.objectpath.GetValue()
		kx =  int(pipelineitem.kdims[0].value.GetValue())
		ky =  int(pipelineitem.kdims[1].value.GetValue())
		kz =  int(pipelineitem.kdims[2].value.GetValue())
		maxdev =  float(pipelineitem.maxdev.value.GetValue())
		try:
				array = LoadArray(self, filename_in)
		except:
			msg = "Could not load array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		else:
			try:
				tmparray = NewArray(self,*array.shape)
			except:
				return
			from ..lib.prfftw import medianfilter
			medianfilter(array, tmparray, kx,ky,kz, maxdev)
			try:
				SaveArray(self, filename_out, array)
			except:
				msg = "Could not save array."
				wx.CallAfter(self.UserMessage, title, msg)
				self.pipeline_started = False
				return
def Sequence_GaussianFill(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Preparing Gaussian distribution array...")
		filename_in = pipelineitem.input_filename.objectpath.GetValue()
		filename_out = pipelineitem.output_filename.objectpath.GetValue()
		sigma =  float(pipelineitem.sigma.value.GetValue())
		try:
				array = LoadArray(self, filename_in)
		except:
			msg = "Could not load array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		else:
			from ..lib.prfftw import gaussian_fill
			gaussian_fill(array, sigma)
			try:
				SaveArray(self, filename_out, array)
			except:
				msg = "Could not save array."
				wx.CallAfter(self.UserMessage, title, msg)
				self.pipeline_started = False
				return
def Sequence_FFT(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Preparing Fourier transformed array...")
		filename_in = pipelineitem.input_filename.objectpath.GetValue()
		filename_out = pipelineitem.output_filename.objectpath.GetValue()
		direction = pipelineitem.rbdirection.GetStringSelection()
		try:
			array = LoadArray(self, filename_in)
		except:
			msg = "Could not load array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		else:
			from ..lib.prfftw import fft
			from ..lib.prfftw import wrap
			if direction == "Fourier Space":
				wrap(array, 1)
				fft(array, 1)
				wrap(array, -1)
			else:
				wrap(array, 1)
				fft(array, -1)
				wrap(array, -1)
			try:
				SaveArray(self, filename_out, array)
			except:
				msg = "Could not save array."
				wx.CallAfter(self.UserMessage, title, msg)
				self.pipeline_started = False
				return
def Sequence_Convolve(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Preparing convolved array...")
		filename_in1 = pipelineitem.input_filename1.objectpath.GetValue()
		filename_in2 = pipelineitem.input_filename2.objectpath.GetValue()
		filename_out = pipelineitem.output_filename.objectpath.GetValue()
		try:
			array1 = LoadArray(self, filename_in1)
			array2 = LoadArray(self, filename_in2)
		except:
			msg = "Could not load array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		else:
			if array1.shape != array2.shape:
				msg = "Array dimensions are inconsistent."
				wx.CallAfter(self.UserMessage, title, msg)
				self.pipeline_started = False
				return
			from ..lib.prfftw import convolve
			from ..lib.prfftw import wrap
			wrap(array1, 1)
			wrap(array2, 1)
			convolve(array1, array2)
			wrap(array1, -1)
			wrap(array2, -1)
			try:
				SaveArray(self, filename_out, array1)
			except:
				msg = "Could not save array."
				wx.CallAfter(self.UserMessage, title, msg)
				self.pipeline_started = False
				return
def Sequence_Conjugate_Reflect(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Preparing conjugated and reflected array...")
		filename_in = pipelineitem.input_filename.objectpath.GetValue()
		filename_out = pipelineitem.output_filename.objectpath.GetValue()
		try:
			array = LoadArray(self, filename_in)
		except:
			msg = "Could not load array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		else:
			from ..lib.prfftw import conj_reflect
			conj_reflect(array)
			try:
				SaveArray(self, filename_out, array)
			except:
				msg = "Could not save array."
				wx.CallAfter(self.UserMessage, title, msg)
				self.pipeline_started = False
				return
def Sequence_Threshold(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Preparing threshold array...")
		filename_in = pipelineitem.input_filename.objectpath.GetValue()
		filename_out = pipelineitem.output_filename.objectpath.GetValue()
		frac_max =  float(pipelineitem.max.value.GetValue())
		frac_min =  float(pipelineitem.min.value.GetValue())
		try:
				array = LoadArray(self, filename_in)
		except:
			msg = "Could not load array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		else:
			from ..lib.prfftw import threshold
			threshold(array, frac_min, frac_max, 0.0)
			array[numpy.isnan(array)] = 0 + 0j
			try:
				SaveArray(self, filename_out, array)
			except:
				msg = "Could not save array."
				wx.CallAfter(self.UserMessage, title, msg)
				self.pipeline_started = False
				return
def Sequence_Voxel_Replace(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Preparing voxel replace array...")
		sx =  int(pipelineitem.sdims[0].value.GetValue())
		sy =  int(pipelineitem.sdims[1].value.GetValue())
		sz =  int(pipelineitem.sdims[2].value.GetValue())
		ex =  int(pipelineitem.edims[0].value.GetValue())
		ey =  int(pipelineitem.edims[1].value.GetValue())
		ez =  int(pipelineitem.edims[2].value.GetValue())
		real =  float(pipelineitem.real.value.GetValue())
		imag =  float(pipelineitem.imag.value.GetValue())
		filename_in = pipelineitem.input_filename.objectpath.GetValue()
		filename_out = pipelineitem.output_filename.objectpath.GetValue()
		try:
			array = LoadArray(self, filename_in)
		except:
			msg = "Could not load array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		shp = array.shape
		if ex < sx or ey < sy or ez < sz or ex > shp[0] or ey > shp[1] or ez > shp[2]:
			msg = "Impossible dimensions."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		else:
			array[sx:ex,sy:ey,sz:ez] = real + 1j * imag
			SaveArray(self, filename_out,array)
def Sequence_Crop_Pad(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Preparing cropped array...")
		csx =  int(pipelineitem.csdims[0].value.GetValue())
		csy =  int(pipelineitem.csdims[1].value.GetValue())
		csz =  int(pipelineitem.csdims[2].value.GetValue())
		cex =  int(pipelineitem.cedims[0].value.GetValue())
		cey =  int(pipelineitem.cedims[1].value.GetValue())
		cez =  int(pipelineitem.cedims[2].value.GetValue())
		psx =  int(pipelineitem.psdims[0].value.GetValue())
		psy =  int(pipelineitem.psdims[1].value.GetValue())
		psz =  int(pipelineitem.psdims[2].value.GetValue())
		pex =  int(pipelineitem.pedims[0].value.GetValue())
		pey =  int(pipelineitem.pedims[1].value.GetValue())
		pez =  int(pipelineitem.pedims[2].value.GetValue())
		filename_in = pipelineitem.input_filename.objectpath.GetValue()
		filename_out = pipelineitem.output_filename.objectpath.GetValue()
		try:
			array = LoadArray(self, filename_in)
		except:
			msg = "Could not load array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		shp = array.shape
		if (csx+cex) > shp[0] or (csy+cey) > shp[1] or (csz+cez) > shp[2]:
			msg = "Impossible crop dimensions."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		else:
			array = array[csx:(shp[0]-cex),csy:(shp[1]-cey),csz:(shp[2]-cez)]
			shp =  array.shape
			array = numpy.concatenate((numpy.zeros((psx,shp[1],shp[2]),dtype=numpy.cdouble, order='C'), array),axis=0) #x axis
			array = numpy.concatenate((array, numpy.zeros((pex,shp[1],shp[2]),dtype=numpy.cdouble, order='C')),axis=0) #x axis
			shp =  array.shape
			array = numpy.concatenate((numpy.zeros((shp[0],psy,shp[2]),dtype=numpy.cdouble, order='C'), array),axis=1) #y axis
			array = numpy.concatenate((array, numpy.zeros((shp[0],pey,shp[2]),dtype=numpy.cdouble, order='C')),axis=1) #y axis
			shp =  array.shape
			array = numpy.concatenate((numpy.zeros((shp[0],shp[1],psz),dtype=numpy.cdouble, order='C'), array),axis=2) #z axis
			array = numpy.concatenate((array, numpy.zeros((shp[0],shp[1],pez),dtype=numpy.cdouble, order='C')),axis=2) #z axis
			array = numpy.asarray(array, dtype=numpy.cdouble, order='C')
			SaveArray(self, filename_out,array)
def Sequence_CentredResize(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Preparing centered array...")
		x =  int(pipelineitem.dims[0].value.GetValue())
		y =  int(pipelineitem.dims[1].value.GetValue())
		z =  int(pipelineitem.dims[2].value.GetValue())
		filename_in = pipelineitem.input_filename.objectpath.GetValue()
		filename_out = pipelineitem.output_filename.objectpath.GetValue()
		try:
			array = LoadArray(self, filename_in)
		except:
			msg = "Could not load array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		shp = array.shape
		if x < 1 or y < 1 or z < 1:
			msg = "Impossible resize dimensions."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		else:
			try:
				arraycentred = NewArray(self,x,y,z)
			except:
				return
			max = numpy.array( numpy.unravel_index(array.argmax(), array.shape) )
			shp = numpy.array(array.shape)
			shpnew = numpy.array([x,y,z])
			idx_ns = (shpnew // 2)  - max
			idx_ne = shp + (shpnew // 2)  - max
			idx_s = numpy.array([0,0,0])
			idx_e = numpy.array(array.shape)
			mask = idx_ns < 0
			idx_ns[mask] = 0
			idx_s[mask] = max[mask] - (shpnew[mask] // 2)
			mask = idx_ne > shpnew
			idx_ne[mask] = shpnew[mask]
			idx_e[mask] = max[mask] + (shpnew[mask] // 2)
			arraycentred[idx_ns[0]:idx_ne[0],idx_ns[1]:idx_ne[1],idx_ns[2]:idx_ne[2]] = array[idx_s[0]:idx_e[0],idx_s[1]:idx_e[1],idx_s[2]:idx_e[2]]
			SaveArray(self, filename_out, arraycentred)
def Sequence_Cuboid_Support(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Preparing cuboid support array...")
		sx =  int(pipelineitem.sdims[0].value.GetValue())
		sy =  int(pipelineitem.sdims[1].value.GetValue())
		sz =  int(pipelineitem.sdims[2].value.GetValue())
		x =  int(pipelineitem.dims[0].value.GetValue())
		y =  int(pipelineitem.dims[1].value.GetValue())
		z =  int(pipelineitem.dims[2].value.GetValue())
		fname = pipelineitem.filename.objectpath.GetValue()
		fromfile = pipelineitem.fromfile.objectpath.GetValue()
		if fromfile == "" and (sx> x or sy > y or sz > z):
			msg = "Invalid support dimensions."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		else:
			if fromfile != "":
				fromarray = LoadArray(self, fromfile)
				support = numpy.asarray(fromarray, dtype=numpy.cdouble, order='C')
				x,y,z = numpy.asarray( support.shape, numpy.int)
				if (sx> x or sy > y or sz > z):
					msg = "Invalid support dimensions."
					wx.CallAfter(self.UserMessage, title, msg)
					self.pipeline_started = False
					return
		try:
			support = NewArray(self,x,y,z)
		except:
			return
		x1 = (x - sx)//2;
		x2 = x1 + sx
		y1 = (y - sy)//2
		y2 = y1 + sy
		z1 = (z - sz)//2
		z2 = z1 + sz
		support[x1:x2,y1:y2,z1:z2] = 1 + 1j*0
		try:
			SaveArray(self, fname,support)
		except:
			msg = "Could not save array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
def Sequence_Save_Sequence(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Saving sequence data...")
		filename_out = pipelineitem.output_filename.objectpath.GetValue()
		try:
			SaveArray(self, filename_out,self.seqdata)
		except:
			msg = "Could not save array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
def Sequence_Save_Support(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Saving support data...")
		filename_out = pipelineitem.output_filename.objectpath.GetValue()
		try:
			SaveArray(self, filename_out,self.support)
		except:
			msg = "Could not save array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
def Sequence_Save_Residual(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Saving residual data...")
		filename_out = pipelineitem.output_filename.objectpath.GetValue()
		try:
			data_length = self.citer_flow[0]
			x = numpy.arange(data_length)
			y = self.residual[:data_length]
			xy = numpy.vstack((x,y)).T
			numpy.savetxt(filename_out, xy, delimiter=',')
		except:
			msg = "Could not save array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
def Sequence_ArraytoVTK(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		panelvisual = self.ancestor.GetPage(1)
		self.ancestor.GetPage(0).queue_info.put("Saving VTK array...")
		data_file  = pipelineitem.input_filename.objectpath.GetValue()
		output_filename = pipelineitem.output_filename.objectpath.GetValue()
		try:
			data = LoadArray(self, data_file)
			if (pipelineitem.rbampphase.GetStringSelection() == 'Amplitude'):
				flat_data = (numpy.abs(data)).transpose(2,1,0).flatten();
			elif (pipelineitem.rbampphase.GetStringSelection() == 'Phase'):
				flat_data = (numpy.angle(data)).transpose(2,1,0).flatten();
			vtk_data_array = numpy_support.numpy_to_vtk(flat_data)
			image = vtk.vtkImageData()
			points = image.GetPointData()
			points.SetScalars(vtk_data_array)
			image.SetDimensions(data.shape)
			image.ComputeBounds()
			image.Modified()
			writer = vtk.vtkDataSetWriter()
			writer.SetFileName(output_filename)
			writer.SetFileType(1) #ASCII
			if panelvisual.VTKIsNot6:
				writer.SetInput(image)
			else:
				writer.SetInputData(image)
			writer.Write()
		except:
			msg = "Could not save VTK array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
def Sequence_ObjecttoVTK(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		panelvisual = self.ancestor.GetPage(1)
		self.ancestor.GetPage(0).queue_info.put("Saving VTK object...")
		data_file  = pipelineitem.input_filename.objectpath.GetValue()
		output_filename = pipelineitem.output_filename.objectpath.GetValue()
		coords_filename = pipelineitem.coords_filename.objectpath.GetValue()
		try:
			data = LoadArray(self, data_file)
			coords = LoadCoordsArray(self, coords_filename)
			if (pipelineitem.rbampphase.GetStringSelection() == 'Amplitude'):
				flat_data = (numpy.abs(data)).transpose(2,1,0).flatten();
			elif (pipelineitem.rbampphase.GetStringSelection() == 'Phase'):
				flat_data = (numpy.angle(data)).transpose(2,1,0).flatten();
			vtk_data_array = numpy_support.numpy_to_vtk(flat_data)
			vtk_coordarray = numpy_support.numpy_to_vtk(coords)
			image = vtk.vtkStructuredGrid()
			vtk_points = vtk.vtkPoints()
			vtk_points.SetDataTypeToDouble()
			vtk_points.SetNumberOfPoints(data.size)
			vtk_points.SetData(vtk_coordarray)
			image.SetPoints(vtk_points)
			image.GetPointData().SetScalars(vtk_data_array)
			image.SetDimensions(data.shape)
			image.Modified()
			writer = vtk.vtkDataSetWriter()
			writer.SetFileName(output_filename)
			writer.SetFileType(1) #ASCII
			if panelvisual.VTKIsNot6:
				writer.SetInput(image)
			else:
				writer.SetInputData(image)
			writer.Write()
		except:
			msg = "Could not save VTK array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
def InterpolatedScalarDataset(InputDataSet, grid, range):
	def TPObserver(obj, event):
		pass
	bounds=list(InputDataSet.GetBounds())
	RegGrid=vtk.vtkShepardMethod()
	RegGrid.SetMaximumDistance(range)
	RegGrid.SetSampleDimensions(grid)
	RegGrid.SetModelBounds(bounds)
	if IsNotVTK6():
		RegGrid.SetInput(InputDataSet)
	else:
		tp = vtk.vtkTrivialProducer()
		tp.SetOutput(InputDataSet)
		tp.SetWholeExtent(InputDataSet.GetExtent())
		tp.AddObserver(vtk.vtkCommand.ErrorEvent, TPObserver)
		RegGrid.SetInputConnection(tp.GetOutputPort())
	RegGrid.GetInputInformation().Set(vtk.vtkStreamingDemandDrivenPipeline.UNRESTRICTED_UPDATE_EXTENT(),1)
	RegGrid.Update()
	return RegGrid.GetOutput()
def Sequence_InterpolateObject(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		self.thread_register.put(1)
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Interpolating object...")
		input_filename  = pipelineitem.input_filename.objectpath.GetValue()
		output_filename = pipelineitem.output_filename.objectpath.GetValue()
		coords_filename = pipelineitem.coords_filename.objectpath.GetValue()
		x =  int(pipelineitem.spacer[0].value.GetValue())
		y =  int(pipelineitem.spacer[1].value.GetValue())
		z =  int(pipelineitem.spacer[2].value.GetValue())
		range =  float(pipelineitem.interp_range.value.GetValue())
		def Interpolate(self):
			shp = numpy.array(data.shape, dtype=numpy.int)
			vtk_coordarray = numpy_support.numpy_to_vtk(coords)
			vtk_points = vtk.vtkPoints()
			vtk_points.SetDataTypeToDouble()
			vtk_points.SetNumberOfPoints(data.size)
			vtk_points.SetData(vtk_coordarray)
			flat_data_amp = (numpy.abs(data)).transpose(2,1,0).flatten()
			vtk_data_array_amp = numpy_support.numpy_to_vtk(flat_data_amp)
			image_amp = vtk.vtkStructuredGrid()
			image_amp.SetPoints(vtk_points)
			image_amp.GetPointData().SetScalars(vtk_data_array_amp)
			image_amp.SetDimensions(shp)
			image_amp.Modified()
			flat_data_phase = (numpy.angle(data)).transpose(2,1,0).flatten()
			vtk_data_array_phase = numpy_support.numpy_to_vtk(flat_data_phase)
			image_phase = vtk.vtkStructuredGrid()
			image_phase.SetPoints(vtk_points)
			image_phase.GetPointData().SetScalars(vtk_data_array_phase)
			image_phase.SetDimensions(shp)
			image_phase.Modified()
			bds = list(image_amp.GetBounds())
			scale = [(bds[1] - bds[0])/float(x), (bds[3] - bds[2])/float(y), (bds[5] - bds[4])/float(z)]
			self.ancestor.GetPage(0).queue_info.put("Array (x,y,z) spacing: " + str(scale))
			interp_image_amp = InterpolatedScalarDataset(image_amp, [x,y,z] , range)
			interp_image_phase = InterpolatedScalarDataset(image_phase, [x,y,z] , range)
			dims = interp_image_amp.GetDimensions()
			array_amp_flat = numpy_support.vtk_to_numpy(interp_image_amp.GetPointData().GetScalars())
			array_amp = numpy.reshape(array_amp_flat, dims[::-1]).transpose(2,1,0)
			array_phase_flat = numpy_support.vtk_to_numpy(interp_image_phase.GetPointData().GetScalars())
			array_phase = numpy.reshape(array_phase_flat, dims[::-1]).transpose(2,1,0)
			array = array_amp * (numpy.cos(array_phase) + 1j * numpy.sin(array_phase))
			try:
				SaveArray(self, output_filename,array)
			except:
				msg = "Could not save array."
				wx.CallAfter(self.UserMessage, title, msg)
				self.pipeline_started = False
			self.thread_register.get()
		try:
			test_array = numpy.zeros([x,y,z], dtype=numpy.float)
		except:
			msg = "Array dimensions are too large for the available memory."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			self.thread_register.get()
			return
		else:
			del test_array
		try:
			data = LoadArray(self, input_filename)
			coords = LoadCoordsArray(self, coords_filename)
		except:
			msg = "Could not load array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			self.thread_register.get()
			return
		else:
			thd = threading.Thread(target=Interpolate, args=(self,))
			thd.daemon = True
			thd.start()
			return
def Sequence_View_Array(self, ancestor):
	def ViewDataAmp(self, ancestor, data, r, g, b):
		self.ancestor.GetPage(0).queue_info.put("Preparing array visualisation...")
		self.ancestor.GetPage(0).queue_info.put("Array Size: " + str(data.shape))
		max = numpy.array( numpy.unravel_index(data.argmax(), data.shape) )
		self.ancestor.GetPage(0).queue_info.put("Array Maximum Coordinates: " + str(max))
		self.ancestor.GetPage(0).queue_info.put("Array Maximum: %1.6e" %(numpy.abs(data[max[0]][max[1]][max[2]])))
		panelvisual = ancestor.GetPage(1)
		contour = float(self.contour.value.GetValue())
		maxval = numpy.abs(data).max()
		if contour > maxval: contour = CNTR_CLIP*maxval;
		feature_angle = float(self.feature_angle.value.GetValue())
		sx = float(self.sx.value.GetValue())
		sy = float(self.sy.value.GetValue())
		sz = float(self.sz.value.GetValue())
		panelvisual.flat_data= (numpy.abs(data)).transpose(2,1,0).flatten();
		panelvisual.vtk_data_array = numpy_support.numpy_to_vtk(panelvisual.flat_data)
		points = panelvisual.image_amp_real.GetPointData()
		points.SetScalars(panelvisual.vtk_data_array)
		panelvisual.image_amp_real.SetDimensions(data.shape)
		panelvisual.image_amp_real.SetSpacing(sx,sy,sz)
		panelvisual.image_amp_real.ComputeBounds()
		panelvisual.image_amp_real.Modified()
		panelvisual.image_probe = panelvisual.image_amp_real
		panelvisual.lut_amp_real.SetNumberOfTableValues(256)
		panelvisual.lut_amp_real.SetScaleToLinear()
		panelvisual.lut_amp_real.SetTableRange(panelvisual.image_amp_real.GetPointData().GetScalars().GetRange())
		lutsource = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[0][0]][1]
		if self.ancestor.GetPage(0).cmls[0][1] == 0:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(255-k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		panelvisual.lut_amp_real.SetRamp(0)
		panelvisual.lut_amp_real.Build()
		panelvisual.scalebar_amp_real.SetTitle("")
		panelvisual.scalebar_amp_real.SetOrientationToVertical()
		panelvisual.scalebar_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		panelvisual.scalebar_amp_real.SetWidth(0.07)
		panelvisual.scalebar_amp_real.SetHeight(0.90)
		panelvisual.scalebar_amp_real.SetPosition(0.01,0.1)
		panelvisual.scalebar_amp_real.Modified()
		if panelvisual.VTKIsNot6:
			panelvisual.filter_amp_real.SetInput(panelvisual.image_amp_real)
		else:
			panelvisual.filter_amp_real.SetInputData(panelvisual.image_amp_real)
		panelvisual.filter_amp_real.ComputeNormalsOn()
		panelvisual.filter_amp_real.ComputeScalarsOn()
		panelvisual.filter_amp_real.SetNumberOfContours(1)
		panelvisual.filter_amp_real.SetValue( 0, contour)
		panelvisual.filter_amp_real.Modified()
		panelvisual.filter_amp_real.Update()
		panelvisual.smooth_filter_real.SetInputConnection(panelvisual.filter_amp_real.GetOutputPort())
		panelvisual.smooth_filter_real.SetNumberOfIterations(15)
		panelvisual.smooth_filter_real.SetRelaxationFactor(0.1)
		panelvisual.smooth_filter_real.FeatureEdgeSmoothingOff()
		panelvisual.smooth_filter_real.BoundarySmoothingOn()
		panelvisual.smooth_filter_real.Update()
		panelvisual.normals_amp_real.SetInputConnection(panelvisual.smooth_filter_real.GetOutputPort())
		panelvisual.normals_amp_real.SetFeatureAngle(feature_angle)
		panelvisual.normals_amp_real.ConsistencyOff()
		panelvisual.normals_amp_real.SplittingOff()
		panelvisual.normals_amp_real.AutoOrientNormalsOff()
		panelvisual.normals_amp_real.ComputePointNormalsOn()
		panelvisual.normals_amp_real.ComputeCellNormalsOff()
		panelvisual.normals_amp_real.NonManifoldTraversalOff()
		panelvisual.triangles_amp_real.SetInputConnection(panelvisual.normals_amp_real.GetOutputPort())
		panelvisual.strips_amp_real.SetInputConnection(panelvisual.triangles_amp_real.GetOutputPort())
		panelvisual.mapper_amp_real.SetInputConnection(panelvisual.strips_amp_real.GetOutputPort())
		panelvisual.mapper_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		panelvisual.mapper_amp_real.SetScalarRange(panelvisual.image_amp_real.GetPointData().GetScalars().GetRange())
		panelvisual.mapper_amp_real.SetScalarModeToUsePointData()
		panelvisual.mapper_amp_real.ImmediateModeRenderingOn()
		panelvisual.mapper_amp_real.Modified()
		panelvisual.mapper_amp_real.Update()
		panelvisual.actor_amp_real.GetProperty().SetOpacity(1.0)
		panelvisual.actor_amp_real.SetMapper(panelvisual.mapper_amp_real)
		panelvisual.SetPicker()
		panelvisual.renderer_amp_real.RemoveAllViewProps()
		panelvisual.renderer_phase_real.RemoveAllViewProps()
		panelvisual.renderer_amp_recip.RemoveAllViewProps()
		panelvisual.renderer_phase_recip.RemoveAllViewProps()
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_recip)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_recip)
		panelvisual.renWin.GetRenderWindow().Modified()
		panelvisual.renderer_amp_real.AddActor(panelvisual.actor_amp_real)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.scalebar_amp_real)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.textActor)
		panelvisual.renderer_amp_real.SetBackground(r, g, b)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().SetMultiSamples(0)
		panelvisual.renWin.SetInteractorStyle(panelvisual.style3D)
		panelvisual.renderer_amp_real.ResetCamera()
		panelvisual.renWin.SetPicker(panelvisual.picker_amp_real)
		panelvisual.renderer_amp_real.SetViewport(0,0,1,1)
		panelvisual.renderer_amp_recip.SetViewport(1,1,1,1)
		panelvisual.Layout()
		panelvisual.Show()
		if(self.chkbox_axes.GetValue() == True):
			panelvisual.axis.SetBounds(panelvisual.image_amp_real.GetBounds())
			if panelvisual.VTKIsNot6:
				panelvisual.axis.SetInput(panelvisual.image_amp_real)
			else:
				panelvisual.axis.SetInputData(panelvisual.image_amp_real)
			panelvisual.axis.SetCamera(panelvisual.renderer_amp_real.GetActiveCamera())
			panelvisual.axis.SetLabelFormat("%6.1f")
			panelvisual.axis.SetFlyModeToOuterEdges()
			panelvisual.axis.ScalingOff()
			panelvisual.axis.SetFontFactor(float(self.axes_fontfactor.value.GetValue()))
			panelvisual.axis.SetXLabel("X")
			panelvisual.axis.SetYLabel("Y")
			panelvisual.axis.SetZLabel("Z")
			panelvisual.axis.Modified()
			panelvisual.renderer_amp_real.AddViewProp( panelvisual.axis )
	def ViewDataPhase(self, ancestor, data, r, g, b):
		self.ancestor.GetPage(0).queue_info.put("Preparing array visualisation")
		self.ancestor.GetPage(0).queue_info.put("Array Size: " + str(data.shape))
		panelvisual = ancestor.GetPage(1)
		phasemax = float(self.phasemax.value.GetValue())
		phasemin = float(self.phasemin.value.GetValue())
		ox = float(self.ox.value.GetValue())
		oy = float(self.oy.value.GetValue())
		oz = float(self.oz.value.GetValue())
		nx = float(self.nx.value.GetValue())
		ny = float(self.ny.value.GetValue())
		nz = float(self.nz.value.GetValue())
		sx = float(self.sx.value.GetValue())
		sy = float(self.sy.value.GetValue())
		sz = float(self.sz.value.GetValue())
		panelvisual.flat_data= (numpy.angle(data)).transpose(2,1,0).flatten();
		panelvisual.vtk_data_array = numpy_support.numpy_to_vtk(panelvisual.flat_data)
		points = panelvisual.image_phase_real.GetPointData()
		points.SetScalars(panelvisual.vtk_data_array)
		panelvisual.image_phase_real.SetDimensions(data.shape)
		panelvisual.image_phase_real.SetSpacing(sx,sy,sz)
		panelvisual.image_phase_real.ComputeBounds()
		panelvisual.image_phase_real.Modified()
		panelvisual.image_probe = panelvisual.image_phase_real
		panelvisual.lut_phase_real.SetNumberOfTableValues(256)
		panelvisual.lut_phase_real.SetScaleToLinear()
		panelvisual.lut_phase_real.SetTableRange([phasemin,phasemax])
		lutsource = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[1][0]][1]
		if self.ancestor.GetPage(0).cmls[1][1] == 0:
			for k in range(256):
				panelvisual.lut_phase_real.SetTableValue(k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_phase_real.SetTableValue(255-k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		panelvisual.lut_phase_real.SetRamp(0)
		panelvisual.lut_phase_real.Build()
		panelvisual.scalebar_phase_real.SetTitle("")
		panelvisual.scalebar_phase_real.SetOrientationToVertical()
		panelvisual.scalebar_phase_real.SetLookupTable(panelvisual.lut_phase_real)
		panelvisual.scalebar_phase_real.SetWidth(0.07)
		panelvisual.scalebar_phase_real.SetHeight(0.90)
		panelvisual.scalebar_phase_real.SetPosition(0.01,0.1)
		panelvisual.plane.SetOrigin(ox,oy,oz)
		panelvisual.plane.SetNormal(nx,ny,nz)
		if panelvisual.VTKIsNot6:
			panelvisual.cutter.SetInput(panelvisual.image_phase_real)
		else:
			panelvisual.cutter.SetInputData(panelvisual.image_phase_real)
		panelvisual.cutter.SetCutFunction(panelvisual.plane)
		panelvisual.cutter.GenerateCutScalarsOff()
		panelvisual.triangles_phase_real.SetInputConnection(panelvisual.cutter.GetOutputPort())
		panelvisual.strips_phase_real.SetInputConnection(panelvisual.triangles_phase_real.GetOutputPort())
		panelvisual.mapper_phase_real.SetInputConnection(panelvisual.strips_phase_real.GetOutputPort())
		panelvisual.mapper_phase_real.SetLookupTable(panelvisual.lut_phase_real)
		panelvisual.mapper_phase_real.SetScalarRange([phasemin,phasemax])
		panelvisual.mapper_phase_real.SetScalarModeToUsePointData()
		panelvisual.mapper_phase_real.ImmediateModeRenderingOn()
		panelvisual.mapper_phase_real.Modified()
		panelvisual.mapper_phase_real.Update()
		panelvisual.actor_phase_real.GetProperty().SetOpacity(1.0)
		panelvisual.actor_phase_real.SetMapper(panelvisual.mapper_phase_real)
		panelvisual.SetPicker()
		panelvisual.renderer_amp_real.RemoveAllViewProps()
		panelvisual.renderer_phase_real.RemoveAllViewProps()
		panelvisual.renderer_amp_recip.RemoveAllViewProps()
		panelvisual.renderer_phase_recip.RemoveAllViewProps()
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_recip)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_recip)
		panelvisual.renWin.GetRenderWindow().Modified()
		panelvisual.renderer_phase_real.AddActor(panelvisual.actor_phase_real)
		panelvisual.renderer_phase_real.AddActor2D(panelvisual.scalebar_phase_real)
		panelvisual.renderer_phase_real.AddActor2D(panelvisual.textActor)
		panelvisual.renderer_phase_real.SetBackground(r, g, b)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().SetMultiSamples(0)
		panelvisual.renWin.SetInteractorStyle(panelvisual.style3D)
		panelvisual.renderer_phase_real.ResetCamera()
		panelvisual.renWin.SetPicker(panelvisual.picker_amp_real)
		panelvisual.renderer_phase_real.SetViewport(0,0,1,1)
		panelvisual.renderer_amp_real.SetViewport(1,1,1,1)
		panelvisual.Layout()
		panelvisual.Show()
		if(self.chkbox_axes.GetValue() == True):
			panelvisual.axis.SetBounds(panelvisual.image_phase_real.GetBounds())
			if panelvisual.VTKIsNot6:
				panelvisual.axis.SetInput(panelvisual.image_phase_real)
			else:
				panelvisual.axis.SetInputData(panelvisual.image_phase_real)
			panelvisual.axis.SetCamera(panelvisual.renderer_phase_real.GetActiveCamera())
			panelvisual.axis.SetLabelFormat("%6.1f")
			panelvisual.axis.SetFlyModeToOuterEdges()
			panelvisual.axis.ScalingOff()
			panelvisual.axis.SetFontFactor(float(self.axes_fontfactor.value.GetValue()))
			panelvisual.axis.SetXLabel("X")
			panelvisual.axis.SetYLabel("Y")
			panelvisual.axis.SetZLabel("Z")
			panelvisual.axis.Modified()
			panelvisual.renderer_phase_real.AddViewProp( panelvisual.axis )
	def ViewDataAmpPhase(self, ancestor, data, r, g, b):
		self.ancestor.GetPage(0).queue_info.put("Preparing array visualisation")
		self.ancestor.GetPage(0).queue_info.put("Array Size: " + str(data.shape))
		panelvisual = ancestor.GetPage(1)
		contour = float(self.contour.value.GetValue())
		maxval = numpy.abs(data).max()
		if contour > maxval: contour = CNTR_CLIP*maxval;
		opacity = float(self.opacity.value.GetValue())
		feature_angle = float(self.feature_angle.value.GetValue())
		phasemax = float(self.phasemax.value.GetValue())
		phasemin = float(self.phasemin.value.GetValue())
		ox = float(self.ox.value.GetValue())
		oy = float(self.oy.value.GetValue())
		oz = float(self.oz.value.GetValue())
		nx = float(self.nx.value.GetValue())
		ny = float(self.ny.value.GetValue())
		nz = float(self.nz.value.GetValue())
		sx = float(self.sx.value.GetValue())
		sy = float(self.sy.value.GetValue())
		sz = float(self.sz.value.GetValue())
		panelvisual.flat_data = (numpy.abs(data)).transpose(2,1,0).flatten();
		panelvisual.vtk_data_array = numpy_support.numpy_to_vtk(panelvisual.flat_data)
		panelvisual.image_amp_real.GetPointData().SetScalars(panelvisual.vtk_data_array)
		panelvisual.image_amp_real.SetDimensions(data.shape)
		panelvisual.image_amp_real.SetSpacing(sx,sy,sz)
		panelvisual.image_amp_real.ComputeBounds()
		panelvisual.image_amp_real.Modified()
		panelvisual.lut_amp_real.SetNumberOfTableValues(256)
		panelvisual.lut_amp_real.SetScaleToLinear()
		panelvisual.lut_amp_real.SetTableRange(panelvisual.image_amp_real.GetPointData().GetScalars().GetRange())
		lutsource_amp = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[0][0]][1]
		if self.ancestor.GetPage(0).cmls[0][1] == 0:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(k, lutsource_amp[k][0], lutsource_amp[k][1], lutsource_amp[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(255-k, lutsource_amp[k][0], lutsource_amp[k][1], lutsource_amp[k][2], 1)
		panelvisual.lut_amp_real.SetRamp(0)
		panelvisual.lut_amp_real.Build()
		flat_data_phase = (numpy.angle(data)).transpose(2,1,0).flatten();
		vtk_data_array_phase = numpy_support.numpy_to_vtk(flat_data_phase)
		panelvisual.image_phase_real.GetPointData().SetScalars(vtk_data_array_phase)
		panelvisual.image_phase_real.SetDimensions(data.shape)
		panelvisual.image_phase_real.SetSpacing(sx,sy,sz)
		panelvisual.image_phase_real.ComputeBounds()
		panelvisual.image_phase_real.Modified()
		panelvisual.image_probe = panelvisual.image_phase_real
		panelvisual.lut_phase_real.SetNumberOfTableValues(256)
		panelvisual.lut_phase_real.SetScaleToLinear()
		panelvisual.lut_phase_real.SetTableRange([phasemin,phasemax])
		lutsource_phase = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[1][0]][1]
		if self.ancestor.GetPage(0).cmls[1][1] == 0:
			for k in range(256):
				panelvisual.lut_phase_real.SetTableValue(k, lutsource_phase[k][0], lutsource_phase[k][1], lutsource_phase[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_phase_real.SetTableValue(255-k, lutsource_phase[k][0], lutsource_phase[k][1], lutsource_phase[k][2], 1)
		panelvisual.lut_phase_real.SetRamp(0)
		panelvisual.lut_phase_real.Build()
		panelvisual.scalebar_phase_real.SetTitle("")
		panelvisual.scalebar_phase_real.SetOrientationToVertical()
		panelvisual.scalebar_phase_real.SetLookupTable(panelvisual.lut_phase_real)
		panelvisual.scalebar_phase_real.SetWidth(0.07)
		panelvisual.scalebar_phase_real.SetHeight(0.90)
		panelvisual.scalebar_phase_real.SetPosition(0.01,0.1)
		if panelvisual.VTKIsNot6:
			panelvisual.filter_amp_real.SetInput(panelvisual.image_amp_real)
		else:
			panelvisual.filter_amp_real.SetInputData(panelvisual.image_amp_real)
		panelvisual.filter_amp_real.ComputeNormalsOn()
		panelvisual.filter_amp_real.ComputeScalarsOn()
		panelvisual.filter_amp_real.SetNumberOfContours(1)
		panelvisual.filter_amp_real.SetValue( 0, contour)
		panelvisual.filter_amp_real.Modified()
		panelvisual.filter_amp_real.Update()
		panelvisual.smooth_filter_real.SetInputConnection(panelvisual.filter_amp_real.GetOutputPort())
		panelvisual.smooth_filter_real.SetNumberOfIterations(15)
		panelvisual.smooth_filter_real.SetRelaxationFactor(0.1)
		panelvisual.smooth_filter_real.FeatureEdgeSmoothingOff()
		panelvisual.smooth_filter_real.BoundarySmoothingOn()
		panelvisual.smooth_filter_real.Update()
		panelvisual.normals_amp_real.SetInputConnection(panelvisual.smooth_filter_real.GetOutputPort())
		panelvisual.normals_amp_real.SetFeatureAngle(feature_angle)
		panelvisual.normals_amp_real.ConsistencyOff()
		panelvisual.normals_amp_real.SplittingOff()
		panelvisual.normals_amp_real.AutoOrientNormalsOff()
		panelvisual.normals_amp_real.ComputePointNormalsOn()
		panelvisual.normals_amp_real.ComputeCellNormalsOff()
		panelvisual.normals_amp_real.NonManifoldTraversalOff()
		panelvisual.triangles_amp_real.SetInputConnection(panelvisual.normals_amp_real.GetOutputPort())
		panelvisual.strips_amp_real.SetInputConnection(panelvisual.triangles_amp_real.GetOutputPort())
		panelvisual.mapper_amp_real.SetInputConnection(panelvisual.strips_amp_real.GetOutputPort())
		panelvisual.mapper_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		panelvisual.mapper_amp_real.SetScalarRange(panelvisual.image_amp_real.GetPointData().GetScalars().GetRange())
		panelvisual.mapper_amp_real.SetScalarModeToUsePointData()
		panelvisual.mapper_amp_real.ImmediateModeRenderingOn()
		panelvisual.mapper_amp_real.Modified()
		panelvisual.mapper_amp_real.Update()
		panelvisual.actor_amp_real.GetProperty().SetOpacity(opacity)
		panelvisual.actor_amp_real.SetMapper(panelvisual.mapper_amp_real)
		panelvisual.plane.SetOrigin(ox,oy,oz)
		panelvisual.plane.SetNormal(nx,ny,nz)
		if panelvisual.VTKIsNot6:
			panelvisual.cutter.SetInput(panelvisual.image_phase_real)
		else:
			panelvisual.cutter.SetInputData(panelvisual.image_phase_real)
		panelvisual.cutter.SetCutFunction(panelvisual.plane)
		panelvisual.cutter.GenerateCutScalarsOff()
		panelvisual.triangles_phase_real.SetInputConnection(panelvisual.cutter.GetOutputPort())
		panelvisual.strips_phase_real.SetInputConnection(panelvisual.triangles_phase_real.GetOutputPort())
		panelvisual.mapper_phase_real.SetInputConnection(panelvisual.strips_phase_real.GetOutputPort())
		panelvisual.mapper_phase_real.SetLookupTable(panelvisual.lut_phase_real)
		panelvisual.mapper_phase_real.SetScalarRange([phasemin,phasemax])
		panelvisual.mapper_phase_real.SetScalarModeToUsePointData()
		panelvisual.mapper_phase_real.ImmediateModeRenderingOn()
		panelvisual.mapper_phase_real.Modified()
		panelvisual.mapper_phase_real.Update()
		panelvisual.actor_phase_real.SetMapper(panelvisual.mapper_phase_real)
		panelvisual.SetPicker()
		panelvisual.renderer_amp_real.RemoveAllViewProps()
		panelvisual.renderer_phase_real.RemoveAllViewProps()
		panelvisual.renderer_amp_recip.RemoveAllViewProps()
		panelvisual.renderer_phase_recip.RemoveAllViewProps()
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_recip)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_recip)
		panelvisual.renWin.GetRenderWindow().Modified()
		panelvisual.renderer_phase_real.AddActor(panelvisual.actor_phase_real)
		panelvisual.renderer_phase_real.AddActor(panelvisual.actor_amp_real)
		panelvisual.renderer_phase_real.AddActor2D(panelvisual.scalebar_phase_real)
		panelvisual.renderer_phase_real.AddActor2D(panelvisual.textActor)
		panelvisual.renderer_phase_real.SetBackground(r, g, b)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().SetMultiSamples(0)
		panelvisual.renWin.SetInteractorStyle(panelvisual.style3D)
		panelvisual.renderer_phase_real.ResetCamera()
		panelvisual.renWin.SetPicker(panelvisual.picker_amp_real)
		panelvisual.renderer_amp_real.SetViewport(1,1,1,1)
		panelvisual.renderer_phase_real.SetViewport(0,0,1,1)
		panelvisual.Layout()
		panelvisual.Show()
		if(self.chkbox_axes.GetValue() == True):
			panelvisual.axis.SetBounds(panelvisual.image_amp_real.GetBounds())
			if panelvisual.VTKIsNot6:
				panelvisual.axis.SetInput(panelvisual.image_amp_real)
			else:
				panelvisual.axis.SetInputData(panelvisual.image_amp_real)
			panelvisual.axis.SetCamera(panelvisual.renderer_phase_real.GetActiveCamera())
			panelvisual.axis.SetLabelFormat("%6.1f")
			panelvisual.axis.SetFlyModeToOuterEdges()
			panelvisual.axis.ScalingOff()
			panelvisual.axis.SetFontFactor(float(self.axes_fontfactor.value.GetValue()))
			panelvisual.axis.SetXLabel("X")
			panelvisual.axis.SetYLabel("Y")
			panelvisual.axis.SetZLabel("Z")
			panelvisual.axis.Modified()
			panelvisual.renderer_phase_real.AddViewProp( panelvisual.axis )
	def ViewDataAmpWPhase(self, ancestor, data, r, g, b):
		self.ancestor.GetPage(0).queue_info.put("Preparing array visualisation...")
		self.ancestor.GetPage(0).queue_info.put("Array Size: " + str(data.shape))
		max = numpy.array( numpy.unravel_index(data.argmax(), data.shape) )
		self.ancestor.GetPage(0).queue_info.put("Array Maximum Coordinates: " + str(max))
		self.ancestor.GetPage(0).queue_info.put("Array Maximum: %1.6e" %(numpy.abs(data[max[0]][max[1]][max[2]])))
		panelvisual = ancestor.GetPage(1)
		phasemax = float(self.phasemax.value.GetValue())
		phasemin = float(self.phasemin.value.GetValue())
		contour = float(self.contour.value.GetValue())
		maxval = numpy.abs(data).max()
		if contour > maxval: contour = CNTR_CLIP*maxval;
		sx = float(self.sx.value.GetValue())
		sy = float(self.sy.value.GetValue())
		sz = float(self.sz.value.GetValue())
		feature_angle = float(self.feature_angle.value.GetValue())
		panelvisual.flat_data_phase= (numpy.angle(data)).transpose(2,1,0).flatten();
		panelvisual.vtk_data_array_phase = numpy_support.numpy_to_vtk(panelvisual.flat_data_phase)
		panelvisual.vtk_data_array_phase.SetName("mapscalar")
		panelvisual.image_phase_real.GetPointData().SetScalars(panelvisual.vtk_data_array_phase)
		panelvisual.image_phase_real.SetDimensions(data.shape)
		panelvisual.image_phase_real.SetSpacing(sx,sy,sz)
		panelvisual.image_phase_real.ComputeBounds()
		panelvisual.image_phase_real.Modified()
		panelvisual.flat_data= (numpy.abs(data)).transpose(2,1,0).flatten();
		panelvisual.vtk_data_array = numpy_support.numpy_to_vtk(panelvisual.flat_data)
		panelvisual.vtk_data_array.SetName("isoscalar")
		points = panelvisual.image_amp_real.GetPointData()
		points.SetScalars(panelvisual.vtk_data_array)
		points.AddArray(panelvisual.vtk_data_array_phase)
		panelvisual.image_amp_real.SetDimensions(data.shape)
		panelvisual.image_amp_real.SetSpacing(sx,sy,sz)
		panelvisual.image_amp_real.ComputeBounds()
		panelvisual.image_amp_real.Modified()
		panelvisual.image_probe = panelvisual.image_phase_real
		panelvisual.lut_amp_real.SetNumberOfTableValues(256)
		panelvisual.lut_amp_real.SetScaleToLinear()
		panelvisual.lut_amp_real.SetTableRange([phasemin,phasemax])
		lutsource = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[1][0]][1]
		if self.ancestor.GetPage(0).cmls[1][1] == 0:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(255-k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		panelvisual.lut_amp_real.SetRamp(0)
		panelvisual.lut_amp_real.Build()
		panelvisual.scalebar_amp_real.SetTitle("")
		panelvisual.scalebar_amp_real.SetOrientationToVertical()
		panelvisual.scalebar_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		panelvisual.scalebar_amp_real.SetWidth(0.07)
		panelvisual.scalebar_amp_real.SetHeight(0.90)
		panelvisual.scalebar_amp_real.SetPosition(0.01,0.1)
		if panelvisual.VTKIsNot6:
			panelvisual.filter_amp_real.SetInput(panelvisual.image_amp_real)
		else:
			panelvisual.filter_amp_real.SetInputData(panelvisual.image_amp_real)
		panelvisual.filter_amp_real.ComputeNormalsOn()
		panelvisual.filter_amp_real.ComputeScalarsOn()
		panelvisual.filter_amp_real.SetNumberOfContours(1)
		panelvisual.filter_amp_real.SetValue( 0, contour)
		panelvisual.filter_amp_real.Modified()
		panelvisual.filter_amp_real.Update()
		panelvisual.smooth_filter_real.SetInputConnection(panelvisual.filter_amp_real.GetOutputPort())
		panelvisual.smooth_filter_real.SetNumberOfIterations(15)
		panelvisual.smooth_filter_real.SetRelaxationFactor(0.1)
		panelvisual.smooth_filter_real.FeatureEdgeSmoothingOff()
		panelvisual.smooth_filter_real.BoundarySmoothingOn()
		panelvisual.smooth_filter_real.Update()
		panelvisual.normals_amp_real.SetInputConnection(panelvisual.smooth_filter_real.GetOutputPort())
		panelvisual.normals_amp_real.SetFeatureAngle(feature_angle)
		panelvisual.normals_amp_real.ConsistencyOff()
		panelvisual.normals_amp_real.SplittingOff()
		panelvisual.normals_amp_real.AutoOrientNormalsOff()
		panelvisual.normals_amp_real.ComputePointNormalsOn()
		panelvisual.normals_amp_real.ComputeCellNormalsOff()
		panelvisual.normals_amp_real.NonManifoldTraversalOff()
		panelvisual.triangles_amp_real.SetInputConnection(panelvisual.normals_amp_real.GetOutputPort())
		panelvisual.strips_amp_real.SetInputConnection(panelvisual.triangles_amp_real.GetOutputPort())
		panelvisual.mapper_amp_real.SetInputConnection(panelvisual.strips_amp_real.GetOutputPort())
		panelvisual.mapper_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		panelvisual.mapper_amp_real.SetScalarRange([phasemin,phasemax])
		panelvisual.mapper_amp_real.SetScalarModeToUsePointFieldData()
		panelvisual.mapper_amp_real.SelectColorArray("mapscalar")
		panelvisual.mapper_amp_real.ImmediateModeRenderingOn()
		panelvisual.mapper_amp_real.Modified()
		panelvisual.mapper_amp_real.Update()
		panelvisual.actor_amp_real.GetProperty().SetOpacity(1.0)
		panelvisual.actor_amp_real.SetMapper(panelvisual.mapper_amp_real)
		panelvisual.SetPicker()
		panelvisual.renderer_amp_real.RemoveAllViewProps()
		panelvisual.renderer_phase_real.RemoveAllViewProps()
		panelvisual.renderer_amp_recip.RemoveAllViewProps()
		panelvisual.renderer_phase_recip.RemoveAllViewProps()
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_recip)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_recip)
		panelvisual.renWin.GetRenderWindow().Modified()
		panelvisual.renderer_amp_real.AddActor(panelvisual.actor_amp_real)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.scalebar_amp_real)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.textActor)
		panelvisual.renderer_amp_real.SetBackground(r, g, b)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().SetMultiSamples(0)
		panelvisual.renWin.SetInteractorStyle(panelvisual.style3D)
		panelvisual.renderer_amp_real.ResetCamera()
		panelvisual.renWin.SetPicker(panelvisual.picker_amp_real)
		panelvisual.renderer_amp_real.SetViewport(0,0,1,1)
		panelvisual.renderer_phase_real.SetViewport(1,1,1,1)
		panelvisual.Layout()
		panelvisual.Show()
		if(self.chkbox_axes.GetValue() == True):
			panelvisual.axis.SetBounds(panelvisual.image_amp_real.GetBounds())
			if panelvisual.VTKIsNot6:
				panelvisual.axis.SetInput(panelvisual.image_amp_real)
			else:
				panelvisual.axis.SetInputData(panelvisual.image_amp_real)
			panelvisual.axis.SetCamera(panelvisual.renderer_amp_real.GetActiveCamera())
			panelvisual.axis.SetLabelFormat("%6.1f")
			panelvisual.axis.SetFlyModeToOuterEdges()
			panelvisual.axis.ScalingOff()
			panelvisual.axis.SetFontFactor(float(self.axes_fontfactor.value.GetValue()))
			panelvisual.axis.SetXLabel("X")
			panelvisual.axis.SetYLabel("Y")
			panelvisual.axis.SetZLabel("Z")
			panelvisual.axis.Modified()
			panelvisual.renderer_amp_real.AddViewProp( panelvisual.axis )
	def ViewAmpPlane(self, ancestor, data, r, g, b):
		self.ancestor.GetPage(0).queue_info.put("Preparing array visualisation")
		self.ancestor.GetPage(0).queue_info.put("Array Size: " + str(data.shape))
		max = numpy.array( numpy.unravel_index(data.argmax(), data.shape) )
		self.ancestor.GetPage(0).queue_info.put("Array Maximum Coordinates: " + str(max))
		self.ancestor.GetPage(0).queue_info.put("Array Maximum: %1.6e" %(numpy.abs(data[max[0]][max[1]][max[2]])))
		panelvisual = ancestor.GetPage(1)
		ox = float(self.ox.value.GetValue())
		oy = float(self.oy.value.GetValue())
		oz = float(self.oz.value.GetValue())
		nx = float(self.nx.value.GetValue())
		ny = float(self.ny.value.GetValue())
		nz = float(self.nz.value.GetValue())
		sx = float(self.sx.value.GetValue())
		sy = float(self.sy.value.GetValue())
		sz = float(self.sz.value.GetValue())
		panelvisual.flat_data= (numpy.abs(data)).transpose(2,1,0).flatten();
		panelvisual.vtk_data_array = numpy_support.numpy_to_vtk(panelvisual.flat_data)
		points = panelvisual.image_amp_real.GetPointData()
		points.SetScalars(panelvisual.vtk_data_array)
		panelvisual.image_amp_real.SetDimensions(data.shape)
		panelvisual.image_amp_real.SetSpacing(sx,sy,sz)
		panelvisual.image_amp_real.ComputeBounds()
		panelvisual.image_amp_real.Modified()
		panelvisual.image_probe = panelvisual.image_amp_real
		panelvisual.lut_amp_real.SetNumberOfTableValues(256)
		panelvisual.lut_amp_real.SetScaleToLinear()
		panelvisual.lut_amp_real.SetTableRange(panelvisual.image_amp_real.GetPointData().GetScalars().GetRange())
		lutsource = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[0][0]][1]
		if self.ancestor.GetPage(0).cmls[0][1] == 0:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(255-k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		panelvisual.lut_amp_real.SetRamp(0)
		panelvisual.lut_amp_real.Build()
		panelvisual.scalebar_amp_real.SetTitle("")
		panelvisual.scalebar_amp_real.SetOrientationToVertical()
		panelvisual.scalebar_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		panelvisual.scalebar_amp_real.SetWidth(0.07)
		panelvisual.scalebar_amp_real.SetHeight(0.90)
		panelvisual.scalebar_amp_real.SetPosition(0.01,0.1)
		panelvisual.plane.SetOrigin(ox,oy,oz)
		panelvisual.plane.SetNormal(nx,ny,nz)
		if panelvisual.VTKIsNot6:
			panelvisual.cutter.SetInput(panelvisual.image_amp_real)
		else:
			panelvisual.cutter.SetInputData(panelvisual.image_amp_real)
		panelvisual.cutter.SetCutFunction(panelvisual.plane)
		panelvisual.cutter.GenerateCutScalarsOff()
		panelvisual.triangles_amp_real.SetInputConnection(panelvisual.cutter.GetOutputPort())
		panelvisual.strips_amp_real.SetInputConnection(panelvisual.triangles_amp_real.GetOutputPort())
		panelvisual.mapper_amp_real.SetInputConnection(panelvisual.strips_amp_real.GetOutputPort())
		panelvisual.mapper_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		panelvisual.mapper_amp_real.SetScalarRange(panelvisual.image_amp_real.GetPointData().GetScalars().GetRange())
		panelvisual.mapper_amp_real.ImmediateModeRenderingOn()
		panelvisual.mapper_amp_real.Modified()
		panelvisual.actor_amp_real.GetProperty().SetOpacity(1.0)
		panelvisual.actor_amp_real.SetMapper(panelvisual.mapper_amp_real)
		panelvisual.SetPicker()
		panelvisual.renderer_amp_real.RemoveAllViewProps()
		panelvisual.renderer_phase_real.RemoveAllViewProps()
		panelvisual.renderer_amp_recip.RemoveAllViewProps()
		panelvisual.renderer_phase_recip.RemoveAllViewProps()
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_recip)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_recip)
		panelvisual.renWin.GetRenderWindow().Modified()
		panelvisual.renderer_amp_real.AddActor(panelvisual.actor_amp_real)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.scalebar_amp_real)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.textActor)
		panelvisual.renderer_amp_real.SetBackground(r, g, b)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().SetMultiSamples(0)
		panelvisual.renWin.SetInteractorStyle(panelvisual.style3D)
		panelvisual.renderer_amp_real.ResetCamera()
		panelvisual.renWin.SetPicker(panelvisual.picker_amp_real)
		panelvisual.renderer_amp_real.SetViewport(0,0,1,1)
		panelvisual.Layout()
		panelvisual.Show()
		if(self.chkbox_axes.GetValue() == True):
			panelvisual.axis.SetBounds(panelvisual.image_amp_real.GetBounds())
			if panelvisual.VTKIsNot6:
				panelvisual.axis.SetInput(panelvisual.image_amp_real)
			else:
				panelvisual.axis.SetInputData(panelvisual.image_amp_real)
			panelvisual.axis.SetCamera(panelvisual.renderer_amp_real.GetActiveCamera())
			panelvisual.axis.SetLabelFormat("%6.1f")
			panelvisual.axis.SetFlyModeToOuterEdges()
			panelvisual.axis.ScalingOff()
			panelvisual.axis.SetFontFactor(float(self.axes_fontfactor.value.GetValue()))
			panelvisual.axis.SetXLabel("X")
			panelvisual.axis.SetYLabel("Y")
			panelvisual.axis.SetZLabel("Z")
			panelvisual.axis.Modified()
			panelvisual.renderer_amp_real.AddViewProp( panelvisual.axis )
	def ViewDataAmp2D(self, ancestor, data, r, g, b):
		self.ancestor.GetPage(0).queue_info.put("Preparing 2D array visualisation")
		self.ancestor.GetPage(0).queue_info.put("Array Size: " + str(data.shape))
		max = numpy.array( numpy.unravel_index(data.argmax(), data.shape) )
		self.ancestor.GetPage(0).queue_info.put("Array Maximum Coordinates: " + str(max))
		self.ancestor.GetPage(0).queue_info.put("Array Maximum: %1.6e" %(numpy.abs(data[max[0]][max[1]][max[2]])))
		panelvisual = ancestor.GetPage(1)
		sx = float(self.sx.value.GetValue())
		sy = float(self.sy.value.GetValue())
		sz = float(self.sz.value.GetValue())
		panelvisual.flat_data= (numpy.abs(data)).transpose(2,1,0).flatten();
		panelvisual.vtk_data_array = numpy_support.numpy_to_vtk(panelvisual.flat_data)
		points = panelvisual.image2D_amp_real.GetPointData()
		points.SetScalars(panelvisual.vtk_data_array)
		panelvisual.image2D_amp_real.SetDimensions(data.shape)
		panelvisual.image2D_amp_real.SetSpacing(sx,sy,sz)
		panelvisual.image2D_amp_real.ComputeBounds()
		panelvisual.image2D_amp_real.Modified()
		panelvisual.image_probe = panelvisual.image2D_amp_real
		panelvisual.lut_amp_real.SetNumberOfTableValues(256)
		panelvisual.lut_amp_real.SetScaleToLinear()
		panelvisual.lut_amp_real.SetTableRange(panelvisual.image2D_amp_real.GetPointData().GetScalars().GetRange())
		lutsource = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[0][0]][1]
		if self.ancestor.GetPage(0).cmls[0][1] == 0:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(255-k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		panelvisual.lut_amp_real.SetRamp(0)
		panelvisual.lut_amp_real.Build()
		panelvisual.scalebar_amp_real.SetTitle("")
		panelvisual.scalebar_amp_real.SetOrientationToVertical()
		panelvisual.scalebar_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		panelvisual.scalebar_amp_real.SetWidth(0.07)
		panelvisual.scalebar_amp_real.SetHeight(0.90)
		panelvisual.scalebar_amp_real.SetPosition(0.01,0.1)
		panelvisual.color_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		if panelvisual.VTKIsNot6:
			panelvisual.color_amp_real.SetInput(panelvisual.image2D_amp_real)
		else:
			panelvisual.color_amp_real.SetInputData(panelvisual.image2D_amp_real)
		panelvisual.color_amp_real.Update()
		if panelvisual.VTKIsNot6:
			panelvisual.mapper2D_amp_real.SetInputConnection(panelvisual.color_amp_real.GetOutputPort())
			panelvisual.actor2D_amp_real.SetInput(panelvisual.mapper2D_amp_real.GetInput())
		else:
			panelvisual.actor2D_amp_real.GetMapper().SetInputConnection(panelvisual.color_amp_real.GetOutputPort())
		panelvisual.SetPicker()
		panelvisual.renderer_amp_real.RemoveAllViewProps()
		panelvisual.renderer_phase_real.RemoveAllViewProps()
		panelvisual.renderer_amp_recip.RemoveAllViewProps()
		panelvisual.renderer_phase_recip.RemoveAllViewProps()
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_recip)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_recip)
		panelvisual.renWin.GetRenderWindow().Modified()
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.actor2D_amp_real)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.scalebar_amp_real)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.textActor)
		panelvisual.renderer_amp_real.SetBackground(r, g, b)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_real)
		panelvisual.renderer_amp_real.GetActiveCamera().SetPosition(0,0,1)
		panelvisual.renderer_amp_real.GetActiveCamera().SetViewUp(0,1,0)
		panelvisual.renderer_amp_real.GetActiveCamera().SetFocalPoint(0,0,0)
		panelvisual.renderer_amp_real.ResetCamera()
		panelvisual.renderer_amp_real.SetViewport(0,0,1,1)
		panelvisual.renderer_amp_recip.SetViewport(1,1,1,1)
		panelvisual.renWin.SetPicker(panelvisual.picker_amp_real)
		panelvisual.renWin.SetInteractorStyle(panelvisual.style2D)
		panelvisual.Layout()
		panelvisual.Show()
		if(self.chkbox_axes.GetValue() == True):
			if panelvisual.VTKIsNot6:
				panelvisual.axis2D.SetInput(panelvisual.image2D_amp_real)
			else:
				panelvisual.axis2D.SetInputData(panelvisual.image2D_amp_real)
			panelvisual.axis2D.SetBounds(panelvisual.image2D_amp_real.GetBounds())
			panelvisual.axis2D.SetCamera(panelvisual.renderer_amp_real.GetActiveCamera())
			panelvisual.axis2D.SetLabelFormat("%6.1f")
			panelvisual.axis2D.SetNumberOfLabels(10)
			panelvisual.axis.SetFlyModeToOuterEdges()
			panelvisual.axis.ScalingOff()
			panelvisual.axis.SetFontFactor(float(self.axes_fontfactor.value.GetValue()))
			panelvisual.axis.SetXLabel("X")
			panelvisual.axis.SetYLabel("Y")
			panelvisual.axis.Modified()
			panelvisual.renderer_amp_real.AddViewProp( panelvisual.axis2D )
	def ViewDataPhase2D(self, ancestor, data, r, g, b):
		self.ancestor.GetPage(0).queue_info.put("Preparing 2D array visualisation")
		self.ancestor.GetPage(0).queue_info.put("Array Size: " + str(data.shape))
		panelvisual = ancestor.GetPage(1)
		phasemax = float(self.phasemax.value.GetValue())
		phasemin = float(self.phasemin.value.GetValue())
		sx = float(self.sx.value.GetValue())
		sy = float(self.sy.value.GetValue())
		sz = float(self.sz.value.GetValue())
		panelvisual.flat_data= (numpy.angle(data)).transpose(2,1,0).flatten();
		panelvisual.vtk_data_array = numpy_support.numpy_to_vtk(panelvisual.flat_data)
		points = panelvisual.image2D_phase_real.GetPointData()
		points.SetScalars(panelvisual.vtk_data_array)
		panelvisual.image2D_phase_real.SetDimensions(data.shape)
		panelvisual.image2D_phase_real.SetSpacing(sx,sy,sz)
		panelvisual.image2D_phase_real.ComputeBounds()
		panelvisual.image2D_phase_real.Modified()
		panelvisual.image_probe = panelvisual.image2D_phase_real
		panelvisual.lut_phase_real.SetNumberOfTableValues(256)
		panelvisual.lut_phase_real.SetScaleToLinear()
		panelvisual.lut_phase_real.SetTableRange([phasemin,phasemax])
		lutsource = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[1][0]][1]
		if self.ancestor.GetPage(0).cmls[1][1] == 0:
			for k in range(256):
				panelvisual.lut_phase_real.SetTableValue(k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_phase_real.SetTableValue(255-k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		panelvisual.lut_phase_real.SetRamp(0)
		panelvisual.lut_phase_real.Build()
		panelvisual.scalebar_phase_real.SetTitle("")
		panelvisual.scalebar_phase_real.SetOrientationToVertical()
		panelvisual.scalebar_phase_real.SetLookupTable(panelvisual.lut_phase_real)
		panelvisual.scalebar_phase_real.SetWidth(0.07)
		panelvisual.scalebar_phase_real.SetHeight(0.90)
		panelvisual.scalebar_phase_real.SetPosition(0.01,0.1)
		panelvisual.color_phase_real.SetLookupTable(panelvisual.lut_phase_real)
		if panelvisual.VTKIsNot6:
			panelvisual.color_phase_real.SetInput(panelvisual.image2D_phase_real)
		else:
			panelvisual.color_phase_real.SetInputData(panelvisual.image2D_phase_real)
		panelvisual.color_phase_real.Update()
		if panelvisual.VTKIsNot6:
			panelvisual.mapper2D_phase_real.SetInputConnection(panelvisual.color_phase_real.GetOutputPort())
			panelvisual.actor2D_phase_real.SetInput(panelvisual.mapper2D_phase_real.GetInput())
		else:
			panelvisual.actor2D_phase_real.GetMapper().SetInputConnection(panelvisual.color_phase_real.GetOutputPort())
		panelvisual.SetPicker()
		panelvisual.renderer_amp_real.RemoveAllViewProps()
		panelvisual.renderer_phase_real.RemoveAllViewProps()
		panelvisual.renderer_amp_recip.RemoveAllViewProps()
		panelvisual.renderer_phase_recip.RemoveAllViewProps()
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_recip)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_recip)
		panelvisual.renWin.GetRenderWindow().Modified()
		panelvisual.renderer_phase_real.AddActor2D(panelvisual.actor2D_phase_real)
		panelvisual.renderer_phase_real.AddActor2D(panelvisual.scalebar_phase_real)
		panelvisual.renderer_phase_real.AddActor2D(panelvisual.textActor)
		panelvisual.renderer_phase_real.SetBackground(r, g, b)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_phase_real)
		panelvisual.renderer_phase_real.GetActiveCamera().SetPosition(0,0,1)
		panelvisual.renderer_phase_real.GetActiveCamera().SetViewUp(0,1,0)
		panelvisual.renderer_phase_real.GetActiveCamera().SetFocalPoint(0,0,0)
		panelvisual.renderer_phase_real.ResetCamera()
		panelvisual.renderer_phase_real.SetViewport(0,0,1,1)
		panelvisual.renderer_phase_recip.SetViewport(1,1,1,1)
		panelvisual.renWin.SetPicker(panelvisual.picker_amp_real)
		panelvisual.renWin.SetInteractorStyle(panelvisual.style2D)
		panelvisual.Layout()
		panelvisual.Show()
		if(self.chkbox_axes.GetValue() == True):
			if panelvisual.VTKIsNot6:
				panelvisual.axis2D.SetInput(panelvisual.image2D_phase_real)
			else:
				panelvisual.axis2D.SetInputData(panelvisual.image2D_phase_real)
			panelvisual.axis2D.SetBounds(panelvisual.image2D_phase_real.GetBounds())
			panelvisual.axis2D.SetCamera(panelvisual.renderer_phase_real.GetActiveCamera())
			panelvisual.axis2D.SetLabelFormat("%6.1f")
			panelvisual.axis2D.SetNumberOfLabels(10)
			panelvisual.axis.SetFlyModeToOuterEdges()
			panelvisual.axis.ScalingOff()
			panelvisual.axis.SetFontFactor(float(self.axes_fontfactor.value.GetValue()))
			panelvisual.axis.SetXLabel("X")
			panelvisual.axis.SetYLabel("Y")
			panelvisual.axis.Modified()
			panelvisual.renderer_phase_real.AddViewProp( panelvisual.axis2D )
	def ViewDataAmpPhase2D(self, ancestor, data, r, g, b):
		self.ancestor.GetPage(0).queue_info.put("Preparing 2D array visualisation")
		self.ancestor.GetPage(0).queue_info.put("Array Size: " + str(data.shape))
		max = numpy.array( numpy.unravel_index(data.argmax(), data.shape) )
		self.ancestor.GetPage(0).queue_info.put("Array Maximum Coordinates: " + str(max))
		self.ancestor.GetPage(0).queue_info.put("Array Maximum: %1.6e" %(numpy.abs(data[max[0]][max[1]][max[2]])))
		panelvisual = ancestor.GetPage(1)
		sx = float(self.sx.value.GetValue())
		sy = float(self.sy.value.GetValue())
		sz = float(self.sz.value.GetValue())
		panelvisual.flat_data_amp= (numpy.abs(data)).transpose(2,1,0).flatten();
		panelvisual.vtk_data_array_amp = numpy_support.numpy_to_vtk(panelvisual.flat_data_amp)
		points_amp = panelvisual.image2D_amp_real.GetPointData()
		points_amp.SetScalars(panelvisual.vtk_data_array_amp)
		panelvisual.image2D_amp_real.SetDimensions(data.shape)
		panelvisual.image2D_amp_real.SetSpacing(sx,sy,sz)
		panelvisual.image2D_amp_real.ComputeBounds()
		panelvisual.image2D_amp_real.Modified()
		panelvisual.image_probe = panelvisual.image2D_amp_real
		panelvisual.lut_amp_real.SetNumberOfTableValues(256)
		panelvisual.lut_amp_real.SetScaleToLinear()
		panelvisual.lut_amp_real.SetTableRange(panelvisual.image2D_amp_real.GetPointData().GetScalars().GetRange())
		lutsource = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[0][0]][1]
		if self.ancestor.GetPage(0).cmls[0][1] == 0:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(255-k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		panelvisual.lut_amp_real.SetRamp(0)
		panelvisual.lut_amp_real.Build()
		panelvisual.scalebar_amp_real.SetTitle("")
		panelvisual.scalebar_amp_real.SetOrientationToVertical()
		panelvisual.scalebar_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		panelvisual.scalebar_amp_real.SetWidth(0.07)
		panelvisual.scalebar_amp_real.SetHeight(0.90)
		panelvisual.scalebar_amp_real.SetPosition(0.01,0.1)
		panelvisual.color_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		if panelvisual.VTKIsNot6:
			panelvisual.color_amp_real.SetInput(panelvisual.image2D_amp_real)
		else:
			panelvisual.color_amp_real.SetInputData(panelvisual.image2D_amp_real)
		panelvisual.color_amp_real.Update()
		if panelvisual.VTKIsNot6:
			panelvisual.mapper2D_amp_real.SetInputConnection(panelvisual.color_amp_real.GetOutputPort())
			panelvisual.actor2D_amp_real.SetInput(panelvisual.mapper2D_amp_real.GetInput())
		else:
			panelvisual.actor2D_amp_real.GetMapper().SetInputConnection(panelvisual.color_amp_real.GetOutputPort())
		phasemax = float(self.phasemax.value.GetValue())
		phasemin = float(self.phasemin.value.GetValue())
		flat_data_phase= (numpy.angle(data)).transpose(2,1,0).flatten();
		vtk_data_array_phase = numpy_support.numpy_to_vtk(flat_data_phase)
		points_phase = panelvisual.image2D_phase_real.GetPointData()
		points_phase.SetScalars(vtk_data_array_phase)
		panelvisual.image2D_phase_real.SetDimensions(data.shape)
		panelvisual.image2D_phase_real.SetSpacing(sx,sy,sz)
		panelvisual.image2D_phase_real.ComputeBounds()
		panelvisual.image2D_phase_real.Modified()
		panelvisual.lut_phase_real.SetNumberOfTableValues(256)
		panelvisual.lut_phase_real.SetTableRange([phasemin,phasemax])
		lutsource = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[1][0]][1]
		if self.ancestor.GetPage(0).cmls[1][1] == 0:
			for k in range(256):
				panelvisual.lut_phase_real.SetTableValue(k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_phase_real.SetTableValue(255-k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		panelvisual.lut_phase_real.SetRamp(0)
		panelvisual.lut_phase_real.Build()
		panelvisual.scalebar_phase_real.SetTitle("")
		panelvisual.scalebar_phase_real.SetOrientationToVertical()
		panelvisual.scalebar_phase_real.SetLookupTable(panelvisual.lut_phase_real)
		panelvisual.scalebar_phase_real.SetWidth(0.07)
		panelvisual.scalebar_phase_real.SetHeight(0.90)
		panelvisual.scalebar_phase_real.SetPosition(0.01,0.1)
		panelvisual.color_phase_real.SetLookupTable(panelvisual.lut_phase_real)
		if panelvisual.VTKIsNot6:
			panelvisual.color_phase_real.SetInput(panelvisual.image2D_phase_real)
		else:
			panelvisual.color_phase_real.SetInputData(panelvisual.image2D_phase_real)
		panelvisual.color_phase_real.Update()
		if panelvisual.VTKIsNot6:
			panelvisual.mapper2D_phase_real.SetInputConnection(panelvisual.color_phase_real.GetOutputPort())
			panelvisual.actor2D_phase_real.SetInput(panelvisual.mapper2D_phase_real.GetInput())
		else:
			panelvisual.actor2D_phase_real.GetMapper().SetInputConnection(panelvisual.color_phase_real.GetOutputPort())
		panelvisual.SetPicker()
		panelvisual.renderer_amp_real.RemoveAllViewProps()
		panelvisual.renderer_phase_real.RemoveAllViewProps()
		panelvisual.renderer_amp_recip.RemoveAllViewProps()
		panelvisual.renderer_phase_recip.RemoveAllViewProps()
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_recip)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_recip)
		panelvisual.renWin.GetRenderWindow().Modified()
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.actor2D_amp_real)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.scalebar_amp_real)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.textActor)
		panelvisual.renderer_amp_real.SetBackground(r, g, b)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_real)
		panelvisual.renderer_amp_real.GetActiveCamera().SetPosition(0,0,1)
		panelvisual.renderer_amp_real.GetActiveCamera().SetViewUp(0,1,0)
		panelvisual.renderer_amp_real.GetActiveCamera().SetFocalPoint(0,0,0)
		panelvisual.renderer_amp_real.ResetCamera()
		panelvisual.renderer_amp_real.SetViewport(0,0,0.5,1)
		panelvisual.renderer_phase_real.AddActor2D(panelvisual.actor2D_phase_real)
		panelvisual.renderer_phase_real.AddActor2D(panelvisual.scalebar_phase_real)
		panelvisual.renderer_phase_real.SetBackground(r, g, b)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_phase_real)
		panelvisual.renderer_phase_real.GetActiveCamera().SetPosition(0,0,1)
		panelvisual.renderer_phase_real.GetActiveCamera().SetViewUp(0,1,0)
		panelvisual.renderer_phase_real.GetActiveCamera().SetFocalPoint(0,0,0)
		panelvisual.renderer_phase_real.ResetCamera()
		panelvisual.renderer_phase_real.SetViewport(0.5,0,1,1)
		panelvisual.renWin.SetPicker(panelvisual.picker_amp_real)
		panelvisual.renWin.SetInteractorStyle(panelvisual.style2D)
		panelvisual.Layout()
		panelvisual.Show()
		if(self.chkbox_axes.GetValue() == True):
			if panelvisual.VTKIsNot6:
				panelvisual.axis2D.SetInput(panelvisual.image2D_amp_real)
			else:
				panelvisual.axis2D.SetInputData(panelvisual.image2D_amp_real)
			panelvisual.axis2D.SetBounds(panelvisual.image2D_amp_real.GetBounds())
			panelvisual.axis2D.SetCamera(panelvisual.renderer_amp_real.GetActiveCamera())
			panelvisual.axis2D.SetLabelFormat("%6.1f")
			panelvisual.axis2D.SetNumberOfLabels(10)
			panelvisual.axis.SetFlyModeToOuterEdges()
			panelvisual.renderer_amp_real.AddViewProp( panelvisual.axis2D )
			if panelvisual.VTKIsNot6:
				panelvisual.axis2D_phase.SetInput(panelvisual.image2D_phase_real)
			else:
				panelvisual.axis2D_phase.SetInputData(panelvisual.image2D_phase_real)
			panelvisual.axis2D_phase.SetBounds(panelvisual.image2D_phase_real.GetBounds())
			panelvisual.axis2D_phase.SetCamera(panelvisual.renderer_phase_real.GetActiveCamera())
			panelvisual.axis2D_phase.SetLabelFormat("%6.1f")
			panelvisual.axis2D_phase.SetNumberOfLabels(10)
			panelvisual.axis.SetFlyModeToOuterEdges()
			panelvisual.axis.ScalingOff()
			panelvisual.axis.SetFontFactor(float(self.axes_fontfactor.value.GetValue()))
			panelvisual.axis.SetXLabel("X")
			panelvisual.axis.SetYLabel("Y")
			panelvisual.axis.Modified()
			panelvisual.renderer_phase_real.AddViewProp( panelvisual.axis2D_phase )
	data_file  = self.input_filename.objectpath.GetValue()
	panelvisual = self.ancestor.GetPage(1)
	panelvisual.contour_real.value.SetValue(self.contour.value.GetValue())
	panelvisual.OnContourSelect(None, forceshow=True)
	r = float(panelvisual.r)/255.0
	g = float(panelvisual.g)/255.0
	b = float(panelvisual.b)/255.0
	try:
		panelvisual.data = LoadArray(self.ancestor.GetPage(0), data_file)
		panelvisual.data_max = numpy.abs(panelvisual.data).max()
	except:
		msg = "Could not load array."
		dlg = wx.MessageDialog(self, msg, "Sequence View Array", wx.OK)
		dlg.ShowModal()
		dlg.Destroy()
		return
	else:
		if (self.rbampphase.GetStringSelection() == 'Amplitude'):
			if panelvisual.data.shape[2] == 1:
				ViewDataAmp2D(self, ancestor , panelvisual.data, r, g, b)
			else:
				ViewDataAmp(self, ancestor , panelvisual.data, r, g, b)
		if (self.rbampphase.GetStringSelection() == 'Phase'):
			if panelvisual.data.shape[2] == 1:
				ViewDataPhase2D(self, ancestor , panelvisual.data, r, g, b)
			else:
				ViewDataPhase(self, ancestor , panelvisual.data, r, g, b)
		if (self.rbampphase.GetStringSelection() == 'Amplitude and Phase'):
			if panelvisual.data.shape[2] == 1:
				ViewDataAmpPhase2D(self, ancestor , panelvisual.data, r, g, b)
			else:
				ViewDataAmpPhase(self, ancestor , panelvisual.data, r, g, b)
		if (self.rbampphase.GetStringSelection() == 'Amplitude with Phase'):
			if panelvisual.data.shape[2] == 1:
				pass
			else:
				ViewDataAmpWPhase(self, ancestor , panelvisual.data, r, g, b)
		if (self.rbampphase.GetStringSelection() == 'Amplitude (cut plane)'):
			if panelvisual.data.shape[2] == 1:
				pass
			else:
				ViewAmpPlane(self, ancestor , panelvisual.data, r, g, b)
		panelvisual.datarangelist = []
		panelvisual.ReleaseVisualButtons(gotovisual=True)
		panelvisual.RefreshSceneFull()
def Sequence_View_Support(self, ancestor):
	def ViewDataSupport(self, ancestor, data, inputdata, r, g, b):
		self.ancestor.GetPage(0).queue_info.put("Preparing Support array visualisation...")
		self.ancestor.GetPage(0).queue_info.put("Array Size: " + str(data.shape))
		max = numpy.array( numpy.unravel_index(data.argmax(), data.shape) )
		self.ancestor.GetPage(0).queue_info.put("Array Maximum Coordinates: " + str(max))
		self.ancestor.GetPage(0).queue_info.put("Array Maximum: %1.6e" %(numpy.abs(data[max[0]][max[1]][max[2]])))
		panelvisual = ancestor.GetPage(1)
		contour = float(self.contour.value.GetValue())
		contour_support = float(self.contour_support.value.GetValue())
		opacity = float(self.opacity.value.GetValue())
		maxval = numpy.abs(inputdata).max()
		if contour > maxval: contour = CNTR_CLIP*maxval;
		feature_angle = float(self.feature_angle.value.GetValue())
		panelvisual.flat_data = (numpy.abs(data)).transpose(2,1,0).flatten();
		panelvisual.vtk_data_array = numpy_support.numpy_to_vtk(panelvisual.flat_data)
		points = panelvisual.image_phase_real.GetPointData()
		points.SetScalars(panelvisual.vtk_data_array)
		panelvisual.image_phase_real.SetDimensions(data.shape)
		panelvisual.image_phase_real.SetSpacing(1.0,1.0,1.0)
		panelvisual.image_phase_real.ComputeBounds()
		panelvisual.image_phase_real.Modified()
		panelvisual.image_probe = panelvisual.image_phase_real
		panelvisual.flat_data2 = (numpy.abs(inputdata)).transpose(2,1,0).flatten();
		panelvisual.vtk_data_array2 = numpy_support.numpy_to_vtk(panelvisual.flat_data2)
		panelvisual.image_amp_real.GetPointData().SetScalars(panelvisual.vtk_data_array2)
		panelvisual.image_amp_real.SetDimensions(inputdata.shape)
		panelvisual.image_amp_real.SetSpacing(1.0,1.0,1.0)
		panelvisual.image_amp_real.ComputeBounds()
		panelvisual.image_amp_real.Modified()
		panelvisual.lut_amp_real.SetNumberOfTableValues(256)
		panelvisual.lut_amp_real.SetScaleToLinear()
		panelvisual.lut_amp_real.SetTableRange(panelvisual.image_amp_real.GetPointData().GetScalars().GetRange())
		lutsource = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[0][0]][1]
		if self.ancestor.GetPage(0).cmls[0][1] == 0:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(255-k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		panelvisual.lut_amp_real.SetRamp(0)
		panelvisual.lut_amp_real.Build()
		panelvisual.scalebar_amp_real.SetTitle("")
		panelvisual.scalebar_amp_real.SetOrientationToVertical()
		panelvisual.scalebar_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		panelvisual.scalebar_amp_real.SetWidth(0.07)
		panelvisual.scalebar_amp_real.SetHeight(0.90)
		panelvisual.scalebar_amp_real.SetPosition(0.01,0.1)
		panelvisual.scalebar_amp_real.Modified()
		if panelvisual.VTKIsNot6:
			panelvisual.filter_support.SetInput(panelvisual.image_phase_real)
		else:
			panelvisual.filter_support.SetInputData(panelvisual.image_phase_real)
		panelvisual.filter_support.ComputeNormalsOn()
		panelvisual.filter_support.ComputeScalarsOn()
		panelvisual.filter_support.SetNumberOfContours(1)
		panelvisual.filter_support.SetValue( 0, contour_support)
		panelvisual.filter_support.Modified()
		panelvisual.filter_support.Update()
		if panelvisual.VTKIsNot6:
			panelvisual.filter_amp_real.SetInput(panelvisual.image_amp_real)
		else:
			panelvisual.filter_amp_real.SetInputData(panelvisual.image_amp_real)
		panelvisual.filter_amp_real.ComputeNormalsOn()
		panelvisual.filter_amp_real.ComputeScalarsOn()
		panelvisual.filter_amp_real.SetNumberOfContours(1)
		panelvisual.filter_amp_real.SetValue(0, contour)
		panelvisual.filter_amp_real.Modified()
		panelvisual.filter_amp_real.Update()
		panelvisual.smooth_filter_support.SetInputConnection(panelvisual.filter_support.GetOutputPort())
		panelvisual.smooth_filter_support.SetNumberOfIterations(15)
		panelvisual.smooth_filter_support.SetRelaxationFactor(0.1)
		panelvisual.smooth_filter_support.FeatureEdgeSmoothingOff()
		panelvisual.smooth_filter_support.BoundarySmoothingOn()
		panelvisual.smooth_filter_support.Update()
		panelvisual.smooth_filter_real.SetInputConnection(panelvisual.filter_amp_real.GetOutputPort())
		panelvisual.smooth_filter_real.SetNumberOfIterations(15)
		panelvisual.smooth_filter_real.SetRelaxationFactor(0.1)
		panelvisual.smooth_filter_real.FeatureEdgeSmoothingOff()
		panelvisual.smooth_filter_real.BoundarySmoothingOn()
		panelvisual.smooth_filter_real.Update()
		panelvisual.normals_support.SetInputConnection(panelvisual.smooth_filter_support.GetOutputPort())
		panelvisual.normals_support.SetFeatureAngle(feature_angle)
		panelvisual.normals_support.ConsistencyOff()
		panelvisual.normals_support.SplittingOff()
		panelvisual.normals_support.AutoOrientNormalsOff()
		panelvisual.normals_support.ComputePointNormalsOn()
		panelvisual.normals_support.ComputeCellNormalsOff()
		panelvisual.normals_support.NonManifoldTraversalOff()
		panelvisual.normals_amp_real.SetInputConnection(panelvisual.smooth_filter_real.GetOutputPort())
		panelvisual.normals_amp_real.SetFeatureAngle(feature_angle)
		panelvisual.normals_amp_real.ConsistencyOff()
		panelvisual.normals_amp_real.SplittingOff()
		panelvisual.normals_amp_real.AutoOrientNormalsOff()
		panelvisual.normals_amp_real.ComputePointNormalsOn()
		panelvisual.normals_amp_real.ComputeCellNormalsOff()
		panelvisual.normals_amp_real.NonManifoldTraversalOff()
		panelvisual.triangles_support.SetInputConnection(panelvisual.normals_support.GetOutputPort())
		panelvisual.strips_support.SetInputConnection(panelvisual.triangles_support.GetOutputPort())
		panelvisual.triangles_amp_real.SetInputConnection(panelvisual.normals_amp_real.GetOutputPort())
		panelvisual.strips_amp_real.SetInputConnection(panelvisual.triangles_amp_real.GetOutputPort())
		panelvisual.mapper_support.SetInputConnection(panelvisual.strips_support.GetOutputPort())
		panelvisual.mapper_support.SetScalarRange(panelvisual.image_phase_real.GetPointData().GetScalars().GetRange())
		panelvisual.mapper_support.SetScalarModeToUsePointData()
		panelvisual.mapper_support.ImmediateModeRenderingOn()
		panelvisual.mapper_support.Modified()
		panelvisual.mapper_support.Update()
		panelvisual.actor_support.GetProperty().SetOpacity(opacity)
		panelvisual.actor_support.SetMapper(panelvisual.mapper_support)
		panelvisual.mapper_amp_real.SetInputConnection(panelvisual.strips_amp_real.GetOutputPort())
		panelvisual.mapper_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		panelvisual.mapper_amp_real.SetScalarRange(panelvisual.image_amp_real.GetPointData().GetScalars().GetRange())
		panelvisual.mapper_amp_real.SetScalarModeToUsePointData()
		panelvisual.mapper_amp_real.ImmediateModeRenderingOn()
		panelvisual.mapper_amp_real.Modified()
		panelvisual.mapper_amp_real.Update()
		panelvisual.actor_amp_real.GetProperty().SetOpacity(1.0)
		panelvisual.actor_amp_real.SetMapper(panelvisual.mapper_amp_real)
		panelvisual.SetPicker()
		panelvisual.renderer_amp_real.RemoveAllViewProps()
		panelvisual.renderer_phase_real.RemoveAllViewProps()
		panelvisual.renderer_amp_recip.RemoveAllViewProps()
		panelvisual.renderer_phase_recip.RemoveAllViewProps()
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_recip)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_recip)
		panelvisual.renWin.GetRenderWindow().Modified()
		panelvisual.renderer_amp_real.AddActor(panelvisual.actor_amp_real)
		panelvisual.renderer_amp_real.AddActor(panelvisual.actor_support)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.scalebar_amp_real)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.textActor)
		panelvisual.renderer_amp_real.SetBackground(r, g, b)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().SetMultiSamples(0)
		panelvisual.renWin.SetInteractorStyle(panelvisual.style3D)
		panelvisual.renderer_amp_real.ResetCamera()
		panelvisual.renWin.SetPicker(panelvisual.picker_amp_real)
		panelvisual.renderer_amp_real.SetViewport(0,0,1,1)
		panelvisual.renderer_amp_recip.SetViewport(1,1,1,1)
		panelvisual.Layout()
		panelvisual.Show()
		if(self.chkbox_axes.GetValue() == True):
			panelvisual.axis.SetBounds(panelvisual.image_amp_real.GetBounds())
			if panelvisual.VTKIsNot6:
				panelvisual.axis.SetInput(panelvisual.image_amp_real)
			else:
				panelvisual.axis.SetInputData(panelvisual.image_amp_real)
			panelvisual.axis.SetCamera(panelvisual.renderer_amp_real.GetActiveCamera())
			panelvisual.axis.SetLabelFormat("%6.1f")
			panelvisual.axis.SetFlyModeToOuterEdges()
			panelvisual.axis.ScalingOff()
			panelvisual.axis.SetFontFactor(float(self.axes_fontfactor.value.GetValue()))
			panelvisual.axis.SetXLabel("X")
			panelvisual.axis.SetYLabel("Y")
			panelvisual.axis.SetZLabel("Z")
			panelvisual.axis.Modified()
			panelvisual.renderer_amp_real.AddViewProp( panelvisual.axis )
	data_file  = self.support.objectpath.GetValue()
	input_file  = self.input_filename.objectpath.GetValue()
	panelvisual = self.ancestor.GetPage(1)
	panelvisual.contour_real.value.SetValue(self.contour.value.GetValue())
	panelvisual.contour_support.value.SetValue(self.contour_support.value.GetValue())
	panelvisual.OnContourSelect(None, forceshow=True)
	r = float(panelvisual.r)/255.0
	g = float(panelvisual.g)/255.0
	b = float(panelvisual.b)/255.0
	try:
		panelvisual.data = LoadArray(self.ancestor.GetPage(0), data_file)
		panelvisual.data_max_support = numpy.abs(panelvisual.data).max()
		panelvisual.inputdata = LoadArray(self.ancestor.GetPage(0), input_file)
		panelvisual.data_max = numpy.abs(panelvisual.inputdata).max()
	except:
		msg = "Could not load array."
		dlg = wx.MessageDialog(self, msg, "Sequence View Array", wx.OK)
		dlg.ShowModal()
		dlg.Destroy()
		return
	else:
		if panelvisual.data.shape[2] == 1:
			pass
		else:
			ViewDataSupport(self, ancestor , panelvisual.data, panelvisual.inputdata, r, g, b)
		panelvisual.datarangelist = []
		panelvisual.ReleaseVisualButtons(gotovisual=True)
		panelvisual.RefreshSceneFull()
def Sequence_Random(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		self.ancestor.GetPage(0).queue_info.put("Preparing random start array...")
		amp_max = float(pipelineitem.amp_max.value.GetValue())
		try:
			self.seqdata
		except AttributeError:
			pass
		else:
			try:
				self.seqdata[:] = amp_max * numpy.random.random_sample(self.seqdata.shape)
				self.ancestor.GetPage(0).queue_info.put("done.")
			except:
				pass
	return
def Sequence_ArrayStart(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Preparing start array...")
		filename_in = pipelineitem.input_filename.objectpath.GetValue()
		try:
				array = LoadArray(self, filename_in)
		except:
			msg = "Could not load array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
		else:
			try:
				if self.seqdata.shape == array.shape:
					self.seqdata[:] = array.copy()
					self.ancestor.GetPage(0).queue_info.put("done.")
				else:
					self.ancestor.GetPage(0).queue_info.put("array shape incorrect. Aborting.")
					self.pipeline_started = False
			except:
				pass
	return
def Sequence_Transform(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		panelvisual = self.ancestor.GetPage(1)
		self.thread_register.put(1)
		self.ancestor.GetPage(0).queue_info.put("Starting transformation...")
		filename_in = pipelineitem.input_filename.objectpath.GetValue()
		filename_out_amp = pipelineitem.output_filename_amp.objectpath.GetValue()
		filename_out_phase = pipelineitem.output_filename_phase.objectpath.GetValue()
		if(pipelineitem.rbfrom.GetStringSelection() == 'Input data file'):
			try:
				array = LoadArray(self, filename_in)
			except:
				msg = "Could not load array."
				wx.CallAfter(self.UserMessage, title, msg)
				self.pipeline_started = False
				self.thread_register.get()
				return
		else:
			if self.seqdata is None:
				msg = "Could not load array."
				wx.CallAfter(self.UserMessage, title, msg)
				self.pipeline_started = False
				self.thread_register.get()
				return
			else:
				array = self.seqdata
		def Transform(self):
			shp = numpy.array(array.shape, dtype=numpy.int)
			R = float(pipelineitem.armln.value.GetValue())
			binx =  float(pipelineitem.bdims[0].value.GetValue())
			biny =  float(pipelineitem.bdims[1].value.GetValue())
			binz =  float(pipelineitem.bdims[2].value.GetValue())
			dx = float(pipelineitem.pixelx.value.GetValue()) * 10.0**(-6)
			dy = float(pipelineitem.pixely.value.GetValue()) * 10.0**(-6)
			waveln = float(pipelineitem.waveln.value.GetValue()) * 10.0**(-9)
			k = 2.0*math.pi/waveln
			twotheta = float(pipelineitem.twotheta.value.GetValue())
			dtheta = float(pipelineitem.dtheta.value.GetValue())
			phi = float(pipelineitem.phi.value.GetValue())
			dphi = float(pipelineitem.dphi.value.GetValue())
			dpx = binx*dx/R
			dpy = biny*dy/R
			Q = k * numpy.array([math.cos(phi)*math.sin(twotheta),math.sin(phi), (math.cos(phi)*math.cos(twotheta) - 1.0) ], dtype=numpy.double)
			Qmag = math.sqrt(numpy.dot(Q,Q))
			dQdx = [-math.sin(phi)*math.sin(twotheta), math.cos(phi), -math.sin(phi)*math.cos(twotheta)]
			dQdy = [math.cos(phi)*math.cos(twotheta), 0.0, -math.cos(phi)*math.sin(twotheta)]
			dQdtheta = [math.cos(phi)*math.cos(twotheta) - 1.0, 0.0, -math.cos(phi)*math.sin(twotheta)]
			dQdphi= [-math.sin(phi)*math.sin(twotheta), math.sin(phi) - 1.0, -math.sin(phi)*math.cos(twotheta)]
			astar = k*dpx * numpy.array(dQdx, dtype=numpy.double)
			bstar = k*dpy * numpy.array(dQdy, dtype=numpy.double)
			if (pipelineitem.rbcurve.GetStringSelection() == 'Theta'):
				cstar = k*dtheta * binz * numpy.array(dQdtheta, dtype=numpy.double)
			if (pipelineitem.rbcurve.GetStringSelection() == 'Phi'):
				cstar = k*dphi * binz * numpy.array(dQdphi, dtype=numpy.double)
			v = numpy.dot(astar,numpy.cross(bstar,cstar))
			if (pipelineitem.rbtype.GetStringSelection() == 'Real-space'):
				a = 2.0*math.pi*numpy.cross(bstar,cstar)/v
				b = 2.0*math.pi*numpy.cross(cstar,astar)/v
				c = 2.0*math.pi*numpy.cross(astar,bstar)/v
				mx = 1.0/float(shp[0])
				my = 1.0/float(shp[1])
				mz = 1.0/float(shp[2])
				nmeter = 10.0**(9)
			else:
				a = astar
				b = bstar
				c = cstar
				mx = 1.0
				my = 1.0
				mz = 1.0
				nmeter = 10.0**(-9)
			T = numpy.vstack((a,b,c)).T
			vtk_dataset = vtk.vtkStructuredGrid()
			flat_data_amp = (numpy.abs(array)).transpose(2,1,0).flatten()
			flat_data_phase = (numpy.angle(array)).transpose(2,1,0).flatten()
			vtk_scalararray_amp = numpy_support.numpy_to_vtk(flat_data_amp)
			vtk_scalararray_phase = numpy_support.numpy_to_vtk(flat_data_phase)
			vtk_points = vtk.vtkPoints()
			if self.coordarray is None:
				self.coordarray = numpy.zeros((array.size,3), dtype=numpy.double)
			vtk_points.SetDataTypeToDouble()
			vtk_points.SetNumberOfPoints(array.size)
			if (pipelineitem.chkbox_ccdflip.GetValue() == True):
				X = numpy.array([[float(shp[0]-x-1)*mx, float(y)*my, float(z)*mz] for z in range(shp[2]) for y in range(shp[1]) for x in range(shp[0])], dtype=numpy.double)
				self.coordarray[:] = nmeter * numpy.dot(T,X.T).T
			else:
				X = numpy.array([[float(x)*mx, float(y)*my, float(z)*mz] for z in range(shp[2]) for y in range(shp[1]) for x in range(shp[0])], dtype=numpy.double)
				self.coordarray[:] = nmeter * numpy.dot(T,X.T).T
			vtk_coordarray = numpy_support.numpy_to_vtk(self.coordarray)
			vtk_points.SetData(vtk_coordarray)
			vtk_dataset.SetPoints(vtk_points)
			vtk_dataset.GetPointData().SetScalars(vtk_scalararray_amp)
			vtk_dataset.SetDimensions(shp)
			vtk_dataset.Modified()
			writer = vtk.vtkStructuredGridWriter()
			writer.SetFileName(filename_out_amp)
			writer.SetFileTypeToBinary()
			if panelvisual.VTKIsNot6:
				writer.SetInput(vtk_dataset)
			else:
				writer.SetInputData(vtk_dataset)
			writer.Update()
			writer.Write()
			vtk_dataset.GetPointData().SetScalars(vtk_scalararray_phase)
			vtk_dataset.Modified()
			writer.SetFileName(filename_out_phase)
			writer.SetFileTypeToBinary()
			if panelvisual.VTKIsNot6:
				writer.SetInput(vtk_dataset)
			else:
				writer.SetInputData(vtk_dataset)
			writer.Update()
			writer.Write()
			self.thread_register.get()
		thd = threading.Thread(target=Transform, args=(self,))
		thd.daemon = True
		thd.start()
		return
def Sequence_Save_Coordinates(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		title = "Sequence " + pipelineitem.treeitem['name']
		self.ancestor.GetPage(0).queue_info.put("Saving coordinates...")
		filename_out = pipelineitem.output_filename.objectpath.GetValue()
		try:
			numpy.save(filename_out, self.coordarray)
		except:
			msg = "Could not save coordinates array."
			wx.CallAfter(self.UserMessage, title, msg)
			self.pipeline_started = False
			return
def Sequence_View_Object(self, ancestor):
	def ViewDataAmp(self, ancestor, data, r, g, b):
		self.ancestor.GetPage(0).queue_info.put("Preparing object visualisation")
		self.ancestor.GetPage(0).queue_info.put("Array Size: " + str(data.shape))
		panelvisual = ancestor.GetPage(1)
		contour = float(self.contour.value.GetValue())
		maxval = numpy.abs(data).max()
		if contour > maxval: contour = CNTR_CLIP*maxval;
		feature_angle = float(self.feature_angle.value.GetValue())
		shp = numpy.array(data.shape, dtype=numpy.int)
		panelvisual.flat_data= (numpy.abs(data)).transpose(2,1,0).flatten();
		panelvisual.vtk_data_array = numpy_support.numpy_to_vtk(panelvisual.flat_data)
		panelvisual.vtk_coordarray = numpy_support.numpy_to_vtk(panelvisual.coords)
		panelvisual.object_amp_points.SetDataTypeToDouble()
		panelvisual.object_amp_points.SetNumberOfPoints(data.size)
		panelvisual.object_amp_points.SetData(panelvisual.vtk_coordarray)
		panelvisual.object_amp.SetPoints(panelvisual.object_amp_points)
		panelvisual.object_amp.GetPointData().SetScalars(panelvisual.vtk_data_array)
		panelvisual.object_amp.SetDimensions(shp)
		panelvisual.object_amp.Modified()
		panelvisual.image_probe = panelvisual.object_amp
		panelvisual.lut_amp_real.SetNumberOfTableValues(256)
		panelvisual.lut_amp_real.SetScaleToLinear()
		panelvisual.lut_amp_real.SetTableRange(panelvisual.object_amp.GetPointData().GetScalars().GetRange())
		lutsource = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[0][0]][1]
		if self.ancestor.GetPage(0).cmls[0][1] == 0:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(255-k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		panelvisual.lut_amp_real.SetRamp(0)
		panelvisual.lut_amp_real.Build()
		panelvisual.scalebar_amp_real.SetTitle("")
		panelvisual.scalebar_amp_real.SetOrientationToVertical()
		panelvisual.scalebar_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		panelvisual.scalebar_amp_real.SetWidth(0.07)
		panelvisual.scalebar_amp_real.SetHeight(0.90)
		panelvisual.scalebar_amp_real.SetPosition(0.01,0.1)
		panelvisual.scalebar_amp_real.Modified()
		if panelvisual.VTKIsNot6:
			panelvisual.filter_amp_real.SetInput(panelvisual.object_amp)
		else:
			panelvisual.filter_amp_real.SetInputData(panelvisual.object_amp)
		panelvisual.filter_amp_real.ComputeNormalsOn()
		panelvisual.filter_amp_real.ComputeScalarsOn()
		panelvisual.filter_amp_real.SetNumberOfContours(1)
		panelvisual.filter_amp_real.SetValue( 0, contour)
		panelvisual.filter_amp_real.Modified()
		panelvisual.filter_amp_real.Update()
		panelvisual.smooth_filter_real.SetInputConnection(panelvisual.filter_amp_real.GetOutputPort())
		panelvisual.smooth_filter_real.SetNumberOfIterations(15)
		panelvisual.smooth_filter_real.SetRelaxationFactor(0.1)
		panelvisual.smooth_filter_real.FeatureEdgeSmoothingOff()
		panelvisual.smooth_filter_real.BoundarySmoothingOn()
		panelvisual.smooth_filter_real.Update()
		panelvisual.normals_amp_real.SetInputConnection(panelvisual.smooth_filter_real.GetOutputPort())
		panelvisual.normals_amp_real.SetFeatureAngle(feature_angle)
		panelvisual.normals_amp_real.ConsistencyOff()
		panelvisual.normals_amp_real.SplittingOff()
		panelvisual.normals_amp_real.AutoOrientNormalsOff()
		panelvisual.normals_amp_real.ComputePointNormalsOn()
		panelvisual.normals_amp_real.ComputeCellNormalsOff()
		panelvisual.normals_amp_real.NonManifoldTraversalOff()
		panelvisual.triangles_amp_real.SetInputConnection(panelvisual.normals_amp_real.GetOutputPort())
		panelvisual.strips_amp_real.SetInputConnection(panelvisual.triangles_amp_real.GetOutputPort())
		panelvisual.mapper_amp_real.SetInputConnection(panelvisual.strips_amp_real.GetOutputPort())
		panelvisual.mapper_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		panelvisual.mapper_amp_real.SetScalarRange(panelvisual.object_amp.GetPointData().GetScalars().GetRange())
		panelvisual.mapper_amp_real.SetScalarModeToUsePointData()
		panelvisual.mapper_amp_real.ImmediateModeRenderingOn()
		panelvisual.mapper_amp_real.Modified()
		panelvisual.mapper_amp_real.Update()
		panelvisual.actor_amp_real.GetProperty().SetOpacity(1.0)
		panelvisual.actor_amp_real.SetMapper(panelvisual.mapper_amp_real)
		panelvisual.SetPicker()
		panelvisual.renderer_amp_real.RemoveAllViewProps()
		panelvisual.renderer_phase_real.RemoveAllViewProps()
		panelvisual.renderer_amp_recip.RemoveAllViewProps()
		panelvisual.renderer_phase_recip.RemoveAllViewProps()
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_recip)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_recip)
		panelvisual.renWin.GetRenderWindow().Modified()
		panelvisual.renderer_amp_real.AddActor(panelvisual.actor_amp_real)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.scalebar_amp_real)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.textActor)
		panelvisual.renderer_amp_real.SetBackground(r, g, b)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().SetMultiSamples(0)
		panelvisual.renWin.SetInteractorStyle(panelvisual.style3D)
		panelvisual.renderer_amp_real.ResetCamera()
		panelvisual.renWin.SetPicker(panelvisual.picker_amp_real)
		panelvisual.renderer_amp_real.SetViewport(0,0,1,1)
		panelvisual.renderer_amp_recip.SetViewport(1,1,1,1)
		panelvisual.Layout()
		panelvisual.Show()
		if(self.chkbox_axes.GetValue() == True):
			panelvisual.axis.SetBounds(panelvisual.object_amp.GetBounds())
			if panelvisual.VTKIsNot6:
				panelvisual.axis.SetInput(panelvisual.object_amp)
			else:
				panelvisual.axis.SetInputData(panelvisual.object_amp)
			panelvisual.axis.SetCamera(panelvisual.renderer_amp_real.GetActiveCamera())
			panelvisual.axis.SetLabelFormat("%6.1f")
			panelvisual.axis.SetFlyModeToOuterEdges()
			panelvisual.axis.ScalingOff()
			panelvisual.axis.SetFontFactor(float(self.axes_fontfactor.value.GetValue()))
			panelvisual.axis.SetXLabel("X")
			panelvisual.axis.SetYLabel("Y")
			panelvisual.axis.SetZLabel("Z")
			panelvisual.axis.Modified()
			panelvisual.renderer_amp_real.AddViewProp( panelvisual.axis )
	def ViewDataPhase(self, ancestor, data, r, g, b):
		self.ancestor.GetPage(0).queue_info.put("Preparing object visualisation")
		self.ancestor.GetPage(0).queue_info.put("Array Size: " + str(data.shape))
		panelvisual = ancestor.GetPage(1)
		phasemax = float(self.phasemax.value.GetValue())
		phasemin = float(self.phasemin.value.GetValue())
		ox = float(self.ox.value.GetValue())
		oy = float(self.oy.value.GetValue())
		oz = float(self.oz.value.GetValue())
		nx = float(self.nx.value.GetValue())
		ny = float(self.ny.value.GetValue())
		nz = float(self.nz.value.GetValue())
		shp = numpy.array(data.shape, dtype=numpy.int)
		panelvisual.flat_data= (numpy.angle(data)).transpose(2,1,0).flatten();
		panelvisual.vtk_data_array = numpy_support.numpy_to_vtk(panelvisual.flat_data)
		panelvisual.vtk_coordarray = numpy_support.numpy_to_vtk(panelvisual.coords)
		panelvisual.object_amp_points.SetDataTypeToDouble()
		panelvisual.object_amp_points.SetNumberOfPoints(data.size)
		panelvisual.object_amp_points.SetData(panelvisual.vtk_coordarray)
		panelvisual.object_phase.SetPoints(panelvisual.object_amp_points)
		panelvisual.object_phase.GetPointData().SetScalars(panelvisual.vtk_data_array)
		panelvisual.object_phase.SetDimensions(shp)
		panelvisual.object_phase.Modified()
		panelvisual.image_probe = panelvisual.object_phase
		panelvisual.lut_phase_real.SetNumberOfTableValues(256)
		panelvisual.lut_phase_real.SetScaleToLinear()
		panelvisual.lut_phase_real.SetTableRange([phasemin,phasemax])
		lutsource = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[1][0]][1]
		if self.ancestor.GetPage(0).cmls[1][1] == 0:
			for k in range(256):
				panelvisual.lut_phase_real.SetTableValue(k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_phase_real.SetTableValue(255-k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		panelvisual.lut_phase_real.SetRamp(0)
		panelvisual.lut_phase_real.Build()
		panelvisual.scalebar_phase_real.SetTitle("")
		panelvisual.scalebar_phase_real.SetOrientationToVertical()
		panelvisual.scalebar_phase_real.SetLookupTable(panelvisual.lut_phase_real)
		panelvisual.scalebar_phase_real.SetWidth(0.07)
		panelvisual.scalebar_phase_real.SetHeight(0.90)
		panelvisual.scalebar_phase_real.SetPosition(0.01,0.1)
		panelvisual.plane.SetOrigin(ox,oy,oz)
		panelvisual.plane.SetNormal(nx,ny,nz)
		if panelvisual.VTKIsNot6:
			panelvisual.cutter.SetInput(panelvisual.object_phase)
		else:
			panelvisual.cutter.SetInputData(panelvisual.object_phase)
		panelvisual.cutter.SetCutFunction(panelvisual.plane)
		panelvisual.cutter.GenerateCutScalarsOff()
		panelvisual.triangles_phase_real.SetInputConnection(panelvisual.cutter.GetOutputPort())
		panelvisual.strips_phase_real.SetInputConnection(panelvisual.triangles_phase_real.GetOutputPort())
		panelvisual.mapper_phase_real.SetInputConnection(panelvisual.strips_phase_real.GetOutputPort())
		panelvisual.mapper_phase_real.SetLookupTable(panelvisual.lut_phase_real)
		panelvisual.mapper_phase_real.SetScalarRange([phasemin,phasemax])
		panelvisual.mapper_phase_real.SetScalarModeToUsePointData()
		panelvisual.mapper_phase_real.ImmediateModeRenderingOn()
		panelvisual.mapper_phase_real.Modified()
		panelvisual.mapper_phase_real.Update()
		panelvisual.actor_phase_real.GetProperty().SetOpacity(1.0)
		panelvisual.actor_phase_real.SetMapper(panelvisual.mapper_phase_real)
		panelvisual.SetPicker()
		panelvisual.renderer_amp_real.RemoveAllViewProps()
		panelvisual.renderer_phase_real.RemoveAllViewProps()
		panelvisual.renderer_amp_recip.RemoveAllViewProps()
		panelvisual.renderer_phase_recip.RemoveAllViewProps()
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_recip)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_recip)
		panelvisual.renWin.GetRenderWindow().Modified()
		panelvisual.renderer_phase_real.AddActor(panelvisual.actor_phase_real)
		panelvisual.renderer_phase_real.AddActor2D(panelvisual.scalebar_phase_real)
		panelvisual.renderer_phase_real.AddActor2D(panelvisual.textActor)
		panelvisual.renderer_phase_real.SetBackground(r, g, b)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().SetMultiSamples(0)
		panelvisual.renWin.SetInteractorStyle(panelvisual.style3D)
		panelvisual.renderer_phase_real.ResetCamera()
		panelvisual.renWin.SetPicker(panelvisual.picker_amp_real)
		panelvisual.renderer_phase_real.SetViewport(0,0,1,1)
		panelvisual.renderer_amp_real.SetViewport(1,1,1,1)
		panelvisual.Layout()
		panelvisual.Show()
		if(self.chkbox_axes.GetValue() == True):
			panelvisual.axis.SetBounds(panelvisual.object_phase.GetBounds())
			if panelvisual.VTKIsNot6:
				panelvisual.axis.SetInput(panelvisual.object_phase)
			else:
				panelvisual.axis.SetInputData(panelvisual.object_phase)
			panelvisual.axis.SetCamera(panelvisual.renderer_phase_real.GetActiveCamera())
			panelvisual.axis.SetLabelFormat("%6.1f")
			panelvisual.axis.SetFlyModeToOuterEdges()
			panelvisual.axis.ScalingOff()
			panelvisual.axis.SetFontFactor(float(self.axes_fontfactor.value.GetValue()))
			panelvisual.axis.SetXLabel("X")
			panelvisual.axis.SetYLabel("Y")
			panelvisual.axis.SetZLabel("Z")
			panelvisual.axis.Modified()
			panelvisual.renderer_phase_real.AddViewProp( panelvisual.axis )
	def ViewDataAmpPhase(self, ancestor, data, r, g, b):
		self.ancestor.GetPage(0).queue_info.put("Preparing object visualisation")
		self.ancestor.GetPage(0).queue_info.put("Array Size: " + str(data.shape))
		panelvisual = ancestor.GetPage(1)
		contour = float(self.contour.value.GetValue())
		maxval = numpy.abs(data).max()
		if contour > maxval: contour = CNTR_CLIP*maxval;
		opacity = float(self.opacity.value.GetValue())
		feature_angle = float(self.feature_angle.value.GetValue())
		phasemax = float(self.phasemax.value.GetValue())
		phasemin = float(self.phasemin.value.GetValue())
		ox = float(self.ox.value.GetValue())
		oy = float(self.oy.value.GetValue())
		oz = float(self.oz.value.GetValue())
		nx = float(self.nx.value.GetValue())
		ny = float(self.ny.value.GetValue())
		nz = float(self.nz.value.GetValue())
		shp = numpy.array(data.shape, dtype=numpy.int)
		panelvisual.flat_data = (numpy.abs(data)).transpose(2,1,0).flatten();
		panelvisual.vtk_data_array = numpy_support.numpy_to_vtk(panelvisual.flat_data)
		panelvisual.vtk_coordarray = numpy_support.numpy_to_vtk(panelvisual.coords)
		panelvisual.object_amp_points.SetDataTypeToDouble()
		panelvisual.object_amp_points.SetNumberOfPoints(data.size)
		panelvisual.object_amp_points.SetData(panelvisual.vtk_coordarray)
		panelvisual.object_amp.SetPoints(panelvisual.object_amp_points)
		panelvisual.object_amp.GetPointData().SetScalars(panelvisual.vtk_data_array)
		panelvisual.object_amp.SetDimensions(shp)
		panelvisual.object_amp.Modified()
		panelvisual.lut_amp_real.SetNumberOfTableValues(256)
		panelvisual.lut_amp_real.SetScaleToLinear()
		panelvisual.lut_amp_real.SetTableRange(panelvisual.object_amp.GetPointData().GetScalars().GetRange())
		lutsource_amp = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[0][0]][1]
		if self.ancestor.GetPage(0).cmls[0][1] == 0:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(k, lutsource_amp[k][0], lutsource_amp[k][1], lutsource_amp[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(255-k, lutsource_amp[k][0], lutsource_amp[k][1], lutsource_amp[k][2], 1)
		panelvisual.lut_amp_real.SetRamp(0)
		panelvisual.lut_amp_real.Build()
		flat_data_phase= (numpy.angle(data)).transpose(2,1,0).flatten();
		vtk_data_array_phase = numpy_support.numpy_to_vtk(flat_data_phase)
		panelvisual.object_phase.SetPoints(panelvisual.object_amp_points)
		panelvisual.object_phase.GetPointData().SetScalars(panelvisual.vtk_data_array_phase)
		panelvisual.object_phase.SetDimensions(shp)
		panelvisual.object_phase.Modified()
		panelvisual.image_probe = panelvisual.object_phase
		panelvisual.lut_phase_real.SetNumberOfTableValues(256)
		panelvisual.lut_phase_real.SetScaleToLinear()
		panelvisual.lut_phase_real.SetTableRange([phasemin,phasemax])
		lutsource_phase = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[1][0]][1]
		if self.ancestor.GetPage(0).cmls[1][1] == 0:
			for k in range(256):
				panelvisual.lut_phase_real.SetTableValue(k, lutsource_phase[k][0], lutsource_phase[k][1], lutsource_phase[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_phase_real.SetTableValue(255-k, lutsource_phase[k][0], lutsource_phase[k][1], lutsource_phase[k][2], 1)
		panelvisual.lut_phase_real.SetRamp(0)
		panelvisual.lut_phase_real.Build()
		panelvisual.scalebar_phase_real.SetTitle("")
		panelvisual.scalebar_phase_real.SetOrientationToVertical()
		panelvisual.scalebar_phase_real.SetLookupTable(panelvisual.lut_phase_real)
		panelvisual.scalebar_phase_real.SetWidth(0.07)
		panelvisual.scalebar_phase_real.SetHeight(0.90)
		panelvisual.scalebar_phase_real.SetPosition(0.01,0.1)
		if panelvisual.VTKIsNot6:
			panelvisual.filter_amp_real.SetInput(panelvisual.object_amp)
		else:
			panelvisual.filter_amp_real.SetInputData(panelvisual.object_amp)
		panelvisual.filter_amp_real.ComputeNormalsOn()
		panelvisual.filter_amp_real.ComputeScalarsOn()
		panelvisual.filter_amp_real.SetNumberOfContours(1)
		panelvisual.filter_amp_real.SetValue( 0, contour)
		panelvisual.filter_amp_real.Modified()
		panelvisual.filter_amp_real.Update()
		panelvisual.smooth_filter_real.SetInputConnection(panelvisual.filter_amp_real.GetOutputPort())
		panelvisual.smooth_filter_real.SetNumberOfIterations(15)
		panelvisual.smooth_filter_real.SetRelaxationFactor(0.1)
		panelvisual.smooth_filter_real.FeatureEdgeSmoothingOff()
		panelvisual.smooth_filter_real.BoundarySmoothingOn()
		panelvisual.smooth_filter_real.Update()
		panelvisual.normals_amp_real.SetInputConnection(panelvisual.smooth_filter_real.GetOutputPort())
		panelvisual.normals_amp_real.SetFeatureAngle(feature_angle)
		panelvisual.normals_amp_real.ConsistencyOff()
		panelvisual.normals_amp_real.SplittingOff()
		panelvisual.normals_amp_real.AutoOrientNormalsOff()
		panelvisual.normals_amp_real.ComputePointNormalsOn()
		panelvisual.normals_amp_real.ComputeCellNormalsOff()
		panelvisual.normals_amp_real.NonManifoldTraversalOff()
		panelvisual.triangles_amp_real.SetInputConnection(panelvisual.normals_amp_real.GetOutputPort())
		panelvisual.strips_amp_real.SetInputConnection(panelvisual.triangles_amp_real.GetOutputPort())
		panelvisual.mapper_amp_real.SetInputConnection(panelvisual.strips_amp_real.GetOutputPort())
		panelvisual.mapper_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		panelvisual.mapper_amp_real.SetScalarRange(panelvisual.object_amp.GetPointData().GetScalars().GetRange())
		panelvisual.mapper_amp_real.SetScalarModeToUsePointData()
		panelvisual.mapper_amp_real.ImmediateModeRenderingOn()
		panelvisual.mapper_amp_real.Modified()
		panelvisual.mapper_amp_real.Update()
		panelvisual.actor_amp_real.GetProperty().SetOpacity(opacity)
		panelvisual.actor_amp_real.SetMapper(panelvisual.mapper_amp_real)
		panelvisual.plane.SetOrigin(ox,oy,oz)
		panelvisual.plane.SetNormal(nx,ny,nz)
		if panelvisual.VTKIsNot6:
			panelvisual.cutter.SetInput(panelvisual.object_phase)
		else:
			panelvisual.cutter.SetInputData(panelvisual.object_phase)
		panelvisual.cutter.SetCutFunction(panelvisual.plane)
		panelvisual.cutter.GenerateCutScalarsOff()
		panelvisual.triangles_phase_real.SetInputConnection(panelvisual.cutter.GetOutputPort())
		panelvisual.strips_phase_real.SetInputConnection(panelvisual.triangles_phase_real.GetOutputPort())
		panelvisual.mapper_phase_real.SetInputConnection(panelvisual.strips_phase_real.GetOutputPort())
		panelvisual.mapper_phase_real.SetLookupTable(panelvisual.lut_phase_real)
		panelvisual.mapper_phase_real.SetScalarRange([phasemin,phasemax])
		panelvisual.mapper_phase_real.SetScalarModeToUsePointData()
		panelvisual.mapper_phase_real.ImmediateModeRenderingOn()
		panelvisual.mapper_phase_real.Modified()
		panelvisual.mapper_phase_real.Update()
		panelvisual.actor_phase_real.SetMapper(panelvisual.mapper_phase_real)
		panelvisual.SetPicker()
		panelvisual.renderer_amp_real.RemoveAllViewProps()
		panelvisual.renderer_phase_real.RemoveAllViewProps()
		panelvisual.renderer_amp_recip.RemoveAllViewProps()
		panelvisual.renderer_phase_recip.RemoveAllViewProps()
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_recip)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_recip)
		panelvisual.renWin.GetRenderWindow().Modified()
		panelvisual.renderer_phase_real.AddActor(panelvisual.actor_phase_real)
		panelvisual.renderer_phase_real.AddActor(panelvisual.actor_amp_real)
		panelvisual.renderer_phase_real.AddActor2D(panelvisual.scalebar_phase_real)
		panelvisual.renderer_phase_real.AddActor2D(panelvisual.textActor)
		panelvisual.renderer_phase_real.SetBackground(r, g, b)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().SetMultiSamples(0)
		panelvisual.renWin.SetInteractorStyle(panelvisual.style3D)
		panelvisual.renderer_phase_real.ResetCamera()
		panelvisual.renWin.SetPicker(panelvisual.picker_amp_real)
		panelvisual.renderer_amp_real.SetViewport(1,1,1,1)
		panelvisual.renderer_phase_real.SetViewport(0,0,1,1)
		panelvisual.Layout()
		panelvisual.Show()
		if(self.chkbox_axes.GetValue() == True):
			panelvisual.axis.SetBounds(panelvisual.object_amp.GetBounds())
			if panelvisual.VTKIsNot6:
				panelvisual.axis.SetInput(panelvisual.object_amp)
			else:
				panelvisual.axis.SetInputData(panelvisual.object_amp)
			panelvisual.axis.SetCamera(panelvisual.renderer_phase_real.GetActiveCamera())
			panelvisual.axis.SetLabelFormat("%6.1f")
			panelvisual.axis.SetFlyModeToOuterEdges()
			panelvisual.axis.ScalingOff()
			panelvisual.axis.SetFontFactor(float(self.axes_fontfactor.value.GetValue()))
			panelvisual.axis.SetXLabel("X")
			panelvisual.axis.SetYLabel("Y")
			panelvisual.axis.SetZLabel("Z")
			panelvisual.axis.Modified()
			panelvisual.renderer_phase_real.AddViewProp( panelvisual.axis )
	def ViewDataAmpWPhase(self, ancestor, data, r, g, b):
		self.ancestor.GetPage(0).queue_info.put("Preparing object visualisation")
		self.ancestor.GetPage(0).queue_info.put("Array Size: " + str(data.shape))
		panelvisual = ancestor.GetPage(1)
		contour = float(self.contour.value.GetValue())
		maxval = numpy.abs(data).max()
		if contour > maxval: contour = CNTR_CLIP*maxval;
		feature_angle = float(self.feature_angle.value.GetValue())
		phasemax = float(self.phasemax.value.GetValue())
		phasemin = float(self.phasemin.value.GetValue())
		panelvisual.flat_data_phase= (numpy.angle(data)).transpose(2,1,0).flatten();
		panelvisual.vtk_data_array_phase = numpy_support.numpy_to_vtk(panelvisual.flat_data_phase)
		panelvisual.vtk_data_array_phase.SetName("mapscalar")
		shp = numpy.array(data.shape, dtype=numpy.int)
		panelvisual.flat_data= (numpy.abs(data)).transpose(2,1,0).flatten();
		panelvisual.vtk_data_array = numpy_support.numpy_to_vtk(panelvisual.flat_data)
		panelvisual.vtk_coordarray = numpy_support.numpy_to_vtk(panelvisual.coords)
		panelvisual.object_amp_points.SetDataTypeToDouble()
		panelvisual.object_amp_points.SetNumberOfPoints(data.size)
		panelvisual.object_amp_points.SetData(panelvisual.vtk_coordarray)
		panelvisual.object_amp.SetPoints(panelvisual.object_amp_points)
		panelvisual.object_amp.GetPointData().SetScalars(panelvisual.vtk_data_array)
		panelvisual.object_amp.GetPointData().AddArray(panelvisual.vtk_data_array_phase)
		panelvisual.object_amp.SetDimensions(shp)
		panelvisual.object_amp.Modified()
		panelvisual.object_phase.SetPoints(panelvisual.object_amp_points)
		panelvisual.object_phase.GetPointData().SetScalars(panelvisual.vtk_data_array_phase)
		panelvisual.object_phase.SetDimensions(shp)
		panelvisual.object_phase.Modified()
		panelvisual.image_probe = panelvisual.object_phase
		panelvisual.lut_amp_real.SetNumberOfTableValues(256)
		panelvisual.lut_amp_real.SetScaleToLinear()
		panelvisual.lut_amp_real.SetTableRange([phasemin,phasemax])
		lutsource = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[1][0]][1]
		if self.ancestor.GetPage(0).cmls[1][1] == 0:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(255-k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		panelvisual.lut_amp_real.SetRamp(0)
		panelvisual.lut_amp_real.Build()
		panelvisual.scalebar_amp_real.SetTitle("")
		panelvisual.scalebar_amp_real.SetOrientationToVertical()
		panelvisual.scalebar_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		panelvisual.scalebar_amp_real.SetWidth(0.07)
		panelvisual.scalebar_amp_real.SetHeight(0.90)
		panelvisual.scalebar_amp_real.SetPosition(0.01,0.1)
		if panelvisual.VTKIsNot6:
			panelvisual.filter_amp_real.SetInput(panelvisual.object_amp)
		else:
			panelvisual.filter_amp_real.SetInputData(panelvisual.object_amp)
		panelvisual.filter_amp_real.ComputeNormalsOn()
		panelvisual.filter_amp_real.ComputeScalarsOn()
		panelvisual.filter_amp_real.SetNumberOfContours(1)
		panelvisual.filter_amp_real.SetValue( 0, contour)
		panelvisual.filter_amp_real.Modified()
		panelvisual.filter_amp_real.Update()
		panelvisual.smooth_filter_real.SetInputConnection(panelvisual.filter_amp_real.GetOutputPort())
		panelvisual.smooth_filter_real.SetNumberOfIterations(15)
		panelvisual.smooth_filter_real.SetRelaxationFactor(0.1)
		panelvisual.smooth_filter_real.FeatureEdgeSmoothingOff()
		panelvisual.smooth_filter_real.BoundarySmoothingOn()
		panelvisual.smooth_filter_real.Update()
		panelvisual.normals_amp_real.SetInputConnection(panelvisual.smooth_filter_real.GetOutputPort())
		panelvisual.normals_amp_real.SetFeatureAngle(feature_angle)
		panelvisual.normals_amp_real.ConsistencyOff()
		panelvisual.normals_amp_real.SplittingOff()
		panelvisual.normals_amp_real.AutoOrientNormalsOff()
		panelvisual.normals_amp_real.ComputePointNormalsOn()
		panelvisual.normals_amp_real.ComputeCellNormalsOff()
		panelvisual.normals_amp_real.NonManifoldTraversalOff()
		panelvisual.triangles_amp_real.SetInputConnection(panelvisual.normals_amp_real.GetOutputPort())
		panelvisual.strips_amp_real.SetInputConnection(panelvisual.triangles_amp_real.GetOutputPort())
		panelvisual.mapper_amp_real.SetInputConnection(panelvisual.strips_amp_real.GetOutputPort())
		panelvisual.mapper_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		panelvisual.mapper_amp_real.SetScalarRange([phasemin,phasemax])
		panelvisual.mapper_amp_real.SetScalarModeToUsePointFieldData()
		panelvisual.mapper_amp_real.SelectColorArray("mapscalar")
		panelvisual.mapper_amp_real.ImmediateModeRenderingOn()
		panelvisual.mapper_amp_real.Modified()
		panelvisual.mapper_amp_real.Update()
		panelvisual.actor_amp_real.GetProperty().SetOpacity(1.0)
		panelvisual.actor_amp_real.SetMapper(panelvisual.mapper_amp_real)
		panelvisual.SetPicker()
		panelvisual.renderer_amp_real.RemoveAllViewProps()
		panelvisual.renderer_phase_real.RemoveAllViewProps()
		panelvisual.renderer_amp_recip.RemoveAllViewProps()
		panelvisual.renderer_phase_recip.RemoveAllViewProps()
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_recip)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_recip)
		panelvisual.renWin.GetRenderWindow().Modified()
		panelvisual.renderer_amp_real.AddActor(panelvisual.actor_amp_real)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.scalebar_amp_real)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.textActor)
		panelvisual.renderer_amp_real.SetBackground(r, g, b)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().SetMultiSamples(0)
		panelvisual.renWin.SetInteractorStyle(panelvisual.style3D)
		panelvisual.renderer_amp_real.ResetCamera()
		panelvisual.renWin.SetPicker(panelvisual.picker_amp_real)
		panelvisual.renderer_amp_real.SetViewport(0,0,1,1)
		panelvisual.renderer_phase_real.SetViewport(1,1,1,1)
		panelvisual.Layout()
		panelvisual.Show()
		if(self.chkbox_axes.GetValue() == True):
			panelvisual.axis.SetBounds(panelvisual.object_amp.GetBounds())
			if panelvisual.VTKIsNot6:
				panelvisual.axis.SetInput(panelvisual.object_amp)
			else:
				panelvisual.axis.SetInputData(panelvisual.object_amp)
			panelvisual.axis.SetCamera(panelvisual.renderer_amp_real.GetActiveCamera())
			panelvisual.axis.SetLabelFormat("%6.1f")
			panelvisual.axis.SetFlyModeToOuterEdges()
			panelvisual.axis.ScalingOff()
			panelvisual.axis.SetFontFactor(float(self.axes_fontfactor.value.GetValue()))
			panelvisual.axis.SetXLabel("X")
			panelvisual.axis.SetYLabel("Y")
			panelvisual.axis.SetZLabel("Z")
			panelvisual.axis.Modified()
			panelvisual.renderer_amp_real.AddViewProp( panelvisual.axis )
	def ViewAmpPlane(self, ancestor, data, r, g, b):
		self.ancestor.GetPage(0).queue_info.put("Preparing object visualisation")
		self.ancestor.GetPage(0).queue_info.put("Array Size: " + str(data.shape))
		panelvisual = ancestor.GetPage(1)
		ox = float(self.ox.value.GetValue())
		oy = float(self.oy.value.GetValue())
		oz = float(self.oz.value.GetValue())
		nx = float(self.nx.value.GetValue())
		ny = float(self.ny.value.GetValue())
		nz = float(self.nz.value.GetValue())
		shp = numpy.array(data.shape, dtype=numpy.int)
		panelvisual.flat_data= (numpy.abs(data)).transpose(2,1,0).flatten();
		panelvisual.vtk_data_array = numpy_support.numpy_to_vtk(panelvisual.flat_data)
		panelvisual.vtk_coordarray = numpy_support.numpy_to_vtk(panelvisual.coords)
		panelvisual.object_amp_points.SetDataTypeToDouble()
		panelvisual.object_amp_points.SetNumberOfPoints(data.size)
		panelvisual.object_amp_points.SetData(panelvisual.vtk_coordarray)
		panelvisual.object_amp.SetPoints(panelvisual.object_amp_points)
		panelvisual.object_amp.GetPointData().SetScalars(panelvisual.vtk_data_array)
		panelvisual.object_amp.SetDimensions(shp)
		panelvisual.object_amp.Modified()
		panelvisual.image_probe = panelvisual.object_amp
		lutsource = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[0][0]][1]
		if self.ancestor.GetPage(0).cmls[0][1] == 0:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(255-k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		panelvisual.lut_amp_real.SetRamp(0)
		panelvisual.lut_amp_real.Build()
		panelvisual.scalebar_amp_real.SetTitle("")
		panelvisual.scalebar_amp_real.SetOrientationToVertical()
		panelvisual.scalebar_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		panelvisual.scalebar_amp_real.SetWidth(0.07)
		panelvisual.scalebar_amp_real.SetHeight(0.90)
		panelvisual.scalebar_amp_real.SetPosition(0.01,0.1)
		panelvisual.plane.SetOrigin(ox,oy,oz)
		panelvisual.plane.SetNormal(nx,ny,nz)
		if panelvisual.VTKIsNot6:
			panelvisual.cutter.SetInput(panelvisual.object_amp)
		else:
			panelvisual.cutter.SetInputData(panelvisual.object_amp)
		panelvisual.cutter.SetCutFunction(panelvisual.plane)
		panelvisual.cutter.GenerateCutScalarsOff()
		panelvisual.triangles_amp_real.SetInputConnection(panelvisual.cutter.GetOutputPort())
		panelvisual.strips_amp_real.SetInputConnection(panelvisual.triangles_amp_real.GetOutputPort())
		panelvisual.mapper_amp_real.SetInputConnection(panelvisual.strips_amp_real.GetOutputPort())
		panelvisual.mapper_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		panelvisual.mapper_amp_real.SetScalarRange(panelvisual.object_amp.GetPointData().GetScalars().GetRange())
		panelvisual.mapper_amp_real.ImmediateModeRenderingOn()
		panelvisual.mapper_amp_real.Modified()
		panelvisual.actor_amp_real.GetProperty().SetOpacity(1.0)
		panelvisual.actor_amp_real.SetMapper(panelvisual.mapper_amp_real)
		panelvisual.SetPicker()
		panelvisual.renderer_amp_real.RemoveAllViewProps()
		panelvisual.renderer_phase_real.RemoveAllViewProps()
		panelvisual.renderer_amp_recip.RemoveAllViewProps()
		panelvisual.renderer_phase_recip.RemoveAllViewProps()
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_recip)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_recip)
		panelvisual.renWin.GetRenderWindow().Modified()
		panelvisual.renderer_amp_real.AddActor(panelvisual.actor_amp_real)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.scalebar_amp_real)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.textActor)
		panelvisual.renderer_amp_real.SetBackground(r, g, b)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().SetMultiSamples(0)
		panelvisual.renWin.SetInteractorStyle(panelvisual.style3D)
		panelvisual.renderer_amp_real.ResetCamera()
		panelvisual.renWin.SetPicker(panelvisual.picker_amp_real)
		panelvisual.renderer_amp_real.SetViewport(0,0,1,1)
		panelvisual.Layout()
		panelvisual.Show()
		if(self.chkbox_axes.GetValue() == True):
			panelvisual.axis.SetBounds(panelvisual.object_amp.GetBounds())
			if panelvisual.VTKIsNot6:
				panelvisual.axis.SetInput(panelvisual.object_amp)
			else:
				panelvisual.axis.SetInputData(panelvisual.object_amp)
			panelvisual.axis.SetCamera(panelvisual.renderer_amp_real.GetActiveCamera())
			panelvisual.axis.SetLabelFormat("%6.1f")
			panelvisual.axis.SetFlyModeToOuterEdges()
			panelvisual.axis.ScalingOff()
			panelvisual.axis.SetFontFactor(float(self.axes_fontfactor.value.GetValue()))
			panelvisual.axis.SetXLabel("X")
			panelvisual.axis.SetYLabel("Y")
			panelvisual.axis.SetZLabel("Z")
			panelvisual.axis.Modified()
			panelvisual.renderer_amp_real.AddViewProp( panelvisual.axis )
	data_file  = self.input_filename.objectpath.GetValue()
	coords_file  = self.coords_filename.objectpath.GetValue()
	panelvisual = self.ancestor.GetPage(1)
	panelvisual.contour_real.value.SetValue(self.contour.value.GetValue())
	panelvisual.OnContourSelect(None, forceshow=True)
	r = float(panelvisual.r)/255.0
	g = float(panelvisual.g)/255.0
	b = float(panelvisual.b)/255.0
	try:
		panelvisual.data = LoadArray(self.ancestor.GetPage(0), data_file)
		panelvisual.data_max = numpy.abs(panelvisual.data).max()
		panelvisual.coords = LoadCoordsArray(self.ancestor.GetPage(0), coords_file)
	except:
		msg = "Could not load array."
		dlg = wx.MessageDialog(self, msg, "Sequence View Object", wx.OK)
		dlg.ShowModal()
		dlg.Destroy()
		return
	else:
		if (self.rbampphase.GetStringSelection() == 'Amplitude'):
			ViewDataAmp(self, ancestor , panelvisual.data, r, g, b)
		if (self.rbampphase.GetStringSelection() == 'Phase'):
			ViewDataPhase(self, ancestor , panelvisual.data, r, g, b)
		if (self.rbampphase.GetStringSelection() == 'Amplitude and Phase'):
			ViewDataAmpPhase(self, ancestor , panelvisual.data, r, g, b)
		if (self.rbampphase.GetStringSelection() == 'Amplitude with Phase'):
			ViewDataAmpWPhase(self, ancestor , panelvisual.data, r, g, b)
		if (self.rbampphase.GetStringSelection() == 'Amplitude (cut plane)'):
			ViewAmpPlane(self, ancestor , panelvisual.data, r, g, b)
		panelvisual.datarangelist = []
		panelvisual.ReleaseVisualButtons(gotovisual=True)
		panelvisual.button_vremove.Enable(False)
		panelvisual.RefreshSceneFull()
def Sequence_View_VTK(self, ancestor):
	def ViewDataAmp(self, ancestor, image, r, g, b):
		self.ancestor.GetPage(0).queue_info.put("Preparing 3D array visualisation")
		panelvisual = ancestor.GetPage(1)
		contour = float(self.contour.value.GetValue())
		maxval = image.GetScalarRange()[1]
		if contour > maxval: contour = CNTR_CLIP*maxval;
		feature_angle = float(self.feature_angle.value.GetValue())
		panelvisual.image_amp_real_vtk = image
		panelvisual.image_probe = panelvisual.image_amp_real_vtk
		panelvisual.lut_amp_real.SetNumberOfTableValues(256)
		panelvisual.lut_amp_real.SetScaleToLinear()
		panelvisual.lut_amp_real.SetTableRange(panelvisual.image_amp_real_vtk.GetPointData().GetScalars().GetRange())
		lutsource = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[0][0]][1]
		if self.ancestor.GetPage(0).cmls[0][1] == 0:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(255-k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		panelvisual.lut_amp_real.SetRamp(0)
		panelvisual.lut_amp_real.Build()
		panelvisual.scalebar_amp_real.SetTitle("")
		panelvisual.scalebar_amp_real.SetOrientationToVertical()
		panelvisual.scalebar_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		panelvisual.scalebar_amp_real.SetWidth(0.07)
		panelvisual.scalebar_amp_real.SetHeight(0.90)
		panelvisual.scalebar_amp_real.SetPosition(0.01,0.1)
		panelvisual.scalebar_amp_real.Modified()
		if panelvisual.VTKIsNot6:
			panelvisual.filter_amp_real.SetInput(panelvisual.image_amp_real_vtk)
		else:
			panelvisual.filter_amp_real.SetInputData(panelvisual.image_amp_real_vtk)
		panelvisual.filter_amp_real.ComputeNormalsOn()
		panelvisual.filter_amp_real.ComputeScalarsOn()
		panelvisual.filter_amp_real.SetNumberOfContours(1)
		panelvisual.filter_amp_real.SetValue( 0, contour)
		panelvisual.filter_amp_real.Modified()
		panelvisual.filter_amp_real.Update()
		panelvisual.smooth_filter_real.SetInputConnection(panelvisual.filter_amp_real.GetOutputPort())
		panelvisual.smooth_filter_real.SetNumberOfIterations(15)
		panelvisual.smooth_filter_real.SetRelaxationFactor(0.1)
		panelvisual.smooth_filter_real.FeatureEdgeSmoothingOff()
		panelvisual.smooth_filter_real.BoundarySmoothingOn()
		panelvisual.smooth_filter_real.Update()
		panelvisual.normals_amp_real.SetInputConnection(panelvisual.smooth_filter_real.GetOutputPort())
		panelvisual.normals_amp_real.SetFeatureAngle(feature_angle)
		panelvisual.normals_amp_real.ConsistencyOff()
		panelvisual.normals_amp_real.SplittingOff()
		panelvisual.normals_amp_real.AutoOrientNormalsOff()
		panelvisual.normals_amp_real.ComputePointNormalsOn()
		panelvisual.normals_amp_real.ComputeCellNormalsOff()
		panelvisual.normals_amp_real.NonManifoldTraversalOff()
		panelvisual.triangles_amp_real.SetInputConnection(panelvisual.normals_amp_real.GetOutputPort())
		panelvisual.strips_amp_real.SetInputConnection(panelvisual.triangles_amp_real.GetOutputPort())
		panelvisual.mapper_amp_real.SetInputConnection(panelvisual.strips_amp_real.GetOutputPort())
		panelvisual.mapper_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		panelvisual.mapper_amp_real.SetScalarRange(panelvisual.image_amp_real_vtk.GetPointData().GetScalars().GetRange())
		panelvisual.mapper_amp_real.SetScalarModeToUsePointData()
		panelvisual.mapper_amp_real.ImmediateModeRenderingOn()
		panelvisual.mapper_amp_real.Modified()
		panelvisual.mapper_amp_real.Update()
		panelvisual.actor_amp_real.GetProperty().SetOpacity(1.0)
		panelvisual.actor_amp_real.SetMapper(panelvisual.mapper_amp_real)
		panelvisual.SetPicker()
		panelvisual.renderer_amp_real.RemoveAllViewProps()
		panelvisual.renderer_phase_real.RemoveAllViewProps()
		panelvisual.renderer_amp_recip.RemoveAllViewProps()
		panelvisual.renderer_phase_recip.RemoveAllViewProps()
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_recip)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_recip)
		panelvisual.renWin.GetRenderWindow().Modified()
		panelvisual.renderer_amp_real.AddActor(panelvisual.actor_amp_real)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.scalebar_amp_real)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.textActor)
		panelvisual.renderer_amp_real.SetBackground(r, g, b)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().SetMultiSamples(0)
		panelvisual.renWin.SetInteractorStyle(panelvisual.style3D)
		panelvisual.renderer_amp_real.ResetCamera()
		panelvisual.renWin.SetPicker(panelvisual.picker_amp_real)
		panelvisual.renderer_amp_real.SetViewport(0,0,1,1)
		panelvisual.renderer_amp_recip.SetViewport(1,1,1,1)
		panelvisual.Layout()
		panelvisual.Show()
		if(self.chkbox_axes.GetValue() == True):
			panelvisual.axis.SetBounds(panelvisual.image_amp_real_vtk.GetBounds())
			if panelvisual.VTKIsNot6:
				panelvisual.axis.SetInput(panelvisual.image_amp_real_vtk)
			else:
				panelvisual.axis.SetInputData(panelvisual.image_amp_real_vtk)
			panelvisual.axis.SetCamera(panelvisual.renderer_amp_real.GetActiveCamera())
			panelvisual.axis.SetLabelFormat("%6.1f")
			panelvisual.axis.SetFlyModeToOuterEdges()
			panelvisual.axis.ScalingOff()
			panelvisual.axis.SetFontFactor(float(self.axes_fontfactor.value.GetValue()))
			panelvisual.axis.SetXLabel("X")
			panelvisual.axis.SetYLabel("Y")
			panelvisual.axis.SetZLabel("Z")
			panelvisual.axis.Modified()
			panelvisual.renderer_amp_real.AddViewProp( panelvisual.axis )
	def ViewDataPhase(self, ancestor, image, r, g, b):
		self.ancestor.GetPage(0).queue_info.put("Preparing 3D array visualisation")
		panelvisual = ancestor.GetPage(1)
		phasemax = float(self.phasemax.value.GetValue())
		phasemin = float(self.phasemin.value.GetValue())
		ox = float(self.ox.value.GetValue())
		oy = float(self.oy.value.GetValue())
		oz = float(self.oz.value.GetValue())
		nx = float(self.nx.value.GetValue())
		ny = float(self.ny.value.GetValue())
		nz = float(self.nz.value.GetValue())
		panelvisual.image_phase_real_vtk = image
		panelvisual.image_probe = panelvisual.image_phase_real_vtk
		panelvisual.lut_phase_real.SetNumberOfTableValues(256)
		panelvisual.lut_phase_real.SetScaleToLinear()
		panelvisual.lut_phase_real.SetTableRange([phasemin,phasemax])
		lutsource = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[1][0]][1]
		if self.ancestor.GetPage(0).cmls[1][1] == 0:
			for k in range(256):
				panelvisual.lut_phase_real.SetTableValue(k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_phase_real.SetTableValue(255-k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		panelvisual.lut_phase_real.SetRamp(0)
		panelvisual.lut_phase_real.Build()
		panelvisual.scalebar_phase_real.SetTitle("")
		panelvisual.scalebar_phase_real.SetOrientationToVertical()
		panelvisual.scalebar_phase_real.SetLookupTable(panelvisual.lut_phase_real)
		panelvisual.scalebar_phase_real.SetWidth(0.07)
		panelvisual.scalebar_phase_real.SetHeight(0.90)
		panelvisual.scalebar_phase_real.SetPosition(0.01,0.1)
		panelvisual.plane.SetOrigin(ox,oy,oz)
		panelvisual.plane.SetNormal(nx,ny,nz)
		if panelvisual.VTKIsNot6:
			panelvisual.cutter.SetInput(panelvisual.image_phase_real_vtk)
		else:
			panelvisual.cutter.SetInputData(panelvisual.image_phase_real_vtk)
		panelvisual.cutter.SetCutFunction(panelvisual.plane)
		panelvisual.cutter.GenerateCutScalarsOff()
		panelvisual.triangles_phase_real.SetInputConnection(panelvisual.cutter.GetOutputPort())
		panelvisual.strips_phase_real.SetInputConnection(panelvisual.triangles_phase_real.GetOutputPort())
		panelvisual.mapper_phase_real.SetInputConnection(panelvisual.strips_phase_real.GetOutputPort())
		panelvisual.mapper_phase_real.SetLookupTable(panelvisual.lut_phase_real)
		panelvisual.mapper_phase_real.SetScalarRange([phasemin,phasemax])
		panelvisual.mapper_phase_real.SetScalarModeToUsePointData()
		panelvisual.mapper_phase_real.ImmediateModeRenderingOn()
		panelvisual.mapper_phase_real.Modified()
		panelvisual.mapper_phase_real.Update()
		panelvisual.actor_phase_real.GetProperty().SetOpacity(1.0)
		panelvisual.actor_phase_real.SetMapper(panelvisual.mapper_phase_real)
		panelvisual.SetPicker()
		panelvisual.renderer_amp_real.RemoveAllViewProps()
		panelvisual.renderer_phase_real.RemoveAllViewProps()
		panelvisual.renderer_amp_recip.RemoveAllViewProps()
		panelvisual.renderer_phase_recip.RemoveAllViewProps()
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_recip)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_recip)
		panelvisual.renWin.GetRenderWindow().Modified()
		panelvisual.renderer_phase_real.AddActor(panelvisual.actor_phase_real)
		panelvisual.renderer_phase_real.AddActor2D(panelvisual.scalebar_phase_real)
		panelvisual.renderer_phase_real.AddActor2D(panelvisual.textActor)
		panelvisual.renderer_phase_real.SetBackground(r, g, b)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().SetMultiSamples(0)
		panelvisual.renWin.SetInteractorStyle(panelvisual.style3D)
		panelvisual.renderer_phase_real.ResetCamera()
		panelvisual.renWin.SetPicker(panelvisual.picker_amp_real)
		panelvisual.renderer_phase_real.SetViewport(0,0,1,1)
		panelvisual.renderer_amp_real.SetViewport(1,1,1,1)
		panelvisual.Layout()
		panelvisual.Show()
		if(self.chkbox_axes.GetValue() == True):
			panelvisual.axis.SetBounds(panelvisual.image_phase_real_vtk.GetBounds())
			if panelvisual.VTKIsNot6:
				panelvisual.axis.SetInput(panelvisual.image_phase_real_vtk)
			else:
				panelvisual.axis.SetInputData(panelvisual.image_phase_real_vtk)
			panelvisual.axis.SetCamera(panelvisual.renderer_phase_real.GetActiveCamera())
			panelvisual.axis.SetLabelFormat("%6.1f")
			panelvisual.axis.SetFlyModeToOuterEdges()
			panelvisual.axis.ScalingOff()
			panelvisual.axis.SetFontFactor(float(self.axes_fontfactor.value.GetValue()))
			panelvisual.axis.SetXLabel("X")
			panelvisual.axis.SetYLabel("Y")
			panelvisual.axis.SetZLabel("Z")
			panelvisual.axis.Modified()
			panelvisual.renderer_phase_real.AddViewProp( panelvisual.axis )
	def ViewAmpPlane(self, ancestor, image, r, g, b):
		self.ancestor.GetPage(0).queue_info.put("Preparing 3D array visualisation")
		panelvisual = ancestor.GetPage(1)
		ox = float(self.ox.value.GetValue())
		oy = float(self.oy.value.GetValue())
		oz = float(self.oz.value.GetValue())
		nx = float(self.nx.value.GetValue())
		ny = float(self.ny.value.GetValue())
		nz = float(self.nz.value.GetValue())
		panelvisual.image_amp_real_vtk = image
		panelvisual.image_probe = panelvisual.image_amp_real_vtk
		panelvisual.lut_amp_real.SetNumberOfTableValues(256)
		panelvisual.lut_amp_real.SetScaleToLinear()
		panelvisual.lut_amp_real.SetTableRange(panelvisual.image_amp_real_vtk.GetPointData().GetScalars().GetRange())
		lutsource = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[0][0]][1]
		if self.ancestor.GetPage(0).cmls[0][1] == 0:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(255-k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		panelvisual.lut_amp_real.SetRamp(0)
		panelvisual.lut_amp_real.Build()
		panelvisual.scalebar_amp_real.SetTitle("")
		panelvisual.scalebar_amp_real.SetOrientationToVertical()
		panelvisual.scalebar_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		panelvisual.scalebar_amp_real.SetWidth(0.07)
		panelvisual.scalebar_amp_real.SetHeight(0.90)
		panelvisual.scalebar_amp_real.SetPosition(0.01,0.1)
		panelvisual.plane.SetOrigin(ox,oy,oz)
		panelvisual.plane.SetNormal(nx,ny,nz)
		if panelvisual.VTKIsNot6:
			panelvisual.cutter.SetInput(panelvisual.image_amp_real_vtk)
		else:
			panelvisual.cutter.SetInputData(panelvisual.image_amp_real_vtk)
		panelvisual.cutter.SetCutFunction(panelvisual.plane)
		panelvisual.cutter.GenerateCutScalarsOff()
		panelvisual.triangles_amp_real.SetInputConnection(panelvisual.cutter.GetOutputPort())
		panelvisual.strips_amp_real.SetInputConnection(panelvisual.triangles_amp_real.GetOutputPort())
		panelvisual.mapper_amp_real.SetInputConnection(panelvisual.strips_amp_real.GetOutputPort())
		panelvisual.mapper_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		panelvisual.mapper_amp_real.SetScalarRange(panelvisual.image_amp_real_vtk.GetPointData().GetScalars().GetRange())
		panelvisual.mapper_amp_real.ImmediateModeRenderingOn()
		panelvisual.mapper_amp_real.Modified()
		panelvisual.actor_amp_real.GetProperty().SetOpacity(1.0)
		panelvisual.actor_amp_real.SetMapper(panelvisual.mapper_amp_real)
		panelvisual.SetPicker()
		panelvisual.renderer_amp_real.RemoveAllViewProps()
		panelvisual.renderer_phase_real.RemoveAllViewProps()
		panelvisual.renderer_amp_recip.RemoveAllViewProps()
		panelvisual.renderer_phase_recip.RemoveAllViewProps()
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_recip)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_recip)
		panelvisual.renWin.GetRenderWindow().Modified()
		panelvisual.renderer_amp_real.AddActor(panelvisual.actor_amp_real)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.scalebar_amp_real)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.textActor)
		panelvisual.renderer_amp_real.SetBackground(r, g, b)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().SetMultiSamples(0)
		panelvisual.renWin.SetInteractorStyle(panelvisual.style3D)
		panelvisual.renderer_amp_real.ResetCamera()
		panelvisual.renWin.SetPicker(panelvisual.picker_amp_real)
		panelvisual.renderer_amp_real.SetViewport(0,0,1,1)
		panelvisual.Layout()
		panelvisual.Show()
		if(self.chkbox_axes.GetValue() == True):
			panelvisual.axis.SetBounds(panelvisual.image_amp_real_vtk.GetBounds())
			if panelvisual.VTKIsNot6:
				panelvisual.axis.SetInput(panelvisual.image_amp_real_vtk)
			else:
				panelvisual.axis.SetInputData(panelvisual.image_amp_real_vtk)
			panelvisual.axis.SetCamera(panelvisual.renderer_amp_real.GetActiveCamera())
			panelvisual.axis.SetLabelFormat("%6.1f")
			panelvisual.axis.SetFlyModeToOuterEdges()
			panelvisual.axis.ScalingOff()
			panelvisual.axis.SetFontFactor(float(self.axes_fontfactor.value.GetValue()))
			panelvisual.axis.SetXLabel("X")
			panelvisual.axis.SetYLabel("Y")
			panelvisual.axis.SetZLabel("Z")
			panelvisual.axis.Modified()
			panelvisual.renderer_amp_real.AddViewProp( panelvisual.axis )
	def ViewDataAmp2D(self, ancestor, data, r, g, b):
		self.ancestor.GetPage(0).queue_info.put("Preparing 2D array visualisation")
		self.ancestor.GetPage(0).queue_info.put("Array Size: " + str(data.GetDimensions()))
		panelvisual = ancestor.GetPage(1)
		panelvisual.image2D_amp_real_vtk = data
		panelvisual.image2D_amp_real_vtk.Modified()
		panelvisual.image_probe = panelvisual.image2D_amp_real_vtk
		panelvisual.lut_amp_real.SetNumberOfTableValues(256)
		panelvisual.lut_amp_real.SetScaleToLinear()
		panelvisual.lut_amp_real.SetTableRange(panelvisual.image2D_amp_real_vtk.GetPointData().GetScalars().GetRange())
		lutsource = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[0][0]][1]
		if self.ancestor.GetPage(0).cmls[0][1] == 0:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(255-k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		panelvisual.lut_amp_real.SetRamp(0)
		panelvisual.lut_amp_real.Build()
		panelvisual.scalebar_amp_real.SetTitle("")
		panelvisual.scalebar_amp_real.SetOrientationToVertical()
		panelvisual.scalebar_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		panelvisual.scalebar_amp_real.SetWidth(0.07)
		panelvisual.scalebar_amp_real.SetHeight(0.90)
		panelvisual.scalebar_amp_real.SetPosition(0.01,0.1)
		panelvisual.color_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		if panelvisual.VTKIsNot6:
			panelvisual.color_amp_real.SetInput(panelvisual.image2D_amp_real_vtk)
		else:
			panelvisual.color_amp_real.SetInputData(panelvisual.image2D_amp_real_vtk)
		panelvisual.color_amp_real.Update()
		if panelvisual.VTKIsNot6:
			panelvisual.mapper2D_amp_real.SetInputConnection(panelvisual.color_amp_real.GetOutputPort())
			panelvisual.actor2D_amp_real.SetInput(panelvisual.mapper2D_amp_real.GetInput())
		else:
			panelvisual.actor2D_amp_real.GetMapper().SetInputConnection(panelvisual.color_amp_real.GetOutputPort())
		panelvisual.SetPicker()
		panelvisual.renderer_amp_real.RemoveAllViewProps()
		panelvisual.renderer_phase_real.RemoveAllViewProps()
		panelvisual.renderer_amp_recip.RemoveAllViewProps()
		panelvisual.renderer_phase_recip.RemoveAllViewProps()
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_recip)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_recip)
		panelvisual.renWin.GetRenderWindow().Modified()
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.actor2D_amp_real)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.scalebar_amp_real)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.textActor)
		panelvisual.renderer_amp_real.SetBackground(r, g, b)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_real)
		panelvisual.renderer_amp_real.GetActiveCamera().SetPosition(0,0,1)
		panelvisual.renderer_amp_real.GetActiveCamera().SetViewUp(0,1,0)
		panelvisual.renderer_amp_real.GetActiveCamera().SetFocalPoint(0,0,0)
		panelvisual.renderer_amp_real.ResetCamera()
		panelvisual.renderer_amp_real.SetViewport(0,0,1,1)
		panelvisual.renderer_amp_recip.SetViewport(1,1,1,1)
		panelvisual.renWin.SetPicker(panelvisual.picker_amp_real)
		panelvisual.renWin.SetInteractorStyle(panelvisual.style2D)
		panelvisual.Layout()
		panelvisual.Show()
		if(self.chkbox_axes.GetValue() == True):
			if panelvisual.VTKIsNot6:
				panelvisual.axis2D.SetInput(panelvisual.image2D_amp_real_vtk)
			else:
				panelvisual.axis2D.SetInputData(panelvisual.image2D_amp_real_vtk)
			panelvisual.axis2D.SetBounds(panelvisual.image2D_amp_real_vtk.GetBounds())
			panelvisual.axis2D.SetCamera(panelvisual.renderer_amp_real.GetActiveCamera())
			panelvisual.axis2D.SetLabelFormat("%6.1f")
			panelvisual.axis2D.SetNumberOfLabels(10)
			panelvisual.axis.SetFlyModeToOuterEdges()
			panelvisual.axis.ScalingOff()
			panelvisual.axis.SetFontFactor(float(self.axes_fontfactor.value.GetValue()))
			panelvisual.axis.SetXLabel("X")
			panelvisual.axis.SetYLabel("Y")
			panelvisual.axis.Modified()
			panelvisual.renderer_amp_real.AddViewProp( panelvisual.axis2D )
	def ViewDataPhase2D(self, ancestor, data, r, g, b):
		self.ancestor.GetPage(0).queue_info.put("Preparing 2D array visualisation")
		self.ancestor.GetPage(0).queue_info.put("Array Size: " + str(data.GetDimensions()))
		panelvisual = ancestor.GetPage(1)
		phasemax = float(self.phasemax.value.GetValue())
		phasemin = float(self.phasemin.value.GetValue())
		panelvisual.image2D_amp_real_vtk = data
		panelvisual.image2D_amp_real_vtk.Modified()
		panelvisual.image_probe = panelvisual.image2D_amp_real_vtk
		panelvisual.lut_amp_real.SetNumberOfTableValues(256)
		panelvisual.lut_amp_real.SetScaleToLinear()
		panelvisual.lut_amp_real.SetTableRange([phasemin,phasemax])
		lutsource = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[1][0]][1]
		if self.ancestor.GetPage(0).cmls[1][1] == 0:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(255-k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		panelvisual.lut_amp_real.SetRamp(0)
		panelvisual.lut_amp_real.Build()
		panelvisual.scalebar_amp_real.SetTitle("")
		panelvisual.scalebar_amp_real.SetOrientationToVertical()
		panelvisual.scalebar_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		panelvisual.scalebar_amp_real.SetWidth(0.07)
		panelvisual.scalebar_amp_real.SetHeight(0.90)
		panelvisual.scalebar_amp_real.SetPosition(0.01,0.1)
		panelvisual.color_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		if panelvisual.VTKIsNot6:
			panelvisual.color_amp_real.SetInput(panelvisual.image2D_amp_real_vtk)
		else:
			panelvisual.color_amp_real.SetInputData(panelvisual.image2D_amp_real_vtk)
		panelvisual.color_amp_real.Update()
		if panelvisual.VTKIsNot6:
			panelvisual.mapper2D_amp_real.SetInputConnection(panelvisual.color_amp_real.GetOutputPort())
			panelvisual.actor2D_amp_real.SetInput(panelvisual.mapper2D_amp_real.GetInput())
		else:
			panelvisual.actor2D_amp_real.GetMapper().SetInputConnection(panelvisual.color_amp_real.GetOutputPort())
		panelvisual.SetPicker()
		panelvisual.renderer_amp_real.RemoveAllViewProps()
		panelvisual.renderer_phase_real.RemoveAllViewProps()
		panelvisual.renderer_amp_recip.RemoveAllViewProps()
		panelvisual.renderer_phase_recip.RemoveAllViewProps()
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_recip)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_recip)
		panelvisual.renWin.GetRenderWindow().Modified()
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.actor2D_amp_real)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.scalebar_amp_real)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.textActor)
		panelvisual.renderer_amp_real.SetBackground(r, g, b)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_real)
		panelvisual.renderer_amp_real.GetActiveCamera().SetPosition(0,0,1)
		panelvisual.renderer_amp_real.GetActiveCamera().SetViewUp(0,1,0)
		panelvisual.renderer_amp_real.GetActiveCamera().SetFocalPoint(0,0,0)
		panelvisual.renderer_amp_real.ResetCamera()
		panelvisual.renderer_amp_real.SetViewport(0,0,1,1)
		panelvisual.renderer_phase_real.SetViewport(1,1,1,1)
		panelvisual.renWin.SetPicker(panelvisual.picker_amp_real)
		panelvisual.renWin.SetInteractorStyle(panelvisual.style2D)
		panelvisual.Layout()
		panelvisual.Show()
		if(self.chkbox_axes.GetValue() == True):
			if panelvisual.VTKIsNot6:
				panelvisual.axis2D.SetInput(panelvisual.image2D_amp_real_vtk)
			else:
				panelvisual.axis2D.SetInputData(panelvisual.image2D_amp_real_vtk)
			panelvisual.axis2D.SetBounds(panelvisual.image2D_amp_real_vtk.GetBounds())
			panelvisual.axis2D.SetCamera(panelvisual.renderer_amp_real.GetActiveCamera())
			panelvisual.axis2D.SetLabelFormat("%6.1f")
			panelvisual.axis2D.SetNumberOfLabels(10)
			panelvisual.axis.SetFlyModeToOuterEdges()
			panelvisual.axis.ScalingOff()
			panelvisual.axis.SetFontFactor(float(self.axes_fontfactor.value.GetValue()))
			panelvisual.axis.SetXLabel("X")
			panelvisual.axis.SetYLabel("Y")
			panelvisual.axis.Modified()
			panelvisual.renderer_amp_real.AddViewProp( panelvisual.axis2D )
	data_file  = self.input_filename.objectpath.GetValue()
	panelvisual = self.ancestor.GetPage(1)
	panelvisual.contour_real.value.SetValue(self.contour.value.GetValue())
	panelvisual.OnContourSelect(None, forceshow=True)
	r = float(panelvisual.r)/255.0
	g = float(panelvisual.g)/255.0
	b = float(panelvisual.b)/255.0
	try:
		reader = vtk.vtkDataSetReader()
		reader.SetFileName(data_file)
		reader.Update()
		panelvisual.image=reader.GetOutput()
		panelvisual.image.Modified()
		panelvisual.data = None
		self.ancestor.GetPage(0).seqdata_max = panelvisual.image.GetScalarRange()[1]
	except:
		msg = "Could not load array."
		dlg = wx.MessageDialog(self, msg, "Sequence View VTK", wx.OK)
		dlg.ShowModal()
		dlg.Destroy()
		return
	else:
		self.ancestor.GetPage(0).queue_info.put("Preparing VTK array visualisation")
		self.ancestor.GetPage(0).queue_info.put("Data type: %d"%panelvisual.image.GetDataObjectType())
		self.ancestor.GetPage(0).queue_info.put("Dimensions: " + str(panelvisual.image.GetDimensions()))
		if (self.rbampphase.GetStringSelection() == 'Amplitude (isosurface)'):
			if "vtkStructuredPoints" in panelvisual.image.GetClassName():
				if panelvisual.image.GetDataDimension() < 3:
					ViewDataAmp2D(self, ancestor , panelvisual.image, r, g, b)
			else:
				ViewDataAmp(self, ancestor , panelvisual.image, r, g, b)
		if (self.rbampphase.GetStringSelection() == 'Phase (cut plane)'):
			if "vtkStructuredPoints" in panelvisual.image.GetClassName():
				if panelvisual.image.GetDataDimension() < 3:
					ViewDataPhase2D(self, ancestor , panelvisual.image, r, g, b)
			else:
				ViewDataPhase(self, ancestor , panelvisual.image, r, g, b)
		if (self.rbampphase.GetStringSelection() == 'Amplitude (cut plane)'):
			if "vtkStructuredPoints" in panelvisual.image.GetClassName():
				if panelvisual.image.GetDataDimension() < 3:
					pass
			else:
				ViewAmpPlane(self, ancestor , panelvisual.image, r, g, b)
		panelvisual.datarangelist = []
		panelvisual.ReleaseVisualButtons(gotovisual=True)
		panelvisual.button_vremove.Enable(False)
