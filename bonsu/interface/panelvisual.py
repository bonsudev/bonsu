#############################################
##   Filename: panelvisual.py
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
import os
import vtk
from .render import wxVTKRenderWindowInteractor
import numpy
from vtk.util import numpy_support
from time import strftime, sleep
from .common import *
from ..operations.wrap import WrapArray
from ..operations.wrap import WrapArrayAmp
import threading, time
if IsNotWX4():
	from .plot import PlotCanvas, PolyLine, PlotGraphics
else:
	from wx.lib.plot.plotcanvas import PlotCanvas, PolyLine
	from wx.lib.plot.polyobjects import PlotGraphics
if IsPy3():
	from queue import Queue
else:
	from Queue import Queue
class AnimateDialog(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, title="Animate Scene", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
		self.SetSizeHints(450,300,-1,-1)
		self.count = 0
		self.count_total = 0
		self.xstep = 0
		self.ystep = 0
		self.zstep = 0
		self.sleep = 0
		self.filename=""
		self.stopmotion = False
		self.parent = parent
		self.panelvisual = self.GetParent()
		vbox = wx.BoxSizer(wx.VERTICAL)
		sbox1 = wx.StaticBox(self, label="Rotate Scene", style=wx.SUNKEN_BORDER)
		sboxs1 = wx.StaticBoxSizer(sbox1,wx.VERTICAL)
		sboxs1.Add((-1, 5))
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		text1 = StaticTextNew(self, label="Axis:",size=(50, 30))
		text1.SetToolTipNew("Axis about which the scene will rotate.")
		self.x = SpinnerObject(self,"x: ",MAX_INT_16,0,1,0,15,80)
		self.y = SpinnerObject(self,"y: ",MAX_INT_16,0,1,0,15,80)
		self.z = SpinnerObject(self,"z: ",MAX_INT_16,0,1,1,15,80)
		hbox1.Add(text1 ,0, flag=wx.EXPAND|wx.RIGHT, border=10)
		hbox1.Add(self.x ,0, flag=wx.EXPAND|wx.RIGHT, border=5)
		hbox1.Add(self.y ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
		hbox1.Add(self.z ,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
		sboxs1.Add(hbox1, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		sboxs1.Add((-1, 5))
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		self.angle = SpinnerObject(self,"Angle: ",360,-360,0.1,5.0,75,80)
		self.angle.label.SetToolTipNew("Angle (degrees) by which the rotation is incremented.")
		hbox2.Add(self.angle ,0, flag=wx.EXPAND|wx.RIGHT, border=5)
		sboxs1.Add(hbox2, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		self.steps = SpinnerObject(self,"Steps: ",MAX_INT_16,1,1,36,75,80)
		hbox3.Add(self.steps ,0, flag=wx.EXPAND|wx.RIGHT, border=5)
		sboxs1.Add(hbox3, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add(sboxs1, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.delay = SpinnerObject(self,"Delay (ms): ",MAX_INT_16,0,10,0,75,80)
		vbox.Add(self.delay ,0, flag=wx.EXPAND|wx.RIGHT, border=5)
		vbox.Add((-1, 10))
		self.chkbox_save = wx.CheckBox(self, -1, 'Save scene', size=(200, 20))
		self.chkbox_save.SetValue(False)
		vbox.Add(self.chkbox_save, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
		vbox.Add((-1, 5))
		self.filename_path = TextPanelObject(self, "Filename: ", "",80,"PNG files (*.png)|*.png|JPEG files (*.jpg)|*.jpg|PPM files (*.ppm)|*.ppm|All files (*.*)|*.*")
		vbox.Add(self.filename_path, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		vbox.Add((-1, 5))
		self.gauge = wx.Gauge(self, range=100, size=(400, 20))
		vbox.Add(self.gauge, 1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=25)
		self.gauge.SetValue(0)
		vbox.Add((-1, 5))
		hbox_btn = wx.BoxSizer(wx.HORIZONTAL)
		button_start = wx.Button(self, label="Start", size=(120, 30))
		hbox_btn.Add(button_start, 1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=0)
		self.Bind(wx.EVT_BUTTON, self.Start, button_start)
		hbox_btn.Add((2, -1))
		button_stop =wx.Button(self, label="Stop", size=(120, 30))
		hbox_btn.Add(button_stop, 1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=0)
		self.Bind(wx.EVT_BUTTON, self.Stop, button_stop)
		hbox_btn.Add((2, -1))
		vbox.Add(hbox_btn, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		vbox.Add((-1, 5))
		self.SetAutoLayout(True)
		self.SetSizer( vbox )
		self.Fit()
		self.Layout()
		self.Show()
	def Start(self,event):
		self.stopmotion = False
		self.count_total = int(self.steps.value.GetValue())
		if self.count >= self.count_total:
			return
		self.gauge.SetRange(self.count_total)
		self.xstep = float(self.angle.value.GetValue())*float(self.x.value.GetValue())
		self.ystep = float(self.angle.value.GetValue())*float(self.y.value.GetValue())
		self.zstep = float(self.angle.value.GetValue())*float(self.z.value.GetValue())
		self.filename = file_ext = os.path.splitext( self.filename_path.objectpath.GetValue() )[0]
		for i in range(self.count,self.count_total):
			if self.stopmotion == False:
				self.OnTimer(None)
				sleep(float(self.delay.value.GetValue())/1000.0)
			else:
				break
			wx.Yield()
		self.count = 0
		self.count_total = 0
	def Stop(self,event):
		self.stopmotion = True
	def OnTimer(self, event):
		renderers = self.parent.renWin.GetRenderWindow().GetRenderers()
		renderers.InitTraversal()
		no_renderers = renderers.GetNumberOfItems()
		for i in range(no_renderers):
			renderers.GetItemAsObject(i).GetActiveCamera().Elevation(self.xstep)
			renderers.GetItemAsObject(i).GetActiveCamera().OrthogonalizeViewUp()
			renderers.GetItemAsObject(i).GetActiveCamera().Roll(self.ystep)
			renderers.GetItemAsObject(i).GetActiveCamera().Azimuth(self.zstep)
		self.panelvisual.RefreshScene()
		wx.Yield()
		if(self.chkbox_save.GetValue() == True):
			image = vtk.vtkWindowToImageFilter()
			image.SetInput(self.parent.renWin.GetRenderWindow())
			image.Update()
			writer = vtk.vtkPNGWriter()
			countstr = str(self.count).rjust(4, "0")
			writer.SetFileName(self.filename+countstr+".png")
			if self.parent.VTKIsNot6:
				writer.SetInput(image.GetOutput())
			else:
				writer.SetInputData(image.GetOutput())
			writer.Write()
		self.count = self.count +1
		self.gauge.SetValue(self.count)
class MeasureDialog(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, title="Measure Scene", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
		self.SetSizeHints(640,480,-1,-1)
		self.Bind(wx.EVT_CLOSE, self.OnExit)
		self.panelvisual = self.GetParent()
		self.nb = wx.Notebook(self)
		self.nb.AddPage(MeasureLine(self.nb), "Line Scan")
		self.nb.AddPage(MeasureAngle(self.nb), "Angle")
		self.nb.AddPage(OrientXYZ(self.nb), "Orientation")
		sizer = wx.BoxSizer()
		sizer.Add(self.nb, 1, wx.EXPAND)
		self.SetSizer(sizer)
		self.Fit()
		self.Layout()
		self.Show()
	def Update(self):
		self.nb.GetPage(0).linewidget.SetEnabled(0)
		bounds = self.panelvisual.image_probe.GetBounds()
		self.nb.GetPage(0).linerep.PlaceWidget(bounds)
		self.nb.GetPage(0).linerep.Modified()
		if self.nb.GetPage(0).chkbox_enable.GetValue() == True:
			self.nb.GetPage(0).linewidget.SetEnabled(1)
			self.nb.GetPage(0).DrawGraph(None,None)
		self.nb.GetPage(1).anglewidget.SetEnabled(0)
		if hasattr(self.panelvisual.data, 'shape'):
			if self.panelvisual.data.shape[2] == 1:
				self.nb.GetPage(1).anglewidget.SetRepresentation(self.nb.GetPage(1).anglerep2D)
			else:
				self.nb.GetPage(1).anglewidget.SetRepresentation(self.nb.GetPage(1).anglerep)
		else:
			self.nb.GetPage(1).anglewidget.SetRepresentation(self.nb.GetPage(1).anglerep)
		if self.nb.GetPage(1).chkbox_enable.GetValue() == True:
			self.nb.GetPage(1).anglewidget.SetEnabled(1)
	def OnExit(self,event):
		self.nb.GetPage(0).linewidget.SetEnabled(0)
		self.nb.GetPage(1).anglewidget.SetEnabled(0)
		self.panelvisual.linewidget = None
		self.panelvisual.anglewidget = None
		del self.panelvisual.meauredialog
		self.Destroy()
		self.panelvisual.EnablePanelPhase(enable=True)
class OrientXYZ(wx.Panel):
	def __init__(self,parent):
		wx.Panel.__init__(self, parent)
		self.panelvisual = self.GetParent().GetParent().GetParent()
		self.cylinder_shaft = vtk.vtkAxesActor().CYLINDER_SHAFT
		self.line_shaft = vtk.vtkAxesActor().LINE_SHAFT
		self.vbox = wx.BoxSizer(wx.VERTICAL)
		self.hbox_btn = wx.BoxSizer(wx.HORIZONTAL)
		self.chkbox_enable = CheckBoxNew(self, -1, 'Enable XYZ Axes')
		self.chkbox_enable.SetToolTipNew("Enable Widget")
		if self.panelvisual.widget.GetEnabled() == 0:
			self.chkbox_enable.SetValue(False)
		else:
			self.chkbox_enable.SetValue(True)
		self.Bind(wx.EVT_CHECKBOX, self.OnChkbox, self.chkbox_enable)
		self.hbox_btn.Add(self.chkbox_enable, 1, flag=wx.EXPAND|wx.CENTER, border=2)
		self.vbox.Add((-1, 5))
		self.vbox.Add(self.hbox_btn, 0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.sbox1 = wx.StaticBox(self, label="Shaft", style=wx.BORDER_DEFAULT)
		self.sboxs1 = wx.StaticBoxSizer(self.sbox1,wx.VERTICAL)
		self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		self.rbshaft1 = wx.RadioButton(self, wx.ID_ANY, label = 'Line', style = wx.RB_GROUP)
		self.rbshaft2 = wx.RadioButton(self, wx.ID_ANY, label = 'Cylinder')
		if self.panelvisual.axes.GetShaftType() == self.cylinder_shaft:
			self.rbshaft1.SetValue(False)
			self.rbshaft2.SetValue(True)
		self.Bind(wx.EVT_RADIOBUTTON, self.OnShaft, self.rbshaft1)
		self.Bind(wx.EVT_RADIOBUTTON, self.OnShaft, self.rbshaft2)
		self.shaft = SpinnerObject(self,"Radius:",1.0,0.0,0.01,self.panelvisual.axes.GetCylinderRadius(),60,60)
		self.shaft.spin.SetEventFunc(self.OnShaftRadiusChange)
		self.shaft_opac = SpinnerObject(self,"Opacity:",1.0,0.0,0.1,self.panelvisual.axes.GetXAxisShaftProperty().GetOpacity(),60,60)
		self.shaft_opac.spin.SetEventFunc(self.OnShaftOpacityChange)
		self.hbox1.Add(self.rbshaft1, 1 , flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.hbox1.Add(self.rbshaft2, 1 , flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.hbox1.Add(self.shaft, 1 , flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=4)
		self.hbox1.Add(self.shaft_opac, 1 , flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=4)
		self.sboxs1.Add(self.hbox1,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.vbox.Add(self.sboxs1,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.vbox.Add((-1, 5))
		self.sbox2 = wx.StaticBox(self, label="Cone", style=wx.BORDER_DEFAULT)
		self.sboxs2 = wx.StaticBoxSizer(self.sbox2,wx.VERTICAL)
		self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		self.cone = SpinnerObject(self,"Radius:",MAX_INT_16,0.0,0.1,self.panelvisual.axes.GetConeRadius(),80,100)
		self.cone.spin.SetEventFunc(self.OnConeRadiusChange)
		self.cone_opac = SpinnerObject(self,"Opacity:",1.0,0.0,0.1,self.panelvisual.axes.GetXAxisTipProperty().GetOpacity(),60,60)
		self.cone_opac.spin.SetEventFunc(self.OnConeOpacityChange)
		self.hbox2.Add(self.cone, 1 , flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=4)
		self.hbox2.Add(self.cone_opac, 1 , flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=4)
		self.sboxs2.Add(self.hbox2,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.vbox.Add(self.sboxs2,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.vbox.Add((-1, 5))
		self.sbox3 = wx.StaticBox(self, label="Labels", style=wx.BORDER_DEFAULT)
		self.sboxs3 = wx.StaticBoxSizer(self.sbox3,wx.VERTICAL)
		self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox31 = wx.BoxSizer(wx.HORIZONTAL)
		self.label_enable = CheckBoxNew(self, -1, 'Enable Label')
		if self.panelvisual.axes.GetAxisLabels() != 0:
			self.label_enable.SetValue(True)
		self.sboxs3.Add(self.label_enable, 0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.Bind(wx.EVT_CHECKBOX, self.OnChkboxLabel, self.label_enable)
		self.labeltitle = wx.StaticText(self, label="Label text:")
		self.labelx = TextCtrlNew(self, value=self.panelvisual.axes.GetXAxisLabelText(), size=(50,-1), style=wx.TE_PROCESS_ENTER)
		self.labely = TextCtrlNew(self, value=self.panelvisual.axes.GetYAxisLabelText(), size=(50,-1), style=wx.TE_PROCESS_ENTER)
		self.labelz = TextCtrlNew(self, value=self.panelvisual.axes.GetZAxisLabelText(), size=(50,-1), style=wx.TE_PROCESS_ENTER)
		self.labelx.Bind(wx.EVT_TEXT, self.OnLabelEdit)
		self.labely.Bind(wx.EVT_TEXT, self.OnLabelEdit)
		self.labelz.Bind(wx.EVT_TEXT, self.OnLabelEdit)
		self.hbox3.Add(self.labelx, 1 , flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.hbox3.Add(self.labely, 1 , flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.hbox3.Add(self.labelz, 1 , flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.labelcolour = wx.StaticText(self, label="Label colour:")
		labelcolours = self.panelvisual.axestext.GetColor()
		self.labelr = SpinnerObject(self,"Red:",1.0,0.0,0.1,labelcolours[0],100,50)
		self.labelg = SpinnerObject(self,"Green:",1.0,0.0,0.1,labelcolours[1],100,50)
		self.labelb = SpinnerObject(self,"Blue:",1.0,0.0,0.1,labelcolours[2],100,50)
		self.labelr.spin.SetEventFunc(self.OnLabelRGB)
		self.labelg.spin.SetEventFunc(self.OnLabelRGB)
		self.labelb.spin.SetEventFunc(self.OnLabelRGB)
		self.hbox31.Add(self.labelr, 1 , flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.hbox31.Add(self.labelg, 1 , flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.hbox31.Add(self.labelb, 1 , flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.labelfontsize = SpinnerObject(self,"Font size:",MAX_INT_16,1,1,self.panelvisual.axestext.GetFontSize(),100,150)
		self.labelfontsize.spin.SetEventFunc(self.OnLabelFontSize)
		self.label_shadow = CheckBoxNew(self, -1, 'Enable Label Shadows')
		if self.panelvisual.axestext.GetShadow() != 0:
			self.label_shadow.SetValue(True)
		self.Bind(wx.EVT_CHECKBOX, self.OnChkboxLabelShadow, self.label_shadow)
		self.sboxs3.Add(self.labeltitle,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.sboxs3.Add(self.hbox3,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.sboxs3.Add(self.labelcolour,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.sboxs3.Add(self.hbox31,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.sboxs3.Add(self.labelfontsize,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=8)
		self.sboxs3.Add(self.label_shadow, 0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=8)
		self.vbox.Add(self.sboxs3,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.sbox4 = wx.StaticBox(self, label="Rotation", style=wx.BORDER_DEFAULT)
		self.sboxs4 = wx.StaticBoxSizer(self.sbox4,wx.VERTICAL)
		self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
		self.rotationangle1 = SpinnerObject(self,"x",180,-180,5,self.panelvisual.axestransformRX,20,40)
		self.rotationangle1.label.SetToolTipNew("Rotation angle in degrees.")
		self.rotationangle2 = SpinnerObject(self,"y",180,-180,5,self.panelvisual.axestransformRY,20,40)
		self.rotationangle2.label.SetToolTipNew("Rotation angle in degrees.")
		self.rotationangle3 = SpinnerObject(self,"z",180,-180,5,self.panelvisual.axestransformRZ,20,40)
		self.rotationangle3.label.SetToolTipNew("Rotation angle in degrees.")
		self.rotationangle1.GetItem(self.rotationangle1.value, recursive=False).SetFlag(wx.EXPAND)
		self.rotationangle1.GetItem(self.rotationangle1.value, recursive=False).SetProportion(1)
		self.rotationangle2.GetItem(self.rotationangle2.value, recursive=False).SetFlag(wx.EXPAND)
		self.rotationangle2.GetItem(self.rotationangle2.value, recursive=False).SetProportion(1)
		self.rotationangle3.GetItem(self.rotationangle3.value, recursive=False).SetFlag(wx.EXPAND)
		self.rotationangle3.GetItem(self.rotationangle3.value, recursive=False).SetProportion(1)
		self.rotationangle1.spin.SetEventFunc(self.OnRotateChange)
		self.rotationangle1.value.Bind(wx.EVT_KEY_DOWN, self.OnRotateKey)
		self.rotationangle2.spin.SetEventFunc(self.OnRotateChange)
		self.rotationangle2.value.Bind(wx.EVT_KEY_DOWN, self.OnRotateKey)
		self.rotationangle3.spin.SetEventFunc(self.OnRotateChange)
		self.rotationangle3.value.Bind(wx.EVT_KEY_DOWN, self.OnRotateKey)
		self.hbox4.Add(self.rotationangle1, 1,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=0)
		self.hbox4.Add(self.rotationangle2, 1,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=0)
		self.hbox4.Add(self.rotationangle3, 1,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=0)
		self.sboxs4.Add(self.hbox4,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.vbox.Add(self.sboxs4,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.vbox.Add((-1, 10))
		self.resolution = SpinnerObject(self,"Resolution: ",MAX_INT_16,1.0,1,self.panelvisual.axes.GetCylinderResolution(),150,100)
		self.resolution.spin.SetEventFunc(self.OnResolutionChange)
		self.vbox.Add(self.resolution,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.SetSizer(self.vbox)
		self.Fit()
		self.Show()
	def OnShaft(self, event):
		rb = event.GetEventObject()
		rselect = rb.GetLabel()
		if rselect == 'Line':
			self.panelvisual.axes.SetShaftTypeToLine()
		elif rselect == 'Cylinder':
			self.panelvisual.axes.SetShaftTypeToCylinder()
		self.panelvisual.RefreshScene()
	def OnShaftRadiusChange(self, event):
		radius = float(self.shaft.value.GetValue())
		self.panelvisual.axes.SetCylinderRadius(radius)
		self.panelvisual.RefreshScene()
	def OnShaftOpacityChange(self, event):
		opac = float(self.shaft_opac.value.GetValue())
		self.panelvisual.axes.GetXAxisShaftProperty().SetOpacity(opac)
		self.panelvisual.axes.GetYAxisShaftProperty().SetOpacity(opac)
		self.panelvisual.axes.GetZAxisShaftProperty().SetOpacity(opac)
		self.panelvisual.RefreshScene()
	def OnConeOpacityChange(self, event):
		opac = float(self.cone_opac.value.GetValue())
		self.panelvisual.axes.GetXAxisTipProperty().SetOpacity(opac)
		self.panelvisual.axes.GetYAxisTipProperty().SetOpacity(opac)
		self.panelvisual.axes.GetZAxisTipProperty().SetOpacity(opac)
		self.panelvisual.RefreshScene()
	def OnConeRadiusChange(self, event):
		radius = float(self.cone.value.GetValue())
		self.panelvisual.axes.SetConeRadius(radius)
		self.panelvisual.RefreshScene()
	def OnChkboxLabel(self, event):
		if self.label_enable.GetValue() == True:
			self.panelvisual.axes.AxisLabelsOn()
		else:
			self.panelvisual.axes.AxisLabelsOff()
		self.panelvisual.RefreshScene()
	def OnChkboxLabelShadow(self, event):
		if self.label_shadow.GetValue() == True:
			self.panelvisual.axestext.ShadowOn()
		else:
			self.panelvisual.axestext.ShadowOff()
		self.panelvisual.RefreshScene()
	def OnLabelEdit(self, event):
		x = self.labelx.GetValue()
		y = self.labely.GetValue()
		z = self.labelz.GetValue()
		self.panelvisual.axes.SetXAxisLabelText(x)
		self.panelvisual.axes.SetYAxisLabelText(y)
		self.panelvisual.axes.SetZAxisLabelText(z)
		self.panelvisual.RefreshScene()
	def OnLabelRGB(self, event):
		r = float(self.labelr.value.GetValue())
		g = float(self.labelg.value.GetValue())
		b = float(self.labelb.value.GetValue())
		self.panelvisual.axestext.SetColor(r,g,b)
		self.panelvisual.RefreshScene()
	def OnLabelFontSize(self, event):
		size = int(float(self.labelfontsize.value.GetValue()))
		self.panelvisual.axestext.SetFontSize(size)
		self.panelvisual.RefreshScene()
	def OnRotateKey(self, event):
		if event.GetKeyCode() == wx.WXK_RETURN:
			self.OnRotateChange(None)
		else:
			event.Skip()
	def OnRotateChange(self, event):
		angle1 = float(self.rotationangle1.value.GetValue())
		angle2 = float(self.rotationangle2.value.GetValue())
		angle3 = float(self.rotationangle3.value.GetValue())
		dx = angle1 - self.panelvisual.axestransformRX
		dy = angle2 - self.panelvisual.axestransformRY
		dz = angle3 - self.panelvisual.axestransformRZ
		self.panelvisual.axestransformRX = angle1
		self.panelvisual.axestransformRY = angle2
		self.panelvisual.axestransformRZ = angle3
		self.panelvisual.axestransform.RotateZ(dz)
		self.panelvisual.axestransform.RotateY(dy)
		self.panelvisual.axestransform.RotateX(dx)
		self.panelvisual.axes.Modified()
		self.panelvisual.RefreshScene()
	def OnResolutionChange(self, event):
		res = int(float(self.resolution.value.GetValue()))
		self.panelvisual.axes.SetCylinderResolution(res)
		self.panelvisual.axes.SetConeResolution(res)
		self.panelvisual.RefreshScene()
	def OnChkbox(self, event):
		if(event.GetEventObject().GetValue() == True):
			if self.panelvisual.widget.GetEnabled() == 0:
				self.panelvisual.widget.SetOutlineColor( 0.9300, 0.5700, 0.1300 )
				self.panelvisual.widget.SetOrientationMarker( self.panelvisual.axes )
				self.panelvisual.widget.SetInteractor(self.panelvisual.renWin)
				self.panelvisual.widget.SetViewport( 0.0, 0.0, 0.1, 0.1 )
				self.panelvisual.widget.SetEnabled( 1 )
				self.panelvisual.widget.InteractiveOn()
				self.panelvisual.RefreshScene()
		else:
			self.panelvisual.widget.SetEnabled( 0 )
			self.panelvisual.RefreshScene()
class LineScan():
	def __init__(self, line, probe):
		self.data = []
		self.p1 = [0.0,0.0,0.0]
		self.p2 = [0.0,0.0,0.0]
		self.nopoints = 2
		if line is None:
			self.line = vtk.vtkLineSource()
		else:
			self.line = line
		self.line.SetResolution(self.nopoints)
		self.line.Modified()
		if probe is None:
			self.probe = vtk.vtkProbeFilter()
		else:
			self.probe = probe
		self.probe.SetInputConnection(self.line.GetOutputPort())
		self.x = None
		self.y = None
	def NumpyToVTK(self, ar, phase=False):
		if phase:
			flat_data= (numpy.angle(ar)).transpose(2,1,0).flatten();
		else:
			flat_data= (numpy.abs(ar)).transpose(2,1,0).flatten();
		vtk_data_array = numpy_support.numpy_to_vtk(flat_data)
		image = vtk.vtkImageData()
		points = image.GetPointData()
		points.SetScalars(vtk_data_array)
		image.SetDimensions(ar.shape)
		image.SetSpacing(1,1,1)
		image.ComputeBounds()
		image.Modified()
		return image
	def NumpyCoordsToVTK(self, ar, coords, phase=False):
		shp = numpy.array(ar.shape, dtype=numpy.int)
		if phase:
			flat_data= (numpy.angle(ar)).transpose(2,1,0).flatten();
		else:
			flat_data= (numpy.abs(ar)).transpose(2,1,0).flatten();
		vtk_data_array = numpy_support.numpy_to_vtk(flat_data)
		vtk_coordarray = numpy_support.numpy_to_vtk(coords)
		object = vtk.vtkStructuredGrid()
		objectpoints = vtk.vtkPoints()
		objectpoints.SetDataTypeToDouble()
		objectpoints.SetNumberOfPoints(ar.size)
		objectpoints.SetData(vtk_coordarray)
		object.SetPoints(objectpoints)
		object.GetPointData().SetScalars(vtk_data_array)
		object.SetDimensions(shp)
		object.Modified()
		return object
	def SetData(self, dataobject):
		from vtk import vtkVersion
		VTKMajor = vtkVersion().GetVTKMajorVersion()
		if VTKMajor < 6:
			self.probe.SetSource(dataobject)
		else:
			self.probe.SetSourceData(dataobject)
	def UpdateLine(self):
		self.probe.Update()
		polydata = self.probe.GetPolyDataOutput()
		scalars = polydata.GetPointData().GetScalars()
		self.data  = []
		for i in range(self.nopoints):
			self.data.append(scalars.GetComponent(i,0))
		l1 = (self.p2[0]-self.p1[0])*(self.p2[0]-self.p1[0])
		l2 = (self.p2[1]-self.p1[1])*(self.p2[1]-self.p1[1])
		l3 = (self.p2[2]-self.p1[2])*(self.p2[2]-self.p1[2])
		length = numpy.sqrt(l1+l2+l3)
		self.x = (length / float(self.nopoints)) * numpy.arange(self.nopoints)
		self.y = numpy.array(self.data)
	def SetPoints(self, p1, p2):
		self.p1 = p1
		self.p2 = p2
		self.line.SetPoint1(self.p1)
		self.line.SetPoint2(self.p2)
		self.line.Modified()
	def SetResolution(self, n):
		self.nopoints = n
		self.line.SetResolution(self.nopoints)
		self.line.Modified()
	def SaveLine(self, filename):
		xy = numpy.vstack((self.x,self.y)).T
		numpy.savetxt(filename, xy, delimiter=',')
class MeasureLine(wx.Panel):
	def __init__(self,parent):
		wx.Panel.__init__(self, parent)
		self.panelvisual = self.GetParent().GetParent().GetParent()
		self.canvas = PlotCanvas(self)
		self.canvas.SetInitialSize(size=self.GetClientSize())
		fontpoint = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT).GetPointSize()
		if IsNotWX4():
			self.canvas.SetShowScrollbars(False)
			self.canvas.SetEnableLegend(True)
			self.canvas.SetGridColour(wx.Colour(0, 0, 0))
			self.canvas.SetForegroundColour(wx.Colour(0, 0, 0))
			self.canvas.SetBackgroundColour(wx.Colour(255, 255, 255))
			self.canvas.SetEnableZoom(False)
			self.canvas.SetFontSizeAxis(point=fontpoint)
			self.canvas.SetFontSizeTitle(point=fontpoint)
		else:
			self.canvas.showScrollbars = False
			self.canvas.enableLegend = True
			self.canvas.enablePointLabel = True
			self.canvas.enableZoom = True
			self.canvas.fontSizeAxis = fontpoint
			self.canvas.fontSizeTitle =fontpoint
		self.vbox = wx.BoxSizer(wx.VERTICAL)
		self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.EXPAND)
		self.hbox_p1 = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox_p2 = wx.BoxSizer(wx.HORIZONTAL)
		self.p1x = NumberObject(self,"P1:x:",0.0,60)
		self.p1y = NumberObject(self,"P1:y:",0.0,60)
		self.p1z = NumberObject(self,"P1:z:",0.0,60)
		self.p2x = NumberObject(self,"P2:x:",0.0,60)
		self.p2y = NumberObject(self,"P2:y:",0.0,60)
		self.p2z = NumberObject(self,"P2:z:",0.0,60)
		self.p1x.value.Bind(wx.EVT_KEY_DOWN, self.SetPointCoords)
		self.p1y.value.Bind(wx.EVT_KEY_DOWN, self.SetPointCoords)
		self.p1z.value.Bind(wx.EVT_KEY_DOWN, self.SetPointCoords)
		self.p2x.value.Bind(wx.EVT_KEY_DOWN, self.SetPointCoords)
		self.p2y.value.Bind(wx.EVT_KEY_DOWN, self.SetPointCoords)
		self.p2z.value.Bind(wx.EVT_KEY_DOWN, self.SetPointCoords)
		self.EnablePointCoordsDisplay(0)
		self.hbox_p1.Add(self.p1x ,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
		self.hbox_p1.Add(self.p1y ,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
		self.hbox_p1.Add(self.p1z ,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
		self.vbox.Add(self.hbox_p1, 0, flag=wx.LEFT | wx.TOP | wx.EXPAND)
		self.hbox_p2.Add(self.p2x ,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
		self.hbox_p2.Add(self.p2y ,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
		self.hbox_p2.Add(self.p2z ,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
		self.vbox.Add(self.hbox_p2, 0, flag=wx.LEFT | wx.TOP | wx.EXPAND)
		self.hbox_btn = wx.BoxSizer(wx.HORIZONTAL)
		self.button_save = wx.Button(self, label="Save Data")
		self.Bind(wx.EVT_BUTTON, self.OnClickSaveButton, self.button_save)
		self.hbox_btn.Add(self.button_save)
		self.hbox_btn.Add((10, -1))
		self.pointcount = SpinnerObject(self,"Data Points",MAX_INT_16,2,1,100,100,80)
		self.pointcount.spin.SetEventFunc(self.OnDataPoints)
		self.Bind(wx.EVT_TEXT, self.OnDataPoints, self.pointcount.value)
		self.hbox_btn.Add(self.pointcount)
		self.hbox_btn.Add((10, -1))
		self.button_reset = wx.Button(self, label="Reset zoom")
		self.button_reset.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnClickResetButton, self.button_reset)
		self.hbox_btn.Add(self.button_reset)
		self.hbox_btn.Add((10, -1))
		self.chkbox_enable = CheckBoxNew(self, -1, 'Enable')
		self.chkbox_enable.SetToolTipNew("Enable Widget")
		self.chkbox_enable.SetValue(False)
		self.Bind(wx.EVT_CHECKBOX, self.OnChkbox, self.chkbox_enable)
		self.hbox_btn.Add(self.chkbox_enable)
		self.chkbox_log = CheckBoxNew(self, -1, 'Log')
		self.chkbox_log.SetToolTipNew("Log Scale")
		self.chkbox_log.SetValue(False)
		self.Bind(wx.EVT_CHECKBOX, self.OnChkboxLog, self.chkbox_log)
		self.hbox_btn.Add(self.chkbox_log)
		self.vbox.Add(self.hbox_btn, 0, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.TOP | wx.EXPAND, border=2)
		self.SetSizer(self.vbox)
		self.Fit()
		self.Show()
		self.data = None
		self.nopoints = int(self.pointcount.value.GetValue())
		self.linerep = vtk.vtkLineRepresentation()
		self.linewidget = vtk.vtkLineWidget2()
		self.line = vtk.vtkLineSource()
		bounds = self.panelvisual.image_probe.GetBounds()
		if (self.panelvisual.measure_data[0] == list(bounds)):
			p1 = self.panelvisual.measure_data[1][0]
			p2 = self.panelvisual.measure_data[1][1]
		else:
			self.panelvisual.measure_data[0] = list(bounds)
			p1 = [bounds[0],bounds[2],bounds[4]]
			p2 = [bounds[1],bounds[3],bounds[5]]
			self.panelvisual.measure_data[1][0] = p1
			self.panelvisual.measure_data[1][1] = p2
		self.linerep.PlaceWidget(bounds)
		self.linerep.SetPoint1WorldPosition(p1)
		self.linerep.SetPoint2WorldPosition(p2)
		self.linerep.DistanceAnnotationVisibilityOff()
		self.linewidget.SetInteractor(self.panelvisual.renWin)
		self.linewidget.SetRepresentation(self.linerep)
		self.linewidget.AddObserver("EndInteractionEvent", self.DrawGraph)
		self.linewidget.SetEnabled(0)
		self.panelvisual.linewidget = self.linewidget
	def OnDataPoints(self, event):
		self.nopoints = int(self.pointcount.value.GetValue())
		if self.nopoints < 1:
			return
		self.DrawGraph(None,None)
		self.panelvisual.ancestor.GetParent().Refresh()
	def EnablePointCoordsDisplay(self,enabled):
		if enabled == 0:
			self.p1x.Disable()
			self.p1y.Disable()
			self.p1z.Disable()
			self.p2x.Disable()
			self.p2y.Disable()
			self.p2z.Disable()
		else:
			self.p1x.Enable()
			self.p1y.Enable()
			self.p1z.Enable()
			self.p2x.Enable()
			self.p2y.Enable()
			self.p2z.Enable()
	def SetPointCoordsDisplay(self,p1,p2):
		self.p1x.value.SetValue(str(p1[0]))
		self.p1y.value.SetValue(str(p1[1]))
		self.p1z.value.SetValue(str(p1[2]))
		self.p2x.value.SetValue(str(p2[0]))
		self.p2y.value.SetValue(str(p2[1]))
		self.p2z.value.SetValue(str(p2[2]))
	def SetPointCoords(self, event):
		if event.GetKeyCode() == wx.WXK_RETURN:
			try:
				p1 = [float(self.p1x.value.GetValue()),float(self.p1y.value.GetValue()),float(self.p1z.value.GetValue())]
				p2 = [float(self.p2x.value.GetValue()),float(self.p2y.value.GetValue()),float(self.p2z.value.GetValue())]
			except:
				return
			self.panelvisual.measure_data[1][0] = p1
			self.panelvisual.measure_data[1][1] = p2
			self.linerep.SetPoint1WorldPosition(p1)
			self.linerep.SetPoint2WorldPosition(p2)
			self.linerep.Modified()
			self.DrawGraph(None,None)
			self.panelvisual.ancestor.GetParent().Refresh()
		else:
			event.Skip()
	def OnClickResetButton(self, event):
		self.canvas.Reset()
	def OnClickSaveButton(self, event):
		x = (self.linerep.GetDistance() / float(self.nopoints)) * numpy.arange(self.nopoints)
		y = numpy.array(self.data)
		xy = numpy.vstack((x,y)).T
		datestr = strftime("%Y-%m-%d_%H.%M.%S")
		numpy.savetxt('linescan_'+datestr+'.csv', xy, delimiter=',')
	def OnChkbox(self, event):
		if(event.GetEventObject().GetValue() == True):
			self.linewidget.SetEnabled(1)
			self.EnablePointCoordsDisplay(1)
			self.button_reset.Enable(True)
			self.panelvisual.ancestor.GetParent().Refresh()
			self.DrawGraph(None,None)
		else:
			self.linewidget.SetEnabled(0)
			self.EnablePointCoordsDisplay(0)
			self.button_reset.Enable(False)
			self.panelvisual.ancestor.GetParent().Refresh()
	def OnChkboxLog(self, event):
		self.panelvisual.ancestor.GetParent().Refresh()
		self.DrawGraph(None,None)
	def DrawGraph(self,object, event):
		self.nopoints = int(self.pointcount.value.GetValue())
		p1 = self.linerep.GetPoint1WorldPosition()
		p2 = self.linerep.GetPoint2WorldPosition()
		self.SetPointCoordsDisplay(p1,p2)
		self.panelvisual.GetParent().GetPage(0).queue_info.put("Line point 1: "+str(p1))
		self.panelvisual.GetParent().GetPage(0).queue_info.put("Line point 2: "+str(p2))
		self.panelvisual.GetParent().GetPage(0).queue_info.put("Line distance: "+str(self.linerep.GetDistance()))
		self.panelvisual.GetParent().GetPage(4).UpdateLog(None)
		self.line.SetResolution(self.nopoints)
		self.line.SetPoint1(p1)
		self.line.SetPoint2(p2)
		self.line.Modified()
		self.panelvisual.measure_data[1][0] = list(p1)
		self.panelvisual.measure_data[1][1] = list(p2)
		probe = vtk.vtkProbeFilter()
		probe.SetInputConnection(self.line.GetOutputPort())
		if self.panelvisual.VTKIsNot6:
			probe.SetSource(self.panelvisual.image_probe)
		else:
			probe.SetSourceData(self.panelvisual.image_probe)
		probe.Update()
		polydata = probe.GetPolyDataOutput()
		scalars = polydata.GetPointData().GetScalars()
		self.data  = []
		for i in range(self.nopoints):
			self.data.append(scalars.GetComponent(i,0))
		x = (self.linerep.GetDistance() / float(self.nopoints)) * numpy.arange(self.nopoints)
		y = numpy.array(self.data)
		graphdata = numpy.vstack((x,y)).T
		line = PolyLine(graphdata, colour='blue', width=2.5)
		if (self.panelvisual.image_probe == self.panelvisual.image_phase_real) or\
			(self.panelvisual.image_probe == self.panelvisual.image2D_phase_real) or\
			(self.panelvisual.image_probe == self.panelvisual.object_phase):
			graphic_y_axis = "Phase"
			self.chkbox_log.Enable(False)
		else:
			graphic_y_axis = "Amplitude"
			self.chkbox_log.Enable(True)
		graphic = PlotGraphics([line],"", "Distance", graphic_y_axis)
		if self.chkbox_log.GetValue() == True:
			if IsNotWX4():
				self.canvas.setLogScale((False,True))
			else:
				self.canvas.logScale = (False,True)
			ymin = numpy.min(y[numpy.nonzero(y)])
			ymax = y.max()
			if ymin < 1e-6:
				ymin = 1e-6
			if ymax > 1e300:
				ymax = 1e300
			self.canvas.Draw(graphic, xAxis=(x.min(), x.max()), yAxis=(ymin, ymax))
		else:
			if IsNotWX4():
				self.canvas.setLogScale((False,True))
			else:
				self.canvas.logScale = (False,False)
			self.canvas.Draw(graphic, xAxis=(x.min(), x.max()), yAxis=(y.min(), y.max()))
		self.Refresh()
class MeasureAngle(wx.Panel):
	def __init__(self,parent):
		wx.Panel.__init__(self, parent)
		self.panelvisual = self.GetParent().GetParent().GetParent()
		self.vbox = wx.BoxSizer(wx.VERTICAL)
		self.vbox.Add((-1, 10))
		self.info = wx.StaticText(self, -1, label="First, select three points in free "+os.linesep+"space to create an angle.", style=wx.ALIGN_LEFT)
		self.vbox.Add(self.info, 1, flag=wx.LEFT | wx.RIGHT | wx.EXPAND, border=15)
		self.vbox.Add((-1, 10))
		self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		txtp1label = wx.StaticText(self, -1, label="Point 1:", style=wx.ALIGN_RIGHT, size=(120,30))
		self.hbox1.Add(txtp1label, 0, flag=wx.LEFT | wx.RIGHT, border=0)
		self.txtp1 = wx.TextCtrl(self, value="", style=wx.TE_READONLY, size=(-1,30))
		self.txtp1.SetEditable(False)
		self.hbox1.Add(self.txtp1, 1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=0)
		self.vbox.Add(self.hbox1, 1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)
		self.vbox.Add((-1, 10))
		self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		txtp2label = wx.StaticText(self, -1, label="Point 2:", style=wx.ALIGN_RIGHT, size=(120,30))
		self.hbox2.Add(txtp2label, 0, flag=wx.LEFT | wx.RIGHT, border=0)
		self.txtp2 = wx.TextCtrl(self, value="", style=wx.TE_READONLY, size=(-1,30))
		self.txtp2.SetEditable(False)
		self.hbox2.Add(self.txtp2, 1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=0)
		self.vbox.Add(self.hbox2, 1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)
		self.vbox.Add((-1, 10))
		self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		txtc0label = wx.StaticText(self, -1, label="Centre:", style=wx.ALIGN_RIGHT, size=(120,30))
		self.hbox3.Add(txtc0label, 0, flag=wx.LEFT | wx.RIGHT, border=0)
		self.txtc0 = wx.TextCtrl(self, value="", style=wx.TE_READONLY, size=(-1,30))
		self.txtc0.SetEditable(False)
		self.hbox3.Add(self.txtc0, 1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=0)
		self.vbox.Add(self.hbox3, 1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)
		self.vbox.Add((-1, 10))
		self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
		txtanglelabel = wx.StaticText(self, -1, label="Angle:", style=wx.ALIGN_RIGHT, size=(120,30))
		self.hbox4.Add(txtanglelabel, 0, flag=wx.LEFT | wx.RIGHT, border=0)
		self.txtangle = wx.TextCtrl(self, value="", style=wx.TE_READONLY , size=(-1,30))
		self.txtangle.SetEditable(False)
		self.hbox4.Add(self.txtangle, 1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=0)
		self.vbox.Add(self.hbox4, 1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)
		self.vbox.Add((-1, 10))
		self.hbox_btn = wx.BoxSizer(wx.HORIZONTAL)
		self.chkbox_enable = CheckBoxNew(self, -1, 'Enable', size=(120, 25))
		self.chkbox_enable.SetToolTipNew("Enable Widget")
		self.chkbox_enable.SetValue(False)
		self.Bind(wx.EVT_CHECKBOX, self.OnChkbox, self.chkbox_enable)
		self.hbox_btn.Add(self.chkbox_enable, flag=wx.LEFT | wx.RIGHT | wx.EXPAND, border=260)
		self.vbox.Add(self.hbox_btn, 0, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.TOP | wx.EXPAND, border=5)
		self.vbox.Add((-1, 10))
		self.SetSizer(self.vbox)
		self.Fit()
		bounds = self.panelvisual.image_probe.GetBounds()
		if (self.panelvisual.measure_data[2] == list(bounds)):
			p1 = self.panelvisual.measure_data[3][0]
			p2 = self.panelvisual.measure_data[3][1]
			c0 = self.panelvisual.measure_data[3][2]
		else:
			self.panelvisual.measure_data[2] = list(bounds)
			p1 = [bounds[0],bounds[2],bounds[4]]
			p2 = [bounds[1],bounds[3],bounds[5]]
			c0 = [bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4]]
			self.panelvisual.measure_data[3][0] = p1
			self.panelvisual.measure_data[3][1] = p2
			self.panelvisual.measure_data[3][2] = c0
		self.handle = vtk.vtkPointHandleRepresentation3D()
		self.handle.PlaceWidget(bounds)
		self.handle.SetHandleSize(20)
		self.anglerep = vtk.vtkAngleRepresentation3D()
		self.anglerep.SetHandleRepresentation(self.handle)
		self.anglerep.InstantiateHandleRepresentation()
		self.anglerep.SetPoint1WorldPosition(p1)
		self.anglerep.SetPoint2WorldPosition(p2)
		self.anglerep.SetCenterWorldPosition(c0)
		self.anglerep.GetPoint1Representation().GetProperty().SetColor(1,0,0)
		self.anglerep.GetPoint1Representation().GetProperty().SetLineWidth(4)
		self.anglerep.GetPoint2Representation().GetProperty().SetColor(1,0,0)
		self.anglerep.GetPoint2Representation().GetProperty().SetLineWidth(4)
		self.anglerep.GetCenterRepresentation().GetProperty().SetColor(1,0,0)
		self.anglerep.GetCenterRepresentation().GetProperty().SetLineWidth(4)
		self.anglerep.GetRay1().GetProperty().SetLineWidth(1)
		self.anglerep.GetRay2().GetProperty().SetLineWidth(1)
		self.anglerep.GetArc().GetProperty().SetLineWidth(1)
		self.anglerep.GetRay1().GetProperty().SetColor(1,1,1)
		self.anglerep.GetRay2().GetProperty().SetColor(1,1,1)
		self.anglerep.GetArc().GetProperty().SetColor(1,1,1)
		self.anglerep.GetTextActor().GetProperty().SetColor(1,1,1)
		self.anglerep.GetTextActor().GetProperty().SetLineWidth(1)
		self.anglerep.BuildRepresentation()
		self.anglerep2D = vtk.vtkAngleRepresentation2D()
		self.anglerep2D.InstantiateHandleRepresentation()
		self.anglerep2D.SetPoint1DisplayPosition(p1)
		self.anglerep2D.SetPoint2DisplayPosition(p2)
		self.anglerep2D.SetCenterDisplayPosition(c0)
		self.anglerep2D.ArcVisibilityOff()
		self.anglerep2D.GetPoint1Representation().GetProperty().SetColor(1,0,0)
		self.anglerep2D.GetPoint1Representation().GetProperty().SetLineWidth(2)
		self.anglerep2D.GetPoint2Representation().GetProperty().SetColor(1,0,0)
		self.anglerep2D.GetPoint2Representation().GetProperty().SetLineWidth(2)
		self.anglerep2D.GetCenterRepresentation().GetProperty().SetColor(1,0,0)
		self.anglerep2D.GetCenterRepresentation().GetProperty().SetLineWidth(2)
		self.anglerep2D.GetRay1().SetArrowLength(5)
		self.anglerep2D.GetRay2().SetArrowLength(5)
		self.anglerep2D.GetArc().GetProperty().SetLineWidth(1)
		self.anglerep2D.GetArc().GetLabelTextProperty().BoldOff()
		self.anglerep2D.GetArc().GetLabelTextProperty().SetFontSize(6)
		self.anglerep2D.GetArc().SetLabelFactor(0.5)
		self.anglerep2D.BuildRepresentation()
		self.anglewidget = vtk.vtkAngleWidget()
		self.anglewidget.SetInteractor(self.panelvisual.renWin)
		self.anglewidget.CreateDefaultRepresentation()
		if hasattr(self.panelvisual.data, 'shape'):
			if self.panelvisual.data.shape[2] == 1:
				self.anglewidget.SetRepresentation(self.anglerep2D)
			else:
				self.anglewidget.SetRepresentation(self.anglerep)
		else:
			self.anglewidget.SetRepresentation(self.anglerep)
		self.anglewidget.AddObserver("EndInteractionEvent", self.UpdatePanel)
		self.anglewidget.SetEnabled(0)
		self.panelvisual.anglewidget = self.anglewidget
	def UpdatePanel(self,object, event):
		p1 = self.anglewidget.GetRepresentation().GetPoint1Representation().GetWorldPosition()
		p2 = self.anglewidget.GetRepresentation().GetPoint2Representation().GetWorldPosition()
		c0 = self.anglewidget.GetRepresentation().GetCenterRepresentation().GetWorldPosition()
		angle = self.anglewidget.GetRepresentation().GetAngle()
		self.txtp1.Clear()
		self.txtp1.WriteText(str(p1))
		self.txtp2.Clear()
		self.txtp2.WriteText(str(p2))
		self.txtc0.Clear()
		self.txtc0.WriteText(str(c0))
		self.txtangle.Clear()
		self.txtangle.WriteText(str(angle))
	def OnChkbox(self, event):
		if(event.GetEventObject().GetValue() == True):
			self.anglewidget.SetEnabled(1)
			self.panelvisual.ancestor.GetParent().Refresh()
		else:
			self.anglewidget.SetEnabled(0)
			self.panelvisual.ancestor.GetParent().Refresh()
class ContourDialog(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, title="Set Contour Value", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
		self.SetSizeHints(350,250,-1,-1)
		self.Bind(wx.EVT_CLOSE, self.OnExit)
		self.parent = parent
		self.panelvisual = self.GetParent()
		self.vbox = wx.BoxSizer(wx.VERTICAL)
		self.vbox.Add((-1, 5))
		ivalue = int(self.panelvisual.filter_amp_real.GetValue(0))
		self.contour_real = SpinnerObject(self,"RSI:",MAX_INT,0,1,ivalue,50,90)
		self.contour_real.label.SetToolTipNew("Real space isosurface")
		self.contour_real.GetItem(self.contour_real.value, recursive=False).SetFlag(wx.EXPAND)
		self.contour_real.GetItem(self.contour_real.value, recursive=False).SetProportion(1)
		self.contour_real.spin.SetEventFunc(self.OnContourReal)
		self.contour_real.value.Bind(wx.EVT_KEY_UP, self.OnContourRealKey)
		self.vbox.Add(self.contour_real,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.vbox.Add((-1, 5))
		ivalue = int(self.panelvisual.filter_amp_recip.GetValue(0))
		self.contour_recip = SpinnerObject(self,"FSI:",MAX_INT,0,1,ivalue,50,90)
		self.contour_recip.label.SetToolTipNew("Fourier space isosurface")
		self.contour_recip.GetItem(self.contour_recip.value, recursive=False).SetFlag(wx.EXPAND)
		self.contour_recip.GetItem(self.contour_recip.value, recursive=False).SetProportion(1)
		self.contour_recip.spin.SetEventFunc(self.OnContourRecip)
		self.contour_recip.value.Bind(wx.EVT_KEY_UP, self.OnContourRecipKey)
		self.vbox.Add(self.contour_recip,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.vbox.Add((-1, 5))
		ivalue = float(self.panelvisual.filter_support.GetValue(0))
		self.contour_support = SpinnerObject(self,"SI:",1.0,0.0,0.1,ivalue,50,90)
		self.contour_support.label.SetToolTipNew("Support isosurface")
		self.contour_support.GetItem(self.contour_support.value, recursive=False).SetFlag(wx.EXPAND)
		self.contour_support.GetItem(self.contour_support.value, recursive=False).SetProportion(1)
		self.contour_support.spin.SetEventFunc(self.OnContourSupport)
		self.contour_support.value.Bind(wx.EVT_KEY_UP, self.OnContourSupportKey)
		self.vbox.Add(self.contour_support,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.SetAutoLayout(True)
		self.SetSizer( self.vbox )
		self.Fit()
		self.Layout()
		self.Show()
	def OnExit(self,event):
		del self.panelvisual.contourdialog
		self.Destroy()
		if self.panelvisual.ancestor.GetPage(0).pipeline_started == False:
			self.panelvisual.EnablePanelPhase(enable=True)
	def OnContourRealKey(self, event):
		if event.GetKeyCode() != (wx.WXK_RETURN or wx.WXK_NUMPAD_ENTER):
			event.Skip()
		else:
			self.OnContourReal(event)
	def OnContourReal(self, event):
		if self.panelvisual.filter_amp_real.GetTotalNumberOfInputConnections() > 0:
			try:
				contour = float(self.contour_real.value.GetValue())
			except:
				return
			if self.panelvisual.data is None:
				max = self.panelvisual.ancestor.GetPage(0).seqdata_max
			else:
				max = self.panelvisual.data_max
			if contour > max: contour = CNTR_CLIP*max;
			if contour <= 0.0: contour = (1.0-CNTR_CLIP);
			self.panelvisual.filter_amp_real.SetValue( 0, contour)
			self.panelvisual.filter_amp_real.Modified()
			self.panelvisual.filter_amp_real.Update()
			if self.panelvisual.filter_plane.GetTotalNumberOfInputConnections() > 0:
				self.panelvisual.filter_plane.SetValue( 0, contour)
				self.panelvisual.filter_plane.Modified()
				self.panelvisual.filter_plane.Update()
			if event is not None:
				event.Skip()
				self.panelvisual.RefreshScene()
	def OnContourRecipKey(self, event):
		if event.GetKeyCode() != (wx.WXK_RETURN or wx.WXK_NUMPAD_ENTER):
			event.Skip()
		else:
			self.OnContourRecip(event)
	def OnContourRecip(self, event):
		if self.panelvisual.filter_amp_recip.GetTotalNumberOfInputConnections() > 0:
			try:
				contour = float(self.contour_recip.value.GetValue())
			except:
				return
			if self.panelvisual.data is None:
				max = self.panelvisual.ancestor.GetPage(0).seqdata_max_recip
			else:
				max = self.panelvisual.data_max_recip
			if contour > max: contour = CNTR_CLIP*max;
			if contour <= 0.0: contour = (1.0-CNTR_CLIP);
			self.panelvisual.filter_amp_recip.SetValue( 0, contour)
			self.panelvisual.filter_amp_recip.Modified()
			self.panelvisual.filter_amp_recip.Update()
			if event is not None:
				event.Skip()
				self.panelvisual.RefreshScene()
	def OnContourSupportKey(self, event):
		if event.GetKeyCode() != (wx.WXK_RETURN or wx.WXK_NUMPAD_ENTER):
			event.Skip()
		else:
			self.OnContourSupport(event)
	def OnContourSupport(self, event):
		if self.panelvisual.filter_support.GetTotalNumberOfInputConnections() > 0:
			try:
				contour = float(self.contour_support.value.GetValue())
			except:
				return
			if self.panelvisual.data is None:
				max = self.panelvisual.ancestor.GetPage(0).seqdata_max_support
			else:
				max = self.panelvisual.data_max_support
			if contour > max: contour = CNTR_CLIP*max;
			if contour <= 0.0: contour = (1.0-CNTR_CLIP);
			self.panelvisual.filter_support.SetValue( 0, contour)
			self.panelvisual.filter_support.Modified()
			self.panelvisual.filter_support.Update()
			if event is not None:
				event.Skip()
				self.panelvisual.RefreshScene()
class DataRangeDialog(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, title="Set lookup table data range", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
		self.SetSizeHints(450,380,-1,-1)
		from math import floor, log10, pi
		self.parent = parent
		self.panelvisual = self.GetParent()
		self.vbox = wx.BoxSizer(wx.VERTICAL)
		self.vbox.Add((-1, 5))
		self.sbox1 = wx.StaticBox(self, label="Real Amplitude", style=wx.BORDER_DEFAULT)
		self.sboxs1 = wx.StaticBoxSizer(self.sbox1,wx.VERTICAL)
		self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		range = self.panelvisual.lut_amp_real.GetTableRange()
		self.real_amp_max = SpinnerObject(self,"Max: ",MAX_INT,MIN_INT,1,range[1],100,100)
		self.real_amp_min = SpinnerObject(self,"Min: ",MAX_INT,MIN_INT,1,range[0],100,100)
		self.real_amp_max.GetItem(self.real_amp_max.value, recursive=False).SetFlag(wx.EXPAND)
		self.real_amp_max.GetItem(self.real_amp_max.value, recursive=False).SetProportion(1)
		self.real_amp_min.GetItem(self.real_amp_min.value, recursive=False).SetFlag(wx.EXPAND)
		self.real_amp_min.GetItem(self.real_amp_min.value, recursive=False).SetProportion(1)
		self.hbox1.Add(self.real_amp_max,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.hbox1.Add(self.real_amp_min,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.real_amp_log = CheckBoxNew(self, -1, ' Log', size=(100, 50))
		self.hbox1.Add((10, -1))
		self.hbox1.Add(self.real_amp_log, 0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.sboxs1.Add(self.hbox1,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.vbox.Add(self.sboxs1,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.CheckLog(self.panelvisual.lut_amp_real, self.real_amp_log)
		self.vbox.Add((-1, 5))
		self.sbox2 = wx.StaticBox(self, label="Real Phase", style=wx.BORDER_DEFAULT)
		self.sboxs2 = wx.StaticBoxSizer(self.sbox2,wx.VERTICAL)
		self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		range = self.panelvisual.lut_phase_real.GetTableRange()
		self.real_phase_max = SpinnerObject(self,"Max: ",MAX_INT_16,MIN_INT_16,0.01,range[1],100,100)
		self.real_phase_min = SpinnerObject(self,"Min: ",MAX_INT_16,MIN_INT_16,0.01,range[0],100,100)
		self.real_phase_max.GetItem(self.real_phase_max.value, recursive=False).SetFlag(wx.EXPAND)
		self.real_phase_max.GetItem(self.real_phase_max.value, recursive=False).SetProportion(1)
		self.real_phase_min.GetItem(self.real_phase_min.value, recursive=False).SetFlag(wx.EXPAND)
		self.real_phase_min.GetItem(self.real_phase_min.value, recursive=False).SetProportion(1)
		self.hbox2.Add(self.real_phase_max,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.hbox2.Add(self.real_phase_min,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.real_phase_log = CheckBoxNew(self, -1, ' Log', size=(100, 50))
		self.hbox2.Add((10, -1))
		self.hbox2.Add(self.real_phase_log, 0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.sboxs2.Add(self.hbox2,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.vbox.Add(self.sboxs2,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.CheckLog(self.panelvisual.lut_phase_real, self.real_phase_log)
		self.vbox.Add((-1, 5))
		self.sbox3 = wx.StaticBox(self, label="Fourier Amplitude", style=wx.BORDER_DEFAULT)
		self.sboxs3 = wx.StaticBoxSizer(self.sbox3,wx.VERTICAL)
		self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		range = self.panelvisual.lut_amp_recip.GetTableRange()
		self.recip_amp_max = SpinnerObject(self,"Max: ",MAX_INT,MIN_INT,1,range[1],100,100)
		self.recip_amp_min = SpinnerObject(self,"Min: ",MAX_INT,MIN_INT,1,range[0],100,100)
		self.recip_amp_max.GetItem(self.recip_amp_max.value, recursive=False).SetFlag(wx.EXPAND)
		self.recip_amp_max.GetItem(self.recip_amp_max.value, recursive=False).SetProportion(1)
		self.recip_amp_min.GetItem(self.recip_amp_min.value, recursive=False).SetFlag(wx.EXPAND)
		self.recip_amp_min.GetItem(self.recip_amp_min.value, recursive=False).SetProportion(1)
		self.hbox3.Add(self.recip_amp_max,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.hbox3.Add(self.recip_amp_min,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.recip_amp_log = CheckBoxNew(self, -1, ' Log', size=(100, 50))
		self.hbox3.Add((10, -1))
		self.hbox3.Add(self.recip_amp_log, 0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.sboxs3.Add(self.hbox3,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.vbox.Add(self.sboxs3,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.CheckLog(self.panelvisual.lut_amp_recip, self.recip_amp_log)
		self.vbox.Add((-1, 5))
		self.sbox4 = wx.StaticBox(self, label="Fourier Phase", style=wx.BORDER_DEFAULT)
		self.sboxs4 = wx.StaticBoxSizer(self.sbox4,wx.VERTICAL)
		self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
		range = self.panelvisual.lut_phase_recip.GetTableRange()
		self.recip_phase_max = SpinnerObject(self,"Max: ",MAX_INT_16,MIN_INT_16,0.01,range[1],100,100)
		self.recip_phase_min = SpinnerObject(self,"Min: ",MAX_INT_16,MIN_INT_16,0.01,range[0],100,100)
		self.recip_phase_max.GetItem(self.recip_phase_max.value, recursive=False).SetFlag(wx.EXPAND)
		self.recip_phase_max.GetItem(self.recip_phase_max.value, recursive=False).SetProportion(1)
		self.recip_phase_min.GetItem(self.recip_phase_min.value, recursive=False).SetFlag(wx.EXPAND)
		self.recip_phase_min.GetItem(self.recip_phase_min.value, recursive=False).SetProportion(1)
		self.hbox4.Add(self.recip_phase_max,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.hbox4.Add(self.recip_phase_min,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.recip_phase_log = CheckBoxNew(self, -1, ' Log', size=(100, 50))
		self.hbox4.Add((10, -1))
		self.hbox4.Add(self.recip_phase_log, 0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.sboxs4.Add(self.hbox4,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.vbox.Add(self.sboxs4,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.CheckLog(self.panelvisual.lut_phase_recip, self.recip_phase_log)
		self.vbox.Add((-1, 5))
		self.real_amp_max.spin.SetEventFunc(self.OnRealAmpSpin)
		self.real_amp_max.value.Bind(wx.EVT_KEY_DOWN, self.OnRealAmpKey)
		self.real_amp_min.spin.SetEventFunc(self.OnRealAmpSpin)
		self.real_amp_min.value.Bind(wx.EVT_KEY_DOWN, self.OnRealAmpKey)
		self.real_phase_max.spin.SetEventFunc(self.OnRealPhaseSpin)
		self.real_phase_max.value.Bind(wx.EVT_KEY_DOWN, self.OnRealPhaseKey)
		self.real_phase_min.spin.SetEventFunc(self.OnRealPhaseSpin)
		self.real_phase_min.value.Bind(wx.EVT_KEY_DOWN, self.OnRealPhaseKey)
		self.recip_amp_max.spin.SetEventFunc(self.OnRecipAmpSpin)
		self.recip_amp_max.value.Bind(wx.EVT_KEY_DOWN, self.OnRecipAmpKey)
		self.recip_amp_min.spin.SetEventFunc(self.OnRecipAmpSpin)
		self.recip_amp_min.value.Bind(wx.EVT_KEY_DOWN, self.OnRecipAmpKey)
		self.recip_phase_max.spin.SetEventFunc(self.OnRecipPhaseSpin)
		self.recip_phase_max.value.Bind(wx.EVT_KEY_DOWN, self.OnRecipPhaseKey)
		self.recip_phase_min.spin.SetEventFunc(self.OnRecipPhaseSpin)
		self.recip_phase_min.value.Bind(wx.EVT_KEY_DOWN, self.OnRecipPhaseKey)
		self.Bind(wx.EVT_CHECKBOX, self.OnLogRealAmp, self.real_amp_log)
		self.Bind(wx.EVT_CHECKBOX, self.OnLogRealPhase, self.real_phase_log)
		self.Bind(wx.EVT_CHECKBOX, self.OnLogRecipAmp, self.recip_amp_log)
		self.Bind(wx.EVT_CHECKBOX, self.OnLogRecipPhase, self.recip_phase_log)
		self.SetAutoLayout(True)
		self.SetSizer( self.vbox )
		self.Fit()
		self.Layout()
		self.Show()
	def SetTableRange(self, lut, scalebar, mapper, objmax, objmin):
		min = float(objmin.value.GetValue())
		max = float(objmax.value.GetValue())
		lut.SetTableRange((min,max))
		lut.Modified()
		scalebar.Modified()
		mapper.SetScalarRange((min,max))
		mapper.Modified()
		self.panelvisual.RefreshScene()
	def OnRealAmpSpin(self,event):
		self.SetTableRange(self.panelvisual.lut_amp_real, self.panelvisual.scalebar_amp_real,\
										self.panelvisual.mapper_amp_real,\
										self.real_amp_max, self.real_amp_min)
		self.SetTableRange(self.panelvisual.lut_amp_real, self.panelvisual.scalebar_amp_real,\
										self.panelvisual.mapper_amp_real2,\
										self.real_amp_max, self.real_amp_min)
	def OnRealPhaseSpin(self,event):
		self.SetTableRange(self.panelvisual.lut_phase_real, self.panelvisual.scalebar_phase_real,\
										self.panelvisual.mapper_phase_real,\
										self.real_phase_max, self.real_phase_min)
	def OnRecipAmpSpin(self,event):
		self.SetTableRange(self.panelvisual.lut_amp_recip, self.panelvisual.scalebar_amp_recip,\
										self.panelvisual.mapper_amp_recip,\
										self.recip_amp_max, self.recip_amp_min)
	def OnRecipPhaseSpin(self,event):
		self.SetTableRange(self.panelvisual.lut_phase_recip, self.panelvisual.scalebar_phase_recip,\
										self.panelvisual.mapper_phase_recip,\
										self.recip_phase_max, self.recip_phase_min)
	def OnRealAmpKey(self,event):
		if event.GetKeyCode() == wx.WXK_RETURN:
			self.OnRealAmpSpin(None)
		else:
			event.Skip()
	def OnRealPhaseKey(self,event):
		if event.GetKeyCode() == wx.WXK_RETURN:
			self.OnRealPhaseSpin(None)
		else:
			event.Skip()
	def OnRecipAmpKey(self,event):
		if event.GetKeyCode() == wx.WXK_RETURN:
			self.OnRecipAmpSpin(None)
		else:
			event.Skip()
	def OnRecipPhaseKey(self,event):
		if event.GetKeyCode() == wx.WXK_RETURN:
			self.OnRecipPhaseSpin(None)
		else:
			event.Skip()
	def SetLogTable(self, lut, scalebar, mapper, objmax, objmin, log=False):
		min = float(objmin.value.GetValue())
		max = float(objmax.value.GetValue())
		if min > 0 and max > min and log:
			lut.SetScaleToLog10()
		else:
			lut.SetScaleToLinear()
		lut.Modified()
		scalebar.Modified()
		mapper.Modified()
		self.panelvisual.RefreshScene()
	def CheckLog(self, lut, chkbox):
		if lut.GetScale() == vtk.VTK_SCALE_LOG10:
			chkbox.SetValue(True)
	def OnLogRealAmp(self,event):
		if self.real_amp_log.GetValue() == True:
			self.SetLogTable(self.panelvisual.lut_amp_real, self.panelvisual.scalebar_amp_real,\
										self.panelvisual.mapper_amp_real,\
										self.real_amp_max, self.real_amp_min, log=True)
			self.SetLogTable(self.panelvisual.lut_amp_real, self.panelvisual.scalebar_amp_real,\
										self.panelvisual.mapper_amp_real2,\
										self.real_amp_max, self.real_amp_min, log=True)
		else:
			self.SetLogTable(self.panelvisual.lut_amp_real, self.panelvisual.scalebar_amp_real,\
										self.panelvisual.mapper_amp_real,\
										self.real_amp_max, self.real_amp_min)
			self.SetLogTable(self.panelvisual.lut_amp_real, self.panelvisual.scalebar_amp_real,\
										self.panelvisual.mapper_amp_real2,\
										self.real_amp_max, self.real_amp_min)
	def OnLogRealPhase(self,event):
		if self.real_phase_log.GetValue() == True:
			self.SetLogTable(self.panelvisual.lut_phase_real, self.panelvisual.scalebar_phase_real,\
										self.panelvisual.mapper_phase_real,\
										self.real_phase_max, self.real_phase_min, log=True)
		else:
			self.SetLogTable(self.panelvisual.lut_phase_real, self.panelvisual.scalebar_phase_real,\
										self.panelvisual.mapper_phase_real,\
										self.real_phase_max, self.real_phase_min)
	def OnLogRecipAmp(self,event):
		if self.recip_amp_log.GetValue() == True:
			self.SetLogTable(self.panelvisual.lut_amp_recip, self.panelvisual.scalebar_amp_recip,\
										self.panelvisual.mapper_amp_recip,\
										self.recip_amp_max, self.recip_amp_min, log=True)
		else:
			self.SetLogTable(self.panelvisual.lut_amp_recip, self.panelvisual.scalebar_amp_recip,\
										self.panelvisual.mapper_amp_recip,\
										self.recip_amp_max, self.recip_amp_min)
	def OnLogRecipPhase(self,event):
		if self.recip_phase_log.GetValue() == True:
			self.SetLogTable(self.panelvisual.lut_phase_recip, self.panelvisual.scalebar_phase_recip,\
										self.panelvisual.mapper_phase_recip,\
										self.recip_phase_max, self.recip_phase_min, log=True)
		else:
			self.SetLogTable(self.panelvisual.lut_phase_recip, self.panelvisual.scalebar_phase_recip,\
										self.panelvisual.mapper_phase_recip,\
										self.recip_phase_max, self.recip_phase_min)
class SBDialog(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, title="Scale Bar", size=(500,530), style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
		self.SetSizeHints(500,530,-1,-1)
		self.Bind(wx.EVT_CLOSE, self.OnExit)
		self.panelvisual = self.GetParent()
		self.vbox = wx.BoxSizer(wx.VERTICAL)
		self.sbox1 = wx.StaticBox(self, label="Label colour", style=wx.BORDER_DEFAULT)
		self.sboxs1 = wx.StaticBoxSizer(self.sbox1,wx.VERTICAL)
		self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox11 = wx.BoxSizer(wx.HORIZONTAL)
		labelcolours = self.panelvisual.scalebar_amp_real.GetLabelTextProperty().GetColor()
		self.labelr = SpinnerObject(self,"Red:",1.0,0.0,0.1,labelcolours[0],40,60)
		self.labelg = SpinnerObject(self,"Green:",1.0,0.0,0.1,labelcolours[1],40,60)
		self.labelb = SpinnerObject(self,"Blue:",1.0,0.0,0.1,labelcolours[2],40,60)
		self.labelr.spin.SetEventFunc(self.OnLabelRGB)
		self.labelg.spin.SetEventFunc(self.OnLabelRGB)
		self.labelb.spin.SetEventFunc(self.OnLabelRGB)
		self.labelr.value.Bind(wx.EVT_KEY_UP, self.OnLabelRGBKey)
		self.labelg.value.Bind(wx.EVT_KEY_UP, self.OnLabelRGBKey)
		self.labelb.value.Bind(wx.EVT_KEY_UP, self.OnLabelRGBKey)
		self.hbox1.Add(self.labelr, 1 , flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.hbox1.Add(self.labelg, 1 , flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.hbox1.Add(self.labelb, 1 , flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.labelfontsize = SpinnerObject(self,"Font size:",MAX_INT_16,1,1,self.panelvisual.scalebar_amp_real.GetLabelTextProperty().GetFontSize(),60,50)
		self.labelfontsize.spin.SetEventFunc(self.OnLabelFontSize)
		self.labelfontsizeauto = CheckBoxNew(self, -1, 'Auto')
		if IsNotVTK7():
			if self.panelvisual.scalebar_amp_real.GetAnnotationTextScaling == 0:
				self.labelfontsizeauto.SetValue(True)
				self.labelfontsize.Disable()
		else:
			if self.panelvisual.scalebar_amp_real.GetUnconstrainedFontSize() == False:
				self.labelfontsizeauto.SetValue(True)
				self.labelfontsize.Disable()
		self.Bind(wx.EVT_CHECKBOX, self.OnChkboxLabelFontSize, self.labelfontsizeauto)
		self.hbox11.Add(self.labelfontsize, 0 , flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.hbox11.Add(self.labelfontsizeauto, 0 , flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.label_shadow = CheckBoxNew(self, -1, 'Enable Label Shadows')
		if self.panelvisual.scalebar_amp_real.GetLabelTextProperty().GetShadow() != 0:
			self.label_shadow.SetValue(True)
		self.Bind(wx.EVT_CHECKBOX, self.OnChkboxLabelShadow, self.label_shadow)
		self.sboxs1.Add(self.hbox1,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.sboxs1.Add(self.hbox11,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=8)
		self.sboxs1.Add(self.label_shadow, 0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=8)
		self.vbox.Add(self.sboxs1,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.vbox.Add((-1, 5))
		self.hboxfmt = wx.BoxSizer(wx.HORIZONTAL)
		self.labeltitle = wx.StaticText(self, label="Label Format: ")
		self.labelformat = wx.TextCtrl(self, -1, style=wx.TE_PROCESS_ENTER)
		self.labelformat.SetValue(self.panelvisual.scalebar_amp_real.GetLabelFormat())
		self.labelformat.Bind(wx.EVT_TEXT_ENTER, self.OnLabelFormat)
		self.hboxfmt.Add(self.labeltitle,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.hboxfmt.Add(self.labelformat,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.vbox.Add(self.hboxfmt,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.vbox.Add((-1, 5))
		self.sbox2 = wx.StaticBox(self, label="Dimensions", style=wx.BORDER_DEFAULT)
		self.sboxs2 = wx.StaticBoxSizer(self.sbox2,wx.VERTICAL)
		self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		self.dimx = SpinnerObject(self,"Width:",1.0,0.0,0.01,self.panelvisual.scalebar_amp_real.GetWidth(),60,100)
		self.dimy = SpinnerObject(self,"Height:",1.0,0.0,0.01,self.panelvisual.scalebar_amp_real.GetHeight(),60,100)
		self.dimx.spin.SetEventFunc(self.OnDim)
		self.dimy.spin.SetEventFunc(self.OnDim)
		self.dimx.value.Bind(wx.EVT_KEY_UP, self.OnDimKey)
		self.dimy.value.Bind(wx.EVT_KEY_UP, self.OnDimKey)
		self.hbox2.Add(self.dimx, 1 , flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.hbox2.Add(self.dimy, 1 , flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.sboxs2.Add(self.hbox2,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.vbox.Add(self.sboxs2,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.sbox3 = wx.StaticBox(self, label="Position", style=wx.BORDER_DEFAULT)
		self.sboxs3 = wx.StaticBoxSizer(self.sbox3,wx.VERTICAL)
		self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		posxy = self.panelvisual.scalebar_amp_real.GetPosition()
		self.posx = SpinnerObject(self,"x:",1.0,0.0,0.01,posxy[0],60,100)
		self.posy = SpinnerObject(self,"y:",1.0,0.0,0.01,posxy[1],60,100)
		self.posx.spin.SetEventFunc(self.OnPos)
		self.posy.spin.SetEventFunc(self.OnPos)
		self.posx.value.Bind(wx.EVT_KEY_UP, self.OnPosKey)
		self.posy.value.Bind(wx.EVT_KEY_UP, self.OnPosKey)
		self.hbox3.Add(self.posx, 1 , flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.hbox3.Add(self.posy, 1 , flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.sboxs3.Add(self.hbox3,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.vbox.Add(self.sboxs3,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.vbox.Add((-1, 5))
		self.nlabels = SpinnerObject(self,"Number of labels:",MAX_INT_16,0,1,self.panelvisual.scalebar_amp_real.GetNumberOfLabels(),150,50)
		self.nlabels.spin.SetEventFunc(self.OnNLabels)
		self.nlabels.value.Bind(wx.EVT_KEY_UP, self.OnNLabelsKey)
		self.vbox.Add(self.nlabels,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.vbox.Add((-1, 5))
		self.tickframe = CheckBoxNew(self, -1, 'Enable Frame')
		if self.panelvisual.scalebar_amp_real.GetDrawFrame() != 0:
			self.tickframe.SetValue(True)
		self.Bind(wx.EVT_CHECKBOX, self.OnChkboxTickframe, self.tickframe)
		self.vbox.Add(self.tickframe,0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.vbox.Add((-1, 5))
		self.rborient = wx.RadioBox(self, label="Orientation", choices=['Vertical','Horizontal'],  majorDimension=2, style=wx.RA_SPECIFY_COLS)
		self.Bind(wx.EVT_RADIOBOX, self.OnRadioOrient, self.rborient)
		if self.panelvisual.scalebar_amp_real.GetOrientation() != 0:
			self.rborient.SetSelection(0)
		else:
			self.rborient.SetSelection(1)
		self.vbox.Add(self.rborient,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.vbox.Add((-1, 5))
		self.rbtextpos = wx.RadioBox(self, label="Text position", choices=['Succeed', 'Precede'],  majorDimension=2, style=wx.RA_SPECIFY_COLS)
		self.Bind(wx.EVT_RADIOBOX, self.OnRadioTextPos, self.rbtextpos)
		if self.panelvisual.scalebar_amp_real.GetTextPosition() != 0:
			self.rbtextpos.SetSelection(0)
		else:
			self.rbtextpos.SetSelection(1)
		self.vbox.Add(self.rbtextpos,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.vbox.Add((-1, 30))
		self.SetSizer(self.vbox)
		self.Fit()
		self.Show()
	def OnExit(self,event):
		del self.panelvisual.SBdialog
		self.Destroy()
	def OnLabelRGBKey(self, event):
		if event.GetKeyCode() != (wx.WXK_RETURN or wx.WXK_NUMPAD_ENTER):
			event.Skip()
		else:
			self.OnLabelRGB(event)
	def OnLabelRGB(self, event):
		r = float(self.labelr.value.GetValue())
		g = float(self.labelg.value.GetValue())
		b = float(self.labelb.value.GetValue())
		self.panelvisual.scalebar_amp_real.GetLabelTextProperty().SetColor(r,g,b)
		self.panelvisual.scalebar_phase_real.GetLabelTextProperty().SetColor(r,g,b)
		self.panelvisual.scalebar_amp_recip.GetLabelTextProperty().SetColor(r,g,b)
		self.panelvisual.scalebar_phase_recip.GetLabelTextProperty().SetColor(r,g,b)
		self.panelvisual.RefreshScene()
	def OnLabelFontSize(self, event):
		size = int(float(self.labelfontsize.value.GetValue()))
		self.panelvisual.scalebar_amp_real.GetLabelTextProperty().SetFontSize(size)
		self.panelvisual.scalebar_phase_real.GetLabelTextProperty().SetFontSize(size)
		self.panelvisual.scalebar_amp_recip.GetLabelTextProperty().SetFontSize(size)
		self.panelvisual.scalebar_phase_recip.GetLabelTextProperty().SetFontSize(size)
		self.panelvisual.RefreshScene()
	def OnChkboxLabelShadow(self, event):
		if self.label_shadow.GetValue() == True:
			self.panelvisual.scalebar_amp_real.GetLabelTextProperty().ShadowOn()
			self.panelvisual.scalebar_phase_real.GetLabelTextProperty().ShadowOn()
			self.panelvisual.scalebar_amp_recip.GetLabelTextProperty().ShadowOn()
			self.panelvisual.scalebar_phase_recip.GetLabelTextProperty().ShadowOn()
		else:
			self.panelvisual.scalebar_amp_real.GetLabelTextProperty().ShadowOff()
			self.panelvisual.scalebar_phase_real.GetLabelTextProperty().ShadowOff()
			self.panelvisual.scalebar_amp_recip.GetLabelTextProperty().ShadowOff()
			self.panelvisual.scalebar_phase_recip.GetLabelTextProperty().ShadowOff()
		self.panelvisual.RefreshScene()
	def OnLabelFormat(self, event):
		value = self.labelformat.GetValue()
		try:
			self.panelvisual.scalebar_amp_real.SetLabelFormat(value)
			self.panelvisual.scalebar_phase_real.SetLabelFormat(value)
			self.panelvisual.scalebar_amp_recip.SetLabelFormat(value)
			self.panelvisual.scalebar_phase_recip.SetLabelFormat(value)
		except:
			pass
		self.panelvisual.RefreshScene()
	def OnChkboxLabelFontSize(self, event):
		if self.labelfontsizeauto.GetValue() == True:
			if IsNotVTK7():
				pass
			else:
				self.panelvisual.scalebar_amp_real.UnconstrainedFontSizeOff()
				self.panelvisual.scalebar_phase_real.UnconstrainedFontSizeOff()
				self.panelvisual.scalebar_amp_recip.UnconstrainedFontSizeOff()
				self.panelvisual.scalebar_phase_recip.UnconstrainedFontSizeOff()
			self.labelfontsize.Disable()
		else:
			if IsNotVTK7():
				pass
			else:
				self.panelvisual.scalebar_amp_real.UnconstrainedFontSizeOn()
				self.panelvisual.scalebar_phase_real.UnconstrainedFontSizeOn()
				self.panelvisual.scalebar_amp_recip.UnconstrainedFontSizeOn()
				self.panelvisual.scalebar_phase_recip.UnconstrainedFontSizeOn()
			self.labelfontsize.Enable()
		self.panelvisual.RefreshScene()
	def OnDimKey(self, event):
		if event.GetKeyCode() != (wx.WXK_RETURN or wx.WXK_NUMPAD_ENTER):
			event.Skip()
		else:
			self.OnDim(event)
	def OnDim(self, event):
		x = float(self.dimx.value.GetValue())
		y = float(self.dimy.value.GetValue())
		self.panelvisual.scalebar_amp_real.SetWidth(x)
		self.panelvisual.scalebar_phase_real.SetWidth(x)
		self.panelvisual.scalebar_amp_recip.SetWidth(x)
		self.panelvisual.scalebar_phase_recip.SetWidth(x)
		self.panelvisual.scalebar_amp_real.SetHeight(y)
		self.panelvisual.scalebar_phase_real.SetHeight(y)
		self.panelvisual.scalebar_amp_recip.SetHeight(y)
		self.panelvisual.scalebar_phase_recip.SetHeight(y)
		self.panelvisual.RefreshScene()
	def OnPosKey(self, event):
		if event.GetKeyCode() != (wx.WXK_RETURN or wx.WXK_NUMPAD_ENTER):
			event.Skip()
		else:
			self.OnPos(event)
	def OnPos(self, event):
		x = float(self.posx.value.GetValue())
		y = float(self.posy.value.GetValue())
		self.panelvisual.scalebar_amp_real.SetPosition(x,y)
		self.panelvisual.scalebar_phase_real.SetPosition(x,y)
		self.panelvisual.scalebar_amp_recip.SetPosition(x,y)
		self.panelvisual.scalebar_phase_recip.SetPosition(x,y)
		self.panelvisual.RefreshScene()
	def OnNLabelsKey(self, event):
		if event.GetKeyCode() != (wx.WXK_RETURN or wx.WXK_NUMPAD_ENTER):
			event.Skip()
		else:
			self.OnNLabels(event)
	def OnNLabels(self, event):
		nlabels = int(float(self.nlabels.value.GetValue()))
		self.panelvisual.scalebar_amp_real.SetNumberOfLabels(nlabels)
		self.panelvisual.scalebar_phase_real.SetNumberOfLabels(nlabels)
		self.panelvisual.scalebar_amp_recip.SetNumberOfLabels(nlabels)
		self.panelvisual.scalebar_phase_recip.SetNumberOfLabels(nlabels)
		self.panelvisual.RefreshScene()
	def OnChkboxTickframe(self, event):
		if self.tickframe.GetValue() == True:
			self.panelvisual.scalebar_amp_real.DrawFrameOn()
			self.panelvisual.scalebar_phase_real.DrawFrameOn()
			self.panelvisual.scalebar_amp_recip.DrawFrameOn()
			self.panelvisual.scalebar_phase_recip.DrawFrameOn()
		else:
			self.panelvisual.scalebar_amp_real.DrawFrameOff()
			self.panelvisual.scalebar_phase_real.DrawFrameOff()
			self.panelvisual.scalebar_amp_recip.DrawFrameOff()
			self.panelvisual.scalebar_phase_recip.DrawFrameOff()
		self.panelvisual.RefreshScene()
	def OnRadioOrient(self, event):
		rselect = self.rborient.GetStringSelection()
		if rselect == 'Vertical':
			self.panelvisual.scalebar_amp_real.SetOrientationToVertical()
			self.panelvisual.scalebar_phase_real.SetOrientationToVertical()
			self.panelvisual.scalebar_amp_recip.SetOrientationToVertical()
			self.panelvisual.scalebar_phase_recip.SetOrientationToVertical()
		else:
			self.panelvisual.scalebar_amp_real.SetOrientationToHorizontal()
			self.panelvisual.scalebar_phase_real.SetOrientationToHorizontal()
			self.panelvisual.scalebar_amp_recip.SetOrientationToHorizontal()
			self.panelvisual.scalebar_phase_recip.SetOrientationToHorizontal()
		self.panelvisual.RefreshScene()
	def OnRadioTextPos(self, event):
		rselect = self.rbtextpos.GetStringSelection()
		if rselect == 'Precede':
			self.panelvisual.scalebar_amp_real.SetTextPositionToPrecedeScalarBar()
			self.panelvisual.scalebar_phase_real.SetTextPositionToPrecedeScalarBar()
			self.panelvisual.scalebar_amp_recip.SetTextPositionToPrecedeScalarBar()
			self.panelvisual.scalebar_phase_recip.SetTextPositionToPrecedeScalarBar()
		else:
			self.panelvisual.scalebar_amp_real.SetTextPositionToSucceedScalarBar()
			self.panelvisual.scalebar_phase_real.SetTextPositionToSucceedScalarBar()
			self.panelvisual.scalebar_amp_recip.SetTextPositionToSucceedScalarBar()
			self.panelvisual.scalebar_phase_recip.SetTextPositionToSucceedScalarBar()
		self.panelvisual.RefreshScene()
class LightDialog(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, title="Light Properties", size=(350,350), style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
		self.SetSizeHints(350,350,-1,-1)
		self.Bind(wx.EVT_CLOSE, self.OnExit)
		self.panelvisual = self.GetParent()
		self.vbox = wx.BoxSizer(wx.VERTICAL)
		self.ambient = SpinnerObject(self,"Ambient lighting coefficient: ",1.0,0.0,0.01,self.panelvisual.actor_amp_real.GetProperty().GetAmbient(),200,100)
		self.ambient.spin.SetEventFunc(self.OnAmbient)
		self.ambient.value.Bind(wx.EVT_KEY_UP, self.OnAmbientKey)
		self.vbox.Add(self.ambient,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=5)
		self.diffuse = SpinnerObject(self,"Diffuse lighting coefficient: ",1.0,0.0,0.01,self.panelvisual.actor_amp_real.GetProperty().GetDiffuse(),200,100)
		self.diffuse.spin.SetEventFunc(self.OnDiffuse)
		self.diffuse.value.Bind(wx.EVT_KEY_UP, self.OnDiffuseKey)
		self.vbox.Add(self.diffuse,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=5)
		self.specular = SpinnerObject(self,"Specular lighting coefficient: ",1.0,0.0,0.01,self.panelvisual.actor_amp_real.GetProperty().GetSpecular(),200,100)
		self.specular.spin.SetEventFunc(self.OnSpecular)
		self.specular.value.Bind(wx.EVT_KEY_UP, self.OnSpecularKey)
		self.vbox.Add(self.specular,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=5)
		self.specularpower = SpinnerObject(self,"Specular Power: ",128,0.0,1,self.panelvisual.actor_amp_real.GetProperty().GetSpecularPower(),200,100)
		self.specularpower.spin.SetEventFunc(self.OnSpecularpower)
		self.specularpower.value.Bind(wx.EVT_KEY_UP, self.OnSpecularpowerKey)
		self.vbox.Add(self.specularpower,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=5)
		self.vbox.Add((-1, 20))
		self.SetSizer(self.vbox)
		self.Fit()
		self.Show()
	def OnExit(self,event):
		del self.panelvisual.Lightdialog
		self.Destroy()
	def OnAmbientKey(self, event):
		if event.GetKeyCode() != (wx.WXK_RETURN or wx.WXK_NUMPAD_ENTER):
			event.Skip()
		else:
			self.OnAmbient(event)
	def OnAmbient(self, event):
		value = float(self.ambient.value.GetValue())
		self.panelvisual.actor_amp_real.GetProperty().SetAmbient(value)
		self.panelvisual.actor_phase_real.GetProperty().SetAmbient(value)
		self.panelvisual.actor_amp_recip.GetProperty().SetAmbient(value)
		self.panelvisual.actor_phase_recip.GetProperty().SetAmbient(value)
		self.panelvisual.RefreshScene()
	def OnDiffuseKey(self, event):
		if event.GetKeyCode() != (wx.WXK_RETURN or wx.WXK_NUMPAD_ENTER):
			event.Skip()
		else:
			self.OnDiffuse(event)
	def OnDiffuse(self, event):
		value = float(self.diffuse.value.GetValue())
		self.panelvisual.actor_amp_real.GetProperty().SetDiffuse(value)
		self.panelvisual.actor_phase_real.GetProperty().SetDiffuse(value)
		self.panelvisual.actor_amp_recip.GetProperty().SetDiffuse(value)
		self.panelvisual.actor_phase_recip.GetProperty().SetDiffuse(value)
		self.panelvisual.RefreshScene()
	def OnSpecularKey(self, event):
		if event.GetKeyCode() != (wx.WXK_RETURN or wx.WXK_NUMPAD_ENTER):
			event.Skip()
		else:
			self.OnSpecular(event)
	def OnSpecular(self, event):
		value = float(self.specular.value.GetValue())
		self.panelvisual.actor_amp_real.GetProperty().SetSpecular(value)
		self.panelvisual.actor_phase_real.GetProperty().SetSpecular(value)
		self.panelvisual.actor_amp_recip.GetProperty().SetSpecular(value)
		self.panelvisual.actor_phase_recip.GetProperty().SetSpecular(value)
		self.panelvisual.RefreshScene()
	def OnSpecularpowerKey(self, event):
		if event.GetKeyCode() != (wx.WXK_RETURN or wx.WXK_NUMPAD_ENTER):
			event.Skip()
		else:
			self.OnSpecularpower(event)
	def OnSpecularpower(self, event):
		value = float(self.specularpower.value.GetValue())
		self.panelvisual.actor_amp_real.GetProperty().SetSpecularPower(value)
		self.panelvisual.actor_phase_real.GetProperty().SetSpecularPower(value)
		self.panelvisual.actor_amp_recip.GetProperty().SetSpecularPower(value)
		self.panelvisual.actor_phase_recip.GetProperty().SetSpecularPower(value)
		self.panelvisual.RefreshScene()
class LUTDialog(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, title="Lookup Table", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
		self.SetSizeHints(800,480,-1,-1)
		self.parent = parent
		self.Bind(wx.EVT_CLOSE, self.OnExit)
		self.panelphase = parent.GetParent().GetPage(0)
		self.panelvisual = self.GetParent()
		self.actor_list3D = ["vtkOpenGLActor", "vtkActor", "vtkMesaActor"]
		self.actor_list2D = ["vtkOpenGLImageActor", "vtkImageActor"]
		self.LUTlist = [self.panelvisual.lut_amp_real, self.panelvisual.lut_phase_real, self.panelvisual.lut_amp_recip, self.panelvisual.lut_phase_recip]
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.hbox = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		self.vbox1 = wx.BoxSizer(wx.VERTICAL)
		self.vbox2 = wx.BoxSizer(wx.VERTICAL)
		self.font = self.panelvisual.font
		self.panels = []
		self.listtitles = ["Real Amp","Real Phase", "Fourier Amp","Fourier Phase"]
		self.list = wx.ListCtrl(self,wx.ID_ANY,style=wx.LC_REPORT|wx.LC_NO_HEADER|wx.LC_HRULES|wx.SUNKEN_BORDER, size=(200,-1))
		self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelectListItem)
		self.list.InsertColumn(0,'Settings', width = 200)
		self.list.SetFont(self.font)
		for i in range(len(self.listtitles)):
			if IsNotWX4():
				self.list.InsertStringItem(i,self.listtitles[i],i)
			else:
				self.list.InsertItem(i,self.listtitles[i],i)
			self.list.SetItemFont(i, self.font)
			self.panels.append(ColourDialog(self))
			self.panels[-1].Hide()
			self.panels[-1].Layout()
			self.GetRadioChoice(i)
			self.vbox2.Add(self.panels[-1], 1, wx.EXPAND)
		self.vbox1.Add(self.list, 1, wx.EXPAND)
		self.panel_hld = wx.StaticText(self, label='')
		self.vbox2.Add(self.panel_hld, 1, wx.EXPAND)
		self.hbox.Add(self.vbox1, 0, wx.EXPAND,2)
		self.hbox.Add(self.vbox2, 1, wx.EXPAND,2)
		self.sizer.Add(self.hbox, 1, wx.EXPAND,2)
		self.button_update = wx.Button(self, label="Update Scale", size=(300, 30))
		self.hbox2.Add((5, 5))
		self.hbox2.Add(self.button_update, 1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=10)
		self.hbox2.Add((5, 5))
		self.Bind(wx.EVT_BUTTON, self.OnClickUpdate,self.button_update)
		self.sizer.Add(self.hbox2, 0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=2)
		self.SetSizer(self.sizer)
		self.Fit()
		self.Layout()
		self.Show()
	def GetRadioChoice(self, idx):
		choice = self.panelphase.cmls[idx][0]
		reverse = self.panelphase.cmls[idx][1]
		self.panels[idx].rb[choice].SetValue(True)
		if reverse == 0:
			self.panels[idx].chkb[choice].SetValue(False)
		else:
			self.panels[idx].chkb[choice].SetValue(True)
	def SetRadioChoice(self, idx):
		for i in range(len(self.panels[idx].rb)):
			if self.panels[idx].rb[i].GetValue() == True:
				self.panelphase.cmls[idx] = i
				reverse = self.panels[idx].chkb[i].GetValue()
				if reverse == True:
					self.panelphase.cmls[idx][1] = 1
				else:
					self.panelphase.cmls[idx][1] = 0
	def OnSelectListItem(self, event):
		if IsNotWX4():
			self.CurrentListItem = event.m_itemIndex
		else:
			self.CurrentListItem = event.GetIndex()
		self.panel_hld.Hide()
		for  i in range(len(self.panels)):
			if i == self.CurrentListItem:
				self.panels[i].Show();
			else:
				self.panels[i].Hide()
		self.Layout()
	def OnClickUpdate(self, event):
		for i in range(len(self.listtitles)):
			self.SetRadioChoice( i )
		for i in range(len(self.LUTlist)):
			lut = self.LUTlist[i]
			lutsource = self.panelphase.cms[self.panelphase.cmls[i][0]][1]
			if self.panelphase.cmls[i][1] == 0:
				for k in range(256):
					lut.SetTableValue(k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
			else:
				for k in range(256):
					lut.SetTableValue(255-k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
			lut.Modified()
		self.panelphase.ancestor.GetParent().Refresh()
		self.panelvisual.RefreshScene()
	def OnExit(self,event):
		for i in range(len(self.listtitles)):
			self.SetRadioChoice( i )
		self.panelphase.ancestor.GetParent().Refresh()
		self.Hide()
class ColourDialog(wx.ScrolledWindow):
	def __init__(self, parent):
		self.panel = wx.ScrolledWindow.__init__(self, parent)
		self.SetScrollRate(5, 5)
		self.panelphase = self.GetParent().panelphase
		self.panelvisual = self.GetParent().panelvisual
		self.cmvbox = wx.BoxSizer(wx.VERTICAL)
		self.cmhbox = []
		self.imglist = []
		self.sellist = []
		self.rb = []
		self.chkb = []
		array = self.panelphase.cms[0][1]
		dc = wx.ScreenDC()
		dc.SetFont(self.panelvisual.font)
		w,h = dc.GetTextExtent("TestString")
		height = h
		if IsNotWX4():
			image = wx.EmptyImage(array.shape[0],height)
		else:
			image = wx.Image(array.shape[0],height)
		newarray = numpy.zeros((height, array.shape[0], 3), dtype=numpy.uint8)
		for i in range(self.panelphase.cms.shape[0]):
			self.cmhbox.append( wx.BoxSizer(wx.HORIZONTAL) )
			name = self.panelphase.cms[i][0]
			array = self.panelphase.cms[i][1]
			for j in range(height):
				newarray[j,:,:] = numpy.uint8(255.0*array)
			image.SetData( newarray.tostring())
			bmp = image.ConvertToBitmap()
			self.imglist.append(wx.StaticBitmap(self, -1, bmp))
			self.rb.append( wx.RadioButton(self, -1, label=name, size=(150, height) ) )
			self.cmhbox[-1].Add(self.rb[-1], 0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
			self.cmhbox[-1].Add((5, -1))
			self.cmhbox[-1].Add(self.imglist[-1], 1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
			self.chkb.append( wx.CheckBox(self, -1, 'Reverse', size=(120, height)) )
			self.cmhbox[-1].Add(self.chkb[-1], 0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
			self.cmvbox.Add(self.cmhbox[-1], 1, wx.EXPAND)
		self.SetSizer(self.cmvbox)
		self.Fit()
		self.Layout()
		self.Show()
class PanelVisual(wx.Panel,wx.App):
	def __init__(self,parent):
		self.ancestor = parent
		def ParseStart(event):
			self.ancestor.GetPage(0).OnClickStart(self.ancestor.GetPage(0))
		def ParsePause(event):
			self.ancestor.GetPage(0).OnClickPause(self.ancestor.GetPage(0))
		def ParseStop(event):
			self.ancestor.GetPage(0).OnClickStop(self.ancestor.GetPage(0))
		self.panel = wx.Panel.__init__(self, parent)
		self.VTKIsNot6 = IsNotVTK6()
		self.VTKIsNot7 = IsNotVTK7()
		self.nblock_dialogs = 0
		self.font = self.ancestor.GetParent().font
		self.flat_data = None
		self.flat_data2 = None
		self.flat_data_phase = None
		self.vtk_data_array = None
		self.vtk_data_array2 = None
		self.vtk_data_array_phase = None
		self.vtk_coordarray = None
		self.vtk_points = None
		self.data = None
		self.data_max = 0.0
		self.data_max_recip = 0.0
		self.data_max_support = 1.0
		self.FXAA = False
		self.coords = None
		self.inputdata = None
		self.image_probe = None
		self.image = vtk.vtkImageData()
		self.object_amp = vtk.vtkStructuredGrid()
		self.object_phase = vtk.vtkStructuredGrid()
		self.object_amp_points = vtk.vtkPoints()
		self.image_amp_real = vtk.vtkImageData()
		self.image_phase_real = vtk.vtkImageData()
		self.image_amp_recip = vtk.vtkImageData()
		self.image_phase_recip = vtk.vtkImageData()
		self.image_support = vtk.vtkImageData()
		self.image_amp_real_vtk = None
		self.image_phase_real_vtk = None
		self.measure_data = [None, [None, None], None, [None,None,None]]
		self.line = vtk.vtkLineSource()
		self.lineprobe = vtk.vtkProbeFilter()
		self.LineScan = LineScan(self.line, self.lineprobe)
		self.image2D_amp_real = vtk.vtkImageData()
		self.image2D_phase_real = vtk.vtkImageData()
		self.image2D_amp_real_vtk = None
		self.image2D_phase_real_vtk = None
		self.lut_amp_real = vtk.vtkLookupTable()
		self.lut_phase_real = vtk.vtkLookupTable()
		self.scalebar_amp_real=vtk.vtkScalarBarActor()
		self.scalebar_phase_real=vtk.vtkScalarBarActor()
		self.lut_amp_recip = vtk.vtkLookupTable()
		self.lut_phase_recip = vtk.vtkLookupTable()
		self.scalebar_amp_recip=vtk.vtkScalarBarActor()
		self.scalebar_phase_recip=vtk.vtkScalarBarActor()
		self.scalebar_amp_real.SetWidth(0.07)
		self.scalebar_amp_real.SetHeight(0.8)
		self.scalebar_amp_real.SetPosition(0.01,0.1)
		self.scalebar_amp_recip.SetWidth(0.07)
		self.scalebar_amp_recip.SetHeight(0.8)
		self.scalebar_amp_recip.SetPosition(0.01,0.1)
		self.scalebar_phase_real.SetWidth(0.07)
		self.scalebar_phase_real.SetHeight(0.80)
		self.scalebar_phase_real.SetPosition(0.01,0.1)
		self.scalebar_phase_recip.SetWidth(0.07)
		self.scalebar_phase_recip.SetHeight(0.80)
		self.scalebar_phase_recip.SetPosition(0.01,0.1)
		self.color_amp_real = vtk.vtkImageMapToColors()
		self.color_phase_real = vtk.vtkImageMapToColors()
		self.color_amp_recip = vtk.vtkImageMapToColors()
		self.color_phase_recip = vtk.vtkImageMapToColors()
		self.mapper2D_amp_real = vtk.vtkImageMapper()
		self.mapper2D_phase_real = vtk.vtkImageMapper()
		self.mapper2D_amp_recip = vtk.vtkImageMapper()
		self.mapper2D_phase_recip = vtk.vtkImageMapper()
		self.style2D = vtk.vtkInteractorStyleImage()
		self.filter_amp_real = vtk.vtkContourFilter()
		self.filter_amp_recip = vtk.vtkContourFilter()
		self.filter_support = vtk.vtkContourFilter()
		self.filter_amp_real.AddObserver(vtk.vtkCommand.ErrorEvent, self.SmoothFilterObserver)
		self.filter_amp_recip.AddObserver(vtk.vtkCommand.ErrorEvent, self.SmoothFilterObserver)
		self.filter_support.AddObserver(vtk.vtkCommand.ErrorEvent, self.SmoothFilterObserver)
		self.filter_march_amp_real = vtk.vtkImageMarchingCubes()
		self.smooth_filter_real = vtk.vtkSmoothPolyDataFilter()
		self.smooth_filter_recip = vtk.vtkSmoothPolyDataFilter()
		self.smooth_filter_support = vtk.vtkSmoothPolyDataFilter()
		self.smooth_filter_real.AddObserver(vtk.vtkCommand.ErrorEvent, self.SmoothFilterObserver)
		self.smooth_filter_recip.AddObserver(vtk.vtkCommand.ErrorEvent, self.SmoothFilterObserver)
		self.smooth_filter_support.AddObserver(vtk.vtkCommand.ErrorEvent, self.SmoothFilterObserver)
		self.normals_amp_real = vtk.vtkPolyDataNormals()
		self.normals_phase_real = vtk.vtkPolyDataNormals()
		self.normals_amp_recip = vtk.vtkPolyDataNormals()
		self.normals_phase_recip = vtk.vtkPolyDataNormals()
		self.normals_support = vtk.vtkPolyDataNormals()
		self.normals_plane = vtk.vtkPolyDataNormals()
		self.triangles_amp_real = vtk.vtkTriangleFilter()
		self.triangles_phase_real = vtk.vtkTriangleFilter()
		self.triangles_amp_recip = vtk.vtkTriangleFilter()
		self.triangles_phase_recip = vtk.vtkTriangleFilter()
		self.triangles_support = vtk.vtkTriangleFilter()
		self.strips_amp_real = vtk.vtkStripper()
		self.strips_amp_recip = vtk.vtkStripper()
		self.strips_phase_real = vtk.vtkStripper()
		self.strips_phase_recip = vtk.vtkStripper()
		self.strips_support = vtk.vtkStripper()
		self.plane = vtk.vtkPlane()
		self.planes = vtk.vtkPlaneCollection()
		self.cutter = vtk.vtkCutter()
		self.clipper = vtk.vtkClipPolyData()
		self.triangles_plane = vtk.vtkTriangleFilter()
		if not self.VTKIsNot7:
			self.meshsub = vtk.vtkAdaptiveSubdivisionFilter()
		self.probefilter = vtk.vtkProbeFilter()
		self.filter_plane = vtk.vtkContourFilter()
		self.smooth_plane = vtk.vtkSmoothPolyDataFilter()
		self.filter_tri = vtk.vtkContourTriangulator()
		self.mapper_amp_real = vtk.vtkPolyDataMapper()
		self.mapper_amp_real2 = vtk.vtkPolyDataMapper()
		self.mapper_phase_real = vtk.vtkPolyDataMapper()
		self.mapper_amp_recip = vtk.vtkPolyDataMapper()
		self.mapper_phase_recip = vtk.vtkPolyDataMapper()
		self.mapper_support = vtk.vtkPolyDataMapper()
		self.textMapper_amp_real = vtk.vtkTextMapper()
		self.actor_amp_real = vtk.vtkActor()
		self.actor_amp_real2 = vtk.vtkActor()
		self.actor_phase_real = vtk.vtkActor()
		self.actor_amp_recip = vtk.vtkActor()
		self.actor_phase_recip = vtk.vtkActor()
		self.actor_support = vtk.vtkActor()
		self.actor2D_amp_real = vtk.vtkImageActor()
		self.actor2D_phase_real = vtk.vtkImageActor()
		self.actor2D_amp_recip = vtk.vtkImageActor()
		self.actor2D_phase_recip = vtk.vtkImageActor()
		self.actor2D_support = vtk.vtkImageActor()
		self.textActor = vtk.vtkActor2D()
		self.picker_amp_real = vtk.vtkCellPicker()
		self.picker_observer = None
		self.style = None
		self.style3D = vtk.vtkInteractorStyleSwitch()
		self.style3D.SetCurrentStyleToTrackballCamera()
		self.renderers = None
		self.renderer_amp_real_docked = vtk.vtkRenderer()
		self.renderer_phase_real_docked = vtk.vtkRenderer()
		self.renderer_amp_recip_docked = vtk.vtkRenderer()
		self.renderer_phase_recip_docked = vtk.vtkRenderer()
		self.renderer_amp_real = self.renderer_amp_real_docked
		self.renderer_phase_real = self.renderer_phase_real_docked
		self.renderer_amp_recip = self.renderer_amp_recip_docked
		self.renderer_phase_recip = self.renderer_phase_recip_docked
		self.renderer_amp_real.SetBackground(0.0, 0.0, 0.0)
		self.renderer_phase_real.SetBackground(0.0, 0.0, 0.0)
		self.renderer_amp_recip.SetBackground(0.0, 0.0, 0.0)
		self.renderer_phase_recip.SetBackground(0.0, 0.0, 0.0)
		self.picker = None
		self.cube = vtk.vtkCubeSource()
		self.cube.SetXLength(1)
		self.cube.SetYLength(1)
		self.cube.SetZLength(1)
		self.cube.SetCenter(0.0,0.0,0.0)
		self.cubemapper = vtk.vtkPolyDataMapper()
		self.cubemapper.SetInputConnection(self.cube.GetOutputPort())
		self.cubeactor = vtk.vtkActor()
		self.cubeactor.PickableOff()
		self.cubeactor.SetMapper(self.cubemapper)
		self.cubeactor.GetProperty().SetColor(0,1.0,0.75)
		self.cubeactor.GetProperty().SetOpacity(0.2)
		self.cubecircle = vtk.vtkRegularPolygonSource()
		self.cubecircle.GeneratePolygonOff()
		self.cubecircle.SetNumberOfSides(64)
		self.cubecircle.SetRadius(9)
		self.cubecircle.SetCenter(0.0,0.0,0.0)
		self.cubecirclemapper = vtk.vtkPolyDataMapper()
		self.cubecirclemapper.SetInputConnection(self.cubecircle.GetOutputPort())
		self.cubecircleactor = vtk.vtkActor()
		self.cubecircleactor.PickableOff()
		self.cubecircleactor.SetMapper(self.cubecirclemapper)
		self.cubecircleactor.GetProperty().SetColor(0,1,0.5)
		self.cubecircleactor.GetProperty().SetOpacity(1.0)
		self.xyza_kxyz = Queue()
		self.axis = vtk.vtkCubeAxesActor2D()
		self.axis2D = vtk.vtkCubeAxesActor2D()
		self.axis2D_phase = vtk.vtkCubeAxesActor2D()
		self.axes = vtk.vtkAxesActor()
		self.axestext = vtk.vtkTextProperty()
		self.axestext.SetColor(1.0, 1.0, 1.0)
		self.axestext.SetFontSize(12)
		self.axestext.ShadowOn()
		self.axes.GetXAxisCaptionActor2D().SetCaptionTextProperty(self.axestext)
		self.axes.GetYAxisCaptionActor2D().SetCaptionTextProperty(self.axestext)
		self.axes.GetZAxisCaptionActor2D().SetCaptionTextProperty(self.axestext)
		self.axestransform = vtk.vtkTransform()
		self.axestransformRX = 0.0
		self.axestransformRY = 0.0
		self.axestransformRZ = 0.0
		self.axes.SetUserTransform(self.axestransform)
		self.widget = vtk.vtkOrientationMarkerWidget()
		self.vbox = wx.BoxSizer(wx.VERTICAL)
		self.hboxrender = wx.BoxSizer(wx.HORIZONTAL)
		self.vtkpanel_holder = wx.StaticText(self, label=' ')
		self.vtkpanel_holder.Hide()
		self.vtkpanel = wx.Panel(self, wx.ID_ANY)
		self.vtkpanelId = self.vtkpanel.GetId()
		self.renWinMain = wxVTKRenderWindowInteractor(self.vtkpanel, wx.ID_ANY)
		self.renWinMain.Enable(1)
		self.renWin = self.renWinMain
		self.RefreshSceneCMD = self.renWin.Render
		self.linewidget = None
		self.anglewidget = None
		self.vtkvbox = wx.BoxSizer(wx.VERTICAL)
		self.vtkvbox.Add(self.renWinMain, 1, wx.EXPAND)
		self.vtkpanel.SetSizer(self.vtkvbox)
		self.vtkpanel.Fit()
		self.vtkpanel.Layout()
		self.vtkpanel.Show()
		self.hboxrender.Add(self.vtkpanel_holder, 1, wx.EXPAND)
		self.hboxrender.Add(self.vtkpanel, 1, wx.EXPAND)
		self.vbox.Add(self.hboxrender,1 ,wx.EXPAND)
		self.hbox_btn = wx.BoxSizer(wx.HORIZONTAL)
		buttonx = OptIconSize()
		buttonsize = (buttonx,buttonx)
		self.button_start = BitmapButtonNew(self, -1, getstartBitmap(), size=buttonsize)
		self.button_start.SetToolTipNew('Start pipline execution')
		self.hbox_btn.Add(self.button_start, flag=wx.LEFT, border=10)
		self.Bind(wx.EVT_BUTTON, ParseStart, self.button_start)
		self.hbox_btn.Add((2, -1))
		self.button_pause = BitmapButtonNew(self, -1, getpauseBitmap(), size=buttonsize)
		self.button_pause.SetToolTipNew('Pause pipline execution')
		self.hbox_btn.Add(self.button_pause)
		self.Bind(wx.EVT_BUTTON, ParsePause, self.button_pause)
		self.hbox_btn.Add((2, -1))
		self.button_stop = BitmapButtonNew(self, -1, getstopBitmap(), size=buttonsize)
		self.button_stop.SetToolTipNew('Stop pipline execution')
		self.hbox_btn.Add(self.button_stop)
		self.Bind(wx.EVT_BUTTON, ParseStop, self.button_stop)
		self.hbox_btn.Add((2, -1))
		self.button_save = BitmapButtonNew(self, -1, wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE), size=buttonsize)
		self.button_save.SetToolTipNew('Save scene')
		self.hbox_btn.Add(self.button_save)
		self.Bind(wx.EVT_BUTTON, self.SaveScene, self.button_save)
		self.hbox_btn.Add((2, -1))
		self.button_animate = BitmapButtonNew(self, -1, getanimateBitmap(), size=buttonsize)
		self.button_animate.SetToolTipNew('Animate scene')
		self.hbox_btn.Add(self.button_animate)
		self.Bind(wx.EVT_BUTTON, self.AnimateScene, self.button_animate)
		self.button_animate.Enable(False)
		self.hbox_btn.Add((2, -1))
		self.button_measure = BitmapButtonNew(self, -1, getrulerBitmap(), size=buttonsize)
		self.button_measure.SetToolTipNew('Measure scene')
		self.hbox_btn.Add(self.button_measure)
		self.Bind(wx.EVT_BUTTON, self.MeasureScene, self.button_measure)
		self.button_measure.Enable(False)
		self.hbox_btn.Add((2, -1))
		self.button_vremove = BitmapButtonNew(self, -1, getvcutBitmap(), size=buttonsize)
		self.button_vremove.SetToolTipNew('Voxel Remove')
		self.button_vremove.Hide()
		self.hbox_btn.Add(self.button_vremove)
		self.button_vremove.Enable(False)
		self.hbox_btn.Add((2, -1))
		self.button_rgb = BitmapButtonNew(self, -1, getcolorpickBitmap(), size=buttonsize)
		self.button_rgb.SetToolTipNew('Scene background colour')
		self.Bind(wx.EVT_BUTTON, self.OnColourSelect, self.button_rgb)
		self.hbox_btn.Add(self.button_rgb)
		self.button_spectrum = BitmapButtonNew(self, -1, getspectrumBitmap(), size=buttonsize)
		self.button_spectrum.SetToolTipNew('Lookup table')
		self.Bind(wx.EVT_BUTTON, self.OnLUTSelect, self.button_spectrum)
		self.hbox_btn.Add(self.button_spectrum)
		self.button_scalerange = BitmapButtonNew(self, -1, getsliderBitmap(), size=buttonsize)
		self.button_scalerange.SetToolTipNew('Lookup table data range')
		self.button_scalerange.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.DataRange, self.button_scalerange)
		self.hbox_btn.Add(self.button_scalerange)
		self.button_contour = BitmapButtonNew(self, -1, getsphereBitmap(), size=buttonsize)
		self.button_contour.SetToolTipNew('Isosurfaces for 3D phasing')
		self.button_contours_shown = 0
		self.Bind(wx.EVT_BUTTON, self.OnContourSelect, self.button_contour)
		self.hbox_btn.Add(self.button_contour)
		self.hbox_btn.Add((2, -1))
		self.datarangelist = []
		self.r = 255.0
		self.g = 255.0
		self.b = 255.0
		self.vbox.Add(self.hbox_btn, 0, wx.EXPAND)
		self.SetSizer(self.vbox)
		self.Fit()
		self.Layout()
		self.Show()
		self.InitRender()
		self.ancestor.GetParent().Refresh()
	def EnablePanelPhase(self, enable=True):
		if enable==True:
			self.nblock_dialogs -= 1
			if self.nblock_dialogs <= 0:
				self.ancestor.GetPage(0).EnablePanel(enable=True)
				self.button_start.Enable(True)
				self.button_pause.Enable(True)
				self.button_stop.Enable(True)
				self.ancestor.GetPage(0).button_start.Enable(True)
				self.ancestor.GetPage(0).button_pause.Enable(True)
				self.ancestor.GetPage(0).button_stop.Enable(True)
				self.ancestor.GetPage(0).Refresh()
				self.nblock_dialogs = 0
		elif enable==False:
			self.ancestor.GetPage(0).EnablePanel(enable=False)
			self.button_start.Enable(False)
			self.button_pause.Enable(False)
			self.button_stop.Enable(False)
			self.ancestor.GetPage(0).button_start.Enable(False)
			self.ancestor.GetPage(0).button_pause.Enable(False)
			self.ancestor.GetPage(0).button_stop.Enable(False)
			self.ancestor.GetPage(0).Refresh()
			self.nblock_dialogs += 1
	def RefreshSceneFull(self, gotovisual=False):
		if self.ancestor.GetParent().visualdialog_docked == True:
			self.ancestor.GetParent().Refresh()
			if gotovisual:
				self.ancestor.SetSelection(1)
		else:
			self.ancestor.GetParent().visualdialog.Refresh()
	def RefreshScene(self, gotovisual=False):
		self.RefreshSceneCMD()
		if gotovisual:
			self.ancestor.SetSelection(1)
	def FXAAScene(self, enable=True):
		if enable:
			if hasattr(self.renderer_amp_real, 'UseFXAAOn'):
				self.renderer_amp_real.UseFXAAOn()
				self.renderer_phase_real.UseFXAAOn()
				self.renderer_amp_recip.UseFXAAOn()
				self.renderer_phase_recip.UseFXAAOn()
				self.FXAA = True
		else:
			if hasattr(self.renderer_amp_real, 'UseFXAAOff'):
				self.renderer_amp_real.UseFXAAOff()
				self.renderer_phase_real.UseFXAAOff()
				self.renderer_amp_recip.UseFXAAOff()
				self.renderer_phase_recip.UseFXAAOff()
				self.FXAA = False
	def ReleaseVisualButtons(self, gotovisual=False):
		self.button_scalerange.Enable(True)
		self.button_measure.Enable(True)
		self.button_vremove.Enable(True)
		try:
			panelvisual.meauredialog
		except:
			pass
		else:
			panelvisual.meauredialog.Update()
		self.button_animate.Enable(True)
		self.ancestor.GetParent().viewmenuundock.Enable(1)
		self.ancestor.GetParent().viewmenudock.Enable(1)
		self.ancestor.GetParent().scenemenu_animate.Enable(1)
		self.ancestor.GetParent().scenemenu_measure.Enable(1)
		self.ancestor.GetParent().scenemenu_lut_range.Enable(1)
		self.RefreshSceneFull(gotovisual)
	def SetPhaseVisualButtons(self):
		self.button_animate.Enable(True)
		self.button_measure.Enable(False)
		self.button_scalerange.Enable(False)
		self.button_vremove.Enable(False)
		self.ancestor.GetParent().scenemenu_animate.Enable(0)
		self.ancestor.GetParent().scenemenu_measure.Enable(0)
		self.ancestor.GetParent().scenemenu_lut_range.Enable(0)
		self.ancestor.GetParent().viewmenuundock.Enable(1)
		self.ancestor.GetParent().viewmenudock.Enable(1)
	def PickCoords(self, object, event):
		if self.picker_amp_real.GetCellId() < 0:
			self.textActor.VisibilityOff()
		else:
			selectedpoint = self.picker_amp_real.GetSelectionPoint()
			selectedposition = self.picker_amp_real.GetPickPosition()
			self.textMapper_amp_real.SetInput("(%.6f, %.6f, %.6f)"%selectedposition)
			self.textMapper_amp_real.Modified()
			self.textActor.SetPosition(selectedpoint[:2])
			self.textActor.VisibilityOn()
			self.textActor.Modified()
			self.RefreshScene()
			self.ancestor.GetPage(0).queue_info.put("Picked point: (%.6f, %.6f, %.6f)"%selectedposition)
			self.ancestor.GetPage(4).UpdateLog(self,)
	def SetPicker(self):
		textprop = self.textMapper_amp_real.GetTextProperty()
		textprop.SetFontFamilyToArial()
		textprop.SetFontSize(12)
		textprop.BoldOn()
		textprop.ShadowOn()
		textprop.SetColor(0, 0, 0)
		self.textActor.VisibilityOff()
		self.textActor.SetMapper(self.textMapper_amp_real)
		if not self.picker_amp_real.HasObserver("EndPickEvent"):
			self.picker_amp_real.AddObserver("EndPickEvent", self.PickCoords)
	def InitRender(self):
		self.renderer_amp_real.SetBackground(1.0, 1.0, 1.0)
		self.renWin.GetRenderWindow().AddRenderer(self.renderer_amp_real)
		self.renWin.SetInteractorStyle(self.style3D)
		self.renderer_amp_real.ResetCamera()
		self.renderer_amp_real.SetViewport(0,0,1,1)
		self.renderer_amp_recip.SetViewport(1,1,1,1)
		self.Layout()
		self.Show()
	def SaveScene(self,event):
		w2if = vtk.vtkWindowToImageFilter()
		w2if.SetInput(self.renWin.GetRenderWindow())
		w2if.Update()
		writer = vtk.vtkPNGWriter()
		datestr = strftime("%Y-%m-%d_%H.%M.%S")
		writer.SetFileName("image_"+datestr+".png")
		if self.VTKIsNot6:
			writer.SetInput(w2if.GetOutput())
		else:
			writer.SetInputData(w2if.GetOutput())
		writer.Write()
	def SaveSceneAs(self,event):
		filetypes = "PNG files (*.png)|*.png|JPEG files (*.jpg)|*.jpg|TIFF files (*.tif)|*.tif"
		filetypeext = [".png",".jpg",".tif"]
		cwd = self.ancestor.GetParent().CurrentWD()
		if IsNotWX4():
			dlg = wx.FileDialog(self, "Choose a file", cwd, "", filetypes, wx.SAVE | wx.OVERWRITE_PROMPT)
		else:
			dlg = wx.FileDialog(self, "Choose a file", cwd, "", filetypes, wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
		if dlg.ShowModal() == wx.ID_OK:
			filename=dlg.GetFilename()
			dirname=dlg.GetDirectory()
			file_ext = os.path.splitext(filename)[1]
			if file_ext not in filetypeext:
				file_ext = ".png"
				filename = filename + file_ext
			w2if = vtk.vtkWindowToImageFilter()
			w2if.SetInput(self.renWin.GetRenderWindow())
			w2if.Update()
			if file_ext == ".png":
				writer = vtk.vtkPNGWriter()
			elif file_ext == ".jpg":
				writer = vtk.vtkJPEGWriter()
			elif file_ext == ".tif":
				writer = vtk.vtkTIFFWriter()
			else:
				writer = vtk.vtkPNGWriter()
			filenamepath = os.path.join(dirname, filename)
			writer.SetFileName(filenamepath)
			if self.VTKIsNot6:
				writer.SetInput(w2if.GetOutput())
			else:
				writer.SetInputData(w2if.GetOutput())
			writer.Write()
		dlg.Destroy()
	def AnimateScene(self,event):
		dialog = AnimateDialog(self)
		dialog.ShowModal()
		dialog.Destroy()
	def MeasureScene(self,event):
		try:
			self.meauredialog
		except AttributeError:
			self.EnablePanelPhase(enable=False)
			self.meauredialog = MeasureDialog(self)
			self.meauredialog.Show()
	def SmoothFilterObserver(self, obj, event):
		pass
	def OnColourSelect(self, event):
		cdata = wx.ColourData()
		cdata.SetColour((self.r,self.g,self.b))
		dlg = wx.ColourDialog(self, data=cdata)
		dlg.GetColourData().SetChooseFull(True)
		if dlg.ShowModal() == wx.ID_OK:
			self.r,self.g,self.b = dlg.GetColourData().GetColour().Get(includeAlpha=False)
			self.SetBackground()
			self.RefreshScene()
		dlg.Destroy()
	def SetBackground(self):
		r = float(self.r)/255.0
		g = float(self.g)/255.0
		b = float(self.b)/255.0
		renderers = self.renWin.GetRenderWindow().GetRenderers()
		renderers.InitTraversal()
		no_renderers = renderers.GetNumberOfItems()
		for i in range(no_renderers):
			renderers.GetItemAsObject(i).SetBackground(r, g, b)
	def OnContourSelect(self, event):
		try:
			self.contourdialog
		except AttributeError:
			if self.ancestor.GetPage(0).pipeline_started == False:
				self.EnablePanelPhase(enable=False)
			self.contourdialog = ContourDialog(self)
			self.contourdialog.Show()
	def OnLUTSelect(self, event):
		try:
			self.LUTdialog
		except AttributeError:
			self.LUTdialog = LUTDialog(self)
		else:
			self.LUTdialog.Show()
	def OnScalebarSelect(self, event):
		try:
			self.SBdialog
		except AttributeError:
			self.SBdialog = SBDialog(self)
			self.SBdialog.Show()
	def OnLightSelect(self, event):
		try:
			self.Lightdialog
		except AttributeError:
			self.Lightdialog = LightDialog(self)
			self.Lightdialog.Show()
	def DataRange(self, event):
		dialog = DataRangeDialog(self)
		dialog.ShowModal()
		dialog.Destroy()
	def UpdateReal(self):
		if self.ancestor.GetPage(0).visual_amp_real.shape[2] == 1:
			try:
				self.flat_data_amp_real = (self.ancestor.GetPage(0).visual_amp_real).transpose(2,1,0).ravel();
				self.vtk_data_array_amp_real = numpy_support.numpy_to_vtk(self.flat_data_amp_real)
				self.image_amp_real.GetPointData().SetScalars(self.vtk_data_array_amp_real)
				self.image_amp_real.Modified()
				self.lut_amp_real.SetTableRange(self.image_amp_real.GetPointData().GetScalars().GetRange())
				self.lut_amp_real.Build()
				self.Layout()
				self.Show()
				self.RefreshScene()
			except:
				pass
			if self.ancestor.GetPage(0).citer_flow[6] > 0:
				try:
					self.flat_data_phase_real = (self.ancestor.GetPage(0).visual_phase_real).transpose(2,1,0).ravel();
					self.vtk_data_array_phase_real = numpy_support.numpy_to_vtk(self.flat_data_phase_real)
					self.image_phase_real.GetPointData().SetScalars(self.vtk_data_array_phase_real)
					self.image_phase_real.Modified()
					self.lut_phase_real.SetTableRange(self.image_phase_real.GetPointData().GetScalars().GetRange())
					self.lut_phase_real.Build()
					self.Layout()
					self.Show()
					self.RefreshScene()
				except:
					pass
		else:
			try:
				self.flat_data_amp_real = (self.ancestor.GetPage(0).visual_amp_real).transpose(2,1,0).ravel();
				self.vtk_data_array_amp_real = numpy_support.numpy_to_vtk(self.flat_data_amp_real)
				self.image_amp_real.GetPointData().SetScalars(self.vtk_data_array_amp_real)
				self.image_amp_real.Modified()
				self.ancestor.GetPage(0).seqdata_max = self.ancestor.GetPage(0).visual_amp_real.max()
				if self.ancestor.GetPage(0).citer_flow[6] > 0:
					self.flat_data_phase_real = (self.ancestor.GetPage(0).visual_phase_real).transpose(2,1,0).ravel()
					self.vtk_data_array_phase_real = numpy_support.numpy_to_vtk(self.flat_data_phase_real)
					self.vtk_data_array_phase_real.SetName("mapscalar")
					points_amp_real = self.image_amp_real.GetPointData()
					points_amp_real.AddArray(self.vtk_data_array_phase_real)
					self.image_amp_real.Modified()
				self.OnContourReal(None)
				if self.ancestor.GetPage(0).citer_flow[6] > 0:
					self.mapper_amp_real.SetScalarRange(self.image_amp_real.GetPointData().GetArray("mapscalar").GetRange())
					self.mapper_amp_real.ColorByArrayComponent("mapscalar",0)
					self.mapper_amp_real.SetScalarModeToUsePointFieldData()
					self.mapper_amp_real.Modified()
					self.mapper_amp_real.Update()
				else:
					self.mapper_amp_real.SetScalarRange(self.image_amp_real.GetPointData().GetScalars().GetRange())
					self.mapper_amp_real.Modified()
					self.mapper_amp_real.Update()
				self.RefreshScene()
			except:
				pass
	def UpdateRecip(self):
		if self.ancestor.GetPage(0).visual_amp_recip.shape[2] == 1:
			try:
				array = WrapArrayAmp(self.ancestor.GetPage(0).visual_amp_recip)
				self.flat_data_amp_recip = (array).transpose(2,1,0).ravel();
				self.vtk_data_array_amp_recip = numpy_support.numpy_to_vtk(self.flat_data_amp_recip)
				self.image_amp_recip.GetPointData().SetScalars(self.vtk_data_array_amp_recip)
				self.image_amp_recip.Modified()
				self.lut_amp_recip.SetTableRange(self.image_amp_recip.GetPointData().GetScalars().GetRange())
				self.lut_amp_recip.Build()
				self.Layout()
				self.Show()
				self.RefreshScene()
			except:
				pass
			if self.ancestor.GetPage(0).citer_flow[6] > 0:
				try:
					array = WrapArrayAmp(self.ancestor.GetPage(0).visual_phase_recip)
					self.flat_data_phase_recip = (array).transpose(2,1,0).ravel();
					self.vtk_data_array_phase_recip = numpy_support.numpy_to_vtk(self.flat_data_phase_recip)
					self.image_phase_recip.GetPointData().SetScalars(self.vtk_data_array_phase_recip)
					self.image_phase_recip.Modified()
					self.lut_phase_recip.SetTableRange(self.image_phase_recip.GetPointData().GetScalars().GetRange())
					self.lut_phase_recip.Build()
					self.Layout()
					self.Show()
					self.RefreshScene()
				except:
					pass
		else:
			try:
				array = WrapArrayAmp(self.ancestor.GetPage(0).visual_amp_recip)
				self.flat_data_amp_recip = (array).transpose(2,1,0).ravel();
				self.vtk_data_array_amp_recip = numpy_support.numpy_to_vtk(self.flat_data_amp_recip)
				self.image_amp_recip.GetPointData().SetScalars(self.vtk_data_array_amp_recip)
				self.image_amp_recip.Modified()
				self.ancestor.GetPage(0).seqdata_max_recip = self.ancestor.GetPage(0).visual_amp_recip.max()
				if self.ancestor.GetPage(0).citer_flow[6] > 0:
					array2 = WrapArrayAmp(self.ancestor.GetPage(0).visual_phase_recip)
					self.flat_data_phase_recip = (array2).transpose(2,1,0).ravel()
					self.vtk_data_array_phase_recip = numpy_support.numpy_to_vtk(self.flat_data_phase_recip)
					self.vtk_data_array_phase_recip.SetName("mapscalar")
					points_amp_recip = self.image_amp_recip.GetPointData()
					points_amp_recip.AddArray(self.vtk_data_array_phase_recip)
					self.image_amp_recip.Modified()
				self.OnContourRecip(None)
				if self.ancestor.GetPage(0).citer_flow[6] > 0:
					self.mapper_amp_recip.SetScalarRange(self.image_amp_recip.GetPointData().GetArray("mapscalar").GetRange())
					self.mapper_amp_recip.ColorByArrayComponent("mapscalar",0)
					self.mapper_amp_recip.SetScalarModeToUsePointFieldData()
					self.mapper_amp_recip.Modified()
					self.mapper_amp_recip.Update()
				else:
					self.mapper_amp_recip.SetScalarRange(self.image_amp_recip.GetPointData().GetScalars().GetRange())
					self.mapper_amp_recip.Modified()
					self.mapper_amp_recip.Update()
				self.renderer_amp_recip.ResetCamera()
				self.RefreshScene()
			except:
				pass
	def UpdateSupport(self):
		if self.ancestor.GetPage(0).visual_support.shape[2] == 1:
			pass
		else:
			try:
				self.flat_data_support = (self.ancestor.GetPage(0).visual_support).transpose(2,1,0).ravel();
				self.vtk_data_array_support = numpy_support.numpy_to_vtk(self.flat_data_support)
				self.image_support.GetPointData().SetScalars(self.vtk_data_array_support)
				self.image_support.Modified()
				#self.mapper_support.SetScalarRange(self.image_support.GetPointData().GetScalars().GetRange())
				self.mapper_support.SetScalarRange(0.0, 1.0)
				self.mapper_support.Modified()
				self.mapper_support.Update()
				self.filter_support.SetValue(0, 1.0)
				self.filter_support.Modified()
				self.filter_support.Update()
				#self.renderer_support.ResetCamera()
				self.RefreshScene()
			except:
				pass
