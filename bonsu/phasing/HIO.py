#############################################
##   Filename: phasing/HIO.py
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
class HIO(PhaseAbstract):
	"""
	Fienup's hybrid input-output (HIO) algorithm.
	"""
	def __init__(self, parent=None):
		PhaseAbstract.__init__(self, parent)
class SWHIO(HIO,ShrinkWrap):
	"""
	Fienup's hybrid input-output (HIO) algorithm.
	Shrink wrapped.
	"""
	def __init__(self):
		HIO.__init__(self)
		ShrinkWrap.__init__(self)
class HIOMask(PhaseAbstract):
	"""
	Fienup's hybrid input-output (HIO) algorithm with the addition of a Fourier space constraint mask.
	"""
	def __init__(self, parent=None):
		PhaseAbstract.__init__(self,parent)
		self.numiter_relax = 0
	def SetNumiterRelax(self,numiter_relax):
		self.numiter_relax = numiter_relax
	def GetNumiterRelax(self):
		return self.numiter_relax
class SWHIOMask(HIOMask,ShrinkWrap):
	"""
	Fienup's hybrid input-output (HIO) algorithm with the addition of a
	Fourier space constraint mask.
	Shrink wrapped.
	"""
	def __init__(self):
		HIOMask.__init__(self)
		ShrinkWrap.__init__(self)
class HIOPlus(PhaseAbstract):
	"""
	Fienup's hybrid input-output (HIO) algorithm with non-negativity constraint
	and with the addition of a Fourier space constraint mask.
	"""
	def __init__(self, parent=None):
		PhaseAbstract.__init__(self,parent)
		from ..lib.prutillib import rshiop
		self._rshiop = rshiop
	def RSCons(self):
		self._rshiop(self.seqdata, self.rho_m1, self.support, self.beta, self.nthreads)
class SWHIOPlus(HIOPlus,ShrinkWrap):
	"""
	Fienup's hybrid input-output (HIO) algorithm with non-negativity constraint
	and with the addition of a Fourier space constraint mask.
	Shrink wrapped.
	"""
	def __init__(self):
		HIOPlus.__init__(self)
		ShrinkWrap.__init__(self)
class PCHIO(PhaseAbstract):
	"""
	Fienup's hybrid input-output (HIO) algorithm with phase constraint
	and with the addition of a Fourier space constraint mask.
	"""
	def __init__(self, parent=None):
		PhaseAbstract.__init__(self,parent)
		from ..lib.prutillib import rspchio
		self._rspchio = rspchio
		self.phasemax = 3.1416
		self.phasemin = -3.1416
	def RSCons(self):
		self._rspchio(self.seqdata, self.rho_m1, self.support, self.beta, self.phasemax, self.phasemin, self.nthreads)
	def SetMaxphase(self, max):
		"""
		Set phase maximum.
		"""
		self.phasemax = max
	def GetMaxphase(self):
		"""
		Get phase maximum.
		"""
		return self.phasemax
	def SetMinphase(self, min):
		"""
		Set phase minimum.
		"""
		self.phasemin = min
	def GetMinphase(self):
		"""
		Get phase minimum.
		"""
		return self.phasemin
class SWPCHIO(PCHIO,ShrinkWrap):
	"""
	Fienup's hybrid input-output (HIO) algorithm with phase constraint
	and with the addition of a Fourier space constraint mask.
	Shrink wrapped.
	"""
	def __init__(self):
		PCHIO.__init__(self)
		ShrinkWrap.__init__(self)
class PGCHIO(PhaseAbstract):
	"""
	Fienup's hybrid input-output (HIO) algorithm with phase gradient constraint
	in the Q-vector direction with the addition of a Fourier space constraint mask.
	"""
	def __init__(self, parent=None):
		PhaseAbstract.__init__(self,parent)
		from ..lib.prutillib import rspgchio
		self._rspgchio = rspgchio
		self.phasemax = 3.1416
		self.phasemin = -3.1416
		self.q = [1.0,1.0,1.0]
	def RSCons(self):
		self._rspgchio(self.seqdata, self.rho_m1, self.support, self.tmpdata, self.beta, self.phasemax, self.phasemin, self.q[0], self.q[1], self.q[2], self.nthreads)
	def SetMaxphase(self, max):
		"""
		Set phase maximum.
		"""
		self.phasemax = max
	def GetMaxphase(self):
		"""
		Get phase maximum.
		"""
		return self.phasemax
	def SetMinphase(self, min):
		"""
		Set phase minimum.
		"""
		self.phasemin = min
	def GetMinphase(self):
		"""
		Get phase minimum.
		"""
		return self.phasemin
	def SetQ(self, q):
		"""
		Set Q-vector tuple
		"""
		self.q = q
	def GetQ(self):
		"""
		Get Q-vector tuple
		"""
		return self.q
	def _Prepare(self):
		if self.parent != None:
			from ..operations.loadarray import NewArray
			if self.citer_flow[12] > 0:
				self.rho_m1 = NewArray(self.parent, *self.seqdata.shape, dtype=numpy.csingle)
				self.tmpdata = NewArray(self.parent, *self.seqdata.shape, dtype=numpy.csingle)
			else:
				self.rho_m1 = NewArray(self.parent, *self.seqdata.shape, dtype=numpy.cdouble)
				self.tmpdata = NewArray(self.parent, *self.seqdata.shape, dtype=numpy.cdouble)
		else:
			self.rho_m1 = numpy.empty_like(self.seqdata)
			self.tmpdata = numpy.empty_like(self.seqdata)
			self.SetResidual()
		self.SetDimensions()
class SWPGCHIO(PGCHIO,ShrinkWrap):
	"""
	Fienup's hybrid input-output (HIO) algorithm with phase gradient constraint
	in the Q-vector direction with the addition of a Fourier space constraint mask.
	Shrink wrapped.
	"""
	def __init__(self):
		PGCHIO.__init__(self)
		ShrinkWrap.__init__(self)
class HIOMaskPC(PhaseAbstractPC):
	"""
	HIO Mask with Partial Coherence Optimisation.
	"""
	def __init__(self, parent=None):
		PhaseAbstractPC.__init__(self, parent)
class SWHIOMaskPC(HIOMaskPC,ShrinkWrap):
	"""
	HIO Mask with Partial Coherence Optimisation.
	Shrink wrapped.
	"""
	def __init__(self):
		HIOMaskPC.__init__(self)
		ShrinkWrap.__init__(self)
	def Start(self):
		self.SetNumiterRLpre(self.niterrlpretmp - self.startiter)
		if self.citer_flow[1] == 0:
			self.Phase()
