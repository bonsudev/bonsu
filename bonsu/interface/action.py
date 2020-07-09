#############################################
##   Filename: action.py
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
import numpy
from time import sleep
from threading import enumerate
from .subpanel import *
from .common import *
from ..operations.loadarray import LoadArray
from ..operations.loadarray import SaveArray
from ..operations.loadarray import NewArray
def OnClickStartAction(self, event):
	if self.pipeline_started == False:
		self.pipeline_started = True
		self.citer_flow[7] = int(self.nthreads.value.GetValue())
		self.pipeline_exec_idx = 0
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
		clean_init = 0
		self.total_iter = 0
		if len(self.pipelineitems) == 0:
			dlg = wx.MessageDialog(self, "There are no items in the pipeline. Please add items as needed.", "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			self.maintree.Enable(True)
			self.maintree.Refresh()
			self.mainlist.Enable(True)
			self.mainlist.Refresh()
			self.spin_up.Enable(True)
			self.spin_down.Enable(True)
			self.spin_up.Refresh()
			self.spin_down.Refresh()
			return
		for i in range(len(self.pipelineitems)):
			if self.mainlist.IsChecked(i):
				if self.pipelineitems[i].treeitem['type'] == 'algsstart' or self.pipelineitems[i].treeitem['type'] == 'operpost':
					self.pipelineitems[i].start_iter = self.total_iter
				elif self.pipelineitems[i].treeitem['type'] == 'algs':
					self.pipelineitems[i].start_iter = self.total_iter
					self.total_iter += int(self.pipelineitems[i].niter.value.GetValue())
		try:
			residual_length = self.residual.shape[0]
		except AttributeError:
			self.residual = numpy.zeros(self.total_iter, dtype=numpy.double)
		else:
			if self.total_iter != residual_length:
				self.residual = numpy.zeros(self.total_iter, dtype=numpy.double)
		for i in range(len(self.pipelineitems)):
			if self.mainlist.IsChecked(i):
				if self.pipelineitems[i].treeitem['type'] == 'algs':
					tmp_npy_array_path = self.pipelineitems[i].exp_amps.objectpath.GetValue()
					tmp_npy_array = None
					try:
						tmp_npy_array = LoadArray(self, tmp_npy_array_path)
					except:
						dlg = wx.MessageDialog(self, "Could not load array for sequence."+os.linesep+"Please check the log.", "Pipeline Message", wx.OK)
						dlg.ShowModal()
						dlg.Destroy()
						clean_init = 1
						break
					if self.seqdata is None:
						self.queue_info.put("Creating sequence data")
						try:
							self.seqdata =  NewArray(self, *tmp_npy_array.shape)
						except:
							clean_init = 1
							break
						SaveArray(self, "memorysequence", self.seqdata)
					elif tmp_npy_array.shape != self.seqdata.shape:
						dlg = wx.MessageDialog(self, "Array and sequence dimensions are inconsistent."+os.linesep+"You may need to start a new session.", "Pipeline Message", wx.OK)
						dlg.ShowModal()
						dlg.Destroy()
						clean_init = 1
						break
					tmp_npy_array = None
					if self.chkbox_phase.GetValue() == True:
						self.citer_flow[6] = 1
					else:
						self.citer_flow[6] = 0
					if self.chkbox_amp_real.GetValue() == True:
						if self.visual_amp_real is None:
							try:
								self.visual_amp_real =  NewArray(self, *self.seqdata.shape, type=1, val=1)
							except:
								clean_init = 1
								break
						self.citer_flow[3] = int(self.amp_real_update_interval.value.GetValue())
						if self.chkbox_phase.GetValue() == True:
							if self.visual_phase_real is None:
								try:
									self.visual_phase_real =  NewArray(self, *self.seqdata.shape, type=1, val=1)
								except:
									clean_init = 1
									break
						else:
							self.visual_phase_real = None
					else:
						self.visual_amp_real = None
						self.visual_phase_real = None
						self.citer_flow[3] = 0
					if self.chkbox_support.GetValue() == True:
						if self.visual_support is None:
							try:
								self.visual_support =  NewArray(self, *self.seqdata.shape, type=1, val=1)
							except:
								clean_init = 1
								break
						self.citer_flow[4] = int(self.support_update_interval.value.GetValue())
					else:
						self.visual_support = None
						self.citer_flow[4] = 0
					if self.chkbox_amp_recip.GetValue() == True:
						if self.visual_amp_recip is None:
							try:
								self.visual_amp_recip =  NewArray(self, *self.seqdata.shape, type=1, val=1)
							except:
								clean_init = 1
								break
						self.citer_flow[5] = int(self.amp_recip_update_interval.value.GetValue())
						if self.chkbox_phase.GetValue() == True:
							if self.visual_phase_recip is None:
								try:
									self.visual_phase_recip =  NewArray(self, *self.seqdata.shape, type=1, val=1)
								except:
									clean_init = 1
									break
						else:
							self.visual_phase_recip = None
					else:
						self.visual_amp_recip = None
						self.visual_phase_recip = None
						self.citer_flow[5] = 0
					break
		self.citer_flow[0] = 0
		self.citer_flow[1] = 0
		self.citer_flow[2] = 0
		if clean_init != 0:
			self.pipeline_started = False
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
			return
		def OrderedSequence(event):
			if self.citer_flow[1] == 2 or self.pipeline_started == False:
				self.sequence_timer.Stop()
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
				self.ancestor.GetPage(2).data_poll_timer.Stop()
				if self.citer_flow[1] < 2:
					self.queue_info.put("Pipeline Complete.")
				self.ancestor.GetPage(4).UpdateLog(None)
				return
			if self.pipeline_exec_idx < len(self.pipelineitems):
				object = self.pipelineitems[self.pipeline_exec_idx]
				if self.mainlist.IsChecked(self.pipeline_exec_idx):
					if hasattr(object, 'treeitem') and self.thread_register.empty():
						if object.treeitem['type'] == 'operpreview':
							self.pipeline_exec_idx += 1
						elif object.treeitem['type'] == 'operpre' or object.treeitem['type'] == 'importtools' or object.treeitem['type'] == 'exporttools':
							def RunUnthreaded(objectsequence, self, object):
								objectsequence(self, object)
								self.thread_register.get()
							self.thread_register.put(1)
							thd = threading.Thread(target=RunUnthreaded, args=(object.sequence, self, object))
							thd.daemon = True
							thd.start()
							self.pipeline_exec_idx += 1
						elif (object.treeitem['type'] == 'algs' or object.treeitem['type'] == 'algsstart'):
							object.sequence(self,object)
							self.pipeline_exec_idx += 1
						elif object.treeitem['type'] == 'operpost':
							object.sequence(self,object)
							self.pipeline_exec_idx += 1
				else:
					self.pipeline_exec_idx += 1
			elif (self.pipeline_exec_idx == len(self.pipelineitems) and (self.citer_flow[0] == self.total_iter or self.total_iter == 0) and self.thread_register.empty()):
				self.pipeline_started = False
		self.ancestor.GetPage(4).data_poll_timer.Start(1000)
		if clean_init == 0:
			self.sequence_timer = wx.Timer(self)
			self.Bind(wx.EVT_TIMER, OrderedSequence, self.sequence_timer)
			self.sequence_timer.Start(1000)
			if self.total_iter > 0 :
				self.ancestor.GetPage(2).data_poll_timer.Start(1000)
		else:
			self.pipeline_started = False
			return
def OnClickPauseAction(self, event):
	if self.pipeline_started == True:
		if self.citer_flow[1] == 0:
			self.citer_flow[1] = 1
			self.button_pause.SetBitmapLabel(getpause482Bitmap())
			self.ancestor.GetPage(1).button_pause.SetBitmapLabel(getpause2Bitmap())
			try:
				self.sequence_timer.Stop()
				self.ancestor.GetPage(2).data_poll_timer.Stop()
				self.ancestor.GetPage(4).data_poll_timer.Stop()
			except:
				pass
		else:
			self.citer_flow[1] = 0
			self.button_pause.SetBitmapLabel(getpause48Bitmap())
			self.ancestor.GetPage(1).button_pause.SetBitmapLabel(getpauseBitmap())
			try:
				self.sequence_timer.Start(1000)
				self.ancestor.GetPage(4).data_poll_timer.Start(1000)
				if self.total_iter > 0:
					self.ancestor.GetPage(2).data_poll_timer.Start(1000)
			except:
				pass
def OnClickStopAction(self, event):
	if self.pipeline_started == True:
		if self.citer_flow[1] == 1:
			self.sequence_timer.Start(1000)
			self.ancestor.GetPage(4).data_poll_timer.Start(1000)
			if self.total_iter > 0:
				self.ancestor.GetPage(2).data_poll_timer.Start(1000)
		if self.citer_flow[1] < 2:
			self.citer_flow[1] = 2
			self.pipeline_started = False
			self.button_pause.SetBitmapLabel(getpause48Bitmap())
			self.ancestor.GetPage(1).button_pause.SetBitmapLabel(getpauseBitmap())
			self.citer_flow[3] = 0
			self.citer_flow[4] = 0
			self.citer_flow[5] = 0
			def ThreadClean(self):
				while len(enumerate()) > 2:
					sleep(0.1)
				wx.CallAfter(self.OnClickFinal,)
			self.thread = threading.Thread(target=ThreadClean, args=(self,))
			self.thread.daemon = True
			self.thread.start()
def OnClickFinalAction(self):
	self.sequence_timer.Stop()
	self.ancestor.GetPage(2).data_poll_timer.Stop()
	self.ancestor.GetPage(4).data_poll_timer.Stop()
	self.maintree.Enable(True)
	self.maintree.Refresh()
	self.mainlist.Enable(True)
	self.mainlist.Refresh()
	self.spin_up.Enable(True)
	self.spin_down.Enable(True)
	self.spin_up.Refresh()
	self.spin_down.Refresh()
	for i in range(len(self.pipelineitems)):
		self.pipelineitems[i].Enable(True)
		self.pipelineitems[i].Refresh()
	self.queue_info.put("Sequence halted.")
	self.queue_info.put("Pipeline Complete.")
	self.ancestor.GetPage(4).UpdateLog(None)
