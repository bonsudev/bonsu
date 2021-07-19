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

int CopyAmp2
(
	double* data1, 
	double* data2, 
	int32_t* nn
)
{
	CopyAmp(data1, data2, nn);
	return 0;
}

int CopyAbs
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
		data2[2*i] = sqrt(data1[2*i]*data1[2*i] + data1[2*i+1]*data1[2*i+1]);
		data2[2*i+1] = 0.0;
	}
	return 0;
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

void CopySquare
(
	double* rho, 
	double* itnsty,
	int32_t* nn
)
{
	int len = nn[0] * nn[1] * nn[2];
	int i;
	for(i=0; i<len; i++)
	{
		itnsty[2*i] = (rho[2*i]*rho[2*i] + rho[2*i+1]*rho[2*i+1]);
		itnsty[2*i+1] = 0.0;
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

int FFTPlan
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
	return 1;
	}
	else
	{
	return 0;
	}
}

int FFTPlanPair
(
	fftw_plan* torecip,
	fftw_plan* toreal,
	double* data1,
	double* data2,
	int32_t* nn,
	int32_t ndim
)
{
	int  dist = (((fftw_complex*) data2) - ((fftw_complex*) data1));
	*torecip = fftw_plan_many_dft(ndim, (int32_t*) nn, 2,
		(fftw_complex*) data1, NULL, 1, dist,
		(fftw_complex*) data1, NULL, 1, dist,
		+1, FFTW_MEASURE);
	*toreal = fftw_plan_many_dft(ndim, (int32_t*) nn, 2,
		(fftw_complex*) data1, NULL, 1, dist,
		(fftw_complex*) data1, NULL, 1, dist,
		-1, FFTW_MEASURE);
	
	if (torecip == NULL || toreal == NULL)
	{
	return 1;
	}
	else
	{
	return 0;
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

void FFTStridePair
(
	double* data1,
	double* data2,
	int32_t* nn,
	fftw_plan* plan
)
{
	double inv_sqrt_n;
	int64_t i;
	int64_t len = (int64_t) nn[0] * nn[1] * nn[2];
	fftw_execute( *plan );
	inv_sqrt_n = 1.0 / sqrt((double) len);
	for(i=0; i<len; i++)
	{
		data1[2*i] *= inv_sqrt_n;
		data1[2*i+1] *= inv_sqrt_n;
		data2[2*i] *= inv_sqrt_n;
		data2[2*i+1] *= inv_sqrt_n;
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

int wrap_array_nomem(double* indata, double* tmpdata, int32_t* nn, int drctn)
{
	int i, j, k;
	int64_t ii, iih;
	int iish;
	int splt[3] = {0,0,0};
	int32_t nnh[3] = {0,0,0};
	int64_t lenh;
	CopyArray(indata, tmpdata, nn);
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
	int qd;
	int32_t c[3] = {0,0,0};
	int32_t cn[3] = {0,0,0};
	for(qd=0; qd<8; qd++)
	{
		c[0] = ((qd+2)/2)%2;
		c[1] = ((qd+4)/4)%2;
		c[2] = 1;
		c[0] = (c[0]+qd)%2;
		c[1] = (c[1]+qd)%2;
		c[2] = (c[2]+qd)%2;
		cn[0] = (c[0]+1)%2;
		cn[1] = (c[1]+1)%2;
		cn[2] = (c[2]+1)%2;
		nnh[0] = abs(nn[0]*cn[0] - splt[0]);
		nnh[1] = abs(nn[1]*cn[1] - splt[1]);
		nnh[2] = abs(nn[2]*cn[2] - splt[2]);
		lenh = nnh[0] * nnh[1] * nnh[2];
		for(iih=0; iih<lenh; iih++)
		{
			idx2ijk(iih, &i, &j, &k, &nnh[0]);
			i+=cn[0]*splt[0]; j+=cn[1]*splt[1]; k+=cn[2]*splt[2];
			ii = (k+nn[2]*(j+nn[1]*i));
			iish = ((nn[2]*c[2] - splt[2] + k)+nn[2]*((nn[1]*c[1] - splt[1] + j)+nn[1]*(nn[0]*c[0] - splt[0] + i)));
			indata[2*iish] = tmpdata[2*ii];
			indata[2*iish+1] = tmpdata[2*ii+1];
		}
	}
	return 0;
}


int wrap_array_nomem_tmppair(double* indata, double* tmpdata1, double* tmpdata2, int32_t* nn, int drctn)
{
	int i, j, k;
	int64_t ii, iih;
	int iish;
	int64_t len = nn[0] * nn[1] * nn[2];
	int splt[3] = {0,0,0};
	int32_t nnh[3] = {0,0,0};
	int64_t lenh;
	for(ii=0; ii<len; ii++)
	{
		tmpdata1[ii] = indata[2*ii];
		tmpdata2[ii] = indata[2*ii+1];
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
	int qd;
	int32_t c[3] = {0,0,0};
	int32_t cn[3] = {0,0,0};
	for(qd=0; qd<8; qd++)
	{
		c[0] = ((qd+2)/2)%2;
		c[1] = ((qd+4)/4)%2;
		c[2] = 1;
		c[0] = (c[0]+qd)%2;
		c[1] = (c[1]+qd)%2;
		c[2] = (c[2]+qd)%2;
		cn[0] = (c[0]+1)%2;
		cn[1] = (c[1]+1)%2;
		cn[2] = (c[2]+1)%2;
		nnh[0] = abs(nn[0]*cn[0] - splt[0]);
		nnh[1] = abs(nn[1]*cn[1] - splt[1]);
		nnh[2] = abs(nn[2]*cn[2] - splt[2]);
		lenh = nnh[0] * nnh[1] * nnh[2];
		for(iih=0; iih<lenh; iih++)
		{
			idx2ijk(iih, &i, &j, &k, &nnh[0]);
			i+=cn[0]*splt[0]; j+=cn[1]*splt[1]; k+=cn[2]*splt[2];
			ii = (k+nn[2]*(j+nn[1]*i));
			iish = ((nn[2]*c[2] - splt[2] + k)+nn[2]*((nn[1]*c[1] - splt[1] + j)+nn[1]*(nn[0]*c[0] - splt[0] + i)));
			indata[2*iish] = tmpdata1[ii];
			indata[2*iish+1] = tmpdata2[ii];
		}
	}
	return 0;
}



int convolve_nomem3(double* indata1, double* indata2, int32_t ndim, int32_t* dims, double* data1, double* data2, fftw_plan* torecip, fftw_plan* toreal)
{
	int iib, ii, i, j, k;
	int len;
	double val1[2] = {0.0,0.0};
	double val2[2] = {0.0,0.0};
	int32_t nn[3] = {dims[0], dims[1], dims[2]};
	int32_t nnh[3] = {(dims[0] / 8), (dims[1] / 8), (dims[2] / 8)};
	int32_t nn2[3] = {0,0,0};
	nn2[0] = dims[0] + 2*(dims[0]/8);
	nn2[1] = dims[1] + 2*(dims[1]/8);
	nn2[2] = dims[2] + 2*(dims[2]/8);
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
	FFTStridePair(data1, data2, nn2, torecip);
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
	FFTStridePair(data1, data2, nn2, toreal);
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

void MaskedSetPCAmplitudes
(
	double* seqdata,
	double* expdata,
	double* itnsty,
	double* mask,
	int32_t* nn
)
{
	int64_t len = (int64_t) nn[0] * nn[1] * nn[2];
	int64_t i;
	double expamp, pcamp, amp, phase;
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

void make_Id_iter
(
	double* rho,
	double* rhom1,
	double* pca_Id_iter,
	int32_t* nn
)
{
	int len = nn[0] * nn[1] * nn[2];
	int i;
	double itnsty, itnstym1;
	for(i=0; i<len; i++)
	{
		itnsty = rho[2*i]*rho[2*i] + rho[2*i+1]*rho[2*i+1];
		itnstym1 = rhom1[2*i]*rhom1[2*i] + rhom1[2*i+1]*rhom1[2*i+1];
		pca_Id_iter[2*i] = (2.0*itnsty - itnstym1);
		pca_Id_iter[2*i+1] = 0.0;
	}
}

void divide_I_Id_iter
(
	double* expdata,
	double* pca_Idm_iter,
	double* mask,
	double* pca_Idmdiv_iter,
	int32_t* nn
)
{
	int len = nn[0] * nn[1] * nn[2];
	int i;
	double val1[2] = {0.0,0.0};
	double val2[2] = {0.0,0.0};
	double divis = 0;
	for(i=0; i<len; i++)
	{
		
		val1[0] = (expdata[2*i]*expdata[2*i] + expdata[2*i+1]*expdata[2*i+1]);
		val1[1] = 0.0;
		val2[0] = pca_Idm_iter[2*i];
		val2[1] = pca_Idm_iter[2*i+1];
		divis = val2[0]*val2[0] + val2[1]*val2[1];
		if(divis >1e-150)
		{
			pca_Idmdiv_iter[2*i] = (val1[0]*val2[0] + val1[1]*val2[1])/divis;
			pca_Idmdiv_iter[2*i+1] =(val1[1]*val2[0] - val1[0]*val2[1])/divis;
		}
		else
		{
			pca_Idmdiv_iter[2*i] = 0.0;
			pca_Idmdiv_iter[2*i+1] = 0.0;
		}
	}
}

void mask_gamma(double* gamma, int32_t* nn, int32_t* maskdim)
{
	int ii, i, j, k;
	if( nn[0] ==1 )  maskdim[0] = 1;
	if( nn[1] ==1 )  maskdim[1] = 1;
	if( nn[2] ==1 )  maskdim[2] = 1;
	int32_t nns[3] = {0, 0, 0};
	int32_t nne[3] = {0, 0, 0};
	nns[0] = (nn[0] - maskdim[0])/2;
	nne[0] = nns[0] + maskdim[0];
	nns[1] = (nn[1] - maskdim[1])/2;
	nne[1] = nns[1] + maskdim[1];
	nns[2] = (nn[2] - maskdim[2])/2;
	nne[2] = nns[2] + maskdim[2];
	
	for(i=0;i<nn[0]; i++)
	{
		for(j=0;j<nn[1]; j++)
		{
			for(k=0;k<nn[2]; k++)
			{
				if( i >= nns[0] && i  < nne[0] &&
					j >= nns[1] && j < nne[1] &&
					k >= nns[2] && k < nne[2] )
				{
					ii = (k+nn[2]*(j+nn[1]*i));
					gamma[2*ii] = 0.0;
					gamma[2*ii+1] = 0.0;
				}
			}
		}
	}
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

