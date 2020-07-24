/*
#############################################
##   Filename: prfftwrs.cxx
##
##    Copyright (C) 2020 Marcus C. Newton
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


#include <pthread.h>
#define NO_IMPORT_ARRAY
#define PY_ARRAY_UNIQUE_SYMBOL prfftw_ARRAY_API
#include <Python.h>
#include "prfftwmodule.h"


void* RS_ER_p(void* thdata)
{
	ThreadData* thd=(ThreadData*) thdata;
	int64_t idxstart = thd->idxstart;
	int64_t idxend = thd->idxend;
	double* seqdata = (double *) thd->ar1;
	double* support = (double *) thd->ar3;
	int64_t i;
	for(i=idxstart; i<idxend; i++)
	{
		if ( support[2*i] < 1e-6 )
		{
			seqdata[2*i] = 0.0;
			seqdata[2*i+1] = 0.0;
		}
	}
	return NULL;
}

void RS_ER
(
   double* seqdata,
   double* rho_m1,
   double* support,
   int32_t* nn
)
{
	int64_t len =  (int64_t) nn[0] * nn[1] * nn[2];
	pthread_t thread[npthread];
	int64_t thdlen = (len + npthread-1)/npthread;
	ThreadData thdata[npthread];
	int64_t i;
	for (i=0; i<npthread; i++)
	{
		thdata[i].id = i;
		thdata[i].idxstart = i*thdlen;
		thdata[i].idxend = (i+1)*thdlen;
		thdata[i].ar1 = seqdata;
		thdata[i].ar2 = rho_m1;
		thdata[i].ar3 = support;
	}
	thdata[npthread-1].idxend = len;
	for (i=0; i<npthread; i++)
	{
		pthread_create(&thread[i], NULL, RS_ER_p, &thdata[i]);
	}
	for (i=0; i<npthread; i++)
	{
		pthread_join(thread[i], NULL);
	}
}


void* RS_HIO_p(void* thdata)
{
	ThreadData* thd=(ThreadData*) thdata;
	int64_t idxstart = thd->idxstart;
	int64_t idxend = thd->idxend;
	double* seqdata = (double *) thd->ar1;
	double* rho_m1 = (double *) thd->ar2;
	double* support = (double *) thd->ar3;
	double* beta_ = (double *) thd->ar4;
	double beta = *beta_;
	int64_t i;
	for(i=idxstart; i<idxend; i++)
	{
		if ( support[2*i] < 1e-6 )
		{
			seqdata[2*i] = rho_m1[2*i] - beta*seqdata[2*i];
			seqdata[2*i+1] = rho_m1[2*i+1] - beta*seqdata[2*i+1];
		}
	}
	return NULL;
}

void RS_HIO
(
   double* seqdata,
   double* rho_m1,
   double* support,
   int32_t* nn,
   double beta
)
{
	int64_t len =  (int64_t) nn[0] * nn[1] * nn[2];
	pthread_t thread[npthread];
	int64_t thdlen = (len + npthread-1)/npthread;
	ThreadData thdata[npthread];
	int64_t i;
	for (i=0; i<npthread; i++)
	{
		thdata[i].id = i;
		thdata[i].idxstart = i*thdlen;
		thdata[i].idxend = (i+1)*thdlen;
		thdata[i].ar1 = seqdata;
		thdata[i].ar2 = rho_m1;
		thdata[i].ar3 = support;
		thdata[i].ar4 = &beta;
	}
	thdata[npthread-1].idxend = len;
	for (i=0; i<npthread; i++)
	{
		pthread_create(&thread[i], NULL, RS_HIO_p, &thdata[i]);
	}
	for (i=0; i<npthread; i++)
	{
		pthread_join(thread[i], NULL);
	}
}


void* RS_HIO_P_p(void* thdata)
{
	ThreadData* thd=(ThreadData*) thdata;
	int64_t idxstart = thd->idxstart;
	int64_t idxend = thd->idxend;
	double* seqdata = (double *) thd->ar1;
	double* rho_m1 = (double *) thd->ar2;
	double* support = (double *) thd->ar3;
	double* beta_ = (double *) thd->ar4;
	double beta = *beta_;
	int64_t i;
	for(i=idxstart; i<idxend; i++)
	{
		if ( support[2*i] < 1e-6 || (seqdata[2*i] < 0.0 && seqdata[2*i+1] < 0.0) )
		{
			seqdata[2*i] = rho_m1[2*i] - beta*seqdata[2*i];
			seqdata[2*i+1] = rho_m1[2*i+1] - beta*seqdata[2*i+1];
		}
	}
	return NULL;
}

void RS_HIO_P
(
   double* seqdata,
   double* rho_m1,
   double* support,
   int32_t* nn,
   double beta
)
{
	int64_t len =  (int64_t) nn[0] * nn[1] * nn[2];
	pthread_t thread[npthread];
	int64_t thdlen = (len + npthread-1)/npthread;
	ThreadData thdata[npthread];
	int64_t i;
	for (i=0; i<npthread; i++)
	{
		thdata[i].id = i;
		thdata[i].idxstart = i*thdlen;
		thdata[i].idxend = (i+1)*thdlen;
		thdata[i].ar1 = seqdata;
		thdata[i].ar2 = rho_m1;
		thdata[i].ar3 = support;
		thdata[i].ar4 = &beta;
	}
	thdata[npthread-1].idxend = len;
	for (i=0; i<npthread; i++)
	{
		pthread_create(&thread[i], NULL, RS_HIO_P_p, &thdata[i]);
	}
	for (i=0; i<npthread; i++)
	{
		pthread_join(thread[i], NULL);
	}
}

void* RS_HPR_p(void* thdata)
{
	ThreadData* thd=(ThreadData*) thdata;
	int64_t idxstart = thd->idxstart;
	int64_t idxend = thd->idxend;
	double* seqdata = (double *) thd->ar1;
	double* rho_m1 = (double *) thd->ar2;
	double* support = (double *) thd->ar3;
	double* beta_ = (double *) thd->ar4;
	double beta = *beta_;
	int64_t i;
	for(i=idxstart; i<idxend; i++)
	{
		if ( support[2*i] < 1e-6 || ((2*seqdata[2*i] - rho_m1[2*i])  < (1.0 - beta)*seqdata[2*i]  &&  (2*seqdata[2*i+1] - rho_m1[2*i+1])  < (1.0 - beta)*seqdata[2*i+1]))
		{
			seqdata[2*i] = rho_m1[2*i] - beta*seqdata[2*i];
			seqdata[2*i+1] = rho_m1[2*i+1] - beta*seqdata[2*i+1];
		}
	}
	return NULL;
}

void RS_HPR
(
   double* seqdata,
   double* rho_m1,
   double* support,
   int32_t* nn,
   double beta
)
{
	int64_t len =  (int64_t) nn[0] * nn[1] * nn[2];
    pthread_t thread[npthread];
	int64_t thdlen = (len + npthread-1)/npthread;
	ThreadData thdata[npthread];
	int64_t i;
	for (i=0; i<npthread; i++)
	{
		thdata[i].id = i;
		thdata[i].idxstart = i*thdlen;
		thdata[i].idxend = (i+1)*thdlen;
		thdata[i].ar1 = seqdata;
		thdata[i].ar2 = rho_m1;
		thdata[i].ar3 = support;
		thdata[i].ar4 = &beta;
	}
	thdata[npthread-1].idxend = len;
	for (i=0; i<npthread; i++)
	{
		pthread_create(&thread[i], NULL, RS_HPR_p, &thdata[i]);
	}
	for (i=0; i<npthread; i++)
	{
		pthread_join(thread[i], NULL);
	}
}


void* RS_RAAR_p(void* thdata)
{
	ThreadData* thd=(ThreadData*) thdata;
	int64_t idxstart = thd->idxstart;
	int64_t idxend = thd->idxend;
	double* seqdata = (double *) thd->ar1;
	double* rho_m1 = (double *) thd->ar2;
	double* support = (double *) thd->ar3;
	double* beta_ = (double *) thd->ar4;
	double beta = *beta_;
	int64_t i;
	for(i=idxstart; i<idxend; i++)
	{
		if ( support[2*i] < 1e-6 || (( 2.0*seqdata[2*i] - rho_m1[2*i] ) < 0.0 && ( 2.0*seqdata[2*i+1] - rho_m1[2*i+1] ) < 0.0 ) )
		{
			seqdata[2*i] = beta * rho_m1[2*i] - ( 1.0 - 2.0*beta ) * seqdata[2*i];
			seqdata[2*i+1] = beta*rho_m1[2*i+1] - ( 1.0 - 2.0*beta ) * seqdata[2*i+1];
		}
	}
	return NULL;
}

void RS_RAAR
(
   double* seqdata,
   double* rho_m1,
   double* support,
   int32_t* nn,
   double beta
)
{
	int64_t len =  (int64_t) nn[0] * nn[1] * nn[2];
    pthread_t thread[npthread];
	int64_t thdlen = (len + npthread-1)/npthread;
	ThreadData thdata[npthread];
	int64_t i;
	for (i=0; i<npthread; i++)
	{
		thdata[i].id = i;
		thdata[i].idxstart = i*thdlen;
		thdata[i].idxend = (i+1)*thdlen;
		thdata[i].ar1 = seqdata;
		thdata[i].ar2 = rho_m1;
		thdata[i].ar3 = support;
		thdata[i].ar4 = &beta;
	}
	thdata[npthread-1].idxend = len;
	for (i=0; i<npthread; i++)
	{
		pthread_create(&thread[i], NULL, RS_RAAR_p, &thdata[i]);
	}
	for (i=0; i<npthread; i++)
	{
		pthread_join(thread[i], NULL);
	}
}


void* RS_PCHIO_p(void* thdata)
{
	ThreadData* thd=(ThreadData*) thdata;
	int64_t idxstart = thd->idxstart;
	int64_t idxend = thd->idxend;
	double* seqdata = (double *) thd->ar1;
	double* rho_m1 = (double *) thd->ar2;
	double* support = (double *) thd->ar3;
	double* beta_ = (double *) thd->ar4;
	double* phasemax_ = (double *) thd->ar5;
	double* phasemin_ = (double *) thd->ar6;
	double beta = *beta_;
	double phasemax = *phasemax_;
	double phasemin = *phasemin_;
	int64_t i;
	double phase;
	for(i=idxstart; i<idxend; i++)
	{
		phase = atan2(seqdata[2*i+1], seqdata[2*i]);
		if ( support[2*i] < 1e-6 || phase > phasemax || phase < phasemin )
		{
			seqdata[2*i] = rho_m1[2*i] - beta*seqdata[2*i];
			seqdata[2*i+1] = rho_m1[2*i+1] - beta*seqdata[2*i+1];
		}
	}
	return NULL;
}

void RS_PCHIO
(
   double* seqdata,
   double* rho_m1,
   double* support,
   int32_t* nn,
   double beta,
   double phasemax,
   double phasemin
)
{
	int64_t len = (int64_t) nn[0] * nn[1] * nn[2];
    pthread_t thread[npthread];
	int64_t thdlen = (len + npthread-1)/npthread;
	ThreadData thdata[npthread];
	int64_t i;
	for (i=0; i<npthread; i++)
	{
		thdata[i].id = i;
		thdata[i].idxstart = i*thdlen;
		thdata[i].idxend = (i+1)*thdlen;
		thdata[i].ar1 = seqdata;
		thdata[i].ar2 = rho_m1;
		thdata[i].ar3 = support;
		thdata[i].ar4 = &beta;
		thdata[i].ar5 = &phasemax;
		thdata[i].ar6 = &phasemin;
	}
	thdata[npthread-1].idxend = len;
	for (i=0; i<npthread; i++)
	{
		pthread_create(&thread[i], NULL, RS_PCHIO_p, &thdata[i]);
	}
	for (i=0; i<npthread; i++)
	{
		pthread_join(thread[i], NULL);
	}
}


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


void* RS_POER_p(void* thdata)
{
	ThreadData* thd=(ThreadData*) thdata;
	int64_t idxstart = thd->idxstart;
	int64_t idxend = thd->idxend;
	double* seqdata = (double *) thd->ar1;
	double* support = (double *) thd->ar3;
	int64_t i;
	double amp;
	for(i=idxstart; i<idxend; i++)
	{
		amp = sqrt( seqdata[2*i]*seqdata[2*i] + seqdata[2*i+1]*seqdata[2*i+1] );
		if ( support[2*i] < 1e-6 && seqdata[2*i] >= 0.0)
		{
			seqdata[2*i] = amp;
			seqdata[2*i+1] = 0.0;
		}
		else if (support[2*i] < 1e-6 && seqdata[2*i] < 0.0)
		{
			seqdata[2*i] = -amp;
			seqdata[2*i+1] = 0.0;
		}
	}
	return NULL;
}

void RS_POER
(
   double* seqdata,
   double* rho_m1,
   double* support,
   int32_t* nn
)
{
	int64_t len =  (int64_t) nn[0] * nn[1] * nn[2];
    pthread_t thread[npthread];
	int64_t thdlen = (len + npthread-1)/npthread;
	ThreadData thdata[npthread];
	int64_t i;
	for (i=0; i<npthread; i++)
	{
		thdata[i].id = i;
		thdata[i].idxstart = i*thdlen;
		thdata[i].idxend = (i+1)*thdlen;
		thdata[i].ar1 = seqdata;
		thdata[i].ar2 = rho_m1;
		thdata[i].ar3 = support;
	}
	thdata[npthread-1].idxend = len;
	for (i=0; i<npthread; i++)
	{
		pthread_create(&thread[i], NULL, RS_POER_p, &thdata[i]);
	}
	for (i=0; i<npthread; i++)
	{
		pthread_join(thread[i], NULL);
	}
}