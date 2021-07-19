#############################################
##   Filename: panelscipt.py
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
from wx.py.shell import Shell
class ShellNew(Shell):
	def __init__(self, parent, *args, **kwargs):
		Shell.__init__(self, parent, *args, **kwargs)
		self.Bind(wx.EVT_MIDDLE_UP, self.OnMiddle)
	def OnMiddle(self, event):
		pass
class PanelScript(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		self.intro = "Interactive Phase Retrieval Suite"
		self.shell = ShellNew(parent = self, id = wx.ID_ANY, introText=self.intro)
		self.shell.zoom(4)
		self.shell.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown, self.shell)
		self.ih = 0
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.shell, 1, flag = wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		sizer.Fit(self)
		self.SetSizer(sizer)
		self.SetAutoLayout(True)
		self.Layout()
	def OnKeyDown(self, event):
		if self.shell.AutoCompActive():
			event.Skip()
			return
		key = event.GetKeyCode()
		if key == wx.WXK_RETURN:
			self.ih = 0
			self.shell.processLine()
			self.shell.clearCommand()
		elif key == wx.WXK_UP:
			if self.ih < len(self.shell.history):
				self.ih += 1
				self.shell.clearCommand()
				self.shell.write(self.shell.history[(self.ih-1)])
		elif key == wx.WXK_DOWN:
			self.shell.clearCommand()
			self.ih -= 1
			if self.ih > 0:
				self.shell.write(self.shell.history[self.ih - 1])
			else:
				self.ih = 0
		else:
			event.Skip()
