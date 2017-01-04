#############################################
##   Filename: wrap.py
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
def WrapArray2(array):
	if array.shape[2] == 1:
		b1 = numpy.array_split( numpy.array_split( array, 2, axis=0 )[0], 2, axis=1 )[0]
		b2 = numpy.array_split( numpy.array_split( array, 2, axis=0 )[0], 2, axis=1 )[1]
		b3 = numpy.array_split( numpy.array_split( array, 2, axis=0 )[1], 2, axis=1 )[0]
		b4 = numpy.array_split( numpy.array_split( array, 2, axis=0 )[1], 2, axis=1 )[1]
		v1 = numpy.vstack((b4,b2))
		v2 = numpy.vstack((b3,b1))
		arrayfinal = numpy.array(numpy.hstack((v1,v2)), dtype=numpy.cdouble, copy=True, order='C')
		return arrayfinal
	else:
		b1 = numpy.array_split( numpy.array_split( numpy.array_split( array, 2, axis=0 )[0], 2, axis=1 )[0], 2, axis=2 )[0]
		b2 = numpy.array_split( numpy.array_split( numpy.array_split( array, 2, axis=0 )[0], 2, axis=1 )[0], 2, axis=2 )[1]
		b3 = numpy.array_split( numpy.array_split( numpy.array_split( array, 2, axis=0 )[0], 2, axis=1 )[1], 2, axis=2 )[0]
		b4 = numpy.array_split( numpy.array_split( numpy.array_split( array, 2, axis=0 )[0], 2, axis=1 )[1], 2, axis=2 )[1]
		b5 = numpy.array_split( numpy.array_split( numpy.array_split( array, 2, axis=0 )[1], 2, axis=1 )[0], 2, axis=2 )[0]
		b6 = numpy.array_split( numpy.array_split( numpy.array_split( array, 2, axis=0 )[1], 2, axis=1 )[0], 2, axis=2 )[1]
		b7 = numpy.array_split( numpy.array_split( numpy.array_split( array, 2, axis=0 )[1], 2, axis=1 )[1], 2, axis=2 )[0]
		b8 = numpy.array_split( numpy.array_split( numpy.array_split( array, 2, axis=0 )[1], 2, axis=1 )[1], 2, axis=2 )[1]
		v1 = numpy.vstack((b8,b4))
		v2 = numpy.vstack((b7,b3))
		v3 = numpy.vstack((b6,b2))
		v4 = numpy.vstack((b5,b1))
		h1 = numpy.hstack((v1,v3))
		h2 = numpy.hstack((v2,v4))
		arrayfinal = numpy.array(numpy.dstack((h1,h2)), dtype=numpy.cdouble, copy=True, order='C')
		return arrayfinal
def WrapArrayAmp(array):
	if array.shape[2] == 1:
		b1 = numpy.array_split( numpy.array_split( array, 2, axis=0 )[0], 2, axis=1 )[0]
		b2 = numpy.array_split( numpy.array_split( array, 2, axis=0 )[0], 2, axis=1 )[1]
		b3 = numpy.array_split( numpy.array_split( array, 2, axis=0 )[1], 2, axis=1 )[0]
		b4 = numpy.array_split( numpy.array_split( array, 2, axis=0 )[1], 2, axis=1 )[1]
		v1 = numpy.vstack((b4,b2))
		v2 = numpy.vstack((b3,b1))
		arrayfinal = numpy.array(numpy.hstack((v1,v2)), dtype=numpy.double, copy=True, order='C')
		return arrayfinal
	else:
		b1 = numpy.array_split( numpy.array_split( numpy.array_split( array, 2, axis=0 )[0], 2, axis=1 )[0], 2, axis=2 )[0]
		b2 = numpy.array_split( numpy.array_split( numpy.array_split( array, 2, axis=0 )[0], 2, axis=1 )[0], 2, axis=2 )[1]
		b3 = numpy.array_split( numpy.array_split( numpy.array_split( array, 2, axis=0 )[0], 2, axis=1 )[1], 2, axis=2 )[0]
		b4 = numpy.array_split( numpy.array_split( numpy.array_split( array, 2, axis=0 )[0], 2, axis=1 )[1], 2, axis=2 )[1]
		b5 = numpy.array_split( numpy.array_split( numpy.array_split( array, 2, axis=0 )[1], 2, axis=1 )[0], 2, axis=2 )[0]
		b6 = numpy.array_split( numpy.array_split( numpy.array_split( array, 2, axis=0 )[1], 2, axis=1 )[0], 2, axis=2 )[1]
		b7 = numpy.array_split( numpy.array_split( numpy.array_split( array, 2, axis=0 )[1], 2, axis=1 )[1], 2, axis=2 )[0]
		b8 = numpy.array_split( numpy.array_split( numpy.array_split( array, 2, axis=0 )[1], 2, axis=1 )[1], 2, axis=2 )[1]
		v1 = numpy.vstack((b8,b4))
		v2 = numpy.vstack((b7,b3))
		v3 = numpy.vstack((b6,b2))
		v4 = numpy.vstack((b5,b1))
		h1 = numpy.hstack((v1,v3))
		h2 = numpy.hstack((v2,v4))
		arrayfinal = numpy.array(numpy.dstack((h1,h2)), dtype=numpy.double, copy=True, order='C')
		return arrayfinal
def WrapArray(array, direction=1):
	from ..lib.prfftw import wrap
	wrap(array, direction)
	return array
