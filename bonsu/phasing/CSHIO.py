#############################################
##   Filename: phasing/CSHIO.py
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
class CSHIO(PhaseAbstract):
	"""
	Compressed Sensing HIO (CSHIO) algorithm.
	"""
	def __init__(self, parent=None):
		PhaseAbstract.__init__(self, parent)
		from ..lib.prutillib import sumofsqs
		from ..lib.prutillib import cshio_dp
		self._sumofsqs = sumofsqs
		self._cshio_dp = cshio_dp
		self.epsilon = numpy.zeros((2),dtype=numpy.double)
		self.cs_p  = 1.0
		self.cs_epsilon = 1.0
		self.cs_epsilon_min = 1e-6
		self.cs_d = 2.0
		self.cs_eta = 100.0
		self.relax = 0
		self.__narrays__ = 7
	def SetPnorm(self, p):
		"""
		Set p-norm of the Lebesgue space.
		"""
		self.cs_p = p
	def GetPnorm(self):
		"""
		Get p-norm of the Lebesgue space.
		"""
		return self.cs_p
	def SetEpsilon(self, epsilon):
		"""
		Set positive relaxation parameter (\epsilon) for the weighted p-norm.
		"""
		self.cs_epsilon = epsilon
	def GetEpsilon(self):
		"""
		Get positive relaxation parameter (\epsilon) for the weighted p-norm.
		"""
		return self.cs_epsilon
	def SetEpsilonmin(self, epsilonmin):
		"""
		Set minimum value that epsilon can take.
		"""
		self.cs_epsilon_min = epsilonmin
	def GetEpsilonmin(self):
		"""
		Set minimum value that epsilon can take.
		"""
		return self.cs_epsilon_min
	def SetDivisor(self, d):
		"""
		Set amount by which epsilon is divided when constraint is met.
		"""
		self.cs_d = d
	def GetDivisor(self):
		"""
		Get amount by which epsilon is divided when constraint is met.
		"""
		return self.cs_d
	def SetEta(self, eta):
		"""
		Set parameter in the divisor condition.
		"""
		self.cs_eta = eta
	def GetEta(self):
		"""
		Get parameter in the divisor condition.
		"""
		return self.cs_eta
	def SetRelax(self, relax):
		self.relax = relax
	def GetRelax(self):
		return self.relax
	def _Prepare(self):
		if self.parent != None:
			from ..operations.loadarray import NewArray
			if self.citer_flow[12] > 0:
				self.rho_m1 = NewArray(self.parent, *self.seqdata.shape, dtype=numpy.csingle)
			else:
				self.rho_m1 = NewArray(self.parent, *self.seqdata.shape, dtype=numpy.cdouble)
			self.rho_m2 = NewArray(self.parent, *self.seqdata.shape, dtype=numpy.cdouble)
			self.elp = NewArray(self.parent, *self.seqdata.shape, dtype=numpy.cdouble)
		else:
			self.rho_m1 = numpy.empty_like(self.seqdata)
			self.rho_m2 = numpy.empty_like(self.seqdata, dtype=numpy.cdouble)
			self.elp = numpy.empty_like(self.seqdata, dtype=numpy.cdouble)
			self.SetResidual()
		self.SetDimensions()
		self.epsilon[0] = self.cs_epsilon
		self.epsilon[1] = self.cs_epsilon_min
	def DoIter(self):
		while self.citer_flow[1] == 1:
			sleep(FFTW_PSLEEP);
		self.rho_m2[:] = self.rho_m1[:]
		norm2_n = numpy.sqrt(self._sumofsqs(self.seqdata, self.nthreads))
		norm2_n_m1 = numpy.sqrt(self._sumofsqs(self.rho_m1, self.nthreads))
		if numpy.fabs(norm2_n-norm2_n_m1) < numpy.sqrt(self.epsilon[0])/self.cs_eta and self.epsilon[0] > self.epsilon[1]:
			self.epsilon[0]  = self.epsilon[0] / self.cs_d
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
		if self.citer_flow[12] > 0:
			self._cshio_dp(self.rho_m1.astype(numpy.cdouble), self.rho_m2, self.elp, self.cs_p, self.epsilon[0], self.nthreads)
		else:
			self._cshio_dp(self.rho_m1, self.rho_m2, self.elp, self.cs_p, self.epsilon[0], self.nthreads)
		self.seqdata[:] = self.seqdata[:] - self.elp[:]
		self.RSCons()
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
class SWCSHIO(CSHIO,ShrinkWrap):
	"""
	Compressed Sensing HIO (CSHIO) algorithm.
	Shrink wrapped.
	"""
	def __init__(self):
		CSHIO.__init__(self)
		ShrinkWrap.__init__(self)
