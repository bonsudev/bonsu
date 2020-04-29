#############################################
##   Filename: phasing/RAAR.py
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
class RAAR(PhaseAbstract):
	"""
	Relaxed Average Alternating Reflection (RAAR) algorithm.
	"""
	def __init__(self, parent=None):
		PhaseAbstract.__init__(self, parent)
		from ..lib.prfftw import raar
		self.algorithm = raar
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
		from ..lib.prfftw import raarmaskpc
		self.algorithm = raarmaskpc
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
		self.Algorithm()
