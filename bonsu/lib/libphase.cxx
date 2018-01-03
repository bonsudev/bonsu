/*
#############################################
##   Filename: libphase.cxx
##
##    Copyright (C) 2011 Marcus C. Newton
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
#include "prfftwmodule.h"

void SqrtArray
(
	double* data,
	int32_t* nn
)
{
	int64_t len = (int64_t) nn[0] * nn[1] * nn[2];
	int64_t i;
	double theta;
	double amp;
	for(i=0; i<len; i++)
	{
		theta = 0.5 * atan2(data[2*i+1], data[2*i]);
		amp = sqrt(
		data[2*i] * data[2*i] +
		data[2*i+1] * data[2*i+1] );
		amp = sqrt(amp);
		data[2*i  ] = amp * cos(theta);
		data[2*i+1] = amp * sin(theta);
	}
}

void CopyArray
(
	double* data1, 
	double* data2, 
	int32_t* nn
)
{
	int64_t len = (int64_t) nn[0] * nn[1] * nn[2];
	int64_t i;
	for(i=0; i<len; i++)
	{
		data2[2*i] = data1[2*i];
		data2[2*i+1] = data1[2*i+1];
	}
}

void CopyRealArray
(
	double* data1, 
	double* data2, 
	int32_t* nn
)
{
	int64_t len = (int64_t) nn[0] * nn[1] * nn[2];
	int64_t i;
	for(i=0; i<len; i++)
	{
		data2[i] = data1[i];
	}
}

void SubtractArray
(
	double* data0, 
	double* data1, 
	double* data2, 
	int32_t* nn
)
{
	int64_t len = (int64_t) nn[0] * nn[1] * nn[2];
	int64_t i;
	for(i=0; i<len; i++)
	{
		data2[2*i] = data0[2*i] - data1[2*i];
		data2[2*i+1] = data0[2*i+1] - data1[2*i+1];
	}
}

void AddArray
(
	double* data0, 
	double* data1, 
	double* data2, 
	int32_t* nn
)
{
	int64_t len = (int64_t) nn[0] * nn[1] * nn[2];
	int64_t i;
	for(i=0; i<len; i++)
	{
		data2[2*i] = data0[2*i] + data1[2*i];
		data2[2*i+1] = data0[2*i+1] + data1[2*i+1];
	}
}


void MultiplyArray
(
	double* data0, 
	double* data1, 
	double* data2, 
	int32_t* nn
)
{
	int64_t len = (int64_t) nn[0] * nn[1] * nn[2];
	int64_t i;
	double val1[2] = {0.0,0.0};
	double val2[2] = {0.0,0.0};
	for(i=0; i<len; i++)
	{
		val1[0] = data0[2*i];
		val1[1] = data0[2*i+1];
		val2[0] = data1[2*i];
		val2[1] = data1[2*i+1];
		data2[2*i] = (val1[0]*val2[0] - val1[1]*val2[1]);
		data2[2*i+1] =(val1[1]*val2[0] + val1[0]*val2[1]);
	}
}

void CopyAmp
(
	double* data1, 
	double* data2, 
	int32_t* nn
)
{
	int64_t len = (int64_t) nn[0] * nn[1] * nn[2];
	int64_t i;
	for(i=0; i<len; i++)
	{
		data2[i] = sqrt(data1[2*i]*data1[2*i] + data1[2*i+1]*data1[2*i+1]);
	}
}

void CopyPhase
(
	double* data1, 
	double* data2, 
	int32_t* nn
)
{
	int64_t len = (int64_t) nn[0] * nn[1] * nn[2];
	int64_t i;
	for(i=0; i<len; i++)
	{
		data2[i] = atan2(data1[2*i+1], data1[2*i]);
	}
}

void ZeroArray
(
    double* data,
    int32_t* nn
)
{
    int64_t len =  (int64_t) nn[0] * nn[1] * nn[2];
	int64_t i;
	for(i=0; i<len; i++)
	{
		data[2*i] = 0.0;
		data[2*i+1] = 0.0;
	}
}

void ScaleArray
(
    double* data,
    int32_t* nn,
    double factor
)
{
    int64_t len =  (int64_t) nn[0] * nn[1] * nn[2];
	int64_t i;
	for(i=0; i<len; i++)
	{
		data[2*i] *= factor;
		data[2*i+1] *= factor;
	}
}

void ExponentArray
(
    double* data,
    int32_t* nn,
    int factor
)
{
    if (factor > 1)
	{
		int64_t len =  (int64_t) nn[0] * nn[1] * nn[2];
		int64_t i;
		double amp, phase;
		for(i=0; i<len; i++)
		{
			amp = sqrt(data[2*i]*data[2*i]+data[2*i+1]*data[2*i+1]);
			phase = atan2(data[2*i+1], data[2*i]);
			data[2*i] = amp*cos(((double) factor)*phase);
			data[2*i+1] = amp*sin(((double) factor)*phase);
		}
	}
}

void ConstantArray
(
    double* data,
    int32_t* nn,
    double real,
    double imag
)
{
    int64_t len =  (int64_t) nn[0] * nn[1] * nn[2];
	int64_t i;
	for(i=0; i<len; i++)
	{
		data[2*i] = real;
		data[2*i+1] = imag;
	}
}

void Norm2array
(
	double* data,
	int32_t* nn,
	double* norm2
)
{
	*norm2 = 0.0;
	int64_t len = (int64_t) nn[0] * nn[1] * nn[2];
	int64_t i;
	for(i=0; i<len; i++)
	{
		*norm2 += data[2*i]*data[2*i] + data[2*i+1]*data[2*i+1];
	}
	*norm2 = sqrt( *norm2 );
}

void FFTPlan
(
	fftw_plan* torecip,
	fftw_plan* toreal,
	double* data,
	int32_t* nn,
	int32_t ndim
)
{
	*torecip = fftw_plan_dft(ndim, (int32_t*) nn,
	(fftw_complex*) data, (fftw_complex*) data, +1, FFTW_MEASURE);	
	*toreal = fftw_plan_dft(ndim, (int32_t*) nn,
	(fftw_complex*) data, (fftw_complex*) data, -1, FFTW_MEASURE);
	if (torecip == NULL || toreal == NULL)
	{
	printf("FFTWPlan: could not create plan");
	}
}

void FFTStride
(
	double* data,
	int32_t* nn,
	fftw_plan* plan
)
{
	double inv_sqrt_n;
	int64_t i;
	int64_t len = (int64_t) nn[0] * nn[1] * nn[2];
	fftw_execute_dft( *plan, (fftw_complex*) data, (fftw_complex*) data );
	inv_sqrt_n = 1.0 / sqrt((double) len);
	for(i=0; i<len; i++)
	{
		data[2*i] *= inv_sqrt_n;
		data[2*i+1] *= inv_sqrt_n;
	}
}

void SumArray
(
	double* data,
	int32_t* nn,
	double* sum
)
{
	int len = nn[0] * nn[1] * nn[2];
	int i;
	*sum = 0.0;
	for(i=0; i<len; i++)
	{
		*sum += sqrt( data[2*i]*data[2*i] + data[2*i+1]*data[2*i+1] );
	}
}

void SumOfSquares
(
	double* data,
	int32_t* nn,
	double* sos
)
{
	int64_t len = (int64_t) nn[0] * nn[1] * nn[2];
	int64_t i; 
	*sos = 0.0;
	for(i=0; i<len; i++)
	{
		*sos += data[2*i] * data[2*i] + data[2*i+1] * data[2*i+1] ;
	}
}

void MaskedSumOfSquares
(
	double* data,
	double* mask,
	int32_t* nn,
	double* sos
)
{
	int64_t len =  (int64_t) nn[0] * nn[1] * nn[2];
	int64_t i; 
	double amp_mask;
	*sos = 0.0;
	for(i=0; i<len; i++)
	{
		amp_mask = mask[2*i] * mask[2*i] + mask[2*i+1] * mask[2*i+1];
		*sos += (data[2*i] * data[2*i] + data[2*i+1] * data[2*i+1])*amp_mask;
	}
}

void CalculateResiduals
(
	double* seqdata,
	double* expdata,
	int32_t* nn,
	double* sos
)
{
	int64_t len = (int64_t) nn[0] * nn[1] * nn[2];
	int64_t i;
	double amp1, amp2;
	*sos = 0.0;
	for(i=0; i<len; i++)
	{
		amp1 = sqrt(
		seqdata[2*i] * seqdata[2*i] +
		seqdata[2*i+1] * seqdata[2*i+1] );
		amp2 = sqrt(
		expdata[2*i] * expdata[2*i] +
		expdata[2*i+1] * expdata[2*i+1] );
		
	*sos += ( amp1 - amp2 ) * ( amp1 - amp2 );
	}
}

void MaskedCalculateResiduals
(
	double* seqdata,
	double* expdata,
	double* mask,
	int32_t* nn,
	double* sos
)
{
	int64_t len = (int64_t) nn[0] * nn[1] * nn[2];
	int64_t i;
	double amp1, amp2;
	*sos = 0.0;
	for(i=0; i<len; i++)
	{
		amp1 = sqrt(
		seqdata[2*i] * seqdata[2*i] +
		seqdata[2*i+1] * seqdata[2*i+1] );
		amp2 = sqrt(
		expdata[2*i] * expdata[2*i] +
		expdata[2*i+1] * expdata[2*i+1] );
		
	*sos += ( amp1 - amp2 ) * ( amp1 - amp2 ) * mask[2*i];
	}
}

void MaskedSetAmplitudes
(
	double* seqdata,
	double* expdata,
	double* mask,
	int32_t* nn
)
{
	int64_t len = (int64_t) nn[0] * nn[1] * nn[2];
	int64_t i;
	double amp, phase;
	for(i=0; i<len; i++)
	{
		if (mask[2*i] > 1e-6)
		{
			amp = sqrt( expdata[2*i]*expdata[2*i] +
						expdata[2*i+1]*expdata[2*i+1]);

			phase = atan2(seqdata[2*i+1], seqdata[2*i]);
			seqdata[2*i] = amp*cos(phase);
			seqdata[2*i+1] = amp*sin(phase);
		}
	}
}

void SetAmplitudes
(
	double* seqdata,
	double* expdata,
	int32_t* nn
)
{
	int64_t len =  nn[0] * nn[1] * nn[2];
	int64_t i;
	double amp, phase;
	for(i=0; i<len; i++)
	{
		amp = sqrt( expdata[2*i]*expdata[2*i] +
					expdata[2*i+1]*expdata[2*i+1]);

		phase = atan2(seqdata[2*i+1], seqdata[2*i]);
		seqdata[2*i] = amp*cos(phase);
		seqdata[2*i+1] = amp*sin(phase);
	}
}

void Calculate_Delp
(
	double* rho_m1,
	double* rho_m2,
	double* elp,
	int32_t* nn,
	double p,
	double epsilon
)
{
	int64_t len =  nn[0] * nn[1] * nn[2];
	int64_t i;
	double amp1, amp1_sqrt, amp2, i_wgt;
	double gamma, gamma_pm2;
	for(i=0; i<len; i++)
	{
		amp1 = rho_m1[2*i]*rho_m1[2*i] + rho_m1[2*i+1]*rho_m1[2*i+1];
		amp2 = rho_m2[2*i]*rho_m2[2*i] + rho_m2[2*i+1]*rho_m2[2*i+1];
		amp1_sqrt = sqrt( amp1 );
		i_wgt =  1.0 / sqrt( amp2+epsilon );
		gamma = i_wgt*amp1 - amp1_sqrt;
		gamma_pm2 = pow( fabs(gamma), (p - 2.0) );
		elp[2*i] = 0.5*fabs(p)*gamma*gamma_pm2*( 2.0*i_wgt*rho_m1[2*i] - (rho_m1[2*i] / amp1_sqrt) );
		elp[2*i+1] = 0.5*fabs(p)*gamma*gamma_pm2*( 2.0*i_wgt*rho_m1[2*i+1] - (rho_m1[2*i+1] / amp1_sqrt) );
	}	
}

void MaskedSetAmplitudesRelaxed
(
	double* seqdata,
	double* expdata,
	double* mask,
	double res,
	int32_t relax,
	int32_t* nn
)
{
	int64_t len = (int64_t) nn[0] * nn[1] * nn[2];
	int64_t i;
	double amp, amp2, seqamp, phase;
	double factor;
	
	if (relax > 0)
	{
		factor = exp( ( res - 1.0)/res );
		for(i=0; i<len; i++)
		{
			if (mask[2*i] > 1e-6)
			{
				amp2 = expdata[2*i]*expdata[2*i] +
							expdata[2*i+1]*expdata[2*i+1];
				amp = sqrt(amp2);
				seqamp = seqdata[2*i]*seqdata[2*i] +
							seqdata[2*i+1]*seqdata[2*i+1];
				if ( fabs(amp2 - seqamp) > (amp * factor) )
				{
					phase = atan2(seqdata[2*i+1], seqdata[2*i]);
					seqdata[2*i] = amp*cos(phase);
					seqdata[2*i+1] = amp*sin(phase);
				}
			}
		}
	}
	else
	{
		for(i=0; i<len; i++)
		{
			if (mask[2*i] > 1e-6)
			{
				amp = sqrt( expdata[2*i]*expdata[2*i] +
							expdata[2*i+1]*expdata[2*i+1]);

				phase = atan2(seqdata[2*i+1], seqdata[2*i]);
				seqdata[2*i] = amp*cos(phase);
				seqdata[2*i+1] = amp*sin(phase);
			}
		}
	}
}

void MaskedSetAmplitudesIterRelaxed
(
	double* seqdata,
	double* expdata,
	double* mask,
	int32_t* nn,
	int niter,
	int iter
)
{
	int64_t len = (int64_t) nn[0] * nn[1] * nn[2];
	int64_t i;
	double amp, amp2, seqamp, phase;
	double factor;
	
	if (iter <= niter)
	{
		factor = ((double) (niter - iter))/((double) niter);
		for(i=0; i<len; i++)
		{
			if (mask[2*i] > 1e-6)
			{
				amp2 = expdata[2*i]*expdata[2*i] +
							expdata[2*i+1]*expdata[2*i+1];
				amp = sqrt(amp2);
				seqamp = seqdata[2*i]*seqdata[2*i] +
							seqdata[2*i+1]*seqdata[2*i+1];
				if ( fabs(amp2 - seqamp) > (amp * factor) )
				{
					phase = atan2(seqdata[2*i+1], seqdata[2*i]);
					seqdata[2*i] = amp*cos(phase);
					seqdata[2*i+1] = amp*sin(phase);
				}
			}
		}
	}
	else
	{
		for(i=0; i<len; i++)
		{
			if (mask[2*i] > 1e-6)
			{
				amp = sqrt( expdata[2*i]*expdata[2*i] +
							expdata[2*i+1]*expdata[2*i+1]);

				phase = atan2(seqdata[2*i+1], seqdata[2*i]);
				seqdata[2*i] = amp*cos(phase);
				seqdata[2*i+1] = amp*sin(phase);
			}
		}
	}
}

void MaskedSetPCAmplitudesIterRelaxed
(
	double* seqdata,
	double* expdata,
	double* itnsty,
	double* mask,
	int32_t* nn,
	int niter,
	int iter
)
{
	int64_t len = (int64_t) nn[0] * nn[1] * nn[2];
	int64_t i;
	double amp, amp2, expamp, expamp2, pcamp, phase;
	double factor;
	
	if (iter <= niter)
	{
		factor = ((double) (niter - iter))/((double) niter);
		for(i=0; i<len; i++)
		{
			if (mask[2*i] > 1e-6)
			{
				expamp2 = expdata[2*i]*expdata[2*i] +
							expdata[2*i+1]*expdata[2*i+1];
				expamp = sqrt(expamp2);
				amp2 = seqdata[2*i]*seqdata[2*i] +
							seqdata[2*i+1]*seqdata[2*i+1];
				amp = sqrt(amp2);
				if ( fabs(expamp2 - amp2) > (expamp * factor) )
				{
					pcamp = sqrt(sqrt( itnsty[2*i]*itnsty[2*i] + itnsty[2*i+1]*itnsty[2*i+1] ));
					phase = atan2(seqdata[2*i+1], seqdata[2*i]);
					seqdata[2*i] = (expamp*amp/pcamp)*cos(phase);
					seqdata[2*i+1] = (expamp*amp/pcamp)*sin(phase);
				}
			}
		}
	}
	else
	{
		for(i=0; i<len; i++)
		{
			if (mask[2*i] > 1e-6)
			{
				expamp = sqrt( expdata[2*i]*expdata[2*i] +
					expdata[2*i+1]*expdata[2*i+1]);
				amp = sqrt( seqdata[2*i]*seqdata[2*i] +
					seqdata[2*i+1]*seqdata[2*i+1]);
				pcamp = sqrt(sqrt( itnsty[2*i]*itnsty[2*i] + itnsty[2*i+1]*itnsty[2*i+1] ));
				phase = atan2(seqdata[2*i+1], seqdata[2*i]);
				seqdata[2*i] = (expamp*amp/pcamp)*cos(phase);
				seqdata[2*i+1] = (expamp*amp/pcamp)*sin(phase);
			}
		}
	}
}
