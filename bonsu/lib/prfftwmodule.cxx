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
#define NPY_NO_DEPRECATED_API NPY_1_10_API_VERSION
#include <numpy/arrayobject.h> 
#include "prfftwmodule.h"




int wrap_array(double* indata, int32_t* nn, int drctn)
{
	int ii, i, j, k;
	int iish;
	int len = nn[0] * nn[1] * nn[2];
	int splt[3] = {0,0,0};
	double* data = (double*) malloc( 2*len * sizeof(double));
	if (!data)
	{
		free(data);
		return 1;
	}
	for(ii=0; ii<len; ii++)
	{
		data[2*ii] = indata[2*ii];
		data[2*ii+1] = indata[2*ii+1];
	}
	
	if( (nn[0] > 1) && (nn[0] % 2  > 0) && (drctn < 0) )
	{
		splt[0] = nn[0]/2 +1;
	}
	else
	{
		splt[0] = nn[0]/2;
	}
	if( (nn[1] > 1) && (nn[1] % 2  > 0) && (drctn < 0) )
	{
		splt[1] = nn[1]/2 +1;
	}
	else
	{
		splt[1] = nn[1]/2;
	}
	if( (nn[2] > 1) && (nn[2] % 2  > 0) && (drctn < 0) )
	{
		splt[2] = nn[2]/2 +1;
	}
	else
	{
		splt[2] = nn[2]/2;
	}
	/* 1 - 8 */
	for(i=0; i<splt[0]; i++)
	{
		for(j=0; j<splt[1]; j++)
		{
			for(k=0; k<splt[2]; k++)
			{
				ii = (k+nn[2]*(j+nn[1]*i));
				iish = ((nn[2] - splt[2] + k)+nn[2]*((nn[1] - splt[1] + j)+nn[1]*(nn[0] - splt[0] + i)));
				indata[2*iish] = data[2*ii];
				indata[2*iish+1] = data[2*ii+1];
			}
		}
	}
	/* 8 - 1 */
	for(i=splt[0]; i<(nn[0]); i++)
	{
		for(j=splt[1]; j<(nn[1]); j++)
		{
			for(k=splt[2]; k<(nn[2]); k++)
			{
				ii = (k+nn[2]*(j+nn[1]*i));
				iish = ((k - splt[2])+nn[2]*((j - splt[1])+nn[1]*(i - splt[0])));
				indata[2*iish] = data[2*ii];
				indata[2*iish+1] = data[2*ii+1];
			}
		}
	}
	/* 2 - 7 */
	for(i=splt[0]; i<(nn[0]); i++)
	{
		for(j=0; j<(splt[1]); j++)
		{
			for(k=0; k<(splt[2]); k++)
			{
				ii = (k+nn[2]*(j+nn[1]*i));
				iish = ((nn[2] - splt[2] + k)+nn[2]*((nn[1] - splt[1] + j)+nn[1]*(i - splt[0])));
				indata[2*iish] = data[2*ii];
				indata[2*iish+1] = data[2*ii+1];
			}
		}
	}
	/* 7 - 2 */
	for(i=0; i<(splt[0]); i++)
	{
		for(j=splt[1]; j<(nn[1]); j++)
		{
			for(k=splt[2]; k<(nn[2]); k++)
			{
				ii = (k+nn[2]*(j+nn[1]*i));
				iish = ((k - splt[2])+nn[2]*((j - splt[1])+nn[1]*(nn[0] - splt[0] + i)));
				indata[2*iish] = data[2*ii];
				indata[2*iish+1] = data[2*ii+1];
			}
		}
	}
	/* 3 - 6 */
	for(i=0; i<(splt[0]); i++)
	{
		for(j=splt[1]; j<(nn[1]); j++)
		{
			for(k=0; k<(splt[2]); k++)
			{
				ii = (k+nn[2]*(j+nn[1]*i));
				iish = ((nn[2] - splt[2] + k)+nn[2]*((j - splt[1])+nn[1]*(nn[0] - splt[0] + i)));
				indata[2*iish] = data[2*ii];
				indata[2*iish+1] = data[2*ii+1];
			}
		}
	}
	/* 6 - 3 */
	for(i=splt[0]; i<(nn[0]); i++)
	{
		for(j=0; j<(splt[1]); j++)
		{
			for(k=splt[2]; k<(nn[2]); k++)
			{
				ii = (k+nn[2]*(j+nn[1]*i));
				iish = ((k - splt[2])+nn[2]*((nn[1] - splt[1] + j)+nn[1]*(i - splt[0])));
				indata[2*iish] = data[2*ii];
				indata[2*iish+1] = data[2*ii+1];
			}
		}
	}
	/* 4 - 5 */
	for(i=splt[0]; i<(nn[0]); i++)
	{
		for(j=splt[1]; j<(nn[1]); j++)
		{
			for(k=0; k<(splt[2]); k++)
			{
				ii = (k+nn[2]*(j+nn[1]*i));
				iish = ((nn[2] - splt[2] + k)+nn[2]*((j - splt[1])+nn[1]*(i - splt[0])));
				indata[2*iish] = data[2*ii];
				indata[2*iish+1] = data[2*ii+1];
			}
		}
	}
	/* 5 - 4 */
	for(i=0; i<(splt[0]); i++)
	{
		for(j=0; j<(splt[1]); j++)
		{
			for(k=splt[2]; k<(nn[2]); k++)
			{
				ii = (k+nn[2]*(j+nn[1]*i));
				iish = ((k - splt[2])+nn[2]*((nn[1] - splt[1] + j)+nn[1]*(nn[0] - splt[0] + i)));
				indata[2*iish] = data[2*ii];
				indata[2*iish+1] = data[2*ii+1];
			}
		}
	}
	free(data);
	return 0;
}

PyObject* prfftw_wrap(PyObject *self, PyObject *args)
{
	double *indata;
	npy_intp *dims;
	int32_t nn[3];
	PyArrayObject *arg1=NULL;
	int drctn;
	if (!PyArg_ParseTuple(args, "Oi", &arg1, &drctn)) return NULL;
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
        return NULL;
	
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
        return NULL;
	
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
        return NULL;
	
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
        return NULL;
	
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
        return NULL;
	
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
        return NULL;
	
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
        return NULL;
	
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
        return NULL;
	
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
        return NULL;
	
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
        return NULL;
	
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
        return NULL;
	
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
	PyArrayObject *arg1=NULL, *arg2=NULL, *arg3=NULL, *arg4=NULL;
	double gammaHWHM; int gammaRS, numiterRL, startiterRL, waititerRL;
	int zex, zey, zez;
	double beta; int startiter, numiter, ndim;
	PyArrayObject *psf=NULL;
	PyArrayObject *arg9=NULL, *arg10=NULL, *arg11=NULL, *arg12=NULL;
	PyArrayObject *arg13=NULL, *arg14=NULL, *arg15=NULL, *arg16=NULL, *arg17=NULL;
	PyObject *updatereal, *updaterecip, *updatelog, *updatelog2;
	int accel;

    if (!PyArg_ParseTuple(args, "OOOOdiiiiiiidiiiOOOOOOOOOOOOOOi",
		&arg1, &arg2, &arg3, &arg4,
		&gammaHWHM, &gammaRS, &numiterRL, &startiterRL, &waititerRL,
		&zex, &zey, &zez,
		&beta, &startiter, &numiter, &ndim,
		&arg9, &psf, &arg10, &arg11, &arg12, &arg13, &arg14, &arg15, &arg16,
		&arg17, &updatereal, &updaterecip, &updatelog, &updatelog2, &accel))
        return NULL;
	
	double *seqdata = (double*) PyArray_DATA(arg1);
	double *expdata = (double*) PyArray_DATA(arg2);
	double *support = (double*) PyArray_DATA(arg3);
	double *mask = (double*) PyArray_DATA(arg4);
	
	double *rho_m1 = (double*) PyArray_DATA(arg9);
	double *pca_gamma_ft = (double*) PyArray_DATA(psf);
	int32_t *nn = (int32_t*) PyArray_DATA(arg10);
	double *residual = (double*) PyArray_DATA(arg11);
	double *residualRL = (double*) PyArray_DATA(arg12);
	int32_t *citer_flow = (int32_t*) PyArray_DATA(arg13);
	
	double *visual_amp_real = (double*) PyArray_DATA(arg14);
	double *visual_phase_real = (double*) PyArray_DATA(arg15);
	double *visual_amp_recip = (double*) PyArray_DATA(arg16);
	double *visual_phase_recip = (double*) PyArray_DATA(arg17);
	
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
	
	HIOMaskPC(seqdata, expdata, support, mask,
					gammaHWHM, gammaRS, numiterRL, startiterRL, waititerRL,
					zex, zey, zez,
					beta, startiter, numiter, ndim, 
					rho_m1, pca_gamma_ft, nn, residual, residualRL, citer_flow,
					visual_amp_real, visual_phase_real, visual_amp_recip, visual_phase_recip,
					updatereal, updaterecip, updatelog, updatelog2, accel);

	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* prfftw_ermaskpc(PyObject *self, PyObject *args)
{
	PyArrayObject *arg1=NULL, *arg2=NULL, *arg3=NULL, *arg4=NULL;
	double gammaHWHM; int gammaRS, numiterRL, startiterRL, waititerRL;
	int zex, zey, zez;
	int startiter, numiter, ndim;
	PyArrayObject *psf=NULL;
	PyArrayObject *arg9=NULL, *arg10=NULL, *arg11=NULL, *arg12=NULL;
	PyArrayObject *arg13=NULL, *arg14=NULL, *arg15=NULL, *arg16=NULL, *arg17=NULL;
	PyObject *updatereal, *updaterecip, *updatelog, *updatelog2;
	int accel;

    if (!PyArg_ParseTuple(args, "OOOOdiiiiiiiiiiOOOOOOOOOOOOOOi",
		&arg1, &arg2, &arg3, &arg4,
		&gammaHWHM, &gammaRS, &numiterRL, &startiterRL, &waititerRL,
		&zex, &zey, &zez,
		&startiter, &numiter, &ndim,
		&arg9, &psf, &arg10, &arg11, &arg12, &arg13, &arg14, &arg15, &arg16,
		&arg17, &updatereal, &updaterecip, &updatelog, &updatelog2, &accel))
        return NULL;
	
	double *seqdata = (double*) PyArray_DATA(arg1);
	double *expdata = (double*) PyArray_DATA(arg2);
	double *support = (double*) PyArray_DATA(arg3);
	double *mask = (double*) PyArray_DATA(arg4);
	
	double *rho_m1 = (double*) PyArray_DATA(arg9);
	double *pca_gamma_ft = (double*) PyArray_DATA(psf);
	int32_t *nn = (int32_t*) PyArray_DATA(arg10);
	double *residual = (double*) PyArray_DATA(arg11);
	double *residualRL = (double*) PyArray_DATA(arg12);
	int32_t *citer_flow = (int32_t*) PyArray_DATA(arg13);
	
	double *visual_amp_real = (double*) PyArray_DATA(arg14);
	double *visual_phase_real = (double*) PyArray_DATA(arg15);
	double *visual_amp_recip = (double*) PyArray_DATA(arg16);
	double *visual_phase_recip = (double*) PyArray_DATA(arg17);
	
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
	
	ERMaskPC(seqdata, expdata, support, mask,
					gammaHWHM, gammaRS, numiterRL, startiterRL, waititerRL,
					zex, zey, zez,
					startiter, numiter, ndim, 
					rho_m1, pca_gamma_ft, nn, residual, residualRL, citer_flow,
					visual_amp_real, visual_phase_real, visual_amp_recip, visual_phase_recip,
					updatereal, updaterecip, updatelog, updatelog2, accel);

	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* prfftw_hprmaskpc(PyObject *self, PyObject *args)
{
	PyArrayObject *arg1=NULL, *arg2=NULL, *arg3=NULL, *arg4=NULL;
	double gammaHWHM; int gammaRS, numiterRL, startiterRL, waititerRL;
	int zex, zey, zez;
	double beta; int startiter, numiter, ndim;
	PyArrayObject *psf=NULL;
	PyArrayObject *arg9=NULL, *arg10=NULL, *arg11=NULL, *arg12=NULL;
	PyArrayObject *arg13=NULL, *arg14=NULL, *arg15=NULL, *arg16=NULL, *arg17=NULL;
	PyObject *updatereal, *updaterecip, *updatelog, *updatelog2;
	int accel;

    if (!PyArg_ParseTuple(args, "OOOOdiiiiiiidiiiOOOOOOOOOOOOOOi",
		&arg1, &arg2, &arg3, &arg4,
		&gammaHWHM, &gammaRS, &numiterRL, &startiterRL, &waititerRL,
		&zex, &zey, &zez,
		&beta, &startiter, &numiter, &ndim,
		&arg9, &psf, &arg10, &arg11, &arg12, &arg13, &arg14, &arg15, &arg16,
		&arg17, &updatereal, &updaterecip, &updatelog, &updatelog2, &accel))
        return NULL;
	
	double *seqdata = (double*) PyArray_DATA(arg1);
	double *expdata = (double*) PyArray_DATA(arg2);
	double *support = (double*) PyArray_DATA(arg3);
	double *mask = (double*) PyArray_DATA(arg4);
	
	double *rho_m1 = (double*) PyArray_DATA(arg9);
	double *pca_gamma_ft = (double*) PyArray_DATA(psf);
	int32_t *nn = (int32_t*) PyArray_DATA(arg10);
	double *residual = (double*) PyArray_DATA(arg11);
	double *residualRL = (double*) PyArray_DATA(arg12);
	int32_t *citer_flow = (int32_t*) PyArray_DATA(arg13);
	
	double *visual_amp_real = (double*) PyArray_DATA(arg14);
	double *visual_phase_real = (double*) PyArray_DATA(arg15);
	double *visual_amp_recip = (double*) PyArray_DATA(arg16);
	double *visual_phase_recip = (double*) PyArray_DATA(arg17);
	
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
	
	HPRMaskPC(seqdata, expdata, support, mask,
					gammaHWHM, gammaRS, numiterRL, startiterRL, waititerRL,
					zex, zey, zez,
					beta, startiter, numiter, ndim, 
					rho_m1, pca_gamma_ft, nn, residual, residualRL, citer_flow,
					visual_amp_real, visual_phase_real, visual_amp_recip, visual_phase_recip,
					updatereal, updaterecip, updatelog, updatelog2, accel);

	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* prfftw_raarmaskpc(PyObject *self, PyObject *args)
{
	PyArrayObject *arg1=NULL, *arg2=NULL, *arg3=NULL, *arg4=NULL;
	double gammaHWHM; int gammaRS, numiterRL, startiterRL, waititerRL;
	int zex, zey, zez;
	double beta; int startiter, numiter, ndim;
	PyArrayObject *psf=NULL;
	PyArrayObject *arg9=NULL, *arg10=NULL, *arg11=NULL, *arg12=NULL;
	PyArrayObject *arg13=NULL, *arg14=NULL, *arg15=NULL, *arg16=NULL, *arg17=NULL;
	PyObject *updatereal, *updaterecip, *updatelog, *updatelog2;
	int accel;

    if (!PyArg_ParseTuple(args, "OOOOdiiiiiiidiiiOOOOOOOOOOOOOOi",
		&arg1, &arg2, &arg3, &arg4,
		&gammaHWHM, &gammaRS, &numiterRL, &startiterRL, &waititerRL,
		&zex, &zey, &zez,
		&beta, &startiter, &numiter, &ndim,
		&arg9, &psf, &arg10, &arg11, &arg12, &arg13, &arg14, &arg15, &arg16,
		&arg17, &updatereal, &updaterecip, &updatelog, &updatelog2, &accel))
        return NULL;
	
	double *seqdata = (double*) PyArray_DATA(arg1);
	double *expdata = (double*) PyArray_DATA(arg2);
	double *support = (double*) PyArray_DATA(arg3);
	double *mask = (double*) PyArray_DATA(arg4);
	
	double *rho_m1 = (double*) PyArray_DATA(arg9);
	double *pca_gamma_ft = (double*) PyArray_DATA(psf);
	int32_t *nn = (int32_t*) PyArray_DATA(arg10);
	double *residual = (double*) PyArray_DATA(arg11);
	double *residualRL = (double*) PyArray_DATA(arg12);
	int32_t *citer_flow = (int32_t*) PyArray_DATA(arg13);
	
	double *visual_amp_real = (double*) PyArray_DATA(arg14);
	double *visual_phase_real = (double*) PyArray_DATA(arg15);
	double *visual_amp_recip = (double*) PyArray_DATA(arg16);
	double *visual_phase_recip = (double*) PyArray_DATA(arg17);
	
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
	
	RAARMaskPC(seqdata, expdata, support, mask,
					gammaHWHM, gammaRS, numiterRL, startiterRL, waititerRL,
					zex, zey, zez,
					beta, startiter, numiter, ndim, 
					rho_m1, pca_gamma_ft, nn, residual, residualRL, citer_flow,
					visual_amp_real, visual_phase_real, visual_amp_recip, visual_phase_recip,
					updatereal, updaterecip, updatelog, updatelog2, accel);

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
        return NULL;
	
	
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
        return NULL;
	
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
	int32_t ndim;
	int32_t nn[3];
	double gammaHWHM;
    if (!PyArg_ParseTuple(args, "Od", &arg1, &gammaHWHM)) return NULL;
	indata = (double*) PyArray_DATA(arg1);
	dims = PyArray_DIMS(arg1);
	ndim = PyArray_NDIM(arg1);
	nn[0] = (int32_t) dims[0]; nn[1] = (int32_t) dims[1]; nn[2] = (int32_t) dims[2];
	lorentz_ft_fill(indata, nn, gammaHWHM);
	Py_INCREF(Py_None);
	return Py_None;
}


PyObject* prfftw_gaussian_fill(PyObject *self, PyObject *args)
{
	PyArrayObject *arg1=NULL;
	double sigma;
    if (!PyArg_ParseTuple(args, "Od", &arg1, &sigma)) return NULL;
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
	if (!PyArg_ParseTuple(args, "OOd", &arg1, &arg2, &sigma)) return NULL;
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
	if (!PyArg_ParseTuple(args, "OO", &arg1, &arg2)) return NULL;
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
	if (!PyArg_ParseTuple(args, "OO", &arg1, &arg2)) return NULL;
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
	if (!PyArg_ParseTuple(args, "Oi", &arg1, &space)) return NULL;
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

void conj_reflect(double* data, int32_t* nn)
{
	int ii, iir, i, j, k;
	double val1[2] = {0.0,0.0};
	double val2[2] = {0.0,0.0};
	for(i=0; i<(nn[0]/2); i++)
	{
		for(j=0; j<nn[1]; j++)
		{
			for(k=0; k<nn[2]; k++)
			{
				ii = (k+nn[2]*(j+nn[1]*i));
				iir = ((nn[2] - k - 1)+nn[2]*((nn[1] - j - 1)+nn[1]*(nn[0] - i - 1)));
				val1[0] = data[2*ii];
				val1[1] = data[2*ii+1];
				val2[0] = data[2*iir];
				val2[1] = data[2*iir+1];
				data[2*ii] = val2[0];
				data[2*ii+1] = -val2[1];
				data[2*iir] = val1[0];
				data[2*iir+1] = -val1[1];
			}
		}
	}
	if ((nn[0] % 2)==1)
	{
		i=(nn[0]/2);
		for(j=0; j<(nn[1]/2); j++)
		{
			for(k=0; k<nn[2]; k++)
			{
				ii = (k+nn[2]*(j+nn[1]*i));
				iir = ((nn[2] - k - 1)+nn[2]*((nn[1] - j - 1)+nn[1]*(nn[0] - i - 1)));
				val1[0] = data[2*ii];
				val1[1] = data[2*ii+1];
				val2[0] = data[2*iir];
				val2[1] = data[2*iir+1];
				data[2*ii] = val2[0];
				data[2*ii+1] = -val2[1];
				data[2*iir] = val1[0];
				data[2*iir+1] = -val1[1];
			}
		}
	}
	if ((nn[0] % 2)==1 && (nn[1] % 2)==1)
	{
		i=(nn[0]/2);
		j=(nn[1]/2);
		{
			for(k=0; k<(nn[2]/2); k++)
			{
				ii = (k+nn[2]*(j+nn[1]*i));
				iir = ((nn[2] - k - 1)+nn[2]*((nn[1] - j - 1)+nn[1]*(nn[0] - i - 1)));
				val1[0] = data[2*ii];
				val1[1] = data[2*ii+1];
				val2[0] = data[2*iir];
				val2[1] = data[2*iir+1];
				data[2*ii] = val2[0];
				data[2*ii+1] = -val2[1];
				data[2*iir] = val1[0];
				data[2*iir+1] = -val1[1];
			}
		}
	}
	if ((nn[0] % 2)==1 && (nn[1] % 2)==1 && (nn[2] % 2)==1)
	{
		i=(nn[0]/2);
		j=(nn[1]/2);
		k=(nn[2]/2);
		ii = (k+nn[2]*(j+nn[1]*i));
		data[2*ii+1] = -data[2*ii+1];
	}
}

PyObject* prfftw_conj_reflect(PyObject *self, PyObject *args)
{
	PyArrayObject *arg1=NULL;
	double *indata;
	npy_intp *dims;
	int32_t nn[3];
	if (!PyArg_ParseTuple(args, "O", &arg1)) return NULL;
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
	if (!PyArg_ParseTuple(args, "OOiiid", &arg1, &arg2, &kx, &ky, &kz, &maxerr)) return NULL;
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
	if (!PyArg_ParseTuple(args, "OOiiiiiiiii", &arg1, &arg2, &kx, &ky, &kz, &x1, &x2, &y1, &y2, &z1, &z2)) return NULL;
	data1 = (double*) PyArray_DATA(arg1);
	data2 = (double*) PyArray_DATA(arg2);
	dims = PyArray_DIMS(arg1);
	nn[0] = (int32_t) dims[0]; nn[1] = (int32_t) dims[1]; nn[2] = (int32_t) dims[2];
	BlankLineReplace(data1, data2, nn, kx, ky, kz, x1, x2, y1, y2, z1, z2);
	Py_INCREF(Py_None);
	return Py_None;
}




static PyMethodDef prfftwMethods[] = {
	{"fft",  prfftw_fft, METH_VARARGS,
     "Fourier transform a complex array."},
	 {"wrap",  prfftw_wrap, METH_VARARGS,
     "Wrap array."},
	 {"medianfilter",  prfftw_medianfilter, METH_VARARGS,
     "Median filter array."},
	 {"blanklinefill",  prfftw_blanklinereplace, METH_VARARGS,
     "Fill blank voxels with non-zero average value."},
	{"conj_reflect",  prfftw_conj_reflect, METH_VARARGS,
     "Reflect and conjugate a complex array."},
	 {"convolve",  prfftw_convolve, METH_VARARGS,
     "Convolve two complex arrays."},
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

PyMODINIT_FUNC
initprfftw(void)
{
    (void) Py_InitModule("prfftw", prfftwMethods);
	import_array();
}

