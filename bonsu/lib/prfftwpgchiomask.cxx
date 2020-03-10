/*
#############################################
##   Filename: prfftwpgchiomask.cxx
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

void RS_PGCHIO
(
   double* seqdata,
   double* rho_m1,
   double* support,
   double* tmpdata,
   int32_t* nn,
   double beta,
   double phasemax,
   double phasemin,
   double qx,
   double qy,
   double qz
)
{
    int64_t i;
    int64_t ix1;
    int64_t iy1;
    int64_t iz1;
	int32_t ix, iy, iz;
	int32_t x1, y1, z1;
	if (qx > 0) {x1 = 1;} else {x1 = -1;}
	if (qy > 0) {y1 = 1;} else {y1 = -1;}
	if (qz > 0) {z1 = 1;} else {z1 = -1;}
	double phase, phaseq; /* in Q vector direction */
	
	CopyArray(seqdata, tmpdata, nn);
	for(iz=0; iz<nn[2]; iz++)
	{
		for(iy=0; iy<nn[1]; iy++)
		{
			for(ix=0; ix<nn[0]; ix++)
			{
				i=((iz)+(nn[2])*((iy)+(nn[1])*(ix)));
				ix1=((iz)+(nn[2])*((iy)+(nn[1])*(modclip(ix+x1, nn[0] - 1))));
				iy1=((iz)+(nn[2])*((modclip(iy+y1, nn[1] - 1))+(nn[1])*ix));
				iz1=((modclip(iz+z1, nn[2] - 1))+(nn[2])*((iy)+(nn[1])*(ix)));
				phase = atan2(tmpdata[2*i+1], tmpdata[2*i]);
				/* phase difference in direction of q*/
				phaseq  = fabs( qx * (phase - atan2(tmpdata[2*ix1+1], tmpdata[2*ix1]) ) +
								qy * (phase - atan2(tmpdata[2*iy1+1], tmpdata[2*iy1]) ) +
								qz * (phase - atan2(tmpdata[2*iz1+1], tmpdata[2*iz1]) ) );
				if ( support[2*i] < 1e-6 || phaseq > phasemax || phaseq < phasemin)
				{
					seqdata[2*i] = rho_m1[2*i] - beta*seqdata[2*i];
					seqdata[2*i+1] = rho_m1[2*i+1] - beta*seqdata[2*i+1];
				}

			}
		}
	}
}

void PGCHIO
(
	double* seqdata,
	double* expdata,
	double* support,
	double* mask,
	double* tmpdata,
	double beta,
	int startiter,
	int numiter,
	int ndim,
	double phasemax,
	double phasemin,
	double qx,
	double qy,
	double qz,
	double* rho_m1,
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

	fftw_plan torecip;
	fftw_plan toreal;
	int32_t iter;
	double sos = 0.0;
	double sos1 = 0.0;
	double sos2 = 0.0;
	double res = 0.0;
	double norm = 0.0;
	double qmag;

	int32_t update_count_real = 0;
	int32_t update_count_recip = 0;
	
	qmag = sqrt(qx*qx + qy*qy + qz*qz);
	qx = qx / qmag;
	qy = qy / qmag;
	qz = qz / qmag;

	CopyArray(seqdata, rho_m1, nn); 
	Py_BLOCK_THREADS;
	FFTPlan( &torecip, &toreal, seqdata, nn, ndim );
	Py_UNBLOCK_THREADS;
	CopyArray(rho_m1, seqdata, nn); 

	MaskedSumOfSquares( expdata, mask, nn, &sos );

	for( iter=startiter; iter < (numiter+startiter); iter++)
	{
		while( citer_flow[1] == 1 ) sleep(PRFFTW_PSLEEP);
		if( citer_flow[1] == 2 ) break; 
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
		MaskedSetAmplitudes(seqdata, expdata, mask, nn);
		FFTStride(seqdata, nn, &toreal);
		
		residual[iter] = (double) ( (double) res/sos);
		
		SumOfSquares( seqdata, nn, &sos1);
		RS_PGCHIO(seqdata, rho_m1, support, tmpdata, nn, beta, phasemax, phasemin, qx, qy, qz);
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

