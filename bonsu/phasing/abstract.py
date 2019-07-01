#############################################
##   Filename: phasing/abstract.py
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
class PhaseAbstract():
	"""
	Phasing Base Class
	"""
	def __init__(self):
		self.seqdata = None
		self.expdata = None
		self.support = None
		self.mask = None
		self.rho_m1 = None
		self.beta = 0.9
		self.startiter = 0
		self.numiter = 0
		self.nthreads = 1
		self.citer_flow = numpy.zeros((20), dtype=numpy.int32)
		self.residual = None
		self.visual_amp_real = numpy.zeros((1), dtype=numpy.double)
		self.visual_amp_recip = numpy.zeros((1), dtype=numpy.double)
		self.visual_phase_real = numpy.zeros((1), dtype=numpy.double)
		self.visual_phase_recip = numpy.zeros((1), dtype=numpy.double)
		self.algorithm = None
	def Algorithm(self):
		pass
	def SetResidual(self):
		self.residual = numpy.zeros(self.numiter, dtype=numpy.double)
	def SetDimensions(self):
		self.nn = numpy.asarray( self.seqdata.shape, numpy.int32 )
		self.ndim = int(self.seqdata.ndim)
	def Prepare(self):
		"""
		Prepare algorithm.
		"""
		self.rho_m1 = numpy.empty_like(self.seqdata)
		self.SetResidual()
		self.SetDimensions()
	def SetStartiter(self,startiter):
		"""
		Set the starting iteration number.
		"""
		self.startiter = startiter
		self.citer_flow[0] = self.startiter
	def SetNumiter(self,numiter):
		"""
		Set the number of iterations of the
		algorithm to perform.
		"""
		self.numiter = numiter + self.startiter
	def SetNumthreads(self,nthreads):
		"""
		Set the number of FFTW threads.
		"""
		self.nthreads = nthreads
		self.citer_flow[7] = self.nthreads
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
	def updatereal(self):
		pass
	def updaterecip(self):
		pass
	def updatelog(self):
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
		self.Algorithm()
	def Stop(self):
		"""
		Stop the reconstruction process.
		"""
		self.citer_flow[1] = 2
class PhaseAbstractPC(PhaseAbstract):
	"""
	Phasing Partial Coherence Base Class
	"""
	def __init__(self):
		PhaseAbstract.__init__(self)
		self.algorithm = None
		self.residualRL = None
		self.psf = None
		self.niterrlpre = 100
		self.niterrlpretmp = 0
		self.niterrl = 10
		self.niterrlinterval = 10
		self.gammaHWHM = 0.1
		self.ze = [0,0,0]
		self.reset_gamma = 0
		self.accel = 1
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
		from bonsu.lib.prfftw import lorentzftfill
		self.psf = numpy.empty_like(self.seqdata)
		lorentzftfill(self.psf, self.gammaHWHM)
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
	def SetAccel(self, accel):
		self.accel = accel
	def Prepare(self):
		self.niterrlpretmp = self.niterrlpre
		self.rho_m1 = numpy.empty_like(self.seqdata)
		self.SetResidual()
		self.SetResidualRL()
		self.SetDimensions()
	def updatelog2(self):
		try:
			n = self.citer_flow[8]
			string = " R-L iteration: %03d, mean scaling factor: %1.6f" %(n,self.residualRL[0])
			print(string)
		except:
			pass
	def Algorithm(self):
		pass
