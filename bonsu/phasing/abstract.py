#############################################
##   Filename: phasing/abstract.py
##
##    Copyright (C) 2011 - 2024 Marcus C. Newton
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
from ..operations.loadarray import NewArrayPair
from ..operations.memory import GetVirtualMemory
from ..interface.common import FFTW_PSLEEP
from ..lib.fftwlib import FFTW_ESTIMATE, FFTW_MEASURE
from ..lib.fftwlib import FFTW_PATIENT, FFTW_EXHAUSTIVE
from ..lib.fftwlib import FFTW_TORECIP, FFTW_TOREAL
from ..lib.fftwlib import fftw_createplan as fftw_create_plan
from ..lib.fftwlib import fftw_destroyplan as fftw_destroy_plan
from ..lib.fftwlib import fftw_stride
from ..lib.fftwlib import fftw_create_plan_pair
from ..lib.prutillib import residual, updateamps, sumofsqs, rshio
from ..lib.prutillib import wrap_nomem
from ..lib.prutillib import conv_nmem_nplan
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
		sos1 = sumofsqs(self.seqdata, self.nthreads)
		self.RSCons()
		sos2 = sumofsqs(self.seqdata, self.nthreads)
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
	def _Prepare(self):
		"""
		Prepare algorithm.
		"""
		if self.MemoryIsShort():
			return True
		if self.parent != None:
			if self.citer_flow[12] > 0:
				self.rho_m1 = NewArray(self.parent, *self.seqdata.shape, dtype=numpy.csingle)
			else:
				self.rho_m1 = NewArray(self.parent, *self.seqdata.shape, dtype=numpy.cdouble)
		else:
			self.rho_m1 = numpy.empty_like(self.seqdata)
			self.SetResidual()
		self.SetDimensions()
		return False
	def PrepareCustom(self):
		"""
		Prepare algorithm using FFTW python interface.
		"""
		return self.Prepare()
	def Prepare(self):
		if self._Prepare():
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
		self.res = residual(self.seqdata, self.expdata, self.mask, self.nthreads)
	def GetRes(self):
		return self.res
	def SetAmplitudes(self):
		updateamps(self.seqdata, self.expdata, self.mask, self.nthreads)
	def RSCons(self):
		rshio(self.seqdata, self.rho_m1, self.support, self.beta, self.nthreads)
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
		self.gamma_count = 0
		self.itnsty_sum = 0.0
		self.gamma_sum = 0.0
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
		from ..lib.prutillib import lorentz_ft_fill
		self.psf = numpy.empty_like(self.seqdata, dtype=numpy.cdouble)
		lorentz_ft_fill(self.psf, self.gammaHWHM, self.nthreads)
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
	def NewPlan(self, flag=FFTW_MEASURE):
		data = self.rho_m1
		data1 = self.tmpdata1
		data2 = self.tmpdata2
		self.plan = fftw_create_plan(data,self.nthreads,FFTW_MEASURE)
		self.planpair = fftw_create_plan_pair(data1,data2,self.nthreads,FFTW_MEASURE)
	def MaskGamma(self, pca_gamma_ft):
		shape = pca_gamma_ft.shape
		idx = []
		for i in range( len(shape) ):
			st = (shape[i] - self.ze[i])//2
			ed = st + self.ze[i]
			idx.append(numpy.s_[st, ed])
		pca_gamma_ft[idx] = 0.0
	def _Prepare(self):
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
			if self.citer_flow[12] > 0:
				self.rho_m1 = NewArray(self.parent, *self.seqdata.shape, dtype=numpy.csingle)
			else:
				self.rho_m1 = NewArray(self.parent, *self.seqdata.shape, dtype=numpy.cdouble)
			self.pca_inten = NewArray(self.parent, *self.seqdata.shape)
			self.pca_rho_m1_ft = NewArray(self.parent, *self.seqdata.shape)
			self.pca_Idm_iter = NewArray(self.parent, *self.seqdata.shape)
			self.pca_Idmdiv_iter = NewArray(self.parent, *self.seqdata.shape)
			self.pca_IdmdivId_iter = NewArray(self.parent, *self.seqdata.shape)
			self.tmpdata1,self.tmpdata2 = NewArrayPair(self.parent, self.nn2[0],self.nn2[1],self.nn2[2])
			self.updatelog2 = self._updatelog2a
		else:
			self.rho_m1 = numpy.empty_like(self.seqdata)
			self.pca_inten = numpy.empty_like(self.seqdata, dtype=numpy.cdouble)
			self.pca_rho_m1_ft = numpy.empty_like(self.seqdata, dtype=numpy.cdouble)
			self.pca_Idm_iter = numpy.empty_like(self.seqdata, dtype=numpy.cdouble)
			self.pca_Idmdiv_iter = numpy.empty_like(self.seqdata, dtype=numpy.cdouble)
			self.pca_IdmdivId_iter = numpy.empty_like(self.seqdata, dtype=numpy.cdouble)
			self.tmpdata1 = numpy.empty((self.nn2[0],self.nn2[1],self.nn2[2]), dtype=numpy.cdouble)
			self.tmpdata2 = numpy.empty((self.nn2[0],self.nn2[1],self.nn2[2]), dtype=numpy.cdouble)
			self.updatelog2 = self._updatelog2b
			self.SetResidual()
			self.SetResidualRL()
		self.SetDimensions()
	def Phase(self):
		self.gamma_count = self.niterrlinterval + 1
		wrap_nomem(self.psf, self.tmpdata1, 1)
		self.gamma_sum = numpy.sum(numpy.abs(self.psf))
		self.psf[:] = self.psf / self.gamma_sum
		self.MaskGamma(self.psf)
		for i in range(self.startiter, self.startiter+self.numiter, 1):
			if self.citer_flow[1] == 2:
				self.DestroyPlan()
				break
			self.DoIter()
		wrap_nomem(self.psf, self.tmpdata1, -1)
	def MakeIdIter(self, rho, rhom1, pca_Id_iter):
		pca_Id_iter.real[:] = 2.0*rho.real*rho.real + 2.0*rho.imag*rho.imag - rhom1.real*rhom1.real - rhom1.imag*rhom1.imag
		pca_Id_iter.imag[:] = 0.0
	def DivideIIdIter(self, expdata, pca_Idm_iter, pca_Idmdiv_iter):
		inten = expdata.real*expdata.real + expdata.imag*expdata.imag
		divis = pca_Idm_iter.real*pca_Idm_iter.real + pca_Idm_iter.imag*pca_Idm_iter.imag
		pca_Idmdiv_iter.real[:] = inten*pca_Idm_iter.real/divis
		pca_Idmdiv_iter.imag[:] = - inten*pca_Idm_iter.imag/divis
	def SetPCAmplitudes(self):
		self.pca_inten.real[:] = self.seqdata.real*self.seqdata.real + self.seqdata.imag*self.seqdata.imag
		self.pca_inten.imag[:] = 0.0
		wrap_nomem(self.pca_inten, self.tmpdata1, -1)
		wrap_nomem(self.psf, self.tmpdata1, -1)
		conv_nmem_nplan(self.pca_inten, self.psf, self.tmpdata1, self.tmpdata2, self.planpair, self.nthreads)
		wrap_nomem(self.pca_inten, self.tmpdata1, 1)
		wrap_nomem(self.psf, self.tmpdata1, 1)
		expamp = numpy.absolute(self.expdata)
		amp = numpy.absolute(self.seqdata)
		phase = numpy.angle(self.seqdata)
		pcamp = numpy.sqrt(numpy.absolute(self.pca_inten))
		self.seqdata.real[:] = (expamp*amp/pcamp)*numpy.cos(phase)
		self.seqdata.imag[:] = (expamp*amp/pcamp)*numpy.sin(phase)
	def DoRLIter(self):
		self.pca_Idmdiv_iter[:] = 0.0
		self.MakeIdIter(self.seqdata, self.pca_rho_m1_ft, self.pca_Idm_iter)
		self.itnsty_sum = numpy.sum(numpy.absolute(self.pca_Idm_iter))
		self.pca_IdmdivId_iter[:] = self.pca_Idm_iter[:]
		self.pca_IdmdivId_iter[:] = numpy.conjugate(numpy.flip(self.pca_IdmdivId_iter, axis=numpy.arange(self.pca_IdmdivId_iter.ndim)))
		wrap_nomem(self.pca_Idm_iter, self.tmpdata1, -1)
		wrap_nomem(self.psf, self.tmpdata1, -1)
		conv_nmem_nplan(self.pca_Idm_iter, self.psf, self.tmpdata1, self.tmpdata2, self.planpair, self.nthreads)
		wrap_nomem(self.pca_Idm_iter, self.tmpdata1, 1)
		wrap_nomem(self.psf, self.tmpdata1, 1)
		self.DivideIIdIter(self.expdata, self.pca_Idm_iter, self.pca_Idmdiv_iter)
		wrap_nomem(self.pca_IdmdivId_iter, self.tmpdata1, -1)
		wrap_nomem(self.pca_Idmdiv_iter, self.tmpdata1, -1)
		conv_nmem_nplan(self.pca_IdmdivId_iter, self.pca_Idmdiv_iter, self.tmpdata1, self.tmpdata2, self.planpair, self.nthreads)
		wrap_nomem(self.pca_IdmdivId_iter, self.tmpdata1, 1)
		wrap_nomem(self.pca_Idmdiv_iter, self.tmpdata1, 1)
		self.pca_IdmdivId_iter[:] = self.pca_IdmdivId_iter / self.itnsty_sum
		self.pca_IdmdivId_iter[:] = numpy.power(self.pca_IdmdivId_iter, self.accel, dtype=numpy.cdouble)
		self.psf[:] = self.psf * self.pca_IdmdivId_iter
		self.MaskGamma(self.psf)
		self.residualRL[0] = numpy.sum(numpy.absolute(self.pca_IdmdivId_iter)) / self.seqdata.size
		self.updatelog2()
		self.citer_flow[8] += 1
		self.gamma_sum = numpy.sum(numpy.absolute(self.psf))
		self.psf[:] = self.psf / self.gamma_sum
	def DoIter(self):
		while self.citer_flow[1] == 1:
			sleep(FFTW_PSLEEP)
		self.rho_m1[:] = self.seqdata[:]
		fftw_stride(self.seqdata,self.seqdata,self.plan,FFTW_TORECIP,1)
		if( (self.citer_flow[0] - self.startiter+1) == self.niterrlpre ):
			self.pca_rho_m1_ft[:] = self.seqdata[:]
		if( self.gamma_count > self.niterrlinterval and (self.citer_flow[0] - self.startiter+1) > self.niterrlpre):
			if self.reset_gamma > 0:
				self.LorentzFillPSF()
				wrap_nomem(self.psf, self.tmpdata1, 1)
				self.gamma_sum = numpy.sum(numpy.abs(self.psf))
				self.psf[:] = self.psf / self.gamma_sum
				self.MaskGamma(self.psf)
			self.citer_flow[8] = 0
			for i in range(0, self.niterrl, 1):
				if( self.citer_flow[1] == 2 ):
					break
				self.DoRLIter()
			self.gamma_count = 1
			self.pca_rho_m1_ft[:] = self.seqdata[:]
		if self.citer_flow[5] > 0 and self.update_count_recip == self.citer_flow[5]:
			self.visual_amp_recip[:] = numpy.absolute(self.seqdata)
			if self.citer_flow[6] > 0:  self.visual_phase_recip[:] = numpy.angle(self.seqdata);
			self.update_count_recip = 0
			self.updaterecip()
		else:
			self.update_count_recip += 1
		self.SetRes()
		if (self.citer_flow[0] - self.startiter+1) > self.niterrlpre:
			self.SetPCAmplitudes()
		else:
			self.SetAmplitudes()
		fftw_stride(self.seqdata,self.seqdata,self.plan,FFTW_TOREAL,1)
		n = self.citer_flow[0]
		self.residual[n] = self.res/self.sos
		sos1 = sumofsqs(self.seqdata, self.nthreads)
		self.RSCons()
		sos2 = sumofsqs(self.seqdata, self.nthreads)
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
		self.gamma_count += 1
	def DestroyPlan(self):
		fftw_destroy_plan(self.plan)
		fftw_destroy_plan(self.planpair)
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
