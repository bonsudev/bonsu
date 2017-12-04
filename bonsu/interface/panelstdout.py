#############################################
##   Filename: panelstdout.py
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
import sys
from time import strftime
from .common import IsNotWX4
class RedirectText:
	def __init__(self,aWxTextCtrl):
		self.out=aWxTextCtrl
	def write(self,string):
		self.out.AppendText(string)
	def flush(self):
		pass
class PanelStdOut(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		self.ancestor = parent
		self.filename = ""
		self.dirname = '.'
		self.vbox = wx.BoxSizer(wx.VERTICAL)
		self.log= wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
		self.vbox.Add(self.log, 1, wx.EXPAND | wx.ALL, 2)
		self.vbox.AddSpacer(2)
		self.hbox_ent = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox_ent.AddSpacer(20)
		self.font = self.ancestor.GetParent().font
		self.label = wx.StaticText(self, -1,"Log Entry:", style=wx.ALIGN_CENTRE_HORIZONTAL, size=(160,-1) )
		self.label.SetFont(self.font)
		self.hbox_ent.Add( self.label, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 2)
		self.entry = wx.TextCtrl(self, -1, style=wx.TE_PROCESS_ENTER)
		self.entry.SetFont(self.font)
		self.entry.SetValue("")
		if IsNotWX4():
			self.entry.SetToolTipString("Enter comments into the log here.")
		else:
			self.entry.SetToolTip("Enter comments into the log here.")
		self.entry.Bind(wx.EVT_TEXT_ENTER, self.OnEnterComments)
		self.hbox_ent.Add( self.entry, 1, wx.EXPAND | wx.LEFT | wx.RIGHT)
		self.vbox.Add(self.hbox_ent, 0, wx.EXPAND)
		self.hbox_btn = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox_btn.AddSpacer(20)
		self.button_save =wx.Button(self, label="Save Log")
		self.Bind(wx.EVT_BUTTON, self.OnClickSaveButton, self.button_save)
		self.hbox_btn.Add(self.button_save)
		self.button_clear =wx.Button(self, label="Clear Log")
		self.Bind(wx.EVT_BUTTON, self.OnClickClearButton, self.button_clear)
		self.hbox_btn.Add(self.button_clear)
		self.vbox.Add(self.hbox_btn, 0, wx.EXPAND)
		self.SetSizerAndFit(self.vbox)
		self.redir=RedirectText(self.log)
		sys.stdout=self.redir
		self.data_poll_timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.UpdateLog, self.data_poll_timer)
	def UpdateLog(self,event):
		try:
			while not self.ancestor.GetPage(0).queue_info.empty():
				string  = self.ancestor.GetPage(0).queue_info.get()
				print(string)
				self.ancestor.GetPage(0).queue_info.task_done()
		except:
			pass
		if self.ancestor.GetPage(0).citer_flow[1] == 2 or self.ancestor.GetPage(0).pipeline_started == False:
			self.data_poll_timer.Stop()
			return
	def OnClickSaveButton(self, event):
		try:
			datestr = strftime("%Y-%m-%d_%H.%M.%S")
			file = open('log_'+datestr+'.txt', 'w')
			text = self.log.GetValue()
			file.write(text)
			file.close()
		except:
			pass
	def OnClickClearButton(self,event):
		dlg = wx.MessageDialog(self, "Clear log?","Confirm clearing log", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
		result = dlg.ShowModal()
		dlg.Destroy()
		if result == wx.ID_OK:
			try:
				self.log.Clear()
			except:
				pass
	def OnEnterComments(self,event):
		value = self.entry.GetValue()
		self.ancestor.GetPage(0).queue_info.put(value)
		self.entry.Clear()
		self.UpdateLog(None)
