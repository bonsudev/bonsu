#############################################
##   Filename: phasing/concurrent.py
##
##    Copyright (C) 2011 - 2023 Marcus C. Newton
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
class Bifurcate():
	def __init__(self):
		self.base = None
		self.base_n = 1
		self.base_methods = []
		self.base_method_except = []
		self.base_insts = []
	def SetBaseClass(self, base):
		self.base = base
	def Bifurcate(self):
		self.base_insts = [self.base() for i in range(self.base_n)]
		self.base_methods = [method for method in dir(self.base) if (method.startswith('Set') is True and method not in self.base_method_except)]
		for method in self.base_methods:
			setattr(self, method, self.Decor(method))
	def Decor(self, func_name):
		def fdec(*args):
			for i in range(self.base_n):
				getattr(self.base_insts[i], func_name)(args[0][i])
		return fdec
class PhaseConcurrent(Bifurcate):
	"""
	Phase Concurrent Base Class
	"""
	def __init__(self, ampmean=False):
		Bifurcate.__init__(self)
		self.base_method_except = ['SetStartiter','SetNumiter','SetNumthreads']
		self.ampmean = ampmean
		self.NQ = 0
		self.Qar = None
		self.seqdata_angle_bundle = None
		self.dfield = None
		self.stop = False
	def SetNQ(self, NQ):
		"""
		Set Number of Q-Vectors.
		"""
		self.base_n = NQ
		self.NQ = NQ
		self.Qar = numpy.zeros((NQ,3),dtype=numpy.double)
		self.Bifurcate()
	def SetQ(self, idx, Q):
		"""
		Set each Q-vector (3 element NumPy array).
		"""
		self.Qar[idx,:] = Q
	def _PrepQ(self):
		self.Qmat = self.Qar
		if self.NQ == 3:
			self.QmatInv = numpy.linalg.inv(self.Qmat)
		else:
			squareQ = numpy.dot(numpy.transpose(self.Qmat), self.Qmat)
			self.QmatInv = numpy.linalg.inv(squareQ)
	def SetStartiter(self,startiter):
		"""
		Set the starting iteration number.
		"""
		self.startiter = startiter
		for i in range(self.NQ):
			self.base_insts[i].SetStartiter(startiter)
	def SetNumiter(self,numiter):
		"""
		Set the number of iterations for the
		algorithm to perform.
		"""
		self.numiter = numiter
		for i in range(self.NQ):
			self.base_insts[i].SetNumiter(numiter)
	def SetNumthreads(self,nthreads):
		"""
		Set the number of FFTW threads per Q-vector.
		"""
		self.nthreads = nthreads
		for i in range(self.NQ):
			self.base_insts[i].SetNumthreads(nthreads)
	def Prepare(self):
		"""
		Prepare Data
		"""
		self._PrepQ()
		for i in range(self.NQ):
			self.base_insts[i].PrepareCustom()
		self.dims = self.base_insts[0].seqdata.shape
		self.seqdata_angle_bundle = numpy.zeros((self.dims[0],self.dims[1],self.dims[2],self.NQ), dtype=numpy.double)
		self.seqdata_amp = numpy.zeros((self.dims[0],self.dims[1],self.dims[2]), dtype=numpy.double)
		self.dfield = numpy.zeros((self.dims[0],self.dims[1],self.dims[2],3),dtype=numpy.double)
	def _Concrnt(self):
		for i in range(self.NQ):
			self.seqdata_angle_bundle[:,:,:,i] = numpy.angle(self.base_insts[i].seqdata)
		phimat = numpy.asmatrix(self.seqdata_angle_bundle.reshape(self.dims[0]*self.dims[1]*self.dims[2],self.NQ))
		if self.NQ == 3:
			vector_mat = numpy.dot(self.QmatInv, numpy.transpose(phimat))
		else:
			vector_mat = numpy.dot(self.QmatInv, numpy.dot(numpy.transpose(self.Qmat), numpy.transpose(phimat)))
		u = vector_mat
		dfield_flat = self.dfield.reshape(self.dims[0]*self.dims[1]*self.dims[2],3)
		dfield_flat[:] = numpy.transpose(u)
		newphiar = []
		for jj in range(self.NQ):
			phineww = numpy.dot(self.Qar[jj,:],u)
			newphiar.append(numpy.asarray(phineww).squeeze().reshape(self.dims[0],self.dims[1],self.dims[2]))
		if self.ampmean:
			self.seqdata_amp = numpy.abs(self.base_insts[0].seqdata)
			for jj in range(1,self.NQ,1):
				self.seqdata_amp[:] += numpy.abs(self.base_insts[jj].seqdata)
			self.seqdata_amp[:] *= 1.0/float(self.NQ)
			for jj in range(self.NQ):
				self.base_insts[jj].seqdata[:,:,:] = self.seqdata_amp*numpy.cos(newphiar[jj]) + 1j * self.seqdata_amp*numpy.sin(newphiar[jj])
		else:
			for jj in range(self.NQ):
				self.seqdata_amp = numpy.abs(self.base_insts[jj].seqdata)
				self.base_insts[jj].seqdata[:,:,:] = self.seqdata_amp*numpy.cos(newphiar[jj]) + 1j * self.seqdata_amp*numpy.sin(newphiar[jj])
	def Start(self):
		"""
		Start the reconstruction process.
		"""
		for i in range(self.startiter, self.startiter+self.numiter, 1):
			if self.stop == True:
				for j in range(self.NQ):
					self.base_insts[j].DestroyPlan()
				break
			else:
				for j in range(self.NQ):
					self.base_insts[j].DoIter()
				self._Concrnt()
	def SaveDField(self, name):
		"""
		Save the displacement field to a NumPy file.
		"""
		numpy.save(name, self.dfield)
	def SaveSequences(self, name):
		"""
		Save each reconstruction to a NumPy file.
		"""
		if "." in name:
			name_ar = name.rsplit('.', 1)
		else:
			name_ar = [name, "npy"]
		for i in range(self.NQ):
			seq_name = name_ar[0]+"%02.d"%(i)+"."+name_ar[-1]
			numpy.save(seq_name, self.base_insts[i].seqdata)
