#############################################
##   Filename: phasing/HIO.py
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
from .abstract import PhaseAbstractPC
from .ShrinkWrap import ShrinkWrap
class HIO(PhaseAbstract):
	"""
	Fienup's hybrid input-output (HIO) algorithm.
	"""
	def __init__(self, parent=None):
		PhaseAbstract.__init__(self, parent)
		from ..lib.prfftw import hio
		self.algorithm = hio
	def Algorithm(self):
		self.algorithm(self.seqdata,self.expdata,self.support,\
		self.beta,self.startiter,self.numiter,self.ndim,self.rho_m1,self.nn,self.residual,self.citer_flow,\
		self.visual_amp_real,self.visual_phase_real,self.visual_amp_recip,self.visual_phase_recip,\
		self.updatereal,self.updaterecip,self.updatelog)
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
		from ..lib.prfftw import hiomask
		self.algorithm = hiomask
		self.numiter_relax = 0
	def SetNumiterRelax(self,numiter_relax):
		self.numiter_relax = numiter_relax
	def GetNumiterRelax(self):
		return self.numiter_relax
	def Algorithm(self):
		self.algorithm(self.seqdata,self.expdata,self.support,self.mask,\
		self.beta,self.startiter,self.numiter,self.ndim,self.rho_m1,self.nn,self.residual,self.citer_flow,\
		self.visual_amp_real,self.visual_phase_real,self.visual_amp_recip,self.visual_phase_recip,\
		self.updatereal,self.updaterecip,self.updatelog,self.numiter_relax)
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
		from ..lib.prfftw import hioplus
		self.algorithm = hioplus
	def Algorithm(self):
		self.algorithm(self.seqdata,self.expdata,self.support,self.mask,\
		self.beta,self.startiter,self.numiter,self.ndim,self.rho_m1,self.nn,self.residual,self.citer_flow,\
		self.visual_amp_real,self.visual_phase_real,self.visual_amp_recip,self.visual_phase_recip,\
		self.updatereal,self.updaterecip,self.updatelog)
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
		from ..lib.prfftw import pchio
		self.algorithm = pchio
		self.phasemax = 3.1416
		self.phasemin = -3.1416
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
	def Algorithm(self):
		self.algorithm(self.seqdata,self.expdata,self.support,self.mask,\
		self.beta,self.startiter,self.numiter,self.ndim,self.phasemax,self.phasemin,self.rho_m1,self.nn,self.residual,self.citer_flow,\
		self.visual_amp_real,self.visual_phase_real,self.visual_amp_recip,self.visual_phase_recip,\
		self.updatereal,self.updaterecip,self.updatelog)
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
		from ..lib.prfftw import pgchio
		self.algorithm = pgchio
		self.phasemax = 3.1416
		self.phasemin = -3.1416
		self.q = [1.0,1.0,1.0]
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
	def Prepare(self):
		if self.parent != None:
			from ..operations.loadarray import NewArray
			self.rho_m1 = NewArray(self.parent, *self.seqdata.shape)
			self.tmpdata = NewArray(self.parent, *self.seqdata.shape)
		else:
			self.rho_m1 = numpy.empty_like(self.seqdata)
			self.SetResidual()
		self.SetDimensions()
	def Algorithm(self):
		self.algorithm(self.seqdata,self.expdata,self.support,self.mask,self.tmpdata,\
		self.beta,self.startiter,self.numiter,self.ndim,self.phasemax,self.phasemin,\
		self.q[0],self.q[1],self.q[2],self.rho_m1,self.nn,self.residual,self.citer_flow,\
		self.visual_amp_real,self.visual_phase_real,self.visual_amp_recip,self.visual_phase_recip,\
		self.updatereal,self.updaterecip,self.updatelog)
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
		from ..lib.prfftw import hiomaskpc
		self.algorithm = hiomaskpc
	def Algorithm(self):
		SeqArrayObjects = [self.seqdata,self.expdata,self.support,self.mask,self.psf,\
									self.rho_m1,self.pca_inten,self.pca_rho_m1_ft,self.pca_Idm_iter,\
									self.pca_Idmdiv_iter,self.pca_IdmdivId_iter,self.tmpdata1,self.tmpdata2,\
									self.nn,self.ndim, self.nn2,self.startiter,self.numiter,self.citer_flow]
		SeqObjects = [self.residual,self.residualRL,\
								self.visual_amp_real,self.visual_phase_real,self.visual_amp_recip,self.visual_phase_recip,\
								self.updatereal,self.updaterecip, self.updatelog, self.updatelog2,\
								self.gammaHWHM, self.reset_gamma, self.niterrl, self.niterrlpre, self.niterrlinterval, self.ze[0], self.ze[1], self.ze[2],\
								self.beta,self.accel]
		self.algorithm(SeqObjects,SeqArrayObjects)
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
		self.Algorithm()
