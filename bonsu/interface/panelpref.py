#############################################
##   Filename: panelpref.py
##
##    Copyright (C) 2011 - 2013 Marcus C. Newton
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
import vtk
import numpy
class VisualDialog(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, style=wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.MAXIMIZE_BOX | wx.CLOSE_BOX, title="Visualisation", size=(640,480))
		self.SetSizeHints(640,480,-1,-1)
		self.Bind(wx.EVT_CLOSE, self.OnExit)
		panelvisual = self.GetParent().nb.GetPage(1)
		panelvisual.vtkpanel.Hide()
		panelvisual.vtkpanel_holder.Show()
		panelvisual.vtkpanel.Layout()
		panelvisual.vtkpanel_holder.Layout()
		if panelvisual.linewidget is not None:
			self.linewidget_enabled = panelvisual.linewidget.GetEnabled()
		if panelvisual.anglewidget is not None:
			self.anglewiget_enabled = panelvisual.anglewidget.GetEnabled()
		panelvisual.style = panelvisual.renWin.GetInteractorStyle()
		from .render import wxVTKRenderWindowInteractor
		self.renWin = wxVTKRenderWindowInteractor(self, wx.ID_ANY)
		self.renWin.Enable(1)
		self.renWin.GetRenderWindow().SetMultiSamples(0)
		panelvisual.renderers = panelvisual.renWin.GetRenderWindow().GetRenderers()
		panelvisual.renderers.InitTraversal()
		renderer = panelvisual.renderers.GetFirstRenderer()
		while renderer != None:
			if renderer is panelvisual.renderer_amp_real:
				panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_real)
				self.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_real)
			elif renderer is panelvisual.renderer_phase_real:
				panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_real)
				self.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_phase_real)
			elif renderer is panelvisual.renderer_amp_recip:
				panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_recip)
				self.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_recip)
			elif renderer is panelvisual.renderer_phase_recip:
				panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_recip)
				self.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_phase_recip)
			renderer = panelvisual.renderers.GetNextItem()
		self.style2D = vtk.vtkInteractorStyleImage()
		self.style3D = vtk.vtkInteractorStyleSwitch()
		self.style3D.SetCurrentStyleToTrackballCamera()
		if panelvisual.style is panelvisual.style3D:
			self.renWin.SetInteractorStyle(self.style3D)
		else:
			self.renWin.SetInteractorStyle(self.style2D)
		panelvisual.picker = panelvisual.renWinMain.GetPicker()
		self.renWin.SetPicker(panelvisual.picker)
		panelvisual.renWin = self.renWin
		panelvisual.vtkvbox.Detach(panelvisual.renWinMain)
		panelvisual.vtkvbox.Layout()
		panelvisual.renWinMain.GetRenderWindow().Finalize()
		panelvisual.renWinMain.SetRenderWindow(None)
		try:
			panelvisual.renWinMain.Destroy()
		except:
			pass
		panelvisual.renWinMain = None
		panelvisual.renderers = panelvisual.renWin.GetRenderWindow().GetRenderers()
		panelvisual.RefreshSceneCMD = panelvisual.renWin.Render
		if panelvisual.linewidget is not None:
			panelvisual.linewidget.SetInteractor(panelvisual.renWin)
			panelvisual.linewidget.Modified()
			if self.linewidget_enabled:
				panelvisual.linewidget.SetEnabled(0)
				panelvisual.linewidget.SetEnabled(1)
		if panelvisual.anglewidget is not None:
			panelvisual.anglewidget.SetInteractor(panelvisual.renWin)
			panelvisual.anglewidget.Modified()
			if self.anglewiget_enabled:
				panelvisual.anglewidget.SetEnabled(0)
				panelvisual.anglewidget.SetEnabled(1)
		self.vbox = wx.BoxSizer(wx.VERTICAL)
		self.vbox.Add(self.renWin, 1, wx.EXPAND)
		self.SetSizer(self.vbox)
		self.Fit()
		self.Layout()
		self.Show()
	def OnExit(self,event):
		self.GetParent().nb.SetSelection(1)
		panelvisual = self.GetParent().nb.GetPage(1)
		panelvisual.vtkpanel_holder.Hide()
		panelvisual.vtkpanel_holder.Layout()
		panelvisual.vtkpanel.Show()
		panelvisual.vtkpanel.Layout()
		panelvisual.Layout()
		if panelvisual.linewidget is not None:
			self.linewidget_enabled = panelvisual.linewidget.GetEnabled()
		if panelvisual.anglewidget is not None:
			self.anglewiget_enabled = panelvisual.anglewidget.GetEnabled()
		from .render import wxVTKRenderWindowInteractor
		panelvisual.renWinMain = wxVTKRenderWindowInteractor(panelvisual.vtkpanel, wx.ID_ANY)
		panelvisual.renWinMain.Enable(1)
		panelvisual.renWinMain.GetRenderWindow().SetMultiSamples(0)
		panelvisual.vtkvbox.Add(panelvisual.renWinMain, 1, wx.EXPAND)
		panelvisual.vtkvbox.Layout()
		panelvisual.renWin = panelvisual.renWinMain
		panelvisual.renderers = self.renWin.GetRenderWindow().GetRenderers()
		panelvisual.renderers.InitTraversal()
		renderer = panelvisual.renderers.GetFirstRenderer()
		while renderer != None:
			if renderer is panelvisual.renderer_amp_real:
					self.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_real)
					panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_real)
			elif renderer is panelvisual.renderer_phase_real:
					self.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_real)
					panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_phase_real)
			elif renderer is panelvisual.renderer_amp_recip:
					self.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_recip)
					panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_recip)
			elif renderer is panelvisual.renderer_phase_recip:
					self.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_recip)
					panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_phase_recip)
			renderer = panelvisual.renderers.GetNextItem()
		if (panelvisual.style is panelvisual.style3D) or (panelvisual.style is self.style3D):
			panelvisual.renWin.SetInteractorStyle(panelvisual.style3D)
		else:
			panelvisual.renWin.SetInteractorStyle(panelvisual.style2D)
		panelvisual.style = None
		panelvisual.renWin.SetPicker(panelvisual.picker)
		self.renWin.GetRenderWindow().Finalize()
		self.renWin.SetRenderWindow(None)
		try:
			self.renWin.Destroy()
		except:
			pass
		del self.renWin
		panelvisual.renderers = panelvisual.renWin.GetRenderWindow().GetRenderers()
		self.GetParent().Refresh()
		panelvisual.RefreshSceneCMD = panelvisual.renWin.Render
		if panelvisual.linewidget is not None:
			panelvisual.linewidget.SetInteractor(panelvisual.renWin)
			panelvisual.linewidget.Modified()
			if self.linewidget_enabled:
				panelvisual.linewidget.SetEnabled(0)
				panelvisual.linewidget.SetEnabled(1)
		if panelvisual.anglewidget is not None:
			panelvisual.anglewidget.SetInteractor(panelvisual.renWin)
			panelvisual.anglewidget.Modified()
			if self.anglewiget_enabled:
				panelvisual.anglewidget.SetEnabled(0)
				panelvisual.anglewidget.SetEnabled(1)
		panelvisual.ancestor.GetParent().visualdialog_docked = True
		del self.GetParent().visualdialog
		self.Destroy()
