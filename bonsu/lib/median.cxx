/*
#############################################
##   Filename: median.cxx
##
##    Copyright (C) 2015 Marcus C. Newton
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
#include <stdlib.h>
#include "prfftwmodule.h"


void MedianReplaceVoxel
(
	double* data1, 
	double* data2, 
	int32_t* nn,
	int32_t k_x,
	int32_t k_y,
	int32_t k_z,
	double maxerr
)
{
	int64_t len = (int64_t) nn[0] * nn[1] * nn[2];
	int64_t i;
	double amp1, amp2, err;
	MedianFilter( data1, data2, nn, k_x, k_y, k_z );
	for(i=0; i<len; i++)
	{
		amp1 = sqrt(data1[2*i] * data1[2*i] + data1[2*i+1] * data1[2*i+1]);
		amp2 = sqrt(data2[2*i] * data2[2*i] + data2[2*i+1] * data2[2*i+1]);
		err = fabs(amp2 - amp1)/amp1;
		if (err > maxerr)
		{
			data1[2*i] = data2[2*i];
			data1[2*i+1] = data2[2*i+1];
		}
	}
}


int Compare (const void *X, const void *Y)
{
	   double x = *((double *)X);
	   double y = *((double *)Y);

	   if (x > y)
	   {
		   return 1;
	   }
	   else
	   {
		   if (x < y)
		   {
			   return -1;
		   }
		   else
		   {
			   return 0;
		   }
	   }
}

void MedianFilter
( 
	double* data1, 
	double* data2, 
	int32_t* nn,
	int32_t k_x,
	int32_t k_y,
	int32_t k_z  
)
{
	double* k_array = (double*) malloc((k_x*k_y*k_z) * sizeof(double));
	uint32_t n=0;
	int32_t i,j,k,mx,my,mz;
	int32_t x,y,z;
	uint64_t index;
	double phase;
		
	k_x = ((abs(k_x) - 1)/2)*2 +1;
	k_y = ((abs(k_y) - 1)/2)*2 +1;
	k_z = ((abs(k_z) - 1)/2)*2 +1;
	
	for(z=0; z < nn[2]; z++)
	{
		for(y=0; y < nn[1]; y++)
		{
			for(x=0; x < nn[0]; x++)
			{
				n=0;
				for(k=0; k < k_z; k++)
				{
					for(j=0; j < k_y; j++)
					{
						for(i=0; i < k_x; i++)
						{
							mx = x + i - k_x/2;
							my = y + j - k_y/2;
							mz = z + k - k_z/2;
							if(mx < 0) mx = 0;
							if(mx > (nn[0] -1)) mx = (nn[0] -1);
							if(my < 0) my = 0;
							if(my > (nn[1] -1)) my = (nn[1] -1);
							if(mz < 0) mz = 0;
							if(mz > (nn[2] -1)) mz = (nn[2] -1);
							
							index = (mz+(nn[2])*(my+(nn[1])*mx));
							k_array[n] = sqrt(data1[2*index] * data1[2*index] + data1[2*index+1] * data1[2*index+1]);
							n++;
						}
					}
				}
				/* find median value */
				index = (z+(nn[2])*(y+(nn[1])*x));
				qsort(k_array,(k_x*k_y*k_z),sizeof(double),Compare);
				/* pass back  */
				phase = atan2(data1[2*index+1], data1[2*index]);
				data2[2*index] = (k_array[k_x*k_y*k_z/2]) * cos(phase);
				data2[2*index+1] = (k_array[k_x*k_y*k_z/2]) * sin(phase);
			}
		}
	}
	free(k_array);
}
