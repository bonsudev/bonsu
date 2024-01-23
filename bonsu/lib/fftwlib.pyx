##
#############################################
##   Filename: fftwlib.pyx
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
from . cimport fftwlib
import numpy
cimport numpy as cnumpy
cnumpy.import_array()
cimport cython
from libc.math cimport sqrt
from cpython.mem cimport PyMem_Malloc, PyMem_Free
from cpython.pycapsule cimport PyCapsule_New, PyCapsule_GetPointer, PyCapsule_IsValid
from cython.parallel import prange
from threading import Lock
cdef object plan_mutex = Lock()
cdef fftw_plan _fftw_plan_dft(
	int ndim, int *nn,
	cdouble *data_in, cdouble *data_out,
	int direction, unsigned int planflag) nogil:
	return fftw_plan_dft(ndim, nn, data_in, data_out, direction, planflag)
cdef fftwf_plan _fftwf_plan_dft(
	int ndim, int *nn,
	csingle *data_in, csingle *data_out,
	int direction, unsigned int planflag) nogil:
	return fftwf_plan_dft(ndim, nn, data_in, data_out, direction, planflag)
cdef FFTWPlan* _fftw_create_plan(double complex[:, :, :] ar_in, int nthreads, unsigned int planflag):
	cdef cdouble* ar_in_buff = <cdouble*> &ar_in[0,0,0]
	cdef int[3] ar_in_shape_buff = [<int> ar_in.shape[0], <int> ar_in.shape[1], <int> ar_in.shape[2]]
	fftw_init_threads()
	fftw_plan_with_nthreads(nthreads)
	cdef FFTWPlan *plan = <FFTWPlan*> PyMem_Malloc(sizeof(FFTWPlan))
	if not plan:
		raise MemoryError()
	plan.nthreads = nthreads
	plan.planflag = planflag
	with plan_mutex:
		plan.torecip = _fftw_plan_dft(ar_in.ndim, ar_in_shape_buff, ar_in_buff, ar_in_buff, FFTW_TORECIP, planflag)
		plan.toreal = _fftw_plan_dft(ar_in.ndim, ar_in_shape_buff, ar_in_buff, ar_in_buff, FFTW_TOREAL, planflag)
		plan.torecipf = NULL
		plan.torealf = NULL
		plan.scale = <double> (1.0 / sqrt(<double> (ar_in.shape[0]*ar_in.shape[1]*ar_in.shape[2])))
		plan.scalef = 1.0
	return plan
cdef FFTWPlan* _fftwf_create_plan(float complex[:, :, :] ar_in, int nthreads, unsigned int planflag):
	cdef csingle* ar_in_buff = <csingle*> &ar_in[0,0,0]
	cdef int[3] ar_in_shape_buff = [<int> ar_in.shape[0], <int> ar_in.shape[1], <int> ar_in.shape[2]]
	fftw_init_threads()
	fftw_plan_with_nthreads(nthreads)
	cdef FFTWPlan *plan = <FFTWPlan*> PyMem_Malloc(sizeof(FFTWPlan))
	if not plan:
		raise MemoryError()
	plan.nthreads = nthreads
	plan.planflag = planflag
	with plan_mutex:
		plan.torecipf = _fftwf_plan_dft(ar_in.ndim, ar_in_shape_buff, ar_in_buff, ar_in_buff, FFTW_TORECIP, planflag)
		plan.torealf = _fftwf_plan_dft(ar_in.ndim, ar_in_shape_buff, ar_in_buff, ar_in_buff, FFTW_TOREAL, planflag)
		plan.torecip = NULL
		plan.toreal = NULL
		plan.scale = 1.0
		plan.scalef = <float> (1.0 / sqrt(<float> (ar_in.shape[0]*ar_in.shape[1]*ar_in.shape[2])))
	return plan
cpdef object fftw_createplan(cnumpy.ndarray ar_in, int nthreads, unsigned int planflag):
	cdef FFTWPlan *plan
	if ar_in.dtype == numpy.cdouble:
		plan = _fftw_create_plan(ar_in, nthreads, planflag)
		planobj = PyCapsule_New(plan, "fftw.plan", NULL)
		return planobj
	elif ar_in.dtype == numpy.csingle:
		plan = _fftwf_create_plan(ar_in, nthreads, planflag)
		planobj = PyCapsule_New(plan, "fftw.plan", NULL)
		return planobj
	else:
		raise TypeError()
cdef fftw_plan _fftw_plan_dft_pair(
	int ndim, int *nn,
	cdouble *data_in, int dist, cdouble *data_out,
	int direction, unsigned int planflag) nogil:
	return fftw_plan_many_dft(ndim, nn, 2, data_in, NULL, 1, dist, data_out, NULL, 1, dist, direction, planflag)
cdef fftwf_plan _fftwf_plan_dft_pair(
	int ndim, int *nn,
	csingle *data_in, int dist, csingle *data_out,
	int direction, unsigned int planflag) nogil:
	return fftwf_plan_many_dft(ndim, nn, 2, data_in, NULL, 1, dist, data_out, NULL, 1, dist, direction, planflag)
cdef FFTWPlan* _fftw_create_plan_pair(double complex[:, :, :] ar_in1, double complex[:, :, :] ar_in2, int nthreads, unsigned int planflag):
	cdef cdouble* ar_in1_buff = <cdouble*> &ar_in1[0,0,0]
	cdef cdouble* ar_in2_buff = <cdouble*> &ar_in2[0,0,0]
	cdef int[3] ar_in_shape_buff = [<int> ar_in1.shape[0], <int> ar_in1.shape[1], <int> ar_in1.shape[2]]
	cdef int dist = <int> ((<cdouble*> ar_in2_buff) - (<cdouble*> ar_in1_buff))
	fftw_init_threads()
	fftw_plan_with_nthreads(nthreads)
	cdef FFTWPlan *plan = <FFTWPlan*> PyMem_Malloc(sizeof(FFTWPlan))
	if not plan:
		raise MemoryError()
	plan.nthreads = nthreads
	plan.planflag = planflag
	with plan_mutex:
		plan.torecip = _fftw_plan_dft_pair(ar_in1.ndim, ar_in_shape_buff, ar_in1_buff, dist, ar_in1_buff, FFTW_TORECIP, planflag)
		plan.toreal = _fftw_plan_dft_pair(ar_in1.ndim, ar_in_shape_buff, ar_in1_buff, dist, ar_in1_buff, FFTW_TOREAL, planflag)
		plan.torecipf = NULL
		plan.torealf = NULL
		plan.scale = <double> (1.0 / sqrt(<double> (ar_in1.shape[0]*ar_in1.shape[1]*ar_in1.shape[2])))
		plan.scalef = 1.0
	return plan
cdef FFTWPlan* _fftwf_create_plan_pair(float complex[:, :, :] ar_in1, float complex[:, :, :] ar_in2, int nthreads, unsigned int planflag):
	cdef csingle* ar_in1_buff = <csingle*> &ar_in1[0,0,0]
	cdef csingle* ar_in2_buff = <csingle*> &ar_in2[0,0,0]
	cdef int[3] ar_in_shape_buff = [<int> ar_in1.shape[0], <int> ar_in1.shape[1], <int> ar_in1.shape[2]]
	cdef int dist = <int> ((<csingle*> ar_in2_buff) - (<csingle*> ar_in1_buff))
	fftw_init_threads()
	fftw_plan_with_nthreads(nthreads)
	cdef FFTWPlan *plan = <FFTWPlan*> PyMem_Malloc(sizeof(FFTWPlan))
	if not plan:
		raise MemoryError()
	plan.nthreads = nthreads
	plan.planflag = planflag
	with plan_mutex:
		plan.torecipf = _fftwf_plan_dft_pair(ar_in1.ndim, ar_in_shape_buff, ar_in1_buff, dist, ar_in1_buff, FFTW_TORECIP, planflag)
		plan.torealf = _fftwf_plan_dft_pair(ar_in1.ndim, ar_in_shape_buff, ar_in1_buff, dist, ar_in1_buff, FFTW_TOREAL, planflag)
		plan.torecip = NULL
		plan.toreal = NULL
		plan.scale = 1.0
		plan.scalef = <float> (1.0 / sqrt(<float> (ar_in1.shape[0]*ar_in1.shape[1]*ar_in1.shape[2])))
	return plan
cpdef object fftw_create_plan_pair(cnumpy.ndarray ar_in1, cnumpy.ndarray ar_in2, int nthreads, unsigned int planflag):
	cdef FFTWPlan *plan
	if ar_in1.dtype == numpy.cdouble and ar_in2.dtype == numpy.cdouble:
		plan = _fftw_create_plan_pair(ar_in1, ar_in2, nthreads, planflag)
		planobj = PyCapsule_New(plan, "fftw.planpair", NULL)
		return planobj
	elif ar_in1.dtype == numpy.csingle and ar_in2.dtype == numpy.csingle:
		plan = _fftwf_create_plan_pair(ar_in1, ar_in2, nthreads, planflag)
		planobj = PyCapsule_New(plan, "fftw.planpair", NULL)
		return planobj
	else:
		raise TypeError()
cdef _fftw_destroy_plan(FFTWPlan* plan):
	with plan_mutex:
		fftw_destroy_plan(plan.torecip)
		fftw_destroy_plan(plan.toreal)
		fftw_cleanup_threads()
	PyMem_Free(plan)
cdef _fftwf_destroy_plan(FFTWPlan* plan):
	with plan_mutex:
		fftwf_destroy_plan(plan.torecipf)
		fftwf_destroy_plan(plan.torealf)
		fftwf_cleanup_threads()
	PyMem_Free(plan)
cpdef object fftw_destroyplan(object planobj):
	cdef FFTWPlan *plan
	if PyCapsule_IsValid(planobj, "fftw.plan"):
		plan = <FFTWPlan*> PyCapsule_GetPointer(planobj, "fftw.plan")
	elif PyCapsule_IsValid(planobj, "fftw.planpair"):
		plan = <FFTWPlan*> PyCapsule_GetPointer(planobj, "fftw.planpair")
	else:
		raise ValueError("invalid FFTW Plan pointer")
	if plan.torecip == NULL and plan.toreal == NULL:
		return _fftwf_destroy_plan(plan)
	elif plan.torecipf == NULL and plan.torealf == NULL:
		return _fftw_destroy_plan(plan)
	else:
		raise TypeError()
@cython.boundscheck(False)
@cython.wraparound(False)
cdef void fftw_stride_scale(f_sdp_t ar_in, cnumpy.int_t size, f_sd_t scale, int nthreads) noexcept nogil:
	cdef cnumpy.int64_t i
	for i in prange(size, num_threads=nthreads):
		ar_in[2*i] *= scale
		ar_in[2*i+1] *= scale
cpdef fftw_stride(cnumpy.ndarray ar_in1, cnumpy.ndarray ar_in2, object planobj, int direction, int scale):
	if not PyCapsule_IsValid(planobj, "fftw.plan"):
		raise ValueError("invalid FFTW Plan pointer")
	cdef FFTWPlan *plan = <FFTWPlan*> PyCapsule_GetPointer(planobj, "fftw.plan")
	if ar_in1.dtype == numpy.cdouble and ar_in2.dtype == numpy.cdouble:
		_fftw_stride(ar_in1, ar_in2, plan, direction, scale)
	elif ar_in1.dtype == numpy.csingle and ar_in2.dtype == numpy.csingle:
		_fftwf_stride(ar_in1, ar_in2, plan, direction, scale)
	else:
		raise TypeError()
@cython.boundscheck(False)
@cython.wraparound(False)
cdef void _fftw_stride(double complex[:, :, ::1] ar_in1, double complex[:, :, ::1] ar_in2, FFTWPlan* plan, int direction, int scale) noexcept nogil:
	cdef cdouble* ar_in1_buff = <cdouble*> &ar_in1[0,0,0]
	cdef int[3] ar_in1_shape_buff = [<int> ar_in1.shape[0], <int> ar_in1.shape[1], <int> ar_in1.shape[2]]
	cdef cdouble* ar_in2_buff = <cdouble*> &ar_in2[0,0,0]
	cdef double* ar_in2_buff2 = <double*> &ar_in2[0,0,0]
	cdef int[3] ar_in2_shape_buff = [<int> ar_in2.shape[0], <int> ar_in2.shape[1], <int> ar_in2.shape[2]]
	cdef cnumpy.int_t size = ar_in2.shape[0]*ar_in2.shape[1]*ar_in2.shape[2]
	if direction == FFTW_TORECIP:
		fftw_execute_dft(plan.torecip, ar_in1_buff, ar_in2_buff)
	elif direction == FFTW_TOREAL:
		fftw_execute_dft(plan.toreal, ar_in1_buff, ar_in2_buff)
	if scale > 0:
		fftw_stride_scale(ar_in2_buff2, size, plan.scale, plan.nthreads)
@cython.boundscheck(False)
@cython.wraparound(False)
cdef void _fftwf_stride(float complex[:, :, ::1] ar_in1, float complex[:, :, ::1] ar_in2, FFTWPlan* plan, int direction, int scale) noexcept nogil:
	cdef csingle* ar_in1_buff = <csingle*> &ar_in1[0,0,0]
	cdef int[3] ar_in1_shape_buff = [<int> ar_in1.shape[0], <int> ar_in1.shape[1], <int> ar_in1.shape[2]]
	cdef csingle* ar_in2_buff = <csingle*> &ar_in2[0,0,0]
	cdef float* ar_in2_buff2 = <float*> &ar_in2[0,0,0]
	cdef int[3] ar_in2_shape_buff = [<int> ar_in2.shape[0], <int> ar_in2.shape[1], <int> ar_in2.shape[2]]
	cdef cnumpy.int_t size = ar_in2.shape[0]*ar_in2.shape[1]*ar_in2.shape[2]
	if direction == FFTW_TORECIP:
		fftwf_execute_dft(plan.torecipf, ar_in1_buff, ar_in2_buff)
	elif direction == FFTW_TOREAL:
		fftwf_execute_dft(plan.torealf, ar_in1_buff, ar_in2_buff)
	if scale > 0:
		fftw_stride_scale(ar_in2_buff2, size, plan.scalef, plan.nthreads)
cpdef fftw_stride_pair(f_csd_t[:, :, ::1] ar_in1, f_csd_t[:, :, ::1] ar_in2, object planobj, int direction, int scale):
	if not PyCapsule_IsValid(planobj, "fftw.planpair"):
		raise ValueError("invalid FFTW Plan pointer")
	cdef FFTWPlan *plan = <FFTWPlan*> PyCapsule_GetPointer(planobj, "fftw.planpair")
	with nogil:
		_fftw_stride_pair(ar_in1, ar_in2, plan, direction, scale)
@cython.boundscheck(False)
@cython.wraparound(False)
cdef void fftw_stride_pair_scale(f_sdp_t ar_in1, f_sdp_t ar_in2, cnumpy.int64_t size, f_sd_t scale, int nthreads) noexcept nogil:
	cdef cnumpy.int64_t i
	for i in prange(size, num_threads=nthreads):
		ar_in1[2*i] *= scale
		ar_in1[2*i+1] *= scale
		ar_in2[2*i] *= scale
		ar_in2[2*i+1] *= scale
cdef void _fftw_stride_pair(f_csd_t[:, :, ::1] ar_in1, f_csd_t[:, :, ::1] ar_in2, FFTWPlan* plan, int direction, int scale) noexcept nogil:
	cdef cnumpy.int64_t i,j,k, size
	size = ar_in1.shape[0]*ar_in1.shape[1]*ar_in1.shape[2]
	cdef double* ar_in1_buff
	cdef double* ar_in2_buff
	cdef float* ar_in1f_buff
	cdef float* ar_in2f_buff
	if direction == FFTW_TORECIP:
		fftw_execute(plan.torecip)
	elif direction == FFTW_TOREAL:
		fftw_execute(plan.toreal)
	if scale > 0:
		if f_csd_t is cdouble_:
			ar_in1_buff = <double*> &ar_in1[0,0,0]
			ar_in2_buff = <double*> &ar_in2[0,0,0]
			fftw_stride_pair_scale(ar_in1_buff, ar_in2_buff, size, plan.scale, plan.nthreads)
		elif f_csd_t is csingle_:
			ar_in1f_buff = <float*> &ar_in1[0,0,0]
			ar_in2f_buff = <float*> &ar_in2[0,0,0]
			fftw_stride_pair_scale(ar_in1f_buff, ar_in2f_buff, size, plan.scalef, plan.nthreads)
