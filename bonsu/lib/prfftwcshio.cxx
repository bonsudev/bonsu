/*
#############################################
##   Filename: prfftwcshio.cxx
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


#define NO_IMPORT_ARRAY
#define PY_ARRAY_UNIQUE_SYMBOL prfftw_ARRAY_API
#include <Python.h>
#include "prfftwmodule.h"

void CSHIO
(
	double* seqdata,
	double* expdata,
	double* support,
	double* mask,
	double beta,
	int startiter,
	int numiter,
	int ndim,
	double cs_p,
	double* epsilon,
	double cs_d,
	double cs_eta,
	int32_t relax,
	double* rho_m1,
	double* rho_m2,
	double* elp,
	int32_t* nn,
	double* residual,
	int32_t* citer_flow,
	double* visual_amp_real,
	double* visual_phase_real,
	double* visual_amp_recip,
	double* visual_phase_recip,
	PyObject* updatereal,
	PyObject* updaterecip,
	PyObject* updatelog
)
{
	Py_BEGIN_ALLOW_THREADS;

	fftw_init_threads();
	fftw_plan_with_nthreads(citer_flow[7]);
	
	npthread = citer_flow[7];

	fftw_plan torecip;
	fftw_plan toreal;
	int32_t iter;
	double sos = 0.0;
	double sos1 = 0.0;
	double sos2 = 0.0;
	double res = 0.0;
	double norm = 0.0;

	int32_t update_count_real = 0;
	int32_t update_count_recip = 0;

	double norm2_n = 0.0;
	double norm2_n_m1 = 0.0;

	double setampres = 1.0;

	CopyArray(seqdata, rho_m1, nn); 
	Py_BLOCK_THREADS;
	FFTPlan( &torecip, &toreal, seqdata, nn, ndim );
	Py_UNBLOCK_THREADS;
	CopyArray(rho_m1, seqdata, nn); 

	MaskedSumOfSquares( expdata, mask, nn, &sos );

	
	ConstantArray(rho_m1, nn, 1.0, 0.0);

	for( iter=startiter; iter < (numiter+startiter); iter++)
	{
		while( citer_flow[1] == 1 ) sleep(PRFFTW_PSLEEP);
		if( citer_flow[1] == 2 ) break; 
		
		CopyArray( rho_m1, rho_m2, nn );
		Norm2array( seqdata, nn,  &norm2_n);
		Norm2array( rho_m1, nn,  &norm2_n_m1);
		if( fabs(norm2_n-norm2_n_m1) < sqrt(epsilon[0])/cs_eta && epsilon[0] > epsilon[1])
		{
			epsilon[0]  = epsilon[0] / cs_d;
			
		}
		
		CopyArray( seqdata, rho_m1, nn );
		
		FFTStride(seqdata, nn, &torecip);
		
		if( citer_flow[5] > 0 && update_count_recip == citer_flow[5] ) 
		{
			CopyAmp( seqdata, visual_amp_recip, nn );
			if( citer_flow[6] > 0 ) CopyPhase( seqdata, visual_phase_recip, nn );
			update_count_recip = 0;
			Py_BLOCK_THREADS;
			PyObject_CallObject(updaterecip, NULL);
			Py_UNBLOCK_THREADS;
		}
		else
		{
			update_count_recip += 1;
		}
		MaskedCalculateResiduals(seqdata, expdata, mask, nn, &res);
		MaskedSetAmplitudesRelaxed(seqdata, expdata, mask, setampres, relax, nn);
		FFTStride(seqdata, nn, &toreal);
		
		residual[iter] = (double) ( (double) res/sos);
		setampres = residual[iter];
		
		SumOfSquares( seqdata, nn, &sos1);
		
		Calculate_Delp(rho_m1, rho_m2, elp, nn, cs_p, epsilon[0] );
		SubtractArray(seqdata, elp, seqdata, nn);
		
		RS_HIO(seqdata, rho_m1, support, nn, beta );
		SumOfSquares( seqdata, nn, &sos2 );
		norm = sqrt( (double) sos1/sos2 );
		ScaleArray( seqdata, nn, norm );
		
		if( citer_flow[3] > 0 && update_count_real == citer_flow[3] ) 
		{
			CopyAmp( seqdata, visual_amp_real, nn );
			if( citer_flow[6] > 0 ) CopyPhase( seqdata, visual_phase_real, nn );
			update_count_real = 0;
			Py_BLOCK_THREADS;
			PyObject_CallObject(updatereal, NULL);
			Py_UNBLOCK_THREADS;
		}
		else
		{
			update_count_real += 1;
		}
		
		Py_BLOCK_THREADS;
		PyObject_CallObject(updatelog, NULL);
		Py_UNBLOCK_THREADS;
		
		citer_flow[0] += 1;
	}

	fftw_destroy_plan( torecip );
	fftw_destroy_plan( toreal );

	fftw_cleanup_threads();

	Py_END_ALLOW_THREADS;
}

