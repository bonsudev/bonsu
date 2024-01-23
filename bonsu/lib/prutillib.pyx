##
#############################################
##   Filename: prutillib.pyx
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
cimport numpy as cnumpy
cnumpy.import_array()
cimport cython
from libc.math cimport sqrt, sqrtf
from libc.math cimport cos, cosf
from libc.math cimport sin, sinf
from libc.math cimport atan2, atan2f
from libc.math cimport exp, expf
from libc.math cimport fabs, fabsf
from libc.math cimport pi
from libc.math cimport pow,powf
from libc.stdlib cimport abs as aabs
from libc.stdlib cimport qsort
from libc.stdlib cimport abort, malloc, free
from cython.parallel import prange, parallel
from cpython.pycapsule cimport PyCapsule_GetPointer, PyCapsule_IsValid
from .fftwlib cimport FFTWPlan, FFTW_MEASURE
from .fftwlib cimport FFTW_TORECIP, FFTW_TOREAL
from .fftwlib cimport _fftw_create_plan, _fftwf_create_plan
from .fftwlib cimport _fftw_create_plan_pair, _fftwf_create_plan_pair
from .fftwlib cimport _fftw_stride_pair
from .fftwlib cimport _fftw_stride, _fftwf_stride
ctypedef double complex cdouble
ctypedef float complex csingle
ctypedef float* single_p
ctypedef double* double_p
ctypedef fused f_csd_t:
	csingle
	cdouble
ctypedef fused f_sdp_t:
	single_p
	double_p
ctypedef fused f_sd_t:
	float
	double
@cython.boundscheck(False)
@cython.wraparound(False)
cdef inline double div0chk(double a, double b) noexcept nogil:
	if b == 0.0:
		return 0.0
	else:
		return a/b
@cython.boundscheck(False)
@cython.wraparound(False)
cdef inline void idx2ijk(cnumpy.int64_t idx, cnumpy.int_t[:] dims, cnumpy.int_t[:] ijk) noexcept nogil:
	ijk[2] = idx % dims[2]
	ijk[1] = ((idx - ijk[2])//dims[2]) % dims[1]
	ijk[0] = ((idx - ijk[2])//dims[2]) // dims[1]
@cython.boundscheck(False)
@cython.wraparound(False)
cdef inline int compare(const void *X, const void *Y) noexcept nogil:
	cdef double *x = <double*> X
	cdef double *y = <double*> Y
	if x[0] > y[0]:
		return 1
	elif x[0] < y[0]:
		return -1
	else:
		return 0
@cython.boundscheck(False)
@cython.wraparound(False)
cdef inline cnumpy.int64_t modclip(cnumpy.int64_t idx, cnumpy.int64_t idx_max) noexcept nogil:
	if idx < 0:
		return 0
	elif idx > idx_max:
		return idx_max
	else:
		return idx
cpdef void conv_nmem_nplan(f_csd_t[:, :, ::1] ar_in1, f_csd_t[:, :, ::1] ar_in2,
						f_csd_t[:, :, ::1] ar_tmp1, f_csd_t[:, :, ::1] ar_tmp2,
						object planobj, int nthreads):
	if not PyCapsule_IsValid(planobj, "fftw.planpair"):
		raise ValueError("invalid FFTW Plan pointer")
	cdef FFTWPlan *plan = <FFTWPlan*> PyCapsule_GetPointer(planobj, "fftw.planpair")
	with nogil:
		_conv_nmem_nplan(ar_in1, ar_in2, ar_tmp1, ar_tmp2, plan, nthreads)
@cython.boundscheck(False)
@cython.wraparound(False)
cdef void _conv_nmem_nplan(f_csd_t[:, :, ::1] ar_in1, f_csd_t[:, :, ::1] ar_in2,
						f_csd_t[:, :, ::1] ar_tmp1, f_csd_t[:, :, ::1] ar_tmp2,
						FFTWPlan* plan, int nthreads) noexcept nogil:
	cdef cnumpy.int64_t i,j,k,size
	cdef cnumpy.int64_t pdi, pdj, pdk
	cdef double v1r, v1i
	cdef double v2r, v2i
	cdef float v1rf, v1if
	cdef float v2rf, v2if
	cdef cdouble czero = 0.0 + 1j*0.0
	cdef csingle czerof = 0.0 + 1j*0.0
	size = <cnumpy.int64_t> (ar_tmp1.shape[0]*ar_tmp1.shape[1]*ar_tmp1.shape[2])
	pdi = <cnumpy.int64_t> ((ar_tmp1.shape[0] - ar_in1.shape[0]) // 2)
	pdj = <cnumpy.int64_t> ((ar_tmp1.shape[1] - ar_in1.shape[1]) // 2)
	pdk = <cnumpy.int64_t> ((ar_tmp1.shape[2] - ar_in1.shape[2]) // 2)
	if f_csd_t is cdouble:
		for i in prange(ar_tmp1.shape[0], num_threads=nthreads):
			for j in prange(ar_tmp1.shape[1], num_threads=nthreads):
				for k in prange(ar_tmp1.shape[2], num_threads=nthreads):
					ar_tmp1[i,j,k] = czero
					ar_tmp2[i,j,k] = czero
	elif f_csd_t is csingle:
		for i in prange(ar_tmp1.shape[0], num_threads=nthreads):
			for j in prange(ar_tmp1.shape[1], num_threads=nthreads):
				for k in prange(ar_tmp1.shape[2], num_threads=nthreads):
					ar_tmp1[i,j,k] = czerof
					ar_tmp2[i,j,k] = czerof
	for i in prange(ar_in1.shape[0], num_threads=nthreads):
		for j in prange(ar_in1.shape[1], num_threads=nthreads):
			for k in prange(ar_in1.shape[2], num_threads=nthreads):
				ar_tmp1[i+pdi,j+pdj,k+pdk] = ar_in1[i,j,k]
				ar_tmp2[i+pdi,j+pdj,k+pdk] = ar_in2[i,j,k]
	with gil:
		wrap(ar_tmp1, 1)
		wrap(ar_tmp2, 1)
	_fftw_stride_pair(ar_tmp1, ar_tmp2, plan, FFTW_TORECIP, 1)
	if f_csd_t is cdouble:
		for i in prange(ar_tmp1.shape[0], num_threads=nthreads):
			for j in prange(ar_tmp1.shape[1], num_threads=nthreads):
				for k in prange(ar_tmp1.shape[2], num_threads=nthreads):
					v1r = ar_tmp1[i,j,k].real
					v1i = ar_tmp1[i,j,k].imag
					v2r = ar_tmp2[i,j,k].real
					v2i = ar_tmp2[i,j,k].imag
					ar_tmp1[i,j,k] = (v1r*v2r - v1i*v2i)\
								+ 1j*(v1r*v2i + v1i*v2r)
	elif f_csd_t is csingle:
		for i in prange(ar_tmp1.shape[0], num_threads=nthreads):
			for j in prange(ar_tmp1.shape[1], num_threads=nthreads):
				for k in prange(ar_tmp1.shape[2], num_threads=nthreads):
					v1rf = ar_tmp1[i,j,k].real
					v1if = ar_tmp1[i,j,k].imag
					v2rf = ar_tmp2[i,j,k].real
					v2if = ar_tmp2[i,j,k].imag
					ar_tmp1[i,j,k] = (v1rf*v2rf - v1if*v2if)\
								+ 1j*(v1rf*v2if + v1if*v2rf)
	_fftw_stride_pair(ar_tmp1, ar_tmp2, plan, FFTW_TOREAL, 0)
	with gil:
		wrap(ar_tmp1, -1)
		wrap(ar_tmp2, -1)
	for i in prange(ar_in1.shape[0], num_threads=nthreads):
		for j in prange(ar_in1.shape[1], num_threads=nthreads):
			for k in prange(ar_in1.shape[2], num_threads=nthreads):
				ar_in1[i,j,k] = ar_tmp1[i+pdi,j+pdj,k+pdk]
cpdef convolve(f_csd_t[:, :, ::1] ar_in1, f_csd_t[:, :, ::1] ar_in2, int nthreads):
	cdef cdouble[:, :, ::1] ar_tmp1
	cdef cdouble[:, :, ::1] ar_tmp2
	cdef csingle[:, :, ::1] ar_tmp1f
	cdef csingle[:, :, ::1] ar_tmp2f
	cdef FFTWPlan *plan
	if f_csd_t is cdouble:
		ar_tmp1 = numpy.empty((ar_in1.shape[0]*2,ar_in1.shape[1]*2,ar_in1.shape[2]*2), dtype=numpy.cdouble)
		ar_tmp2 = numpy.empty((ar_in1.shape[0]*2,ar_in1.shape[1]*2,ar_in1.shape[2]*2), dtype=numpy.cdouble)
		plan = _fftw_create_plan_pair(ar_tmp1, ar_tmp2, nthreads, FFTW_MEASURE)
		with nogil:
			_conv_nmem_nplan(ar_in1, ar_in2, ar_tmp1, ar_tmp2, plan, nthreads)
	elif f_csd_t is csingle:
		ar_tmp1f = numpy.empty((ar_in1.shape[0]*2,ar_in1.shape[1]*2,ar_in1.shape[2]*2), dtype=numpy.csingle)
		ar_tmp2f = numpy.empty((ar_in1.shape[0]*2,ar_in1.shape[1]*2,ar_in1.shape[2]*2), dtype=numpy.csingle)
		plan = _fftwf_create_plan_pair(ar_tmp1f, ar_tmp2f, nthreads, FFTW_MEASURE)
		with nogil:
			_conv_nmem_nplan(ar_in1, ar_in2, ar_tmp1f, ar_tmp2f, plan, nthreads)
@cython.boundscheck(False)
@cython.wraparound(False)
cdef void _convolve_ntmp(f_csd_t[:, :, ::1] ar_in1, f_csd_t[:, :, ::1] ar_in2,\
						FFTWPlan* plan, int nthreads) noexcept nogil:
	cdef cnumpy.int64_t i,j,k
	cdef double scale = sqrt(<double> (ar_in1.shape[0]*ar_in1.shape[1]*ar_in1.shape[2]))
	cdef float scalef = sqrtf(<float> (ar_in1.shape[0]*ar_in1.shape[1]*ar_in1.shape[2]))
	cdef double v1r, v1i
	cdef double v2r, v2i
	cdef float v1rf, v1if
	cdef float v2rf, v2if
	if f_csd_t is cdouble:
		_fftw_stride(ar_in1, ar_in1, plan, FFTW_TORECIP, 1)
		_fftw_stride(ar_in2, ar_in2, plan, FFTW_TORECIP, 1)
	elif f_csd_t is csingle:
		_fftwf_stride(ar_in1, ar_in1, plan, FFTW_TORECIP, 1)
		_fftwf_stride(ar_in2, ar_in2, plan, FFTW_TORECIP, 1)
	if f_csd_t is cdouble:
		for i in prange(ar_in1.shape[0], num_threads=nthreads):
			for j in prange(ar_in1.shape[1], num_threads=nthreads):
				for k in prange(ar_in1.shape[2], num_threads=nthreads):
					v1r = ar_in1[i,j,k].real
					v1i = ar_in1[i,j,k].imag
					v2r = ar_in2[i,j,k].real
					v2i = ar_in2[i,j,k].imag
					ar_in1[i,j,k] = (v1r*v2r - v1i*v2i)*scale\
								+ 1j*(v1r*v2i + v1i*v2r)*scale
	elif f_csd_t is csingle:
		for i in prange(ar_in1.shape[0], num_threads=nthreads):
			for j in prange(ar_in1.shape[1], num_threads=nthreads):
				for k in prange(ar_in1.shape[2], num_threads=nthreads):
					v1rf = ar_in1[i,j,k].real
					v1if = ar_in1[i,j,k].imag
					v2rf = ar_in2[i,j,k].real
					v2if = ar_in2[i,j,k].imag
					ar_in1[i,j,k] = (v1rf*v2rf - v1if*v2if)*scalef\
								+ 1j*(v1rf*v2if + v1if*v2rf)*scalef
	if f_csd_t is cdouble:
		_fftw_stride(ar_in1, ar_in1, plan, FFTW_TOREAL, 1)
		_fftw_stride(ar_in2, ar_in2, plan, FFTW_TOREAL, 1)
	elif f_csd_t is csingle:
		_fftwf_stride(ar_in1, ar_in1, plan, FFTW_TOREAL, 1)
		_fftwf_stride(ar_in2, ar_in2, plan, FFTW_TOREAL, 1)
cpdef convolve_ntmp(f_csd_t[:, :, ::1] ar_in1, f_csd_t[:, :, ::1] ar_in2, int nthreads):
	cdef FFTWPlan *plan
	if f_csd_t is cdouble:
		plan = _fftw_create_plan(ar_in1, nthreads, FFTW_MEASURE)
	elif f_csd_t is csingle:
		plan = _fftwf_create_plan(ar_in1, nthreads, FFTW_MEASURE)
	else:
		raise TypeError()
	with nogil:
		_convolve_ntmp(ar_in1, ar_in2, plan, nthreads)
@cython.boundscheck(False)
@cython.wraparound(False)
cdef void _fft(f_csd_t[:, :, ::1] ar_in, FFTWPlan* plan, int direction) noexcept nogil:
	if f_csd_t is cdouble:
		_fftw_stride(ar_in, ar_in, plan, direction, 1)
	elif f_csd_t is csingle:
		_fftwf_stride(ar_in, ar_in, plan, direction, 1)
cpdef fft(f_csd_t[:, :, ::1] ar_in, int direction, int nthreads):
	cdef FFTWPlan *plan
	if f_csd_t is cdouble:
		plan = _fftw_create_plan(ar_in, nthreads, FFTW_MEASURE)
	elif f_csd_t is csingle:
		plan = _fftwf_create_plan(ar_in, nthreads, FFTW_MEASURE)
	else:
		raise TypeError()
	with nogil:
		_fft(ar_in, plan, direction)
@cython.boundscheck(False)
@cython.wraparound(False)
cdef void _wrap_nomem(f_sdp_t ar_in, f_sdp_t ar_tmp, cnumpy.int_t[:] split,
						cnumpy.int_t[:] nnh, cnumpy.int_t[:] c, cnumpy.int_t[:] cn, cnumpy.int_t[:] ijk,
						cnumpy.int_t[:] ijks, cnumpy.int_t[:] shape, int drctn) noexcept nogil:
	cdef cnumpy.int64_t lenh = 0
	cdef cnumpy.int64_t qd = 0
	cdef cnumpy.int64_t i = 0
	cdef cnumpy.int64_t ii = 0
	cdef cnumpy.int64_t iih = 0
	cdef cnumpy.int64_t iish = 0
	cdef cnumpy.int64_t size = shape[0]*shape[1]*shape[2]
	for i in range(size):
		ar_tmp[2*i] = ar_in[2*i]
		ar_tmp[2*i+1] = ar_in[2*i+1]
	if shape[0] > 1 and shape[0] % 2  > 0 and drctn < 0:
		split[0] = shape[0] // 2 + 1
	else:
		split[0] = shape[0] // 2
	if shape[1] > 1 and shape[1] % 2  > 0 and drctn < 0:
		split[1] = shape[1] // 2 + 1
	else:
		split[1] = shape[1] // 2
	if shape[2] > 1 and shape[2] % 2  > 0 and drctn < 0:
		split[2] = shape[2] // 2 + 1
	else:
		split[2] = shape[2] // 2
	for qd in range(8):
		c[0] = ((qd+2)//2)%2
		c[1] = ((qd+4)//4)%2
		c[2] = 1
		c[0] = (c[0]+qd)%2
		c[1] = (c[1]+qd)%2
		c[2] = (c[2]+qd)%2
		cn[0] = (c[0]+1)%2
		cn[1] = (c[1]+1)%2
		cn[2] = (c[2]+1)%2
		nnh[0] = aabs(shape[0]*cn[0] - split[0])
		nnh[1] = aabs(shape[1]*cn[1] - split[1])
		nnh[2] = aabs(shape[2]*cn[2] - split[2])
		lenh = nnh[0] * nnh[1] * nnh[2]
		for iih in range(lenh):
			idx2ijk(iih, nnh, ijk)
			ijk[0] += cn[0]*split[0]
			ijk[1] += cn[1]*split[1]
			ijk[2] += cn[2]*split[2]
			ii = (ijk[2]+shape[2]*(ijk[1]+shape[1]*ijk[0]))
			iish = ((shape[2]*c[2] - split[2] + ijk[2])+shape[2]*((shape[1]*c[1] - split[1] + ijk[1])+shape[1]*(shape[0]*c[0] - split[0] + ijk[0])))
			ar_in[2*iish] = ar_tmp[2*ii]
			ar_in[2*iish+1] = ar_tmp[2*ii+1]
cpdef wrap_nomem(f_csd_t[:, :, ::1] ar_in, f_csd_t[:, :, ::1] ar_tmp, int drctn):
	cdef int size = ar_in.size
	cdef cnumpy.int_t[:] split, nnh, c, cn, ijk, ijks, shape
	shape = numpy.array([ar_in.shape[0], ar_in.shape[1], ar_in.shape[2]], dtype=numpy.int_)
	split = numpy.zeros((3), dtype=numpy.int_)
	nnh = numpy.zeros((3), dtype=numpy.int_)
	c = numpy.zeros((3), dtype=numpy.int_)
	cn = numpy.zeros((3), dtype=numpy.int_)
	ijk = numpy.zeros((3), dtype=numpy.int_)
	ijks = numpy.zeros((3), dtype=numpy.int_)
	cdef double* ar_in_buff = <double*> &ar_in[0,0,0]
	cdef float* ar_inf_buff = <float*> &ar_in[0,0,0]
	cdef double* ar_tmp_buff = <double*> &ar_tmp[0,0,0]
	cdef float* ar_tmpf_buff = <float*> &ar_tmp[0,0,0]
	if f_csd_t is cdouble:
		with nogil:
			_wrap_nomem(ar_in_buff, ar_tmp_buff, split, nnh, c, cn, ijk, ijks, shape, drctn)
	elif f_csd_t is csingle:
		with nogil:
			_wrap_nomem(ar_inf_buff, ar_tmpf_buff, split, nnh, c, cn, ijk, ijks, shape, drctn)
cpdef wrap(f_csd_t[:, :, ::1] ar_in, int drctn):
	cdef cdouble[:, :, ::1] ar_tmp
	cdef csingle[:, :, ::1] ar_tmpf
	if f_csd_t is cdouble:
		ar_tmp = numpy.empty_like(ar_in)
		wrap_nomem(ar_in, ar_tmp, drctn)
	elif f_csd_t is csingle:
		ar_tmpf = numpy.empty_like(ar_in)
		wrap_nomem(ar_in, ar_tmpf, drctn)
@cython.boundscheck(False)
@cython.wraparound(False)
cdef double _residual(f_csd_t[:, :, ::1] seqdata, f_csd_t[:, :, ::1] expdata, int size, int nthreads) noexcept nogil:
	cdef double* seqdata_buff = <double*> &seqdata[0,0,0]
	cdef double* expdata_buff = <double*> &expdata[0,0,0]
	cdef double var1 = 0
	cdef double var2 = 0
	cdef double res = 0
	cdef float* seqdataf_buff = <float*> &seqdata[0,0,0]
	cdef float* expdataf_buff = <float*> &expdata[0,0,0]
	cdef float var1f = 0
	cdef float var2f = 0
	cdef float resf = 0
	cdef cnumpy.int64_t i
	if f_csd_t is cdouble:
		for i in prange(size, num_threads=nthreads):
			var1 = sqrt(seqdata_buff[2*i]*seqdata_buff[2*i]+seqdata_buff[2*i+1]*seqdata_buff[2*i+1])
			var2 = sqrt(expdata_buff[2*i]*expdata_buff[2*i]+expdata_buff[2*i+1]*expdata_buff[2*i+1])
			res += (var1 - var2)*(var1 - var2)
		return res
	elif f_csd_t is csingle:
		for i in prange(size, num_threads=nthreads):
			var1f = sqrt(seqdataf_buff[2*i]*seqdataf_buff[2*i]+seqdataf_buff[2*i+1]*seqdataf_buff[2*i+1])
			var2f = sqrt(expdataf_buff[2*i]*expdataf_buff[2*i]+expdataf_buff[2*i+1]*expdataf_buff[2*i+1])
			resf += (var1f - var2f)*(var1f - var2f)
		return resf
@cython.boundscheck(False)
@cython.wraparound(False)
cdef double _residualmask(f_csd_t[:, :, ::1] seqdata, f_csd_t[:, :, ::1] expdata, f_csd_t[:, :, ::1] mask, int size, int nthreads) noexcept nogil:
	cdef double* seqdata_buff = <double*> &seqdata[0,0,0]
	cdef double* expdata_buff = <double*> &expdata[0,0,0]
	cdef double* mask_buff = <double*> &mask[0,0,0]
	cdef double var1 = 0
	cdef double var2 = 0
	cdef double res = 0
	cdef float* seqdataf_buff = <float*> &seqdata[0,0,0]
	cdef float* expdataf_buff = <float*> &expdata[0,0,0]
	cdef float* maskf_buff = <float*> &mask[0,0,0]
	cdef float var1f = 0
	cdef float var2f = 0
	cdef float resf = 0
	cdef cnumpy.int64_t i
	if f_csd_t is cdouble:
		for i in prange(size, num_threads=nthreads):
			var1 = sqrt(seqdata_buff[2*i]*seqdata_buff[2*i]+seqdata_buff[2*i+1]*seqdata_buff[2*i+1])
			var2 = sqrt(expdata_buff[2*i]*expdata_buff[2*i]+expdata_buff[2*i+1]*expdata_buff[2*i+1])
			res += (var1 - var2)*(var1 - var2)*mask_buff[2*i]
		return res
	elif f_csd_t is csingle:
		for i in prange(size, num_threads=nthreads):
			var1f = sqrt(seqdataf_buff[2*i]*seqdataf_buff[2*i]+seqdataf_buff[2*i+1]*seqdataf_buff[2*i+1])
			var2f = sqrt(expdataf_buff[2*i]*expdataf_buff[2*i]+expdataf_buff[2*i+1]*expdataf_buff[2*i+1])
			resf += (var1f - var2f)*(var1f - var2f)*maskf_buff[2*i]
		return resf
cpdef residual(f_csd_t[:, :, ::1] seqdata, f_csd_t[:, :, ::1] expdata, f_csd_t[:, :, ::1] mask, int nthreads):
	cdef int size = seqdata.size
	cdef double res = 0.0
	if mask is None:
		with nogil:
			res = _residual(seqdata, expdata, size, nthreads)
	else:
		with nogil:
			res =  _residualmask(seqdata, expdata, mask, size, nthreads)
	return res
@cython.boundscheck(False)
@cython.wraparound(False)
cdef void _ampsmask(f_csd_t[:, :, ::1] seqdata, f_csd_t[:, :, ::1] expdata, f_csd_t[:, :, ::1] mask, int size, int nthreads) noexcept nogil:
	cdef double* seqdata_buff = <double*> &seqdata[0,0,0]
	cdef double* expdata_buff = <double*> &expdata[0,0,0]
	cdef double* mask_buff = <double*> &mask[0,0,0]
	cdef double amp
	cdef double phase
	cdef float* seqdataf_buff = <float*> &seqdata[0,0,0]
	cdef float* expdataf_buff = <float*> &expdata[0,0,0]
	cdef float* maskf_buff = <float*> &mask[0,0,0]
	cdef float ampf
	cdef float phasef
	cdef cnumpy.int64_t i
	if f_csd_t is cdouble:
		for i in prange(size, num_threads=nthreads):
			amp = sqrt(expdata_buff[2*i]*expdata_buff[2*i]+expdata_buff[2*i+1]*expdata_buff[2*i+1])
			phase = atan2(seqdata_buff[2*i+1], seqdata_buff[2*i])
			seqdata_buff[2*i] = amp * mask_buff[2*i] * cos(phase)
			seqdata_buff[2*i+1] = amp * mask_buff[2*i] * sin(phase)
	elif f_csd_t is csingle:
		for i in prange(size, num_threads=nthreads):
			ampf = sqrt(expdataf_buff[2*i]*expdataf_buff[2*i]+expdataf_buff[2*i+1]*expdataf_buff[2*i+1])
			phasef = atan2(seqdataf_buff[2*i+1], seqdataf_buff[2*i])
			seqdataf_buff[2*i] = ampf * maskf_buff[2*i] * cos(phasef)
			seqdataf_buff[2*i+1] = ampf * maskf_buff[2*i] * sin(phasef)
@cython.boundscheck(False)
@cython.wraparound(False)
cdef void _amps(f_csd_t[:, :, ::1] seqdata, f_csd_t[:, :, ::1] expdata, int size, int nthreads) noexcept nogil:
	cdef double* seqdata_buff = <double*> &seqdata[0,0,0]
	cdef double* expdata_buff = <double*> &expdata[0,0,0]
	cdef double amp
	cdef double phase
	cdef float* seqdataf_buff = <float*> &seqdata[0,0,0]
	cdef float* expdataf_buff = <float*> &expdata[0,0,0]
	cdef float ampf
	cdef float phasef
	cdef cnumpy.int64_t i
	if f_csd_t is cdouble:
		for i in prange(size, num_threads=nthreads):
			amp = sqrt(expdata_buff[2*i]*expdata_buff[2*i]+expdata_buff[2*i+1]*expdata_buff[2*i+1])
			phase = atan2(seqdata_buff[2*i+1], seqdata_buff[2*i])
			seqdata_buff[2*i] = amp * cos(phase)
			seqdata_buff[2*i+1] = amp * sin(phase)
	elif f_csd_t is csingle:
		for i in prange(size, num_threads=nthreads):
			ampf = sqrt(expdataf_buff[2*i]*expdataf_buff[2*i]+expdataf_buff[2*i+1]*expdataf_buff[2*i+1])
			phasef = atan2(seqdataf_buff[2*i+1], seqdataf_buff[2*i])
			seqdataf_buff[2*i] = ampf * cos(phasef)
			seqdataf_buff[2*i+1] = ampf * sin(phasef)
cpdef updateamps(f_csd_t[:, :, ::1] seqdata, f_csd_t[:, :, ::1] expdata, f_csd_t[:, :, ::1] mask, int nthreads):
	cdef int size = seqdata.size
	if mask is None:
		with nogil:
			_amps(seqdata, expdata, size, nthreads)
	else:
		with nogil:
			_ampsmask(seqdata, expdata, mask, size, nthreads)
@cython.boundscheck(False)
@cython.wraparound(False)
cdef double _sumofsqs(f_csd_t[:, :, ::1] seqdata, int size, int nthreads) noexcept nogil:
	cdef double* seqdata_buff = <double*> &seqdata[0,0,0]
	cdef float* seqdataf_buff = <float*> &seqdata[0,0,0]
	cdef double sos = 0.0
	cdef float sosf = 0.0
	cdef cnumpy.int64_t i
	if f_csd_t is cdouble:
		for i in prange(size, num_threads=nthreads):
			sos += seqdata_buff[2*i]*seqdata_buff[2*i]+seqdata_buff[2*i+1]*seqdata_buff[2*i+1]
		return sos
	elif f_csd_t is csingle:
		for i in prange(size, num_threads=nthreads):
			sosf += seqdataf_buff[2*i]*seqdataf_buff[2*i]+seqdataf_buff[2*i+1]*seqdataf_buff[2*i+1]
		return sosf
cpdef double sumofsqs(f_csd_t[:, :, ::1] seqdata, int nthreads):
	cdef int size = seqdata.size
	with nogil:
		return _sumofsqs(seqdata, size, nthreads)
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef void lorentz_ft_fill(f_csd_t[:, :, ::1] ar_in, double gammaHWHM, int nthreads):
	cdef cnumpy.int64_t i,j,k
	cdef double r, rmax
	cdef float rf, rmaxf
	cdef float gammaHWHMf = <float> gammaHWHM
	cdef double c1 = -2.0
	cdef double c2 = -1.0
	cdef float c1f = -2.0
	cdef float c2f = -1.0
	if f_csd_t is cdouble:
		rmax = sqrt(<double> ((ar_in.shape[0]//2)*(ar_in.shape[0]//2)\
							+(ar_in.shape[1]//2)*(ar_in.shape[1]//2)\
							+(ar_in.shape[2]//2)*(ar_in.shape[2]//2)))
		for i in prange(ar_in.shape[0], nogil=True, num_threads=nthreads):
			for j in prange(ar_in.shape[1], num_threads=nthreads):
				for k in prange(ar_in.shape[2], num_threads=nthreads):
					r = sqrt(<double> ((i-ar_in.shape[0]//2)*(i-ar_in.shape[0]//2)\
										+(j-ar_in.shape[1]//2)*(j-ar_in.shape[1]//2)\
										+(k-ar_in.shape[2]//2)*(k-ar_in.shape[2]//2)))
					ar_in[i,j,k] = fabs(gammaHWHM) * exp(- fabs(gammaHWHM)*r)\
										/ (c1 *( exp(-fabs(gammaHWHM)*rmax) + c2))
	elif f_csd_t is csingle:
		rmaxf = sqrtf(<float> ((ar_in.shape[0]//2)*(ar_in.shape[0]//2)\
							+(ar_in.shape[1]//2)*(ar_in.shape[1]//2)\
							+(ar_in.shape[2]//2)*(ar_in.shape[2]//2)))
		for i in prange(ar_in.shape[0], nogil=True, num_threads=nthreads):
			for j in prange(ar_in.shape[1], num_threads=nthreads):
				for k in prange(ar_in.shape[2], num_threads=nthreads):
					rf = sqrtf(<float> ((i-ar_in.shape[0]//2)*(i-ar_in.shape[0]//2)\
										+(j-ar_in.shape[1]//2)*(j-ar_in.shape[1]//2)\
										+(k-ar_in.shape[2]//2)*(k-ar_in.shape[2]//2)))
					ar_in[i,j,k] = fabsf(gammaHWHMf) * expf(- fabsf(gammaHWHMf)*rf)\
										/ (c1f *( expf(-fabsf(gammaHWHMf)*rmaxf) + c2f))
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef void gaussian_fill(f_csd_t[:, :, ::1] ar_in, double sigma, int nthreads):
	cdef cnumpy.int64_t i,j,k
	cdef float sigmaf = <float> sigma
	cdef double c1 = 1.0
	cdef double c2 = 2.0
	cdef float c1f = 1.0
	cdef float c2f = 2.0
	cdef float pif = <float> pi
	if f_csd_t is cdouble:
		for i in prange(ar_in.shape[0], nogil=True, num_threads=nthreads):
			for j in prange(ar_in.shape[1], num_threads=nthreads):
				for k in prange(ar_in.shape[2], num_threads=nthreads):
					ar_in[i,j,k] = (c1/(sigma*sqrt(c2*pi)))\
									* exp((<double> ((i-ar_in.shape[0]//2)*(i-ar_in.shape[0]//2)\
									+ (j-ar_in.shape[1]//2)*(j-ar_in.shape[1]//2)
									+ (k-ar_in.shape[2]//2)*(k-ar_in.shape[2]//2))) / (-c2*sigma*sigma))
	elif f_csd_t is csingle:
		for i in prange(ar_in.shape[0], nogil=True, num_threads=nthreads):
			for j in prange(ar_in.shape[1], num_threads=nthreads):
				for k in prange(ar_in.shape[2], num_threads=nthreads):
					ar_in[i,j,k] = (c1f/(sigmaf*sqrtf(c2f*pif)))\
									* expf( (<float> ((i-ar_in.shape[0]//2)*(i-ar_in.shape[0]//2)\
									+ (j-ar_in.shape[1]//2)*(j-ar_in.shape[1]//2)
									+ (k-ar_in.shape[2]//2)*(k-ar_in.shape[2]//2))) / (-c2f*sigmaf*sigmaf))
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef void threshold(f_csd_t[:, :, ::1] ar_in, double threshmin, double threshmax, double newval, int nthreads):
	cdef cnumpy.int64_t i,j,k
	cdef double val
	cdef float valf
	cdef float threshminf = <float> threshmin
	cdef float threshmaxf = <float> threshmax
	cdef float newvalf = <float> newval
	if f_csd_t is cdouble:
		for i in prange(ar_in.shape[0], nogil=True, num_threads=nthreads):
			for j in prange(ar_in.shape[1], num_threads=nthreads):
				for k in prange(ar_in.shape[2], num_threads=nthreads):
					val = sqrt(ar_in[i,j,k].real * ar_in[i,j,k].real + ar_in[i,j,k].imag * ar_in[i,j,k].imag)
					if val < threshmin or val > threshmax:
						ar_in[i,j,k] = newval
	elif f_csd_t is csingle:
		for i in prange(ar_in.shape[0], nogil=True, num_threads=nthreads):
			for j in prange(ar_in.shape[1], num_threads=nthreads):
				for k in prange(ar_in.shape[2], num_threads=nthreads):
					valf = sqrtf(<float> (ar_in[i,j,k].real * ar_in[i,j,k].real + ar_in[i,j,k].imag * ar_in[i,j,k].imag))
					if valf < threshminf or valf > threshmaxf:
						ar_in[i,j,k] = newvalf
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef void rangereplace(f_csd_t[:, :, ::1] ar_in, double threshmin, double threshmax, double newval_out, double newval_in, int nthreads):
	cdef cnumpy.int64_t i,j,k
	cdef double val
	cdef float valf
	cdef float threshminf = <float> threshmin
	cdef float threshmaxf = <float> threshmax
	cdef float newval_outf = <float> newval_out
	cdef float newval_inf = <float> newval_in
	if f_csd_t is cdouble:
		for i in prange(ar_in.shape[0], nogil=True, num_threads=nthreads):
			for j in prange(ar_in.shape[1], num_threads=nthreads):
				for k in prange(ar_in.shape[2], num_threads=nthreads):
					val = sqrt(ar_in[i,j,k].real * ar_in[i,j,k].real + ar_in[i,j,k].imag * ar_in[i,j,k].imag)
					if val < threshmin or val > threshmax:
						ar_in[i,j,k] = newval_out
					else:
						ar_in[i,j,k] = newval_in
	elif f_csd_t is csingle:
		for i in prange(ar_in.shape[0], nogil=True, num_threads=nthreads):
			for j in prange(ar_in.shape[1], num_threads=nthreads):
				for k in prange(ar_in.shape[2], num_threads=nthreads):
					valf = sqrtf(<float> (ar_in[i,j,k].real * ar_in[i,j,k].real + ar_in[i,j,k].imag * ar_in[i,j,k].imag))
					if valf < threshminf or valf > threshmaxf:
						ar_in[i,j,k] = newval_outf
					else:
						ar_in[i,j,k] = newval_inf
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef void conj_reflect(f_csd_t[:, :, ::1] ar_in):
	cdef cnumpy.int64_t i,j,k
	cdef cdouble val1
	cdef cdouble val2
	cdef csingle val1f
	cdef csingle val2f
	if f_csd_t is cdouble:
		for i in range(ar_in.shape[0]//2):
			for j in range(ar_in.shape[1]):
				for k in range(ar_in.shape[2]):
					val1 = ar_in[i,j,k]
					val2 = ar_in[ar_in.shape[0]-i-1,ar_in.shape[1]-j-1,ar_in.shape[2]-k-1]
					ar_in[i,j,k] = val2.real - 1j*val2.imag
					ar_in[ar_in.shape[0]-i-1,ar_in.shape[1]-j-1,ar_in.shape[2]-k-1] = val1.real - 1j*val1.imag
		if ar_in.shape[0] % 2 == 1:
			i = ar_in.shape[0]//2
			for j in range(ar_in.shape[1]//2):
				for k in range(ar_in.shape[2]):
					val1 = ar_in[i,j,k]
					val2 = ar_in[ar_in.shape[0]-i-1,ar_in.shape[1]-j-1,ar_in.shape[2]-k-1]
					ar_in[i,j,k] = val2.real - 1j*val2.imag
					ar_in[ar_in.shape[0]-i-1,ar_in.shape[1]-j-1,ar_in.shape[2]-k-1] = val1.real - 1j*val1.imag
		if ar_in.shape[0] % 2 == 1 and ar_in.shape[1] % 2 == 1:
			i = ar_in.shape[0]//2
			j = ar_in.shape[1]//2
			for k in range(ar_in.shape[2]//2):
				val1 = ar_in[i,j,k]
				val2 = ar_in[ar_in.shape[0]-i-1,ar_in.shape[1]-j-1,ar_in.shape[2]-k-1]
				ar_in[i,j,k] = val2.real - 1j*val2.imag
				ar_in[ar_in.shape[0]-i-1,ar_in.shape[1]-j-1,ar_in.shape[2]-k-1] = val1.real - 1j*val1.imag
		if ar_in.shape[0] % 2 == 1 and ar_in.shape[1] % 2 == 1 and ar_in.shape[2] % 2 == 1:
			i = ar_in.shape[0]//2
			j = ar_in.shape[1]//2
			k = ar_in.shape[2]//2
			ar_in[i,j,k] = ar_in[i,j,k].real - 1j*ar_in[i,j,k].imag
	elif f_csd_t is csingle:
		for i in range(ar_in.shape[0]//2):
			for j in range(ar_in.shape[1]):
				for k in range(ar_in.shape[2]):
					val1f = ar_in[i,j,k]
					val2f = ar_in[ar_in.shape[0]-i-1,ar_in.shape[1]-j-1,ar_in.shape[2]-k-1]
					ar_in[i,j,k] = val2f.real - 1j*val2f.imag
					ar_in[ar_in.shape[0]-i-1,ar_in.shape[1]-j-1,ar_in.shape[2]-k-1] = val1f.real - 1j*val1f.imag
		if ar_in.shape[0] % 2 == 1:
			i = ar_in.shape[0]//2
			for j in range(ar_in.shape[1]//2):
				for k in range(ar_in.shape[2]):
					val1f = ar_in[i,j,k]
					val2f = ar_in[ar_in.shape[0]-i-1,ar_in.shape[1]-j-1,ar_in.shape[2]-k-1]
					ar_in[i,j,k] = val2f.real - 1j*val2f.imag
					ar_in[ar_in.shape[0]-i-1,ar_in.shape[1]-j-1,ar_in.shape[2]-k-1] = val1f.real - 1j*val1f.imag
		if ar_in.shape[0] % 2 == 1 and ar_in.shape[1] % 2 == 1:
			i = ar_in.shape[0]//2
			j = ar_in.shape[1]//2
			for k in range(ar_in.shape[2]//2):
				val1f = ar_in[i,j,k]
				val2f = ar_in[ar_in.shape[0]-i-1,ar_in.shape[1]-j-1,ar_in.shape[2]-k-1]
				ar_in[i,j,k] = val2f.real - 1j*val2f.imag
				ar_in[ar_in.shape[0]-i-1,ar_in.shape[1]-j-1,ar_in.shape[2]-k-1] = val1f.real - 1j*val1f.imag
		if ar_in.shape[0] % 2 == 1 and ar_in.shape[1] % 2 == 1 and ar_in.shape[2] % 2 == 1:
			i = ar_in.shape[0]//2
			j = ar_in.shape[1]//2
			k = ar_in.shape[2]//2
			ar_in[i,j,k] = ar_in[i,j,k].real - 1j*ar_in[i,j,k].imag
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef void median_replace_voxel(f_csd_t[:, :, ::1] ar_in1, f_csd_t[:, :, ::1] ar_in2, int k_x, int k_y, int k_z, double maxerr, int nthreads):
	cdef cnumpy.int64_t i,j,k
	cdef double amp1, amp2, err
	medianfilter(ar_in1, ar_in2, k_x, k_y, k_z, nthreads)
	for i in prange(ar_in1.shape[0], nogil=True, num_threads=nthreads):
		for j in prange(ar_in1.shape[1], num_threads=nthreads):
			for k in prange(ar_in1.shape[2], num_threads=nthreads):
				amp1 = sqrt(ar_in1[i,j,k].real * ar_in1[i,j,k].real + ar_in1[i,j,k].imag * ar_in1[i,j,k].imag)
				amp2 = sqrt(ar_in2[i,j,k].real * ar_in2[i,j,k].real + ar_in2[i,j,k].imag * ar_in2[i,j,k].imag)
				err = div0chk(fabs(amp2 - amp1), amp1)
				if err > maxerr:
					ar_in1[i,j,k] = ar_in2[i,j,k]
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef void medianfilter(f_csd_t[:, :, ::1] ar_in1, f_csd_t[:, :, ::1] ar_in2, int k_x, int k_y, int k_z, int nthreads):
	cdef cnumpy.int64_t i,j,k,idx
	cdef cnumpy.int64_t x,y,z
	cdef cnumpy.int64_t mx,my,mz
	cdef cnumpy.int64_t kx = ((aabs(k_x) - 1)//2)*2 +1
	cdef cnumpy.int64_t ky = ((aabs(k_y) - 1)//2)*2 +1
	cdef cnumpy.int64_t kz = ((aabs(k_z) - 1)//2)*2 +1
	cdef double phase
	cdef double* karray_buff
	cdef float phasef
	cdef float* karray_bufff
	if f_csd_t is cdouble:
		with nogil, parallel(num_threads=nthreads):
			karray_buff = <double *> malloc(sizeof(double) * (kx*ky*kz))
			if karray_buff is NULL:
				abort()
			for x in prange(ar_in1.shape[0]):
				for y in prange(ar_in1.shape[1]):
					for z in prange(ar_in1.shape[2]):
						for i in range(kx):
							for j in range(ky):
								for k in range(kz):
									mx = x + i - kx//2
									my = y + j - ky//2
									mz = z + k - kz//2
									if mx < 0: mx = 0;
									if mx > (ar_in1.shape[0] -1): mx = (ar_in1.shape[0] -1);
									if my < 0: my = 0;
									if my > (ar_in1.shape[1] -1): my = (ar_in1.shape[1] -1);
									if mz < 0: mz = 0;
									if mz > (ar_in1.shape[2] -1): mz = (ar_in1.shape[2] -1);
									idx = (k+(kz)*(j+(ky)*i))
									karray_buff[idx] = sqrt(ar_in1[mx,my,mz].real * ar_in1[mx,my,mz].real\
														+ar_in1[mx,my,mz].imag * ar_in1[mx,my,mz].imag)
						qsort(karray_buff, kx*ky*kz, cython.sizeof(cython.double),compare)
						phase = atan2(ar_in1[x,y,z].imag, ar_in1[x,y,z].real)
						ar_in2[x,y,z] = karray_buff[kx*ky*kz//2]*cos(phase) + 1j * karray_buff[kx*ky*kz//2] * sin(phase)
			free(karray_buff)
	elif f_csd_t is csingle:
		with nogil, parallel(num_threads=nthreads):
			karray_bufff = <float *> malloc(sizeof(float) * (kx*ky*kz))
			if karray_bufff is NULL:
				abort()
			for x in prange(ar_in1.shape[0]):
				for y in prange(ar_in1.shape[1]):
					for z in prange(ar_in1.shape[2]):
						for i in range(kx):
							for j in range(ky):
								for k in range(kz):
									mx = x + i - kx//2
									my = y + j - ky//2
									mz = z + k - kz//2
									if mx < 0: mx = 0;
									if mx > (ar_in1.shape[0] -1): mx = (ar_in1.shape[0] -1);
									if my < 0: my = 0;
									if my > (ar_in1.shape[1] -1): my = (ar_in1.shape[1] -1);
									if mz < 0: mz = 0;
									if mz > (ar_in1.shape[2] -1): mz = (ar_in1.shape[2] -1);
									idx = (k+(kz)*(j+(ky)*i))
									karray_bufff[idx] = sqrtf(<float> (ar_in1[mx,my,mz].real * ar_in1[mx,my,mz].real\
														+ar_in1[mx,my,mz].imag * ar_in1[mx,my,mz].imag))
						qsort(karray_bufff, kx*ky*kz, cython.sizeof(cython.float),compare)
						phasef = atan2f(ar_in1[x,y,z].imag, ar_in1[x,y,z].real)
						ar_in2[x,y,z] = karray_bufff[kx*ky*kz//2]*cosf(phasef) + 1j * karray_bufff[kx*ky*kz//2] * sinf(phasef)
			free(karray_bufff)
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef void blanklinefill(f_csd_t[:, :, ::1] ar_in1, f_csd_t[:, :, ::1] ar_in2,\
						int k_x, int k_y, int k_z,\
						int x1, int x2, int y1, int y2, int z1, int z2):
	cdef cnumpy.int64_t i,j,k,idx
	cdef cnumpy.int64_t x,y,z
	cdef cnumpy.int64_t mx,my,mz
	cdef double ksum = 0.0
	cdef double kcount = 0.0
	cdef double kvalue = 0.0
	cdef double c1 = 1.0
	cdef float ksumf = 0.0
	cdef float kcountf = 0.0
	cdef float kvaluef = 0.0
	cdef float c1f = 1.0
	cdef cnumpy.int64_t kx = ((aabs(k_x) - 1)//2)*2 +1
	cdef cnumpy.int64_t ky = ((aabs(k_y) - 1)//2)*2 +1
	cdef cnumpy.int64_t kz = ((aabs(k_z) - 1)//2)*2 +1
	z2 = z2+1
	y2 = y2+1
	x2 = x2+1
	if f_csd_t is cdouble:
		with nogil:
			for x in range(x1, x2, 1):
				for y in range(y1, y2, 1):
					for z in range(z1, z2, 1):
						ksum = 0.0
						kcount = 0.0
						kvalue = 0.0
						for i in range(kx):
							for j in range(ky):
								for k in range(kz):
									mx = x + i - kx//2
									my = y + j - ky//2
									mz = z + k - kz//2
									if mx < 0: mx = 0;
									if mx > (ar_in1.shape[0] -1): mx = (ar_in1.shape[0] -1);
									if my < 0: my = 0;
									if my > (ar_in1.shape[1] -1): my = (ar_in1.shape[1] -1);
									if mz < 0: mz = 0;
									if mz > (ar_in1.shape[2] -1): mz = (ar_in1.shape[2] -1);
									kvalue = sqrt(ar_in1[mx,my,mz].real * ar_in1[mx,my,mz].real\
														+ar_in1[mx,my,mz].imag * ar_in1[mx,my,mz].imag)
									ksum += kvalue
									kcount += c1
						if kcount < 1.0:
							ar_in2[x,y,z] = 0.0
						else:
							ar_in2[x,y,z] = ksum/kcount
			for x in range(x1, x2, 1):
				for y in range(y1, y2, 1):
					for z in range(z1, z2, 1):
						ar_in1[x,y,z] = ar_in2[x,y,z]
	elif f_csd_t is csingle:
		with nogil:
			for x in range(x1, x2, 1):
				for y in range(y1, y2, 1):
					for z in range(z1, z2, 1):
						ksumf = 0.0
						kcountf = 0.0
						kvaluef = 0.0
						for i in range(kx):
							for j in range(ky):
								for k in range(kz):
									mx = x + i - kx//2
									my = y + j - ky//2
									mz = z + k - kz//2
									if mx < 0: mx = 0;
									if mx > (ar_in1.shape[0] -1): mx = (ar_in1.shape[0] -1);
									if my < 0: my = 0;
									if my > (ar_in1.shape[1] -1): my = (ar_in1.shape[1] -1);
									if mz < 0: mz = 0;
									if mz > (ar_in1.shape[2] -1): mz = (ar_in1.shape[2] -1);
									kvaluef = sqrtf(<float> (ar_in1[mx,my,mz].real * ar_in1[mx,my,mz].real\
														+ar_in1[mx,my,mz].imag * ar_in1[mx,my,mz].imag))
									ksumf += kvaluef
									kcountf += c1f
						if kcountf < 1.0:
							ar_in2[x,y,z] = 0.0
						else:
							ar_in2[x,y,z] = ksumf/kcountf
			for x in range(x1, x2, 1):
				for y in range(y1, y2, 1):
					for z in range(z1, z2, 1):
						ar_in1[x,y,z] = ar_in2[x,y,z]
@cython.boundscheck(False)
@cython.wraparound(False)
cdef void _rshio(f_csd_t[:, :, ::1] seqdata, f_csd_t[:, :, ::1] rhom1, f_csd_t[:, :, ::1] support, int size, double beta, int nthreads) noexcept nogil:
	cdef double* seqdata_buff = <double*> &seqdata[0,0,0]
	cdef double* rhom1_buff = <double*> &rhom1[0,0,0]
	cdef double* support_buff = <double*> &support[0,0,0]
	cdef float* seqdataf_buff = <float*> &seqdata[0,0,0]
	cdef float* rhom1f_buff = <float*> &rhom1[0,0,0]
	cdef float* supportf_buff = <float*> &support[0,0,0]
	cdef cnumpy.int64_t i
	cdef float betaf = <float> beta
	if f_csd_t is cdouble:
		for i in prange(size, num_threads=nthreads):
			if support_buff[2*i] < 0.5:
				seqdata_buff[2*i] = rhom1_buff[2*i] - seqdata_buff[2*i] * beta
				seqdata_buff[2*i+1] = rhom1_buff[2*i+1] - seqdata_buff[2*i+1] * beta
	elif f_csd_t is csingle:
		for i in prange(size, num_threads=nthreads):
			if supportf_buff[2*i] < 0.5:
				seqdataf_buff[2*i] = rhom1f_buff[2*i] - seqdataf_buff[2*i] * betaf
				seqdataf_buff[2*i+1] = rhom1f_buff[2*i+1] - seqdataf_buff[2*i+1] * betaf
cpdef rshio(f_csd_t[:, :, ::1] seqdata, f_csd_t[:, :, ::1] rhom1, f_csd_t[:, :, ::1] support, double beta, int nthreads):
	cdef int size = seqdata.size
	with nogil:
		_rshio(seqdata, rhom1, support, size, beta, nthreads)
@cython.boundscheck(False)
@cython.wraparound(False)
cdef void _rshiop(f_csd_t[:, :, ::1] seqdata, f_csd_t[:, :, ::1] rhom1, f_csd_t[:, :, ::1] support, int size, double beta, int nthreads) noexcept nogil:
	cdef double* seqdata_buff = <double*> &seqdata[0,0,0]
	cdef double* rhom1_buff = <double*> &rhom1[0,0,0]
	cdef double* support_buff = <double*> &support[0,0,0]
	cdef float* seqdataf_buff = <float*> &seqdata[0,0,0]
	cdef float* rhom1f_buff = <float*> &rhom1[0,0,0]
	cdef float* supportf_buff = <float*> &support[0,0,0]
	cdef cnumpy.int64_t i
	cdef float betaf = <float> beta
	if f_csd_t is cdouble:
		for i in prange(size, num_threads=nthreads):
			if support_buff[2*i] < 0.5 or (seqdata_buff[2*i] < 0.0 and seqdata_buff[2*i+1] < 0.0):
				seqdata_buff[2*i] = rhom1_buff[2*i] - seqdata_buff[2*i] * beta
				seqdata_buff[2*i+1] = rhom1_buff[2*i+1] - seqdata_buff[2*i+1] * beta
	elif f_csd_t is csingle:
		for i in prange(size, num_threads=nthreads):
			if supportf_buff[2*i] < 0.5 or (seqdataf_buff[2*i] < 0.0 and seqdataf_buff[2*i+1] < 0.0):
				seqdataf_buff[2*i] = rhom1f_buff[2*i] - seqdataf_buff[2*i] * betaf
				seqdataf_buff[2*i+1] = rhom1f_buff[2*i+1] - seqdataf_buff[2*i+1] * betaf
cpdef rshiop(f_csd_t[:, :, ::1] seqdata, f_csd_t[:, :, ::1] rhom1, f_csd_t[:, :, ::1] support, double beta, int nthreads):
	cdef int size = seqdata.size
	with nogil:
		_rshiop(seqdata, rhom1, support, size, beta, nthreads)
@cython.boundscheck(False)
@cython.wraparound(False)
cdef void _rspchio(f_csd_t[:, :, ::1] seqdata, f_csd_t[:, :, ::1] rhom1, f_csd_t[:, :, ::1] support, int size, double beta, double phasemax, double phasemin, int nthreads) noexcept nogil:
	cdef double* seqdata_buff = <double*> &seqdata[0,0,0]
	cdef double* rhom1_buff = <double*> &rhom1[0,0,0]
	cdef double* support_buff = <double*> &support[0,0,0]
	cdef float* seqdataf_buff = <float*> &seqdata[0,0,0]
	cdef float* rhom1f_buff = <float*> &rhom1[0,0,0]
	cdef float* supportf_buff = <float*> &support[0,0,0]
	cdef cnumpy.int64_t i
	cdef float betaf = <float> beta
	cdef float phasemaxf = <float> phasemax
	cdef float phaseminf = <float> phasemin
	cdef double phase
	cdef float phasef
	if f_csd_t is cdouble:
		for i in prange(size, num_threads=nthreads):
			phase = atan2(seqdata_buff[2*i+1], seqdata_buff[2*i])
			if support_buff[2*i] < 0.5 or phase > phasemax or phase < phasemin:
				seqdata_buff[2*i] = rhom1_buff[2*i] - seqdata_buff[2*i] * beta
				seqdata_buff[2*i+1] = rhom1_buff[2*i+1] - seqdata_buff[2*i+1] * beta
	elif f_csd_t is csingle:
		for i in prange(size, num_threads=nthreads):
			phasef = atan2f(seqdataf_buff[2*i+1], seqdataf_buff[2*i])
			if supportf_buff[2*i] < 0.5 or phasef > phasemaxf or phasef < phaseminf:
				seqdataf_buff[2*i] = rhom1f_buff[2*i] - seqdataf_buff[2*i] * betaf
				seqdataf_buff[2*i+1] = rhom1f_buff[2*i+1] - seqdataf_buff[2*i+1] * betaf
cpdef rspchio(f_csd_t[:, :, ::1] seqdata, f_csd_t[:, :, ::1] rhom1, f_csd_t[:, :, ::1] support, double beta, double phasemax, double phasemin, int nthreads):
	cdef int size = seqdata.size
	with nogil:
		_rspchio(seqdata, rhom1, support, size, beta, phasemax, phasemin, nthreads)
@cython.boundscheck(False)
@cython.wraparound(False)
cdef void _rspgchio(f_csd_t[:, :, ::1] seqdata, f_csd_t[:, :, ::1] rhom1, f_csd_t[:, :, ::1] support, f_csd_t[:, :, ::1] tmpdata, int size, double beta, double phasemax, double phasemin, double q_x, double q_y, double q_z, int nthreads) noexcept nogil:
	cdef double* seqdata_buff = <double*> &seqdata[0,0,0]
	cdef double* rhom1_buff = <double*> &rhom1[0,0,0]
	cdef double* support_buff = <double*> &support[0,0,0]
	cdef double* tmpdata_buff = <double*> &tmpdata[0,0,0]
	cdef float* seqdataf_buff = <float*> &seqdata[0,0,0]
	cdef float* rhom1f_buff = <float*> &rhom1[0,0,0]
	cdef float* supportf_buff = <float*> &support[0,0,0]
	cdef float* tmpdataf_buff = <float*> &tmpdata[0,0,0]
	cdef cnumpy.int64_t iz, iy, ix, i
	cdef cnumpy.int64_t iz1, iy1, ix1
	cdef cnumpy.int64_t z1, y1, x1
	cdef float betaf = <float> beta
	cdef double phase
	cdef double phaseq
	cdef float phasef
	cdef float phaseqf
	cdef double qmag = sqrt(q_x*q_x + q_y*q_y + q_z*q_z)
	cdef double qx = q_x / qmag;
	cdef double qy = q_y / qmag;
	cdef double qz = q_z / qmag;
	if qx > 0:
		x1 = 1
	else:
		x1 = -1
	if qy > 0:
		y1 = 1
	else:
		y1 = -1
	if qz > 0:
		z1 = 1
	else:
		z1 = -1
	cdef float qxf = <float> qx
	cdef float qyf = <float> qy
	cdef float qzf = <float> qz
	tmpdata[:,:,:] = seqdata
	if f_csd_t is cdouble:
		for ix in prange(seqdata.shape[0], num_threads=nthreads):
			for iy in prange(seqdata.shape[1], num_threads=nthreads):
				for iz in prange(seqdata.shape[2], num_threads=nthreads):
					i=((iz)+(seqdata.shape[2])*((iy)+(seqdata.shape[1])*(ix)));
					ix1=((iz)+(seqdata.shape[2])*((iy)+(seqdata.shape[1])*(modclip(ix+x1, seqdata.shape[0] - 1))));
					iy1=((iz)+(seqdata.shape[2])*((modclip(iy+y1, seqdata.shape[1] - 1))+(seqdata.shape[1])*ix));
					iz1=((modclip(iz+z1, seqdata.shape[2] - 1))+(seqdata.shape[2])*((iy)+(seqdata.shape[1])*(ix)));
					phase = atan2(tmpdata_buff[2*i+1], tmpdata_buff[2*i])
					phaseq = fabs( qx * (phase - atan2(tmpdata_buff[2*ix1+1], tmpdata_buff[2*ix1]) )\
								+ qy * (phase - atan2(tmpdata_buff[2*iy1+1], tmpdata_buff[2*iy1]) )\
								+ qz * (phase - atan2(tmpdata_buff[2*iz1+1], tmpdata_buff[2*iz1]) ) )
					if support_buff[2*i] < 0.5 or phaseq > phasemax or phaseq < phasemin:
						seqdata_buff[2*i] = rhom1_buff[2*i] - seqdata_buff[2*i] * beta
						seqdata_buff[2*i+1] = rhom1_buff[2*i+1] - seqdata_buff[2*i+1] * beta
	elif f_csd_t is csingle:
		for ix in prange(seqdata.shape[0], num_threads=nthreads):
			for iy in prange(seqdata.shape[1], num_threads=nthreads):
				for iz in prange(seqdata.shape[2], num_threads=nthreads):
					i=((iz)+(seqdata.shape[2])*((iy)+(seqdata.shape[1])*(ix)));
					ix1=((iz)+(seqdata.shape[2])*((iy)+(seqdata.shape[1])*(modclip(ix+x1, seqdata.shape[0] - 1))));
					iy1=((iz)+(seqdata.shape[2])*((modclip(iy+y1, seqdata.shape[1] - 1))+(seqdata.shape[1])*ix));
					iz1=((modclip(iz+z1, seqdata.shape[2] - 1))+(seqdata.shape[2])*((iy)+(seqdata.shape[1])*(ix)));
					phasef = atan2f(tmpdataf_buff[2*i+1], tmpdataf_buff[2*i])
					phaseqf = fabsf( qxf * (phasef - atan2f(tmpdataf_buff[2*ix1+1], tmpdataf_buff[2*ix1]) )\
								+ qyf * (phasef - atan2f(tmpdataf_buff[2*iy1+1], tmpdataf_buff[2*iy1]) )\
								+ qzf * (phasef - atan2f(tmpdataf_buff[2*iz1+1], tmpdataf_buff[2*iz1]) ) )
					if supportf_buff[2*i] < 0.5 or phaseqf > phasemax or phaseqf < phasemin:
						seqdataf_buff[2*i] = rhom1f_buff[2*i] - seqdataf_buff[2*i] * betaf
						seqdataf_buff[2*i+1] = rhom1f_buff[2*i+1] - seqdataf_buff[2*i+1] * betaf
cpdef rspgchio(f_csd_t[:, :, ::1] seqdata, f_csd_t[:, :, ::1] rhom1, f_csd_t[:, :, ::1] support, f_csd_t[:, :, ::1] tmpdata, double beta, double phasemax, double phasemin, double qx, double qy, double qz, int nthreads):
	cdef int size = seqdata.size
	with nogil:
		_rspgchio(seqdata, rhom1, support, tmpdata, size, beta, phasemax, phasemin, qx, qy, qz, nthreads)
@cython.boundscheck(False)
@cython.wraparound(False)
cdef void _rser(f_csd_t[:, :, ::1] seqdata, f_csd_t[:, :, ::1] rhom1, f_csd_t[:, :, ::1] support, int size, int nthreads) noexcept nogil:
	cdef double* seqdata_buff = <double*> &seqdata[0,0,0]
	cdef double* rhom1_buff = <double*> &rhom1[0,0,0]
	cdef double* support_buff = <double*> &support[0,0,0]
	cdef float* seqdataf_buff = <float*> &seqdata[0,0,0]
	cdef float* rhom1f_buff = <float*> &rhom1[0,0,0]
	cdef float* supportf_buff = <float*> &support[0,0,0]
	cdef cnumpy.int64_t i
	if f_csd_t is cdouble:
		for i in prange(size, num_threads=nthreads):
			if support_buff[2*i] < 0.5:
				seqdata_buff[2*i] = 0.0
				seqdata_buff[2*i+1] = 0.0
	elif f_csd_t is csingle:
		for i in prange(size, num_threads=nthreads):
			if supportf_buff[2*i] < 0.5:
				seqdataf_buff[2*i] = 0.0
				seqdataf_buff[2*i+1] = 0.0
cpdef rser(f_csd_t[:, :, ::1] seqdata, f_csd_t[:, :, ::1] rhom1, f_csd_t[:, :, ::1] support, int nthreads):
	cdef int size = seqdata.size
	with nogil:
		_rser(seqdata, rhom1, support, size, nthreads)
@cython.boundscheck(False)
@cython.wraparound(False)
cdef void _rspoer(f_csd_t[:, :, ::1] seqdata, f_csd_t[:, :, ::1] rhom1, f_csd_t[:, :, ::1] support, int size, int nthreads) noexcept nogil:
	cdef double* seqdata_buff = <double*> &seqdata[0,0,0]
	cdef double* rhom1_buff = <double*> &rhom1[0,0,0]
	cdef double* support_buff = <double*> &support[0,0,0]
	cdef float* seqdataf_buff = <float*> &seqdata[0,0,0]
	cdef float* rhom1f_buff = <float*> &rhom1[0,0,0]
	cdef float* supportf_buff = <float*> &support[0,0,0]
	cdef cnumpy.int64_t i
	cdef double amp
	cdef float ampf
	if f_csd_t is cdouble:
		for i in prange(size, num_threads=nthreads):
			amp = sqrt(seqdata_buff[2*i] * seqdata_buff[2*i] + seqdata_buff[2*i+1] * seqdata_buff[2*i+1])
			if support_buff[2*i] < 0.5 and seqdata_buff[2*i] >= 0.0:
				seqdata_buff[2*i] = amp
				seqdata_buff[2*i+1] = 0.0
			elif support_buff[2*i] < 0.5 and seqdata_buff[2*i] < 0.0:
				seqdata_buff[2*i] = -amp
				seqdata_buff[2*i+1] = 0.0
	elif f_csd_t is csingle:
		for i in prange(size, num_threads=nthreads):
			ampf = sqrtf(seqdataf_buff[2*i] * seqdataf_buff[2*i] + seqdataf_buff[2*i+1] * seqdataf_buff[2*i+1])
			if supportf_buff[2*i] < 0.5  and seqdataf_buff[2*i] >= 0.0:
				seqdataf_buff[2*i] = ampf
				seqdataf_buff[2*i+1] = 0.0
			elif supportf_buff[2*i] < 0.5  and seqdataf_buff[2*i] < 0.0:
				seqdataf_buff[2*i] = -ampf
				seqdataf_buff[2*i+1] = 0.0
cpdef rspoer(f_csd_t[:, :, ::1] seqdata, f_csd_t[:, :, ::1] rhom1, f_csd_t[:, :, ::1] support, int nthreads):
	cdef int size = seqdata.size
	with nogil:
		_rspoer(seqdata, rhom1, support, size, nthreads)
@cython.boundscheck(False)
@cython.wraparound(False)
cdef void _rshpr(f_csd_t[:, :, ::1] seqdata, f_csd_t[:, :, ::1] rhom1, f_csd_t[:, :, ::1] support, int size, double beta, int nthreads) noexcept nogil:
	cdef double* seqdata_buff = <double*> &seqdata[0,0,0]
	cdef double* rhom1_buff = <double*> &rhom1[0,0,0]
	cdef double* support_buff = <double*> &support[0,0,0]
	cdef float* seqdataf_buff = <float*> &seqdata[0,0,0]
	cdef float* rhom1f_buff = <float*> &rhom1[0,0,0]
	cdef float* supportf_buff = <float*> &support[0,0,0]
	cdef cnumpy.int64_t i
	cdef float betaf = <float> beta
	if f_csd_t is cdouble:
		for i in prange(size, num_threads=nthreads):
			if support_buff[2*i] < 0.5 or ((2*seqdata_buff[2*i] - rhom1_buff[2*i])  < (1.0 - beta)*seqdata_buff[2*i]  and  (2*seqdata_buff[2*i+1] - rhom1_buff[2*i+1])  < (1.0 - beta)*seqdata_buff[2*i+1]):
				seqdata_buff[2*i] = rhom1_buff[2*i] - seqdata_buff[2*i] * beta
				seqdata_buff[2*i+1] = rhom1_buff[2*i+1] - seqdata_buff[2*i+1] * beta
	elif f_csd_t is csingle:
		for i in prange(size, num_threads=nthreads):
			if supportf_buff[2*i] < 0.5 or ((2*seqdataf_buff[2*i] - rhom1f_buff[2*i])  < (1.0 - betaf)*seqdataf_buff[2*i]  and  (2*seqdataf_buff[2*i+1] - rhom1f_buff[2*i+1])  < (1.0 - betaf)*seqdataf_buff[2*i+1]):
				seqdataf_buff[2*i] = rhom1f_buff[2*i] - seqdataf_buff[2*i] * betaf
				seqdataf_buff[2*i+1] = rhom1f_buff[2*i+1] - seqdataf_buff[2*i+1] * betaf
cpdef rshpr(f_csd_t[:, :, ::1] seqdata, f_csd_t[:, :, ::1] rhom1, f_csd_t[:, :, ::1] support, double beta, int nthreads):
	cdef int size = seqdata.size
	with nogil:
		_rshpr(seqdata, rhom1, support, size, beta, nthreads)
@cython.boundscheck(False)
@cython.wraparound(False)
cdef void _rsraar(f_csd_t[:, :, ::1] seqdata, f_csd_t[:, :, ::1] rhom1, f_csd_t[:, :, ::1] support, int size, double beta, int nthreads) noexcept nogil:
	cdef double* seqdata_buff = <double*> &seqdata[0,0,0]
	cdef double* rhom1_buff = <double*> &rhom1[0,0,0]
	cdef double* support_buff = <double*> &support[0,0,0]
	cdef float* seqdataf_buff = <float*> &seqdata[0,0,0]
	cdef float* rhom1f_buff = <float*> &rhom1[0,0,0]
	cdef float* supportf_buff = <float*> &support[0,0,0]
	cdef cnumpy.int64_t i
	cdef double c1 = 1.0
	cdef double c2 = 2.0
	cdef float c1f = 1.0
	cdef float c2f = 2.0
	cdef float betaf = <float> beta
	if f_csd_t is cdouble:
		for i in prange(size, num_threads=nthreads):
			if support_buff[2*i] < 0.5 or (( 2.0*seqdata_buff[2*i] - rhom1_buff[2*i] ) < 0.0 and ( 2.0*seqdata_buff[2*i+1] - rhom1_buff[2*i+1] ) < 0.0 ):
				seqdata_buff[2*i] = beta * rhom1_buff[2*i] - seqdata_buff[2*i] * ( c1 - c2*beta )
				seqdata_buff[2*i+1] = beta * rhom1_buff[2*i+1] - seqdata_buff[2*i+1] * ( c1 - c2*beta )
	elif f_csd_t is csingle:
		for i in prange(size, num_threads=nthreads):
			if supportf_buff[2*i] < 0.5 or (( 2.0*seqdataf_buff[2*i] - rhom1f_buff[2*i] ) < 0.0 and ( 2.0*seqdataf_buff[2*i+1] - rhom1f_buff[2*i+1] ) < 0.0 ):
				seqdataf_buff[2*i] = betaf * rhom1f_buff[2*i] - seqdataf_buff[2*i] * ( c1f - c2f*betaf )
				seqdataf_buff[2*i+1] = betaf * rhom1f_buff[2*i+1] - seqdataf_buff[2*i+1] * ( c1f - c2f*betaf )
cpdef rsraar(f_csd_t[:, :, ::1] seqdata, f_csd_t[:, :, ::1] rhom1, f_csd_t[:, :, ::1] support, double beta, int nthreads):
	cdef int size = seqdata.size
	with nogil:
		_rsraar(seqdata, rhom1, support, size, beta, nthreads)
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef void cshio_dp(f_csd_t[:, :, ::1] ar_in1, f_csd_t[:, :, ::1] ar_in2, f_csd_t[:, :, ::1] elp, double p, double epsilon, int nthreads):
	cdef cnumpy.int64_t i,j,k
	cdef double amp1, amp2, amp1_sqrt, i_wgt
	cdef double gamma, gamma_pm2
	for i in prange(ar_in1.shape[0], nogil=True, num_threads=nthreads):
		for j in prange(ar_in1.shape[1], num_threads=nthreads):
			for k in prange(ar_in1.shape[2], num_threads=nthreads):
				amp1 = ar_in1[i,j,k].real*ar_in1[i,j,k].real + ar_in1[i,j,k].imag*ar_in1[i,j,k].imag
				amp2 = ar_in2[i,j,k].real*ar_in2[i,j,k].real + ar_in2[i,j,k].imag*ar_in2[i,j,k].imag
				amp1_sqrt = sqrt( amp1 )
				i_wgt =  1.0 / sqrt( amp2+epsilon )
				gamma = i_wgt*amp1 - amp1_sqrt
				gamma_pm2 = pow( fabs(gamma), (p - 2.0) )
				elp[i,j,k] = 0.5*fabs(p)*gamma*gamma_pm2*( 2.0*i_wgt*ar_in1[i,j,k] - (ar_in1[i,j,k] / amp1_sqrt) )
@cython.boundscheck(False)
@cython.wraparound(False)
cdef inline double SOMatVecProd(f_sd_t[:,:] H, f_sd_t[:] y, f_sd_t[:] dtau) noexcept nogil:
	dtau[0] = H[0][0]*y[0] + H[0][1]*y[1]
	dtau[1] = H[1][0]*y[0] + H[1][1]*y[1]
@cython.boundscheck(False)
@cython.wraparound(False)
cdef inline double SOVecNorm(f_sd_t[:] vec) noexcept nogil:
	return sqrt(vec[0]*vec[0]+vec[1]*vec[1])
@cython.boundscheck(False)
@cython.wraparound(False)
cdef inline double SOMatInv(f_sd_t[:,:] H) noexcept nogil:
	cdef double[2][2] Htmp
	cdef double determ = 1.0/(H[0][0]*H[1][1] - H[0][1]*H[1][0])
	Htmp[0][0] = H[1][1]
	Htmp[1][1] = H[0][0]
	Htmp[0][1] = -H[0][1]
	Htmp[1][0] = -H[1][0]
	H[0][0] = Htmp[0][0]*determ
	H[0][1] = Htmp[0][1]*determ
	H[1][0] = Htmp[1][0]*determ
	H[1][1] = Htmp[1][1]*determ
@cython.boundscheck(False)
@cython.wraparound(False)
cdef inline double LGradS(f_csd_t* rho, f_csd_t* rho_m1, int idx) noexcept nogil:
	if idx == 0:
		return (rho[0].real - rho_m1[0].real)
	else:
		return (rho[0].imag - rho_m1[0].imag)
@cython.boundscheck(False)
@cython.wraparound(False)
cdef inline double LGradnS(f_csd_t* rho, f_csd_t* rho_m1, int idx) noexcept nogil:
	if idx == 0:
		return -rho[0].real
	else:
		return -rho[0].imag
@cython.boundscheck(False)
@cython.wraparound(False)
cdef inline double wLGradS(f_csd_t* rho, f_csd_t* rho_m1, f_csd_t* rho_m2, int idx) noexcept nogil:
	cdef double ampT = sqrt(rho_m2[0].real*rho_m2[0].real + rho_m2[0].imag*rho_m2[0].imag)
	cdef double epsilon
	if ampT > 1e-6:
		epsilon = 0.0
	else:
		epsilon = 1.0
	if idx == 0:
		return (1.0 / ( ampT+epsilon ))*(rho[0].real - rho_m1[0].real)
	else:
		return (1.0 / ( ampT+epsilon ))*(rho[0].imag - rho_m1[0].imag)
@cython.boundscheck(False)
@cython.wraparound(False)
cdef inline double wLGradnS(f_csd_t* rho, f_csd_t* rho_m1, f_csd_t* rho_m2, int idx) noexcept nogil:
	cdef double ampT = sqrt(rho_m2[0].real*rho_m2[0].real + rho_m2[0].imag*rho_m2[0].imag)
	cdef double epsilon
	if ampT > 1e-6:
		epsilon = 0.0
	else:
		epsilon = 1.0
	if idx == 0:
		return (-(1.0 / ( ampT+epsilon ))*rho[0].real + ((1.0 / ( ampT+epsilon ))-1.0)*rho_m1[0].real)
	else:
		return (-(1.0 / ( ampT+epsilon ))*rho[0].imag + ((1.0 / ( ampT+epsilon ))-1.0)*rho_m1[0].imag);
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef void SOGradStep(f_csd_t[:, :, ::1] rho, f_csd_t[:, :, ::1] support, f_csd_t[:, :, ::1] rho_m1,\
						f_csd_t[:, :, ::1] rho_m2, f_csd_t[:, :, ::1] grad,\
						double[:] step, cnumpy.int32_t[:] citer_flow, int startiter, int nthreads):
	cdef cnumpy.int64_t i,j,k
	if step[6] >= 0.0 and step[6] < (<double> citer_flow[0] - startiter):
		for i in prange(rho.shape[0], nogil=True, num_threads=nthreads):
			for j in prange(rho.shape[1], num_threads=nthreads):
				for k in prange(rho.shape[2], num_threads=nthreads):
					if support[i,j,k].real > 0.5:
						grad[i,j,k] = wLGradS(&rho[i,j,k], &rho_m1[i,j,k], &rho_m2[i,j,k], 0) +\
									1j * wLGradS(&rho[i,j,k], &rho_m1[i,j,k], &rho_m2[i,j,k], 1)
					else:
						grad[i,j,k] = wLGradnS(&rho[i,j,k], &rho_m1[i,j,k], &rho_m2[i,j,k], 0) +\
									1j * wLGradnS(&rho[i,j,k], &rho_m1[i,j,k], &rho_m2[i,j,k], 1)
	else:
		for i in prange(rho.shape[0], nogil=True, num_threads=nthreads):
			for j in prange(rho.shape[1], num_threads=nthreads):
				for k in prange(rho.shape[2], num_threads=nthreads):
					if support[i,j,k].real > 0.5:
						grad[i,j,k] = LGradS(&rho[i,j,k], &rho_m1[i,j,k], 0) +\
									1j * LGradS(&rho[i,j,k], &rho_m1[i,j,k], 1)
					else:
						grad[i,j,k] = LGradnS(&rho[i,j,k], &rho_m1[i,j,k], 0) +\
									1j * LGradnS(&rho[i,j,k], &rho_m1[i,j,k], 1)
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef double SOFrobSupport(f_csd_t[:, :, ::1] grad1, f_csd_t[:, :, ::1] grad2, f_csd_t[:, :, ::1] support, int nthreads):
	cdef cnumpy.int64_t i,j,k
	cdef double gsum_s = 0.0
	cdef double gsum_ns = 0.0
	cdef double phi = 0.0
	for i in prange(grad1.shape[0], nogil=True, num_threads=nthreads):
		for j in prange(grad1.shape[1], num_threads=nthreads):
			for k in prange(grad1.shape[2], num_threads=nthreads):
				if support[i,j,k].real > 0.5:
					gsum_s += grad1[i,j,k].real*grad2[i,j,k].real + grad1[i,j,k].imag*grad2[i,j,k].imag
				else:
					gsum_ns += grad1[i,j,k].real*grad2[i,j,k].real + grad1[i,j,k].imag*grad2[i,j,k].imag
	phi = sqrt(gsum_s*gsum_s+gsum_ns*gsum_ns)/(<double> (grad1.shape[0]*grad1.shape[1]*grad1.shape[2]))
	return phi
@cython.boundscheck(False)
@cython.wraparound(False)
cdef void MaskedSetAmplitudesZero(f_csd_t[:, :, ::1] seqdata, f_csd_t[:, :, ::1] expdata, f_csd_t[:, :, ::1] mask, int nthreads) noexcept nogil:
	cdef cnumpy.int64_t i,j,k
	cdef double amp = 0.0
	cdef double phase = 0.0
	for i in prange(seqdata.shape[0], nogil=True, num_threads=nthreads):
		for j in prange(seqdata.shape[1], num_threads=nthreads):
			for k in prange(seqdata.shape[2], num_threads=nthreads):
				if mask[i,j,k].real > 0.5:
					amp = sqrt( expdata[i,j,k].real*expdata[i,j,k].real + expdata[i,j,k].imag*expdata[i,j,k].imag )
					phase = atan2(seqdata[i,j,k].imag, seqdata[i,j,k].real)
					seqdata[i,j,k] = amp*cos(phase) + 1j * amp*sin(phase)
				else:
					seqdata[i,j,k] = 0.0
@cython.boundscheck(False)
@cython.wraparound(False)
cdef void MaskedSetAmplitudes(f_csd_t[:, :, ::1] seqdata, f_csd_t[:, :, ::1] expdata, f_csd_t[:, :, ::1] mask, int nthreads) noexcept nogil:
	cdef cnumpy.int64_t i,j,k
	cdef double amp = 0.0
	cdef double phase = 0.0
	for i in prange(seqdata.shape[0], nogil=True, num_threads=nthreads):
		for j in prange(seqdata.shape[1], num_threads=nthreads):
			for k in prange(seqdata.shape[2], num_threads=nthreads):
				if mask[i,j,k].real > 0.5:
					amp = sqrt( expdata[i,j,k].real*expdata[i,j,k].real + expdata[i,j,k].imag*expdata[i,j,k].imag )
					phase = atan2(seqdata[i,j,k].imag, seqdata[i,j,k].real)
					seqdata[i,j,k] = amp*cos(phase) + 1j * amp*sin(phase)
@cython.boundscheck(False)
@cython.wraparound(False)
cdef void SOGradPsi(f_csd_t[:, :, ::1] rho, f_csd_t[:, :, ::1] support, f_csd_t[:, :, ::1] rho_m1,\
						f_csd_t[:, :, ::1] rho_m2, f_csd_t[:, :, ::1] grad,\
						f_csd_t[:, :, ::1] expdata, f_csd_t[:, :, ::1] mask,\
						double[:] step, cnumpy.int32_t[:] citer_flow, int startiter,\
						double[:] tau, double[:] psi, FFTWPlan* plan, int nthreads) noexcept nogil:
	cdef cnumpy.int64_t i,j,k
	cdef double ampT = 0.0
	cdef double[2] psi0_tmp = [0.0,0.0]
	cdef double[2] psi1_tmp = [0.0,0.0]
	cdef double[2] newgrad = [0.0,0.0]
	if step[6] >= 0.0 and step[6] < (<double> (citer_flow[0] - startiter)):
		for i in prange(rho.shape[0], nogil=True, num_threads=nthreads):
			for j in prange(rho.shape[1], num_threads=nthreads):
				for k in prange(rho.shape[2], num_threads=nthreads):
					ampT = sqrt(rho_m2[i,j,k].real*rho_m2[i,j,k].real + rho_m2[i,j,k].imag*rho_m2[i,j,k].imag)
					if support[i,j,k].real > 0.5:
						rho[i,j,k] = rho_m1[i,j,k].real + tau[0]*grad[i,j,k].real*ampT +\
									1j * (rho_m1[i,j,k].imag + tau[0]*grad[i,j,k].imag*ampT)
					else:
						rho[i,j,k] = rho_m1[i,j,k].real + tau[1]*(grad[i,j,k].real*ampT - (1.0-ampT)*rho_m1[i,j,k].real) +\
									1j * (rho_m1[i,j,k].imag + tau[1]*(grad[i,j,k].imag*ampT - (1.0-ampT)*rho_m1[i,j,k].imag ))
	else:
		for i in prange(rho.shape[0], nogil=True, num_threads=nthreads):
			for j in prange(rho.shape[1], num_threads=nthreads):
				for k in prange(rho.shape[2], num_threads=nthreads):
					ampT = sqrt(rho_m2[i,j,k].real*rho_m2[i,j,k].real + rho_m2[i,j,k].imag*rho_m2[i,j,k].imag)
					if support[i,j,k].real > 0.5:
						rho[i,j,k] = rho_m1[i,j,k].real + tau[0]*grad[i,j,k].real*ampT +\
									1j * (rho_m1[i,j,k].imag + tau[0]*grad[i,j,k].imag*ampT)
					else:
						rho[i,j,k] = rho_m1[i,j,k].real + tau[1]*grad[i,j,k].real*ampT +\
									1j * (rho_m1[i,j,k].imag + tau[1]*grad[i,j,k].imag*ampT)
	if f_csd_t is cdouble:
		_fftw_stride(rho, rho, plan, FFTW_TORECIP, 1)
	elif f_csd_t is csingle:
		_fftwf_stride(rho, rho, plan, FFTW_TORECIP, 1)
	MaskedSetAmplitudesZero(rho, expdata, mask, nthreads)
	if f_csd_t is cdouble:
		_fftw_stride(rho, rho, plan, FFTW_TOREAL, 1)
	elif f_csd_t is csingle:
		_fftwf_stride(rho, rho, plan, FFTW_TOREAL, 1)
	if step[6] >= 0.0 and step[6] < (<double> (citer_flow[0] - startiter)):
		for i in prange(rho.shape[0], nogil=True, num_threads=nthreads):
			for j in prange(rho.shape[1], num_threads=nthreads):
				for k in prange(rho.shape[2], num_threads=nthreads):
					if support[i,j,k].real > 0.5:
						newgrad[0] = wLGradS(&rho[i,j,k], &rho_m1[i,j,k], &rho_m2[i,j,k], 0);
						newgrad[1] = wLGradS(&rho[i,j,k], &rho_m1[i,j,k], &rho_m2[i,j,k], 1);
						psi0_tmp[0] += grad[i,j,k].real*newgrad[0] + grad[i,j,k].imag*newgrad[1];
						psi0_tmp[1] += grad[i,j,k].real*newgrad[1] - grad[i,j,k].imag*newgrad[0];
					else:
						newgrad[0] = wLGradnS(&rho[i,j,k], &rho_m1[i,j,k], &rho_m2[i,j,k], 0);
						newgrad[1] = wLGradnS(&rho[i,j,k], &rho_m1[i,j,k], &rho_m2[i,j,k], 1);
						psi1_tmp[0] += grad[i,j,k].real*newgrad[0] + grad[i,j,k].imag*newgrad[1];
						psi1_tmp[1] += grad[i,j,k].real*newgrad[1] - grad[i,j,k].imag*newgrad[0];
	else:
		for i in prange(rho.shape[0], nogil=True, num_threads=nthreads):
			for j in prange(rho.shape[1], num_threads=nthreads):
				for k in prange(rho.shape[2], num_threads=nthreads):
					if support[i,j,k].real > 0.5:
						newgrad[0] = LGradS(&rho[i,j,k], &rho_m1[i,j,k], 0);
						newgrad[1] = LGradS(&rho[i,j,k], &rho_m1[i,j,k], 1);
						psi0_tmp[0] += grad[i,j,k].real*newgrad[0] + grad[i,j,k].imag*newgrad[1];
						psi0_tmp[1] += grad[i,j,k].real*newgrad[1] - grad[i,j,k].imag*newgrad[0];
					else:
						newgrad[0] = LGradnS(&rho[i,j,k], &rho_m1[i,j,k], 0);
						newgrad[1] = LGradnS(&rho[i,j,k], &rho_m1[i,j,k], 1);
						psi1_tmp[0] += grad[i,j,k].real*newgrad[0] + grad[i,j,k].imag*newgrad[1];
						psi1_tmp[1] += grad[i,j,k].real*newgrad[1] - grad[i,j,k].imag*newgrad[0];
	#psi[0] = -sqrt(psi0_tmp[0]*psi0_tmp[0]+psi0_tmp[1]*psi0_tmp[1])/(<double> len)
	#psi[1] = sqrt(psi1_tmp[0]*psi1_tmp[0]+psi1_tmp[1]*psi1_tmp[1])/(<double> len)
	psi[0] = -psi0_tmp[0]/(<double> (rho.shape[0]*rho.shape[1]*rho.shape[2]))
	psi[1] = psi1_tmp[0]/(<double> (rho.shape[0]*rho.shape[1]*rho.shape[2]))
@cython.boundscheck(False)
@cython.wraparound(False)
cdef void SOH(f_csd_t[:, :, ::1] rho, f_csd_t[:, :, ::1] support,\
						f_csd_t[:, :, ::1] rho_m2, f_csd_t[:, :, ::1] grad,\
						f_csd_t[:, :, ::1] expdata, f_csd_t[:, :, ::1] mask,\
						double[:] step, cnumpy.int32_t[:] citer_flow, int startiter,\
						double[:,:] H, double[:] y, double[:] dtau, double[:] steps, FFTWPlan* plan, int nthreads):
	cdef double[2] _Hydtau = [0.0,0.0]
	cdef double[:] Hydtau = _Hydtau
	cdef double[2] _Hy = [0.0,0.0]
	cdef double[:] Hy = _Hy
	cdef double[2][2] dH = [[0.0,0.0],[0.0,0.0]]
	cdef double denom
	cdef double erquad
	cdef double[2] dtau_scaled = [0.0,0.0]
	dtau_scaled[0] = steps[3]*dtau[0]
	dtau_scaled[1] = steps[3]*dtau[1]
	SOMatVecProd(H,y,Hy);
	Hydtau[0] = dtau_scaled[0] - Hy[0]
	Hydtau[1] = dtau_scaled[1] - Hy[1]
	erquad = sqrt(SOVecNorm(Hydtau)/(SOVecNorm(dtau)+SOVecNorm(Hy)))
	if erquad>1.0:
		SOTrueHi(rho, support, rho_m2, grad, expdata, mask, step, citer_flow, startiter, H, plan, nthreads)
		if steps[1] > steps[0]/4.0:
			steps[0] = steps[1]
		else:
			steps[0] = steps[0]/4.0
	elif erquad > 1e-2:
		denom = Hydtau[0]*y[0]+Hydtau[1]*y[1];
		dH[0][0] = Hydtau[0]*Hydtau[0]/denom;
		dH[0][1] = Hydtau[0]*Hydtau[1]/denom;
		dH[1][0] = Hydtau[1]*Hydtau[0]/denom;
		dH[1][1] = Hydtau[1]*Hydtau[1]/denom;
		H[0][0] = H[0][0] + dH[0][0];
		H[0][1] = H[0][1] + dH[0][1];
		H[1][0] = H[1][0] + dH[1][0];
		H[1][1] = H[1][1] + dH[1][1];
		if 2.0*steps[0] > steps[2]:
			steps[0] = steps[2]
		else:
			steps[0] = 2.0*steps[0]
	else:
		if 3.0*steps[0] > steps[2]:
			steps[0] = steps[2]
		else:
			steps[0] = 3.0*steps[0]
@cython.boundscheck(False)
@cython.wraparound(False)
cdef void SOTrueHi(f_csd_t[:, :, ::1] rho, f_csd_t[:, :, ::1] support,\
						f_csd_t[:, :, ::1] rho_m2, f_csd_t[:, :, ::1] grad,\
						f_csd_t[:, :, ::1] expdata, f_csd_t[:, :, ::1] mask,\
						double[:] step, cnumpy.int32_t[:] citer_flow, int startiter,\
						double[:,:] H, FFTWPlan* plan, int nthreads) noexcept nogil:
	cdef cnumpy.int64_t i,j,k
	cdef double[2] H0_tmp = [0.0,0.0]
	cdef double[2] H1_tmp = [0.0,0.0]
	cdef double[2] newgrad = [0.0,0.0]
	for i in prange(rho.shape[0], nogil=True, num_threads=nthreads):
		for j in prange(rho.shape[1], num_threads=nthreads):
			for k in prange(rho.shape[2], num_threads=nthreads):
				rho[i,j,k] = grad[i,j,k]
	if f_csd_t is cdouble:
		_fftw_stride(rho, rho, plan, FFTW_TORECIP, 1)
	elif f_csd_t is csingle:
		_fftwf_stride(rho, rho, plan, FFTW_TORECIP, 1)
	MaskedSetAmplitudes(rho, expdata, mask, nthreads)
	if f_csd_t is cdouble:
		_fftw_stride(rho, rho, plan, FFTW_TOREAL, 1)
	elif f_csd_t is csingle:
		_fftwf_stride(rho, rho, plan, FFTW_TOREAL, 1)
	if step[6] >= 0.0 and step[6] < (<double> citer_flow[0] - startiter):
		for i in prange(rho.shape[0], nogil=True, num_threads=nthreads):
			for j in prange(rho.shape[1], num_threads=nthreads):
				for k in prange(rho.shape[2], num_threads=nthreads):
					if support[i,j,k].real > 0.5:
						newgrad[0] = wLGradS(&rho[i,j,k], &grad[i,j,k], &rho_m2[i,j,k], 0)
						newgrad[1] = wLGradS(&rho[i,j,k], &grad[i,j,k], &rho_m2[i,j,k], 1)
						H0_tmp[0] -= grad[i,j,k].real*newgrad[0] + grad[i,j,k].imag*newgrad[1];
						H0_tmp[1] -= grad[i,j,k].imag*newgrad[0] - grad[i,j,k].real*newgrad[1];
					else:
						newgrad[0] = wLGradnS(&rho[i,j,k], &grad[i,j,k], &rho_m2[i,j,k], 0)
						newgrad[1] = wLGradnS(&rho[i,j,k], &grad[i,j,k], &rho_m2[i,j,k], 1)
						H0_tmp[0] -= grad[i,j,k].real*newgrad[0] + grad[i,j,k].imag*newgrad[1];
						H0_tmp[1] -= grad[i,j,k].imag*newgrad[0] - grad[i,j,k].real*newgrad[1];
	else:
		for i in prange(rho.shape[0], nogil=True, num_threads=nthreads):
			for j in prange(rho.shape[1], num_threads=nthreads):
				for k in prange(rho.shape[2], num_threads=nthreads):
					if support[i,j,k].real > 0.5:
						newgrad[0] = LGradS(&rho[i,j,k], &grad[i,j,k], 0)
						newgrad[1] = LGradS(&rho[i,j,k], &grad[i,j,k], 1)
						H0_tmp[0] -= grad[i,j,k].real*newgrad[0] + grad[i,j,k].imag*newgrad[1];
						H0_tmp[1] -= grad[i,j,k].imag*newgrad[0] - grad[i,j,k].real*newgrad[1];
					else:
						newgrad[0] = LGradnS(&rho[i,j,k], &grad[i,j,k], 0)
						newgrad[1] = LGradnS(&rho[i,j,k], &grad[i,j,k], 1)
						H0_tmp[0] -= grad[i,j,k].real*newgrad[0] + grad[i,j,k].imag*newgrad[1];
						H0_tmp[1] -= grad[i,j,k].imag*newgrad[0] - grad[i,j,k].real*newgrad[1];
	H[0,0] = 2.0*H0_tmp[0]/(<double> (rho.shape[0]*rho.shape[1]*rho.shape[2]))
	H[1,1] = 2.0*H1_tmp[0]/(<double> (rho.shape[0]*rho.shape[1]*rho.shape[2]))
	H[0,0] = 1.0/H[0,0]
	H[1,1] = -1.0/H[1,1]
	H[0,1] = H[1,0] = 0.0
@cython.boundscheck(False)
@cython.wraparound(False)
cdef void Hfit(f_sd_t* taui, f_sd_t* psii, f_sd_t[:] tau,\
				f_sd_t[:] dtau, f_sd_t[:] psi, f_sd_t[:,:] H, cnumpy.int64_t niter):
	cdef double[2] taum = [0.0,0.0]
	cdef double[2] psim = [0.0,0.0]
	cdef double[2] taur = [0.0,0.0]
	cdef double* x = <double *> malloc(sizeof(double) * (2*niter))
	cdef double* y = <double *> malloc(sizeof(double) * (2*niter))
	cdef double* tmp = <double *> malloc(sizeof(double) * (2*niter))
	cdef double[2][2] _xxt = [[0.0,0.0],[0.0,0.0]]
	cdef double[:,:] xxt = _xxt
	cdef double[2][2] _xyt = [[0.0,0.0],[0.0,0.0]]
	cdef double[:,:] xyt = _xyt
	cdef double[2][2] _Htmp = [[0.0,0.0],[0.0,0.0]]
	cdef double[:,:] Htmp = _Htmp
	cdef double mintaul = 0.0
	cdef double r = 0.0
	cdef int i,j,k
	cdef int imin = 0
	for i in range (niter):
		taum[0] += taui[2*i];
		taum[1] += taui[2*i+1];
		psim[0] += psii[2*i];
		psim[1] += psii[2*i+1];
	taum[0] = taum[0] / (<double> niter)
	taum[1] = taum[1] / (<double> niter)
	psim[0] = psim[0] / (<double> niter)
	psim[1] = psim[1] / (<double> niter)
	for i in range (niter):
		x[2*i] = taui[2*i] - taum[0]
		x[2*i+1] = taui[2*i+1] - taum[1]
		y[2*i] = psii[2*i] - psim[0]
		y[2*i+1] = psii[2*i+1] - psim[1]
	for i in range(2):
		for j in range(2):
			for k in range(niter):
				xxt[i][j] += x[2*k+i]*x[2*k+j]
				xyt[i][j] += x[2*k+i]*y[2*k+j]
	SOMatInv(xxt)
	for i in range(2):
		for j in range(2):
			for k in range(2):
				Htmp[i][j] += xxt[i][k]*xyt[k][j]
	SOMatInv(Htmp)
	H[0][0] = Htmp[0][0] / (<double> niter); H[0][1] = Htmp[0][1] / (<double> niter);
	H[1][0] = Htmp[1][0] / (<double> niter); H[1][1] = Htmp[1][1] / (<double> niter);
	for i in range(2):
		for j in range(2):
			for k in range(niter):
				tmp[2*k+i] += H[i][j]*psii[2*k+j]
	for k in range(niter):
		taur[0] += -(tmp[2*k]-taui[2*k])
		taur[1] += -(tmp[2*k+1]-taui[2*k+1])
	taur[0] = taur[0] / (<double> niter)
	taur[1] = taur[1] / (<double> niter)
	for i in range(niter):
		r = sqrt(psii[2*i]*psii[2*i] + psii[2*i+1]*psii[2*i+1]);
		if r < mintaul or mintaul == 0.0:
			mintaul = r
			imin = i
	tau[0] = taui[2*imin]
	tau[1] = taui[2*imin+1]
	psi[0] = psii[2*imin]
	psi[1] = psii[2*imin+1]
	dtau[0] = tau[0] - taur[0]
	dtau[1] = tau[1] - taur[1]
	free(x)
	free(y)
	free(tmp)
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef void SOMinMaxtau(f_csd_t[:, :, ::1] rho, f_csd_t[:, :, ::1] support, f_csd_t[:, :, ::1] rho_m1,\
						f_csd_t[:, :, ::1] rho_m2, f_csd_t[:, :, ::1] grad,\
						f_csd_t[:, :, ::1] expdata, f_csd_t[:, :, ::1] mask,\
						double[:] step, cnumpy.int32_t[:] citer_flow, int startiter,\
						double[:] tau, double[:] tauav, double[:,:] H, double[:,:] Hav,\
						double[:] psi, int algiter,\
						int maxiter, double alpha, double beta,\
						object planobj, int nthreads):
	cdef cnumpy.int64_t ii = 0
	cdef cnumpy.int64_t i,j,k
	cdef double* taui = <double *> malloc(sizeof(double) * (2*maxiter))
	cdef double* psii = <double *> malloc(sizeof(double) * (2*maxiter))
	if not PyCapsule_IsValid(planobj, "fftw.plan"):
		raise ValueError("invalid FFTW Plan pointer")
	cdef FFTWPlan *plan = <FFTWPlan*> PyCapsule_GetPointer(planobj, "fftw.plan")
	cdef double[2] _taumin = [0.0,0.0]
	cdef double[:] taumin = _taumin
	cdef double taul = 0.0
	cdef double[2] _dtau = [0.0,0.0]
	cdef double[:] dtau = _dtau
	cdef double[2] _taudtau = [0.0,0.0]
	cdef double[:] taudtau = _taudtau
	cdef double dtaul = 0.0
	cdef double psil = 0.0
	cdef double psil0 = 0.0
	cdef double psilmin = 0.0
	cdef double[2] _psiold = [0.0,0.0]
	cdef double[:] psiold = _psiold
	cdef double[2] _y = [0.0,0.0]
	cdef double[:] y = _y
	cdef double nav = 1.0
	cdef double navlen = 50.0
	for i in range(maxiter):
		taui[2*i] = 0.0
		taui[2*i+1] = 0.0
		psii[2*i] = 0.0
		psii[2*i+1] = 0.0
	psil0 = SOFrobSupport(grad, grad, support, nthreads)
	if algiter == 0:
		tau[0] = 0.0
		tau[1] = 0.0
	else:
		tau[0] = tauav[0]
		tau[1] = tauav[1]
	SOGradPsi(rho, support, rho_m1, rho_m2, grad, expdata, mask, step, citer_flow, startiter, tau, psi, plan, nthreads)
	if algiter == 0:
		tau[0] = alpha
		tau[1] = beta
	taui[0] = tau[0]; taui[1] = tau[1];
	psii[0] = psi[0]; psii[1] = psi[1];
	psiold[0] = psi[0]; psiold[1] = psi[1];
	psil = SOVecNorm(psi)
	psilmin = psil
	taumin[0] = tau[0]; taumin[1] = tau[1];
	if nav < (navlen-1.0):
		H[0,0] = -alpha*1.0/psi[0]
		H[1,1] = -beta*1.0/psi[1]
	else:
		H[0,0] = Hav[0,0]
		H[0,1] = Hav[0,1]
		H[1,0] = Hav[1,0]
		H[1,1] = Hav[1,1]
	cdef double[4] _steps = [step[0],step[1],1.0,1.0]
	cdef double[:] steps = _steps
	for i in range(maxiter):
		psiold[0] = psi[0]
		psiold[1] = psi[1]
		SOMatVecProd(H,psi,dtau)
		dtau[0] = -dtau[0]
		dtau[1] = -dtau[1]
		if ((i+1) % 10) == 0:
			Hfit(taui, psii, tau, dtau, psi, H, (<cnumpy.int64_t> (i+1)))
		dtaul = SOVecNorm(dtau)
		if dtaul > steps[0]:
			steps[3] = steps[0]/dtaul
		else:
			steps[3] = 1.0
		taudtau[0] = (tau[0] + steps[3]*dtau[0]); taudtau[1] = (tau[1] + steps[3]*dtau[1]);
		SOGradPsi(rho, support, rho_m1, rho_m2, grad, expdata, mask, step, citer_flow, startiter, tau, psi, plan, nthreads)
		if ((fabs(psi[0] - psiold[0])/fabs(psiold[0])) < step[3]):
			break
		psii[2*i] = psi[0]; psii[2*i+1] = psi[1];
		psil = SOVecNorm(psi);
		if (psil < psilmin):
			if taudtau[0] > 0.0 and taudtau[1] > 0.0:
				taumin[0] = taudtau[0]; taumin[1] = taudtau[1];
			psilmin = psil;
		tau[0] = taudtau[0]; tau[1] = taudtau[1];
		taui[2*i] = tau[0]; taui[2*i+1] = tau[1];
		if (psil/psil0 < step[2]):
			break
		y[0] = psiold[0] - psi[0]; y[1] = psiold[1] - psi[1]
		SOH(rho, support, rho_m2, grad, expdata, mask, step, citer_flow, startiter, H, y, dtau, steps, plan, nthreads)
		ii += 1
	if ii >= maxiter:
		tau[0] = taumin[0]; tau[1] = taumin[1];
		psil = psilmin
		if psil/psil0 > step[4]:
			tau[0] = alpha
			tau[1] = beta
	else:
		if tau[0]<0.0 or tau[1]<0.0:
			tau[0] = taumin[0]; tau[1] = taumin[1]
	taul = SOVecNorm(tau);
	if (taul*taul > step[5]*step[5]):
		tau[0] = fabs(step[5]*tau[0]/taul)
		tau[1] = fabs(step[5]*tau[1]/taul)
	tauav[0] = (tauav[0]*nav + fabs(tau[0]))/(nav + 1.0)
	tauav[1] = (tauav[1]*nav + fabs(tau[1]))/(nav + 1.0)
	Hav[0][0] = (Hav[0][0]*nav + H[0][0])/(nav + 1.0)
	Hav[0][1] = (Hav[0][1]*nav + H[0][1])/(nav + 1.0)
	Hav[1][0] = (Hav[1][0]*nav + H[1][0])/(nav + 1.0)
	Hav[1][1] = (Hav[1][1]*nav + H[1][1])/(nav + 1.0)
	if (nav < navlen):
		nav += 1.0
	free(taui)
	free(psii)
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef void SupportScaleAddArray(f_csd_t[:, :, ::1] rho, f_csd_t[:, :, ::1] support, f_csd_t[:, :, ::1] rho_m1,\
						f_csd_t[:, :, ::1] rho_m2, f_csd_t[:, :, ::1] grad, double[:] tau, double Sfactor,double nSfactor,\
						double[:] step, cnumpy.int32_t[:] citer_flow, int startiter, int nthreads):
	cdef cnumpy.int64_t i,j,k
	cdef double ampT
	if step[6] >= 0.0 and step[6] < (<double> citer_flow[0] - startiter):
		for i in prange(rho.shape[0], nogil=True, num_threads=nthreads):
			for j in prange(rho.shape[1], num_threads=nthreads):
				for k in prange(rho.shape[2], num_threads=nthreads):
					ampT = sqrt(rho_m2[i,j,k].real*rho_m2[i,j,k].real + rho_m2[i,j,k].imag*rho_m2[i,j,k].imag)
					if support[i,j,k].real > 0.5:
						rho[i,j,k] = rho_m1[i,j,k].real + Sfactor*tau[0]*grad[i,j,k].real*ampT +\
									1j * (rho_m1[i,j,k].imag + Sfactor*tau[0]*grad[i,j,k].imag*ampT)
					else:
						rho[i,j,k] = rho_m1[i,j,k].real + nSfactor*tau[1]*(grad[i,j,k].real*ampT - (1.0-ampT)*rho_m1[i,j,k].real ) +\
									1j * (rho_m1[i,j,k].imag + nSfactor*tau[1]*(grad[i,j,k].imag*ampT - (1.0-ampT)*rho_m1[i,j,k].imag ))
	else:
		for i in prange(rho.shape[0], nogil=True, num_threads=nthreads):
			for j in prange(rho.shape[1], num_threads=nthreads):
				for k in prange(rho.shape[2], num_threads=nthreads):
					if support[i,j,k].real > 0.5:
						rho[i,j,k] = rho_m1[i,j,k].real + Sfactor*tau[0]*grad[i,j,k].real +\
									1j * (rho_m1[i,j,k].imag + Sfactor*tau[0]*grad[i,j,k].imag)
					else:
						rho[i,j,k] = rho_m1[i,j,k].real + nSfactor*tau[1]*grad[i,j,k].real +\
									1j * (rho_m1[i,j,k].imag + nSfactor*tau[1]*grad[i,j,k].imag)
