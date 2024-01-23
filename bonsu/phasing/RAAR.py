#############################################
##   Filename: phasing/RAAR.py
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
from .abstract import PhaseAbstract
from .abstract import PhaseAbstractPC
from .ShrinkWrap import ShrinkWrap
class RAAR(PhaseAbstract):
	"""
	Relaxed Average Alternating Reflection (RAAR) algorithm.
	"""
	def __init__(self, parent=None):
		PhaseAbstract.__init__(self, parent)
		from ..lib.prutillib import rsraar
		self._rsraar = rsraar
	def RSCons(self):
		self._rsraar(self.seqdata, self.rho_m1, self.support, self.beta, self.nthreads)
		self.numiter_relax = 0
	def SetNumiterRelax(self,numiter_relax):
		self.numiter_relax = numiter_relax
	def GetNumiterRelax(self):
		return self.numiter_relax
class SWRAAR(RAAR,ShrinkWrap):
	"""
	Relaxed Average Alternating Reflection (RAAR) algorithm.
	Shrink wrapped.
	"""
	def __init__(self):
		RAAR.__init__(self)
		ShrinkWrap.__init__(self)
class RAARPC(PhaseAbstractPC):
	"""
	RAAR Mask with Partial Coherence Optimisation algorithm.
	"""
	def __init__(self, parent=None):
		PhaseAbstractPC.__init__(self, parent)
		from ..lib.prutillib import rsraar
		self._rsraar = rsraar
	def RSCons(self):
		self._rsraar(self.seqdata, self.rho_m1, self.support, self.beta, self.nthreads)
class SWRAARPC(RAARPC,ShrinkWrap):
	"""
	RAAR Mask with Partial Coherence Optimisation algorithm.
	Shrink wrapped.
	"""
	def __init__(self):
		RAARPC.__init__(self)
		ShrinkWrap.__init__(self)
	def Start(self):
		self.SetNumiterRLpre(self.niterrlpretmp - self.startiter)
		if self.citer_flow[1] == 0:
			self.Phase()
