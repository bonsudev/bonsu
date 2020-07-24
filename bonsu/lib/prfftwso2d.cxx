/*
#############################################
##   Filename: prfftwso2d.cxx
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

double SOVecNorm
(
	double* vec
)
{
	double norm;
	norm = sqrt(vec[0]*vec[0]+vec[1]*vec[1]);
	return norm;
}

void SOMatVecProd
(
	double H[2][2],
	double* y,
	double* dtau
)
{
	dtau[0] = H[0][0]*y[0] + H[0][1]*y[1];
	dtau[1] = H[1][0]*y[0] + H[1][1]*y[1];
}

void SOMatInv
(
	double H[2][2]
)
{
	double Htmp[2][2];
	double determ = 1.0/(H[0][0]*H[1][1] - H[0][1]*H[1][0]);
	Htmp[0][0] = H[1][1];
	Htmp[1][1] = H[0][0];
	Htmp[0][1] = -H[0][1];
	Htmp[1][0] = -H[1][0];
	H[0][0] = Htmp[0][0]*determ;
	H[0][1] = Htmp[0][1]*determ;
	H[1][0] = Htmp[1][0]*determ;
	H[1][1] = Htmp[1][1]*determ;
}

inline double LGradS
(
	double rho[2],
	double rho_m1[2],
	int idx
)
{
	return (rho[idx] - rho_m1[idx]);
};

inline double LGradnS
(
	double rho[2],
	double rho_m1[2],
	int idx
)
{
	return (-rho[idx]);
};

inline double wLGradS
(
	double rho[2],
	double rho_m1[2],
	double rho_m2[2],
	int idx
)
{
	double ampT = sqrt(rho_m2[0]*rho_m2[0] + rho_m2[1]*rho_m2[1]);
	double epsilon = (ampT > 1e-6) ? 0.0 : 1.0 ;
	
	return (1.0 / ( ampT+epsilon ))*(rho[idx] - rho_m1[idx]);
};

inline double wLGradnS
(
	double rho[2],
	double rho_m1[2],
	double rho_m2[2],
	int idx
)
{
	double ampT = sqrt(rho_m2[0]*rho_m2[0] + rho_m2[1]*rho_m2[1]);
	double epsilon = (ampT > 1e-6) ? 0.0 : 1.0 ;
	
	return (-(1.0 / ( ampT+epsilon ))*rho[idx] + ((1.0 / ( ampT+epsilon ))-1.0)*rho_m1[idx]);
};


void Hfit
(
	double* taui,
	double* psii,
	double* tau,
	double* dtau,
	double* psi,
	double H[2][2],
	int niter
)
{
	double taum[2] = {0.0,0.0};
	double psim[2] = {0.0,0.0};
	double taur[2] = {0.0,0.0};
	double* x = (double*) malloc( 2*niter * sizeof(double));
	double* y = (double*) malloc( 2*niter * sizeof(double));
	double* tmp = (double*) malloc( 2*niter * sizeof(double));
	if (!x || !y || !tmp)
	{
		free(x);
		free(y);
		free(tmp);
		return;
	}
	
	double xxt[2][2] = {{0.0}}; 
	double xyt[2][2] = {{0.0}}; 
	double Htmp[2][2] = {{0.0}}; 
	double mintaul = 0.0;
	double r = 0.0;
	int i,j,k;
	int imin = 0;
	
	
	for( i=0; i<niter; i++)
	{
		taum[0] += taui[2*i];
		taum[1] += taui[2*i+1];
		psim[0] += psii[2*i];
		psim[1] += psii[2*i+1];
	}
	taum[0] = taum[0] / ((double) niter);
	taum[1] = taum[1] / ((double) niter);
	psim[0] = psim[0] / ((double) niter);
	psim[1] = psim[1] / ((double) niter);
	
	
	
	
	
	
	for( i=0; i<niter; i++)
	{
		x[2*i] = taui[2*i] - taum[0];
		x[2*i+1] = taui[2*i+1] - taum[1];
		y[2*i] = psii[2*i] - psim[0];
		y[2*i+1] = psii[2*i+1] - psim[1];
	}
	
	
	for( i=0; i<2; i++)
	{
		for( j=0; j<2; j++)
		{
			for( k=0; k<niter; k++)
			{
				xxt[i][j] += x[2*k+i]*x[2*k+j];
				xyt[i][j] += x[2*k+i]*y[2*k+j];
			}
		}
	}
	SOMatInv(xxt);
	for( i=0; i<2; i++)
	{
		for( j=0; j<2; j++)
		{
			for( k=0; k<2; k++)
			{
				Htmp[i][j] += xxt[i][k]*xyt[k][j];
			}
		}
	}
	SOMatInv(Htmp);
	H[0][0] = Htmp[0][0] / ((double) niter); H[0][1] = Htmp[0][1] / ((double) niter); 
	H[1][0] = Htmp[1][0] / ((double) niter); H[1][1] = Htmp[1][1] / ((double) niter); 
	
	
	
	
	for( i=0; i<2; i++)
	{
		for( j=0; j<2; j++)
		{
			for( k=0; k<niter; k++)
			{
				tmp[2*k+i] += H[i][j]*psii[2*k+j];
			}
		}
	}
	for( k=0; k<niter; k++)
	{
		taur[0] += -(tmp[2*k]-taui[2*k]);
		taur[1] += -(tmp[2*k+1]-taui[2*k+1]);
	}
	taur[0] = taur[0] / ((double) niter);
	taur[1] = taur[1] / ((double) niter);
	
	
	
	
	for( i=0; i<niter; i++)
	{
		r = sqrt(psii[2*i]*psii[2*i] + psii[2*i+1]*psii[2*i+1]);
		if (r < mintaul || !mintaul)
		{
			mintaul = r;
			imin = i;
		}
	}
	
	tau[0] = taui[2*imin];
	tau[1] = taui[2*imin+1];
	psi[0] = psii[2*imin];
	psi[1] = psii[2*imin+1];
	
	dtau[0] = tau[0] - taur[0];
	dtau[1] = tau[1] - taur[1];
	
	free(x);
	free(y);
	free(tmp);
}

void SOTrueHi
(
	SeqArrayObjects* seqarrays,
	double H[2][2],
	fftw_plan* torecip,
	fftw_plan* toreal
)
{
	double* rho = seqarrays->seqdata;
	double* rho_m2 = seqarrays->rho_m2;
	double* expdata = seqarrays->expdata;
	double* support = seqarrays->support;
	double* mask = seqarrays->mask;
	double* grad = seqarrays->tmparray1;
	double* step = seqarrays->tmparray2;
	int32_t* nn = seqarrays->nn;
	int32_t* citer_flow = seqarrays->citer_flow;
	int startiter = seqarrays->startiter;
	
	int64_t len =  nn[0] * nn[1] * nn[2];
	int64_t i;
	double H0_tmp[2] = {0.0,0.0};
	double H1_tmp[2] = {0.0,0.0};
	double newgrad[2] = {0.0,0.0};
	for(i=0; i<len; i++)
	{
		rho[2*i] = grad[2*i];
		rho[2*i+1] = grad[2*i+1];
	}
	FFTStride(rho, nn, torecip);
	MaskedSetAmplitudes(rho, expdata, mask, nn);
	FFTStride(rho, nn, toreal);
	if (step[6] >= 0 && step[6] < (citer_flow[0] - startiter))
	{
		for(i=0; i<len; i++)
		{
			if (support[2*i] > 1e-6)
			{
				
				newgrad[0] = wLGradS(&rho[2*i], &grad[2*i], &rho_m2[2*i], 0);
				newgrad[1] = wLGradS(&rho[2*i], &grad[2*i], &rho_m2[2*i], 1);
				
				H0_tmp[0] -= grad[0]*newgrad[0] + grad[1]*newgrad[1];
				H0_tmp[1] -= grad[1]*newgrad[0] - grad[0]*newgrad[1];
			}
			else
			{
				
				newgrad[0] = wLGradnS(&rho[2*i], &grad[2*i], &rho_m2[2*i], 0);
				newgrad[1] = wLGradnS(&rho[2*i], &grad[2*i], &rho_m2[2*i], 1);
				
				H1_tmp[0] -= grad[0]*newgrad[0] + grad[1]*newgrad[1];
				H1_tmp[1] -= grad[1]*newgrad[0] - grad[0]*newgrad[1];
			}
		}
	}
	else
	{
		for(i=0; i<len; i++)
		{
			if (support[2*i] > 1e-6)
			{
				
				
				
				newgrad[0] = LGradS(&rho[2*i], &grad[2*i], 0);
				newgrad[1] = LGradS(&rho[2*i], &grad[2*i], 1);
				
				H0_tmp[0] -= grad[0]*newgrad[0] + grad[1]*newgrad[1];
				H0_tmp[1] -= grad[1]*newgrad[0] - grad[0]*newgrad[1];
			}
			else
			{
				
				
				
				newgrad[0] = LGradnS(&rho[2*i], &grad[2*i], 0);
				newgrad[1] = LGradnS(&rho[2*i], &grad[2*i], 1);
				
				H1_tmp[0] -= grad[0]*newgrad[0] + grad[1]*newgrad[1];
				H1_tmp[1] -= grad[1]*newgrad[0] - grad[0]*newgrad[1];
			}
		}
	}
	
	
	
	H[0][0] = 2.0*H0_tmp[0]/((double) len);
	H[1][1] = 2.0*H1_tmp[0]/((double) len);
	
	H[0][0] = 1.0/H[0][0];
	H[1][1] = -1.0/H[1][1];
	H[0][1] = H[1][0] = 0.0;
}

void SOH
(
	SeqArrayObjects* seqarrays,
	fftw_plan* torecip,
	fftw_plan* toreal,
	double H[2][2],
	double* y,
	double* dtau,
	double* steps
)
{	
	double Hydtau[2]={0.0,0.0};
	double Hy[2]={0.0,0.0};
	
	double dH[2][2]={{0.0}};
	double denom;
	double erquad;
	double dtau_scaled[2] = {0.0,0.0};
	
	dtau_scaled[0] = steps[3]*dtau[0]; 
	dtau_scaled[1] = steps[3]*dtau[1]; 
	SOMatVecProd(H,y,Hy);
	Hydtau[0] = dtau_scaled[0] - Hy[0];
	Hydtau[1] = dtau_scaled[1] - Hy[1];
	erquad = sqrt(SOVecNorm(Hydtau)/(SOVecNorm(dtau)+SOVecNorm(Hy)));
	if (erquad>1.0)
	{
		
		SOTrueHi(seqarrays, H, torecip, toreal);
		
		if (steps[1] > steps[0]/4.0){steps[0] = steps[1];}else{steps[0] = steps[0]/4.0;};
		
	}
	else if(erquad>1e-2)
	{
		denom = Hydtau[0]*y[0]+Hydtau[1]*y[1];
		dH[0][0] = Hydtau[0]*Hydtau[0]/denom;
		dH[0][1] = Hydtau[0]*Hydtau[1]/denom;
		dH[1][0] = Hydtau[1]*Hydtau[0]/denom;
		dH[1][1] = Hydtau[1]*Hydtau[1]/denom;
		
		H[0][0] = H[0][0] + dH[0][0];
		H[0][1] = H[0][1] + dH[0][1];
		H[1][0] = H[1][0] + dH[1][0];
		H[1][1] = H[1][1] + dH[1][1];
		
		
		
		
		if (2.0*steps[0] > steps[2]){steps[0] = steps[2];}else{steps[0] = 2.0*steps[0];};
	}
	else
	{
		
		if (3.0*steps[0] > steps[2]){steps[0] = steps[2];}else{steps[0] = 3.0*steps[0];};
	}
}

void SOGradPsi
(
	SeqArrayObjects* seqarrays,
	double* tau,
	double* psi,
	fftw_plan* torecip,
	fftw_plan* toreal
)
{
	double* rho = seqarrays->seqdata;
	double* support = seqarrays->support;
	double* rho_m1 = seqarrays->rho_m1;
	double* rho_m2 = seqarrays->rho_m2;
	double* grad = seqarrays->tmparray1;
	double* step = seqarrays->tmparray2;
	int32_t* nn = seqarrays->nn;
	int32_t* citer_flow = seqarrays->citer_flow;
	int startiter = seqarrays->startiter;
	
	int64_t len =  nn[0] * nn[1] * nn[2];
	int64_t i;
	psi[0] = 0.0;
	psi[1] = 0.0;
	double psi0_tmp[2] = {0.0,0.0};
	double psi1_tmp[2] = {0.0,0.0};
	double newgrad[2] = {0.0,0.0};
	double ampT;
	if (step[6] >= 0 && step[6] < (citer_flow[0] - startiter))
	{
		
		for(i=0; i<len; i++)
		{
			ampT = sqrt(rho_m2[2*i]*rho_m2[2*i] + rho_m2[2*i+1]*rho_m2[2*i+1]);
			if ( support[2*i] > 1e-6 )
			{
				rho[2*i] = rho_m1[2*i] + tau[0]*grad[2*i]*ampT;
				rho[2*i+1] = rho_m1[2*i+1] + tau[0]*grad[2*i+1]*ampT;
			}
			else
			{
				rho[2*i] = rho_m1[2*i] + tau[1]*(grad[2*i]*ampT - (1.0-ampT)*rho_m1[2*i] ); 
				rho[2*i+1] = rho_m1[2*i+1] + tau[1]*(grad[2*i+1]*ampT - (1.0-ampT)*rho_m1[2*i+1] );
			}
		}
	}
	else
	{
		for(i=0; i<len; i++)
		{
			if (support[2*i] > 1e-6)
			{
				rho[2*i] = rho_m1[2*i] + grad[2*i]*tau[0];
				rho[2*i+1] = rho_m1[2*i+1] + grad[2*i+1]*tau[0];
			}
			else
			{
				rho[2*i] = rho_m1[2*i] + grad[2*i]*tau[1];
				rho[2*i+1] = rho_m1[2*i+1] + grad[2*i+1]*tau[1];
			}
		}
	}
	FFTStride(rho, nn, torecip);
	
	MaskedSetAmplitudesZero(seqarrays);
	FFTStride(rho, nn, toreal);
	if (step[6] >= 0 && step[6] < (citer_flow[0] - startiter))
	{
		for(i=0; i<len; i++)
		{
			if (support[2*i] > 1e-6)
			{
				
				newgrad[0] = wLGradS(&rho[2*i], &rho_m1[2*i], &rho_m2[2*i], 0);
				newgrad[1] = wLGradS(&rho[2*i], &rho_m1[2*i], &rho_m2[2*i], 1);
				
				psi0_tmp[0] += grad[0]*newgrad[0] + grad[1]*newgrad[1];
				psi0_tmp[1] += grad[0]*newgrad[1] - grad[1]*newgrad[0];
			}
			else
			{
				
				newgrad[0] = wLGradnS(&rho[2*i], &rho_m1[2*i], &rho_m2[2*i], 0);
				newgrad[1] = wLGradnS(&rho[2*i], &rho_m1[2*i], &rho_m2[2*i], 1);
				
				psi1_tmp[0] += grad[0]*newgrad[0] + grad[1]*newgrad[1];
				psi1_tmp[1] += grad[0]*newgrad[1] - grad[1]*newgrad[0];
			}
		}
	}
	else
	{
		for(i=0; i<len; i++)
		{
			if (support[2*i] > 1e-6)
			{
				
				
				
				newgrad[0] = LGradS(&rho[2*i], &rho_m1[2*i], 0);
				newgrad[1] = LGradS(&rho[2*i], &rho_m1[2*i], 1);
				
				psi0_tmp[0] += grad[0]*newgrad[0] + grad[1]*newgrad[1];
				psi0_tmp[1] += grad[0]*newgrad[1] - grad[1]*newgrad[0];
			}
			else
			{
				
				
				
				newgrad[0] = LGradnS(&rho[2*i], &rho_m1[2*i], 0);
				newgrad[1] = LGradnS(&rho[2*i], &rho_m1[2*i], 1);
				
				psi1_tmp[0] += grad[0]*newgrad[0] + grad[1]*newgrad[1];
				psi1_tmp[1] += grad[0]*newgrad[1] - grad[1]*newgrad[0];
			}
		}
	}
	
	
	
	
	psi[0] = -psi0_tmp[0]/((double) len); 
	psi[1] = psi1_tmp[0]/((double) len);
}

double SOFrobSupport
(
	SeqArrayObjects* seqarrays
)
{
	
	double* support = seqarrays->support;
	double* grad1 = seqarrays->tmparray1;
	double* grad2 = seqarrays->tmparray1;
	int32_t* nn = seqarrays->nn;
	
	int64_t len =  nn[0] * nn[1] * nn[2];
	int64_t i;
	double gsum_s[2] = {0.0,0.0};
	double gsum_ns[2] = {0.0,0.0};
	double phi = 0.0; 
	
	for(i=0; i<len; i++)
	{
		if (support[2*i] > 1e-6)
		{
			gsum_s[0] += grad1[2*i]+grad2[2*i] + grad1[2*i+1]*grad2[2*i+1];
			
		}
		else
		{
			gsum_ns[0] += grad1[2*i]+grad2[2*i] + grad1[2*i+1]*grad2[2*i+1];
			
		}
	}
	phi = sqrt(gsum_s[0]*gsum_s[0]+gsum_ns[0]*gsum_ns[0])/((double) len);
	return phi;
}


void SOMinMaxtau
(
	SeqObjects* seqobs,
	SeqArrayObjects* seqarrays,
	double* tau,
	double* tauav,
	double H[2][2],
	double Hav[2][2],
	double* psi,
	int algiter,
	fftw_plan* torecip,
	fftw_plan* toreal
)
{
	double* step = seqarrays->tmparray2;
	
	int maxiter = seqobs->maxiter;
	double alpha = seqobs->alpha;
	double beta = seqobs->beta;
	
	int64_t i;
	double* taui = (double*) malloc( 2*maxiter * sizeof(double));
	double* psii = (double*) malloc( 2*maxiter * sizeof(double));
	if (!taui || !psii)
	{
		free(taui);
		free(psii);
		return;
	}
	double taumin[2] = {0.0,0.0};
	double taul = 0.0;
	double dtau[2] = {0.0,0.0};
	double taudtau[2] = {0.0,0.0};
	
	
	
	double dtaul = 0.0;
	double psil = 0.0;
	double psil0 = 0.0;
	double psilmin = 0.0;
	
	double psiold[2] = {0.0,0.0};
	
	double y[2] = {0.0,0.0};
	
	double nav = 1.0;
	double navlen = 50.0;
	
	for(i=0; i<maxiter; i++)
	{
		taui[2*i] = 0.0;
	 	taui[2*i+1] = 0.0;
	 	psii[2*i] = 0.0;
		psii[2*i+1] = 0.0;
	}
	
	
	psil0 = SOFrobSupport(seqarrays);
	
	if (algiter == 0)
	{
		
		tau[0] = 0.0; 
		tau[1] = 0.0;
	}
	else
	{
		tau[0] = tauav[0];
		tau[1] = tauav[1];
	}
	
	
	SOGradPsi(seqarrays, tau, psi, torecip, toreal);
	if (algiter == 0)
	{
		
		tau[0] = alpha;
		tau[1] = beta;
	}
	
	taui[0] = tau[0]; taui[1] = tau[1];
	psii[0]= psi[0]; psii[1] = psi[1];
	psiold[0] = psi[0]; psiold[1] = psi[1];
	
	psil = SOVecNorm(psi);
	
	psilmin = psil;
	taumin[0] = tau[0]; taumin[1] = tau[1]; 
	
	
	if ( nav < (navlen-1.0))
	{
		
		H[0][0] = -alpha*1.0/psi[0];
		H[1][1] = -beta*1.0/psi[1];
	}
	else
	{
		
		H[0][0] = Hav[0][0]; H[0][1] = Hav[0][1];
		H[1][0] = Hav[1][0]; H[1][1] = Hav[1][1];
	}
	
	
	
	
	double steps[4] = {step[0],step[1],1.0,1.0}; 
	
	for(i=0; i<maxiter; i++)
	{
		
		psiold[0] = psi[0] ; psiold[1] = psi[1];
		
		
		
		
		SOMatVecProd(H,psi,dtau); dtau[0] = -dtau[0]; dtau[1] = -dtau[1];
		
		
		
		
		
		
		if( ((i+1) % 10) == 0 )
		{
			Hfit(taui, psii, tau, dtau, psi, H, (i+1));
		}
		
		dtaul = SOVecNorm(dtau);
		if (dtaul > steps[0]){steps[3] = steps[0]/dtaul;}else{steps[3] = 1.0;};
		
		taudtau[0] = (tau[0] + steps[3]*dtau[0]); taudtau[1] = (tau[1] + steps[3]*dtau[1]); 
		
		SOGradPsi(seqarrays, taudtau, psi, torecip, toreal);
		if ((fabs(psi[0] - psiold[0])/fabs(psiold[0])) < step[3]){break;};
		
		psii[2*i] = psi[0]; psii[2*i+1] = psi[1];
		
		psil = SOVecNorm(psi);
		
		if (psil < psilmin)
		{
			
			if (taudtau[0] > 0.0 && taudtau[1] > 0.0)
			{
				taumin[0] = taudtau[0]; taumin[1] = taudtau[1]; 
			}
			psilmin = psil;
			
		}
		
		tau[0] = taudtau[0]; tau[1] = taudtau[1];
		
		taui[2*i] = tau[0]; taui[2*i+1] = tau[1];
		
		
		
		if (psil/psil0<step[2]){break;}; 
		
		y[0] = psiold[0] - psi[0]; y[1] = psiold[1] - psi[1]; 
		SOH( seqarrays, torecip, toreal, H,y,dtau,steps);
    }
	
	if (i == maxiter)
	{
		tau[0] = taumin[0]; tau[1] = taumin[1]; 
		psil=psilmin;
		if (psil/psil0 > step[4])
		{
			
			tau[0] = alpha;
			tau[1] = beta;
		}
	}
	else
	{
		
		
		
		
		if (tau[0]<0.0 || tau[1]<0.0)
		{
			tau[0] = taumin[0]; tau[1] = taumin[1]; 
		}
	}
	taul = SOVecNorm(tau);
	if (taul*taul > step[5]*step[5]){tau[0] = fabs(step[5]*tau[0]/taul);tau[1] = fabs(step[5]*tau[1]/taul);};
	
	
	
	tauav[0] = (tauav[0]*nav + fabs(tau[0]))/(nav + 1.0);
	tauav[1] = (tauav[1]*nav + fabs(tau[1]))/(nav + 1.0);
	Hav[0][0] = (Hav[0][0]*nav + H[0][0])/(nav + 1.0);
	Hav[0][1] = (Hav[0][1]*nav + H[0][1])/(nav + 1.0);
	Hav[1][0] = (Hav[1][0]*nav + H[1][0])/(nav + 1.0);
	Hav[1][1] = (Hav[1][1]*nav + H[1][1])/(nav + 1.0);
	if (nav < navlen){nav += 1.0;};
	free(taui);
	free(psii);
}

void SOGradStep
(
	SeqArrayObjects* seqarrays
)
{
	double* rho = seqarrays->seqdata;
	double* support = seqarrays->support;
	double* rho_m1 = seqarrays->rho_m1;
	double* rho_m2 = seqarrays->rho_m2;
	double* grad = seqarrays->tmparray1;
	double* step = seqarrays->tmparray2;
	int32_t* nn = seqarrays->nn;
	int32_t* citer_flow = seqarrays->citer_flow;
	int startiter = seqarrays->startiter;
	
	
	int64_t len =  nn[0] * nn[1] * nn[2];
	int64_t i;
	if (step[6] >= 0 && step[6] < (citer_flow[0] - startiter))
	{
		for(i=0; i<len; i++)
		{
			if (support[2*i] > 1e-6)
			{
				
				grad[2*i] = wLGradS(&rho[2*i], &rho_m1[2*i], &rho_m2[2*i], 0);
				grad[2*i+1] = wLGradS(&rho[2*i], &rho_m1[2*i], &rho_m2[2*i], 1);
			}
			else
			{
				
				grad[2*i] = wLGradnS(&rho[2*i], &rho_m1[2*i], &rho_m2[2*i], 0);
				grad[2*i+1] = wLGradnS(&rho[2*i], &rho_m1[2*i], &rho_m2[2*i], 1);
				
			}
		}
	}
	else
	{
		for(i=0; i<len; i++)
		{
			if (support[2*i] > 1e-6)
			{
				
				
				
				grad[2*i] = LGradS(&rho[2*i], &rho_m1[2*i], 0);
				grad[2*i+1] = LGradS(&rho[2*i], &rho_m1[2*i], 1);
			}
			else
			{
				
				
				
				grad[2*i] = LGradnS(&rho[2*i], &rho_m1[2*i], 0);
				grad[2*i+1] = LGradnS(&rho[2*i], &rho_m1[2*i], 1);
				
			}
		}
	}
}

void SupportScaleArray
(
	SeqArrayObjects* seqarrays,
	double* tau,
	double Sfactor,
	double nSfactor
)
{
	double* seqdata = seqarrays->seqdata;
	double* support = seqarrays->support;
	double* grad = seqarrays->tmparray1;
	int32_t* nn = seqarrays->nn;
	
	int64_t len =  (int64_t) nn[0] * nn[1] * nn[2];
    int64_t i;

    for(i=0; i<len; i++)
	{
		if ( support[2*i] > 1e-6 )
		{
			seqdata[2*i] = Sfactor*tau[0]*grad[2*i];
			seqdata[2*i+1] = Sfactor*tau[0]*grad[2*i+1];
		}
		else
		{
			seqdata[2*i] = nSfactor*tau[1]*grad[2*i]; 
			seqdata[2*i+1] = nSfactor*tau[1]*grad[2*i+1];
		}
	}
}

void SupportScaleAddArray
(
	SeqArrayObjects* seqarrays,
	double* tau,
	double Sfactor,
	double nSfactor
)
{
	double* seqdata = seqarrays->seqdata;
	double* support = seqarrays->support;
	double* rho_m1 = seqarrays->rho_m1;
	double* rho_m2 = seqarrays->rho_m2;
	double* grad = seqarrays->tmparray1;
	double* step = seqarrays->tmparray2;
	int32_t* nn = seqarrays->nn;
	int32_t* citer_flow = seqarrays->citer_flow;
	int startiter = seqarrays->startiter;
	
	int64_t len =  (int64_t) nn[0] * nn[1] * nn[2];
    int64_t i;
	
	double ampT;
	
	if (step[6] >= 0 && step[6] < (citer_flow[0] - startiter))
	{
		for(i=0; i<len; i++)
		{
			ampT = sqrt(rho_m2[2*i]*rho_m2[2*i] + rho_m2[2*i+1]*rho_m2[2*i+1]);
			if ( support[2*i] > 1e-6 )
			{
				seqdata[2*i] = rho_m1[2*i] + Sfactor*tau[0]*grad[2*i]*ampT;
				seqdata[2*i+1] = rho_m1[2*i+1] + Sfactor*tau[0]*grad[2*i+1]*ampT;
			}
			else
			{
				seqdata[2*i] = rho_m1[2*i] + nSfactor*tau[1]*(grad[2*i]*ampT - (1.0-ampT)*rho_m1[2*i] ); 
				seqdata[2*i+1] = rho_m1[2*i+1] + nSfactor*tau[1]*(grad[2*i+1]*ampT - (1.0-ampT)*rho_m1[2*i+1] );
			}
		}
	}
	else
	{
		for(i=0; i<len; i++)
		{
			if ( support[2*i] > 1e-6 )
			{
				seqdata[2*i] = rho_m1[2*i] + Sfactor*tau[0]*grad[2*i];
				seqdata[2*i+1] = rho_m1[2*i+1] + Sfactor*tau[0]*grad[2*i+1];
			}
			else
			{
				seqdata[2*i] = rho_m1[2*i] + nSfactor*tau[1]*grad[2*i]; 
				seqdata[2*i+1] = rho_m1[2*i+1] + nSfactor*tau[1]*grad[2*i+1];
			}
		}
	}
}

void MaskedSetAmplitudesZero
(
	SeqArrayObjects* seqarrays
)
{
	double* seqdata = seqarrays->seqdata;
	double* expdata = seqarrays->expdata;
	double* mask = seqarrays->mask;
	int32_t* nn = seqarrays->nn;
	
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
		else
		{
			seqdata[2*i] = 0.0;
			seqdata[2*i+1] = 0.0;
		}
	}
}

void SO2D
(
	SeqObjects* seqobs,
	SeqArrayObjects* seqarrays
)
{
	Py_BEGIN_ALLOW_THREADS;
	
	double* residual = seqobs->residual;
	int32_t* citer_flow = seqobs->citer_flow;
	double* visual_amp_real = seqobs->visual_amp_real;
	double* visual_phase_real = seqobs->visual_phase_real;
	double* visual_amp_recip = seqobs->visual_amp_recip;
	double* visual_phase_recip = seqobs->visual_phase_recip;
	PyObject* updatereal = seqobs->updatereal;
	PyObject* updaterecip = seqobs->updaterecip;
	PyObject* updatelog = seqobs->updatelog;
	int startiter = seqobs->startiter;
	int numiter = seqobs->numiter;
	
	double* seqdata = seqarrays->seqdata;
	double* expdata = seqarrays->expdata;
	double* mask = seqarrays->mask;
	double* epsilon = seqarrays->epsilon;
	double* rho_m1 = seqarrays->rho_m1;
	double* rho_m2 = seqarrays->rho_m2;
	int32_t* nn = seqarrays->nn;
	int ndim = seqarrays->ndim;
	
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
	
	double psi[2] = {0.0,0.0};
	double H[2][2] = {{0.0}};
	double Hav[2][2] = {{0.0}};
	double tau[2] = {0.0,0.0};
	double tauav[2] = {0.0,0.0}; 
	int algiter = 0; 
	
	int64_t len =  nn[0] * nn[1] * nn[2];
	
	
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
		
		
		SOGradStep(seqarrays);
		
		SOMinMaxtau(seqobs,seqarrays,tau,tauav,H,Hav,psi,algiter,&torecip,&toreal);
		algiter += 1;
		
		epsilon[1] = sqrt(psi[0]*psi[0]+psi[1]*psi[1])/((double) len);
		
		epsilon[2] = tau[0]; epsilon[3] = tau[1];
		
		
		SupportScaleAddArray(seqarrays, tau, 1.0, 1.0);
		
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

