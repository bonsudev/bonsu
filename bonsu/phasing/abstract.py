#############################################
##   Filename: phasing/abstract.py
##
##    Copyright (C) 2018 Marcus C. Newton
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
import numpy
import wx
from math import sqrt
from time import sleep
from ..operations.loadarray import NewArray
from ..operations.loadarray import _NewArrayPair, NewArrayPair
from ..operations.memory import GetVirtualMemory
from ..lib.prfftw import fftw_create_plan
from ..lib.prfftw import fftw_destroy_plan
from ..lib.prfftw import fftw_stride
from ..interface.common import FFTW_ESTIMATE, FFTW_MEASURE
from ..interface.common import FFTW_PATIENT, FFTW_EXHAUSTIVE
from ..interface.common import FFTW_TORECIP, FFTW_TOREAL, FFTW_PSLEEP
class PhaseAbstract():
	"""
	Phasing Base Class
	"""
	def __init__(self, parent=None):
		self.parent = parent
		self.seqdata = None
		self.expdata = None
		self.support = None
		self.mask = None
		self.rho_m1 = None
		self.rho_m2 = None
		self.beta = 0.9
		self.startiter = 0
		self.numiter = 0
		self.nthreads = 1
		self.__narrays__ = 5
		if self.parent != None:
			self.seqdata = parent.seqdata
			self.expdata = parent.expdata
			self.support = parent.support
			self.mask = parent.mask
			self.citer_flow = parent.citer_flow
			self.residual = parent.residual
			self.visual_amp_real = parent.visual_amp_real
			self.visual_amp_recip = parent.visual_amp_recip
			self.visual_phase_real = parent.visual_phase_real
			self.visual_phase_recip = parent.visual_phase_recip
			self.updatereal = self._updatereala
			self.updaterecip = self._updaterecipa
			self.updatelog = self._updateloga
			self.nthreads = parent.citer_flow[7]
		else:
			self.citer_flow = numpy.zeros((20), dtype=numpy.int32)
			self.residual = None
			self.visual_amp_real = numpy.zeros((1), dtype=numpy.double)
			self.visual_amp_recip = numpy.zeros((1), dtype=numpy.double)
			self.visual_phase_real = numpy.zeros((1), dtype=numpy.double)
			self.visual_phase_recip = numpy.zeros((1), dtype=numpy.double)
			self.updatereal = self._updaterealb
			self.updaterecip = self._updaterecipb
			self.updatelog = self._updatelogb
		self.update_count_real = 0
		self.update_count_recip = 0
		self.sos = 0.0
		self.res = 0.0
		self.algorithm = None
		self.plan = None
	def Algorithm(self):
		pass
	def DoIter(self):
		while self.citer_flow[1] == 1:
			sleep(FFTW_PSLEEP);
		self.rho_m1[:] = self.seqdata[:]
		fftw_stride(self.seqdata,self.seqdata,self.plan,FFTW_TORECIP,1)
		if self.citer_flow[5] > 0 and self.update_count_recip == self.citer_flow[5]:
			self.visual_amp_recip[:] = numpy.absolute(self.seqdata)
			if self.citer_flow[6] > 0:  self.visual_phase_recip[:] = numpy.angle(self.seqdata);
			self.update_count_recip = 0
			self.updaterecip()
		else:
			self.update_count_recip += 1
		self.SetRes()
		self.SetAmplitudes()
		fftw_stride(self.seqdata,self.seqdata,self.plan,FFTW_TOREAL,1)
		n = self.citer_flow[0]
		self.residual[n] = self.res/self.sos
		amp = numpy.absolute(self.seqdata)
		sos1 = numpy.sum(amp*amp)
		self.RSCons()
		amp = numpy.absolute(self.seqdata)
		sos2 = numpy.sum(amp*amp)
		norm = sqrt(sos1/sos2)
		self.seqdata[:] = norm*self.seqdata[:]
		if self.citer_flow[3] > 0 and self.update_count_real == self.citer_flow[3]:
			self.visual_amp_real[:] = numpy.absolute(self.seqdata)
			if self.citer_flow[6] > 0: self.visual_phase_real[:] = numpy.angle(self.seqdata);
			self.update_count_real = 0
			self.updatereal()
		else:
			self.update_count_real += 1
		self.updatelog()
		self.citer_flow[0] += 1
	def Phase(self):
		for i in range(self.startiter, self.startiter+self.numiter, 1):
			if self.citer_flow[1] == 2:
				self.DestroyPlan()
				break
			self.DoIter()
	def SetResidual(self):
		self.residual = numpy.zeros(self.startiter+self.numiter, dtype=numpy.double)
	def SetDimensions(self):
		self.nn = numpy.asarray( self.seqdata.shape, numpy.int32 )
		self.ndim = int(self.seqdata.ndim)
	def Prepare(self):
		"""
		Prepare algorithm.
		"""
		if self.MemoryIsShort():
			return True
		if self.parent != None:
			self.rho_m1 = NewArray(self.parent, *self.seqdata.shape)
		else:
			self.rho_m1 = numpy.empty_like(self.seqdata)
			self.SetResidual()
		self.SetDimensions()
		return False
	def PrepareCustom(self):
		"""
		Prepare algorithm using FFTW python interface.
		"""
		return self.Prepare2()
	def Prepare2(self):
		if self.Prepare():
			return True
		self.SetSOS()
		if self.plan == None:
			self.NewPlan()
		return False
	def MemoryIsShort(self):
		bytes1 = self.seqdata.size*self.seqdata.dtype.itemsize
		mbytes = bytes1 * self.__narrays__
		mavailbytes = GetVirtualMemory()
		mmsg = "Insufficient memory. Halting. %d bytes required. %d bytes available."%(mbytes,mavailbytes)
		if mbytes > mavailbytes:
			if self.parent != None:
				self.parent.ancestor.GetPage(0).queue_info.put(mmsg)
				self.parent.ancestor.GetPage(0).OnClickStop(None)
			else:
				self.citer_flow[1] = 2
				print(mmsg)
			return True
		else:
			return False
	def SetPlan(self, plan):
		self.plan = plan
	def NewPlan(self, flag=FFTW_MEASURE):
		data = self.rho_m1
		self.plan = fftw_create_plan(data,self.nthreads,FFTW_MEASURE)
	def GetPlan(self):
		return self.plan
	def DestroyPlan(self):
		fftw_destroy_plan(self.plan)
	def SetSOS(self):
		"""
		Set Sum of Squares.
		"""
		amp = numpy.absolute(self.expdata)
		if isinstance(self.mask, numpy.ndarray):
			self.sos = numpy.sum(amp*amp*numpy.real(self.mask))
		else:
			self.sos = numpy.sum(amp*amp)
	def GetSOS(self):
		"""
		Get Sum of Squares.
		"""
		return self.sos
	def SetRes(self):
		dif = numpy.absolute(self.seqdata) - numpy.absolute(self.expdata)
		if isinstance(self.mask, numpy.ndarray):
			self.res = numpy.sum(dif * dif * numpy.real(self.mask))
		else:
			self.res = numpy.sum(dif * dif)
	def GetRes(self):
		return self.res
	def SetAmplitudes(self):
		amp = numpy.absolute(self.expdata)
		phase = numpy.angle(self.seqdata)
		realmask = numpy.real(self.mask)
		unmask = realmask > 0.0
		if isinstance(self.mask, numpy.ndarray):
			self.seqdata[unmask] = amp[unmask]*numpy.cos(phase[unmask]) + 1j*amp[unmask]*numpy.sin(phase[unmask])
		else:
			self.seqdata[:] = amp*numpy.cos(phase) + 1j*amp*numpy.sin(phase)
	def RSCons(self):
		realsupport = numpy.real(self.support)
		nosupport = realsupport < 0.5
		self.seqdata[nosupport] = self.rho_m1[nosupport] - self.seqdata[nosupport] * self.beta
	def SetStartiter(self,startiter):
		"""
		Set the starting iteration number.
		"""
		self.startiter = startiter
		if self.parent == None:
			self.citer_flow[0] = self.startiter
	def SetNumiter(self,numiter):
		"""
		Set the number of iterations of the
		algorithm to perform.
		"""
		self.numiter = numiter
	def SetNumthreads(self,nthreads):
		"""
		Set the number of FFTW threads.
		"""
		self.nthreads = nthreads
		self.citer_flow[7] = self.nthreads
	def CleanData(self):
		self.seqdata = None
		self.expdata = None
		self.support = None
		self.mask = None
		self.rho_m1 = None
		self.rho_m2 = None
		self.visual_amp_real = None
		self.visual_amp_recip = None
		self.visual_phase_real = None
		self.visual_phase_recip = None
	def SetSeqdata(self,seqdata):
		"""
		Set the reconstruction data array.
		"""
		self.seqdata = seqdata
	def GetSeqdata(self):
		"""
		Get the reconstruction data array.
		"""
		return self.seqdata
	def SetExpdata(self,expdata):
		"""
		Set the raw experimental amplitude data array.
		"""
		self.expdata = expdata
	def GetExpdata(self):
		"""
		Get the raw experimental amplitude data array.
		"""
		return self.expdata
	def SetSupport(self,support):
		"""
		Set the support array.
		"""
		self.support = support
	def GetSupport(self):
		"""
		Get the support array.
		"""
		return self.support
	def SetMask(self,mask):
		"""
		Set the mask data array.
		"""
		self.mask = mask
	def GetMask(self):
		"""
		Set the mask data array.
		"""
		return self.mask
	def SetBeta(self, beta):
		"""
		Set beta relaxation parameter.
		"""
		self.beta = beta
	def GetBeta(self):
		"""
		Get beta relaxation parameter.
		"""
		return self.beta
	def _updatereala(self):
		wx.CallAfter(self.parent.ancestor.GetPage(1).UpdateReal,)
	def _updaterealb(self):
		pass
	def _updaterecipa(self):
		wx.CallAfter(self.parent.ancestor.GetPage(1).UpdateRecip,)
	def _updaterecipb(self):
		pass
	def _updateloga(self):
		try:
			n = self.citer_flow[0]
			res = self.parent.ancestor.GetPage(0).residual[n]
			string = "Iteration: %06d, Residual: %1.9f" %(n,res)
			self.parent.ancestor.GetPage(0).queue_info.put(string)
		except:
			pass
	def _updatelogb(self):
		try:
			n = self.citer_flow[0]
			res = self.residual[n]
			string = "Iteration: %06d, Residual: %1.9f" %(n,res)
			print(string)
		except:
			pass
	def Pause(self):
		"""
		Pause the reconstruction process.
		"""
		if self.citer_flow[1] == 0:
			self.citer_flow[1] = 1
	def Resume(self):
		"""
		Resume the reconstruction process.
		"""
		if self.citer_flow[1] != 0:
			self.citer_flow[1] = 0
	def Start(self):
		"""
		Start the reconstruction process.
		"""
		if self.citer_flow[1] == 0:
			if self.plan == None:
				self.Algorithm()
			else:
				self.Phase()
	def Stop(self):
		"""
		Stop the reconstruction process.
		"""
		self.citer_flow[1] = 2
class PhaseAbstractPC(PhaseAbstract):
	"""
	Phasing Partial Coherence Base Class
	"""
	def __init__(self, parent=None):
		PhaseAbstract.__init__(self, parent)
		self.parent = parent
		self.algorithm = None
		if self.parent != None:
			self.residualRL = parent.residualRL
			self.psf = parent.psf
			self.updatelog2 = self._updatelog2a
		else:
			self.residualRL = None
			self.psf = None
			self.updatelog2 = self._updatelog2b
		self.niterrlpre = 100
		self.niterrlpretmp = 0
		self.niterrl = 10
		self.niterrlinterval = 10
		self.gammaHWHM = 0.1
		self.ze = [0,0,0]
		self.reset_gamma = 0
		self.accel = 1
		self.__narrays__ = 14
	def SetResidualRL(self):
		self.residualRL = numpy.zeros(self.numiter, dtype=numpy.double)
	def SetPSF(self, psf):
		"""
		Set point-spread function from data array.
		"""
		self.psf = psf
	def GetPSF(self):
		"""
		Get point-spread function from data array.
		"""
		return self.psf
	def LorentzFillPSF(self):
		"""
		Create a point-spread function with Lorentz distribution.
		This will use the HWHM specified using SetGammaHWHM.
		"""
		from bonsu.lib.prfftw import lorentzftfill
		self.psf = numpy.empty_like(self.seqdata)
		lorentzftfill(self.psf, self.gammaHWHM)
	def SetNumiterRLpre(self, niterrlpre):
		"""
		Set the number of iterations before RL optimisation.
		"""
		if niterrlpre >= 0:
			self.niterrlpre = niterrlpre
		else:
			self.niterrlpre = 0
	def GetNumiterRLpre(self):
		"""
		Get the number of iterations before RL optimisation.
		"""
		return self.niterrlpre
	def SetNumiterRL(self, niterrl):
		"""
		Set the number of RL iterations.
		"""
		self.niterrl = niterrl
	def GetNumiterRL(self):
		"""
		Get the number of RL iterations.
		"""
		return self.niterrl
	def SetNumiterRLinterval(self, niterrlinterval):
		"""
		Set number of iterations between each RL optimisation cycle.
		"""
		self.niterrlinterval = niterrlinterval
	def GetNumiterRLinterval(self):
		"""
		Get number of iterations between each RL optimisation cycle.
		"""
		return self.niterrlinterval
	def SetGammaHWHM(self, gammaHWHM):
		"""
		Set the half-width half-maximum of the Lorentz distribution.
		This is utilised in the LorentzFillPSF method.
		"""
		self.gammaHWHM = gammaHWHM
	def GetGammaHWHM(self):
		"""
		Get the half-width half-maximum of the Lorentz distribution.
		"""
		return self.gammaHWHM
	def SetPSFZeroEnd(self, ze):
		"""
		Voxels upto a distance of [i,j,k] from the perimeter of the
		PSF array are set to zero. This can improve stability of
		the algorithm.
		"""
		self.ze = ze
	def GetPSFZeroEnd(self):
		"""
		Get zero voxels perimeter size.
		"""
		return self.ze
	def SetResetGamma(self, reset_gamma):
		self.reset_gamma = reset_gamma
	def GetResetGamma(self):
		return self.reset_gamma
	def SetAccel(self, accel):
		self.accel = accel
	def Prepare(self):
		if self.MemoryIsShort():
			return
		self.niterrlpretmp = self.niterrlpre
		self.nn=numpy.asarray( self.seqdata.shape, numpy.int32 )
		self.ndim=int(self.seqdata.ndim)
		self.nn2 = numpy.asarray( self.seqdata.shape, numpy.int32 )
		self.nn2[0] = self.nn[0] + 2*(self.nn[0]//8)
		self.nn2[1] = self.nn[1] + 2*(self.nn[1]//8)
		self.nn2[2] = self.nn[2] + 2*(self.nn[2]//8)
		if self.nn[0] == 1: self.nn2[0] = self.nn[0];
		if self.nn[1] == 1: self.nn2[1] = self.nn[1];
		if self.nn[2] == 1: self.nn2[2] = self.nn[2];
		if self.parent != None:
			self.rho_m1 = NewArray(self.parent, *self.seqdata.shape)
			self.pca_inten = NewArray(self.parent, *self.seqdata.shape)
			self.pca_rho_m1_ft = NewArray(self.parent, *self.seqdata.shape)
			self.pca_Idm_iter = NewArray(self.parent, *self.seqdata.shape)
			self.pca_Idmdiv_iter = NewArray(self.parent, *self.seqdata.shape)
			self.pca_IdmdivId_iter = NewArray(self.parent, *self.seqdata.shape)
			self.tmpdata1,self.tmpdata2 = NewArrayPair(self.parent, self.nn2[0],self.nn2[1],self.nn2[2])
			self.updatelog2 = self._updatelog2a
		else:
			self.rho_m1 = numpy.empty_like(self.seqdata)
			self.pca_inten = numpy.empty_like(self.seqdata)
			self.pca_rho_m1_ft = numpy.empty_like(self.seqdata)
			self.pca_Idm_iter = numpy.empty_like(self.seqdata)
			self.pca_Idmdiv_iter = numpy.empty_like(self.seqdata)
			self.pca_IdmdivId_iter = numpy.empty_like(self.seqdata)
			self.tmpdata1,self.tmpdata2 = _NewArrayPair(self.nn2[0],self.nn2[1],self.nn2[2])
			self.updatelog2 = self._updatelog2b
			self.SetResidual()
			self.SetResidualRL()
		self.SetDimensions()
	def CleanData(self):
		self.seqdata = None
		self.expdata = None
		self.support = None
		self.mask = None
		self.rho_m1 = None
		self.rho_m2 = None
		self.pca_inten = None
		self.pca_rho_m1_ft = None
		self.pca_Idm_iter = None
		self.pca_Idmdiv_iter = None
		self.pca_IdmdivId_iter = None
		self.tmpdata1 = None
		self.tmpdata2 = None
		self.visual_amp_real = None
		self.visual_amp_recip = None
		self.visual_phase_real = None
		self.visual_phase_recip = None
	def _updatelog2a(self):
		try:
			n = self.citer_flow[8]
			string = " R-L iteration: %03d, mean scaling factor: %1.6f" %(n,self.residualRL[0])
			self.parent.ancestor.GetPage(0).queue_info.put(string)
		except:
			pass
	def _updatelog2b(self):
		try:
			n = self.citer_flow[8]
			string = " R-L iteration: %03d, mean scaling factor: %1.6f" %(n,self.residualRL[0])
			print(string)
		except:
			pass
	def Algorithm(self):
		pass
