#############################################
##   Filename: panelphase.py
##
##    Copyright (C) 2011 - 2023 Marcus C. Newton
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
import inspect
from queue import Queue
import copy
from . import subpanel
from .subpanel import *
from .action import *
from .common import getmaincollapseBitmap
from .common import getmainexpandBitmap
from .common import getmainhoverBitmap
from .common import getpipelineok24Bitmap
from .common import OptIconSize
from .common import CheckListCtrl
from .instance import GetInstanceObject
from .instance import SetInstanceObject
class PanelPhase(wx.Panel,wx.TreeCtrl,wx.App,Action):
	def __init__(self,parent):
		Action.__init__(self)
		self.ancestor = parent
		self.citer_flow = numpy.zeros((20), dtype=numpy.int32)
		self.pipeline_started = False
		self.pipelineitems=[]
		self.pipeline_exec_idx=0
		self.thread = None
		self.thread_register = Queue()
		self.queue_info = Queue()
		self.seqdata = None
		self.seqdata_max = 0.0
		self.seqdata_max_recip = 0.0
		self.seqdata_max_support = 1.0
		self.support = None
		self.mask = None
		self.residual = None
		self.psf = None
		self.residualRL = numpy.zeros((2), dtype=numpy.double)
		self.coordarray = None
		self.memory = {}
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
		self.splitter.SetMinimumPaneSize(400)
		self.panel1 = wx.Panel(self.splitter,  style=wx.NO_BORDER)
		self.panel2 = wx.Panel(self.splitter,  style=wx.NO_BORDER)
		self.maintree = wx.TreeCtrl(self.panel1, style=wx.TR_HAS_BUTTONS | wx.TR_HIDE_ROOT | wx.TR_LINES_AT_ROOT | wx.TR_SINGLE, size=(180,1))
		self.maintree.__collapsing = False
		self.maintree.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnExpColTreeItem)
		self.maintree.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnExpColTreeItem)
		self.treeroot = self.maintree.AddRoot('root')
		self.maintree.SetItemHasChildren(self.treeroot)
		self.visual =  self.maintree.AppendItem(self.treeroot,'Visual Tools')
		self.importtools =  self.maintree.AppendItem(self.treeroot,'Import Tools')
		self.exporttools =  self.maintree.AppendItem(self.treeroot,'Export Tools')
		self.operpre =  self.maintree.AppendItem(self.treeroot,'Functions')
		self.algs =  self.maintree.AppendItem(self.treeroot,'Phasing Algorithms')
		self.operpost =  self.maintree.AppendItem(self.treeroot,'Phasing Operations')
		self.maintree.SetItemHasChildren(self.visual, True)
		self.maintree.SetItemHasChildren(self.importtools, True)
		self.maintree.SetItemHasChildren(self.exporttools, True)
		self.maintree.SetItemHasChildren(self.operpre, True)
		self.maintree.SetItemHasChildren(self.algs, True)
		self.maintree.SetItemHasChildren(self.operpost, True)
		self.maintree.SetItemImage(self.visual, 0,  wx.TreeItemIcon_Normal)
		self.maintree.SetItemImage(self.importtools, 0,  wx.TreeItemIcon_Normal)
		self.maintree.SetItemImage(self.exporttools, 0,  wx.TreeItemIcon_Normal)
		self.maintree.SetItemImage(self.operpre, 0,  wx.TreeItemIcon_Normal)
		self.maintree.SetItemImage(self.algs, 0,  wx.TreeItemIcon_Normal)
		self.maintree.SetItemImage(self.operpost, 0,  wx.TreeItemIcon_Normal)
		self.treechilditems = []
		self.subpanel_items = []
		self.subpanel_members = inspect.getmembers(subpanel, inspect.isclass)
		for item in self.subpanel_members:
			if hasattr(item[1], 'treeitem'):
				self.subpanel_items.append(item[1].treeitem['name'])
				if item[1].treeitem['type'] == 'operpreview':
					self.treechilditems.append(self.maintree.AppendItem(self.visual,item[1].treeitem['name']))
				elif item[1].treeitem['type'] == 'importtools':
					self.treechilditems.append(self.maintree.AppendItem(self.importtools,item[1].treeitem['name']))
				elif item[1].treeitem['type'] == 'exporttools':
					self.treechilditems.append(self.maintree.AppendItem(self.exporttools,item[1].treeitem['name']))
				elif item[1].treeitem['type'] == 'operpre':
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
		self.maintree.Expand(self.visual)
		fontdc = wx.ScreenDC()
		fontdc.SetFont(self.font)
		fontw,fonth = fontdc.GetTextExtent(" ")
		mainlistchksize = fonth
		self.mainlist=CheckListCtrl(self.panel1, id=-1, bmpsize=(mainlistchksize,mainlistchksize), size=(180,1))
		self.mainlist.SetFont(self.font)
		okbmw,okbmh = getpipelineok24Bitmap().GetSize()
		self.ListColumnTick = self.mainlist.InsertColumn(0,'Enabled', width=(8+okbmw))
		self.ListColumn = self.mainlist.InsertColumn(1,'Pipeline of Operations')
		self.mainlist.Arrange()
		self.mainlist.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelectListItem)
		self.mainlist.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnRightDown)
		self.mainlist.Bind(wx.EVT_KEY_DOWN, self.OnKeyListItem)
		self.mainlist.Bind(wx.EVT_KEY_UP, self.OnKeyUpListItem)
		self.CurrentListItem = -1
		self.vbox1 = wx.BoxSizer(wx.VERTICAL)
		self.vbox1.Add((-1,200))
		self.spin_up = BitmapButtonNew(self.panel1, -1, getspinupBitmap(), size=(20, 50))
		self.spin_up.SetToolTipNew('Change item positon in list.')
		self.spin_down = BitmapButtonNew(self.panel1, -1, getspindownBitmap(), size=(20, 50))
		self.spin_down.SetToolTipNew('Change item positon in list.')
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
		buttonx = OptIconSize()
		buttonsize = (2*buttonx,2*buttonx)
		self.hbox_btn = wx.BoxSizer(wx.HORIZONTAL)
		self.button_start = BitmapButtonNew(self.panel3, -1, getstart48Bitmap(), size=buttonsize)
		self.button_start.SetToolTipNew('Start pipeline execution.')
		self.hbox_btn.Add(self.button_start)
		self.Bind(wx.EVT_BUTTON, self.OnClickStart,self.button_start)
		self.hbox_btn.Add((2, -1))
		self.button_pause = BitmapButtonNew(self.panel3, -1, getpause48Bitmap(), size=buttonsize)
		self.button_pause.SetToolTipNew('Pause pipeline execution.')
		self.hbox_btn.Add(self.button_pause)
		self.Bind(wx.EVT_BUTTON, self.OnClickPause,self.button_pause)
		self.hbox_btn.Add((2, -1))
		self.button_stop = BitmapButtonNew(self.panel3, -1, getstop48Bitmap(), size=buttonsize)
		self.button_stop.SetToolTipNew('Stop pipeline execution.')
		self.hbox_btn.Add(self.button_stop)
		self.Bind(wx.EVT_BUTTON, self.OnClickStop,self.button_stop)
		self.sbox1 = wx.StaticBox(self.panel3, label="Visualisation Options", style=wx.BORDER_DEFAULT)
		self.sbox1.SetFont(self.font)
		self.vbox_chk = wx.StaticBoxSizer(self.sbox1,wx.VERTICAL)
		self.hbox_chk1 = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox_chk2 = wx.BoxSizer(wx.HORIZONTAL)
		self.ctrlk = False
		rstext = 'Real'
		fstext = 'Fourier'
		sstext ='Support'
		dc = wx.ScreenDC()
		dc.SetFont(self.font)
		rstextw,rstexth = dc.GetTextExtent(rstext)
		fstextw,fstexth = dc.GetTextExtent(fstext)
		sstextw,sstexth = dc.GetTextExtent(sstext)
		rschkw =120
		fschkw =120
		sschkw =120
		if rstextw > rschkw-25: rschkw = rstextw+35;
		if fstextw > fschkw-25: fschkw = fstextw+35;
		if sstextw > sschkw-25: sschkw = sstextw+35;
		self.chkbox_amp_real = CheckBoxNew(self.panel3, -1, rstext, size=(rschkw, 25))
		self.chkbox_amp_real.SetFont(self.font)
		self.chkbox_amp_real.SetToolTipNew("Visualise")
		self.chkbox_amp_real.SetValue(True)
		self.amp_real_update_interval = SpinnerObject(self.panel3,"",65535,1,1,10,0,70)
		self.amp_real_update_interval.value.SetToolTipNew("Real space update interval")
		self.chkbox_amp_recip = CheckBoxNew(self.panel3, -1, fstext, size=(fschkw, 25))
		self.chkbox_amp_recip.SetFont(self.font)
		self.chkbox_amp_recip.SetToolTipNew("Visualise")
		self.chkbox_amp_recip.SetValue(False)
		self.amp_recip_update_interval = SpinnerObject(self.panel3,"",65535,1,1,10,0,70)
		self.amp_recip_update_interval.value.SetToolTipNew("Fourier space update interval")
		self.hbox_chk1.Add(self.chkbox_amp_real , flag=wx.ALIGN_LEFT |wx.LEFT, border=2)
		self.hbox_chk1.Add(self.amp_real_update_interval , flag=wx.ALIGN_LEFT |wx.LEFT, border=2)
		self.hbox_chk1.Add((20, -1))
		self.hbox_chk1.Add(self.chkbox_amp_recip , flag=wx.ALIGN_LEFT |wx.LEFT, border=2)
		self.hbox_chk1.Add(self.amp_recip_update_interval , flag=wx.ALIGN_LEFT |wx.LEFT, border=2)
		self.hbox_chk1.Add((5,-1))
		self.chkbox_support = CheckBoxNew(self.panel3, -1, sstext, size=(sschkw , 25))
		self.chkbox_support.SetFont(self.font)
		self.chkbox_support.SetToolTipNew("Visualise")
		self.chkbox_support.SetValue(True)
		self.support_update_interval = SpinnerObject(self.panel3,"",65535,1,1,10,0,70)
		self.support_update_interval.value.SetToolTipNew("Update interval")
		self.chkbox_phase = CheckBoxNew(self.panel3, -1, 'Phase', size=(150, 25))
		self.chkbox_phase.SetFont(self.font)
		self.chkbox_phase.SetToolTipNew("Visualise")
		self.chkbox_phase.SetValue(False)
		self.hbox_chk2.Add(self.chkbox_support , flag=wx.ALIGN_LEFT |wx.LEFT, border=2)
		self.hbox_chk2.Add(self.support_update_interval , flag=wx.ALIGN_LEFT |wx.LEFT, border=2)
		self.hbox_chk2.Add((20, -1))
		self.hbox_chk2.Add(self.chkbox_phase , flag=wx.ALIGN_LEFT |wx.LEFT, border=2)
		self.hbox_chk2.Add((20, -1))
		self.sbox2 = wx.StaticBox(self.panel3, label="Threads", style=wx.BORDER_DEFAULT)
		self.sbox2.SetFont(self.font)
		self.vbox_thrd = wx.StaticBoxSizer(self.sbox2,wx.VERTICAL)
		self.nthreads = SpinnerObject(self.panel3,"",65535,1,1,1,5,90)
		self.nthreads.value.SetToolTipNew("Maximum number of FFTW threads")
		self.nthreads.label.SetToolTipNew("Maximum number of FFTW threads")
		self.vbox_thrd.Add(self.nthreads , flag=wx.ALIGN_LEFT |wx.LEFT|wx.RIGHT, border=5)
		self.vbox_thrd.Add((-1,35))
		self.vbox_chk.Add(self.hbox_chk1)
		self.vbox_chk.Add(self.hbox_chk2)
		self.vbox_chk.Add((-1,5))
		self.hbox_btn.Add(self.vbox_chk, flag=wx.ALIGN_LEFT |wx.LEFT, border=40)
		self.hbox_btn.Add(self.vbox_thrd, flag=wx.ALIGN_LEFT |wx.LEFT|wx.RIGHT, border=5)
		self.panel3.SetSizer(self.hbox_btn)
		self.panel3.font = self.font
		self.vbox.Add(self.panel3, 0, flag=wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=5)
		self.SetSizer(self.vbox)
		self.Fit()
		self.Layout()
		self.Show()
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
		if itemtext in ['Visual Tools','Import Tools','Export Tools','Functions','Phasing Algorithms', 'Phasing Operations']:
			if self.maintree.IsExpanded(item):
				self.maintree.Collapse(item)
			else:
				self.maintree.Expand(item)
		if (item not in (self.visual,self.importtools,self.exporttools,self.operpre,self.algs,self.operpost)):
			mainlistidx = self.mainlist.InsertItem(itemcount,"")
			self.mainlist.CheckItem(mainlistidx)
			self.mainlist.SetItem(mainlistidx, 1, itemtext)
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
	def OnKeyUpListItem(self, event):
		keycode = event.GetKeyCode()
		if keycode == wx.WXK_CONTROL:
			self.ctrlk = False
		event.Skip()
	def OnKeyListItem(self, event):
		keycode = event.GetKeyCode()
		ukeycode = event.GetUnicodeKey()
		itemcount = self.mainlist.GetItemCount()
		if keycode == wx.WXK_CONTROL:
			self.ctrlk = True
			event.Skip()
		elif keycode == wx.WXK_DOWN and self.ctrlk:
			self.OnClickDown(None)
		elif keycode == wx.WXK_UP and self.ctrlk:
			self.OnClickUp(None)
		elif ukeycode != wx.WXK_NONE and ukeycode == 68  and self.ctrlk:
			self.OnItemDup(None)
		elif keycode == wx.WXK_DELETE and itemcount > 0:
			self.mainlist.DeleteItem(self.CurrentListItem)
			self.pipelineitems[self.CurrentListItem].Hide()
			self.pipelineitems.pop(self.CurrentListItem)
			if len(self.pipelineitems) == 0:
				self.menu_place_holder.Show()
			next = self.CurrentListItem - 1
			self.mainlist.SetItemState(next, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED )
		else:
			event.Skip()
	def OnSelectListItem(self, event):
		self.CurrentListItem = event.GetIndex()
		if self.menu_place_holder.IsShown():
			self.menu_place_holder.Hide()
		name = self.mainlist.GetItemText(event.GetIndex())
		for  i in range(len(self.pipelineitems)):
			if i == self.CurrentListItem: self.pipelineitems[i].Show();
			else : self.pipelineitems[i].Hide()
		self.Layout()
		self.panel2.Layout()
	def OnRightDown(self,event):
		item = self.mainlist.HitTest(event.GetPoint())[0]
		if item > -1:
			menu = wx.Menu()
			self.CurrentListItem = event.GetIndex()
			self.mainlist.SetItemState(self.CurrentListItem, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED )
			itemup = wx.MenuItem(menu, wx.ID_UP, "Move up (Ctrl + Up)")
			itemdel = wx.MenuItem(menu, wx.ID_DELETE, "Delete  (Del)")
			itemdup = wx.MenuItem(menu, wx.ID_DUPLICATE, "Duplicate (Ctrl + D)")
			itemdown = wx.MenuItem(menu, wx.ID_DOWN, "Move Down  (Ctrl + Down)")
			menu.Append(itemup)
			menu.Append(itemdel)
			menu.Append(itemdup)
			menu.Append(itemdown)
			self.Bind(wx.EVT_MENU, self.OnClickUp, itemup)
			self.Bind(wx.EVT_MENU, self.OnItemDel, itemdel)
			self.Bind(wx.EVT_MENU, self.OnItemDup, itemdup)
			self.Bind(wx.EVT_MENU, self.OnClickDown, itemdown)
			x,y = event.GetPoint().Get()
			mx,my = self.hbox1.GetSize()
			x= 3*mx/4
			self.PopupMenu( menu, (x,y))
	def OnItemDel(self, event):
		self.mainlist.DeleteItem(self.CurrentListItem)
		self.pipelineitems[self.CurrentListItem].Hide()
		self.pipelineitems.pop(self.CurrentListItem)
		if len(self.pipelineitems) == 0:
			self.menu_place_holder.Show()
		next = self.CurrentListItem - 1
		self.mainlist.SetItemState(next, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED )
	def OnItemDup(self, event):
		itemcount = self.mainlist.GetItemCount()
		if self.CurrentListItem < 0:
			return
		item_selected = -1
		for i in range(itemcount):
			if self.mainlist.IsSelected(i):
				item_selected = i
				break
		if item_selected > -1:
			item_new = item_selected + 1
			t = self.mainlist.GetItem(item_selected,1).GetText()
			instance = GetInstanceObject(self, item_selected)
			SetInstanceObject(self, instance, item_new, self.subpanel_items)
	def OnClickUp(self, event):
		itemcount = self.mainlist.GetItemCount()
		if self.CurrentListItem <= 0:
			return
		item_selected = -1
		for i in range(itemcount):
			if self.mainlist.IsSelected(i):
				item_selected = i
				break
		if item_selected > 0:
			item = item_selected-1
			item_next = item_selected
			t = self.mainlist.GetItem(item_next,1).GetText()
			ischecked = self.mainlist.IsChecked(item_next)
			self.mainlist.DeleteItem(item_next)
			mainlistidx = self.mainlist.InsertItem(item,"")
			if ischecked:
				self.mainlist.CheckItem(mainlistidx)
			self.mainlist.SetItem(mainlistidx, 1, t)
			self.mainlist.Select(item, 1)
			self.pipelineitems[item], self.pipelineitems[item_next] = self.pipelineitems[item_next], self.pipelineitems[item]
			cmd = wx.ListEvent(wx.EVT_LIST_ITEM_SELECTED.typeId, self.mainlist.GetId())
			cmd.SetIndex(item)
			self.mainlist.GetEventHandler().ProcessEvent(cmd)
	def OnClickDown(self, event):
		itemcount = self.mainlist.GetItemCount()
		if self.CurrentListItem < 0 or self.CurrentListItem == (itemcount - 1):
			return
		item_selected = -1
		for i in range(itemcount):
			if self.mainlist.IsSelected(i):
				item_selected = i
				break
		if item_selected < itemcount-1:
			item = item_selected+1
			item_next = item_selected
			t = self.mainlist.GetItem(item_next,1).GetText()
			ischecked = self.mainlist.IsChecked(item_next)
			self.mainlist.DeleteItem(item_next)
			mainlistidx = self.mainlist.InsertItem(item,"")
			if ischecked:
				self.mainlist.CheckItem(mainlistidx)
			self.mainlist.SetItem(mainlistidx, 1, t)
			self.pipelineitems[item], self.pipelineitems[item_next] = self.pipelineitems[item_next], self.pipelineitems[item]
			self.mainlist.Select(item, 1)
			cmd = wx.ListEvent(wx.EVT_LIST_ITEM_SELECTED.typeId, self.mainlist.GetId())
			cmd.SetIndex(item)
			self.mainlist.GetEventHandler().ProcessEvent(cmd)
