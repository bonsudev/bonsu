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
	def UpdateGraph(self,event):
		if self.ancestor.GetPage(0).citer_flow[1] == 2:
			self.data_poll_timer.Stop()
			return
		if self.ancestor.GetPage(0).pipeline_started == True and self.paused != True:
			try:
				data_length = self.ancestor.GetPage(0).citer_flow[0]
				x = numpy.arange(data_length)
				y = self.ancestor.GetPage(0).residual[:data_length]
				data = numpy.vstack((x,y)).T
				line = PolyLine(data, colour=self.colour, width=2.5)
				graphic = PlotGraphics([line],"Error Residual", " Iteration", "Residual")
				self.canvas.Draw(graphic, xAxis=(0, data_length), yAxis=(0.0, 1.2))
			except:
				pass
