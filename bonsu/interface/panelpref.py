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
		self.FXAA = panelvisual.FXAA
		panelvisual.FXAAScene(False)
		if panelvisual.linewidget is not None:
			self.linewidget_enabled = panelvisual.linewidget.GetEnabled()
		if panelvisual.anglewidget is not None:
			self.anglewiget_enabled = panelvisual.anglewidget.GetEnabled()
		widget_enabled = panelvisual.widget.GetEnabled()
		if widget_enabled:
			panelvisual.widget.SetEnabled(0)
			self.widget_viewport = panelvisual.widget.GetViewport()
		self.renderer_amp_real_undocked = vtk.vtkRenderer()
		self.renderer_phase_real_undocked = vtk.vtkRenderer()
		self.renderer_amp_recip_undocked = vtk.vtkRenderer()
		self.renderer_phase_recip_undocked = vtk.vtkRenderer()
		from .render import wxVTKRenderWindowInteractor
		self.renWin = wxVTKRenderWindowInteractor(self, wx.ID_ANY)
		self.renWin.Enable(1)
		self.renWin.GetRenderWindow().SetMultiSamples(0)
		panelvisual.renderers = panelvisual.renWin.GetRenderWindow().GetRenderers()
		panelvisual.renderers.InitTraversal()
		renderer = panelvisual.renderers.GetFirstRenderer()
		while renderer != None:
			if renderer is panelvisual.renderer_amp_real:
				self.RenderSwitch(panelvisual.renderer_amp_real, self.renderer_amp_real_undocked)
			elif renderer is panelvisual.renderer_phase_real:
				self.RenderSwitch(panelvisual.renderer_phase_real, self.renderer_phase_real_undocked)
			elif renderer is panelvisual.renderer_amp_recip:
				self.RenderSwitch(panelvisual.renderer_amp_recip, self.renderer_amp_recip_undocked)
			elif renderer is panelvisual.renderer_phase_recip:
				self.RenderSwitch(panelvisual.renderer_phase_recip, self.renderer_phase_recip_undocked)
			renderer = panelvisual.renderers.GetNextItem()
		panelvisual.renderer_amp_real = self.renderer_amp_real_undocked
		panelvisual.renderer_phase_real = self.renderer_phase_real_undocked
		panelvisual.renderer_amp_recip = self.renderer_amp_recip_undocked
		panelvisual.renderer_phase_recip = self.renderer_phase_recip_undocked
		panelvisual.style = panelvisual.renWin.GetInteractorStyle()
		self.style2D = vtk.vtkInteractorStyleImage()
		self.style3D = vtk.vtkInteractorStyleSwitch()
		self.style3D.SetCurrentStyleToTrackballCamera()
		if panelvisual.style is panelvisual.style3D:
			self.renWin.SetInteractorStyle(self.style3D)
			panelvisual.style = self.style3D
		else:
			self.renWin.SetInteractorStyle(self.style2D)
			panelvisual.style = self.style2D
		panelvisual.picker = panelvisual.renWinMain.GetPicker()
		self.renWin.SetPicker(panelvisual.picker)
		panelvisual.renWin = self.renWin
		panelvisual.renWinMain.Hide()
		panelvisual.vtkvbox.Layout()
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
		if widget_enabled:
			panelvisual.widget.SetEnabled(0)
			panelvisual.widget.SetInteractor(panelvisual.renWin)
			panelvisual.widget.SetOrientationMarker(panelvisual.axes)
			panelvisual.widget.Modified()
			panelvisual.widget.SetViewport(self.widget_viewport)
			panelvisual.widget.SetEnabled(1)
			panelvisual.widget.InteractiveOn()
		if self.FXAA:
			panelvisual.FXAAScene()
		panelvisual.SetBackground()
		self.vbox = wx.BoxSizer(wx.VERTICAL)
		self.vbox.Add(self.renWin, 1, wx.EXPAND)
		self.SetSizer(self.vbox)
		self.Fit()
		self.Layout()
		self.Show()
	def RenderSwitch(self, renderer_old, renderer_new, undock=True):
		if not undock:
			renderer_new.RemoveAllViewProps()
		props = renderer_old.GetViewProps()
		view = renderer_old.GetViewport()
		for i in range(props.GetNumberOfItems()):
			renderer_new.AddViewProp(props.GetItemAsObject(i))
		renderer_new.Modified()
		if undock:
			self.renWin.GetRenderWindow().AddRenderer(renderer_new)
			cam = renderer_old.GetActiveCamera()
			renderer_new.SetActiveCamera(cam)
		renderer_new.SetViewport(view)
	def OnPreventExit(self,event):
		pass
	def OnExit(self,event):
		self.GetParent().nb.SetSelection(1)
		panelvisual = self.GetParent().nb.GetPage(1)
		panelvisual.vtkpanel_holder.Hide()
		panelvisual.vtkpanel_holder.Layout()
		panelvisual.vtkpanel.Show()
		panelvisual.vtkpanel.Layout()
		panelvisual.Layout()
		self.FXAA = panelvisual.FXAA
		panelvisual.FXAAScene(False)
		if panelvisual.linewidget is not None:
			self.linewidget_enabled = panelvisual.linewidget.GetEnabled()
		if panelvisual.anglewidget is not None:
			self.anglewiget_enabled = panelvisual.anglewidget.GetEnabled()
		widget_enabled = panelvisual.widget.GetEnabled()
		if widget_enabled:
			panelvisual.widget.SetEnabled(0)
			self.widget_viewport = panelvisual.widget.GetViewport()
		panelvisual.renWinMain.Show()
		panelvisual.renWinMain.Layout()
		panelvisual.vtkvbox.Layout()
		panelvisual.renderers = panelvisual.renWin.GetRenderWindow().GetRenderers()
		panelvisual.renderers.InitTraversal()
		panelvisual.renWin = panelvisual.renWinMain
		renderers = self.renWin.GetRenderWindow().GetRenderers()
		renderer = renderers.GetFirstRenderer()
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_real_docked)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_real_docked)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_recip_docked)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_recip_docked)
		while renderer != None:
			if renderer is panelvisual.renderer_amp_real:
				self.RenderSwitch(panelvisual.renderer_amp_real, panelvisual.renderer_amp_real_docked, undock=False)
				panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_real_docked)
			elif renderer is panelvisual.renderer_phase_real:
				self.RenderSwitch(panelvisual.renderer_phase_real, panelvisual.renderer_phase_real_docked, undock=False)
				panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_phase_real_docked)
			elif renderer is panelvisual.renderer_amp_recip:
				self.RenderSwitch(panelvisual.renderer_amp_recip, panelvisual.renderer_amp_recip_docked, undock=False)
				panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_recip_docked)
			elif renderer is panelvisual.renderer_phase_recip:
				self.RenderSwitch(panelvisual.renderer_phase_recip, panelvisual.renderer_phase_recip_docked, undock=False)
				panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_phase_recip_docked)
			renderer = panelvisual.renderers.GetNextItem()
		panelvisual.renderer_amp_real = panelvisual.renderer_amp_real_docked
		panelvisual.renderer_phase_real = panelvisual.renderer_phase_real_docked
		panelvisual.renderer_amp_recip = panelvisual.renderer_amp_recip_docked
		panelvisual.renderer_phase_recip = panelvisual.renderer_phase_recip_docked
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
		panelvisual.renWin.SetInteractorStyle(panelvisual.style2D)
		panelvisual.renWin.SetInteractorStyle(panelvisual.style3D)
		if panelvisual.style is self.style3D:
			panelvisual.renWin.SetInteractorStyle(panelvisual.style3D)
			panelvisual.style = panelvisual.style3D
		else:
			panelvisual.renWin.SetInteractorStyle(panelvisual.style2D)
			panelvisual.style = panelvisual.style2D
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
		if widget_enabled != 0:
			panelvisual.widget.SetEnabled(0)
			panelvisual.widget.SetInteractor(panelvisual.renWin)
			panelvisual.widget.SetOrientationMarker(panelvisual.axes)
			panelvisual.widget.Modified()
			panelvisual.widget.SetViewport(self.widget_viewport)
			panelvisual.widget.SetEnabled(1)
			panelvisual.widget.InteractiveOn()
		if self.FXAA:
			panelvisual.FXAAScene()
		panelvisual.SetBackground()
		panelvisual.ancestor.GetParent().visualdialog_docked = True
		del self.GetParent().visualdialog
		self.Destroy()
