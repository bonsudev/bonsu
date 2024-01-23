## 
#############################################
##   Filename: fftwlib.pxd
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


ctypedef float[2] csingle
ctypedef double[2] cdouble

ctypedef double complex cdouble_
ctypedef float complex csingle_

ctypedef fused f_csd_t:
	csingle_
	cdouble_

ctypedef float* single_p
ctypedef double* double_p

ctypedef fused f_sdp_t:
	single_p
	double_p

ctypedef fused f_sd_t:
	float
	double


cdef extern from 'fftw3.h':
	
	ctypedef struct struct_fftw_plan:
		pass
	
	ctypedef struct_fftw_plan *fftw_plan
	
	ctypedef struct struct_fftwf_plan:
		pass
	
	ctypedef struct_fftwf_plan *fftwf_plan
	
	void fftw_init_threads()
	void fftw_plan_with_nthreads(int n)

	void fftwf_init_threads()
	void fftwf_plan_with_nthreads(int n)
	
	void fftw_destroy_plan(fftw_plan)
	void fftwf_destroy_plan(fftwf_plan)
	
	void fftw_cleanup_threads()
	void fftwf_cleanup_threads()
	
	fftw_plan fftw_plan_dft(int ndim, int *nn, cdouble *data_in, cdouble *data_out, int direction, unsigned int planflag) nogil
	fftwf_plan fftwf_plan_dft(int ndim, int *nn, csingle *data_in, csingle *data_out, int direction, unsigned int planflag) nogil
	
	fftw_plan fftw_plan_many_dft(int ndim, int *nn, int n, cdouble *data_in, const int *inembed, int istride, int idist, cdouble *data_out, const int *onembed, int ostride, int odist, int direction, unsigned int planflag) nogil
	fftwf_plan fftwf_plan_many_dft(int ndim, int *nn, int n, csingle *data_in, const int *inembed, int istride, int idist, csingle *data_out, const int *onembed, int ostride, int odist, int direction, unsigned int planflag) nogil
	
	void fftw_execute_dft(fftw_plan, cdouble *data_in, cdouble *data_out) nogil
	void fftwf_execute_dft(fftwf_plan,  csingle *data_in, csingle *data_out) nogil
	
	void fftw_execute(fftw_plan) nogil
	void fftwf_execute(fftwf_plan) nogil


cdef struct _FFTWPlan:
	fftw_plan torecip
	fftw_plan toreal
	fftwf_plan torecipf
	fftwf_plan torealf
	int nthreads
	unsigned int planflag
	double scale
	float scalef

ctypedef _FFTWPlan FFTWPlan


cdef FFTWPlan* _fftw_create_plan(double complex[:, :, :] ar_in, int nthreads, unsigned int planflag)
cdef FFTWPlan* _fftwf_create_plan(float complex[:, :, :] ar_in, int nthreads, unsigned int planflag)
cdef FFTWPlan* _fftw_create_plan_pair(double complex[:, :, :] ar_in1, double complex[:, :, :] ar_in2, int nthreads, unsigned int planflag)
cdef FFTWPlan* _fftwf_create_plan_pair(float complex[:, :, :] ar_in1, float complex[:, :, :] ar_in2, int nthreads, unsigned int planflag)
cdef void _fftw_stride_pair(f_csd_t[:, :, ::1] ar_in1, f_csd_t[:, :, ::1] ar_in2, FFTWPlan* plan, int direction, int scale) noexcept nogil
cdef void _fftw_stride(double complex[:, :, ::1] ar_in1, double complex[:, :, ::1] ar_in2, FFTWPlan* plan, int direction, int scale) noexcept nogil
cdef void _fftwf_stride(float complex[:, :, ::1] ar_in1, float complex[:, :, ::1] ar_in2, FFTWPlan* plan, int direction, int scale) noexcept nogil
cdef _fftw_destroy_plan(FFTWPlan* plan)
cdef _fftwf_destroy_plan(FFTWPlan* plan)


cpdef enum:
	FFTW_ESTIMATE = 64
	FFTW_PATIENT = 32
	FFTW_EXHAUSTIVE = 8
	FFTW_MEASURE = 0
	FFTW_TORECIP = 1
	FFTW_TOREAL = -1


