#############################################
##   Filename: panelgraph.py
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
import numpy
from time import strftime
from .common import IsNotWX4
from .common import CheckBoxNew
from .common import SpinnerObject
from .common import MIN_INT, MAX_INT
if IsNotWX4():
	from .plot import PlotCanvas, PolyLine, PlotGraphics
else:
	from wx.lib.plot import PlotCanvas
	from wx.lib.plot.polyobjects import PolyLine
	from wx.lib.plot.polyobjects import PlotGraphics
class PanelGraph(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		self.ancestor = parent
		self.fontpointsize=wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT).GetPointSize()
		self.colour = wx.Colour(30,70,115, alpha=wx.ALPHA_OPAQUE)
		self.canvas = PlotCanvas(self)
		if IsNotWX4():
			self.canvas.SetInitialSize(size=self.GetClientSize())
			self.canvas.SetShowScrollbars(True)
			self.canvas.SetEnableZoom(False)
			self.canvas.SetFontSizeAxis(point=12)
			self.canvas.SetFontSizeTitle(point=12)
			self.canvas.SetGridColour(wx.Colour(0, 0, 0))
			self.canvas.SetForegroundColour(wx.Colour(0, 0, 0))
			self.canvas.SetBackgroundColour(wx.Colour(255, 255, 255))
		else:
			self.canvas.axesPen = wx.Pen(self.colour, width=1, style=wx.PENSTYLE_SOLID)
			self.canvas.SetForegroundColour(wx.Colour(0, 0, 0))
			self.canvas.SetBackgroundColour(wx.Colour(255, 255, 255))
			self.canvas.enableGrid = (True,True)
			self.canvas.fontSizeAxis = self.fontpointsize
			self.canvas.fontSizeTitle = self.fontpointsize
		self.vbox = wx.BoxSizer(wx.VERTICAL)
		self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW)
		self.paused = False
		self.hbox_axes = wx.BoxSizer(wx.HORIZONTAL)
		self.vbox_axes_mm = wx.BoxSizer(wx.VERTICAL)
		self.hbox_axes_nmm = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox_axes_ermm = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox_axes.Add((10, -1))
		self.chkbox = CheckBoxNew(self, -1, 'Fixed limits', size=(-1, -1))
		self.chkbox.Bind(wx.EVT_CHECKBOX, self.OnCheck)
		self.hbox_axes.Add(self.chkbox, 0,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.hbox_axes.Add((10, -1))
		self.nmin = SpinnerObject(self,"N min: ",MAX_INT,1,1,1,200,150)
		self.nmin.GetItem(self.nmin.value, recursive=False).SetFlag(wx.EXPAND)
		self.nmin.GetItem(self.nmin.value, recursive=False).SetProportion(1)
		self.nmax = SpinnerObject(self,"N max:",MAX_INT,1,1,1,200,150)
		self.nmax.GetItem(self.nmax.value, recursive=False).SetFlag(wx.EXPAND)
		self.nmax.GetItem(self.nmax.value, recursive=False).SetProportion(1)
		self.hbox_axes_nmm.Add(self.nmin, 1,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.hbox_axes_nmm.Add(self.nmax, 1,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.nmin.Disable()
		self.nmax.Disable()
		self.nmin.spin.SetEventFunc(self.OnNSpin)
		self.nmin.value.Bind(wx.EVT_KEY_DOWN, self.OnNKey)
		self.nmax.spin.SetEventFunc(self.OnNSpin)
		self.nmax.value.Bind(wx.EVT_KEY_DOWN, self.OnNKey)
		self.ermin = SpinnerObject(self,"Error min: ",10000,0,0.1,0,200,150)
		self.ermin.GetItem(self.ermin.value, recursive=False).SetFlag(wx.EXPAND)
		self.ermin.GetItem(self.ermin.value, recursive=False).SetProportion(1)
		self.ermax = SpinnerObject(self,"Error max:",10000,0,0.1,1.1,200,150)
		self.ermax.GetItem(self.ermax.value, recursive=False).SetFlag(wx.EXPAND)
		self.ermax.GetItem(self.ermax.value, recursive=False).SetProportion(1)
		self.hbox_axes_ermm.Add(self.ermin, 1,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.hbox_axes_ermm.Add(self.ermax, 1,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=2)
		self.ermin.Disable()
		self.ermax.Disable()
		self.ermin.spin.SetEventFunc(self.OnNSpin)
		self.ermin.value.Bind(wx.EVT_KEY_DOWN, self.OnNKey)
		self.ermax.spin.SetEventFunc(self.OnNSpin)
		self.ermax.value.Bind(wx.EVT_KEY_DOWN, self.OnNKey)
		self.vbox_axes_mm.Add(self.hbox_axes_nmm, 0, wx.EXPAND|wx.LEFT|wx.RIGHT)
		self.vbox_axes_mm.Add(self.hbox_axes_ermm, 0, wx.EXPAND|wx.LEFT|wx.RIGHT)
		self.hbox_axes.Add(self.vbox_axes_mm, 1, wx.EXPAND|wx.LEFT|wx.RIGHT)
		self.vbox.Add(self.hbox_axes, 0, wx.EXPAND|wx.LEFT|wx.RIGHT)
		self.vbox.Add((-1, 5))
		self.hbox_btn = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox_btn.AddSpacer(20)
		self.button_pause =wx.Button(self, label="Pause Graph")
		self.Bind(wx.EVT_BUTTON, self.OnClickPauseButton, self.button_pause)
		self.hbox_btn.Add(self.button_pause)
		self.button_save =wx.Button(self, label="Save Data")
		self.Bind(wx.EVT_BUTTON, self.OnClickSaveButton, self.button_save)
		self.hbox_btn.Add(self.button_save)
		self.vbox.Add(self.hbox_btn, 0, wx.EXPAND)
		self.SetSizer(self.vbox)
		self.Fit()
		self.Show()
		self.data_poll_timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.UpdateGraph, self.data_poll_timer)
	def OnCheck(self,event):
		if self.chkbox.GetValue():
			try:
				length = len(self.ancestor.GetPage(0).residual)
			except:
				self.ancestor.GetPage(0).queue_info.put("Graph fixed limits not defined.")
				self.ancestor.GetPage(4).UpdateLog(None)
				return
			data_length = self.ancestor.GetPage(0).citer_flow[0]
			self.nmax.spin.SetRange(1, length)
			self.nmax.spin.SetValue(data_length)
			self.nmax.value.ChangeValue("%d"%data_length)
			self.nmin.Enable()
			self.nmax.Enable()
			self.ermin.Enable()
			self.ermax.Enable()
		else:
			self.nmin.Disable()
			self.nmax.Disable()
			self.ermin.Disable()
			self.ermax.Disable()
	def OnNSpin(self,event):
		try:
			xmin = int(self.nmin.value.GetValue())
			xmax = int(self.nmax.value.GetValue())
			ymin = float(self.ermin.value.GetValue())
			ymax = float(self.ermax.value.GetValue())
		except:
			pass
		else:
			if xmin > xmax or ymin> ymax:
				return
			else:
				self._UpdateGraph(xmin, xmax, ymin, ymax)
	def OnNKey(self,event):
		if event.GetKeyCode() == wx.WXK_RETURN:
			self.OnNSpin(None)
		else:
			event.Skip()
	def OnClickPauseButton(self, event):
		self.paused = not self.paused
		label = "Resume" if self.paused else "Pause Graph"
		if self.paused == True:
			if IsNotWX4():
				self.canvas.SetEnableZoom(True)
			else:
				self.canvas.enableZoom = True
		else:
			if IsNotWX4():
				self.canvas.SetEnableZoom(False)
			else:
				self.canvas.enableZoom = False
		self.button_pause.SetLabel(label)
	def OnClickSaveButton(self, event):
		data_length = self.ancestor.GetPage(0).citer_flow[0]
		if data_length > 0:
			self.ancestor.GetPage(0).OnClickPause(self.ancestor.GetPage(0))
			x = numpy.arange(data_length)
			y = self.ancestor.GetPage(0).residual[:data_length]
			xy = numpy.vstack((x,y)).T
			datestr = strftime("%Y-%m-%d_%H.%M.%S")
			numpy.savetxt('Residual_'+datestr+'.csv', xy, delimiter=',')
			self.ancestor.GetPage(0).OnClickPause(self.ancestor.GetPage(0))
	def _UpdateGraph(self, xmin, xmax, ymin, ymax):
		x = numpy.arange(xmax-xmin)
		y = self.ancestor.GetPage(0).residual[xmin:xmax]
		data = numpy.vstack((x,y)).T
		line = PolyLine(data, colour=self.colour, width=2.5)
		graphic = PlotGraphics([line],"Error Residual", " Iteration", "Residual")
		self.canvas.Draw(graphic, xAxis=(xmin, xmax), yAxis=(ymin, ymax))
	def UpdateGraph(self,event):
		if self.ancestor.GetPage(0).citer_flow[1] == 2:
			self.data_poll_timer.Stop()
			return
		if self.ancestor.GetPage(0).pipeline_started == True and self.paused != True:
			try:
				data_length = self.ancestor.GetPage(0).citer_flow[0]
				if self.chkbox.GetValue():
					xmin = int(self.nmin.value.GetValue())
					xmax = int(self.nmax.value.GetValue())
					ymin = float(self.ermin.value.GetValue())
					ymax = float(self.ermax.value.GetValue())
				else:
					xmin = 0
					xmax = data_length
					ymin = 0.0
					ymax = 1.2
				self._UpdateGraph(xmin, xmax, ymin, ymax)
			except:
				pass
