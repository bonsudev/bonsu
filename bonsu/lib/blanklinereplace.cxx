/*
#############################################
##   Filename: blanklinereplace.cxx
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


void BlankLineReplace
( 
	double* data1, 
	double* data2, 
	int32_t* nn,
	int32_t k_x,
	int32_t k_y,
	int32_t k_z,
	int32_t x1, int32_t x2,
	int32_t y1, int32_t y2,
	int32_t z1, int32_t z2
)
{
	int32_t i,j,k,mx,my,mz;
	int32_t x,y,z;
	uint64_t index;
	double ksum = 0.0;
	double kcount = 0.0;
	double kvalue = 0.0;
	
	z2 = z2+1;
	y2 = y2+1;
	x2 = x2+1;
	
	k_x = ((abs(k_x) - 1)/2)*2 +1;
	k_y = ((abs(k_y) - 1)/2)*2 +1;
	k_z = ((abs(k_z) - 1)/2)*2 +1;
	
	for(z=z1; z < z2; z++)
	{
		for(y=y1; y < y2; y++)
		{
			for(x=x1; x < x2; x++)
			{
				ksum = 0.0;
				kcount = 0.0;
				kvalue = 0.0;
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
							kvalue = sqrt(data1[2*index] * data1[2*index] + data1[2*index+1] * data1[2*index+1]);

							ksum += kvalue;
							kcount += 1.0;

						}
					}
				}
				index = (z+(nn[2])*(y+(nn[1])*x));
				if( kcount < 1.0 )
				{
					data2[2*index] = 0.0;
					data2[2*index+1] = 0.0;
				}
				else
				{
					data2[2*index] = ksum/kcount;
					data2[2*index+1] = 0.0;
				}
			}
		}
	}
	
	for(z=z1; z < z2; z++)
	{
		for(y=y1; y < y2; y++)
		{
			for(x=x1; x < x2; x++)
			{
				index = (z+(nn[2])*(y+(nn[1])*x));
				data1[2*index] = data2[2*index];
				data1[2*index+1] = data2[2*index+1];
			}
		}
	}
}
