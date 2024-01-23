#############################################
##   Filename: phasing/SO2D.py
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
from math import sqrt
from time import sleep
from .abstract import PhaseAbstract
from .ShrinkWrap import ShrinkWrap
from ..lib.fftwlib import fftw_stride
from ..lib.fftwlib import FFTW_TORECIP, FFTW_TOREAL
from ..interface.common import FFTW_PSLEEP
class SO2D(PhaseAbstract):
	def __init__(self, parent=None):
		PhaseAbstract.__init__(self, parent)
		from ..lib.prutillib import sumofsqs
		from ..lib.prutillib import SOGradStep
		from ..lib.prutillib import SOMinMaxtau
		from ..lib.prutillib import SupportScaleAddArray
		self._sumofsqs = sumofsqs
		self._SOGradStep = SOGradStep
		self._SOMinMaxtau = SOMinMaxtau
		self._SupportScaleAddArray = SupportScaleAddArray
		self.alpha = 1.0
		self.epsilon = numpy.zeros((5),dtype=numpy.double)
		self.step = numpy.zeros((7),dtype=numpy.double)
		self.numsoiter  = 20
		self.reweightiter = 0
		self.dtaumax = 0.1
		self.dtaumin = 0.005
		self.psiexitratio = 0.01
		self.psiexiterror = 0.01
		self.psiresetratio = 0.05
		self.taumax = 2.5
		self.__narrays__ = 7
	def _updateloga(self):
		try:
			n = self.citer_flow[0]
			res = self.parent.ancestor.GetPage(0).residual[n]
			epsilon = self.epsilon
			string = "Iteration: %06d, Residual: %1.9f, Subproblem Error: %.2e, Step: %06.4f %06.4f" %(n,res,epsilon[1],epsilon[2],epsilon[3])
			self.parent.ancestor.GetPage(0).queue_info.put(string)
		except:
			pass
	def _updatelogb(self):
		try:
			n = self.citer_flow[0]
			res = self.residual[n]
			epsilon = self.epsilon
			string = "Iteration: %06d, Residual: %1.9f, Subproblem Error: %.2e, Step: %06.4f %06.4f" %(n,res,epsilon[1],epsilon[2],epsilon[3])
			print(string)
		except:
			pass
	def SetNumsoiter(self, numsoiter):
		"""
		Set total number of iterations performed when optimising the step length.
		"""
		self.numsoiter = numsoiter
	def GetNumsoiter(self):
		"""
		Get total number of iterations performed when optimising the step length.
		"""
		return self.numsoiter
	def SetReweightiter(self, reweightiter):
		"""
		Set iteration after which reweighting is applied.
		A negative value implies no reweighting.
		"""
		self.reweightiter = reweightiter
	def GetReweightiter(self):
		"""
		Get iteration after which reweighting is applied.
		A negative value implies no reweighting.
		"""
		return self.reweightiter
	def SetDtaumax(self, dtaumax):
		"""
		Set maximum amount by which the step can be incremented.
		"""
		self.dtaumax = dtaumax
	def GetDtaumax(self):
		"""
		Get maximum amount by which the step can be incremented.
		"""
		return self.dtaumax
	def SetDtaumin(self, dtaumin):
		"""
		Set minimum amount by which the step can be incremented.
		"""
		self.dtaumin = dtaumin
	def GetDtaumin(self):
		"""
		Get minimum amount by which the step can be incremented.
		"""
		return self.dtaumin
	def SetTaumax(self, taumax):
		"""
		Set maximum size for the total step length.
		"""
		self.taumax = taumax
	def GetTaumax(self):
		"""
		Get maximum size for the total step length.
		"""
		return self.taumax
	def SetPsiexitratio(self,psiexitratio):
		"""
		Set value below |psi|/|psi_0| that will halt step length optimisation.
		"""
		self.psiexitratio = psiexitratio
	def GetPsiexitratio(self):
		"""
		Get value below |psi|/|psi_0| that will halt step length optimisation.
		"""
		return self.psiexitratio
	def SetPsiexiterror(self,psiexiterror):
		"""
		Set value below (psi^(n+1) - psi^(n))/psi^(n) that will halt step length optimisation.
		"""
		self.psiexiterror = psiexiterror
	def GetPsiexiterror(self):
		"""
		Get value below (psi^(n+1) - psi^(n))/psi^(n) that will halt step length optimisation.
		"""
		return self.psiexiterror
	def SetPsiresetratio(self,psiresetratio):
		"""
		Set value above |psi|/|psi_0| that will reset the step length to that of the initial value.
		"""
		self.psiresetratio = psiresetratio
	def GetPsiresetratio(self):
		"""
		Get value above |psi|/|psi_0| that will reset the step length to that of the initial value.
		"""
		return self.psiresetratio
	def _Prepare(self):
		if self.parent != None:
			from ..operations.loadarray import NewArray
			if self.citer_flow[12] > 0:
				self.rho_m1 = NewArray(self.parent, *self.seqdata.shape, dtype=numpy.csingle)
				self.rho_m2 = NewArray(self.parent, *self.seqdata.shape, dtype=numpy.csingle)
				self.grad = NewArray(self.parent, *self.seqdata.shape, dtype=numpy.csingle)
			else:
				self.rho_m1 = NewArray(self.parent, *self.seqdata.shape, dtype=numpy.cdouble)
				self.rho_m2 = NewArray(self.parent, *self.seqdata.shape, dtype=numpy.cdouble)
				self.grad = NewArray(self.parent, *self.seqdata.shape, dtype=numpy.cdouble)
		else:
			self.rho_m1 = numpy.empty_like(self.seqdata)
			self.rho_m2 = numpy.empty_like(self.seqdata)
			self.grad = numpy.empty_like(self.seqdata)
			self.SetResidual()
		self.step[0] = self.dtaumax
		self.step[1] = self.dtaumin
		self.step[2] = self.psiexitratio
		self.step[3] = self.psiexiterror
		self.step[4] = self.psiresetratio
		self.step[5] = self.taumax
		self.step[6] = self.reweightiter
		self._psi = numpy.zeros((2), dtype = numpy.double)
		self._H = numpy.zeros((2,2), dtype = numpy.double)
		self._Hav = numpy.zeros((2,2), dtype = numpy.double)
		self._tau = numpy.zeros((2), dtype = numpy.double)
		self._tauav = numpy.zeros((2), dtype = numpy.double)
		self.algiter = 0
		self.SetDimensions()
	def DoIter(self):
		while self.citer_flow[1] == 1:
			sleep(FFTW_PSLEEP);
		self.rho_m2[:] = self.rho_m2[:]
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
		sos1 = self._sumofsqs(self.seqdata, self.nthreads)
		self._SOGradStep(self.seqdata, self.support, self.rho_m1, self.rho_m2, self.grad,\
							self.step, self.citer_flow, self.startiter ,self.nthreads)
		self._SOMinMaxtau(self.seqdata, self.support, self.rho_m1, self.rho_m2, self.grad,\
							self.expdata, self.mask, self.step, self.citer_flow, self.startiter,\
							self._tau, self._tauav, self._H, self._Hav, self._psi, self.algiter,\
							self.numsoiter, self.alpha, self.beta, self.plan, self.nthreads)
		self.epsilon[1] = sqrt(self._psi[0]*self._psi[0]+self._psi[1]*self._psi[1])/(self.seqdata.size)
		self.epsilon[2] = self._tau[0]; self.epsilon[3] = self._tau[1];
		self._SupportScaleAddArray(self.seqdata, self.support, self.rho_m1, self.rho_m2, self.grad,\
									self._tau, 1.0, 1.0, self.step, self.citer_flow, self.startiter, self.nthreads)
		sos2 = self._sumofsqs(self.seqdata, self.nthreads)
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
class SWSO2D(SO2D,ShrinkWrap):
	def __init__(self):
		SO2D.__init__(self)
		ShrinkWrap.__init__(self)
