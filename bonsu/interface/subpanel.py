#############################################
##   Filename: subpanel.py
##
##    Copyright (C) 2011 - 2012 Marcus C. Newton
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
import os
import numpy
from StringIO import StringIO
from PIL import Image
from ..sequences.functions import *
from ..sequences.algorithms import *
from .common import *
class SubPanel_Comments(wx.Panel):
	treeitem = {'name':  'Comments' , 'type': 'operpreview'}
	def sequence(self, selff, pipelineitem):
		pass
	def __init__(self, parent,ancestor):
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Pipeline Comments:")
		if IsNotWX4():
			title.SetToolTipString("Pipeline Comments.")
		else:
			title.SetToolTip("Pipeline Comments.")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.txt = wx.TextCtrl(self, style=wx.TE_BESTWRAP | wx.TE_MULTILINE)
		self.txt.Enable(True)
		vbox.Add(self.txt, 1, wx.EXPAND | wx.ALL, 2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_BlankLineFill(wx.Panel):
	treeitem = {'name':  'Blank Line Fill', 'type': 'operpre'}
	def sequence(self, selff, pipelineitem):
		Sequence_BlankLineFill(selff, pipelineitem)
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		self.panelphase = self.GetParent().GetParent().GetParent()
		self.font = self.GetParent().font
		self.file = None
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Fill blank voxels lines in raw data.")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input File: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		label = wx.StaticText(self, -1,"ROI:" , style =wx.ALIGN_RIGHT, size=(150,-1) )
		label.SetFont(self.font)
		hbox.Add( label, 0, wx.CENTER )
		def OnEdit(event):
			self.objectpath.ChangeValue(event.GetString())
		self.objectpath = wx.TextCtrl(self, -1)
		self.objectpath.SetFont(self.font)
		self.objectpath.SetValue("")
		if IsNotWX4():
			self.objectpath.SetToolTipString("Region of Interest")
		else:
			self.objectpath.SetToolTip("Region of Interest")
		self.objectpath.Bind(wx.EVT_TEXT_ENTER, OnEdit)
		hbox.Add( self.objectpath, 1, wx.CENTER |wx.EXPAND )
		self.button = wx.Button(self, -1, "Browse")
		self.button.SetFont(self.font)
		if IsNotWX4():
			self.button.SetToolTipString("Browse for ROI.")
		else:
			self.button.SetToolTip("Browse for ROI.")
		self.button.Bind(wx.EVT_BUTTON, self.OnBrowse)
		hbox.Add( self.button, 0, wx.LEFT|wx.CENTER)
		vbox.Add(hbox, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output File: ", "output.npy",150,'*.npy')
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((0,10))
		title2 = wx.StaticText(self, label="Filter kernel dimensions: ")
		vbox.Add(title2 ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.kdims=[{} for i in range(3)]
		self.kdims[0] = SpinnerObject(self,"x",MAX_INT_16,1,1,3,20,60)
		self.kdims[1] = SpinnerObject(self,"y",MAX_INT_16,1,1,3,20,60)
		self.kdims[2] = SpinnerObject(self,"z",MAX_INT_16,1,1,1,20,60)
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1.Add(self.kdims[0], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox1.Add(self.kdims[1], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox1.Add(self.kdims[2], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		vbox.Add(hbox1, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
	def OnBrowse(self, event):
		try:
			array = LoadArray(self.panelphase, self.input_filename.objectpath.GetValue())
			self.arrayobject = numpy.abs(array)
		except:
			title = "Sequence " + self.treeitem['name']
			msg = "Could not load array."
			wx.CallAfter(self.panelphase.UserMessage, title, msg)
			wx.CallAfter(self.panelphase.ancestor.GetPage(4).UpdateLog, None)
			return
		self.roidialog = ROIDialog(self)
		self.roidialog.ShowModal()
class ROIDialog(wx.Dialog):
	def __init__(self,parent):
		wx.Dialog.__init__(self, parent, style=wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION| wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.CLOSE_BOX ,title="ROI Voxel Fill", size=(700,480))
		self.SetSizeHints(700,480,-1,-1)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.object = parent.arrayobject
		self.vbox = wx.BoxSizer(wx.VERTICAL)
		self.vbox1 = wx.BoxSizer(wx.VERTICAL)
		self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		self.image = wx.StaticBitmap(self, bitmap=wx.EmptyBitmap(0,0))
		self.vbox1.Add(self.image, 1, wx.EXPAND | wx.ALL, border=0)
		self.scrollaxis = SpinnerObject(self,"Axis",3,1,1,1,50,40)
		self.Bind(wx.EVT_SPIN, self.OnAxisSpin, self.scrollaxis.spin)
		self.hbox1.Add(self.scrollaxis, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		self.slider = wx.Slider(self, -1, pos=wx.DefaultPosition, size=(150, -1),style=wx.SL_AUTOTICKS | wx.SL_HORIZONTAL | wx.SL_LABELS)
		self.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.OnScrollAxis, self.slider)
		self.Bind(wx.EVT_SCROLL_CHANGED, self.OnScrollAxis, self.slider)
		self.hbox1.Add(self.slider, 1,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		self.roi = [None]*6
		self.roi[0] = SpinnerObject(self,"x:",1,1,1,1,15,40)
		if IsNotWX4():
			self.roi[0].label.SetToolTipString("x, start index")
		else:
			self.roi[0].label.SetToolTip("x, start index")
		self.roi[1] = SpinnerObject(self,"",1,1,1,1,0,40)
		if IsNotWX4():
			self.roi[1].label.SetToolTipString("x, end index")
		else:
			self.roi[1].label.SetToolTip("x, end index")
		self.roi[2] = SpinnerObject(self,"y:",1,1,1,1,15,40)
		if IsNotWX4():
			self.roi[2].label.SetToolTipString("y, start index")
		else:
			self.roi[2].label.SetToolTip("y, start index")
		self.roi[3] = SpinnerObject(self,"",1,1,1,1,0,40)
		if IsNotWX4():
			self.roi[3].label.SetToolTipString("y, end index")
		else:
			self.roi[3].label.SetToolTip("y, end index")
		self.roi[4] = SpinnerObject(self,"z:",1,1,1,1,15,40)
		if IsNotWX4():
			self.roi[4].label.SetToolTipString("z, start index")
		else:
			self.roi[4].label.SetToolTip("z, start index")
		self.roi[5] = SpinnerObject(self,"",1,1,1,1,0,40)
		if IsNotWX4():
			self.roi[5].label.SetToolTipString("z, end index")
		else:
			self.roi[5].label.SetToolTip("z, end index")
		self.SetROILimits()
		axis = int(self.scrollaxis.value.GetValue())
		self.slider.SetRange(1,self.object.shape[axis - 1])
		for i in range(len(self.roi)):
			self.Bind(wx.EVT_SPIN, self.OnROISpin, self.roi[i].spin)
			self.Bind(wx.EVT_TEXT, self.OnROINumEntry, self.roi[i].value)
		for i in range(len(self.roi)):
			self.hbox2.Add(self.roi[i], 0, border=2)
		self.button_open = wx.Button(self, id=wx.ID_OPEN, label="Set ROI", size=(100, 30))
		self.hbox3.Add(self.button_open, 0, flag=wx.TOP, border=15)
		self.Bind(wx.EVT_BUTTON, self.SetROI, self.button_open)
		self.hbox3.Add((5, -1))
		self.button_cancel = wx.Button(self, id=wx.ID_CANCEL, label="Cancel", size=(100, 30))
		self.hbox3.Add(self.button_cancel, 0, flag=wx.TOP, border=15)
		self.Bind(wx.EVT_BUTTON, self.CancelROI, self.button_cancel)
		self.vbox.Add(self.vbox1, 1,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.vbox.Add(self.hbox1, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.vbox.Add(self.hbox2, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.vbox.Add(self.hbox3, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.SetSizer(self.vbox)
		self.Layout()
		self.Fit()
		self.OnSize(0)
	def SetROILimits(self):
		object = self.object
		for i in range(3):
			self.roi[2*i].spin.SetRange(1,object.shape[i])
			self.roi[2*i].spin.SetValue(1)
			self.roi[2*i].value.ChangeValue(str(1))
			self.roi[2*i+1].spin.SetRange(1,object.shape[i])
			self.roi[2*i+1].spin.SetValue(object.shape[i])
			self.roi[2*i+1].value.ChangeValue(str(object.shape[i]))
	def OnROISpin(self, event):
		self.ClearROI()
		self.DrawROI()
	def OnROINumEntry(self, event):
		self.ClearROI()
		self.DrawROI()
	def DrawROI(self):
		object = self.object
		bmp = self.image.GetBitmap()
		w =  bmp.GetWidth()
		h =  bmp.GetHeight()
		roi = [0]*6
		for i in range(3):
			roi[2*i] = int(self.roi[2*i].value.GetValue()) - 1
			roi[2*i+1] = int(self.roi[2*i+1].value.GetValue())
		axis = int(self.scrollaxis.value.GetValue())
		if axis == 1:
			x1 = int(float(w*roi[4])/float(object.shape[2]) +0.5)
			x2 = int(float(w*(roi[5]))/float(object.shape[2]) -0.5)
			y1 = int(float(h*roi[2])/float(object.shape[1]) +0.5)
			y2 = int(float(h*(roi[3]))/float(object.shape[1]) -0.5)
		elif axis == 2:
			x1 = int(float(w*roi[4])/float(object.shape[2]) +0.5)
			x2 = int(float(w*(roi[5]))/float(object.shape[2]) -0.5)
			y1 = int(float(h*roi[0])/float(object.shape[0]) +0.5)
			y2 = int(float(h*(roi[1]))/float(object.shape[0]) -0.5)
		elif axis == 3:
			x1 = int(float(w*roi[2])/float(object.shape[1]) +0.5)
			x2 = int(float(w*(roi[3]))/float(object.shape[1]) -0.5)
			y1 = int(float(h*roi[0])/float(object.shape[0]) +0.5)
			y2 = int(float(h*(roi[1]))/float(object.shape[0]) -0.5)
		self.dc = wx.MemoryDC(bmp)
		self.dc.SelectObject(bmp)
		self.dc.SetPen(wx.Pen(wx.RED, 1))
		self.dc.SetBrush(wx.TRANSPARENT_BRUSH)
		self.dc.DrawLine(x1, 1, x1, h)
		self.dc.DrawLine(x2, 1, x2, h)
		self.dc.DrawLine(1, y1, w, y1)
		self.dc.DrawLine(1, y2, w, y2)
		self.dc.SelectObject(wx.NullBitmap)
		self.image.SetBitmap(bmp)
		self.Layout()
	def ClearROI(self):
		self.image.SetBitmap(self.bmp)
		self.Layout()
	def UpdateImage(self, axis, position):
		object = self.object
		idx = position - 1
		if axis == 1:
			imagedata = object[idx,:,:]
		elif axis == 2:
			imagedata = object[:,idx,:]
		else:
			imagedata = object[:,:,idx]
		imagedata[imagedata < 1e-6] = 1.0
		imagedata = numpy.log(imagedata)
		imagedata = imagedata - imagedata.min()
		if imagedata.max() > 0:
			imagedata = (255.0/imagedata.max())*imagedata
		else:
			imagedata = 255.0*imagedata
		imagedatalow = numpy.uint8(imagedata)
		self.impil = Image.fromarray(imagedatalow, 'L').resize((self.sx,self.sy))
		self.imwx = wx.EmptyImage( self.impil.size[0], self.impil.size[1] )
		self.imwx.SetData( self.impil.convert( 'RGB' ).tobytes() )
		bitmap = wx.BitmapFromImage(self.imwx)
		self.bmp = wx.BitmapFromImage(self.imwx)
		self.image.SetBitmap(bitmap)
		self.Refresh()
		self.Layout()
	def OnScrollAxis(self, event):
		pos = event.GetPosition()
		axis = int(self.scrollaxis.value.GetValue())
		self.UpdateImage(axis,pos)
		self.ClearROI()
		self.DrawROI()
	def OnAxisSpin(self, event):
		axis = int(self.scrollaxis.value.GetValue())
		object = self.object
		self.slider.SetRange(1,object.shape[axis - 1])
		self.UpdateImage(axis,1)
		self.ClearROI()
		self.DrawROI()
	def GetROIString(self):
		if hasattr(self.object, 'shape'):
			if ( len(self.object.shape) == 3 ):
				roi = [0]*6
				for i in range(3):
					roi[2*i] = str(int(self.roi[2*i].value.GetValue()) - 1)
					roi[2*i+1] = str(int(self.roi[2*i+1].value.GetValue()) -1)
				roistr = "["
				for i in range(3):
					roistr += roi[2*i]+":"+roi[2*i+1]+","
				roistr = roistr[:-1] +"]"
				return roistr
			else:
				return ""
		else:
			return ""
	def SetROI(self, event):
		path = self.GetROIString()
		self.GetParent().objectpath.SetValue(path)
		self.OnExit(0)
	def OnSize(self, event):
		self.Layout()
		sx,sy = self.vbox1.GetSize()
		self.sx = sx - 1
		self.sy = sy - 1
		axis = int(self.scrollaxis.value.GetValue())
		pos = self.slider.GetValue()
		self.UpdateImage(axis,pos)
		self.ClearROI()
		self.DrawROI()
		self.Layout()
		self.Refresh()
	def CancelROI(self, event):
		self.OnExit(0)
	def OnExit(self,event):
		del self.GetParent().roidialog
		self.EndModal(wx.ID_YES)
		self.Destroy()
class SubPanel_Scale_Array(wx.Panel):
	treeitem = {'name':  'Scale Array' , 'type': 'operpre'}
	def sequence(self, selff, pipelineitem):
		Sequence_Scale_Array(selff, pipelineitem)
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Scale Arrays")
		if IsNotWX4():
			title.SetToolTipString("Scale array by a specified factor")
		else:
			title.SetToolTip("Scale array by a specified factor")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input File: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output File: ", "output.npy",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.scale = SpinnerObject(self,"Scale factor:",MAX_INT,0.0,1.0,1.0,150,150)
		if IsNotWX4():
			self.scale.label.SetToolTipString("Scale factor.")
		else:
			self.scale.label.SetToolTip("Scale factor.")
		vbox.Add(self.scale, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_SumDiff_Array(wx.Panel):
	treeitem = {'name':  'SumDiff Array' , 'type': 'operpre'}
	def sequence(self, selff, pipelineitem):
		Sequence_SumDiff_Array(selff, pipelineitem)
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Sum or Subtract Arrays")
		if IsNotWX4():
			title.SetToolTipString("Sum or subtract array2 from array 1")
		else:
			title.SetToolTip("Sum or subtract array2 from array 1")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input File 1: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename1 = TextPanelObject(self, "Input File 2: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.input_filename1, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output File: ", "output.npy",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.addsub = wx.RadioBox(self, label="Add or Subtract:", choices=['Add','Subtract'],  majorDimension=2, style=wx.RA_SPECIFY_COLS)
		if IsNotWX4():
			self.addsub.SetToolTipString("Add or Subtract")
		else:
			self.addsub.SetToolTip("Add or Subtract")
		vbox.Add(self.addsub, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_Rotate_Support(wx.Panel):
	treeitem = {'name':  'Rotate Support' , 'type': 'operpre'}
	def sequence(self, selff, pipelineitem):
		Sequence_Rotate_Support(selff, pipelineitem)
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Rotate Support Array")
		if IsNotWX4():
			title.SetToolTipString("Rotate support (binary complex) arrays only. \nStrange results will ensue if used on data arrays.")
		else:
			title.SetToolTip("Rotate support (binary complex) arrays only. \nStrange results will ensue if used on data arrays.")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input File: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output File: ", "data_rotated.npy",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.rotationaxis = SpinnerObject(self,"Axis:",3,1,1,1,150,150)
		if IsNotWX4():
			self.rotationaxis.label.SetToolTipString("Rotation axis.")
		else:
			self.rotationaxis.label.SetToolTip("Rotation axis.")
		vbox.Add(self.rotationaxis, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.rotationangle = SpinnerObject(self,"Angle:",360,-360,1,0,150,150)
		if IsNotWX4():
			self.rotationangle.label.SetToolTipString("Rotation angle in degrees.")
		else:
			self.rotationangle.label.SetToolTip("Rotation angle in degrees.")
		vbox.Add(self.rotationangle, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_Transpose_Array(wx.Panel):
	treeitem = {'name':  'Transpose Array' , 'type': 'operpre'}
	def sequence(self, selff, pipelineitem):
		Sequence_Transpose_Array(selff, pipelineitem)
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Transpose Array")
		if IsNotWX4():
			title.SetToolTipString("Transpose array from x,y,z to z,y,x")
		else:
			title.SetToolTip("Transpose array from x,y,z to z,y,x")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input File: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output File: ", "data_transposed.npy",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_HDF_to_Numpy(wx.Panel):
	treeitem = {'name':  'HDF5 to Numpy', 'type': 'operpre'}
	def sequence(self, selff, pipelineitem):
		Sequence_HDF_to_Numpy(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 0017
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		self.panelphase = self.GetParent().GetParent().GetParent()
		self.font = self.GetParent().font
		self.file = None
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Convert HDF5 to Numpy array.")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input HDF5 File: ", "",150,"HDF files (*.hdf)|*.hdf|HDF5 files (*.h5)|*.h5|All files (*.*)|*.*")
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		label = wx.StaticText(self, -1,"HDF Key Path:" , style =wx.ALIGN_RIGHT, size=(150,-1) )
		label.SetFont(self.font)
		hbox.Add( label, 0, wx.CENTER )
		def OnEdit(event):
			self.objectpath.ChangeValue(event.GetString())
		self.objectpath = wx.TextCtrl(self, -1)
		self.objectpath.SetFont(self.font)
		self.objectpath.SetValue("")
		if IsNotWX4():
			self.objectpath.SetToolTipString("Comma separated key names.")
		else:
			self.objectpath.SetToolTip("Comma separated key names.")
		self.objectpath.Bind(wx.EVT_TEXT_ENTER, OnEdit)
		hbox.Add( self.objectpath, 1, wx.CENTER |wx.EXPAND )
		self.button = wx.Button(self, -1, "Browse")
		self.button.SetFont(self.font)
		if IsNotWX4():
			self.button.SetToolTipString("Browse for HDF5 key path.")
		else:
			self.button.SetToolTip("Browse for HDF5 key path.")
		self.button.Bind(wx.EVT_BUTTON, self.OnBrowse)
		hbox.Add( self.button, 0, wx.LEFT|wx.CENTER)
		vbox.Add(hbox, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output File: ", "output.npy",150,'*.npy')
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
	def OnBrowse(self, event):
		try:
			import h5py
			self.file = h5py.File(self.input_filename.objectpath.GetValue(),'r')
		except:
			title = "Sequence " + self.treeitem['name']
			msg = "Could not load HDF file. Is H5py installed?"
			wx.CallAfter(self.panelphase.UserMessage, title, msg)
			wx.CallAfter(self.panelphase.ancestor.GetPage(4).UpdateLog, None)
			return
		self.keydialog = KeyDialog(self)
		self.keydialog.ShowModal()
class KeyDialog(wx.Dialog):
	def __init__(self,parent):
		wx.Dialog.__init__(self, parent, style=wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.MAXIMIZE_BOX | wx.CLOSE_BOX ,title="HDF5 Import", size=(700,480))
		self.SetSizeHints(700,480,-1,-1)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_CLOSE, self.OnExit)
		self.vbox = wx.BoxSizer(wx.VERTICAL)
		self.bmp = None
		self.dc = None
		self.object = None
		self.sx = None
		self.sy = None
		self.file = self.GetParent().file
		self.tree = wx.TreeCtrl(self, style=wx.TR_NO_BUTTONS)
		self.treeid = 0
		self.tree.SetFocus()
		self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivateTreeItem)
		self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelTreeItem)
		self.tree.__collapsing = False
		self.treeroot = self.tree.AddRoot(self.file.name)
		self.tree.SetItemPyData(self.treeroot, self.treeid)
		self.treeid += 1
		self.MakeBranch(self.file.get(self.file.name), self.treeroot)
		self.im = wx.ImageList(16, 16)
		self.im.Add(getcollapseBitmap())
		self.im.Add(getexpandBitmap())
		self.im.Add(gethoverBitmap())
		self.tree.AssignImageList(self.im)
		self.tree.SetItemImage(self.treeroot, 0)
		self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox1.Add(self.tree, 1,  flag=wx.EXPAND|wx.RIGHT|wx.TOP, border=2)
		self.vbox1 = wx.BoxSizer(wx.VERTICAL)
		self.rb = wx.RadioBox(self, label="View data", choices=['None','Array', 'Image'],  majorDimension=3, style=wx.RA_SPECIFY_COLS, size=(-1,40))
		self.Bind(wx.EVT_RADIOBOX, self.OnRadioSelect, self.rb)
		self.vbox1.Add(self.rb,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.dataview = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
		self.vbox1.Add(self.dataview, 1, wx.EXPAND | wx.ALL, border=2)
		self.vbox2 = wx.BoxSizer(wx.VERTICAL)
		self.vbox3 = wx.BoxSizer(wx.VERTICAL)
		self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		self.scrollaxis = SpinnerObject(self,"Axis",3,1,1,1,50,40)
		self.Bind(wx.EVT_SPIN, self.OnAxisSpin, self.scrollaxis.spin)
		self.hbox2.Add(self.scrollaxis, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		self.slider = wx.Slider(self, -1, pos=wx.DefaultPosition, size=(150, -1),style=wx.SL_AUTOTICKS | wx.SL_HORIZONTAL | wx.SL_LABELS)
		self.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.OnScrollAxis, self.slider)
		self.Bind(wx.EVT_SCROLL_CHANGED, self.OnScrollAxis, self.slider)
		self.hbox2.Add(self.slider, 1,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		self.roi_enable = wx.CheckBox(self, -1, 'ROI', size=(50, 20))
		self.roi_enable.SetValue(False)
		self.Bind(wx.EVT_CHECKBOX, self.OnROI, self.roi_enable)
		if IsNotWX4():
			self.roi_enable.SetToolTipString("Enable ROI")
		else:
			self.roi_enable.SetToolTip("Enable ROI")
		self.roi = [None]*6
		self.roi[0] = SpinnerObject(self,"x:",1,1,1,1,15,40)
		if IsNotWX4():
			self.roi[0].label.SetToolTipString("x, start index")
		else:
			self.roi[0].label.SetToolTip("x, start index")
		self.roi[1] = SpinnerObject(self,"",1,1,1,1,0,40)
		if IsNotWX4():
			self.roi[1].label.SetToolTipString("x, end index")
		else:
			self.roi[1].label.SetToolTip("x, end index")
		self.roi[2] = SpinnerObject(self,"y:",1,1,1,1,15,40)
		if IsNotWX4():
			self.roi[2].label.SetToolTipString("y, start index")
		else:
			self.roi[2].label.SetToolTip("y, start index")
		self.roi[3] = SpinnerObject(self,"",1,1,1,1,0,40)
		if IsNotWX4():
			self.roi[3].label.SetToolTipString("y, end index")
		else:
			self.roi[3].label.SetToolTip("y, end index")
		self.roi[4] = SpinnerObject(self,"z:",1,1,1,1,15,40)
		if IsNotWX4():
			self.roi[4].label.SetToolTipString("z, start index")
		else:
			self.roi[4].label.SetToolTip("z, start index")
		self.roi[5] = SpinnerObject(self,"",1,1,1,1,0,40)
		if IsNotWX4():
			self.roi[5].label.SetToolTipString("z, end index")
		else:
			self.roi[5].label.SetToolTip("z, end index")
		for i in range(len(self.roi)):
			self.roi[i].Disable()
		for i in range(len(self.roi)):
			self.Bind(wx.EVT_SPIN, self.OnROISpin, self.roi[i].spin)
			self.Bind(wx.EVT_TEXT, self.OnROINumEntry, self.roi[i].value)
		self.hbox3.Add(self.roi_enable, 0, border=2)
		for i in range(len(self.roi)):
			self.hbox3.Add(self.roi[i], 0, border=2)
		self.image = wx.StaticBitmap(self, bitmap=wx.EmptyBitmap(0,0))
		self.vbox3.Add(self.image, 1, wx.EXPAND | wx.ALL, border=0)
		self.vbox2.Add(self.vbox3, 1, wx.EXPAND | wx.ALL, border=2)
		self.vbox2.Add(self.hbox2, 0, wx.EXPAND | wx.ALL, border=2)
		self.vbox2.Add(self.hbox3, 0, wx.EXPAND | wx.ALL, border=2)
		self.hbox2.ShowItems(False)
		self.hbox3.ShowItems(False)
		self.vbox2.ShowItems(False)
		self.vbox1.Add(self.vbox2, 1, wx.EXPAND | wx.ALL, border=2)
		self.dataview.Hide()
		self.hbox1.Add(self.vbox1, 2, wx.EXPAND | wx.ALL, border=0)
		self.vbox.Add(self.hbox1, 1,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=0)
		self.hbox = wx.BoxSizer(wx.HORIZONTAL)
		self.info = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL, size=(300,55))
		self.hbox.Add(self.info, 1, wx.EXPAND | wx.ALL, border=2)
		self.button_open = wx.Button(self, id=wx.ID_OPEN, label="Open", size=(100, 30))
		self.hbox.Add(self.button_open, 0, flag=wx.TOP, border=15)
		self.Bind(wx.EVT_BUTTON, self.OpenKeyItem, self.button_open)
		self.hbox.Add((5, -1))
		self.button_cancel = wx.Button(self, id=wx.ID_CANCEL, label="Cancel", size=(100, 30))
		self.hbox.Add(self.button_cancel, 0, flag=wx.TOP, border=15)
		self.Bind(wx.EVT_BUTTON, self.CancelKeyItem, self.button_cancel)
		self.vbox.Add(self.hbox, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetSizer(self.vbox)
		self.Layout()
		self.Fit()
	def OnROI(self, event):
		if(event.GetEventObject().GetValue() == True):
			for i in range(len(self.roi)):
				self.roi[i].Enable()
			axis = int(self.scrollaxis.value.GetValue())
			object = self.object
			for i in range(3):
				self.roi[2*i].spin.SetRange(1,object.shape[i])
				self.roi[2*i].spin.SetValue(1)
				self.roi[2*i].value.ChangeValue(str(1))
				self.roi[2*i+1].spin.SetRange(1,object.shape[i])
				self.roi[2*i+1].spin.SetValue(object.shape[i])
				self.roi[2*i+1].value.ChangeValue(str(object.shape[i]))
			self.DrawROI()
		else:
			self.ClearROI()
			for i in range(len(self.roi)):
				self.roi[i].Disable()
	def OnROISpin(self, event):
		self.ClearROI()
		self.DrawROI()
	def OnROINumEntry(self, event):
		self.ClearROI()
		self.DrawROI()
	def DrawROI(self):
		object = self.object
		bmp = self.image.GetBitmap()
		w =  bmp.GetWidth()
		h =  bmp.GetHeight()
		roi = [0]*6
		for i in range(3):
			roi[2*i] = int(self.roi[2*i].value.GetValue()) - 1
			roi[2*i+1] = int(self.roi[2*i+1].value.GetValue()) - 1
		axis = int(self.scrollaxis.value.GetValue())
		if axis == 1:
			rx = int(float(w*roi[4])/float(object.shape[2]) +0.5)
			rw = int(float(w*(roi[5] - roi[4] +1.0))/float(object.shape[2]) +0.5)
			ry = int(float(h*roi[2])/float(object.shape[1]) +0.5)
			rh = int(float(h*(roi[3] - roi[2] +1.0))/float(object.shape[1]) +0.5)
		elif axis == 2:
			rx = int(float(w*roi[4])/float(object.shape[2]) +0.5)
			rw = int(float(w*(roi[5] - roi[4] +1.0))/float(object.shape[2]) +0.5)
			ry = int(float(h*roi[0])/float(object.shape[0]) +0.5)
			rh = int(float(h*(roi[1] - roi[0] +1.0))/float(object.shape[0]) +0.5)
		elif axis == 3:
			rx = int(float(w*roi[2])/float(object.shape[1]) +0.5)
			rw = int(float(w*(roi[3] - roi[2] +1.0))/float(object.shape[1]) +0.5)
			ry = int(float(h*roi[0])/float(object.shape[0]) +0.5)
			rh = int(float(h*(roi[1] - roi[0] +1.0))/float(object.shape[0]) +0.5)
		self.dc = wx.MemoryDC(bmp)
		self.dc.SelectObject(bmp)
		self.dc.SetPen(wx.Pen(wx.RED, 1))
		self.dc.SetBrush(wx.TRANSPARENT_BRUSH)
		self.dc.DrawRectangle(rx, ry, rw, rh)
		self.dc.SelectObject(wx.NullBitmap)
		self.image.SetBitmap(bmp)
		self.Layout()
	def ClearROI(self):
		self.image.SetBitmap(self.bmp)
		self.Layout()
	def UpdateROI(self):
		if self.roi_enable.GetValue() == True:
			self.ClearROI()
			self.DrawROI()
	def UpdateImage2D(self):
		object = self.object
		imagedata = numpy.array(object, dtype=numpy.double)
		imagedata[imagedata < 1e-6] = 1.0
		imagedata = numpy.log(imagedata)
		imagedata = imagedata - imagedata.min()
		if imagedata.max() > 0:
			imagedata = (255.0/imagedata.max())*imagedata
		else:
			imagedata = 255.0*imagedata
		imagedatalow = numpy.uint8(imagedata)
		self.impil = Image.fromarray(imagedatalow, 'L').resize((self.sx,self.sy))
		self.imwx = wx.EmptyImage( self.impil.size[0], self.impil.size[1] )
		self.imwx.SetData( self.impil.convert( 'RGB' ).tobytes() )
		bitmap = wx.BitmapFromImage(self.imwx)
		self.bmp = bitmap
		self.image.SetBitmap(bitmap)
		self.Refresh()
		self.Layout()
	def UpdateImage(self, axis, position):
		object = self.object
		idx = position - 1
		if axis == 1:
			imagedata = numpy.array(object[idx,:,:])
		elif axis == 2:
			imagedata = numpy.array(object[:,idx,:])
		else:
			imagedata = numpy.array(object[:,:,idx])
		imagedata[imagedata < 1e-6] = 1.0
		imagedata = numpy.log(imagedata)
		imagedata = imagedata - imagedata.min()
		if imagedata.max() > 0:
			imagedata = (255.0/imagedata.max())*imagedata
		else:
			imagedata = 255.0*imagedata
		imagedatalow = numpy.uint8(imagedata)
		self.impil = Image.fromarray(imagedatalow, 'L').resize((self.sx,self.sy))
		self.imwx = wx.EmptyImage( self.impil.size[0], self.impil.size[1] )
		self.imwx.SetData( self.impil.convert( 'RGB' ).tobytes() )
		bitmap = wx.BitmapFromImage(self.imwx)
		self.bmp = bitmap
		self.image.SetBitmap(bitmap)
		self.Refresh()
		self.Layout()
	def OnScrollAxis(self, event):
		pos = self.slider.GetValue()
		axis = int(self.scrollaxis.value.GetValue())
		self.UpdateImage(axis,pos)
		self.UpdateROI()
	def OnAxisSpin(self, event):
		axis = int(self.scrollaxis.value.GetValue())
		object = self.object
		self.slider.SetRange(1,object.shape[axis - 1])
		self.UpdateImage(axis,1)
		self.UpdateROI()
	def MakeBranch(self, item, limb):
		try:
			keys = item.keys()
		except:
			pass
		else:
			if not self.tree.GetChildrenCount(limb) > 0:
				for key in keys:
					newitem = item.get(key)
					newlimb = self.tree.AppendItem(limb, key)
					self.tree.SetItemPyData(newlimb, self.treeid)
					self.treeid += 1
					try:
						subkey = newitem.keys()
					except:
						pass
					else:
						self.tree.SetItemHasChildren(newlimb, True)
						self.tree.SetItemImage(newlimb, 0)
	def BranchPath(self, item):
		itemtext = self.tree.GetItemText(item)
		hdfpath = []
		parent = item
		hdfpath.append(itemtext)
		parentobj = self.tree.GetItemPyData(self.treeroot)
		atroot = cmp(parentobj, self.tree.GetItemPyData(parent))
		if atroot != 0:
			while atroot != 0:
				parent = self.tree.GetItemParent(parent)
				atroot = cmp(parentobj, self.tree.GetItemPyData(parent))
				itemtext = self.tree.GetItemText(parent)
				hdfpath.append(itemtext)
			hdfpath.reverse()
		return hdfpath
	def GetROIString(self):
		if hasattr(self.object, 'shape'):
			if ( len(self.object.shape) == 3 and self.roi_enable.GetValue() == True):
				roi = [0]*6
				for i in range(3):
					roi[2*i] = str(int(self.roi[2*i].value.GetValue()) - 1)
					roi[2*i+1] = str(int(self.roi[2*i+1].value.GetValue()) - 1)
				roistr = "["
				for i in range(3):
					roistr += roi[2*i]+":"+roi[2*i+1]+","
				roistr = roistr[:-1] +"]"
				return roistr
			else:
				return ""
		else:
			return ""
	def OnActivateTreeItem(self, event):
		item = event.GetItem()
		hdfpath = self.BranchPath(item)
		if not self.tree.ItemHasChildren(item):
			path = ""
			for key in hdfpath:
				path = path+key+","
			path = path[:-1]
			path = path+self.GetROIString()
			self.GetParent().objectpath.SetValue(path)
			self.OnExit(0)
		else:
			if self.tree.IsExpanded(item):
				self.tree.SetItemImage(item, 0)
				self.tree.Collapse(item)
			else:
				newitem = self.file.get(self.file.name)
				for key in hdfpath:
					newitem = newitem.get(key)
				self.MakeBranch(newitem, item)
				self.tree.SetItemImage(item, 1)
				self.tree.Expand(item)
	def OnSelTreeItem(self, event):
		item = event.GetItem()
		self.SelTreeItem(item)
	def SelTreeItem(self, item):
		if not self.tree.ItemHasChildren(item):
			hdfpath = self.BranchPath(item)
			object = self.file
			for key in hdfpath:
				object = object.get(key)
			self.object = object
			self.info.Clear()
			self.info.AppendText("Data type: "+str(object.dtype.name)+os.linesep)
			self.info.AppendText("Element size: "+str(object.dtype.itemsize)+os.linesep)
			self.info.AppendText("Data shape: "+str(object.shape))
			if self.rb.GetStringSelection() == 'Array':
				self.dataview.Clear()
				if str(object.dtype.name).startswith('string'):
					self.dataview.AppendText(str(numpy.char.mod('%s',object)))
				elif str(object.dtype.name).startswith('uint') or str(object.dtype.name).startswith('int'):
					self.dataview.AppendText(str(numpy.char.mod('%d',object)))
				else:
					self.dataview.AppendText(str(numpy.char.mod('%e',object)))
			elif self.rb.GetStringSelection() == 'Image':
				if (not str(object.dtype.name).startswith('string')):
						if len(object.shape) == 2:
							self.hbox2.ShowItems(False)
							self.hbox3.ShowItems(False)
							self.Layout()
							sx,sy = self.vbox3.GetSize()
							self.sx = sx - 1
							self.sy = sy - 1
							self.UpdateImage2D()
						elif len(object.shape) == 3:
							self.hbox2.ShowItems(True)
							self.hbox3.ShowItems(True)
							self.Layout()
							sx,sy = self.vbox3.GetSize()
							self.sx = sx - 1
							self.sy = sy - 1
							axis = int(self.scrollaxis.value.GetValue())
							self.slider.SetRange(1,object.shape[axis - 1])
							self.OnScrollAxis(None)
			else:
				self.dataview.Clear()
		self.Refresh()
		self.Layout()
	def OpenKeyItem(self, event):
		item = self.tree.GetSelection()
		if not self.tree.ItemHasChildren(item):
			hdfpath = self.BranchPath(item)
			path = ""
			for key in hdfpath:
				path = path+key+","
			path = path[:-1]
			path = path+self.GetROIString()
			self.GetParent().objectpath.SetValue(path)
			self.OnExit(0)
	def CancelKeyItem(self, event):
		self.OnExit(0)
	def OnRadioSelect(self, event):
		rselect = self.rb.GetStringSelection()
		if rselect == 'None':
			self.vbox2.ShowItems(False)
			self.dataview.Hide()
		if rselect == 'Array':
			self.vbox2.ShowItems(False)
			self.dataview.Show()
		if rselect == 'Image':
			self.vbox2.ShowItems(True)
			if hasattr(self.object, 'shape'):
				if len(self.object.shape) != 3:
					self.hbox2.ShowItems(False)
					self.hbox3.ShowItems(False)
			else:
				self.hbox2.ShowItems(False)
				self.hbox3.ShowItems(False)
			self.dataview.Hide()
		self.Layout()
		item = self.tree.GetSelection()
		self.SelTreeItem(item)
	def OnSize(self, event):
		self.Layout()
		if self.vbox2.IsShown(self.hbox2) == True:
			sx,sy = self.vbox3.GetSize()
			self.sx = sx - 1
			self.sy = sy - 1
			object = self.object
			if len(object.shape) == 2:
				self.UpdateImage2D()
			elif len(object.shape) == 3:
				self.OnScrollAxis(None)
			self.Layout()
		self.Refresh()
	def OnExit(self,event):
		self.file.close()
		del self.GetParent().keydialog
		self.EndModal(wx.ID_YES)
		self.Destroy()
class SubPanel_SPE_to_Numpy(wx.Panel):
	treeitem = {'name':  'SPE to Numpy' , 'type': 'operpre'}
	def sequence(self, selff, pipelineitem):
		Sequence_SPE_to_Numpy(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 0010
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Convert SPE to Numpy array")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input SPE File: ", "",150,'*.SPE')
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output File: ", "",150,'*.npy')
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_Image_to_Numpy(wx.Panel):
	treeitem = {'name':  'Image to Numpy' , 'type': 'operpre'}
	def sequence(self, selff, pipelineitem):
		Sequence_Image_to_Numpy(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 0032
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Convert Image file to Numpy array")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input Image File: ", "",150,"PNG files (*.png)|*.png|JPEG files (*.jpg)|*.jpg|PPM files (*.ppm)|*.ppm|TIF files (*.tif)|*.tif|All files (*.*)|*.*")
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output File: ", "",150,'*.npy')
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_Array_to_Memory(wx.Panel):
	treeitem = {'name':  'Array to Memory' , 'type': 'operpre'}
	def sequence(self, selff, pipelineitem):
		Sequence_Array_to_Memory(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 0050
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Load Array to Memory Location")
		if IsNotWX4():
			title.SetToolTipString("Memory locations: memory0, memory1, ... , memory9")
		else:
			title.SetToolTip("Memory locations: memory0, memory1, ... , memory9")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input File: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output File: ", "memory0",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_Memory_to_Array(wx.Panel):
	treeitem = {'name':  'Memory to Array' , 'type': 'operpre'}
	def sequence(self, selff, pipelineitem):
		Sequence_Memory_to_Array(selff, pipelineitem)
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Save Array from Memory Location")
		if IsNotWX4():
			title.SetToolTipString("Memory locations: memory0, memory1, ... , memory9")
		else:
			title.SetToolTip("Memory locations: memory0, memory1, ... , memory9")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input File: ", "memory0",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output File: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_Load_PSF(wx.Panel):
	treeitem = {'name':  'Load PSF' , 'type': 'algsstart'}
	def sequence(self, selff, pipelineitem):
		Sequence_Load_PSF(selff, pipelineitem)
	def __init__(self, parent):
		self.start_iter = None
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Load Fourier Tranform of Point Spread function.")
		if IsNotWX4():
			title.SetToolTipString("Load Fourier Tranform of Point Spread function.")
		else:
			title.SetToolTip("Load Fourier Tranform of Point Spread function.")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input File: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_Save_PSF(wx.Panel):
	treeitem = {'name':  'Save PSF' , 'type': 'operpost'}
	def sequence(self, selff, pipelineitem):
		Sequence_Save_PSF(selff, pipelineitem)
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Save Fourier Tranform of Point Spread function.")
		if IsNotWX4():
			title.SetToolTipString("Save Fourier Tranform of Point Spread function.")
		else:
			title.SetToolTip("Save Fourier Tranform of Point Spread function.")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output File: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_Crop_Pad(wx.Panel):
	treeitem = {'name':  'Crop Pad' , 'type': 'operpre'}
	def sequence(self, selff, pipelineitem):
		Sequence_Crop_Pad(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 0011
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Crop and Pad Numpy Array")
		if IsNotWX4():
			title.SetToolTipString("Input array will be cropped and then "+os.linesep+"padded according to the values below.")
		else:
			title.SetToolTip("Input array will be cropped and then "+os.linesep+"padded according to the values below.")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input File: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output File: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		title2 = wx.StaticText(self, label="Crop dimensions: Start: ")
		vbox.Add(title2 ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.csdims=[{} for i in range(3)]
		self.csdims[0] = SpinnerObject(self,"i",MAX_INT_16,0,1,0,20,60)
		self.csdims[1] = SpinnerObject(self,"j",MAX_INT_16,0,1,0,20,60)
		self.csdims[2] = SpinnerObject(self,"k",MAX_INT_16,0,1,0,20,60)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.csdims[0], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox.Add(self.csdims[1], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox.Add(self.csdims[2], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		vbox.Add(hbox, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		title3 = wx.StaticText(self, label="Crop dimensions: End: ")
		vbox.Add(title3 ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.cedims=[{} for i in range(3)]
		self.cedims[0] = SpinnerObject(self,"i",MAX_INT_16,0,1,0,20,60)
		self.cedims[1] = SpinnerObject(self,"j",MAX_INT_16,0,1,0,20,60)
		self.cedims[2] = SpinnerObject(self,"k",MAX_INT_16,0,1,0,20,60)
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1.Add(self.cedims[0], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox1.Add(self.cedims[1], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox1.Add(self.cedims[2], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		vbox.Add(hbox1, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		title4 = wx.StaticText(self, label="Pad dimensions: Start: ")
		vbox.Add(title4 ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.psdims=[{} for i in range(3)]
		self.psdims[0] = SpinnerObject(self,"i",MAX_INT_16,0,1,0,20,60)
		self.psdims[1] = SpinnerObject(self,"j",MAX_INT_16,0,1,0,20,60)
		self.psdims[2] = SpinnerObject(self,"k",MAX_INT_16,0,1,0,20,60)
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2.Add(self.psdims[0], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox2.Add(self.psdims[1], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox2.Add(self.psdims[2], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		vbox.Add(hbox2, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		title5 = wx.StaticText(self, label="Pad dimensions: End: ")
		vbox.Add(title5 ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.pedims=[{} for i in range(3)]
		self.pedims[0] = SpinnerObject(self,"i",MAX_INT_16,0,1,0,20,60)
		self.pedims[1] = SpinnerObject(self,"j",MAX_INT_16,0,1,0,20,60)
		self.pedims[2] = SpinnerObject(self,"k",MAX_INT_16,0,1,0,20,60)
		hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3.Add(self.pedims[0], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox3.Add(self.pedims[1], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox3.Add(self.pedims[2], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		vbox.Add(hbox3, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_Mask(wx.Panel):
	treeitem = {'name':  'Mask' , 'type': 'operpre'}
	def sequence(self, selff, pipelineitem):
		Sequence_Mask(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 0012
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Create binary mask from Numpy array")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input File: ", "",150,'*.npy')
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output File: ", "mask.npy",150,'*.npy')
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.max = SpinnerObject(self,"Maximum Value:",MAX_INT,MIN_INT,1.0,MAX_INT,150,150)
		if IsNotWX4():
			self.max.label.SetToolTipString("Data within the min/max range "+os.linesep+"will result in a non-zero mask value.")
		else:
			self.max.label.SetToolTip("Data within the min/max range "+os.linesep+"will result in a non-zero mask value.")
		self.min = SpinnerObject(self,"Minimum Value:",MAX_INT,MIN_INT,1,50.0,150,150)
		if IsNotWX4():
			self.min.label.SetToolTipString("Data within the min/max range "+os.linesep+"will result in a non-zero mask value.")
		else:
			self.min.label.SetToolTip("Data within the min/max range "+os.linesep+"will result in a non-zero mask value.")
		vbox.Add(self.max, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add(self.min, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_Bin(wx.Panel):
	treeitem = {'name':  'Bin' , 'type': 'operpre'}
	def sequence(self, selff, pipelineitem):
		Sequence_Bin(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 0014
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Bin Numpy Array")
		if IsNotWX4():
			title.SetToolTipString("Input array will be binned "+os.linesep+"according to the values below.")
		else:
			title.SetToolTip("Input array will be binned "+os.linesep+"according to the values below.")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input File: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output File: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		title2 = wx.StaticText(self, label="Bin dimensions: ")
		vbox.Add(title2 ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.bdims=[{} for i in range(3)]
		self.bdims[0] = SpinnerObject(self,"x",MAX_INT_16,1,1,1,20,60)
		self.bdims[1] = SpinnerObject(self,"y",MAX_INT_16,1,1,1,20,60)
		self.bdims[2] = SpinnerObject(self,"z",MAX_INT_16,1,1,1,20,60)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.bdims[0], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox.Add(self.bdims[1], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox.Add(self.bdims[2], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		vbox.Add(hbox, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_AutoCentre(wx.Panel):
	treeitem = {'name':  'Auto Centre' , 'type': 'operpre'}
	def sequence(self, selff, pipelineitem):
		Sequence_AutoCentre(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 0015
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Auto Centre Numpy Array")
		if IsNotWX4():
			title.SetToolTipString("Input array will be Auto Centred "+os.linesep+"according to the brightest voxel.")
		else:
			title.SetToolTip("Input array will be Auto Centred "+os.linesep+"according to the brightest voxel.")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input File: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output File: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_Wrap(wx.Panel):
	treeitem = {'name':  'Wrap Data' , 'type': 'operpre'}
	def sequence(self, selff, pipelineitem):
		Sequence_Wrap(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 0016
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Wrap Numpy Array")
		if IsNotWX4():
			title.SetToolTipString("Input array will be converted "+os.linesep+"to wrap around order.")
		else:
			title.SetToolTip("Input array will be converted "+os.linesep+"to wrap around order.")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input File: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output File: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 5))
		self.rbdirection = wx.RadioBox(self, label="Wrap Direction", choices=['Forward','Reverse',],  majorDimension=2, style=wx.RA_SPECIFY_COLS)
		if IsNotWX4():
			self.rbdirection.SetToolTipString("If an array dimension has an odd number of elements, "+os.linesep+
															"a Forward followed by a Reverse wrap is required "+os.linesep+
															"to obtain the original array.")
		else:
			self.rbdirection.SetToolTip("If an array dimension has an odd number of elements, "+os.linesep+
															"a Forward followed by a Reverse wrap is required "+os.linesep+
															"to obtain the original array.")
		vbox.Add(self.rbdirection ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_Threshold(wx.Panel):
	treeitem = {'name':  'Threshold Data' , 'type': 'operpre'}
	def sequence(self, selff, pipelineitem):
		Sequence_Threshold(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 0013
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Threshold data in Numpy array")
		if IsNotWX4():
			title.SetToolTipString("Data outside range is set to zero.")
		else:
			title.SetToolTip("Data outside range is set to zero.")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input File: ", "",150,'*.npy')
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output File: ", "data_thresh.npy",150,'*.npy')
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.max = SpinnerObject(self,"Maximum Value:",MAX_INT,MIN_INT,1.0,MAX_INT,150,150)
		if IsNotWX4():
			self.max.label.SetToolTipString("Data within the min/max range "+os.linesep+"will result in a non-zero mask value.")
		else:
			self.max.label.SetToolTip("Data within the min/max range "+os.linesep+"will result in a non-zero mask value.")
		self.min = SpinnerObject(self,"Minimum Value:",MAX_INT,MIN_INT,1,50.0,150,150)
		if IsNotWX4():
			self.min.label.SetToolTipString("Data within the min/max range "+os.linesep+"will result in a non-zero mask value.")
		else:
			self.min.label.SetToolTip("Data within the min/max range "+os.linesep+"will result in a non-zero mask value.")
		vbox.Add(self.max, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add(self.min, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_Voxel_Replace(wx.Panel):
	treeitem = {'name':  'Voxel Replace' , 'type': 'operpre'}
	def sequence(self, selff, pipelineitem):
		Sequence_Voxel_Replace(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 0033
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Replace Voxels in Numpy Array")
		if IsNotWX4():
			title.SetToolTipString("Useful for viewing data with a cut-out section.")
		else:
			title.SetToolTip("Useful for viewing data with a cut-out section.")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input File: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output File: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		title2 = wx.StaticText(self, label="Start dimensions:")
		vbox.Add(title2 ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.sdims=[{} for i in range(3)]
		self.sdims[0] = SpinnerObject(self,"i",MAX_INT_16,0,1,0,20,60)
		self.sdims[1] = SpinnerObject(self,"j",MAX_INT_16,0,1,0,20,60)
		self.sdims[2] = SpinnerObject(self,"k",MAX_INT_16,0,1,0,20,60)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.sdims[0], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox.Add(self.sdims[1], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox.Add(self.sdims[2], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		vbox.Add(hbox, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		title3 = wx.StaticText(self, label="End dimensions:")
		vbox.Add(title3 ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.edims=[{} for i in range(3)]
		self.edims[0] = SpinnerObject(self,"i",MAX_INT_16,0,1,0,20,60)
		self.edims[1] = SpinnerObject(self,"j",MAX_INT_16,0,1,0,20,60)
		self.edims[2] = SpinnerObject(self,"k",MAX_INT_16,0,1,0,20,60)
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1.Add(self.edims[0], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox1.Add(self.edims[1], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox1.Add(self.edims[2], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		vbox.Add(hbox1, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		sbox1 = wx.StaticBox(self, label="Complex Value", style=wx.SUNKEN_BORDER)
		sboxs1 = wx.StaticBoxSizer(sbox1,wx.VERTICAL)
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		self.real = SpinnerObject(self,"Real:",MAX_INT_16,MIN_INT_16,0.1,1.0,50,150)
		hbox2.Add(self.real, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		hbox2.Add((5, -1))
		self.imag = SpinnerObject(self,"Imag:",MAX_INT_16,MIN_INT_16,0.1,0.0,50,150)
		hbox2.Add(self.imag, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		sboxs1.Add(hbox2, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add(sboxs1, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_Median_Filter(wx.Panel):
	treeitem = {'name':  'Median Filter' , 'type': 'operpre'}
	def sequence(self, selff, pipelineitem):
		Sequence_Median_Filter(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 0051
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Filter array with median filter.")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input File: ", "",150,'*.npy')
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output File: ", "output.npy",150,'*.npy')
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		title2 = wx.StaticText(self, label="Filter kernel dimensions: ")
		vbox.Add(title2 ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.kdims=[{} for i in range(3)]
		self.kdims[0] = SpinnerObject(self,"x",MAX_INT_16,1,1,3,20,60)
		self.kdims[1] = SpinnerObject(self,"y",MAX_INT_16,1,1,3,20,60)
		self.kdims[2] = SpinnerObject(self,"z",MAX_INT_16,1,1,1,20,60)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.kdims[0], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox.Add(self.kdims[1], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox.Add(self.kdims[2], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		vbox.Add(hbox, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.maxdev = SpinnerObject(self,"Normal deviation:",MAX_INT_16,0.0,0.1,0.5,150,150)
		if IsNotWX4():
			self.maxdev.label.SetToolTipString("Maximum element-wise normal deviation.")
		else:
			self.maxdev.label.SetToolTip("Maximum element-wise normal deviation.")
		vbox.Add(self.maxdev, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_GaussianFill(wx.Panel):
	treeitem = {'name':  'Gaussian Fill' , 'type': 'operpre'}
	def sequence(self, selff, pipelineitem):
		Sequence_GaussianFill(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 0035
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Fill Numpy array with Gaussian distribution.")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input File: ", "",150,'*.npy')
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output File: ", "data_gaussian.npy",150,'*.npy')
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.sigma = SpinnerObject(self,"Sigma:",MAX_INT_16,0.0,0.1,2.0,150,150)
		if IsNotWX4():
			self.sigma.label.SetToolTipString("Standard deviation.")
		else:
			self.sigma.label.SetToolTip("Standard deviation.")
		vbox.Add(self.sigma, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_FFT(wx.Panel):
	treeitem = {'name':  'Fourier Transform' , 'type': 'operpre'}
	def sequence(self, selff, pipelineitem):
		Sequence_FFT(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 0036
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Fourier Transform Array")
		if IsNotWX4():
			title.SetToolTipString("Fourier Transform Input Array.")
		else:
			title.SetToolTip("Fourier Transform Input Array.")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input File: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output File: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 5))
		self.rbdirection = wx.RadioBox(self, label="To:", choices=['Fourier Space','Real Space',],  majorDimension=2, style=wx.RA_SPECIFY_COLS)
		vbox.Add(self.rbdirection ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_Convolve(wx.Panel):
	treeitem = {'name':  'Convolve' , 'type': 'operpre'}
	def sequence(self, selff, pipelineitem):
		Sequence_Convolve(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 0037
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Convolve Arrays")
		if IsNotWX4():
			title.SetToolTipString("Convolve Input Arrays.")
		else:
			title.SetToolTip("Convolve Input Arrays.")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename1 = TextPanelObject(self, "Input File 1: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.input_filename1, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename2 = TextPanelObject(self, "Input File 2: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.input_filename2, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output File: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_Conjugate_Reflect(wx.Panel):
	treeitem = {'name':  'Conjugate Reflect' , 'type': 'operpre'}
	def sequence(self, selff, pipelineitem):
		Sequence_Conjugate_Reflect(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 0034
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Conjugate and Reflect Array")
		if IsNotWX4():
			title.SetToolTipString("Conjugate and Reflect Array.")
		else:
			title.SetToolTip("Conjugate and Reflect Array.")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input File: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output File: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_Cuboid_Support(wx.Panel):
	treeitem = {'name':  'Cuboid Support' , 'type': 'operpre'}
	def sequence(self, selff, pipelineitem):
		Sequence_Cuboid_Support(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 0100
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Make Cuboid Support")
		if IsNotWX4():
			title.SetToolTipString("Support is made using the (x,y,z) values below."+os.linesep+"If an additional numpy array is supplied, its "+os.linesep+"dimensions will be used.")
		else:
			title.SetToolTip("Support is made using the (x,y,z) values below."+os.linesep+"If an additional numpy array is supplied, its "+os.linesep+"dimensions will be used.")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.filename = TextPanelObject(self, "Support File: ", "support.npy",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.fromfile = TextPanelObject(self, "(x,y,z) from array: ", "",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.fromfile, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		title2 = wx.StaticText(self, label="(x,y,z) from dimensions: ")
		vbox.Add(title2 ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.dims=[{} for i in range(3)]
		self.dims[0] = SpinnerObject(self,"x",MAX_INT_16,1,1,1,20,60)
		self.dims[1] = SpinnerObject(self,"y",MAX_INT_16,1,1,1,20,60)
		self.dims[2] = SpinnerObject(self,"z",MAX_INT_16,1,1,1,20,60)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.dims[0], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox.Add(self.dims[1], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox.Add(self.dims[2], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		vbox.Add(hbox, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		title3 = wx.StaticText(self, label="Support size: ")
		vbox.Add(title3 ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.sdims=[{} for i in range(3)]
		self.sdims[0] = SpinnerObject(self,"sx",MAX_INT_16,1,1,1,20,60)
		self.sdims[1] = SpinnerObject(self,"sy",MAX_INT_16,1,1,1,20,60)
		self.sdims[2] = SpinnerObject(self,"sz",MAX_INT_16,1,1,1,20,60)
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1.Add(self.sdims[0], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox1.Add(self.sdims[1], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox1.Add(self.sdims[2], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		vbox.Add(hbox1, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_ArraytoVTK(wx.Panel):
	treeitem = {'name':  'Array to VTK' , 'type': 'operpre'}
	def sequence(self, selff, pipelineitem):
		Sequence_ArraytoVTK(selff, pipelineitem)
	def __init__(self,parent):
		self.pipeline_id = 0020
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Numpy array to VTK array")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input file: ", "input.npy",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 5))
		self.output_filename = TextPanelObject(self, "Output file: ", "output.vtk",150,"VTK files (*.vtk)|*.vtk|All files (*.*)|*.*")
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 5))
		self.rbampphase = wx.RadioBox(self, label="Type", choices=['Amplitude','Phase'],  majorDimension=2, style=wx.RA_SPECIFY_COLS)
		vbox.Add(self.rbampphase,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_ObjecttoVTK(wx.Panel):
	treeitem = {'name':  'Object to VTK' , 'type': 'operpre'}
	def sequence(self, selff, pipelineitem):
		Sequence_ObjecttoVTK(selff, pipelineitem)
	def __init__(self,parent):
		self.pipeline_id = 0021
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Numpy array with coordinates to VTK array")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input file: ", "input.npy",150,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 5))
		self.coords_filename = TextPanelObject(self, "Co-ord's file: ", "coordinates.npy",150,'*.npy')
		vbox.Add(self.coords_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 5))
		self.output_filename = TextPanelObject(self, "Output file: ", "output.vtk",150,"VTK files (*.vtk)|*.vtk|All files (*.*)|*.*")
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 5))
		self.rbampphase = wx.RadioBox(self, label="Type", choices=['Amplitude','Phase'],  majorDimension=2, style=wx.RA_SPECIFY_COLS)
		vbox.Add(self.rbampphase,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_View_Support(wx.ScrolledWindow):
	treeitem = {'name':  'View Support' , 'type': 'operpreview'}
	def sequence(self, selff, pipelineitem):
		pass
	def __init__(self,parent,ancestor):
		from math import pi
		self.ancestor = ancestor
		wx.ScrolledWindow.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="View Support array")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.support = TextPanelObject(self, "Support: ", "",100,'*.npy')
		vbox.Add(self.support, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Data array: ", "",100,'*.npy')
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 5))
		self.sbox1 = wx.StaticBox(self, label="Isosurface", style=wx.SUNKEN_BORDER)
		self.sboxs1 = wx.StaticBoxSizer(self.sbox1,wx.VERTICAL)
		self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		self.contour_support = SpinnerObject(self,"Support:",1.0,0.0,0.1,0.5,100,100)
		self.hbox1.Add(self.contour_support,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.hbox1.Add((20, -1))
		self.opacity = SpinnerObject(self,"Opacity:",1.0,0.0,0.1,0.5,130,100)
		self.hbox1.Add(self.opacity,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.sboxs1.Add(self.hbox1,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		self.contour = SpinnerObject(self,"Data:",MAX_INT,MIN_INT,1,100,100,100)
		self.hbox2.Add(self.contour,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.hbox2.Add((20, -1))
		self.feature_angle = SpinnerObject(self,"Feature Angle:",180,0,1,90,130,100)
		self.hbox2.Add(self.feature_angle,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.sboxs1.Add(self.hbox2,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.sboxs1.Add((-1, 5))
		vbox.Add(self.sboxs1,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 5))
		self.hbox6 = wx.BoxSizer(wx.HORIZONTAL)
		self.chkbox_axes = wx.CheckBox(self, -1, 'View axes', size=(200, 20))
		self.chkbox_axes.SetValue(False)
		self.hbox6.Add(self.chkbox_axes, 1,flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.hbox6.Add((-1, 5))
		self.axes_fontfactor = SpinnerObject(self,"Font Factor:",MAX_INT,1,1,2,100,100)
		self.hbox6.Add(self.axes_fontfactor, 0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		vbox.Add(self.hbox6, 0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		vbox.Add((-1, 5))
		button_view = wx.Button(self, label="View", size=(70, 30))
		button_view.Bind(wx.EVT_BUTTON, self.SeqParser )
		vbox.Add(button_view,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
		self.FitInside()
		self.SetScrollRate(5, 5)
	def SeqParser(self,event):
		Sequence_View_Support(self, self.ancestor)
		self.ancestor.GetPage(4).data_poll_timer.Start(1000)
class SubPanel_View_Array(wx.ScrolledWindow):
	treeitem = {'name':  'View Array' , 'type': 'operpreview'}
	def sequence(self, selff, pipelineitem):
		pass
	def __init__(self,parent,ancestor):
		from math import pi
		self.ancestor = ancestor
		self.pipeline_id = 0001
		wx.ScrolledWindow.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="View Numpy array")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input file: ", "",100,'*.npy')
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 5))
		self.rbampphase = wx.RadioBox(self, label="Type", choices=['Amplitude','Phase', 'Amplitude and Phase', 'Amplitude with Phase', 'Amplitude (cut plane)'],  majorDimension=2, style=wx.RA_SPECIFY_COLS)
		vbox.Add(self.rbampphase,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.Bind(wx.EVT_RADIOBOX, self.OnRadioSelect, self.rbampphase)
		vbox.Add((-1, 5))
		self.sbox1 = wx.StaticBox(self, label="Amplitude", style=wx.SUNKEN_BORDER)
		self.sboxs1 = wx.StaticBoxSizer(self.sbox1,wx.VERTICAL)
		self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		self.contour = SpinnerObject(self,"Isosurface:",MAX_INT,MIN_INT,1,100,100,100)
		self.hbox1.Add(self.contour,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.hbox1.Add((5, -1))
		self.opacity = SpinnerObject(self,"Opacity:",1.0,0.0,0.1,0.5,100,100)
		self.hbox1.Add(self.opacity,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.sboxs1.Add(self.hbox1,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.feature_angle = SpinnerObject(self,"Feature Angle:",180,0,1,90,100,100)
		self.sboxs1.Add(self.feature_angle,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add(self.sboxs1,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 5))
		self.sbox2 = wx.StaticBox(self, label="Phase", style=wx.SUNKEN_BORDER)
		self.sboxs2 = wx.StaticBoxSizer(self.sbox2,wx.VERTICAL)
		self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		self.phasemax = SpinnerObject(self,"Max:",pi,0.0,0.01,pi,50,150)
		self.hbox2.Add(self.phasemax, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.hbox2.Add((5, -1))
		self.phasemin = SpinnerObject(self,"Min:",0.0,-pi,0.01,-pi,50,150)
		self.hbox2.Add(self.phasemin, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.sboxs2.Add(self.hbox2, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add(self.sboxs2, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 10))
		self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		origintext = wx.StaticText(self, label="Origin:",size=(70, 30))
		if IsNotWX4():
			origintext.SetToolTipString("Origin of cut plane")
		else:
			origintext.SetToolTip("Origin of cut plane")
		self.ox = SpinnerObject(self,"x",MAX_INT_16,MIN_INT_16,1,10,15,80)
		self.oy = SpinnerObject(self,"y",MAX_INT_16,MIN_INT_16,1,10,15,80)
		self.oz = SpinnerObject(self,"z",MAX_INT_16,MIN_INT_16,1,10,15,80)
		self.hbox3.Add(origintext ,0, flag=wx.EXPAND|wx.RIGHT, border=10)
		self.hbox3.Add(self.ox ,0, flag=wx.EXPAND|wx.RIGHT, border=5)
		self.hbox3.Add(self.oy ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
		self.hbox3.Add(self.oz ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
		vbox.Add(self.hbox3 ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
		normaltext = wx.StaticText(self, label="Normal:",size=(70, 30))
		if IsNotWX4():
			normaltext.SetToolTipString("Normal to cut plane")
		else:
			normaltext.SetToolTip("Normal to cut plane")
		self.nx = SpinnerObject(self,"x",MAX_INT_16,MIN_INT_16,0.1,1,15,80)
		self.ny = SpinnerObject(self,"y",MAX_INT_16,MIN_INT_16,0.1,0,15,80)
		self.nz = SpinnerObject(self,"z",MAX_INT_16,MIN_INT_16,0.1,0,15,80)
		self.hbox4.Add(normaltext ,0, flag=wx.EXPAND|wx.RIGHT, border=10)
		self.hbox4.Add(self.nx ,0, flag=wx.EXPAND|wx.RIGHT, border=5)
		self.hbox4.Add(self.ny ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
		self.hbox4.Add(self.nz ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
		vbox.Add(self.hbox4 ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		vbox.Add((-1, 5))
		self.hbox5 = wx.BoxSizer(wx.HORIZONTAL)
		spacetext = wx.StaticText(self, label="Spacing:",size=(70, 30))
		if IsNotWX4():
			spacetext.SetToolTipString("Spacing between NumPy array points")
		else:
			spacetext.SetToolTip("Spacing between NumPy array points")
		self.sx = SpinnerObject(self,"x",MAX_INT_16,MIN_INT_16,0.1,1,15,80)
		self.sy = SpinnerObject(self,"y",MAX_INT_16,MIN_INT_16,0.1,1,15,80)
		self.sz = SpinnerObject(self,"z",MAX_INT_16,MIN_INT_16,0.1,1,15,80)
		self.hbox5.Add(spacetext ,0, flag=wx.EXPAND|wx.RIGHT, border=10)
		self.hbox5.Add(self.sx ,0, flag=wx.EXPAND|wx.RIGHT, border=5)
		self.hbox5.Add(self.sy ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
		self.hbox5.Add(self.sz ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
		vbox.Add(self.hbox5 ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		vbox.Add((-1, 5))
		self.hbox6 = wx.BoxSizer(wx.HORIZONTAL)
		self.chkbox_axes = wx.CheckBox(self, -1, 'View axes', size=(200, 20))
		self.chkbox_axes.SetValue(False)
		self.hbox6.Add(self.chkbox_axes, 1,flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.hbox6.Add((-1, 5))
		self.axes_fontfactor = SpinnerObject(self,"Font Factor:",MAX_INT,1,1,2,100,100)
		self.hbox6.Add(self.axes_fontfactor, 0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		vbox.Add(self.hbox6, 0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		vbox.Add((-1, 5))
		button_view = wx.Button(self, label="View", size=(70, 30))
		button_view.Bind(wx.EVT_BUTTON, self.SeqParser )
		vbox.Add(button_view,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
		self.FitInside()
		self.SetScrollRate(5, 5)
		self.OnRadioSelect(None)
	def SeqParser(self,event):
		Sequence_View_Array(self, self.ancestor)
		self.ancestor.GetPage(4).data_poll_timer.Start(1000)
	def OnRadioSelect(self, event):
		rselect = self.rbampphase.GetStringSelection()
		if rselect == 'Amplitude':
			self.sboxs1.ShowItems(True)
			self.sboxs2.ShowItems(False)
			self.hbox3.ShowItems(False)
			self.hbox4.ShowItems(False)
			self.hbox5.ShowItems(False)
			self.Layout()
		elif rselect == 'Amplitude with Phase':
			self.sboxs1.ShowItems(True)
			self.sboxs2.ShowItems(True)
			self.hbox3.ShowItems(False)
			self.hbox4.ShowItems(False)
			self.hbox5.ShowItems(False)
			self.Layout()
		elif rselect == 'Phase':
			self.sboxs1.ShowItems(False)
			self.sboxs2.ShowItems(True)
			self.hbox3.ShowItems(True)
			self.hbox4.ShowItems(True)
			self.hbox5.ShowItems(True)
			self.Layout()
		elif rselect == 'Amplitude (cut plane)':
			self.sboxs1.ShowItems(False)
			self.sboxs2.ShowItems(False)
			self.hbox3.ShowItems(True)
			self.hbox4.ShowItems(True)
			self.hbox5.ShowItems(True)
			self.Layout()
		elif rselect == 'Amplitude and Phase':
			self.sboxs1.ShowItems(True)
			self.sboxs2.ShowItems(True)
			self.hbox3.ShowItems(True)
			self.hbox4.ShowItems(True)
			self.hbox5.ShowItems(True)
			self.Layout()
class SubPanel_Random(wx.Panel):
	treeitem = {'name':  'Random Start' , 'type': 'algsstart'}
	def sequence(self, selff, pipelineitem):
		Sequence_Random(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 1002
		self.start_iter = None
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Random Phase Start")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.amp_max = SpinnerObject(self,"Amp max: ",MAX_INT_16,0.0,1.0,150.0,100,100)
		vbox.Add(self.amp_max, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_ArrayStart(wx.Panel):
	treeitem = {'name':  'Array Start' , 'type': 'algsstart'}
	def sequence(self, selff, pipelineitem):
		Sequence_ArrayStart(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 1003
		self.start_iter = None
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Input Array Start")
		if IsNotWX4():
			title.SetToolTipString("Phase reconstruction will begin with this array.")
		else:
			title.SetToolTip("Phase reconstruction will begin with this array.")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input File: ", "",150,'*.npy')
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_HIO(wx.Panel):
	treeitem = {'name':  'HIO' , 'type': 'algs'}
	def sequence(self, selff, pipelineitem):
		Sequence_HIO(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 1010
		self.start_iter = None
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="HIO Algorithm")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.exp_amps = TextPanelObject(self, "Exp Amp: ", "",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.exp_amps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.chkbox_sqrt_expamps = wx.CheckBox(self, -1, 'Square Root Exp Amp', (50, 10))
		self.chkbox_sqrt_expamps.SetValue(True)
		vbox.Add(self.chkbox_sqrt_expamps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=5)
		self.support = TextPanelObject(self,"Support: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		if IsNotWX4():
			self.support.label.SetToolTipString("Support. If empty, previous instance will be used.")
		else:
			self.support.label.SetToolTip("Support. If empty, previous instance will be used.")
		vbox.Add(self.support, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.beta = SpinnerObject(self,"Beta: ",1.0,0.0,0.01,0.9,100,100)
		vbox.Add(self.beta, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.niter = SpinnerObject(self,"Iterations: ",MAX_INT_16,1,1,1,100,100)
		vbox.Add(self.niter, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_ER(wx.Panel):
	treeitem = {'name':  'ER' , 'type': 'algs'}
	def sequence(self, selff, pipelineitem):
		Sequence_ER(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 1011
		self.start_iter = None
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="ER Algorithm")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.exp_amps = TextPanelObject(self, "Exp Amp: ", "",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.exp_amps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.chkbox_sqrt_expamps = wx.CheckBox(self, -1, 'Square Root Exp Amp', (50, 10))
		self.chkbox_sqrt_expamps.SetValue(True)
		vbox.Add(self.chkbox_sqrt_expamps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=5)
		self.support = TextPanelObject(self,"Support: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		if IsNotWX4():
			self.support.label.SetToolTipString("Support. If empty, previous instance will be used.")
		else:
			self.support.label.SetToolTip("Support. If empty, previous instance will be used.")
		vbox.Add(self.support, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		#self.mask = TextPanelObject(self,"Mask: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		#vbox.Add(self.mask, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.niter = SpinnerObject(self,"Iterations: ",MAX_INT_16,1,1,1,100,100)
		vbox.Add(self.niter, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_ERMask(wx.Panel):
	treeitem = {'name':  'ER Mask' , 'type': 'algs'}
	def sequence(self, selff, pipelineitem):
		Sequence_ERMask(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 1019
		self.start_iter = None
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="ER Mask Algorithm")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.exp_amps = TextPanelObject(self, "Exp Amp: ", "",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.exp_amps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.chkbox_sqrt_expamps = wx.CheckBox(self, -1, 'Square Root Exp Amp', (50, 10))
		self.chkbox_sqrt_expamps.SetValue(True)
		vbox.Add(self.chkbox_sqrt_expamps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=5)
		self.support = TextPanelObject(self,"Support: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		if IsNotWX4():
			self.support.label.SetToolTipString("Support. If empty, previous instance will be used.")
		else:
			self.support.label.SetToolTip("Support. If empty, previous instance will be used.")
		vbox.Add(self.support, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.mask = TextPanelObject(self,"Mask: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.mask, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.niter = SpinnerObject(self,"Iterations: ",MAX_INT_16,1,1,1,100,100)
		vbox.Add(self.niter, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 5))
		self.chkbox = wx.CheckBox(self, -1, 'Relax Modulus Constraint', size=(200, 20))
		if IsNotWX4():
			self.chkbox.SetToolTipString("Do not apply modulus constraint if the change in amplitude"+os.linesep+" is within the Poisson noise.")
		else:
			self.chkbox.SetToolTip("Do not apply modulus constraint if the change in amplitude"+os.linesep+" is within the Poisson noise.")
		self.chkbox.Bind(wx.EVT_CHECKBOX, self.OnCheck)
		vbox.Add(self.chkbox, 0,flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.niter_relax = SpinnerObject(self,"Relax iters: ",MAX_INT_16,0,1,0,100,100)
		if IsNotWX4():
			self.niter_relax.label.SetToolTipString("Reduce the relaxtion to zero linearly over this many iterations.")
		else:
			self.niter_relax.label.SetToolTip("Reduce the relaxtion to zero linearly over this many iterations.")
		self.niter_relax.Disable()
		vbox.Add(self.niter_relax, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.chkbox.Hide()
		self.niter_relax.Hide()
		vbox.Add((-1, 5))
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
	def OnCheck(self,event):
		if self.chkbox.GetValue():
			self.niter_relax.Enable()
		else:
			self.niter_relax.Disable()
class SubPanel_RAAR(wx.Panel):
	treeitem = {'name':  'RAAR' , 'type': 'algs'}
	def sequence(self, selff, pipelineitem):
		Sequence_RAAR(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 1012
		self.start_iter = None
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="RAAR Algorithm")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.exp_amps = TextPanelObject(self, "Exp Amp: ", "",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.exp_amps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.chkbox_sqrt_expamps = wx.CheckBox(self, -1, 'Square Root Exp Amp', (50, 10))
		self.chkbox_sqrt_expamps.SetValue(True)
		vbox.Add(self.chkbox_sqrt_expamps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=5)
		self.support = TextPanelObject(self,"Support: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		if IsNotWX4():
			self.support.label.SetToolTipString("Support. If empty, previous instance will be used.")
		else:
			self.support.label.SetToolTip("Support. If empty, previous instance will be used.")
		vbox.Add(self.support, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.mask = TextPanelObject(self,"Mask: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.mask, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.beta = SpinnerObject(self,"Beta: ",1.0,0.0,0.01,0.9,100,100)
		vbox.Add(self.beta, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.niter = SpinnerObject(self,"Iterations: ",MAX_INT_16,1,1,1,100,100)
		vbox.Add(self.niter, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 5))
		self.chkbox = wx.CheckBox(self, -1, 'Relax Modulus Constraint', size=(200, 20))
		if IsNotWX4():
			self.chkbox.SetToolTipString("Do not apply modulus constraint if the change in amplitude"+os.linesep+" is within the Poisson noise.")
		else:
			self.chkbox.SetToolTip("Do not apply modulus constraint if the change in amplitude"+os.linesep+" is within the Poisson noise.")
		self.chkbox.Bind(wx.EVT_CHECKBOX, self.OnCheck)
		vbox.Add(self.chkbox, 0,flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.niter_relax = SpinnerObject(self,"Relax iters: ",MAX_INT_16,0,1,0,100,100)
		if IsNotWX4():
			self.niter_relax.label.SetToolTipString("Reduce the relaxtion to zero linearly over this many iterations.")
		else:
			self.niter_relax.label.SetToolTip("Reduce the relaxtion to zero linearly over this many iterations.")
		self.niter_relax.Disable()
		vbox.Add(self.niter_relax, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.chkbox.Hide()
		self.niter_relax.Hide()
		vbox.Add((-1, 5))
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
	def OnCheck(self,event):
		if self.chkbox.GetValue():
			self.niter_relax.Enable()
		else:
			self.niter_relax.Disable()
class SubPanel_HPR(wx.Panel):
	treeitem = {'name':  'HPR' , 'type': 'algs'}
	def sequence(self, selff, pipelineitem):
		Sequence_HPR(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 1014
		self.start_iter = None
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="HPR Algorithm")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.exp_amps = TextPanelObject(self, "Exp Amp: ", "",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.exp_amps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.chkbox_sqrt_expamps = wx.CheckBox(self, -1, 'Square Root Exp Amp', (50, 10))
		self.chkbox_sqrt_expamps.SetValue(True)
		vbox.Add(self.chkbox_sqrt_expamps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=5)
		self.support = TextPanelObject(self,"Support: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		if IsNotWX4():
			self.support.label.SetToolTipString("Support. If empty, previous instance will be used.")
		else:
			self.support.label.SetToolTip("Support. If empty, previous instance will be used.")
		vbox.Add(self.support, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.mask = TextPanelObject(self,"Mask: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.mask, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.beta = SpinnerObject(self,"Beta: ",1.0,0.0,0.01,0.9,100,100)
		vbox.Add(self.beta, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.niter = SpinnerObject(self,"Iterations: ",MAX_INT_16,1,1,1,100,100)
		vbox.Add(self.niter, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 5))
		self.chkbox = wx.CheckBox(self, -1, 'Relax Modulus Constraint', size=(200, 20))
		if IsNotWX4():
			self.chkbox.SetToolTipString("Do not apply modulus constraint if the change in amplitude"+os.linesep+" is within the Poisson noise.")
		else:
			self.chkbox.SetToolTip("Do not apply modulus constraint if the change in amplitude"+os.linesep+" is within the Poisson noise.")
		self.chkbox.Bind(wx.EVT_CHECKBOX, self.OnCheck)
		vbox.Add(self.chkbox, 0,flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.niter_relax = SpinnerObject(self,"Relax iters: ",MAX_INT_16,0,1,0,100,100)
		if IsNotWX4():
			self.niter_relax.label.SetToolTipString("Reduce the relaxtion to zero linearly over this many iterations.")
		else:
			self.niter_relax.label.SetToolTip("Reduce the relaxtion to zero linearly over this many iterations.")
		self.niter_relax.Disable()
		vbox.Add(self.niter_relax, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.chkbox.Hide()
		self.niter_relax.Hide()
		vbox.Add((-1, 5))
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
	def OnCheck(self,event):
		if self.chkbox.GetValue():
			self.niter_relax.Enable()
		else:
			self.niter_relax.Disable()
class SubPanel_HIOMask(wx.Panel):
	treeitem = {'name':  'HIO Mask' , 'type': 'algs'}
	def sequence(self, selff, pipelineitem):
		Sequence_HIOMask(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 1015
		self.start_iter = None
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="HIO Algorithm")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.exp_amps = TextPanelObject(self, "Exp Amp: ", "",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.exp_amps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.chkbox_sqrt_expamps = wx.CheckBox(self, -1, 'Square Root Exp Amp', (50, 10))
		self.chkbox_sqrt_expamps.SetValue(True)
		vbox.Add(self.chkbox_sqrt_expamps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=5)
		self.support = TextPanelObject(self,"Support: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		if IsNotWX4():
			self.support.label.SetToolTipString("Support. If empty, previous instance will be used.")
		else:
			self.support.label.SetToolTip("Support. If empty, previous instance will be used.")
		vbox.Add(self.support, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.mask = TextPanelObject(self,"Mask: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.mask, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.beta = SpinnerObject(self,"Beta: ",1.0,0.0,0.01,0.9,100,100)
		vbox.Add(self.beta, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.niter = SpinnerObject(self,"Iterations: ",MAX_INT_16,1,1,1,100,100)
		vbox.Add(self.niter, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 5))
		self.chkbox = wx.CheckBox(self, -1, 'Relax Modulus Constraint', size=(200, 20))
		if IsNotWX4():
			self.chkbox.SetToolTipString("Do not apply modulus constraint if the change in amplitude"+os.linesep+" is within the Poisson noise.")
		else:
			self.chkbox.SetToolTip("Do not apply modulus constraint if the change in amplitude"+os.linesep+" is within the Poisson noise.")
		self.chkbox.Bind(wx.EVT_CHECKBOX, self.OnCheck)
		vbox.Add(self.chkbox, 0,flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.niter_relax = SpinnerObject(self,"Relax iters: ",MAX_INT_16,0,1,0,100,100)
		if IsNotWX4():
			self.niter_relax.label.SetToolTipString("Reduce the relaxtion to zero linearly over this many iterations.")
		else:
			self.niter_relax.label.SetToolTip("Reduce the relaxtion to zero linearly over this many iterations.")
		self.niter_relax.Disable()
		vbox.Add(self.niter_relax, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.chkbox.Hide()
		self.niter_relax.Hide()
		vbox.Add((-1, 5))
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
	def OnCheck(self,event):
		if self.chkbox.GetValue():
			self.niter_relax.Enable()
		else:
			self.niter_relax.Disable()
class SubPanel_POER(wx.Panel):
	treeitem = {'name':  'POER' , 'type': 'algs'}
	def sequence(self, selff, pipelineitem):
		Sequence_POER(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 1018
		self.start_iter = None
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Phase-Only Algorithm")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.exp_amps = TextPanelObject(self, "Exp Amp: ", "",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.exp_amps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.chkbox_sqrt_expamps = wx.CheckBox(self, -1, 'Square Root Exp Amp', (50, 10))
		self.chkbox_sqrt_expamps.SetValue(True)
		vbox.Add(self.chkbox_sqrt_expamps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=5)
		self.support = TextPanelObject(self,"Support: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		if IsNotWX4():
			self.support.label.SetToolTipString("Support. If empty, previous instance will be used.")
		else:
			self.support.label.SetToolTip("Support. If empty, previous instance will be used.")
		vbox.Add(self.support, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.mask = TextPanelObject(self,"Mask: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.mask, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.niter = SpinnerObject(self,"Iterations: ",MAX_INT_16,1,1,1,100,100)
		vbox.Add(self.niter, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_HIOPlus(wx.Panel):
	treeitem = {'name':  'HIO Plus' , 'type': 'algs'}
	def sequence(self, selff, pipelineitem):
		Sequence_HIOPlus(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 1016
		self.start_iter = None
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="HIO Algorithm with positivity constraint")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.exp_amps = TextPanelObject(self, "Exp Amp: ", "",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.exp_amps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.chkbox_sqrt_expamps = wx.CheckBox(self, -1, 'Square Root Exp Amp', (50, 10))
		self.chkbox_sqrt_expamps.SetValue(True)
		vbox.Add(self.chkbox_sqrt_expamps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=5)
		self.support = TextPanelObject(self,"Support: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		if IsNotWX4():
			self.support.label.SetToolTipString("Support. If empty, previous instance will be used.")
		else:
			self.support.label.SetToolTip("Support. If empty, previous instance will be used.")
		vbox.Add(self.support, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.mask = TextPanelObject(self,"Mask: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.mask, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.beta = SpinnerObject(self,"Beta: ",1.0,0.0,0.01,0.9,100,100)
		vbox.Add(self.beta, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.niter = SpinnerObject(self,"Iterations: ",MAX_INT_16,1,1,1,100,100)
		vbox.Add(self.niter, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_PCHIO(wx.Panel):
	treeitem = {'name':  'PCHIO' , 'type': 'algs'}
	def sequence(self, selff, pipelineitem):
		Sequence_PCHIO(selff, pipelineitem)
	def __init__(self, parent):
		from math import pi
		self.pipeline_id = 1017
		self.start_iter = None
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Phase Constrained HIO Algorithm")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.exp_amps = TextPanelObject(self, "Exp Amp: ", "",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.exp_amps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.chkbox_sqrt_expamps = wx.CheckBox(self, -1, 'Square Root Exp Amp', (50, 10))
		self.chkbox_sqrt_expamps.SetValue(True)
		vbox.Add(self.chkbox_sqrt_expamps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=5)
		self.support = TextPanelObject(self,"Support: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		if IsNotWX4():
			self.support.label.SetToolTipString("Support. If empty, previous instance will be used.")
		else:
			self.support.label.SetToolTip("Support. If empty, previous instance will be used.")
		vbox.Add(self.support, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.mask = TextPanelObject(self,"Mask: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.mask, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.beta = SpinnerObject(self,"Beta: ",1.0,0.0,0.01,0.9,100,100)
		vbox.Add(self.beta, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.niter = SpinnerObject(self,"Iterations: ",MAX_INT_16,1,1,1,100,100)
		vbox.Add(self.niter, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.phasemax = SpinnerObject(self,"Phase Max: ",pi,0.0,0.01,pi,100,150)
		vbox.Add(self.phasemax, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.phasemin = SpinnerObject(self,"Phase Min: ",0.0,-pi,0.01,-pi,100,150)
		vbox.Add(self.phasemin, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class QDialog(wx.Dialog):
	def __init__(self, parent, subpanel):
		wx.Dialog.__init__(self, parent, title="Calculate Q-vector", size=(300, 180))
		self.subpanel = subpanel
		vbox = wx.BoxSizer(wx.VERTICAL)
		self.ttheta = NumberObject(self,"2 theta:",self.subpanel.ttheta,80)
		if IsNotWX4():
			self.ttheta.label.SetToolTipString("2 theta angle (radians). "+os.linesep+"Note: Diffraction pattern is assumed "+os.linesep+"to be co-ordinate corrected.")
		else:
			self.ttheta.label.SetToolTip("2 theta angle (radians). "+os.linesep+"Note: Diffraction pattern is assumed "+os.linesep+"to be co-ordinate corrected.")
		self.phi = NumberObject(self,"phi:",self.subpanel.phi,80)
		if IsNotWX4():
			self.phi.label.SetToolTipString("phi angle (radians). "+os.linesep+"Note: Diffraction pattern is assumed "+os.linesep+"to be co-ordinate corrected.")
		else:
			self.phi.label.SetToolTip("phi angle (radians). "+os.linesep+"Note: Diffraction pattern is assumed "+os.linesep+"to be co-ordinate corrected.")
		self.waveln = NumberObject(self,"lambda:",self.subpanel.waveln,80)
		if IsNotWX4():
			self.waveln.label.SetToolTipString("wavelength (nanometers),")
		else:
			self.waveln.label.SetToolTip("wavelength (nanometers),")
		vbox.Add(self.ttheta ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add(self.phi ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add(self.waveln ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.rb = wx.RadioBox(self, label="Coordinate system", choices=['Global','Detector'],  majorDimension=2, style=wx.RA_SPECIFY_COLS)
		if IsNotWX4():
			self.rb.SetToolTipString("Select co-ordinate system for Q-vector. "+os.linesep+"If the Diffraction data is co-ordinate corrected,"+os.linesep+"the global system is appropriate."+os.linesep+"If not, the detector system should be used."+os.linesep+"(i.e. normal to the reflected wave.)")
		else:
			self.rb.SetToolTip("Select co-ordinate system for Q-vector. "+os.linesep+"If the Diffraction data is co-ordinate corrected,"+os.linesep+"the global system is appropriate."+os.linesep+"If not, the detector system should be used."+os.linesep+"(i.e. normal to the reflected wave.)")
		vbox.Add(self.rb ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1,10))
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		self.ok = wx.Button(self, label='Ok', size=(70, 30))
		self.cancel = wx.Button(self, label='Cancel', size=(70, 30))
		hbox.Add(self.ok, 1,flag=wx.EXPAND)
		hbox.Add(self.cancel, 1, flag=wx.EXPAND)
		vbox.Add(hbox ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetSizer(vbox)
		self.ok.Bind(wx.EVT_BUTTON, self.OnOk)
		self.cancel.Bind(wx.EVT_BUTTON, self.OnCancel)
	def OnOk(self, event):
		tth = float(self.ttheta.value.GetValue())
		phi = float(self.phi.value.GetValue())
		waveln = float(self.waveln.value.GetValue())
		self.subpanel.ttheta = tth
		self.subpanel.phi = phi
		self.subpanel.waveln = waveln
		if abs(waveln) < 1e-9:
			self.Destroy()
		else:
			lam = waveln * 10**-9
			qx = math.sin(tth)*math.cos(phi)*(2.0*math.pi)/lam
			qy = math.sin(phi)*(2.0*math.pi)/lam
			qz = (math.cos(tth)*math.cos(phi) - 1.0)*(2.0*math.pi)/lam
			# in detector coords (i.e. normal to k_f)
			qxd = math.cos(tth)*qx - math.sin(tth)*math.sin(phi)*qy - math.sin(tth)*math.cos(phi)*qz
			qyd = math.cos(phi)*qy - math.sin(phi)*qz
			qzd = math.sin(tth)*qx + math.sin(phi)*math.cos(tth)*qy + math.cos(tth)*math.cos(phi)*qz
			coordsystem = self.rb.GetStringSelection()
			if coordsystem == 'Global':
				self.subpanel.qx.value.SetValue(str(qx))
				self.subpanel.qy.value.SetValue(str(qy))
				self.subpanel.qz.value.SetValue(str(qz))
			else:
				self.subpanel.qx.value.SetValue(str(qxd))
				self.subpanel.qy.value.SetValue(str(qyd))
				self.subpanel.qz.value.SetValue(str(qzd))
			self.Destroy()
	def OnCancel(self, event):
		self.EndModal(wx.ID_YES)
		self.Destroy()
class SubPanel_PGCHIO(wx.Panel):
	treeitem = {'name':  'PGCHIO' , 'type': 'algs'}
	def sequence(self, selff, pipelineitem):
		Sequence_PGCHIO(selff, pipelineitem)
	def __init__(self, parent):
		from math import pi
		self.pipeline_id = 1022
		self.start_iter = None
		self.parent = parent
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Phase Gradient Constrained HIO Algorithm")
		if IsNotWX4():
			title.SetToolTipString("Phase is constrained in the direction "+os.linesep+"of the Q-vector.")
		else:
			title.SetToolTip("Phase is constrained in the direction "+os.linesep+"of the Q-vector.")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.exp_amps = TextPanelObject(self, "Exp Amp: ", "",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.exp_amps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.chkbox_sqrt_expamps = wx.CheckBox(self, -1, 'Square Root Exp Amp', (50, 10))
		self.chkbox_sqrt_expamps.SetValue(True)
		vbox.Add(self.chkbox_sqrt_expamps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=5)
		self.support = TextPanelObject(self,"Support: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		if IsNotWX4():
			self.support.label.SetToolTipString("Support. If empty, previous instance will be used.")
		else:
			self.support.label.SetToolTip("Support. If empty, previous instance will be used.")
		vbox.Add(self.support, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.mask = TextPanelObject(self,"Mask: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.mask, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.beta = SpinnerObject(self,"Beta: ",1.0,0.0,0.01,0.9,100,100)
		vbox.Add(self.beta, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.niter = SpinnerObject(self,"Iterations: ",MAX_INT_16,1,1,1,100,100)
		vbox.Add(self.niter, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.phasemax = SpinnerObject(self,"Phase Max: ",2.0*pi,0.0,0.01,pi,100,150)
		vbox.Add(self.phasemax, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.phasemin = SpinnerObject(self,"Phase Min: ",2.0*pi,0.0,0.01,0.0,100,150)
		vbox.Add(self.phasemin, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.qx = NumberObject(self,"Q,x:",0.0,80)
		if IsNotWX4():
			self.qx.label.SetToolTipString("Q vector, x component direction.")
		else:
			self.qx.label.SetToolTip("Q vector, x component direction.")
		vbox.Add(self.qx ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.qy = NumberObject(self,"Q,y:",0.0,80)
		if IsNotWX4():
			self.qy.label.SetToolTipString("Q vector, y component direction.")
		else:
			self.qy.label.SetToolTip("Q vector, y component direction.")
		vbox.Add(self.qy ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.qz = NumberObject(self,"Q,z:",0.0,80)
		if IsNotWX4():
			self.qz.label.SetToolTipString("Q vector, z component direction.")
		else:
			self.qz.label.SetToolTip("Q vector, z component direction.")
		vbox.Add(self.qz ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.ttheta = 0.0
		self.phi = 0.0
		self.waveln = 0.0
		vbox.Add((-1,20))
		self.buttonq = wx.Button(self, label="Calculate Q", size=(100, 30))
		vbox.Add(self.buttonq, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=20)
		self.Bind(wx.EVT_BUTTON, self.OnCalcQ, self.buttonq)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
	def OnCalcQ(self, event):
			calcq = QDialog(self.parent, self)
			calcq.ShowModal()
			calcq.Destroy()
class SubPanel_ShrinkWrap(wx.Panel):
	treeitem = {'name':  'Shrink Wrap' , 'type': 'algs'}
	def sequence(self, selff, pipelineitem):
		Sequence_ShrinkWrap(selff, pipelineitem)
	def __init__(self, parent):
		from math import pi
		self.pipeline_id = 1020
		self.start_iter = None
		self.parent = parent
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Shrink-Wrap Algorithm")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.exp_amps = TextPanelObject(self, "Exp Amp: ", "",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.exp_amps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.chkbox_sqrt_expamps = wx.CheckBox(self, -1, 'Square Root Exp Amp', (50, 10))
		self.chkbox_sqrt_expamps.SetValue(True)
		vbox.Add(self.chkbox_sqrt_expamps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=5)
		self.support = TextPanelObject(self,"Support: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		if IsNotWX4():
			self.support.label.SetToolTipString("Initial support. If empty, previous instance will be used.")
		else:
			self.support.label.SetToolTip("Initial support. If empty, previous instance will be used.")
		vbox.Add(self.support, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.mask = TextPanelObject(self,"Mask: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.mask, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.beta = SpinnerObject(self,"Beta: ",1.0,0.0,0.01,0.9,100,100)
		if IsNotWX4():
			self.beta.label.SetToolTipString("Relaxation parameter.")
		else:
			self.beta.label.SetToolTip("Relaxation parameter.")
		vbox.Add(self.beta, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		self.niter = SpinnerObject(self,"Iterations: ",MAX_INT_16,1,1,100,100,100)
		if IsNotWX4():
			self.niter.label.SetToolTipString("Total number of iterations.")
		else:
			self.niter.label.SetToolTip("Total number of iterations.")
		hbox1.Add(self.niter, 0,  flag=wx.EXPAND|wx.RIGHT, border=5)
		self.cycle = SpinnerObject(self,"Cycle length: ",MAX_INT_16,1,1,30,120,80)
		if IsNotWX4():
			self.cycle.label.SetToolTipString("Number of iterations in a shrink-wrap cycle.")
		else:
			self.cycle.label.SetToolTip("Number of iterations in a shrink-wrap cycle.")
		hbox1.Add(self.cycle, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
		vbox.Add(hbox1, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		self.sigma = SpinnerObject(self,"Sigma: ",5.0,0.0,0.01,0.35,100,100)
		if IsNotWX4():
			self.sigma.label.SetToolTipString("Standard deviation of Gaussian smoothing function for Support.")
		else:
			self.sigma.label.SetToolTip("Standard deviation of Gaussian smoothing function for Support.")
		hbox2.Add(self.sigma, 0,  flag=wx.EXPAND|wx.RIGHT, border=5)
		self.frac = SpinnerObject(self,"threshold: ",1.0,0.0,0.01,0.2,100,100)
		if IsNotWX4():
			self.frac.label.SetToolTipString("Data cut-off threshold for updating the support."+os.linesep+"Data below this fraction is not used for the support.")
		else:
			self.frac.label.SetToolTip("Data cut-off threshold for updating the support."+os.linesep+"Data below this fraction is not used for the support.")
		hbox2.Add(self.frac, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
		vbox.Add(hbox2, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((1,5))
		self.rbrs = wx.RadioBox(self, label="Algorithm:", choices=['HIO','HIOMask','HIOPlus','PCHIO','PGCHIO','ER','HPR','RAAR', 'CSHIO'],  majorDimension=5, style=wx.RA_SPECIFY_COLS)
		if IsNotWX4():
			self.rbrs.SetToolTipString("Select an algorithm for the shrink wrap to use.")
		else:
			self.rbrs.SetToolTip("Select an algorithm for the shrink wrap to use.")
		vbox.Add(self.rbrs ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.Bind(wx.EVT_RADIOBOX, self.OnRadioSelect, self.rbrs)
		self.phasemax = SpinnerObject(self,"Phase Max: ",pi,0.0,0.01,pi,100,150)
		if IsNotWX4():
			self.phasemax.label.SetToolTipString("Maximum phase (PCHIO only).")
		else:
			self.phasemax.label.SetToolTip("Maximum phase (PCHIO only).")
		vbox.Add(self.phasemax, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.phasemin = SpinnerObject(self,"Phase Min: ",0.0,-pi,0.01,-pi,100,150)
		if IsNotWX4():
			self.phasemin.label.SetToolTipString("Minimum phase (PCHIO only).")
		else:
			self.phasemin.label.SetToolTip("Minimum phase (PCHIO only).")
		vbox.Add(self.phasemin, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.phasemax.Hide()
		self.phasemin.Hide()
		self.cs_p = SpinnerObject(self,"p-norm: ",2.0,-2.0,0.01,1.0,100,100)
		if IsNotWX4():
			self.cs_p.label.SetToolTipString("p-normalisation value. "+os.linesep+" (CSHIO only)")
		else:
			self.cs_p.label.SetToolTip("p-normalisation value. "+os.linesep+" (CSHIO only)")
		vbox.Add(self.cs_p, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.cs_epsilon = SpinnerObject(self,"Epsilon: ",MAX_INT_16,0.0,0.01,1.0,100,100)
		if IsNotWX4():
			self.cs_epsilon.label.SetToolTipString("Relaxation parameter. "+os.linesep+" (CSHIO only)")
		else:
			self.cs_epsilon.label.SetToolTip("Relaxation parameter. "+os.linesep+" (CSHIO only)")
		vbox.Add(self.cs_epsilon, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.cs_epsilon_min = SpinnerObject(self,"Epsilon min: ",1.0,0.000000001,0.000000001,0.000001,100,100)
		if IsNotWX4():
			self.cs_epsilon_min.label.SetToolTipString("Relaxation parameter minimum value.")
		else:
			self.cs_epsilon_min.label.SetToolTip("Relaxation parameter minimum value.")
		vbox.Add(self.cs_epsilon_min, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.cs_d = SpinnerObject(self,"Divisor: ",MAX_INT_16,1.0,0.01,2.0,100,100)
		if IsNotWX4():
			self.cs_d.label.SetToolTipString("Number to divide Epsilon when decrement condition is met."+os.linesep+" (CSHIO only)")
		else:
			self.cs_d.label.SetToolTip("Number to divide Epsilon when decrement condition is met."+os.linesep+" (CSHIO only)")
		vbox.Add(self.cs_d, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.cs_eta = SpinnerObject(self,"Eta: ",MAX_INT_16,1.0,0.01,100.0,100,100)
		if IsNotWX4():
			self.cs_eta.label.SetToolTipString("Divisor for decrement condition: "+os.linesep+" i.e sqrt( epsilon )/eta. "+os.linesep+" (CSHIO only)")
		else:
			self.cs_eta.label.SetToolTip("Divisor for decrement condition: "+os.linesep+" i.e sqrt( epsilon )/eta. "+os.linesep+" (CSHIO only)")
		vbox.Add(self.cs_eta, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.chkbox_relax= wx.CheckBox(self, -1, 'Relax Modulus Constraint', (50, 10))
		self.chkbox_relax.SetValue(True)
		vbox.Add(self.chkbox_relax, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=5)
		self.cs_p.Hide()
		self.cs_epsilon.Hide()
		self.cs_epsilon_min.Hide()
		self.cs_d.Hide()
		self.cs_eta.Hide()
		self.chkbox_relax.Hide()
		self.gc_phasemax = SpinnerObject(self,"Phase Max: ",2.0*pi,0.0,0.01,pi,100,150)
		vbox.Add(self.gc_phasemax, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.gc_phasemin = SpinnerObject(self,"Phase Min: ",2.0*pi,0.0,0.01,0.0,100,150)
		vbox.Add(self.gc_phasemin, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.qx = NumberObject(self,"Q,x:",0.0,80)
		if IsNotWX4():
			self.qx.label.SetToolTipString("Q vector, x component direction.")
		else:
			self.qx.label.SetToolTip("Q vector, x component direction.")
		vbox.Add(self.qx ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.qy = NumberObject(self,"Q,y:",0.0,80)
		if IsNotWX4():
			self.qy.label.SetToolTipString("Q vector, y component direction.")
		else:
			self.qy.label.SetToolTip("Q vector, y component direction.")
		vbox.Add(self.qy ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.qz = NumberObject(self,"Q,z:",0.0,80)
		if IsNotWX4():
			self.qz.label.SetToolTipString("Q vector, z component direction.")
		else:
			self.qz.label.SetToolTip("Q vector, z component direction.")
		vbox.Add(self.qz ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.ttheta = 0.0
		self.phi = 0.0
		self.waveln = 0.0
		self.gc_buttonq = wx.Button(self, label="Calculate Q", size=(100, 30))
		vbox.Add(self.gc_buttonq, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=20)
		self.gc_phasemax.Hide()
		self.gc_phasemin.Hide()
		self.qx.Hide()
		self.qy.Hide()
		self.qz.Hide()
		self.gc_buttonq.Hide()
		self.Bind(wx.EVT_BUTTON, self.OnCalcQ, self.gc_buttonq)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
	def OnCalcQ(self, event):
		calcq = QDialog(self.parent, self)
		calcq.ShowModal()
		calcq.Destroy()
	def OnRadioSelect(self, event):
		rselect = self.rbrs.GetStringSelection()
		if rselect == 'HIO' or rselect == 'HIOMask' or rselect == 'HIOPlus' or rselect == 'ER' or rselect == 'HPR' or rselect == 'RAAR':
			self.phasemax.Hide()
			self.phasemin.Hide()
			self.cs_p.Hide()
			self.cs_epsilon.Hide()
			self.cs_epsilon_min.Hide()
			self.cs_d.Hide()
			self.cs_eta.Hide()
			self.chkbox_relax.Hide()
			self.gc_phasemax.Hide()
			self.gc_phasemin.Hide()
			self.qx.Hide()
			self.qy.Hide()
			self.qz.Hide()
			self.gc_buttonq.Hide()
		if rselect == 'PCHIO':
			self.phasemax.Show()
			self.phasemin.Show()
			self.cs_p.Hide()
			self.cs_epsilon.Hide()
			self.cs_epsilon_min.Hide()
			self.cs_d.Hide()
			self.cs_eta.Hide()
			self.chkbox_relax.Hide()
			self.gc_phasemax.Hide()
			self.gc_phasemin.Hide()
			self.qx.Hide()
			self.qy.Hide()
			self.qz.Hide()
			self.gc_buttonq.Hide()
		if rselect == 'CSHIO':
			self.phasemax.Hide()
			self.phasemin.Hide()
			self.cs_p.Show()
			self.cs_epsilon.Show()
			self.cs_epsilon_min.Show()
			self.cs_d.Show()
			self.cs_eta.Show()
			self.chkbox_relax.Show()
			self.gc_phasemax.Hide()
			self.gc_phasemin.Hide()
			self.qx.Hide()
			self.qy.Hide()
			self.qz.Hide()
			self.gc_buttonq.Hide()
		if rselect == 'PGCHIO':
			self.gc_phasemax.Show()
			self.gc_phasemin.Show()
			self.qx.Show()
			self.qy.Show()
			self.qz.Show()
			self.gc_buttonq.Show()
			self.phasemax.Hide()
			self.phasemin.Hide()
			self.cs_p.Hide()
			self.cs_epsilon.Hide()
			self.cs_epsilon_min.Hide()
			self.cs_d.Hide()
			self.cs_eta.Hide()
			self.chkbox_relax.Hide()
		self.Layout()
class SubPanel_CSHIO(wx.Panel):
	treeitem = {'name':  'CSHIO' , 'type': 'algs'}
	def sequence(self, selff, pipelineitem):
		Sequence_CSHIO(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 1040
		self.start_iter = None
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Compressed Sensing HIO Algorithm")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.exp_amps = TextPanelObject(self, "Exp Amp: ", "",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.exp_amps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.chkbox_sqrt_expamps = wx.CheckBox(self, -1, 'Square Root Exp Amp', (50, 10))
		self.chkbox_sqrt_expamps.SetValue(True)
		vbox.Add(self.chkbox_sqrt_expamps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=5)
		self.support = TextPanelObject(self,"Support: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		if IsNotWX4():
			self.support.label.SetToolTipString("Support. If empty, previous instance will be used.")
		else:
			self.support.label.SetToolTip("Support. If empty, previous instance will be used.")
		vbox.Add(self.support, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.mask = TextPanelObject(self,"Mask: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.mask, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.beta = SpinnerObject(self,"Beta: ",1.0,0.0,0.01,0.9,100,100)
		vbox.Add(self.beta, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.niter = SpinnerObject(self,"Iterations: ",MAX_INT_16,1,1,1,100,100)
		vbox.Add(self.niter, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((1,5))
		self.cs_p = SpinnerObject(self,"p-norm: ",2.0,-2.0,0.01,1.0,100,100)
		if IsNotWX4():
			self.cs_p.label.SetToolTipString("p-normalisation value.")
		else:
			self.cs_p.label.SetToolTip("p-normalisation value.")
		vbox.Add(self.cs_p, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.cs_epsilon = SpinnerObject(self,"Epsilon: ",MAX_INT_16,0.0,0.01,1.0,100,150)
		if IsNotWX4():
			self.cs_epsilon.label.SetToolTipString("Relaxation parameter.")
		else:
			self.cs_epsilon.label.SetToolTip("Relaxation parameter.")
		vbox.Add(self.cs_epsilon, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.cs_epsilon_min = SpinnerObject(self,"Epsilon min: ",1.0,0.000000001,0.000000001,0.000001,100,150)
		if IsNotWX4():
			self.cs_epsilon_min.label.SetToolTipString("Relaxation parameter minimum value.")
		else:
			self.cs_epsilon_min.label.SetToolTip("Relaxation parameter minimum value.")
		vbox.Add(self.cs_epsilon_min, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.cs_d = SpinnerObject(self,"Divisor: ",MAX_INT_16,1.0,0.01,2.0,100,150)
		if IsNotWX4():
			self.cs_d.label.SetToolTipString("Number to divide Epsilon when decrement condition is met.")
		else:
			self.cs_d.label.SetToolTip("Number to divide Epsilon when decrement condition is met.")
		vbox.Add(self.cs_d, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.cs_eta = SpinnerObject(self,"Eta: ",MAX_INT_16,1.0,0.01,100.0,100,150)
		if IsNotWX4():
			self.cs_eta.label.SetToolTipString("Divisor for decrement condition: "+os.linesep+" i.e sqrt( epsilon )/eta.")
		else:
			self.cs_eta.label.SetToolTip("Divisor for decrement condition: "+os.linesep+" i.e sqrt( epsilon )/eta.")
		vbox.Add(self.cs_eta, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.chkbox_relax= wx.CheckBox(self, -1, 'Relax Modulus Constraint', (50, 10))
		self.chkbox_relax.SetValue(True)
		vbox.Add(self.chkbox_relax, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=5)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_HIOMaskPC(wx.Panel):
	treeitem = {'name':  'HIO Mask PC' , 'type': 'algs'}
	def sequence(self, selff, pipelineitem):
		Sequence_PhasePC(selff, pipelineitem)
		Sequence_HIOMaskPC(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 1042
		self.start_iter = None
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="HIO Algorithm with Partial Coherence Optimisation")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.exp_amps = TextPanelObject(self, "Exp Amp: ", "",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.exp_amps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.chkbox_sqrt_expamps = wx.CheckBox(self, -1, 'Square Root Exp Amp', (50, 10))
		self.chkbox_sqrt_expamps.SetValue(True)
		vbox.Add(self.chkbox_sqrt_expamps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=5)
		self.support = TextPanelObject(self,"Support: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		if IsNotWX4():
			self.support.label.SetToolTipString("Support. If empty, previous instance will be used.")
		else:
			self.support.label.SetToolTip("Support. If empty, previous instance will be used.")
		vbox.Add(self.support, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.mask = TextPanelObject(self,"Mask: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.mask, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.beta = SpinnerObject(self,"Beta: ",1.0,0.0,0.01,0.9,100,100)
		vbox.Add(self.beta, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.niter = SpinnerObject(self,"Iterations: ",MAX_INT_16,1,1,1,100,100)
		vbox.Add(self.niter, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((1,5))
		self.niterrlpre = SpinnerObject(self,"Iterations preceding R-L optimisation:", MAX_INT_16,1,1,100,300,100)
		if IsNotWX4():
			self.niterrlpre.label.SetToolTipString("Number of HIO iterations performed before R-L Optimisation occurs.")
		else:
			self.niterrlpre.label.SetToolTip("Number of HIO iterations performed before R-L Optimisation occurs.")
		vbox.Add(self.niterrlpre, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.niterrl = SpinnerObject(self,"R-L iterations: ",MAX_INT_16,1,1,10,300,100)
		if IsNotWX4():
			self.niterrl.label.SetToolTipString("Number of Richardon-Lucy iterations.")
		else:
			self.niterrl.label.SetToolTip("Number of Richardon-Lucy iterations.")
		vbox.Add(self.niterrl, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.niterrlinterval = SpinnerObject(self,"Interval between R-L optimisation: ",MAX_INT_16,1,1,50,300,100)
		if IsNotWX4():
			self.niterrlinterval.label.SetToolTipString("")
		else:
			self.niterrlinterval.label.SetToolTip("")
		vbox.Add(self.niterrlinterval, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.accel = SpinnerObject(self,"Acceleration: ",MAX_INT_16,1,1,1,100,100)
		vbox.Add(self.accel, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((1,5))
		self.gammaHWHM = SpinnerObject(self,"Initial PSF HWHM: ",MAX_INT_16,0.0,0.01,0.2,300,100)
		if IsNotWX4():
			self.gammaHWHM.label.SetToolTipString("HWHM of initial FT'd Lorentzian PSF.")
		else:
			self.gammaHWHM.label.SetToolTip("HWHM of initial FT'd Lorentzian PSF.")
		vbox.Add(self.gammaHWHM, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		title1 = wx.StaticText(self, label="Zero fill end dimensions of PSF:")
		vbox.Add(title1 ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.zedims=[{} for i in range(3)]
		self.zedims[0] = SpinnerObject(self,"i",MAX_INT_16,0,1,9,20,60)
		self.zedims[1] = SpinnerObject(self,"j",MAX_INT_16,0,1,9,20,60)
		self.zedims[2] = SpinnerObject(self,"k",MAX_INT_16,0,1,9,20,60)
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1.Add(self.zedims[0], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox1.Add(self.zedims[1], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox1.Add(self.zedims[2], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		vbox.Add(hbox1, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((1,5))
		self.chkbox_reset_gamma = wx.CheckBox(self, -1, 'Reset PSF before the next R-L optimisation cycle.', (50, 10))
		self.chkbox_reset_gamma.SetValue(False)
		vbox.Add(self.chkbox_reset_gamma, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=5)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_ERMaskPC(wx.Panel):
	treeitem = {'name':  'ER Mask PC' , 'type': 'algs'}
	def sequence(self, selff, pipelineitem):
		Sequence_PhasePC(selff, pipelineitem)
		Sequence_ERMaskPC(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 1052
		self.start_iter = None
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="ER Mask Algorithm with Partial Coherence Optimisation")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.exp_amps = TextPanelObject(self, "Exp Amp: ", "",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.exp_amps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.chkbox_sqrt_expamps = wx.CheckBox(self, -1, 'Square Root Exp Amp', (50, 10))
		self.chkbox_sqrt_expamps.SetValue(True)
		vbox.Add(self.chkbox_sqrt_expamps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=5)
		self.support = TextPanelObject(self,"Support: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		if IsNotWX4():
			self.support.label.SetToolTipString("Support. If empty, previous instance will be used.")
		else:
			self.support.label.SetToolTip("Support. If empty, previous instance will be used.")
		vbox.Add(self.support, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.mask = TextPanelObject(self,"Mask: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.mask, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.niter = SpinnerObject(self,"Iterations: ",MAX_INT_16,1,1,1,100,100)
		vbox.Add(self.niter, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((1,5))
		self.niterrlpre = SpinnerObject(self,"Iterations preceding R-L optimisation:", MAX_INT_16,1,1,100,300,100)
		if IsNotWX4():
			self.niterrlpre.label.SetToolTipString("Number of ER iterations performed before R-L Optimisation occurs.")
		else:
			self.niterrlpre.label.SetToolTip("Number of ER iterations performed before R-L Optimisation occurs.")
		vbox.Add(self.niterrlpre, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.niterrl = SpinnerObject(self,"R-L iterations: ",MAX_INT_16,1,1,10,300,100)
		if IsNotWX4():
			self.niterrl.label.SetToolTipString("Number of Richardon-Lucy iterations.")
		else:
			self.niterrl.label.SetToolTip("Number of Richardon-Lucy iterations.")
		vbox.Add(self.niterrl, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.niterrlinterval = SpinnerObject(self,"Interval between R-L optimisation: ",MAX_INT_16,1,1,50,300,100)
		if IsNotWX4():
			self.niterrlinterval.label.SetToolTipString("")
		else:
			self.niterrlinterval.label.SetToolTip("")
		vbox.Add(self.niterrlinterval, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.accel = SpinnerObject(self,"Acceleration: ",MAX_INT_16,1,1,1,100,100)
		vbox.Add(self.accel, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((1,5))
		self.gammaHWHM = SpinnerObject(self,"Initial PSF HWHM: ",MAX_INT_16,0.0,0.01,0.2,300,100)
		if IsNotWX4():
			self.gammaHWHM.label.SetToolTipString("HWHM of initial FT'd Lorentzian PSF.")
		else:
			self.gammaHWHM.label.SetToolTip("HWHM of initial FT'd Lorentzian PSF.")
		vbox.Add(self.gammaHWHM, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		title1 = wx.StaticText(self, label="Zero fill end dimensions of PSF:")
		vbox.Add(title1 ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.zedims=[{} for i in range(3)]
		self.zedims[0] = SpinnerObject(self,"i",MAX_INT_16,0,1,9,20,60)
		self.zedims[1] = SpinnerObject(self,"j",MAX_INT_16,0,1,9,20,60)
		self.zedims[2] = SpinnerObject(self,"k",MAX_INT_16,0,1,9,20,60)
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1.Add(self.zedims[0], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox1.Add(self.zedims[1], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox1.Add(self.zedims[2], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		vbox.Add(hbox1, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((1,5))
		self.chkbox_reset_gamma = wx.CheckBox(self, -1, 'Reset PSF before the next R-L optimisation cycle.', (50, 10))
		self.chkbox_reset_gamma.SetValue(False)
		vbox.Add(self.chkbox_reset_gamma, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=5)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_HPRMaskPC(wx.Panel):
	treeitem = {'name':  'HPR PC' , 'type': 'algs'}
	def sequence(self, selff, pipelineitem):
		Sequence_PhasePC(selff, pipelineitem)
		Sequence_HPRMaskPC(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 1062
		self.start_iter = None
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="HPR Algorithm with Partial Coherence Optimisation")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.exp_amps = TextPanelObject(self, "Exp Amp: ", "",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.exp_amps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.chkbox_sqrt_expamps = wx.CheckBox(self, -1, 'Square Root Exp Amp', (50, 10))
		self.chkbox_sqrt_expamps.SetValue(True)
		vbox.Add(self.chkbox_sqrt_expamps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=5)
		self.support = TextPanelObject(self,"Support: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		if IsNotWX4():
			self.support.label.SetToolTipString("Support. If empty, previous instance will be used.")
		else:
			self.support.label.SetToolTip("Support. If empty, previous instance will be used.")
		vbox.Add(self.support, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.mask = TextPanelObject(self,"Mask: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.mask, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.beta = SpinnerObject(self,"Beta: ",1.0,0.0,0.01,0.9,100,100)
		vbox.Add(self.beta, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.niter = SpinnerObject(self,"Iterations: ",MAX_INT_16,1,1,1,100,100)
		vbox.Add(self.niter, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((1,5))
		self.niterrlpre = SpinnerObject(self,"Iterations preceding R-L optimisation:", MAX_INT_16,1,1,100,300,100)
		if IsNotWX4():
			self.niterrlpre.label.SetToolTipString("Number of HPR iterations performed before R-L Optimisation occurs.")
		else:
			self.niterrlpre.label.SetToolTip("Number of HPR iterations performed before R-L Optimisation occurs.")
		vbox.Add(self.niterrlpre, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.niterrl = SpinnerObject(self,"R-L iterations: ",MAX_INT_16,1,1,10,300,100)
		if IsNotWX4():
			self.niterrl.label.SetToolTipString("Number of Richardon-Lucy iterations.")
		else:
			self.niterrl.label.SetToolTip("Number of Richardon-Lucy iterations.")
		vbox.Add(self.niterrl, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.niterrlinterval = SpinnerObject(self,"Interval between R-L optimisation: ",MAX_INT_16,1,1,50,300,100)
		if IsNotWX4():
			self.niterrlinterval.label.SetToolTipString("")
		else:
			self.niterrlinterval.label.SetToolTip("")
		vbox.Add(self.niterrlinterval, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.accel = SpinnerObject(self,"Acceleration: ",MAX_INT_16,1,1,1,100,100)
		vbox.Add(self.accel, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((1,5))
		self.gammaHWHM = SpinnerObject(self,"Initial PSF HWHM: ",MAX_INT_16,0.0,0.01,0.2,300,100)
		if IsNotWX4():
			self.gammaHWHM.label.SetToolTipString("HWHM of initial FT'd Lorentzian PSF.")
		else:
			self.gammaHWHM.label.SetToolTip("HWHM of initial FT'd Lorentzian PSF.")
		vbox.Add(self.gammaHWHM, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		title1 = wx.StaticText(self, label="Zero fill end dimensions of PSF:")
		vbox.Add(title1 ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.zedims=[{} for i in range(3)]
		self.zedims[0] = SpinnerObject(self,"i",MAX_INT_16,0,1,9,20,60)
		self.zedims[1] = SpinnerObject(self,"j",MAX_INT_16,0,1,9,20,60)
		self.zedims[2] = SpinnerObject(self,"k",MAX_INT_16,0,1,9,20,60)
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1.Add(self.zedims[0], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox1.Add(self.zedims[1], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox1.Add(self.zedims[2], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		vbox.Add(hbox1, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((1,5))
		self.chkbox_reset_gamma = wx.CheckBox(self, -1, 'Reset PSF before the next R-L optimisation cycle.', (50, 10))
		self.chkbox_reset_gamma.SetValue(False)
		vbox.Add(self.chkbox_reset_gamma, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=5)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_RAARMaskPC(wx.Panel):
	treeitem = {'name':  'RAAR PC' , 'type': 'algs'}
	def sequence(self, selff, pipelineitem):
		Sequence_PhasePC(selff, pipelineitem)
		Sequence_RAARMaskPC(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 1072
		self.start_iter = None
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="RAAR Algorithm with Partial Coherence Optimisation")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.exp_amps = TextPanelObject(self, "Exp Amp: ", "",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.exp_amps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.chkbox_sqrt_expamps = wx.CheckBox(self, -1, 'Square Root Exp Amp', (50, 10))
		self.chkbox_sqrt_expamps.SetValue(True)
		vbox.Add(self.chkbox_sqrt_expamps, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=5)
		self.support = TextPanelObject(self,"Support: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		if IsNotWX4():
			self.support.label.SetToolTipString("Support. If empty, previous instance will be used.")
		else:
			self.support.label.SetToolTip("Support. If empty, previous instance will be used.")
		vbox.Add(self.support, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.mask = TextPanelObject(self,"Mask: ","",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.mask, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.beta = SpinnerObject(self,"Beta: ",1.0,0.0,0.01,0.9,100,100)
		vbox.Add(self.beta, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.niter = SpinnerObject(self,"Iterations: ",MAX_INT_16,1,1,1,100,100)
		vbox.Add(self.niter, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((1,5))
		self.niterrlpre = SpinnerObject(self,"Iterations preceding R-L optimisation:", MAX_INT_16,1,1,100,300,100)
		if IsNotWX4():
			self.niterrlpre.label.SetToolTipString("Number of RAAR iterations performed before R-L Optimisation occurs.")
		else:
			self.niterrlpre.label.SetToolTip("Number of RAAR iterations performed before R-L Optimisation occurs.")
		vbox.Add(self.niterrlpre, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.niterrl = SpinnerObject(self,"R-L iterations: ",MAX_INT_16,1,1,10,300,100)
		if IsNotWX4():
			self.niterrl.label.SetToolTipString("Number of Richardon-Lucy iterations.")
		else:
			self.niterrl.label.SetToolTip("Number of Richardon-Lucy iterations.")
		vbox.Add(self.niterrl, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.niterrlinterval = SpinnerObject(self,"Interval between R-L optimisation: ",MAX_INT_16,1,1,50,300,100)
		if IsNotWX4():
			self.niterrlinterval.label.SetToolTipString("")
		else:
			self.niterrlinterval.label.SetToolTip("")
		vbox.Add(self.niterrlinterval, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.accel = SpinnerObject(self,"Acceleration: ",MAX_INT_16,1,1,1,100,100)
		vbox.Add(self.accel, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((1,5))
		self.gammaHWHM = SpinnerObject(self,"Initial PSF HWHM: ",MAX_INT_16,0.0,0.01,0.2,300,100)
		if IsNotWX4():
			self.gammaHWHM.label.SetToolTipString("HWHM of initial FT'd Lorentzian PSF.")
		else:
			self.gammaHWHM.label.SetToolTip("HWHM of initial FT'd Lorentzian PSF.")
		vbox.Add(self.gammaHWHM, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		title1 = wx.StaticText(self, label="Zero fill end dimensions of PSF:")
		vbox.Add(title1 ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.zedims=[{} for i in range(3)]
		self.zedims[0] = SpinnerObject(self,"i",MAX_INT_16,0,1,9,20,60)
		self.zedims[1] = SpinnerObject(self,"j",MAX_INT_16,0,1,9,20,60)
		self.zedims[2] = SpinnerObject(self,"k",MAX_INT_16,0,1,9,20,60)
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1.Add(self.zedims[0], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox1.Add(self.zedims[1], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		hbox1.Add(self.zedims[2], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
		vbox.Add(hbox1, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((1,5))
		self.chkbox_reset_gamma = wx.CheckBox(self, -1, 'Reset PSF before the next R-L optimisation cycle.', (50, 10))
		self.chkbox_reset_gamma.SetValue(False)
		vbox.Add(self.chkbox_reset_gamma, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=5)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_Transform(wx.Panel):
	treeitem = {'name':  'Co-ordinate Transformation' , 'type': 'operpost'}
	def sequence(self, selff, pipelineitem):
		Sequence_Transform(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 2001
		self.start_iter = None
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Rocking Curve Coordinate Transformation")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 5))
		self.rbfrom = wx.RadioBox(self, label="Transform from:", choices=['Sequence data','Input data file'],  majorDimension=2, style=wx.RA_SPECIFY_COLS)
		vbox.Add(self.rbfrom ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.rbtype = wx.RadioBox(self, label="Transform type:", choices=['Real-space','Fourier-space'],  majorDimension=2, style=wx.RA_SPECIFY_COLS)
		vbox.Add(self.rbtype ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input data: ", "output.npy",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename_amp = TextPanelObject(self, "Output amp file: ", "object_amp.vtk",160,"VTK files (*.vtk)|*.vtk|All files (*.*)|*.*")
		vbox.Add(self.output_filename_amp, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename_phase = TextPanelObject(self, "Output phase file: ", "object_phase.vtk",160,"VTK files (*.vtk)|*.vtk|All files (*.*)|*.*")
		vbox.Add(self.output_filename_phase, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 5))
		self.rbcurve = wx.RadioBox(self, label="Rocking curve type:", choices=['Theta', 'Phi'],  majorDimension=3, style=wx.RA_SPECIFY_COLS)
		vbox.Add(self.rbcurve ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		title2 = wx.StaticText(self, label="Array binning: ")
		self.bdims=[{} for i in range(3)]
		self.bdims[0] = SpinnerObject(self,"x",MAX_INT_16,1,1,1,20,60)
		self.bdims[1] = SpinnerObject(self,"y",MAX_INT_16,1,1,1,20,60)
		self.bdims[2] = SpinnerObject(self,"z",MAX_INT_16,1,1,1,20,60)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(title2 ,0, flag=wx.EXPAND|wx.RIGHT, border=10)
		hbox.Add(self.bdims[0], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=2)
		hbox.Add(self.bdims[1], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=2)
		hbox.Add(self.bdims[2], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=2)
		vbox.Add(hbox, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.twotheta = NumberObject(self,"2 theta:",0.0,80)
		if IsNotWX4():
			self.twotheta.label.SetToolTipString("2 theta angle (radians)")
		else:
			self.twotheta.label.SetToolTip("2 theta angle (radians)")
		vbox.Add(self.twotheta ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.dtheta = NumberObject(self,"d theta:",0.0,80)
		if IsNotWX4():
			self.dtheta.label.SetToolTipString("Increment in theta angle (radians)")
		else:
			self.dtheta.label.SetToolTip("Increment in theta angle (radians)")
		vbox.Add(self.dtheta ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.phi = NumberObject(self,"phi:",0.0,80)
		if IsNotWX4():
			self.phi.label.SetToolTipString("Phi angle (radians)")
		else:
			self.phi.label.SetToolTip("Phi angle (radians)")
		vbox.Add(self.phi ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.dphi = NumberObject(self,"d phi:",0.0,80)
		if IsNotWX4():
			self.dphi.label.SetToolTipString("Increment in phi angle (radians)")
		else:
			self.dphi.label.SetToolTip("Increment in phi angle (radians)")
		vbox.Add(self.dphi ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		self.pixelx = NumberObject(self,"Pixel x (microns):",50.0,140)
		if IsNotWX4():
			self.pixelx.label.SetToolTipString("Dimension of detector pixel (microns)")
		else:
			self.pixelx.label.SetToolTip("Dimension of detector pixel (microns)")
		hbox1.Add(self.pixelx ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		hbox1.Add((10, -1))
		self.pixely = NumberObject(self,"Pixel y (microns):",50.0,140)
		if IsNotWX4():
			self.pixely.label.SetToolTipString("Dimension of detector pixel (microns)")
		else:
			self.pixely.label.SetToolTip("Dimension of detector pixel (microns)")
		hbox1.Add(self.pixely ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add(hbox1 ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=0)
		self.waveln = NumberObject(self,"Wavelengh (nm):",0.13,140)
		if IsNotWX4():
			self.waveln.label.SetToolTipString("Wavelengh of light (nanometers)")
		else:
			self.waveln.label.SetToolTip("Wavelengh of light (nanometers)")
		vbox.Add(self.waveln ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.armln = NumberObject(self,"Arm length (m):",1.0,140)
		if IsNotWX4():
			self.armln.label.SetToolTipString("Distance from sample to detector center (meters)")
		else:
			self.armln.label.SetToolTip("Distance from sample to detector center (meters)")
		vbox.Add(self.armln,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 5))
		self.chkbox_ccdflip = wx.CheckBox(self, -1, 'CCD x-axis flip', size=(200, 30))
		self.chkbox_ccdflip.SetValue(True)
		vbox.Add(self.chkbox_ccdflip, flag=wx.ALIGN_LEFT |wx.LEFT, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_Save_Sequence(wx.Panel):
	treeitem = {'name':  'Save Sequence' , 'type': 'operpost'}
	def sequence(self, selff, pipelineitem):
		Sequence_Save_Sequence(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 2010
		self.start_iter = None
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Save sequence data to Numpy array")
		if IsNotWX4():
			title.SetToolTipString("Save sequence to Numpy array. "+os.linesep+"No co-ordinate transformation is performed.")
		else:
			title.SetToolTip("Save sequence to Numpy array. "+os.linesep+"No co-ordinate transformation is performed.")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output File: ", "output.npy",150,'*.npy')
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_Save_Support(wx.Panel):
	treeitem = {'name':  'Save Support' , 'type': 'operpost'}
	def sequence(self, selff, pipelineitem):
		Sequence_Save_Support(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 2012
		self.start_iter = None
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Save support to Numpy array")
		if IsNotWX4():
			title.SetToolTipString("Save support to Numpy array. "+os.linesep+"No co-ordinate transformation is performed.")
		else:
			title.SetToolTip("Save support to Numpy array. "+os.linesep+"No co-ordinate transformation is performed.")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output File: ", "output_support.npy",150,'*.npy')
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_Save_Residual(wx.Panel):
	treeitem = {'name':  'Save Residual' , 'type': 'operpost'}
	def sequence(self, selff, pipelineitem):
		Sequence_Save_Residual(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 2013
		self.start_iter = None
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Save residual data")
		if IsNotWX4():
			title.SetToolTipString("Save residual error data to file (ascii format).")
		else:
			title.SetToolTip("Save residual error data to file (ascii format).")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output File: ", "output_residual.csv",150,'*.csv')
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_Save_Coordinates(wx.Panel):
	treeitem = {'name':  'Save Co-ordinates' , 'type': 'operpost'}
	def sequence(self, selff, pipelineitem):
		Sequence_Save_Coordinates(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 2011
		self.start_iter = None
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="Save Coordinates to Numpy array")
		if IsNotWX4():
			title.SetToolTipString("Save coordinates to Numpy array. "+os.linesep+"A prior co-ordinate transformation\nshould have occured.")
		else:
			title.SetToolTip("Save coordinates to Numpy array. "+os.linesep+"A prior co-ordinate transformation\nshould have occured.")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output File: ", "output_coordinates.npy",150,'*.npy')
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
class SubPanel_View_Object(wx.ScrolledWindow):
	treeitem = {'name':  'View Object' , 'type': 'operpreview'}
	def sequence(self, selff, pipelineitem):
		pass
	def __init__(self,parent,ancestor):
		from math import pi
		self.ancestor = ancestor
		self.pipeline_id = 0002
		wx.ScrolledWindow.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="View Numpy array with coordinate correction")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input file: ", "",100,'*.npy')
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.coords_filename = TextPanelObject(self, "Co-ord's file: ", "",100,'*.npy')
		vbox.Add(self.coords_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 5))
		self.rbampphase = wx.RadioBox(self, label="Type", choices=['Amplitude','Phase', 'Amplitude and Phase', 'Amplitude with Phase', 'Amplitude (cut plane)'],  majorDimension=2, style=wx.RA_SPECIFY_COLS)
		vbox.Add(self.rbampphase,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.Bind(wx.EVT_RADIOBOX, self.OnRadioSelect, self.rbampphase)
		vbox.Add((-1, 10))
		self.sbox1 = wx.StaticBox(self, label="Amplitude", style=wx.SUNKEN_BORDER)
		self.sboxs1 = wx.StaticBoxSizer(self.sbox1,wx.VERTICAL)
		self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		self.contour = SpinnerObject(self,"Isosurface: ",MAX_INT,MIN_INT,1,100,100,100)
		self.hbox1.Add(self.contour,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.hbox1.Add((5, -1))
		self.opacity = SpinnerObject(self,"Opacity: ",1.0,0.0,0.1,0.5,100,100)
		self.hbox1.Add(self.opacity,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.sboxs1.Add(self.hbox1,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.feature_angle = SpinnerObject(self,"Feature Angle:",180,0,1,90,100,100)
		self.sboxs1.Add(self.feature_angle,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add(self.sboxs1,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 5))
		self.sbox2 = wx.StaticBox(self, label="Phase", style=wx.SUNKEN_BORDER)
		self.sboxs2 = wx.StaticBoxSizer(self.sbox2,wx.VERTICAL)
		self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		self.phasemax = SpinnerObject(self,"Max: ",pi,0.0,0.01,pi,50,150)
		self.hbox2.Add(self.phasemax, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.hbox2.Add((5, -1))
		self.phasemin = SpinnerObject(self,"Min: ",0.0,-pi,0.01,-pi,50,150)
		self.hbox2.Add(self.phasemin, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.sboxs2.Add(self.hbox2, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add(self.sboxs2, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 5))
		self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		origintext = wx.StaticText(self, label="Origin:",size=(70, 30))
		if IsNotWX4():
			origintext.SetToolTipString("Origin of cut plane")
		else:
			origintext.SetToolTip("Origin of cut plane")
		self.ox = SpinnerObject(self,"x",MAX_INT_16,MIN_INT_16,1,10,15,80)
		self.oy = SpinnerObject(self,"y",MAX_INT_16,MIN_INT_16,1,10,15,80)
		self.oz = SpinnerObject(self,"z",MAX_INT_16,MIN_INT_16,1,10,15,80)
		self.hbox3.Add(origintext ,0, flag=wx.EXPAND|wx.RIGHT, border=10)
		self.hbox3.Add(self.ox ,0, flag=wx.EXPAND|wx.RIGHT, border=5)
		self.hbox3.Add(self.oy ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
		self.hbox3.Add(self.oz ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
		vbox.Add(self.hbox3 ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
		normaltext = wx.StaticText(self, label="Normal:",size=(70, 30))
		if IsNotWX4():
			normaltext.SetToolTipString("Normal to cut plane")
		else:
			normaltext.SetToolTip("Normal to cut plane")
		self.nx = SpinnerObject(self,"x",MAX_INT_16,MIN_INT_16,0.1,1,15,80)
		self.ny = SpinnerObject(self,"y",MAX_INT_16,MIN_INT_16,0.1,0,15,80)
		self.nz = SpinnerObject(self,"z",MAX_INT_16,MIN_INT_16,0.1,0,15,80)
		self.hbox4.Add(normaltext ,0, flag=wx.EXPAND|wx.RIGHT, border=10)
		self.hbox4.Add(self.nx ,0, flag=wx.EXPAND|wx.RIGHT, border=5)
		self.hbox4.Add(self.ny ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
		self.hbox4.Add(self.nz ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
		vbox.Add(self.hbox4 ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		vbox.Add((-1, 5))
		self.hbox6 = wx.BoxSizer(wx.HORIZONTAL)
		self.chkbox_axes = wx.CheckBox(self, -1, 'View axes', size=(200, 20))
		self.chkbox_axes.SetValue(False)
		self.hbox6.Add(self.chkbox_axes, 1,flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.hbox6.Add((-1, 5))
		self.axes_fontfactor = SpinnerObject(self,"Font Factor:",MAX_INT,1,1,2,100,100)
		self.hbox6.Add(self.axes_fontfactor, 0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		vbox.Add(self.hbox6, 0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		vbox.Add((-1, 5))
		button_view = wx.Button(self, label="View", size=(70, 30))
		button_view.Bind(wx.EVT_BUTTON, self.SeqParser )
		vbox.Add(button_view,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
		self.FitInside()
		self.SetScrollRate(5, 5)
		self.OnRadioSelect(None)
	def SeqParser(self,event):
		Sequence_View_Object(self, self.ancestor)
		self.ancestor.GetPage(4).data_poll_timer.Start(1000)
	def OnRadioSelect(self, event):
		rselect = self.rbampphase.GetStringSelection()
		if rselect == 'Amplitude':
			self.sboxs1.ShowItems(True)
			self.sboxs2.ShowItems(False)
			self.hbox3.ShowItems(False)
			self.hbox4.ShowItems(False)
			self.Layout()
		elif rselect == 'Amplitude with Phase':
			self.sboxs1.ShowItems(True)
			self.sboxs2.ShowItems(True)
			self.hbox3.ShowItems(False)
			self.hbox4.ShowItems(False)
			self.Layout()
		elif rselect == 'Phase':
			self.sboxs1.ShowItems(False)
			self.sboxs2.ShowItems(True)
			self.hbox3.ShowItems(True)
			self.hbox4.ShowItems(True)
			self.Layout()
		elif rselect == 'Amplitude (cut plane)':
			self.sboxs1.ShowItems(False)
			self.sboxs2.ShowItems(False)
			self.hbox3.ShowItems(True)
			self.hbox4.ShowItems(True)
			self.Layout()
		elif rselect == 'Amplitude and Phase':
			self.sboxs1.ShowItems(True)
			self.sboxs2.ShowItems(True)
			self.hbox3.ShowItems(True)
			self.hbox4.ShowItems(True)
			self.Layout()
class SubPanel_View_VTK(wx.ScrolledWindow):
	treeitem = {'name':  'View VTK Array' , 'type': 'operpreview'}
	def sequence(self, selff, pipelineitem):
		pass
	def __init__(self,parent,ancestor):
		from math import pi
		self.ancestor = ancestor
		self.pipeline_id = 0003
		wx.ScrolledWindow.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label="View VTK array")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input file: ", "",100,'*.vtk')
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 5))
		self.rbampphase = wx.RadioBox(self, label="Type", choices=['Amplitude (isosurface)','Phase (cut plane)', 'Amplitude (cut plane)'],  majorDimension=2, style=wx.RA_SPECIFY_COLS)
		vbox.Add(self.rbampphase,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.Bind(wx.EVT_RADIOBOX, self.OnRadioSelect, self.rbampphase)
		vbox.Add((-1, 10))
		#amptext = wx.StaticText(self, label="Amplitude: ")
		#vbox.Add(amptext ,0, flag=wx.EXPAND|wx.RIGHT|wx.LEFT, border=15)
		self.sbox1 = wx.StaticBox(self, label="Amplitude", style=wx.SUNKEN_BORDER)
		self.sboxs1 = wx.StaticBoxSizer(self.sbox1,wx.VERTICAL)
		self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		self.contour = SpinnerObject(self,"Isosurface:",MAX_INT,MIN_INT,1,100,100,100)
		self.hbox1.Add(self.contour,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.feature_angle = SpinnerObject(self,"Feature Angle:",180,0,1,90,100,100)
		self.hbox1.Add(self.feature_angle,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.hbox1.Add((5, -1))
		self.sboxs1.Add(self.hbox1,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add(self.sboxs1,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 5))
		self.sbox2 = wx.StaticBox(self, label="Phase", style=wx.SUNKEN_BORDER)
		self.sboxs2 = wx.StaticBoxSizer(self.sbox2,wx.VERTICAL)
		self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		self.phasemax = SpinnerObject(self,"Max:",pi,0.0,0.01,pi,50,150)
		self.hbox2.Add(self.phasemax, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.hbox2.Add((5, -1))
		self.phasemin = SpinnerObject(self,"Min:",0.0,-pi,0.01,-pi,50,150)
		self.hbox2.Add(self.phasemin, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.sboxs2.Add(self.hbox2, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add(self.sboxs2, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 5))
		self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		origintext = wx.StaticText(self, label="Origin:",size=(70, 30))
		if IsNotWX4():
			origintext.SetToolTipString("Origin of cut plane")
		else:
			origintext.SetToolTip("Origin of cut plane")
		self.ox = SpinnerObject(self,"x",MAX_INT_16,MIN_INT_16,1,0,15,80)
		self.oy = SpinnerObject(self,"y",MAX_INT_16,MIN_INT_16,1,0,15,80)
		self.oz = SpinnerObject(self,"z",MAX_INT_16,MIN_INT_16,1,0,15,80)
		self.hbox3.Add(origintext ,0, flag=wx.EXPAND|wx.RIGHT, border=10)
		self.hbox3.Add(self.ox ,0, flag=wx.EXPAND|wx.RIGHT, border=5)
		self.hbox3.Add(self.oy ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
		self.hbox3.Add(self.oz ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
		vbox.Add(self.hbox3 ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
		normaltext = wx.StaticText(self, label="Normal:",size=(70, 30))
		if IsNotWX4():
			normaltext.SetToolTipString("Normal to cut plane")
		else:
			normaltext.SetToolTip("Normal to cut plane")
		self.nx = SpinnerObject(self,"x",MAX_INT_16,MIN_INT_16,0.1,1,15,80)
		self.ny = SpinnerObject(self,"y",MAX_INT_16,MIN_INT_16,0.1,0,15,80)
		self.nz = SpinnerObject(self,"z",MAX_INT_16,MIN_INT_16,0.1,0,15,80)
		self.hbox4.Add(normaltext ,0, flag=wx.EXPAND|wx.RIGHT, border=10)
		self.hbox4.Add(self.nx ,0, flag=wx.EXPAND|wx.RIGHT, border=5)
		self.hbox4.Add(self.ny ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
		self.hbox4.Add(self.nz ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
		vbox.Add(self.hbox4 ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		vbox.Add((-1, 5))
		self.hbox6 = wx.BoxSizer(wx.HORIZONTAL)
		self.chkbox_axes = wx.CheckBox(self, -1, 'View axes', size=(200, 20))
		self.chkbox_axes.SetValue(False)
		self.hbox6.Add(self.chkbox_axes, 1,flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.hbox6.Add((-1, 5))
		self.axes_fontfactor = SpinnerObject(self,"Font Factor:",MAX_INT,1,1,2,100,100)
		self.hbox6.Add(self.axes_fontfactor, 0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		vbox.Add(self.hbox6, 0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		vbox.Add((-1, 5))
		button_view = wx.Button(self, label="View", size=(70, 30))
		button_view.Bind(wx.EVT_BUTTON, self.SeqParser )
		vbox.Add(button_view,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
		self.FitInside()
		self.SetScrollRate(5, 5)
		self.OnRadioSelect(None)
	def SeqParser(self,event):
		Sequence_View_VTK(self, self.ancestor)
		self.ancestor.GetPage(4).data_poll_timer.Start(1000)
	def OnRadioSelect(self, event):
		rselect = self.rbampphase.GetStringSelection()
		if rselect == 'Amplitude (isosurface)':
			self.sboxs1.ShowItems(True)
			self.sboxs2.ShowItems(False)
			self.hbox3.ShowItems(False)
			self.hbox4.ShowItems(False)
			self.Layout()
		elif rselect == 'Phase (cut plane)':
			self.sboxs1.ShowItems(False)
			self.sboxs2.ShowItems(True)
			self.hbox3.ShowItems(True)
			self.hbox4.ShowItems(True)
			self.Layout()
		elif rselect == 'Amplitude (cut plane)':
			self.sboxs1.ShowItems(False)
			self.sboxs2.ShowItems(False)
			self.hbox3.ShowItems(True)
			self.hbox4.ShowItems(True)
			self.Layout()
class SubPanel_InterpolateObject(wx.Panel):
	treeitem = {'name':  'Interpolate Object' , 'type': 'operpre'}
	def sequence(self, selff, pipelineitem):
		Sequence_InterpolateObject(selff, pipelineitem)
	def __init__(self, parent):
		self.pipeline_id = 0030
		wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, label=" Interpolate array with coordinates onto a regular grid Numpy array")
		if IsNotWX4():
			title.SetToolTipString("")
		else:
			title.SetToolTip("")
		vbox.Add(title ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.input_filename = TextPanelObject(self, "Input file: ", "output.npy",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.input_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.coords_filename = TextPanelObject(self, "Input Co-ord's: ", "coordinates.npy",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.coords_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.output_filename = TextPanelObject(self, "Output file: ", "output_interpolated.npy",100,"Numpy files (*.npy)|*.npy|All files (*.*)|*.*")
		vbox.Add(self.output_filename, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 10))
		title2 = wx.StaticText(self, label=" Array grid size (i,j,k): ")
		if IsNotWX4():
			title2.SetToolTipString("Grid Size")
		else:
			title2.SetToolTip("Grid Size")
		vbox.Add(title2 ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.spacer=[{} for i in range(3)]
		self.spacer[0] = SpinnerObject(self,"i",MAX_INT_16,1,1,100,20,100)
		self.spacer[1] = SpinnerObject(self,"j",MAX_INT_16,1,1,100,20,100)
		self.spacer[2] = SpinnerObject(self,"k",MAX_INT_16,1,1,100,20,100)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.spacer[0], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=2)
		hbox.Add(self.spacer[1], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=2)
		hbox.Add(self.spacer[2], 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=2)
		vbox.Add(hbox, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 10))
		self.interp_range = SpinnerObject(self,"Interpolation Range:",1.0,0.0,0.001,0.001,180,60)
		if IsNotWX4():
			self.interp_range.label.SetToolTipString(" Specify influence distance of each input point. This distance is "+os.linesep+" a fraction of the length of the diagonal of the sample space. "+os.linesep+" Thus, values of 1.0 will cause each input point to influence "+os.linesep+" all points in the structured point dataset. Values less than 1.0 "+os.linesep+" can improve performance significantly.")
		else:
			self.interp_range.label.SetToolTip(" Specify influence distance of each input point. This distance is "+os.linesep+" a fraction of the length of the diagonal of the sample space. "+os.linesep+" Thus, values of 1.0 will cause each input point to influence "+os.linesep+" all points in the structured point dataset. Values less than 1.0 "+os.linesep+" can improve performance significantly.")
		vbox.Add(self.interp_range, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( vbox )