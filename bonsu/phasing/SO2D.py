#############################################
##   Filename: phasing/SO2D.py
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
class SO2D(PhaseAbstract):
	def __init__(self, parent=None):
		PhaseAbstract.__init__(self, parent)
		from ..lib.prfftw import so2dmask
		self.algorithm = so2dmask
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
	def Prepare(self):
		if self.parent != None:
			from ..operations.loadarray import NewArray
			self.rho_m1 = NewArray(self.parent, *self.seqdata.shape)
			self.rho_m2 = NewArray(self.parent, *self.seqdata.shape)
			self.grad = NewArray(self.parent, *self.seqdata.shape)
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
		self.SetDimensions()
	def Algorithm(self):
		self.algorithm(self.seqdata,self.expdata,self.support,self.mask,\
			self.alpha,self.beta,self.startiter,self.numiter,self.step,self.numsoiter,\
			self.epsilon,self.rho_m1,self.rho_m2,self.grad,\
			self.residual,self.citer_flow,self.visual_amp_real,self.visual_phase_real,\
			self.visual_amp_recip,self.visual_phase_recip,\
			self.updatereal,self.updaterecip,self.updatelog)
class SWSO2D(SO2D,ShrinkWrap):
	def __init__(self):
		SO2D.__init__(self)
		ShrinkWrap.__init__(self)
