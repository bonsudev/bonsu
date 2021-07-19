/*
#############################################
##   Filename: prfftwmodule.cxx
##
##    Copyright (C) 2012 Marcus C. Newton
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
*/

#include <Python.h>
#define PY_ARRAY_UNIQUE_SYMBOL prfftw_ARRAY_API
#define NPY_NO_DEPRECATED_API NPY_1_10_API_VERSION
#include "prfftwmodule.h"

int npthread = 1;

PyObject* prfftw_fft_stride(PyObject *self, PyObject *args)
{
	double *data1;
	double *data2;
	PyArrayObject *arg1;
	PyArrayObject *arg2;
	PyObject *pyplan;
	FFTWPlan* plan;
	int direction;
	int scale;
	npy_intp *dims;
	fftw_plan* plan_direction;
	if (!PyArg_ParseTuple(args, "OOOii", &arg1, &arg2, &pyplan, &direction, &scale)){return NULL;};
	data1 = (double*) PyArray_DATA(arg1);
	data2 = (double*) PyArray_DATA(arg2);
	dims = PyArray_DIMS(arg1);
	if (!(plan = (FFTWPlan*) PyCapsule_GetPointer(pyplan, "prfftw.plan"))){return NULL;};
	if (direction == 1)
	{
		plan_direction = &plan->torecip;
	}
	else if (direction == -1)
	{
		plan_direction = &plan->toreal;
	}
	else
	{
		return NULL;
	};
	fftw_execute_dft( *plan_direction, (fftw_complex*) data1, (fftw_complex*) data2 );
	if (scale > 0)
	{
		double inv_sqrt_n;
		int64_t i;
		int64_t len = (int64_t) dims[0] * dims[1] * dims[2];
		inv_sqrt_n = 1.0 / sqrt((double) len);
		for(i=0; i<len; i++)
		{
			data2[2*i] *= inv_sqrt_n;
			data2[2*i+1] *= inv_sqrt_n;
		}
	}
	Py_INCREF(Py_None);
	return Py_None;
}


PyObject* prfftw_destroyplan(PyObject *self, PyObject *args)
{
	PyObject *pyplan;
	if (!PyArg_ParseTuple(args, "O", &pyplan)){return NULL;};
	FFTWPlan* plan;
	if (!(plan = (FFTWPlan*) PyCapsule_GetPointer(pyplan, "prfftw.plan"))){return NULL;};
	/* fftw_init_threads(); */
	/* fftw_plan_with_nthreads(plan.nthreads); */
	fftw_destroy_plan( plan->torecip );
	fftw_destroy_plan( plan->toreal );
	fftw_cleanup_threads();
	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* prfftw_createplan(PyObject *self, PyObject *args)
{
	double *data;
	npy_intp *dims;
	int32_t ndim;
	int32_t nn[3];
	int nthreads;
	unsigned int planflag;
	PyArrayObject *arg;
	if (!PyArg_ParseTuple(args, "OiI", &arg, &nthreads, &planflag)){return NULL;};
	data = (double*) PyArray_DATA(arg);
	dims = PyArray_DIMS(arg);
	ndim = PyArray_NDIM(arg);
	nn[0] = (int32_t) dims[0]; nn[1] = (int32_t) dims[1]; nn[2] = (int32_t) dims[2];
	fftw_init_threads();
	fftw_plan_with_nthreads(nthreads);
	FFTWPlan* plan = (FFTWPlan*) malloc(sizeof(FFTWPlan));
	if (!plan){return NULL;};
	plan->nthreads = nthreads;
	plan->planflag = planflag;
	plan->torecip = fftw_plan_dft(ndim, (int32_t*) nn,(fftw_complex*) data, (fftw_complex*) data, +1, plan->planflag);	
	plan->toreal = fftw_plan_dft(ndim, (int32_t*) nn,(fftw_complex*) data, (fftw_complex*) data, -1, plan->planflag);
	if (plan->torecip == NULL || plan->toreal == NULL){return NULL;};
    PyObject *pyplan = PyCapsule_New(plan, "prfftw.plan", NULL);
    return pyplan;
}

PyObject* prfftw_wrap(PyObject *self, PyObject *args)
{
	double *indata;
	npy_intp *dims;
	int32_t nn[3];
	PyArrayObject *arg1=NULL;
	int drctn;
	if (!PyArg_ParseTuple(args, "Oi", &arg1, &drctn)){return NULL;};
	indata = (double*) PyArray_DATA(arg1);
	dims = PyArray_DIMS(arg1);
	nn[0] = (int32_t) dims[0]; nn[1] = (int32_t) dims[1]; nn[2] = (int32_t) dims[2];
	int wrapped;
	Py_BEGIN_ALLOW_THREADS;
	wrapped = wrap_array(indata, nn, drctn);
	Py_END_ALLOW_THREADS;
	if (wrapped)
	{
		PyErr_NoMemory();
		return PyErr_Occurred();
	}
	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* prfftw_wrap_nomem(PyObject *self, PyObject *args)
{
	double *indata;
	double *tmpdata;
	npy_intp *dims;
	int32_t nn[3];
	PyArrayObject *arg1=NULL;
	PyArrayObject *arg2=NULL;
	int drctn;
	if (!PyArg_ParseTuple(args, "OOi", &arg1, &arg2, &drctn)){return NULL;};
	indata = (double*) PyArray_DATA(arg1);
	tmpdata = (double*) PyArray_DATA(arg2);
	dims = PyArray_DIMS(arg1);
	nn[0] = (int32_t) dims[0]; nn[1] = (int32_t) dims[1]; nn[2] = (int32_t) dims[2];
	int wrapped;
	Py_BEGIN_ALLOW_THREADS;
	wrapped = wrap_array_nomem(indata, tmpdata, nn, drctn);
	Py_END_ALLOW_THREADS;
	if (wrapped)
	{
		PyErr_NoMemory();
		return PyErr_Occurred();
	}
	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* prfftw_copy_abs(PyObject *self, PyObject *args)
{
	double *indata;
	double *indata2;
	npy_intp *dims;
	int32_t nn[3];
	PyArrayObject *arg1=NULL;
	PyArrayObject *arg2=NULL;
	if (!PyArg_ParseTuple(args, "OO", &arg1, &arg2)){return NULL;};
	indata = (double*) PyArray_DATA(arg1);
	indata2 = (double*) PyArray_DATA(arg2);
	dims = PyArray_DIMS(arg1);
	nn[0] = (int32_t) dims[0]; nn[1] = (int32_t) dims[1]; nn[2] = (int32_t) dims[2];
	int result;
	Py_BEGIN_ALLOW_THREADS;
	result = CopyAbs(indata, indata2, nn);
	Py_END_ALLOW_THREADS;
	if (result)
	{
		PyErr_NoMemory();
		return PyErr_Occurred();
	}
	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* prfftw_copy_amp(PyObject *self, PyObject *args)
{
	double *indata;
	double *indata2;
	npy_intp *dims;
	int32_t nn[3];
	PyArrayObject *arg1=NULL;
	PyArrayObject *arg2=NULL;
	if (!PyArg_ParseTuple(args, "OO", &arg1, &arg2)){return NULL;};
	indata = (double*) PyArray_DATA(arg1);
	indata2 = (double*) PyArray_DATA(arg2);
	dims = PyArray_DIMS(arg1);
	nn[0] = (int32_t) dims[0]; nn[1] = (int32_t) dims[1]; nn[2] = (int32_t) dims[2];
	int result;
	Py_BEGIN_ALLOW_THREADS;
	result = CopyAmp2(indata, indata2, nn);
	Py_END_ALLOW_THREADS;
	if (result)
	{
		PyErr_NoMemory();
		return PyErr_Occurred();
	}
	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* prfftw_max_value(PyObject *self, PyObject *args)
{
	double *indata;
	double *maxval;
	npy_intp *dims;
	int32_t nn[3];
	PyArrayObject *arg1=NULL;
	PyArrayObject *arg2=NULL;
	if (!PyArg_ParseTuple(args, "OO", &arg1, &arg2)){return NULL;};
	indata = (double*) PyArray_DATA(arg1);
	maxval = (double*) PyArray_DATA(arg2);
	dims = PyArray_DIMS(arg1);
	nn[0] = (int32_t) dims[0]; nn[1] = (int32_t) dims[1]; nn[2] = (int32_t) dims[2];
	Py_BEGIN_ALLOW_THREADS;
	int64_t len = (int64_t) nn[0] * nn[1] * nn[2];
	int64_t i;
	maxval[0] = 0.0;
	maxval[1] = 0.0;
	for(i=0; i<len; i++)
	{
		maxval[1] = indata[i];
		if (maxval[1] > maxval[0])
		{
			maxval[0] = maxval[1];
		}
	}
	Py_END_ALLOW_THREADS;
	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* prfftw_hio(PyObject *self, PyObject *args)
{
	PyArrayObject *arg1=NULL, *arg2=NULL, *arg3=NULL;
	double beta; int startiter, numiter, ndim;
	PyArrayObject *arg9=NULL, *arg10=NULL, *arg11=NULL, *arg12=NULL;
	PyArrayObject *arg13=NULL, *arg14=NULL, *arg15=NULL, *arg16=NULL;
	PyObject *updatereal, *updaterecip, *updatelog;
	
	double *seqdata;
	double *expdata;
	double *support;
	
	double *rho_m1;
	int32_t *nn;
	double *residual;
	int32_t *citer_flow;
	
	double *visual_amp_real;
	double *visual_phase_real;
	double *visual_amp_recip;
	double *visual_phase_recip;

    if (!PyArg_ParseTuple(args, "OOOdiiiOOOOOOOOOOO",
		&arg1, &arg2, &arg3, &beta, &startiter, &numiter, &ndim,
		&arg9, &arg10, &arg11, &arg12, &arg13, &arg14, &arg15,
		&arg16, &updatereal, &updaterecip, &updatelog))
        {return NULL;};
	
	seqdata = (double*) PyArray_DATA(arg1);
	expdata = (double*) PyArray_DATA(arg2);
	support = (double*) PyArray_DATA(arg3);
	
	rho_m1 = (double*) PyArray_DATA(arg9);
	nn = (int32_t*) PyArray_DATA(arg10);
	residual = (double*) PyArray_DATA(arg11);
	citer_flow = (int32_t*) PyArray_DATA(arg12);
	
	visual_amp_real = (double*) PyArray_DATA(arg13);
	visual_phase_real = (double*) PyArray_DATA(arg14);
	visual_amp_recip = (double*) PyArray_DATA(arg15);
	visual_phase_recip = (double*) PyArray_DATA(arg16);
	
	if (!PyCallable_Check(updatereal))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updaterecip))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updatelog))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	Py_XINCREF(updatereal);
	Py_XINCREF(updaterecip);
	Py_XINCREF(updatelog);
	
	HIO(seqdata, expdata, support, beta, startiter, numiter,
					ndim, rho_m1, nn, residual, citer_flow, visual_amp_real,
					visual_phase_real, visual_amp_recip, visual_phase_recip,
					updatereal, updaterecip, updatelog);

	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* prfftw_hiomask(PyObject *self, PyObject *args)
{
	PyArrayObject *arg1=NULL, *arg2=NULL, *arg3=NULL, *arg4=NULL;
	double beta; int startiter, numiter, ndim, numiter_relax;
	PyArrayObject *arg9=NULL, *arg10=NULL, *arg11=NULL, *arg12=NULL;
	PyArrayObject *arg13=NULL, *arg14=NULL, *arg15=NULL, *arg16=NULL;
	PyObject *updatereal, *updaterecip, *updatelog;
	
	double *seqdata;
	double *expdata;
	double *support;
	double *mask;
	
	double *rho_m1;
	int32_t *nn;
	double *residual;
	int32_t *citer_flow;
	
	double *visual_amp_real;
	double *visual_phase_real;
	double *visual_amp_recip;
	double *visual_phase_recip;

    if (!PyArg_ParseTuple(args, "OOOOdiiiOOOOOOOOOOOi",
		&arg1, &arg2, &arg3, &arg4, &beta, &startiter, &numiter, &ndim,
		&arg9, &arg10, &arg11, &arg12, &arg13, &arg14, &arg15,
		&arg16, &updatereal, &updaterecip, &updatelog, &numiter_relax))
        {return NULL;};
	
	seqdata = (double*) PyArray_DATA(arg1);
	expdata = (double*) PyArray_DATA(arg2);
	support = (double*) PyArray_DATA(arg3);
	mask = (double*) PyArray_DATA(arg4);
	
	rho_m1 = (double*) PyArray_DATA(arg9);
	nn = (int32_t*) PyArray_DATA(arg10);
	residual = (double*) PyArray_DATA(arg11);
	citer_flow = (int32_t*) PyArray_DATA(arg12);
	
	visual_amp_real = (double*) PyArray_DATA(arg13);
	visual_phase_real = (double*) PyArray_DATA(arg14);
	visual_amp_recip = (double*) PyArray_DATA(arg15);
	visual_phase_recip = (double*) PyArray_DATA(arg16);
	
	if (!PyCallable_Check(updatereal))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updaterecip))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updatelog))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	Py_XINCREF(updatereal);
	Py_XINCREF(updaterecip);
	Py_XINCREF(updatelog);
	
	HIOMask(seqdata, expdata, support, mask, beta, startiter, numiter,
					ndim, rho_m1, nn, residual, citer_flow, visual_amp_real,
					visual_phase_real, visual_amp_recip, visual_phase_recip,
					updatereal, updaterecip, updatelog, numiter_relax);

	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* prfftw_hioplus(PyObject *self, PyObject *args)
{
	PyArrayObject *arg1=NULL, *arg2=NULL, *arg3=NULL, *arg4=NULL;
	double beta; int startiter, numiter, ndim;
	PyArrayObject *arg9=NULL, *arg10=NULL, *arg11=NULL, *arg12=NULL;
	PyArrayObject *arg13=NULL, *arg14=NULL, *arg15=NULL, *arg16=NULL;
	PyObject *updatereal, *updaterecip, *updatelog;
	
	double *seqdata;
	double *expdata;
	double *support;
	double *mask;
	
	double *rho_m1;
	int32_t *nn;
	double *residual;
	int32_t *citer_flow;
	
	double *visual_amp_real;
	double *visual_phase_real;
	double *visual_amp_recip;
	double *visual_phase_recip;

    if (!PyArg_ParseTuple(args, "OOOOdiiiOOOOOOOOOOO",
		&arg1, &arg2, &arg3, &arg4, &beta, &startiter, &numiter, &ndim,
		&arg9, &arg10, &arg11, &arg12, &arg13, &arg14, &arg15,
		&arg16, &updatereal, &updaterecip, &updatelog))
        {return NULL;};
	
	seqdata = (double*) PyArray_DATA(arg1);
	expdata = (double*) PyArray_DATA(arg2);
	support = (double*) PyArray_DATA(arg3);
	mask = (double*) PyArray_DATA(arg4);
	
	rho_m1 = (double*) PyArray_DATA(arg9);
	nn = (int32_t*) PyArray_DATA(arg10);
	residual = (double*) PyArray_DATA(arg11);
	citer_flow = (int32_t*) PyArray_DATA(arg12);
	
	visual_amp_real = (double*) PyArray_DATA(arg13);
	visual_phase_real = (double*) PyArray_DATA(arg14);
	visual_amp_recip = (double*) PyArray_DATA(arg15);
	visual_phase_recip = (double*) PyArray_DATA(arg16);
	
	if (!PyCallable_Check(updatereal))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updaterecip))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updatelog))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	Py_XINCREF(updatereal);
	Py_XINCREF(updaterecip);
	Py_XINCREF(updatelog);
	
	HIOPlus(seqdata, expdata, support, mask, beta, startiter, numiter,
					ndim, rho_m1, nn, residual, citer_flow, visual_amp_real,
					visual_phase_real, visual_amp_recip, visual_phase_recip,
					updatereal, updaterecip, updatelog);

	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* prfftw_pchio(PyObject *self, PyObject *args)
{
	PyArrayObject *arg1=NULL, *arg2=NULL, *arg3=NULL, *arg4=NULL;
	double beta; int startiter, numiter, ndim;
	double phasemax, phasemin;
	PyArrayObject *arg9=NULL, *arg10=NULL, *arg11=NULL, *arg12=NULL;
	PyArrayObject *arg13=NULL, *arg14=NULL, *arg15=NULL, *arg16=NULL;
	PyObject *updatereal, *updaterecip, *updatelog;
	
	double *seqdata;
	double *expdata;
	double *support;
	double *mask;
	
	double *rho_m1;
	int32_t *nn;
	double *residual;
	int32_t *citer_flow;
	
	double *visual_amp_real;
	double *visual_phase_real;
	double *visual_amp_recip;
	double *visual_phase_recip;

    if (!PyArg_ParseTuple(args, "OOOOdiiiddOOOOOOOOOOO",
		&arg1, &arg2, &arg3, &arg4, &beta, &startiter, &numiter, &ndim,
		&phasemax, &phasemin,
		&arg9, &arg10, &arg11, &arg12, &arg13, &arg14, &arg15,
		&arg16, &updatereal, &updaterecip, &updatelog))
        {return NULL;};
	
	seqdata = (double*) PyArray_DATA(arg1);
	expdata = (double*) PyArray_DATA(arg2);
	support = (double*) PyArray_DATA(arg3);
	mask = (double*) PyArray_DATA(arg4);
	
	rho_m1 = (double*) PyArray_DATA(arg9);
	nn = (int32_t*) PyArray_DATA(arg10);
	residual = (double*) PyArray_DATA(arg11);
	citer_flow = (int32_t*) PyArray_DATA(arg12);
	
	visual_amp_real = (double*) PyArray_DATA(arg13);
	visual_phase_real = (double*) PyArray_DATA(arg14);
	visual_amp_recip = (double*) PyArray_DATA(arg15);
	visual_phase_recip = (double*) PyArray_DATA(arg16);
	
	if (!PyCallable_Check(updatereal))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updaterecip))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updatelog))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	Py_XINCREF(updatereal);
	Py_XINCREF(updaterecip);
	Py_XINCREF(updatelog);
	
	PCHIO(seqdata, expdata, support, mask, beta, startiter, numiter,
					ndim, phasemax, phasemin,
					rho_m1, nn, residual, citer_flow, visual_amp_real,
					visual_phase_real, visual_amp_recip, visual_phase_recip,
					updatereal, updaterecip, updatelog);

	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* prfftw_pgchio(PyObject *self, PyObject *args)
{
	PyArrayObject *arg1=NULL, *arg2=NULL, *arg3=NULL, *arg4=NULL, *arg5=NULL;
	double beta; int startiter, numiter, ndim;
	double phasemax, phasemin, qx, qy, qz;
	PyArrayObject *arg9=NULL, *arg10=NULL, *arg11=NULL, *arg12=NULL;
	PyArrayObject *arg13=NULL, *arg14=NULL, *arg15=NULL, *arg16=NULL;
	PyObject *updatereal, *updaterecip, *updatelog;
	
	double *seqdata;
	double *expdata;
	double *support;
	double *mask;
	double *tmpdata;
	
	double *rho_m1;
	int32_t *nn;
	double *residual;
	int32_t *citer_flow;
	
	double *visual_amp_real;
	double *visual_phase_real;
	double *visual_amp_recip;
	double *visual_phase_recip;

    if (!PyArg_ParseTuple(args, "OOOOOdiiidddddOOOOOOOOOOO",
		&arg1, &arg2, &arg3, &arg4, &arg5, &beta, &startiter, &numiter, &ndim,
		&phasemax, &phasemin, &qx, &qy, &qz,
		&arg9, &arg10, &arg11, &arg12, &arg13, &arg14, &arg15,
		&arg16, &updatereal, &updaterecip, &updatelog))
        {return NULL;};
	
	seqdata = (double*) PyArray_DATA(arg1);
	expdata = (double*) PyArray_DATA(arg2);
	support = (double*) PyArray_DATA(arg3);
	mask = (double*) PyArray_DATA(arg4);
	tmpdata = (double*) PyArray_DATA(arg5);
	
	rho_m1 = (double*) PyArray_DATA(arg9);
	nn = (int32_t*) PyArray_DATA(arg10);
	residual = (double*) PyArray_DATA(arg11);
	citer_flow = (int32_t*) PyArray_DATA(arg12);
	
	visual_amp_real = (double*) PyArray_DATA(arg13);
	visual_phase_real = (double*) PyArray_DATA(arg14);
	visual_amp_recip = (double*) PyArray_DATA(arg15);
	visual_phase_recip = (double*) PyArray_DATA(arg16);
	
	if (!PyCallable_Check(updatereal))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updaterecip))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updatelog))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	Py_XINCREF(updatereal);
	Py_XINCREF(updaterecip);
	Py_XINCREF(updatelog);
	
	PGCHIO(seqdata, expdata, support, mask, tmpdata, beta, startiter, numiter,
					ndim, phasemax, phasemin, qx, qy, qz,
					rho_m1, nn, residual, citer_flow, visual_amp_real,
					visual_phase_real, visual_amp_recip, visual_phase_recip,
					updatereal, updaterecip, updatelog);

	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* prfftw_er(PyObject *self, PyObject *args)
{
	PyArrayObject *arg1=NULL, *arg2=NULL, *arg3=NULL;
	int startiter, numiter, ndim;
	PyArrayObject *arg9=NULL, *arg10=NULL, *arg11=NULL, *arg12=NULL;
	PyArrayObject *arg13=NULL, *arg14=NULL, *arg15=NULL, *arg16=NULL;
	PyObject *updatereal, *updaterecip, *updatelog;
	
	double *seqdata;
	double *expdata;
	double *support;
	
	double *rho_m1;
	int32_t *nn;
	double *residual;
	int32_t *citer_flow;
	
	double *visual_amp_real;
	double *visual_phase_real;
	double *visual_amp_recip;
	double *visual_phase_recip;

    if (!PyArg_ParseTuple(args, "OOOiiiOOOOOOOOOOO",
		&arg1, &arg2, &arg3, &startiter, &numiter, &ndim,
		&arg9, &arg10, &arg11, &arg12, &arg13, &arg14, &arg15,
		&arg16, &updatereal, &updaterecip, &updatelog))
        {return NULL;};
	
	seqdata = (double*) PyArray_DATA(arg1);
	expdata = (double*) PyArray_DATA(arg2);
	support = (double*) PyArray_DATA(arg3);
	
	rho_m1 = (double*) PyArray_DATA(arg9);
	nn = (int32_t*) PyArray_DATA(arg10);
	residual = (double*) PyArray_DATA(arg11);
	citer_flow = (int32_t*) PyArray_DATA(arg12);
	
	visual_amp_real = (double*) PyArray_DATA(arg13);
	visual_phase_real = (double*) PyArray_DATA(arg14);
	visual_amp_recip = (double*) PyArray_DATA(arg15);
	visual_phase_recip = (double*) PyArray_DATA(arg16);
	
	if (!PyCallable_Check(updatereal))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updaterecip))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updatelog))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	Py_XINCREF(updatereal);
	Py_XINCREF(updaterecip);
	Py_XINCREF(updatelog);
	
	ER(seqdata, expdata, support, startiter, numiter,
					ndim, rho_m1, nn, residual, citer_flow, visual_amp_real,
					visual_phase_real, visual_amp_recip, visual_phase_recip,
					updatereal, updaterecip, updatelog);

	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* prfftw_ermask(PyObject *self, PyObject *args)
{
	PyArrayObject *arg1=NULL, *arg2=NULL, *arg3=NULL, *arg4=NULL;
	int startiter, numiter, ndim, numiter_relax;
	PyArrayObject *arg9=NULL, *arg10=NULL, *arg11=NULL, *arg12=NULL;
	PyArrayObject *arg13=NULL, *arg14=NULL, *arg15=NULL, *arg16=NULL;
	PyObject *updatereal, *updaterecip, *updatelog;
	
	double *seqdata;
	double *expdata;
	double *support;
	double *mask;
	
	double *rho_m1;
	int32_t *nn;
	double *residual;
	int32_t *citer_flow;
	
	double *visual_amp_real;
	double *visual_phase_real;
	double *visual_amp_recip;
	double *visual_phase_recip;

    if (!PyArg_ParseTuple(args, "OOOOiiiOOOOOOOOOOOi",
		&arg1, &arg2, &arg3, &arg4, &startiter, &numiter, &ndim,
		&arg9, &arg10, &arg11, &arg12, &arg13, &arg14, &arg15,
		&arg16, &updatereal, &updaterecip, &updatelog, &numiter_relax))
        {return NULL;};
	
	seqdata = (double*) PyArray_DATA(arg1);
	expdata = (double*) PyArray_DATA(arg2);
	support = (double*) PyArray_DATA(arg3);
	mask = (double*) PyArray_DATA(arg4);
	
	rho_m1 = (double*) PyArray_DATA(arg9);
	nn = (int32_t*) PyArray_DATA(arg10);
	residual = (double*) PyArray_DATA(arg11);
	citer_flow = (int32_t*) PyArray_DATA(arg12);
	
	visual_amp_real = (double*) PyArray_DATA(arg13);
	visual_phase_real = (double*) PyArray_DATA(arg14);
	visual_amp_recip = (double*) PyArray_DATA(arg15);
	visual_phase_recip = (double*) PyArray_DATA(arg16);
	
	if (!PyCallable_Check(updatereal))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updaterecip))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updatelog))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	Py_XINCREF(updatereal);
	Py_XINCREF(updaterecip);
	Py_XINCREF(updatelog);
	
	ERMask(seqdata, expdata, support, mask, startiter, numiter,
					ndim, rho_m1, nn, residual, citer_flow, visual_amp_real,
					visual_phase_real, visual_amp_recip, visual_phase_recip,
					updatereal, updaterecip, updatelog, numiter_relax);

	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* prfftw_poermask(PyObject *self, PyObject *args)
{
	PyArrayObject *arg1=NULL, *arg2=NULL, *arg3=NULL, *arg4=NULL;
	int startiter, numiter, ndim;
	PyArrayObject *arg9=NULL, *arg10=NULL, *arg11=NULL, *arg12=NULL;
	PyArrayObject *arg13=NULL, *arg14=NULL, *arg15=NULL, *arg16=NULL;
	PyObject *updatereal, *updaterecip, *updatelog;
	
	double *seqdata;
	double *expdata;
	double *support;
	double *mask;
	
	double *rho_m1;
	int32_t *nn;
	double *residual;
	int32_t *citer_flow;
	
	double *visual_amp_real;
	double *visual_phase_real;
	double *visual_amp_recip;
	double *visual_phase_recip;

    if (!PyArg_ParseTuple(args, "OOOOiiiOOOOOOOOOOO",
		&arg1, &arg2, &arg3, &arg4, &startiter, &numiter, &ndim,
		&arg9, &arg10, &arg11, &arg12, &arg13, &arg14, &arg15,
		&arg16, &updatereal, &updaterecip, &updatelog))
        {return NULL;};
	
	seqdata = (double*) PyArray_DATA(arg1);
	expdata = (double*) PyArray_DATA(arg2);
	support = (double*) PyArray_DATA(arg3);
	mask = (double*) PyArray_DATA(arg4);
	
	rho_m1 = (double*) PyArray_DATA(arg9);
	nn = (int32_t*) PyArray_DATA(arg10);
	residual = (double*) PyArray_DATA(arg11);
	citer_flow = (int32_t*) PyArray_DATA(arg12);
	
	visual_amp_real = (double*) PyArray_DATA(arg13);
	visual_phase_real = (double*) PyArray_DATA(arg14);
	visual_amp_recip = (double*) PyArray_DATA(arg15);
	visual_phase_recip = (double*) PyArray_DATA(arg16);
	
	if (!PyCallable_Check(updatereal))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updaterecip))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updatelog))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	Py_XINCREF(updatereal);
	Py_XINCREF(updaterecip);
	Py_XINCREF(updatelog);
	
	POERMask(seqdata, expdata, support, mask, startiter, numiter,
					ndim, rho_m1, nn, residual, citer_flow, visual_amp_real,
					visual_phase_real, visual_amp_recip, visual_phase_recip,
					updatereal, updaterecip, updatelog);

	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* prfftw_raar(PyObject *self, PyObject *args)
{
	PyArrayObject *arg1=NULL, *arg2=NULL, *arg3=NULL, *arg4=NULL;
	double beta; int startiter, numiter, ndim, numiter_relax;
	PyArrayObject *arg9=NULL, *arg10=NULL, *arg11=NULL, *arg12=NULL;
	PyArrayObject *arg13=NULL, *arg14=NULL, *arg15=NULL, *arg16=NULL;
	PyObject *updatereal, *updaterecip, *updatelog;
	
	double *seqdata;
	double *expdata;
	double *support;
	double *mask;
	
	double *rho_m1;
	int32_t *nn;
	double *residual;
	int32_t *citer_flow;
	
	double *visual_amp_real;
	double *visual_phase_real;
	double *visual_amp_recip;
	double *visual_phase_recip;

    if (!PyArg_ParseTuple(args, "OOOOdiiiOOOOOOOOOOOi",
		&arg1, &arg2, &arg3, &arg4, &beta, &startiter, &numiter, &ndim,
		&arg9, &arg10, &arg11, &arg12, &arg13, &arg14, &arg15,
		&arg16, &updatereal, &updaterecip, &updatelog, &numiter_relax))
        {return NULL;};
	
	seqdata = (double*) PyArray_DATA(arg1);
	expdata = (double*) PyArray_DATA(arg2);
	support = (double*) PyArray_DATA(arg3);
	mask = (double*) PyArray_DATA(arg4);
	
	rho_m1 = (double*) PyArray_DATA(arg9);
	nn = (int32_t*) PyArray_DATA(arg10);
	residual = (double*) PyArray_DATA(arg11);
	citer_flow = (int32_t*) PyArray_DATA(arg12);
	
	visual_amp_real = (double*) PyArray_DATA(arg13);
	visual_phase_real = (double*) PyArray_DATA(arg14);
	visual_amp_recip = (double*) PyArray_DATA(arg15);
	visual_phase_recip = (double*) PyArray_DATA(arg16);
	
	if (!PyCallable_Check(updatereal))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updaterecip))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updatelog))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	Py_XINCREF(updatereal);
	Py_XINCREF(updaterecip);
	Py_XINCREF(updatelog);
	
	RAAR(seqdata, expdata, support, mask, beta, startiter, numiter,
					ndim, rho_m1, nn, residual, citer_flow, visual_amp_real,
					visual_phase_real, visual_amp_recip, visual_phase_recip,
					updatereal, updaterecip, updatelog, numiter_relax);

	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* prfftw_hpr(PyObject *self, PyObject *args)
{
	PyArrayObject *arg1=NULL, *arg2=NULL, *arg3=NULL, *arg4=NULL;
	double beta; int startiter, numiter, ndim, numiter_relax;
	PyArrayObject *arg9=NULL, *arg10=NULL, *arg11=NULL, *arg12=NULL;
	PyArrayObject *arg13=NULL, *arg14=NULL, *arg15=NULL, *arg16=NULL;
	PyObject *updatereal, *updaterecip, *updatelog;
	
	double *seqdata;
	double *expdata;
	double *support;
	double *mask;
	
	double *rho_m1;
	int32_t *nn;
	double *residual;
	int32_t *citer_flow;
	
	double *visual_amp_real;
	double *visual_phase_real;
	double *visual_amp_recip;
	double *visual_phase_recip;

    if (!PyArg_ParseTuple(args, "OOOOdiiiOOOOOOOOOOOi",
		&arg1, &arg2, &arg3, &arg4, &beta, &startiter, &numiter, &ndim,
		&arg9, &arg10, &arg11, &arg12, &arg13, &arg14, &arg15,
		&arg16, &updatereal, &updaterecip, &updatelog, &numiter_relax))
        {return NULL;};
	
	seqdata = (double*) PyArray_DATA(arg1);
	expdata = (double*) PyArray_DATA(arg2);
	support = (double*) PyArray_DATA(arg3);
	mask = (double*) PyArray_DATA(arg4);
	
	rho_m1 = (double*) PyArray_DATA(arg9);
	nn = (int32_t*) PyArray_DATA(arg10);
	residual = (double*) PyArray_DATA(arg11);
	citer_flow = (int32_t*) PyArray_DATA(arg12);
	
	visual_amp_real = (double*) PyArray_DATA(arg13);
	visual_phase_real = (double*) PyArray_DATA(arg14);
	visual_amp_recip = (double*) PyArray_DATA(arg15);
	visual_phase_recip = (double*) PyArray_DATA(arg16);
	
	if (!PyCallable_Check(updatereal))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updaterecip))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updatelog))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	Py_XINCREF(updatereal);
	Py_XINCREF(updaterecip);
	Py_XINCREF(updatelog);
	
	HPR(seqdata, expdata, support, mask, beta, startiter, numiter,
					ndim, rho_m1, nn, residual, citer_flow, visual_amp_real,
					visual_phase_real, visual_amp_recip, visual_phase_recip,
					updatereal, updaterecip, updatelog, numiter_relax);

	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* prfftw_cshio(PyObject *self, PyObject *args)
{
	PyArrayObject *arg1=NULL, *arg2=NULL, *arg3=NULL, *arg4=NULL;
	double beta; int startiter, numiter, ndim;
	double cs_p,cs_d,cs_eta; int32_t relax;
	PyArrayObject *arg5=NULL, *arg6=NULL, *arg7=NULL;
	PyArrayObject *arg9=NULL, *arg10=NULL, *arg11=NULL, *arg12=NULL;
	PyArrayObject *arg13=NULL, *arg14=NULL, *arg15=NULL, *arg16=NULL;
	PyObject *updatereal, *updaterecip, *updatelog;
	
	double *seqdata;
	double *expdata;
	double *support;
	double *mask;
	
	double *epsilon;
	double *rho_m2;
	double *elp;
	
	double *rho_m1;
	int32_t *nn;
	double *residual;
	int32_t *citer_flow;
	
	double *visual_amp_real;
	double *visual_phase_real;
	double *visual_amp_recip;
	double *visual_phase_recip;

    if (!PyArg_ParseTuple(args, "OOOOdiiidOddiOOOOOOOOOOOOO",
		&arg1, &arg2, &arg3, &arg4, &beta, &startiter, &numiter, &ndim,
		&cs_p, &arg5, &cs_d, &cs_eta, &relax,
		&arg9, &arg6, &arg7, &arg10, &arg11, &arg12, &arg13, &arg14, &arg15,
		&arg16, &updatereal, &updaterecip, &updatelog))
        {return NULL;};
	
	seqdata = (double*) PyArray_DATA(arg1);
	expdata = (double*) PyArray_DATA(arg2);
	support = (double*) PyArray_DATA(arg3);
	mask = (double*) PyArray_DATA(arg4);
	
	epsilon = (double*) PyArray_DATA(arg5);
	rho_m2 = (double*) PyArray_DATA(arg6);
	elp = (double*) PyArray_DATA(arg7);
	
	rho_m1 = (double*) PyArray_DATA(arg9);
	nn = (int32_t*) PyArray_DATA(arg10);
	residual = (double*) PyArray_DATA(arg11);
	citer_flow = (int32_t*) PyArray_DATA(arg12);
	
	visual_amp_real = (double*) PyArray_DATA(arg13);
	visual_phase_real = (double*) PyArray_DATA(arg14);
	visual_amp_recip = (double*) PyArray_DATA(arg15);
	visual_phase_recip = (double*) PyArray_DATA(arg16);
	
	if (!PyCallable_Check(updatereal))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updaterecip))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updatelog))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	Py_XINCREF(updatereal);
	Py_XINCREF(updaterecip);
	Py_XINCREF(updatelog);
	
	CSHIO(seqdata, expdata, support, mask, beta, startiter, numiter,
					ndim, cs_p, epsilon, cs_d, cs_eta, relax,
					rho_m1, rho_m2, elp, nn, residual, citer_flow, visual_amp_real,
					visual_phase_real, visual_amp_recip, visual_phase_recip,
					updatereal, updaterecip, updatelog);

	Py_INCREF(Py_None);
	return Py_None;
}


PyObject* prfftw_hiomaskpc(PyObject *self, PyObject *args)
{
	PyObject *pylist1=NULL;
	PyObject *pylist2=NULL;
	if (!PyArg_ParseTuple(args, "OO", &pylist1, &pylist2)){return NULL;};
	
	PyArrayObject *p2arg0=(PyArrayObject*) PyList_GetItem(pylist2, 0); double *seqdata = (double*) PyArray_DATA(p2arg0);
	PyArrayObject *p2arg1=(PyArrayObject*) PyList_GetItem(pylist2, 1); double *expdata = (double*) PyArray_DATA(p2arg1);
	PyArrayObject *p2arg2=(PyArrayObject*) PyList_GetItem(pylist2, 2); double *support = (double*) PyArray_DATA(p2arg2);
	PyArrayObject *p2arg3=(PyArrayObject*) PyList_GetItem(pylist2, 3); double *mask = (double*) PyArray_DATA(p2arg3);
	PyArrayObject *p2arg4=(PyArrayObject*) PyList_GetItem(pylist2, 4); double *pca_gamma_ft = (double*) PyArray_DATA(p2arg4);
	PyArrayObject *p2arg5=(PyArrayObject*) PyList_GetItem(pylist2, 5); double *rho_m1 = (double*) PyArray_DATA(p2arg5);
	PyArrayObject *p2arg6=(PyArrayObject*) PyList_GetItem(pylist2, 6); double *pca_inten = (double*) PyArray_DATA(p2arg6);
	PyArrayObject *p2arg7=(PyArrayObject*) PyList_GetItem(pylist2, 7); double *pca_rho_m1_ft = (double*) PyArray_DATA(p2arg7);
	PyArrayObject *p2arg8=(PyArrayObject*) PyList_GetItem(pylist2, 8); double *pca_Idm_iter = (double*) PyArray_DATA(p2arg8);
	PyArrayObject *p2arg9=(PyArrayObject*) PyList_GetItem(pylist2, 9); double *pca_Idmdiv_iter = (double*) PyArray_DATA(p2arg9);
	PyArrayObject *p2arg10=(PyArrayObject*) PyList_GetItem(pylist2, 10); double *pca_IdmdivId_iter = (double*) PyArray_DATA(p2arg10);
	PyArrayObject *p2arg11=(PyArrayObject*) PyList_GetItem(pylist2, 11); double *tmparray1 = (double*) PyArray_DATA(p2arg11);
	PyArrayObject *p2arg12=(PyArrayObject*) PyList_GetItem(pylist2, 12); double *tmparray2 = (double*) PyArray_DATA(p2arg12);
	PyArrayObject *p2arg13=(PyArrayObject*) PyList_GetItem(pylist2, 13); int32_t  *nn = (int32_t*) PyArray_DATA(p2arg13);
	int ndim=PyLong_AsLong(PyList_GetItem(pylist2, 14));
	PyArrayObject *p2arg15=(PyArrayObject*) PyList_GetItem(pylist2, 15); int32_t  *nn2 = (int32_t*) PyArray_DATA(p2arg15);
	int startiter=PyLong_AsLong(PyList_GetItem(pylist2, 16));
	int numiter=PyLong_AsLong(PyList_GetItem(pylist2, 17));
	PyArrayObject *p2arg18=(PyArrayObject*) PyList_GetItem(pylist2, 18); int32_t  *citer_flow = (int32_t*) PyArray_DATA(p2arg18);
	
	PyArrayObject *p1arg0=(PyArrayObject*) PyList_GetItem(pylist1, 0); double *residual = (double*) PyArray_DATA(p1arg0);
	PyArrayObject *p1arg1=(PyArrayObject*) PyList_GetItem(pylist1, 1); double *residualRL = (double*) PyArray_DATA(p1arg1);
	PyArrayObject *p1arg2=(PyArrayObject*) PyList_GetItem(pylist1, 2); double *visual_amp_real = (double*) PyArray_DATA(p1arg2);
	PyArrayObject *p1arg3=(PyArrayObject*) PyList_GetItem(pylist1, 3); double *visual_phase_real = (double*) PyArray_DATA(p1arg3);
	PyArrayObject *p1arg4=(PyArrayObject*) PyList_GetItem(pylist1, 4); double *visual_amp_recip = (double*) PyArray_DATA(p1arg4);
	PyArrayObject *p1arg5=(PyArrayObject*) PyList_GetItem(pylist1, 5); double *visual_phase_recip = (double*) PyArray_DATA(p1arg5);
	PyObject *updatereal=PyList_GetItem(pylist1, 6); 
	PyObject *updaterecip=PyList_GetItem(pylist1, 7); 
	PyObject *updatelog=PyList_GetItem(pylist1, 8); 
	PyObject *updatelog2=PyList_GetItem(pylist1, 9);
	double gammaHWHM=PyFloat_AsDouble(PyList_GetItem(pylist1, 10));
	int gammaRS=PyLong_AsLong(PyList_GetItem(pylist1, 11));
	int numiterRL=PyLong_AsLong(PyList_GetItem(pylist1, 12));
	int startiterRL=PyLong_AsLong(PyList_GetItem(pylist1, 13));
	int waititerRL=PyLong_AsLong(PyList_GetItem(pylist1, 14));
	int zex=PyLong_AsLong(PyList_GetItem(pylist1, 15));
	int zey=PyLong_AsLong(PyList_GetItem(pylist1, 16));
	int zez=PyLong_AsLong(PyList_GetItem(pylist1, 17));
	double beta=PyFloat_AsDouble(PyList_GetItem(pylist1, 18));
	int accel=PyLong_AsLong(PyList_GetItem(pylist1, 19));
	
	if (!PyCallable_Check(updatereal))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updaterecip))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updatelog))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updatelog2))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	Py_XINCREF(updatereal);
	Py_XINCREF(updaterecip);
	Py_XINCREF(updatelog);
	Py_XINCREF(updatelog2);
	
	SeqArrayObjects seqarrays;
	seqarrays.arraytype = (int) PyArray_TYPE(p2arg0);
	seqarrays.ndim = ndim;
	seqarrays.dims = (npy_intp*) PyArray_DIMS(p2arg0);
	seqarrays.nn[0] = nn[0];
	seqarrays.nn[1] = nn[1];
	seqarrays.nn[2] = nn[2];
	seqarrays.nn2[0] = nn2[0];
	seqarrays.nn2[1] = nn2[1];
	seqarrays.nn2[2] = nn2[2];
	seqarrays.seqdata = seqdata;
	seqarrays.expdata = expdata;
	seqarrays.support = support;
	seqarrays.mask = mask;
	seqarrays.pca_gamma_ft = pca_gamma_ft;
	seqarrays.rho_m1 = rho_m1;
	seqarrays.pca_inten = pca_inten;
    seqarrays.pca_rho_m1_ft = pca_rho_m1_ft;
    seqarrays.pca_Idm_iter = pca_Idm_iter;
    seqarrays.pca_Idmdiv_iter = pca_Idmdiv_iter;
    seqarrays.pca_IdmdivId_iter = pca_IdmdivId_iter;
	seqarrays.tmparray1 = tmparray1;
	seqarrays.tmparray2 = tmparray2;
	seqarrays.citer_flow = citer_flow;
	seqarrays.startiter = startiter;
	seqarrays.numiter = numiter;
	
	SeqObjects seqobs;
	seqobs.residual = residual;
	seqobs.residualRL = residualRL;
	seqobs.citer_flow = citer_flow;
	seqobs.visual_amp_real = visual_amp_real;
	seqobs.visual_phase_real = visual_phase_real;
	seqobs.visual_amp_recip = visual_amp_recip;
	seqobs.visual_phase_recip = visual_phase_recip;
	seqobs.updatereal = updatereal;
	seqobs.updaterecip = updaterecip;
	seqobs.updatelog = updatelog;
	seqobs.updatelog2 = updatelog2;
	seqobs.startiter = startiter;
	seqobs.numiter = numiter;
	seqobs.beta = beta;
	seqobs.gammaHWHM = gammaHWHM;
	seqobs.gammaRS = gammaRS;
	seqobs.numiterRL = numiterRL;
	seqobs.startiterRL = startiterRL;
	seqobs.waititerRL = waititerRL;
	seqobs.zex = zex;
	seqobs.zey = zey;
	seqobs.zez = zez;
	seqobs.accel = accel;
	
	HIOMaskPC(&seqobs,&seqarrays);
	
	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* prfftw_ermaskpc(PyObject *self, PyObject *args)
{
	PyObject *pylist1=NULL;
	PyObject *pylist2=NULL;
	if (!PyArg_ParseTuple(args, "OO", &pylist1, &pylist2)){return NULL;};
	
	PyArrayObject *p2arg0=(PyArrayObject*) PyList_GetItem(pylist2, 0); double *seqdata = (double*) PyArray_DATA(p2arg0);
	PyArrayObject *p2arg1=(PyArrayObject*) PyList_GetItem(pylist2, 1); double *expdata = (double*) PyArray_DATA(p2arg1);
	PyArrayObject *p2arg2=(PyArrayObject*) PyList_GetItem(pylist2, 2); double *support = (double*) PyArray_DATA(p2arg2);
	PyArrayObject *p2arg3=(PyArrayObject*) PyList_GetItem(pylist2, 3); double *mask = (double*) PyArray_DATA(p2arg3);
	PyArrayObject *p2arg4=(PyArrayObject*) PyList_GetItem(pylist2, 4); double *pca_gamma_ft = (double*) PyArray_DATA(p2arg4);
	PyArrayObject *p2arg5=(PyArrayObject*) PyList_GetItem(pylist2, 5); double *rho_m1 = (double*) PyArray_DATA(p2arg5);
	PyArrayObject *p2arg6=(PyArrayObject*) PyList_GetItem(pylist2, 6); double *pca_inten = (double*) PyArray_DATA(p2arg6);
	PyArrayObject *p2arg7=(PyArrayObject*) PyList_GetItem(pylist2, 7); double *pca_rho_m1_ft = (double*) PyArray_DATA(p2arg7);
	PyArrayObject *p2arg8=(PyArrayObject*) PyList_GetItem(pylist2, 8); double *pca_Idm_iter = (double*) PyArray_DATA(p2arg8);
	PyArrayObject *p2arg9=(PyArrayObject*) PyList_GetItem(pylist2, 9); double *pca_Idmdiv_iter = (double*) PyArray_DATA(p2arg9);
	PyArrayObject *p2arg10=(PyArrayObject*) PyList_GetItem(pylist2, 10); double *pca_IdmdivId_iter = (double*) PyArray_DATA(p2arg10);
	PyArrayObject *p2arg11=(PyArrayObject*) PyList_GetItem(pylist2, 11); double *tmparray1 = (double*) PyArray_DATA(p2arg11);
	PyArrayObject *p2arg12=(PyArrayObject*) PyList_GetItem(pylist2, 12); double *tmparray2 = (double*) PyArray_DATA(p2arg12);
	PyArrayObject *p2arg13=(PyArrayObject*) PyList_GetItem(pylist2, 13); int32_t  *nn = (int32_t*) PyArray_DATA(p2arg13);
	int ndim=PyLong_AsLong(PyList_GetItem(pylist2, 14));
	PyArrayObject *p2arg15=(PyArrayObject*) PyList_GetItem(pylist2, 15); int32_t  *nn2 = (int32_t*) PyArray_DATA(p2arg15);
	int startiter=PyLong_AsLong(PyList_GetItem(pylist2, 16));
	int numiter=PyLong_AsLong(PyList_GetItem(pylist2, 17));
	PyArrayObject *p2arg18=(PyArrayObject*) PyList_GetItem(pylist2, 18); int32_t  *citer_flow = (int32_t*) PyArray_DATA(p2arg18);
	
	PyArrayObject *p1arg0=(PyArrayObject*) PyList_GetItem(pylist1, 0); double *residual = (double*) PyArray_DATA(p1arg0);
	PyArrayObject *p1arg1=(PyArrayObject*) PyList_GetItem(pylist1, 1); double *residualRL = (double*) PyArray_DATA(p1arg1);
	PyArrayObject *p1arg2=(PyArrayObject*) PyList_GetItem(pylist1, 2); double *visual_amp_real = (double*) PyArray_DATA(p1arg2);
	PyArrayObject *p1arg3=(PyArrayObject*) PyList_GetItem(pylist1, 3); double *visual_phase_real = (double*) PyArray_DATA(p1arg3);
	PyArrayObject *p1arg4=(PyArrayObject*) PyList_GetItem(pylist1, 4); double *visual_amp_recip = (double*) PyArray_DATA(p1arg4);
	PyArrayObject *p1arg5=(PyArrayObject*) PyList_GetItem(pylist1, 5); double *visual_phase_recip = (double*) PyArray_DATA(p1arg5);
	PyObject *updatereal=PyList_GetItem(pylist1, 6); 
	PyObject *updaterecip=PyList_GetItem(pylist1, 7); 
	PyObject *updatelog=PyList_GetItem(pylist1, 8); 
	PyObject *updatelog2=PyList_GetItem(pylist1, 9);
	double gammaHWHM=PyFloat_AsDouble(PyList_GetItem(pylist1, 10));
	int gammaRS=PyLong_AsLong(PyList_GetItem(pylist1, 11));
	int numiterRL=PyLong_AsLong(PyList_GetItem(pylist1, 12));
	int startiterRL=PyLong_AsLong(PyList_GetItem(pylist1, 13));
	int waititerRL=PyLong_AsLong(PyList_GetItem(pylist1, 14));
	int zex=PyLong_AsLong(PyList_GetItem(pylist1, 15));
	int zey=PyLong_AsLong(PyList_GetItem(pylist1, 16));
	int zez=PyLong_AsLong(PyList_GetItem(pylist1, 17));
	int accel=PyLong_AsLong(PyList_GetItem(pylist1, 18));
	
	if (!PyCallable_Check(updatereal))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updaterecip))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updatelog))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updatelog2))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	Py_XINCREF(updatereal);
	Py_XINCREF(updaterecip);
	Py_XINCREF(updatelog);
	Py_XINCREF(updatelog2);
	
	SeqArrayObjects seqarrays;
	seqarrays.arraytype = (int) PyArray_TYPE(p2arg0);
	seqarrays.ndim = ndim;
	seqarrays.dims = (npy_intp*) PyArray_DIMS(p2arg0);
	seqarrays.nn[0] = nn[0];
	seqarrays.nn[1] = nn[1];
	seqarrays.nn[2] = nn[2];
	seqarrays.nn2[0] = nn2[0];
	seqarrays.nn2[1] = nn2[1];
	seqarrays.nn2[2] = nn2[2];
	seqarrays.seqdata = seqdata;
	seqarrays.expdata = expdata;
	seqarrays.support = support;
	seqarrays.mask = mask;
	seqarrays.pca_gamma_ft = pca_gamma_ft;
	seqarrays.rho_m1 = rho_m1;
	seqarrays.pca_inten = pca_inten;
    seqarrays.pca_rho_m1_ft = pca_rho_m1_ft;
    seqarrays.pca_Idm_iter = pca_Idm_iter;
    seqarrays.pca_Idmdiv_iter = pca_Idmdiv_iter;
    seqarrays.pca_IdmdivId_iter = pca_IdmdivId_iter;
	seqarrays.tmparray1 = tmparray1;
	seqarrays.tmparray2 = tmparray2;
	seqarrays.citer_flow = citer_flow;
	seqarrays.startiter = startiter;
	seqarrays.numiter = numiter;
	
	SeqObjects seqobs;
	seqobs.residual = residual;
	seqobs.residualRL = residualRL;
	seqobs.citer_flow = citer_flow;
	seqobs.visual_amp_real = visual_amp_real;
	seqobs.visual_phase_real = visual_phase_real;
	seqobs.visual_amp_recip = visual_amp_recip;
	seqobs.visual_phase_recip = visual_phase_recip;
	seqobs.updatereal = updatereal;
	seqobs.updaterecip = updaterecip;
	seqobs.updatelog = updatelog;
	seqobs.updatelog2 = updatelog2;
	seqobs.startiter = startiter;
	seqobs.numiter = numiter;
	seqobs.gammaHWHM = gammaHWHM;
	seqobs.gammaRS = gammaRS;
	seqobs.numiterRL = numiterRL;
	seqobs.startiterRL = startiterRL;
	seqobs.waititerRL = waititerRL;
	seqobs.zex = zex;
	seqobs.zey = zey;
	seqobs.zez = zez;
	seqobs.accel = accel;
	
	ERMaskPC(&seqobs,&seqarrays);

	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* prfftw_hprmaskpc(PyObject *self, PyObject *args)
{
	PyObject *pylist1=NULL;
	PyObject *pylist2=NULL;
	if (!PyArg_ParseTuple(args, "OO", &pylist1, &pylist2)){return NULL;};
	
	PyArrayObject *p2arg0=(PyArrayObject*) PyList_GetItem(pylist2, 0); double *seqdata = (double*) PyArray_DATA(p2arg0);
	PyArrayObject *p2arg1=(PyArrayObject*) PyList_GetItem(pylist2, 1); double *expdata = (double*) PyArray_DATA(p2arg1);
	PyArrayObject *p2arg2=(PyArrayObject*) PyList_GetItem(pylist2, 2); double *support = (double*) PyArray_DATA(p2arg2);
	PyArrayObject *p2arg3=(PyArrayObject*) PyList_GetItem(pylist2, 3); double *mask = (double*) PyArray_DATA(p2arg3);
	PyArrayObject *p2arg4=(PyArrayObject*) PyList_GetItem(pylist2, 4); double *pca_gamma_ft = (double*) PyArray_DATA(p2arg4);
	PyArrayObject *p2arg5=(PyArrayObject*) PyList_GetItem(pylist2, 5); double *rho_m1 = (double*) PyArray_DATA(p2arg5);
	PyArrayObject *p2arg6=(PyArrayObject*) PyList_GetItem(pylist2, 6); double *pca_inten = (double*) PyArray_DATA(p2arg6);
	PyArrayObject *p2arg7=(PyArrayObject*) PyList_GetItem(pylist2, 7); double *pca_rho_m1_ft = (double*) PyArray_DATA(p2arg7);
	PyArrayObject *p2arg8=(PyArrayObject*) PyList_GetItem(pylist2, 8); double *pca_Idm_iter = (double*) PyArray_DATA(p2arg8);
	PyArrayObject *p2arg9=(PyArrayObject*) PyList_GetItem(pylist2, 9); double *pca_Idmdiv_iter = (double*) PyArray_DATA(p2arg9);
	PyArrayObject *p2arg10=(PyArrayObject*) PyList_GetItem(pylist2, 10); double *pca_IdmdivId_iter = (double*) PyArray_DATA(p2arg10);
	PyArrayObject *p2arg11=(PyArrayObject*) PyList_GetItem(pylist2, 11); double *tmparray1 = (double*) PyArray_DATA(p2arg11);
	PyArrayObject *p2arg12=(PyArrayObject*) PyList_GetItem(pylist2, 12); double *tmparray2 = (double*) PyArray_DATA(p2arg12);
	PyArrayObject *p2arg13=(PyArrayObject*) PyList_GetItem(pylist2, 13); int32_t  *nn = (int32_t*) PyArray_DATA(p2arg13);
	int ndim=PyLong_AsLong(PyList_GetItem(pylist2, 14));
	PyArrayObject *p2arg15=(PyArrayObject*) PyList_GetItem(pylist2, 15); int32_t  *nn2 = (int32_t*) PyArray_DATA(p2arg15);
	int startiter=PyLong_AsLong(PyList_GetItem(pylist2, 16));
	int numiter=PyLong_AsLong(PyList_GetItem(pylist2, 17));
	PyArrayObject *p2arg18=(PyArrayObject*) PyList_GetItem(pylist2, 18); int32_t  *citer_flow = (int32_t*) PyArray_DATA(p2arg18);
	
	PyArrayObject *p1arg0=(PyArrayObject*) PyList_GetItem(pylist1, 0); double *residual = (double*) PyArray_DATA(p1arg0);
	PyArrayObject *p1arg1=(PyArrayObject*) PyList_GetItem(pylist1, 1); double *residualRL = (double*) PyArray_DATA(p1arg1);
	PyArrayObject *p1arg2=(PyArrayObject*) PyList_GetItem(pylist1, 2); double *visual_amp_real = (double*) PyArray_DATA(p1arg2);
	PyArrayObject *p1arg3=(PyArrayObject*) PyList_GetItem(pylist1, 3); double *visual_phase_real = (double*) PyArray_DATA(p1arg3);
	PyArrayObject *p1arg4=(PyArrayObject*) PyList_GetItem(pylist1, 4); double *visual_amp_recip = (double*) PyArray_DATA(p1arg4);
	PyArrayObject *p1arg5=(PyArrayObject*) PyList_GetItem(pylist1, 5); double *visual_phase_recip = (double*) PyArray_DATA(p1arg5);
	PyObject *updatereal=PyList_GetItem(pylist1, 6); 
	PyObject *updaterecip=PyList_GetItem(pylist1, 7); 
	PyObject *updatelog=PyList_GetItem(pylist1, 8); 
	PyObject *updatelog2=PyList_GetItem(pylist1, 9);
	double gammaHWHM=PyFloat_AsDouble(PyList_GetItem(pylist1, 10));
	int gammaRS=PyLong_AsLong(PyList_GetItem(pylist1, 11));
	int numiterRL=PyLong_AsLong(PyList_GetItem(pylist1, 12));
	int startiterRL=PyLong_AsLong(PyList_GetItem(pylist1, 13));
	int waititerRL=PyLong_AsLong(PyList_GetItem(pylist1, 14));
	int zex=PyLong_AsLong(PyList_GetItem(pylist1, 15));
	int zey=PyLong_AsLong(PyList_GetItem(pylist1, 16));
	int zez=PyLong_AsLong(PyList_GetItem(pylist1, 17));
	double beta=PyFloat_AsDouble(PyList_GetItem(pylist1, 18));
	int accel=PyLong_AsLong(PyList_GetItem(pylist1, 19));
	
	if (!PyCallable_Check(updatereal))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updaterecip))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updatelog))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updatelog2))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	Py_XINCREF(updatereal);
	Py_XINCREF(updaterecip);
	Py_XINCREF(updatelog);
	Py_XINCREF(updatelog2);
	
	SeqArrayObjects seqarrays;
	seqarrays.arraytype = (int) PyArray_TYPE(p2arg0);
	seqarrays.ndim = ndim;
	seqarrays.dims = (npy_intp*) PyArray_DIMS(p2arg0);
	seqarrays.nn[0] = nn[0];
	seqarrays.nn[1] = nn[1];
	seqarrays.nn[2] = nn[2];
	seqarrays.nn2[0] = nn2[0];
	seqarrays.nn2[1] = nn2[1];
	seqarrays.nn2[2] = nn2[2];
	seqarrays.seqdata = seqdata;
	seqarrays.expdata = expdata;
	seqarrays.support = support;
	seqarrays.mask = mask;
	seqarrays.pca_gamma_ft = pca_gamma_ft;
	seqarrays.rho_m1 = rho_m1;
	seqarrays.pca_inten = pca_inten;
    seqarrays.pca_rho_m1_ft = pca_rho_m1_ft;
    seqarrays.pca_Idm_iter = pca_Idm_iter;
    seqarrays.pca_Idmdiv_iter = pca_Idmdiv_iter;
    seqarrays.pca_IdmdivId_iter = pca_IdmdivId_iter;
	seqarrays.tmparray1 = tmparray1;
	seqarrays.tmparray2 = tmparray2;
	seqarrays.citer_flow = citer_flow;
	seqarrays.startiter = startiter;
	seqarrays.numiter = numiter;
	
	SeqObjects seqobs;
	seqobs.residual = residual;
	seqobs.residualRL = residualRL;
	seqobs.citer_flow = citer_flow;
	seqobs.visual_amp_real = visual_amp_real;
	seqobs.visual_phase_real = visual_phase_real;
	seqobs.visual_amp_recip = visual_amp_recip;
	seqobs.visual_phase_recip = visual_phase_recip;
	seqobs.updatereal = updatereal;
	seqobs.updaterecip = updaterecip;
	seqobs.updatelog = updatelog;
	seqobs.updatelog2 = updatelog2;
	seqobs.startiter = startiter;
	seqobs.numiter = numiter;
	seqobs.beta = beta;
	seqobs.gammaHWHM = gammaHWHM;
	seqobs.gammaRS = gammaRS;
	seqobs.numiterRL = numiterRL;
	seqobs.startiterRL = startiterRL;
	seqobs.waititerRL = waititerRL;
	seqobs.zex = zex;
	seqobs.zey = zey;
	seqobs.zez = zez;
	seqobs.accel = accel;
	
	HPRMaskPC(&seqobs,&seqarrays);

	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* prfftw_raarmaskpc(PyObject *self, PyObject *args)
{
	PyObject *pylist1=NULL;
	PyObject *pylist2=NULL;
	if (!PyArg_ParseTuple(args, "OO", &pylist1, &pylist2)){return NULL;};
	
	PyArrayObject *p2arg0=(PyArrayObject*) PyList_GetItem(pylist2, 0); double *seqdata = (double*) PyArray_DATA(p2arg0);
	PyArrayObject *p2arg1=(PyArrayObject*) PyList_GetItem(pylist2, 1); double *expdata = (double*) PyArray_DATA(p2arg1);
	PyArrayObject *p2arg2=(PyArrayObject*) PyList_GetItem(pylist2, 2); double *support = (double*) PyArray_DATA(p2arg2);
	PyArrayObject *p2arg3=(PyArrayObject*) PyList_GetItem(pylist2, 3); double *mask = (double*) PyArray_DATA(p2arg3);
	PyArrayObject *p2arg4=(PyArrayObject*) PyList_GetItem(pylist2, 4); double *pca_gamma_ft = (double*) PyArray_DATA(p2arg4);
	PyArrayObject *p2arg5=(PyArrayObject*) PyList_GetItem(pylist2, 5); double *rho_m1 = (double*) PyArray_DATA(p2arg5);
	PyArrayObject *p2arg6=(PyArrayObject*) PyList_GetItem(pylist2, 6); double *pca_inten = (double*) PyArray_DATA(p2arg6);
	PyArrayObject *p2arg7=(PyArrayObject*) PyList_GetItem(pylist2, 7); double *pca_rho_m1_ft = (double*) PyArray_DATA(p2arg7);
	PyArrayObject *p2arg8=(PyArrayObject*) PyList_GetItem(pylist2, 8); double *pca_Idm_iter = (double*) PyArray_DATA(p2arg8);
	PyArrayObject *p2arg9=(PyArrayObject*) PyList_GetItem(pylist2, 9); double *pca_Idmdiv_iter = (double*) PyArray_DATA(p2arg9);
	PyArrayObject *p2arg10=(PyArrayObject*) PyList_GetItem(pylist2, 10); double *pca_IdmdivId_iter = (double*) PyArray_DATA(p2arg10);
	PyArrayObject *p2arg11=(PyArrayObject*) PyList_GetItem(pylist2, 11); double *tmparray1 = (double*) PyArray_DATA(p2arg11);
	PyArrayObject *p2arg12=(PyArrayObject*) PyList_GetItem(pylist2, 12); double *tmparray2 = (double*) PyArray_DATA(p2arg12);
	PyArrayObject *p2arg13=(PyArrayObject*) PyList_GetItem(pylist2, 13); int32_t  *nn = (int32_t*) PyArray_DATA(p2arg13);
	int ndim=PyLong_AsLong(PyList_GetItem(pylist2, 14));
	PyArrayObject *p2arg15=(PyArrayObject*) PyList_GetItem(pylist2, 15); int32_t  *nn2 = (int32_t*) PyArray_DATA(p2arg15);
	int startiter=PyLong_AsLong(PyList_GetItem(pylist2, 16));
	int numiter=PyLong_AsLong(PyList_GetItem(pylist2, 17));
	PyArrayObject *p2arg18=(PyArrayObject*) PyList_GetItem(pylist2, 18); int32_t  *citer_flow = (int32_t*) PyArray_DATA(p2arg18);
	
	PyArrayObject *p1arg0=(PyArrayObject*) PyList_GetItem(pylist1, 0); double *residual = (double*) PyArray_DATA(p1arg0);
	PyArrayObject *p1arg1=(PyArrayObject*) PyList_GetItem(pylist1, 1); double *residualRL = (double*) PyArray_DATA(p1arg1);
	PyArrayObject *p1arg2=(PyArrayObject*) PyList_GetItem(pylist1, 2); double *visual_amp_real = (double*) PyArray_DATA(p1arg2);
	PyArrayObject *p1arg3=(PyArrayObject*) PyList_GetItem(pylist1, 3); double *visual_phase_real = (double*) PyArray_DATA(p1arg3);
	PyArrayObject *p1arg4=(PyArrayObject*) PyList_GetItem(pylist1, 4); double *visual_amp_recip = (double*) PyArray_DATA(p1arg4);
	PyArrayObject *p1arg5=(PyArrayObject*) PyList_GetItem(pylist1, 5); double *visual_phase_recip = (double*) PyArray_DATA(p1arg5);
	PyObject *updatereal=PyList_GetItem(pylist1, 6); 
	PyObject *updaterecip=PyList_GetItem(pylist1, 7); 
	PyObject *updatelog=PyList_GetItem(pylist1, 8); 
	PyObject *updatelog2=PyList_GetItem(pylist1, 9);
	double gammaHWHM=PyFloat_AsDouble(PyList_GetItem(pylist1, 10));
	int gammaRS=PyLong_AsLong(PyList_GetItem(pylist1, 11));
	int numiterRL=PyLong_AsLong(PyList_GetItem(pylist1, 12));
	int startiterRL=PyLong_AsLong(PyList_GetItem(pylist1, 13));
	int waititerRL=PyLong_AsLong(PyList_GetItem(pylist1, 14));
	int zex=PyLong_AsLong(PyList_GetItem(pylist1, 15));
	int zey=PyLong_AsLong(PyList_GetItem(pylist1, 16));
	int zez=PyLong_AsLong(PyList_GetItem(pylist1, 17));
	double beta=PyFloat_AsDouble(PyList_GetItem(pylist1, 18));
	int accel=PyLong_AsLong(PyList_GetItem(pylist1, 19));
	
	if (!PyCallable_Check(updatereal))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updaterecip))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updatelog))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updatelog2))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	Py_XINCREF(updatereal);
	Py_XINCREF(updaterecip);
	Py_XINCREF(updatelog);
	Py_XINCREF(updatelog2);
	
	SeqArrayObjects seqarrays;
	seqarrays.arraytype = (int) PyArray_TYPE(p2arg0);
	seqarrays.ndim = ndim;
	seqarrays.dims = (npy_intp*) PyArray_DIMS(p2arg0);
	seqarrays.nn[0] = nn[0];
	seqarrays.nn[1] = nn[1];
	seqarrays.nn[2] = nn[2];
	seqarrays.nn2[0] = nn2[0];
	seqarrays.nn2[1] = nn2[1];
	seqarrays.nn2[2] = nn2[2];
	seqarrays.seqdata = seqdata;
	seqarrays.expdata = expdata;
	seqarrays.support = support;
	seqarrays.mask = mask;
	seqarrays.pca_gamma_ft = pca_gamma_ft;
	seqarrays.rho_m1 = rho_m1;
	seqarrays.pca_inten = pca_inten;
    seqarrays.pca_rho_m1_ft = pca_rho_m1_ft;
    seqarrays.pca_Idm_iter = pca_Idm_iter;
    seqarrays.pca_Idmdiv_iter = pca_Idmdiv_iter;
    seqarrays.pca_IdmdivId_iter = pca_IdmdivId_iter;
	seqarrays.tmparray1 = tmparray1;
	seqarrays.tmparray2 = tmparray2;
	seqarrays.citer_flow = citer_flow;
	seqarrays.startiter = startiter;
	seqarrays.numiter = numiter;
	
	SeqObjects seqobs;
	seqobs.residual = residual;
	seqobs.residualRL = residualRL;
	seqobs.citer_flow = citer_flow;
	seqobs.visual_amp_real = visual_amp_real;
	seqobs.visual_phase_real = visual_phase_real;
	seqobs.visual_amp_recip = visual_amp_recip;
	seqobs.visual_phase_recip = visual_phase_recip;
	seqobs.updatereal = updatereal;
	seqobs.updaterecip = updaterecip;
	seqobs.updatelog = updatelog;
	seqobs.updatelog2 = updatelog2;
	seqobs.startiter = startiter;
	seqobs.numiter = numiter;
	seqobs.beta = beta;
	seqobs.gammaHWHM = gammaHWHM;
	seqobs.gammaRS = gammaRS;
	seqobs.numiterRL = numiterRL;
	seqobs.startiterRL = startiterRL;
	seqobs.waititerRL = waititerRL;
	seqobs.zex = zex;
	seqobs.zey = zey;
	seqobs.zez = zez;
	seqobs.accel = accel;
	
	RAARMaskPC(&seqobs,&seqarrays);

	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* prfftw_so2d(PyObject *self, PyObject *args)
{
	PyArrayObject *arg1=NULL, *arg2=NULL, *arg3=NULL, *arg4=NULL;
	double alpha,beta; int startiter, numiter;
	int maxiter;
	PyArrayObject *arg5=NULL, *arg6=NULL, *arg7=NULL, *arg8=NULL;
	PyArrayObject *arg9=NULL, *arg10=NULL, *arg11=NULL, *arg12=NULL;
	PyArrayObject *arg13=NULL, *arg14=NULL;
	PyArrayObject *stepobj=NULL;
	PyObject *updatereal, *updaterecip, *updatelog;

    if (!PyArg_ParseTuple(args, "OOOOddiiOiOOOOOOOOOOOOO",
		&arg1, &arg2, &arg3, &arg4, &alpha, &beta, &startiter, &numiter,
		&stepobj, &maxiter, &arg5, &arg6, &arg7,
		&arg8, &arg9, &arg10, &arg11, &arg12, &arg13, &arg14,
		&updatereal, &updaterecip, &updatelog))
        {return NULL;};
	
	SeqArrayObjects seqarrays;
	seqarrays.arraytype = (int) PyArray_TYPE(arg1);
	seqarrays.ndim = (int) PyArray_NDIM(arg1);
	seqarrays.dims = (npy_intp*) PyArray_DIMS(arg1);
	seqarrays.nn[0] = (int32_t) seqarrays.dims[0];
	seqarrays.nn[1] = (int32_t) seqarrays.dims[1];
	seqarrays.nn[2] = (int32_t) seqarrays.dims[2];
	seqarrays.seqdata = (double*) PyArray_DATA(arg1);
	seqarrays.expdata = (double*) PyArray_DATA(arg2);
	seqarrays.support = (double*) PyArray_DATA(arg3);
	seqarrays.mask = (double*) PyArray_DATA(arg4);
	seqarrays.epsilon = (double*) PyArray_DATA(arg5);
	seqarrays.rho_m1 = (double*) PyArray_DATA(arg6);
	seqarrays.rho_m2 = (double*) PyArray_DATA(arg7);
	seqarrays.tmparray1 = (double*) PyArray_DATA(arg8);
	seqarrays.tmparray2 = (double*) PyArray_DATA(stepobj);
	seqarrays.citer_flow = (int32_t*) PyArray_DATA(arg10);
	seqarrays.startiter = startiter;
	seqarrays.numiter = numiter;
	
	SeqObjects seqobs;
	seqobs.residual = (double*) PyArray_DATA(arg9);
	seqobs.citer_flow = (int32_t*) PyArray_DATA(arg10);
	seqobs.visual_amp_real = (double*) PyArray_DATA(arg11);
	seqobs.visual_phase_real = (double*) PyArray_DATA(arg12);
	seqobs.visual_amp_recip = (double*) PyArray_DATA(arg13);
	seqobs.visual_phase_recip = (double*) PyArray_DATA(arg14);
	seqobs.updatereal = updatereal;
	seqobs.updaterecip = updaterecip;
	seqobs.updatelog = updatelog;
	seqobs.startiter = startiter;
	seqobs.numiter = numiter;
	seqobs.maxiter = maxiter;
	seqobs.alpha = alpha;
	seqobs.beta = beta;
	
	if (!PyCallable_Check(updatereal))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updaterecip))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	if (!PyCallable_Check(updatelog))
	{
		PyErr_SetString(PyExc_TypeError, "function must be callable");
		return NULL;
	}
	Py_XINCREF(updatereal);
	Py_XINCREF(updaterecip);
	Py_XINCREF(updatelog);
	
	SO2D(&seqobs,&seqarrays);

	Py_INCREF(Py_None);
	return Py_None;
}


PyObject* prfftw_threshold(PyObject *self, PyObject *args)
{
	PyArrayObject *arg1=NULL;
	double threshmin, threshmax, newval;
	int i;
	npy_intp *dims;
	double val = 0.0;
	double *data;
	int32_t nn[3];
	int64_t len;

    if (!PyArg_ParseTuple(args, "Oddd",
		&arg1, &threshmin, &threshmax, &newval))
        {return NULL;};
	
	
	dims = PyArray_DIMS(arg1);
	data = (double*) PyArray_DATA(arg1);
	Py_BEGIN_ALLOW_THREADS;
	nn[0] = (int32_t) dims[0]; nn[1] = (int32_t) dims[1]; nn[2] = (int32_t) dims[2];
	len =  (int64_t) nn[0] * nn[1] * nn[2];
    for(i=0; i<len; i++)
	{
		val  = sqrt(data[2*i] * data[2*i] + data[2*i+1] * data[2*i+1]);
		if(val < threshmin || val > threshmax)
		{
			data[2*i] = newval;
			data[2*i+1] = 0.0;
		}
	}
	Py_END_ALLOW_THREADS;
	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* prfftw_rangereplace(PyObject *self, PyObject *args)
{
	PyArrayObject *arg1=NULL;
	double threshmin, threshmax, newval_out, newval_in;
	int i;
	npy_intp *dims;
	double val = 0.0;
	double *data;
	int32_t nn[3];
	int64_t len;

    if (!PyArg_ParseTuple(args, "Odddd",
		&arg1, &threshmin, &threshmax, &newval_out, &newval_in))
        {return NULL;};
	
	dims = PyArray_DIMS(arg1);
	data = (double*) PyArray_DATA(arg1);
	Py_BEGIN_ALLOW_THREADS;
	nn[0] = (int32_t) dims[0]; nn[1] = (int32_t) dims[1]; nn[2] = (int32_t) dims[2];
	len =  (int64_t) nn[0] * nn[1] * nn[2];
    for(i=0; i<len; i++)
	{
		val  = sqrt(data[2*i] * data[2*i] + data[2*i+1] * data[2*i+1]);
		if(val < threshmin || val > threshmax)
		{
			data[2*i] = newval_out;
			data[2*i+1] = 0.0;
		}
		else
		{
			data[2*i] = newval_in;
			data[2*i+1] = 0.0;
		}
	}
	Py_END_ALLOW_THREADS;
	Py_INCREF(Py_None);
	return Py_None;
}

extern void idx2ijk(int64_t idx, int32_t* i, int32_t* j, int32_t* k, int32_t* dims);

void gaussian_fill(PyArrayObject* arg1, double sigma)
{
	int i,j,k,ii;
	npy_intp *dims = PyArray_DIMS(arg1);
	double *data = (double*) PyArray_DATA(arg1);
	double pi = 3.141592653589793238462643;
	int32_t nn[3];
	nn[0] = (int32_t) dims[0]; nn[1] = (int32_t) dims[1]; nn[2] = (int32_t) dims[2];
	for(i=0;i<nn[0]; i++)
	{
		for(j=0;j<nn[1]; j++)
		{
			for(k=0;k<nn[2]; k++)
			{
				ii = (k+nn[2]*(j+nn[1]*i));
				data[2*ii] = (1.0/(sigma*sqrt(2.0*pi))) * exp(((double) (i-nn[0]/2)*(i-nn[0]/2)
									+(j-nn[1]/2)*(j-nn[1]/2)
									+(k-nn[2]/2)*(k-nn[2]/2))
									/(-2.0*sigma*sigma));
				data[2*ii+1] = 0.0;
			}
		}
	}
}

void lorentz_ft_fill
(
	double* data,
	int32_t* nn,
	double gammaHWHM
)
{
	int i,j,k,ii;
	double r;
	double rmax = sqrt((double) (nn[0]/2)*(nn[0]/2)+(nn[1]/2)*(nn[1]/2)+(nn[2]/2)*(nn[2]/2));
	for(i=0;i<nn[0]; i++)
	{
		for(j=0;j<nn[1]; j++)
		{
			for(k=0;k<nn[2]; k++)
			{
				ii = (k+nn[2]*(j+nn[1]*i));
				r = sqrt((double) (i-nn[0]/2)*(i-nn[0]/2)+(j-nn[1]/2)*(j-nn[1]/2)+(k-nn[2]/2)*(k-nn[2]/2));
				
				data[2*ii] = fabs(gammaHWHM) * exp(- fabs(gammaHWHM)*r) / 
				(-2.0 *( exp(-fabs(gammaHWHM)*rmax) - 1.0)) ;
				data[2*ii+1] = 0.0;
			}
		}
	}
}

PyObject* prfftw_lorentz_ft_fill(PyObject *self, PyObject *args)
{
	PyArrayObject *arg1=NULL;
	npy_intp *dims;
	double *indata;
	int32_t nn[3];
	double gammaHWHM;
    if (!PyArg_ParseTuple(args, "Od", &arg1, &gammaHWHM)){ return NULL;};
	indata = (double*) PyArray_DATA(arg1);
	dims = PyArray_DIMS(arg1);
	nn[0] = (int32_t) dims[0]; nn[1] = (int32_t) dims[1]; nn[2] = (int32_t) dims[2];
	lorentz_ft_fill(indata, nn, gammaHWHM);
	Py_INCREF(Py_None);
	return Py_None;
}


PyObject* prfftw_gaussian_fill(PyObject *self, PyObject *args)
{
	PyArrayObject *arg1=NULL;
	double sigma;
    if (!PyArg_ParseTuple(args, "Od", &arg1, &sigma)){ return NULL;};
	gaussian_fill(arg1, sigma);
	Py_INCREF(Py_None);
	return Py_None;
}


PyObject* prfftw_gaussian_filter(PyObject *self, PyObject *args)
{
	PyArrayObject *arg1=NULL, *arg2=NULL;
	double sigma;
	int i;
	double valp[2] = {0.0,0.0};
	double gaup[2] = {0.0,0.0};
	fftw_plan torecip;
	fftw_plan toreal;
	fftw_plan torecipg;
	fftw_plan torealg;
	double *seqdata;
	double *gaussian;
	npy_intp *dims;
	int32_t ndim;
	int32_t nn[3];
	int len;
	if (!PyArg_ParseTuple(args, "OOd", &arg1, &arg2, &sigma)){ return NULL;};
	seqdata = (double*) PyArray_DATA(arg1);
	gaussian = (double*) PyArray_DATA(arg2);
	dims = PyArray_DIMS(arg1);
	ndim = PyArray_NDIM(arg1);
	nn[0] = (int32_t) dims[0]; nn[1] = (int32_t) dims[1]; nn[2] = (int32_t) dims[2];
	len = nn[0] * nn[1] * nn[2];
	FFTPlan( &torecipg, &torealg, gaussian, nn, ndim );
	CopyArray(seqdata, gaussian, nn);
	FFTPlan( &torecip, &toreal, seqdata, nn, ndim );
	CopyArray(gaussian, seqdata, nn);
	gaussian_fill(arg2, sigma);
	FFTStride(seqdata, nn, &torecip);
	FFTStride(gaussian, nn, &torecipg);
	for(i=0; i<len; i++)
	{
		valp[0] = seqdata[2*i];
		valp[1] = seqdata[2*i+1];
		gaup[0] = gaussian[2*i];
		gaup[1] = gaussian[2*i+1];
		seqdata[2*i] = (valp[0]*gaup[0] - valp[1]*gaup[1])*sqrt((double) len);
		seqdata[2*i+1] = 0.0;
	}
	FFTStride(seqdata, nn, &toreal);
	FFTStride(gaussian, nn, &torealg);
	for(i=0; i<len; i++)
	{
		valp[0] = seqdata[2*i];
		valp[1] = seqdata[2*i+1];
		seqdata[2*i] = sqrt(valp[0]*valp[0] + valp[1]*valp[1]);
		seqdata[2*i+1] = 0.0;
	}
	fftw_destroy_plan( torecip );
	fftw_destroy_plan( toreal );
	fftw_destroy_plan( torecipg );
	fftw_destroy_plan( torealg );
	fftw_cleanup();
	Py_INCREF(Py_None);
	return Py_None;
}


int convolve_nomem2(double* indata1, double* indata2, int32_t ndim, int32_t* dims, double* data1, double* data2, fftw_plan* torecip, fftw_plan* toreal)
{
	int iib, ii, i, j, k;
	int len;
	double val1[2] = {0.0,0.0};
	double val2[2] = {0.0,0.0};
	int32_t nn[3] = {dims[0], dims[1], dims[2]};
	int32_t nnh[3] = {(dims[0] / 2), (dims[1] / 2), (dims[2] / 2)};
	int32_t nn2[3] = {0,0,0};
	nn2[0] = dims[0] + 2*(dims[0]/2);
	nn2[1] = dims[1] + 2*(dims[1]/2);
	nn2[2] = dims[2] + 2*(dims[2]/2);
	if( dims[0] == 1)
	{
		nn2[0] = dims[0];
	}
	if( dims[1] == 1)
	{
		nn2[1] = dims[1];
	}
	if( dims[2] == 1)
	{
		nn2[2] = dims[2];
	}
	len = nn2[0] * nn2[1] * nn2[2];
	for(i=0;i<nn2[0]; i++)
	{
		for(j=0;j<nn2[1]; j++)
		{
			for(k=0;k<nn2[2]; k++)
			{
				iib = (k+nn2[2]*(j+nn2[1]*i));
				data1[2*iib] = 0.0;
				data1[2*iib+1] = 0.0;
				data2[2*iib] = 0.0;
				data2[2*iib+1] = 0.0;
			}
		}
	}
	for(i=0;i<nn[0]; i++)
	{
		for(j=0;j<nn[1]; j++)
		{
			for(k=0;k<nn[2]; k++)
			{
				ii = (k+nn[2]*(j+nn[1]*i));
				iib = ((k+nnh[2])+nn2[2]*((j+nnh[1])+nn2[1]*(i+nnh[0])));
				data1[2*iib] = indata1[2*ii];
				data1[2*iib+1] = indata1[2*ii+1];
				data2[2*iib] = indata2[2*ii];
				data2[2*iib+1] = indata2[2*ii+1];
			}
		}
	}
	wrap_array(data1, nn2, 1);
	wrap_array(data2, nn2, 1);
	FFTStride(data1, nn2, torecip);
	FFTStride(data2, nn2, torecip);
	for(i=0;i<nn2[0]; i++)
	{
		for(j=0;j<nn2[1]; j++)
		{
			for(k=0;k<nn2[2]; k++)
			{
				iib = (k+nn2[2]*(j+nn2[1]*i));
				val1[0] = data1[2*iib];
				val1[1] = data1[2*iib+1];
				val2[0] = data2[2*iib];
				val2[1] = data2[2*iib+1];
				data1[2*iib] = (val1[0]*val2[0] - val1[1]*val2[1])*sqrt((double) len);
				data1[2*iib+1] = (val1[0]*val2[1] + val1[1]*val2[0])*sqrt((double) len);
			}
		}
	}
	FFTStride(data1, nn2, toreal);
	FFTStride(data2, nn2, toreal);
	wrap_array(data1, nn2, -1);
	wrap_array(data2, nn2, -1);
	for(i=0;i<nn[0]; i++)
	{
		for(j=0;j<nn[1]; j++)
		{
			for(k=0;k<nn[2]; k++)
			{
				ii = (k+nn[2]*(j+nn[1]*i));
				iib = ((k+nnh[2])+nn2[2]*((j+nnh[1])+nn2[1]*(i+nnh[0])));
				indata1[2*ii] = data1[2*iib];
				indata1[2*ii+1] = data1[2*iib+1];
			}
		}
	}
	return 0;
}

int convolve2(double* indata1, double* indata2, int32_t ndim, int32_t* dims)
{
	fftw_plan torecip;
	fftw_plan toreal;
	int32_t nn2[3] = {0,0,0};
	int len;
	double* data1;
	double* data2;
	nn2[0] = dims[0] + 2*(dims[0]/2);
	nn2[1] = dims[1] + 2*(dims[1]/2);
	nn2[2] = dims[2] + 2*(dims[2]/2);
	if( dims[0] == 1)
	{
		nn2[0] = dims[0];
	}
	if( dims[1] == 1)
	{
		nn2[1] = dims[1];
	}
	if( dims[2] == 1)
	{
		nn2[2] = dims[2];
	}
	len = nn2[0] * nn2[1] * nn2[2];
	data1 = (double*) fftw_malloc( 2*len * sizeof(double));
	data2 = (double*) fftw_malloc( 2*len * sizeof(double));
	if (!data1 || !data2)
	{
		fftw_free(data1);
		fftw_free(data2);
		return 1;
	}
	FFTPlan( &torecip, &toreal, data1, nn2, ndim );
	convolve_nomem2(indata1, indata2, ndim, dims, data1, data2, &torecip, &toreal);
	fftw_destroy_plan( torecip );
	fftw_destroy_plan( toreal );
	fftw_cleanup();
	fftw_free(data1);
	fftw_free(data2);
	return 0;
}

PyObject* prfftw_convolve2(PyObject *self, PyObject *args)
{
	PyArrayObject *arg1=NULL, *arg2=NULL;
	double *indata1;
	double *indata2;
	npy_intp *dims;
	int32_t ndim;
	int32_t nn[3];
	if (!PyArg_ParseTuple(args, "OO", &arg1, &arg2)){ return NULL;};
	indata1 = (double*) PyArray_DATA(arg1);
	indata2= (double*) PyArray_DATA(arg2);
	dims = PyArray_DIMS(arg1);
	ndim = PyArray_NDIM(arg1);
	nn[0] = (int32_t) dims[0]; nn[1] = (int32_t) dims[1]; nn[2] = (int32_t) dims[2];
	int convolved;
	Py_BEGIN_ALLOW_THREADS;
	convolved = convolve2(indata1, indata2, ndim, nn);
	Py_END_ALLOW_THREADS;
	if (convolved)
	{
		PyErr_NoMemory();
		return PyErr_Occurred();
	}
	Py_INCREF(Py_None);
	return Py_None;
}

void convolve_nomem(double* data1, double* data2, int32_t ndim, int32_t* nn, fftw_plan* torecip, fftw_plan* toreal)
{
	int ii, i, j, k;
	int len = nn[0] * nn[1] * nn[2];
	double val1[2] = {0.0,0.0};
	double val2[2] = {0.0,0.0};
	FFTStride(data1, nn, torecip);
	FFTStride(data2, nn, torecip);
	for(i=0;i<nn[0]; i++)
	{
		for(j=0;j<nn[1]; j++)
		{
			for(k=0;k<nn[2]; k++)
			{
				ii = (k+nn[2]*(j+nn[1]*i));
				val1[0] = data1[2*ii];
				val1[1] = data1[2*ii+1];
				val2[0] = data2[2*ii];
				val2[1] = data2[2*ii+1];
				data1[2*ii] = (val1[0]*val2[0] - val1[1]*val2[1])*sqrt((double) len);
				data1[2*ii+1] = (val1[0]*val2[1] + val1[1]*val2[0])*sqrt((double) len);
			}
		}
	}
	FFTStride(data1, nn, toreal);
	FFTStride(data2, nn, toreal);
}


int convolve(double* indata1, double* indata2, int32_t ndim, int32_t* dims)
{
	fftw_plan torecip;
	fftw_plan toreal;
	int ii, i, j, k;
	int32_t nn[3] = {dims[0], dims[1], dims[2]};
	int len = nn[0] * nn[1] * nn[2];
	double* data1 = (double*) fftw_malloc( 2*len * sizeof(double));
	double* data2 = (double*) fftw_malloc( 2*len * sizeof(double));
	if (!data1 || !data2)
	{
		fftw_free(data1);
		fftw_free(data2);
		return 1;
	}
	FFTPlan( &torecip, &toreal, data1, nn, ndim );
	for(i=0;i<nn[0]; i++)
	{
		for(j=0;j<nn[1]; j++)
		{
			for(k=0;k<nn[2]; k++)
			{
				ii = (k+nn[2]*(j+nn[1]*i));
				data1[2*ii] = indata1[2*ii];
				data1[2*ii+1] = indata1[2*ii+1];
				data2[2*ii] = indata2[2*ii];
				data2[2*ii+1] = indata2[2*ii+1];
			}
		}
	}
	convolve_nomem(data1, data2, ndim, nn, &torecip, &toreal);
	for(i=0;i<nn[0]; i++)
	{
		for(j=0;j<nn[1]; j++)
		{
			for(k=0;k<nn[2]; k++)
			{
				ii = (k+nn[2]*(j+nn[1]*i));
				indata1[2*ii] = data1[2*ii];
				indata1[2*ii+1] = data1[2*ii+1];
			}
		}
	}
	fftw_destroy_plan( torecip );
	fftw_destroy_plan( toreal );
	fftw_cleanup();
	fftw_free(data1);
	fftw_free(data2);
	return 0;
}

PyObject* prfftw_convolve(PyObject *self, PyObject *args)
{
	PyArrayObject *arg1=NULL, *arg2=NULL;
	double *indata1;
	double *indata2;
	npy_intp *dims;
	int32_t ndim;
	int32_t nn[3];
	if (!PyArg_ParseTuple(args, "OO", &arg1, &arg2)){ return NULL;};
	indata1 = (double*) PyArray_DATA(arg1);
	indata2 = (double*) PyArray_DATA(arg2);
	dims = PyArray_DIMS(arg1);
	ndim = PyArray_NDIM(arg1);
	nn[0] = (int32_t) dims[0]; nn[1] = (int32_t) dims[1]; nn[2] = (int32_t) dims[2];
	int convolved;
	Py_BEGIN_ALLOW_THREADS;
	convolved = convolve(indata1, indata2, ndim, nn);
	Py_END_ALLOW_THREADS;
	if (convolved)
	{
		PyErr_NoMemory();
		return PyErr_Occurred();
	}
	Py_INCREF(Py_None);
	return Py_None;
}

int convolve_sw(double* indata1, double* indata2, int32_t ndim, int32_t* dims)
{
	Py_BEGIN_ALLOW_THREADS;
	fftw_plan torecip;
	fftw_plan toreal;
	int ii, i, j, k;
	int32_t nn[3] = {dims[0], dims[1], dims[2]};
	int len = nn[0] * nn[1] * nn[2];
	double val1[2] = {0.0,0.0};
	double val2[2] = {0.0,0.0};

	for(ii=0; ii<len; ii++)
	{
		indata2[2*ii+1] = indata1[2*ii];
	}
	FFTPlan( &torecip, &toreal, indata1, nn, ndim );
	for(ii=0; ii<len; ii++)
	{
		indata1[2*ii] = indata2[2*ii+1];
		indata2[2*ii+1] = 0.0;
	}
	
	FFTStride(indata1, nn, &torecip);
	FFTStride(indata2, nn, &torecip);
	for(i=0;i<nn[0]; i++)
	{
		for(j=0;j<nn[1]; j++)
		{
			for(k=0;k<nn[2]; k++)
			{
				ii = (k+nn[2]*(j+nn[1]*i));
				val1[0] = indata1[2*ii];
				val1[1] = indata1[2*ii+1];
				val2[0] = indata2[2*ii];
				val2[1] = indata2[2*ii+1];
				indata1[2*ii] = (val1[0]*val2[0] - val1[1]*val2[1])*sqrt((double) len);
				indata1[2*ii+1] = (val1[0]*val2[1] + val1[1]*val2[0])*sqrt((double) len);
			}
		}
	}
	FFTStride(indata1, nn, &toreal);
	FFTStride(indata2, nn, &toreal);
	
	fftw_destroy_plan( torecip );
	fftw_destroy_plan( toreal );
	fftw_cleanup();
	Py_END_ALLOW_THREADS;
	return 0;
}


PyObject* prfftw_convolve_sw(PyObject *self, PyObject *args)
{
	PyArrayObject *arg1=NULL, *arg2=NULL;
	double *indata1;
	double *indata2;
	npy_intp *dims;
	int32_t ndim;
	int32_t nn[3];
	if (!PyArg_ParseTuple(args, "OO", &arg1, &arg2)){ return NULL;};
	indata1 = (double*) PyArray_DATA(arg1);
	indata2 = (double*) PyArray_DATA(arg2);
	dims = PyArray_DIMS(arg1);
	ndim = PyArray_NDIM(arg1);
	nn[0] = (int32_t) dims[0]; nn[1] = (int32_t) dims[1]; nn[2] = (int32_t) dims[2];
	int convolved;
	convolved = convolve_sw(indata1, indata2, ndim, nn);
	if (convolved)
	{
		PyErr_NoMemory();
		return PyErr_Occurred();
	}
	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* prfftw_fft(PyObject *self, PyObject *args)
{
	PyArrayObject *arg1=NULL;
	int space;
	double *indata;
	npy_intp *dims;
	int32_t ndim;
	int32_t nn[3];
	int len;
	double* data;
	fftw_plan torecip;
	fftw_plan toreal;
	if (!PyArg_ParseTuple(args, "Oi", &arg1, &space)){ return NULL;};
	indata = (double*) PyArray_DATA(arg1);
	dims = PyArray_DIMS(arg1);
	ndim = PyArray_NDIM(arg1);
	nn[0] = (int32_t) dims[0]; nn[1] = (int32_t) dims[1]; nn[2] = (int32_t) dims[2];
	len = nn[0] * nn[1] * nn[2];
	data = (double*) malloc( 2*len * sizeof(double));
	if (!data)
	{
		PyErr_NoMemory();
		return PyErr_Occurred();
	}
	FFTPlan( &torecip, &toreal, data, nn, ndim );
	if( space > 0)
	{
		FFTStride(indata, nn, &torecip);
	}
	else
	{
		FFTStride(indata, nn, &toreal);
	}
	fftw_destroy_plan( torecip );
	fftw_destroy_plan( toreal );
	fftw_cleanup();
	free(data);
	Py_INCREF(Py_None);
	return Py_None;
}


PyObject* prfftw_conj_reflect(PyObject *self, PyObject *args)
{
	PyArrayObject *arg1=NULL;
	double *indata;
	npy_intp *dims;
	int32_t nn[3];
	if (!PyArg_ParseTuple(args, "O", &arg1)){ return NULL;};
	indata = (double*) PyArray_DATA(arg1);
	dims = PyArray_DIMS(arg1);
	nn[0] = (int32_t) dims[0]; nn[1] = (int32_t) dims[1]; nn[2] = (int32_t) dims[2];
	conj_reflect(indata, nn);
	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* prfftw_medianfilter(PyObject *self, PyObject *args)
{
	double *data1;
	double *data2;
	npy_intp *dims;
	int32_t nn[3];
	PyArrayObject *arg1=NULL;
	PyArrayObject *arg2=NULL;
	int kx, ky, kz;
	double maxerr;
	if (!PyArg_ParseTuple(args, "OOiiid", &arg1, &arg2, &kx, &ky, &kz, &maxerr)){ return NULL;};
	data1 = (double*) PyArray_DATA(arg1);
	data2 = (double*) PyArray_DATA(arg2);
	dims = PyArray_DIMS(arg1);
	nn[0] = (int32_t) dims[0]; nn[1] = (int32_t) dims[1]; nn[2] = (int32_t) dims[2];
	Py_BEGIN_ALLOW_THREADS;
	MedianReplaceVoxel(data1, data2, nn, kx, ky, kz, maxerr);
	Py_END_ALLOW_THREADS;
	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* prfftw_blanklinereplace(PyObject *self, PyObject *args)
{
	double *data1;
	double *data2;
	npy_intp *dims;
	int32_t nn[3];
	PyArrayObject *arg1=NULL;
	PyArrayObject *arg2=NULL;
	int kx, ky, kz;
	int x1, x2, y1, y2, z1, z2;
	if (!PyArg_ParseTuple(args, "OOiiiiiiiii", &arg1, &arg2, &kx, &ky, &kz, &x1, &x2, &y1, &y2, &z1, &z2)){ return NULL;};
	data1 = (double*) PyArray_DATA(arg1);
	data2 = (double*) PyArray_DATA(arg2);
	dims = PyArray_DIMS(arg1);
	nn[0] = (int32_t) dims[0]; nn[1] = (int32_t) dims[1]; nn[2] = (int32_t) dims[2];
	BlankLineReplace(data1, data2, nn, kx, ky, kz, x1, x2, y1, y2, z1, z2);
	Py_INCREF(Py_None);
	return Py_None;
}



static PyMethodDef prfftwMethods[] = {
	{"fftw_stride",  prfftw_fft_stride, METH_VARARGS,
     "FFTW Stride."},
	{"fftw_create_plan",  prfftw_createplan, METH_VARARGS,
     "FFTW Create Plan."},
	 {"fftw_destroy_plan",  prfftw_destroyplan, METH_VARARGS,
     "FFTW Destroy Plan."},
	 {"fft",  prfftw_fft, METH_VARARGS,
     "Fourier transform a complex array."},
	 {"wrap",  prfftw_wrap, METH_VARARGS,
     "Wrap array."},
	 {"wrap_nomem",  prfftw_wrap_nomem, METH_VARARGS,
     "Wrap array, nomem."},
	 {"copy_amp",  prfftw_copy_amp, METH_VARARGS,
     "Copy to real amp array."},
	 {"copy_abs",  prfftw_copy_abs, METH_VARARGS,
     "Copy abs array."},
	 {"max_value",  prfftw_max_value, METH_VARARGS,
     "Max value."},
	 {"medianfilter",  prfftw_medianfilter, METH_VARARGS,
     "Median filter array."},
	 {"blanklinefill",  prfftw_blanklinereplace, METH_VARARGS,
     "Fill blank voxels with non-zero average value."},
	{"conj_reflect",  prfftw_conj_reflect, METH_VARARGS,
     "Reflect and conjugate a complex array."},
	 {"convolve",  prfftw_convolve, METH_VARARGS,
     "Convolve two complex arrays."},
	 {"convolve_sw",  prfftw_convolve_sw, METH_VARARGS,
     "Convolve two complex arrays for shrink-wrap."},
	{"convolve2",  prfftw_convolve2, METH_VARARGS,
     "Convolve two complex arrays."},
	{"gaussian_filter",  prfftw_gaussian_filter, METH_VARARGS,
     "Filter array with a gaussian distribution."},
	{"gaussian_fill",  prfftw_gaussian_fill, METH_VARARGS,
     "Fill array with gaussian distribution."},
	 {"lorentzftfill",  prfftw_lorentz_ft_fill, METH_VARARGS,
     "Fill array with lorentzian distribution, FT and wrapped."},
	{"rangereplace",  prfftw_rangereplace, METH_VARARGS,
     "Replace values outside and inside a range."},
	{"threshold",  prfftw_threshold, METH_VARARGS,
     "Threshold array."},
	{"cshio",  prfftw_cshio, METH_VARARGS,
     "CSHIO algorithm."},
	{"so2dmask", prfftw_so2d, METH_VARARGS, "SO2D algorithm."},
	{"hpr",  prfftw_hpr, METH_VARARGS,
     "HPR algorithm."},
	{"raar",  prfftw_raar, METH_VARARGS,
     "RAAR algorithm."},
	{"poermask",  prfftw_poermask, METH_VARARGS,
     "Phase-only error reduction algorithm with mask."},
	{"ermask",  prfftw_ermask, METH_VARARGS,
     "Error reduction algorithm with mask."},
	{"er",  prfftw_er, METH_VARARGS,
     "Error reduction algorithm."},
	{"pgchio",  prfftw_pgchio, METH_VARARGS,
     "Phase gradient constrained HIO algorithm."},
	{"pchio",  prfftw_pchio, METH_VARARGS,
     "Phase constrained HIO algorithm."},
	{"hioplus",  prfftw_hioplus, METH_VARARGS,
     "HIO algorithm with positivity constraint."},
    {"hiomask",  prfftw_hiomask, METH_VARARGS,
     "HIO algorithm with mask."},
	{"hio",  prfftw_hio, METH_VARARGS,
     "HIO algorithm without mask."},
	{"hiomaskpc",  prfftw_hiomaskpc, METH_VARARGS,
     "HIO algorithm with partial coherence optimisation."},
	 {"ermaskpc",  prfftw_ermaskpc, METH_VARARGS,
     "ER algorithm with partial coherence optimisation."},
	 {"hprmaskpc",  prfftw_hprmaskpc, METH_VARARGS,
     "HPR algorithm with partial coherence optimisation."},
	 {"raarmaskpc",  prfftw_raarmaskpc, METH_VARARGS,
     "RAAR algorithm with partial coherence optimisation."},
    {NULL, NULL, 0, NULL}
};


#if PY_MAJOR_VERSION >= 3
    static struct PyModuleDef prfftwmoddef = {
        PyModuleDef_HEAD_INIT,
        "prfftw",     /* m_name */
        "docs",  /* m_doc */
        -1,                  /* m_size */
        prfftwMethods,    /* m_methods */
        NULL,                /* m_reload */
        NULL,                /* m_traverse */
        NULL,                /* m_clear */
        NULL,                /* m_free */
    };
	PyMODINIT_FUNC PyInit_prfftw(void)
	{
		return PyModule_Create(&prfftwmoddef);
		import_array();
	}
#else
	PyMODINIT_FUNC initprfftw(void)
	{
		(void) Py_InitModule("prfftw", prfftwMethods);
		import_array();
	}
#endif


	
