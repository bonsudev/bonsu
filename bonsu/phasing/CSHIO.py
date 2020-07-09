#############################################
##   Filename: phasing/CSHIO.py
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
from .abstract import PhaseAbstract
from .ShrinkWrap import ShrinkWrap
class CSHIO(PhaseAbstract):
	"""
	Compressed Sensing HIO (CSHIO) algorithm.
	"""
	def __init__(self, parent=None):
		PhaseAbstract.__init__(self, parent)
		from ..lib.prfftw import cshio
		self.algorithm = cshio
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
	def Prepare(self):
		if self.parent != None:
			from ..operations.loadarray import NewArray
			self.rho_m1 = NewArray(self.parent, *self.seqdata.shape)
			self.rho_m2 = NewArray(self.parent, *self.seqdata.shape)
			self.elp = NewArray(self.parent, *self.seqdata.shape)
		else:
			self.rho_m1 = numpy.empty_like(self.seqdata)
			self.rho_m2 = numpy.empty_like(self.seqdata)
			self.elp = numpy.empty_like(self.seqdata)
			self.SetResidual()
		self.SetDimensions()
		self.epsilon[0] = self.cs_epsilon
		self.epsilon[1] = self.cs_epsilon_min
	def Algorithm(self):
		self.algorithm(self.seqdata,self.expdata,self.support,self.mask,\
			self.beta,self.startiter,self.numiter,self.ndim,\
			self.cs_p,self.epsilon,self.cs_d,self.cs_eta,self.relax,\
			self.rho_m1,self.rho_m2,self.elp,self.nn,self.residual,self.citer_flow,\
			self.visual_amp_real,self.visual_phase_real,self.visual_amp_recip,self.visual_phase_recip,\
			self.updatereal,self.updaterecip,self.updatelog)
class SWCSHIO(CSHIO,ShrinkWrap):
	"""
	Compressed Sensing HIO (CSHIO) algorithm.
	Shrink wrapped.
	"""
	def __init__(self):
		CSHIO.__init__(self)
		ShrinkWrap.__init__(self)
