#############################################
##   Filename: phasing/ShrinkWrap.py
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
import sys
class ShrinkWrap():
	"""
	Shrink Wrap algorithm.
	"""
	def __init__(self):
		from ..lib.prfftw import gaussian_fill
		self.gaussian_fill = gaussian_fill
		from ..lib.prfftw import wrap
		self.wrap  = wrap
		from ..lib.prfftw import threshold
		self.threshold = threshold
		from ..lib.prfftw import rangereplace
		self.rangereplace = rangereplace
		from ..lib.prfftw import convolve
		self.convolve = convolve
		from ..lib.prfftw import medianfilter
		self.medianfilter = medianfilter
		self.sw_cycle = 10
		self.sw_sigma = 2.0
		self.sw_threshold = 0.2
		self.sw_startiter_tmp = 0
		self.sw_numiter_tmp = 0
	def SetSWCyclelength(self,cycle):
		"""
		Set interval of iterations after which the support is updated.
		"""
		self.sw_cycle = cycle
	def GetSWCyclelength(self):
		"""
		Get interval of iterations after which the support is updated.
		"""
		return self.sw_cycle
	def SetSWSigma(self,sigma):
		"""
		Set standard deviation of the Gaussian smoothing function for the support.
		"""
		self.sw_sigma = sigma
	def GetSWSigma(self):
		"""
		Get standard deviation of the Gaussian smoothing function for the support.
		"""
		return self.sw_sigma
	def SetSWThreshold(self,thresh):
		"""
		Set fractional value below which sequence data is not used when creating the new support.
		"""
		self.sw_threshold = thresh
	def GetSWThreshold(self):
		"""
		Get fractional value below which sequence data is not used when creating the new support.
		"""
		return self.sw_threshold
	def SWGetIterVars(self, fstartiter, fnumiter, ii, fcycle):
		fsw_startiter = fstartiter + (ii * fcycle)
		if  fnumiter <  ((ii+1) * fcycle):
			fsw_numiter =  fnumiter - (ii * fcycle)
		else:
			fsw_numiter = fcycle
		return fsw_startiter, fsw_numiter
	def SWPrepare(self):
		"""
		Prepare shrink wrap algorithm.
		"""
		self.temparray = numpy.empty_like(self.seqdata)
		self.temparray2 = numpy.empty_like(self.seqdata)
		self.gaussian_fill(self.temparray, self.sw_sigma)
		self.wrap(self.temparray, 1)
		self.citer_flow[4] = self.sw_cycle
		self.sw_startiter_tmp = self.startiter
		self.sw_numiter_tmp = self.numiter
		self.IterLoops = (self.numiter + self.sw_cycle - 1)//self.sw_cycle
	def UpdateSupport(self):
		if self.citer_flow[4] > 0:
			print("Updating support ...")
			self.support[:] = numpy.abs(self.seqdata).copy()
			maxvalue = numpy.abs(self.support).max()
			self.threshold(self.support, (self.sw_threshold*maxvalue), maxvalue, 0.0)
			self.medianfilter(self.support, self.temparray2, 3,3,3, 0.0)
			self.wrap(self.support, 1)
			self.convolve(self.support, self.temparray)
			self.wrap(self.support, -1)
			self.rangereplace(self.support, (self.sw_threshold*maxvalue), sys.float_info.max, 0.0, 1.0)
			print("done.")
	def SWStart(self):
		"""
		Start the shrink wrap reconstruction process.
		"""
		for i in range( self.IterLoops ):
			sw_startiter, sw_numiter = self.SWGetIterVars(self.sw_startiter_tmp, self.sw_numiter_tmp, i, self.sw_cycle)
			self.startiter = sw_startiter
			self.numiter = sw_numiter
			self.Start()
			self.UpdateSupport()
