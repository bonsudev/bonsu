#############################################
##   Filename: panelphase.py
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
from threading import BoundedSemaphore
from Queue import Queue
import inspect
from . import subpanel
from .subpanel import *
from .action import *
from .common import getmaincollapseBitmap
from .common import getmainexpandBitmap
from .common import getmainhoverBitmap
class PanelPhase(wx.Panel,wx.TreeCtrl,wx.App):
	def __init__(self,parent):
		self.ancestor = parent
		self.citer_flow = numpy.zeros((8), dtype=numpy.int32)
		self.pipeline_started = False
		self.pipelineitems=[]
		self.thread = None
		self.thread_register = BoundedSemaphore(1000)
		self.queue_info = Queue()
		self.seqdata = None
		self.seqdata_max = 0.0
		self.seqdata_max_recip = 0.0
		self.support = None
		self.residual = None
		self.coordarray = None
		self.memory0 = None
		self.memory1 = None
		self.memory2 = None
		self.memory3 = None
		self.memory4 = None
		self.memory5 = None
		self.memory6 = None
		self.memory7 = None
		self.memory8 = None
		self.memory9 = None
		self.visual_amp_real = None
		self.visual_phase_real = None
		self.visual_support = None
		self.visual_amp_recip = None
		self.visual_phase_recip = None
		self.cms = numpy.load(os.path.join(os.path.dirname(__file__), 'cms.npy'))
		self.cmls = numpy.zeros((4,2), dtype=numpy.int16)
		self.compile = 1
		self.font = self.ancestor.GetParent().font
		self.panel = wx.Panel.__init__(self, parent)
		self.vbox = wx.BoxSizer(wx.VERTICAL)
		self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		self.splitter = wx.SplitterWindow(self, style=wx.SP_NOBORDER | wx.SP_NO_XP_THEME)
		self.splitter.SetSashSize(10)
		self.splitter.SetMinimumPaneSize(400)
		self.panel1 = wx.Panel(self.splitter,  style=wx.NO_BORDER)
		self.panel2 = wx.Panel(self.splitter,  style=wx.NO_BORDER)
		self.maintree = wx.TreeCtrl(self.panel1, style=wx.TR_HAS_BUTTONS | wx.TR_HIDE_ROOT | wx.TR_LINES_AT_ROOT | wx.TR_SINGLE, size=(180,1))
		self.maintree.__collapsing = False
		self.maintree.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnExpColTreeItem)
		self.maintree.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnExpColTreeItem)
		self.treeroot = self.maintree.AddRoot('root')
		self.maintree.SetItemHasChildren(self.treeroot)
		self.operpre =  self.maintree.AppendItem(self.treeroot,'Functions')
		self.algs =  self.maintree.AppendItem(self.treeroot,'Phasing Algorithms')
		self.operpost =  self.maintree.AppendItem(self.treeroot,'Phasing Operations')
		self.maintree.SetItemHasChildren(self.operpre, True)
		self.maintree.SetItemHasChildren(self.algs, True)
		self.maintree.SetItemHasChildren(self.operpost, True)
		self.maintree.SetItemImage(self.operpre, 0,  wx.TreeItemIcon_Normal)
		self.maintree.SetItemImage(self.algs, 0,  wx.TreeItemIcon_Normal)
		self.maintree.SetItemImage(self.operpost, 0,  wx.TreeItemIcon_Normal)
		self.treechilditems = []
		self.subpanel_members = inspect.getmembers(subpanel, inspect.isclass)
		for item in self.subpanel_members:
			if hasattr(item[1], 'treeitem'):
				if item[1].treeitem['type'] == 'operpre' or item[1].treeitem['type'] == 'operpreview':
					self.treechilditems.append(self.maintree.AppendItem(self.operpre,item[1].treeitem['name']))
				elif item[1].treeitem['type'] == 'algs' or item[1].treeitem['type'] == 'algsstart':
					self.treechilditems.append(self.maintree.AppendItem(self.algs,item[1].treeitem['name']))
				elif item[1].treeitem['type'] == 'operpost':
					self.treechilditems.append(self.maintree.AppendItem(self.operpost,item[1].treeitem['name']))
		limb = self.maintree.GetFirstChild(self.treeroot)[0]
		while limb.IsOk():
			self.maintree.SetItemFont(limb, self.font)
			branch = self.maintree.GetFirstChild(limb)[0]
			while branch.IsOk():
				self.maintree.SetItemFont(branch, self.font)
				branch = self.maintree.GetNextSibling(branch)
			limb= self.maintree.GetNextSibling(limb)
		self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivateTreeItem)
		self.maintree.Expand(self.operpre)
		self.mainlist=wx.ListCtrl(self.panel1,-1,style=wx.LC_REPORT|wx.LC_NO_HEADER|wx.LC_HRULES|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL, size=(180,1))
		self.mainlist.SetFont(self.font)
		self.ListColumn = self.mainlist.InsertColumn(0,'Pipeline of Operations', width = 200)
		self.mainlist.Bind(wx.EVT_SIZE, self.OnListResize)
		self.mainlist.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelectListItem)
		self.mainlist.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnRightDown)
		self.mainlist.Bind(wx.EVT_KEY_DOWN, self.OnKeyListItem)
		self.CurrentListItem = -1
		self.vbox1 = wx.BoxSizer(wx.VERTICAL)
		self.vbox1.Add((-1,200))
		self.spin_up = wx.BitmapButton(self.panel1, -1, getspinupBitmap(), size=(20, 50))
		self.spin_up.SetToolTipString('Change item positon in list.')
		self.spin_down = wx.BitmapButton(self.panel1, -1, getspindownBitmap(), size=(20, 50))
		self.spin_down.SetToolTipString('Change item positon in list.')
		self.vbox1.Add(self.spin_up)
		self.vbox1.Add(self.spin_down)
		self.Bind(wx.EVT_BUTTON, self.OnClickUp, self.spin_up)
		self.Bind(wx.EVT_BUTTON, self.OnClickDown, self.spin_down)
		self.hbox1.Add(self.maintree, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP ,2)
		self.hbox1.Add(self.vbox1, 0, wx.EXPAND | wx.LEFT | wx.RIGHT ,2)
		self.hbox1.Add(self.mainlist, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP ,2)
		self.menu_place_holder = wx.StaticText(self.panel2, label=' ')
		self.hbox2.Add(self.menu_place_holder ,1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=0)
		self.panel1.SetSizer(self.hbox1)
		self.panel1.font = self.font
		self.panel2.SetSizer(self.hbox2)
		self.panel2.font = self.font
		self.splitter.SplitVertically(self.panel1,self.panel2, sashPosition=400)
		self.vbox.Add(self.splitter, 5,  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2)
		self.vbox.Add((-1, 5))
		self.panel3 = wx.Panel(self,  style=wx.NO_BORDER)
		self.hbox_btn = wx.BoxSizer(wx.HORIZONTAL)
		self.button_start = wx.BitmapButton(self.panel3, -1, getstart48Bitmap(), size=(70, 70))
		self.button_start.SetToolTipString('Start pipline execution.')
		self.hbox_btn.Add(self.button_start)
		self.Bind(wx.EVT_BUTTON, self.OnClickStart,self.button_start)
		self.hbox_btn.Add((2, -1))
		self.button_pause = wx.BitmapButton(self.panel3, -1, getpause48Bitmap(), size=(70, 70))
		self.button_pause.SetToolTipString('Pause pipline execution.')
		self.hbox_btn.Add(self.button_pause)
		self.Bind(wx.EVT_BUTTON, self.OnClickPause,self.button_pause)
		self.hbox_btn.Add((2, -1))
		self.button_stop = wx.BitmapButton(self.panel3, -1, getstop48Bitmap(), size=(70, 70))
		self.button_stop.SetToolTipString('Stop pipline execution.')
		self.hbox_btn.Add(self.button_stop)
		self.Bind(wx.EVT_BUTTON, self.OnClickStop,self.button_stop)
		self.sbox1 = wx.StaticBox(self.panel3, label="Visualisation Options", style=wx.SUNKEN_BORDER)
		self.sbox1.SetFont(self.font)
		self.vbox_chk = wx.StaticBoxSizer(self.sbox1,wx.VERTICAL)
		self.hbox_chk1 = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox_chk2 = wx.BoxSizer(wx.HORIZONTAL)
		self.chkbox_amp_real = wx.CheckBox(self.panel3, -1, 'Real Space', size=(120, 25))
		self.chkbox_amp_real.SetFont(self.font)
		self.chkbox_amp_real.SetToolTipString("Visualise")
		self.chkbox_amp_real.SetValue(True)
		self.amp_real_update_interval = SpinnerObject(self.panel3,"",65535,1,1,10,0,70)
		self.amp_real_update_interval.value.SetToolTipString("Update interval")
		self.chkbox_amp_recip = wx.CheckBox(self.panel3, -1, 'Fourier Space', size=(130, 25))
		self.chkbox_amp_recip.SetFont(self.font)
		self.chkbox_amp_recip.SetToolTipString("Visualise")
		self.chkbox_amp_recip.SetValue(False)
		self.amp_recip_update_interval = SpinnerObject(self.panel3,"",65535,1,1,10,0,70)
		self.amp_recip_update_interval.value.SetToolTipString("Update interval")
		self.hbox_chk1.Add(self.chkbox_amp_real , flag=wx.ALIGN_LEFT |wx.LEFT, border=2)
		self.hbox_chk1.Add(self.amp_real_update_interval , flag=wx.ALIGN_LEFT |wx.LEFT, border=2)
		self.hbox_chk1.Add((20, -1))
		self.hbox_chk1.Add(self.chkbox_amp_recip , flag=wx.ALIGN_LEFT |wx.LEFT, border=2)
		self.hbox_chk1.Add(self.amp_recip_update_interval , flag=wx.ALIGN_LEFT |wx.LEFT, border=2)
		self.chkbox_support = wx.CheckBox(self.panel3, -1, 'Support', size=(120, 25))
		self.chkbox_support.SetFont(self.font)
		self.chkbox_support.SetToolTipString("Visualise")
		self.chkbox_support.SetValue(True)
		self.support_update_interval = SpinnerObject(self.panel3,"",65535,1,1,10,0,70)
		self.support_update_interval.value.SetToolTipString("Update interval")
		self.chkbox_phase = wx.CheckBox(self.panel3, -1, 'Phase', size=(200, 25))
		self.chkbox_phase.SetFont(self.font)
		self.chkbox_phase.SetToolTipString("Visualise")
		self.chkbox_phase.SetValue(False)
		self.hbox_chk2.Add(self.chkbox_support , flag=wx.ALIGN_LEFT |wx.LEFT, border=2)
		self.hbox_chk2.Add(self.support_update_interval , flag=wx.ALIGN_LEFT |wx.LEFT, border=2)
		self.hbox_chk2.Add((20, -1))
		self.hbox_chk2.Add(self.chkbox_phase , flag=wx.ALIGN_LEFT |wx.LEFT, border=2)
		self.hbox_chk2.Add((20, -1))
		self.sbox2 = wx.StaticBox(self.panel3, label="Threads", style=wx.SUNKEN_BORDER)
		self.sbox2.SetFont(self.font)
		self.vbox_thrd = wx.StaticBoxSizer(self.sbox2,wx.VERTICAL)
		self.nthreads = SpinnerObject(self.panel3,"",65535,1,1,1,5,90)
		self.nthreads.value.SetToolTipString("Maximum number of FFTW threads")
		self.nthreads.label.SetToolTipString("Maximum number of FFTW threads")
		self.vbox_thrd.Add(self.nthreads , flag=wx.ALIGN_LEFT |wx.LEFT, border=2)
		self.vbox_thrd.Add((-1,25))
		self.vbox_chk.Add(self.hbox_chk1)
		self.vbox_chk.Add(self.hbox_chk2)
		self.hbox_btn.Add(self.vbox_chk, flag=wx.ALIGN_LEFT |wx.LEFT, border=50)
		self.hbox_btn.Add(self.vbox_thrd, flag=wx.ALIGN_LEFT |wx.LEFT|wx.RIGHT, border=5)
		self.panel3.SetSizer(self.hbox_btn)
		self.panel3.font = self.font
		self.vbox.Add(self.panel3, 0, flag=wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=5)
		self.SetSizer(self.vbox)
	def EnablePanel(self, enable=True):
		if enable==False:
			self.maintree.Enable(False)
			self.maintree.Refresh()
			self.mainlist.Enable(False)
			self.mainlist.Refresh()
			self.spin_up.Enable(False)
			self.spin_down.Enable(False)
			self.spin_up.Refresh()
			self.spin_down.Refresh()
			for i in range(len(self.pipelineitems)):
				if self.pipelineitems[i].IsShown():
					self.pipelineitems[i].Enable(False)
					self.pipelineitems[i].Refresh()
					break
		elif enable==True:
			self.maintree.Enable(True)
			self.maintree.Refresh()
			self.mainlist.Enable(True)
			self.mainlist.Refresh()
			self.spin_up.Enable(True)
			self.spin_down.Enable(True)
			self.spin_up.Refresh()
			self.spin_down.Refresh()
			for j in range(len(self.pipelineitems)):
				self.pipelineitems[j].Enable(True)
				self.pipelineitems[j].Refresh()
	def UserMessage(self, title, msg):
		self.queue_info.put(title+": "+msg)
		dlg = wx.MessageDialog(self, msg, title, wx.OK)
		dlg.ShowModal()
		dlg.Destroy()
	def OnActivateTreeItem(self, event):
		item = event.GetItem()
		itemtext = self.maintree.GetItemText(item)
		itemcount = self.mainlist.GetItemCount()
		if itemtext in ['Functions','Phasing Algorithms', 'Phasing Operations']:
			if self.maintree.IsExpanded(item):
				self.maintree.Collapse(item)
			else:
				self.maintree.Expand(item)
		if (item not in (self.operpre,self.algs,self.operpost)):
			self.mainlist.InsertStringItem(itemcount,itemtext,itemcount)
			for item in self.subpanel_members:
				if hasattr(item[1], 'treeitem'):
					if item[1].treeitem['name'] == itemtext:
						if item[1].treeitem['type'] == 'operpreview':
							self.pipelineitems.append(item[1](self.panel2,self.ancestor));
						else:
							self.pipelineitems.append(item[1](self.panel2));
			self.pipelineitems[-1].Hide()
			self.hbox2.Add(self.pipelineitems[-1], 1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
	def OnExpColTreeItem(self, event):
		item = event.GetItem()
		if self.maintree.IsExpanded(item):
			self.maintree.SetItemImage(item, 1)
		else:
			self.maintree.SetItemImage(item, 0)
	def OnListResize(self, event):
		self.mainlist.SetColumnWidth(0, self.mainlist.GetSizeTuple()[0]-4)
		event.Skip()
	def OnKeyListItem(self, event):
		keycode = event.GetKeyCode()
		itemcount = self.mainlist.GetItemCount()
		if keycode == wx.WXK_DELETE and itemcount > 0:
			self.mainlist.DeleteItem(self.CurrentListItem)
			self.pipelineitems[self.CurrentListItem].Hide()
			self.pipelineitems.pop(self.CurrentListItem)
			if len(self.pipelineitems) == 0:
				self.menu_place_holder.Show()
			next = self.CurrentListItem - 1
			self.mainlist.SetItemState(next, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED )
		event.Skip()
	def OnSelectListItem(self, event):
		self.CurrentListItem = event.m_itemIndex
		if self.menu_place_holder.IsShown():
			self.menu_place_holder.Hide()
		name = self.mainlist.GetItemText(event.m_itemIndex)
		for  i in range(len(self.pipelineitems)):
			if i == self.CurrentListItem: self.pipelineitems[i].Show();
			else : self.pipelineitems[i].Hide()
		self.Layout()
		self.panel2.Layout()
	def OnRightDown(self,event):
		item = self.mainlist.HitTest(event.GetPosition())[0]
		if item > -1:
			menu = wx.Menu()
			item = wx.MenuItem(menu, wx.NewId(), "Delete")
			menu.AppendItem(item)
			self.CurrentListItem = event.m_itemIndex
			self.Bind(wx.EVT_MENU, self.OnItem, item)
			x,y = event.GetPosition()
			mx,my = self.GetSize()
			x= mx/4
			self.PopupMenu( menu, (x,y))
	def OnItem(self, event):
		self.mainlist.DeleteItem(self.CurrentListItem)
		self.pipelineitems[self.CurrentListItem].Hide()
		self.pipelineitems.pop(self.CurrentListItem)
		if len(self.pipelineitems) == 0:
			self.menu_place_holder.Show()
		next = self.CurrentListItem - 1
		self.mainlist.SetItemState(next, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED )
	def OnClickUp(self, event):
		itemcount = self.mainlist.GetItemCount()
		if self.CurrentListItem <= 0:
			return
		item = 0
		for i in range(itemcount):
			item = self.mainlist.GetNextItem(item,wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
			if item == 0:
				return
		item = -1
		item_next = 0
		while item_next >= 0:
			item_next = self.mainlist.GetNextItem(item,wx.LIST_NEXT_ALL, wx.LIST_STATE_DONTCARE)
			if self.mainlist.IsSelected(item_next) and (item > -1):
				t = self.mainlist.GetItemText(item_next)
				self.mainlist.DeleteItem(item_next)
				self.mainlist.InsertStringItem(item, t, item)
				self.mainlist.Select(item, 1)
				self.pipelineitems[item], self.pipelineitems[item_next] = self.pipelineitems[item_next], self.pipelineitems[item]
				cmd = wx.ListEvent(wx.EVT_LIST_ITEM_SELECTED.typeId, self.mainlist.GetId())
				cmd.m_itemIndex	= item
				self.mainlist.GetEventHandler().ProcessEvent(cmd)
				break
			item = item_next
	def OnClickDown(self, event):
		itemcount = self.mainlist.GetItemCount()
		if self.CurrentListItem < 0 or self.CurrentListItem == (itemcount - 1):
			return
		item = 0
		for i in range(itemcount):
			item = self.mainlist.GetNextItem(item,wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
			if item == (itemcount - 1):
				return
		item = itemcount
		item_next = 0
		while item_next >= 0:
			item_next = item - 1
			if self.mainlist.IsSelected(item_next) and (item_next < (itemcount - 1)):
				t = self.mainlist.GetItemText(item_next)
				self.mainlist.DeleteItem(item_next)
				self.mainlist.InsertStringItem(item, t, item)
				self.pipelineitems[item], self.pipelineitems[item_next] = self.pipelineitems[item_next], self.pipelineitems[item]
				self.mainlist.Select(item, 1)
				cmd = wx.ListEvent(wx.EVT_LIST_ITEM_SELECTED.typeId, self.mainlist.GetId())
				cmd.m_itemIndex	= item
				self.mainlist.GetEventHandler().ProcessEvent(cmd)
				break
			item = item_next
	def OnClickStart(self, event):
		OnClickStartAction(self, event)
	def OnClickPause(self, event):
		OnClickPauseAction(self, event)
	def OnClickStop(self, event):
		OnClickStopAction(self, event)
