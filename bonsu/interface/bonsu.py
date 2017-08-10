#############################################
##   Filename: bonsu.py
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
__author__ = "Marcus C. Newton"
__copyright__ = "Copyright 2011-2017 Marcus C. Newton"
__credits__ = ["Marcus C. Newton"]
__license__ = "GPL v3"
__version__ = "2.3.0"
__maintainer__ = "Marcus C. Newton"
__email__ = "Bonsu.Devel@gmail.com"
__status__ = "Production"
__builddate__ = ''
import os
import sys
import wx
import numpy
import vtk
from PIL import Image
from .panelphase import PanelPhase
from .panelvisual import PanelVisual
from .panelgraph import PanelGraph
from .panelscript import PanelScript
from .panelstdout import PanelStdOut
from .panelstdout import RedirectText
from .instance import SaveInstance
from .instance import RestoreInstance
from .instance import NewInstance
from .panelpref import VisualDialog
from .common import IsNotWX4
from .common import CustomAboutDialog
if IsNotWX4():
	pass
else:
	import wx.adv
class MainWindow(wx.Frame):
	def __init__(self, parent, title):
		self.dirname=os.getcwd()
		wx.Frame.__init__(self, parent, title=title, size=(1000,700))
		self.SetSizeHints(1000,700,-1,-1)
		self.CreateStatusBar()
		filemenu= wx.Menu()
		menuOpen = filemenu.Append(wx.ID_OPEN, "&Open"," Open saved state")
		menuSave = filemenu.Append(wx.ID_SAVE, "&Save"," Save current state")
		filemenu.InsertSeparator(2)
		menuNew = filemenu.Append(wx.ID_NEW, "&New"," Create new session")
		filemenu.InsertSeparator(4)
		menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
		viewmenu = wx.Menu()
		vismenu = wx.Menu()
		self.viewmenuundock = vismenu.Append(wx.ID_ANY,"&Undock","Undock the visualisation")
		self.viewmenuundock.Enable(0)
		self.viewmenudock = vismenu.Append(wx.ID_ANY,"&Dock","Dock the visualisation")
		self.viewmenudock.Enable(0)
		self.Bind(wx.EVT_MENU, self.OnUndock, self.viewmenuundock)
		self.Bind(wx.EVT_MENU, self.OnDock, self.viewmenudock)
		if IsNotWX4():
			viewmenu.AppendMenu(wx.ID_ANY,"&Visualisation", vismenu)
		else:
			viewmenu.Append(wx.ID_ANY,"&Visualisation", vismenu)
		self.visualdialog_docked = True
		editmenu = wx.Menu()
		self.menuCWD = editmenu.Append(wx.ID_ANY, "Current Working &Directory","Current Working Directory")
		self.Bind(wx.EVT_MENU, self.OnCWD, self.menuCWD)
		helpmenu= wx.Menu()
		menuAbout= helpmenu.Append(wx.ID_ABOUT, "&About"," Information about Bonsu")
		menuDoc= helpmenu.Append(wx.ID_HELP, "&Contents","Documentation")
		menuBar = wx.MenuBar()
		menuBar.Append(filemenu,"&File")
		menuBar.Append(viewmenu,"&View")
		menuBar.Append(editmenu,"&Edit")
		menuBar.Append(helpmenu,"&Help")
		self.SetMenuBar(menuBar)
		self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
		self.Bind(wx.EVT_MENU, self.OnSave, menuSave)
		self.Bind(wx.EVT_MENU, self.OnNew, menuNew)
		self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
		self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
		self.Bind(wx.EVT_MENU, self.OnHelp, menuDoc)
		self.Bind(wx.EVT_CLOSE, self.OnExit)
		self.fontpointsize=wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT).GetPointSize()
		self.font = wx.Font(self.fontpointsize, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		self.SetFont(self.font)
		icon = wx.Icon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'image',  'bonsu.ico'), wx.BITMAP_TYPE_ICO)
		wx.Frame.SetIcon(self, icon)
		self.nb = None
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.Fit()
		self.Layout()
		self.Show()
	def OnAbout(self,e):
		description =\
		"""Bonsu is a collection of tools and algorithms primarily for the reconstruction of phase information from diffraction intensity measurements."""
		licence =\
		"""This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>."""
		if IsNotWX4():
			info = wx.AboutDialogInfo()
		else:
			info = wx.adv.AboutDialogInfo()
		info.SetIcon(wx.Icon(os.path.join(os.path.dirname(os.path.dirname(__file__)),'image',  'bonsu.ico'), wx.BITMAP_TYPE_ICO))
		info.SetName('Bonsu')
		info.SetVersion(__version__)
		info.SetDescription(description)
		info.SetCopyright('Copyright (C) 2011-2017 Marcus C. Newton')
		info.SetWebSite('github.com/bonsudev/bonsu')
		info.SetLicence(licence)
		info.AddDeveloper('Marcus C. Newton')
		self.version_str_list = []
		self.version_str_list.append("Python "+str(sys.version_info.major)+"."+str(sys.version_info.minor)+"."+str(sys.version_info.micro))
		self.version_str_list.append("wxPython "+wx.version())
		self.version_str_list.append("NumPy "+numpy.version.version)
		self.version_str_list.append("VTK "+vtk.vtkVersion().GetVTKVersion())
		self.version_str_list.append("PIL "+Image.VERSION)
		try:
			import h5py
			self.version_str_list.append("h5Py "+h5py.version.version)
		except:
			pass
		self.version_str_list.append("Build date: "+__builddate__)
		info.SetArtists(self.version_str_list)
		dialog = CustomAboutDialog(self,info)
		dialog.ShowModal()
		dialog.Destroy()
	def OnHelp(self,e):
		dlg = wx.MessageDialog(self, "Bonsu will attempt to open the"+os.linesep+"documentation with your default"+os.linesep+"browser. Continue?","Confirm Open", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
		result = dlg.ShowModal()
		dlg.Destroy()
		if result == wx.ID_OK:
			path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs',  'bonsu.html')
			if sys.platform.startswith('win'):
				os.startfile(path)
			elif sys.platform.startswith('darwin'):
				from subprocess import Popen
				Popen(['open', path])
			else:
				try:
					from subprocess import Popen
					Popen(['xdg-open', path])
				except:
					pass
	def OnExit(self,e):
		dlg = wx.MessageDialog(self, "Exit Bonsu?","Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
		result = dlg.ShowModal()
		dlg.Destroy()
		if result == wx.ID_OK:
			self.Destroy()
	def CurrentWD(self):
		try:
			cwd = os.getcwd()
		except:
			from os.path import expanduser
			cwd = expanduser("~")
		return cwd
	def OnOpen(self,e):
		panelphase = self.GetChildren()[1].GetPage(0)
		if panelphase.pipeline_started == False:
			cwd = self.CurrentWD()
			dlg = wx.FileDialog(self, "Choose a file", cwd, "", "fin files (*.fin)|*.fin|All files (*.*)|*.*", wx.OPEN)
			if dlg.ShowModal() == wx.ID_OK:
				self.filename = dlg.GetFilename()
				self.dirname = dlg.GetDirectory()
				RestoreInstance(self)
			dlg.Destroy()
	def OnSave(self,e):
		panelphase = self.GetChildren()[1].GetPage(0)
		if panelphase.pipeline_started == False:
			cwd = self.CurrentWD()
			dlg = wx.FileDialog(self, "Choose a file", cwd, "", "fin files (*.fin)|*.fin|All files (*.*)|*.*", wx.SAVE | wx.OVERWRITE_PROMPT)
			if dlg.ShowModal() == wx.ID_OK:
				self.filename=dlg.GetFilename()
				self.dirname=dlg.GetDirectory()
				SaveInstance(self)
			dlg.Destroy()
	def OnNew(self,e):
		panelphase = self.GetChildren()[1].GetPage(0)
		if panelphase.pipeline_started == False:
			dlg = wx.MessageDialog(self, "Start a new session?"+os.linesep+"(This will erase the current session data)","Confirm New Session", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
			result = dlg.ShowModal()
			dlg.Destroy()
			if result == wx.ID_OK:
				NewInstance(self)
	def OnCWD(self,e):
		panelphase = self.GetChildren()[1].GetPage(0)
		if panelphase.pipeline_started == False:
			cwd = self.CurrentWD()
			dlg = wx.DirDialog(self, 'Set Working Directory', cwd, style=wx.DD_DEFAULT_STYLE, name="Change Current Working Directory")
			if dlg.ShowModal() == wx.ID_OK:
				os.chdir(dlg.GetPath())
			dlg.Destroy()
	def OnUndock(self,e):
		try:
			self.visualdialog
		except AttributeError:
			self.visualdialog = VisualDialog(self)
			self.visualdialog_docked = False
	def OnDock(self,e):
		try:
			self.visualdialog
		except AttributeError:
			pass
		else:
			self.visualdialog.OnExit(e)
			self.visualdialog_docked = True
	def OnFileArg(self):
		try:
			arg = sys.argv[1]
		except:
			pass
		else:
			if arg.endswith(".fin"):
				self.filename=arg
				self.dirname=os.getcwd()
				try:
					RestoreInstance(self)
				except:
					pass
class main():
	def __init__(self):
		app = wx.App()
		self.frame = MainWindow(None, "Bonsu - The Interactive Phase Retrieval Suite")
		self.nb = wx.Notebook(self.frame)
		self.nb.AddPage(PanelPhase(self.nb), "Phasing Pipeline")
		self.nb.AddPage(PanelVisual(self.nb), "Visualisation")
		self.nb.AddPage(PanelGraph(self.nb), "Graph")
		self.nb.AddPage(PanelScript(self.nb), "Python Prompt")
		self.nb.AddPage(PanelStdOut(self.nb), "Log")
		self.frame.nb = self.nb
		self.frame.sizer.Add(self.nb, 1, wx.ALL|wx.EXPAND, 5)
		self.frame.SetSizer(self.frame.sizer)
		self.frame.Fit()
		self.frame.Show()
		self.frame.OnFileArg()
		app.MainLoop()
if __name__ == '__main__':
	main_app = main()
