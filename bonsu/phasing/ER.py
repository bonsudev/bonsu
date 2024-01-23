#############################################
##   Filename: phasing/ER.py
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
class ER(PhaseAbstract):
	"""
	Error Reduction (ER) algorithm.
	"""
	def __init__(self, parent=None):
		PhaseAbstract.__init__(self, parent)
		from ..lib.prutillib import rser
		self._rser = rser
	def RSCons(self):
		self._rser(self.seqdata, self.rho_m1, self.support, self.nthreads)
class SWER(ER,ShrinkWrap):
	"""
	Error Reduction (ER) algorithm.
	Shrink wrapped.
	"""
	def __init__(self):
		ER.__init__(self)
		ShrinkWrap.__init__(self)
class ERMask(PhaseAbstract):
	"""
	Error Reduction (ER) algorithm with the addition of a Fourier space constraint mask.
	"""
	def __init__(self, parent=None):
		PhaseAbstract.__init__(self, parent)
		from ..lib.prutillib import rser
		self._rser = rser
	def RSCons(self):
		self._rser(self.seqdata, self.rho_m1, self.support, self.nthreads)
class SWERMask(ERMask,ShrinkWrap):
	"""
	Error Reduction (ER) algorithm with the addition of a Fourier space constraint mask.
	Shrink wrapped.
	"""
	def __init__(self):
		ERMask.__init__(self)
		ShrinkWrap.__init__(self)
class POER(PhaseAbstract):
	"""
	Phase Only Error Reduction (POER) algorithm with the addition of a Fourier space constraint mask.
	"""
	def __init__(self, parent=None):
		PhaseAbstract.__init__(self, parent)
		from ..lib.prutillib import rspoer
		self._rspoer = rspoer
	def RSCons(self):
		self._rspoer(self.seqdata, self.rho_m1, self.support, self.nthreads)
class ERMaskPC(PhaseAbstractPC):
	"""
	ER Mask with Partial Coherence Optimisation algorithm.
	"""
	def __init__(self, parent=None):
		PhaseAbstractPC.__init__(self, parent)
		from ..lib.prutillib import rser
		self._rser = rser
	def RSCons(self):
		self._rser(self.seqdata, self.rho_m1, self.support, self.nthreads)
class SWERMaskPC(ERMaskPC,ShrinkWrap):
	"""
	ER Mask with Partial Coherence Optimisation algorithm.
	Shrink wrapped.
	"""
	def __init__(self):
		ERMaskPC.__init__(self)
		ShrinkWrap.__init__(self)
	def Start(self):
		self.SetNumiterRLpre(self.niterrlpretmp - self.startiter)
		if self.citer_flow[1] == 0:
			self.Phase()
