#############################################
##   Filename: compact.py
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
import numpy
def CompactArray(array, amp):
	dims = array.shape
	if array.shape[2] == 1:
		pass
	else:
		x_yz = numpy.ones((2,dims[1],dims[2]), dtype=numpy.int)
		x_yz[0,:,:] = dims[0] # low set to highest
		x_yz[1,:,:] = 0 # high set to low
		y_xz = numpy.ones((2,dims[0],dims[2]), dtype=numpy.int)
		y_xz[0,:,:] = dims[1] # low set to highest
		y_xz[1,:,:] = 0 # high set to low
		z_xy = numpy.ones((2,dims[0],dims[1]), dtype=numpy.int)
		z_xy[0,:,:] = dims[2] # low set to highest
		z_xy[1,:,:] = 0 # high set to low
		#
		for xi in numpy.ndindex(dims):
			if (array[xi[0]][xi[1]][xi[2]] > 1e-6):
				if (xi[0] < x_yz[0][xi[1]][xi[2]] ):
					x_yz[0][xi[1]][xi[2]] = xi[0]
				if (xi[0] > x_yz[1][xi[1]][xi[2]] ):
					x_yz[1][xi[1]][xi[2]] = xi[0]
				#
				if (xi[1] < y_xz[0][xi[0]][xi[2]] ):
					y_xz[0][xi[0]][xi[2]] = xi[1]
				if (xi[1] > y_xz[1][xi[0]][xi[2]] ):
					y_xz[1][xi[0]][xi[2]] = xi[1]
				#
				if (xi[2] < z_xy[0][xi[0]][xi[1]] ):
					z_xy[0][xi[0]][xi[1]] = xi[2]
				if (xi[2] > z_xy[1][xi[0]][xi[1]] ):
					z_xy[1][xi[0]][xi[1]] = xi[2]
		#
		for xi in numpy.ndindex(dims):
			if (xi[0] > x_yz[0][xi[1]][xi[2]] and xi[0] < x_yz[1][xi[1]][xi[2]]) or\
				 (xi[1] > y_xz[0][xi[0]][xi[2]] and xi[1] < y_xz[1][xi[0]][xi[2]]) or\
				 (xi[2] > z_xy[0][xi[0]][xi[1]] and xi[2] < z_xy[1][xi[0]][xi[1]]):
				array[xi[0]][xi[1]][xi[2]] = amp
