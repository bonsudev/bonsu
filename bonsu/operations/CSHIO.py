#############################################
##   Filename: CSHIO.py
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
import wx
import sys
import os
import numpy
from .wrap import WrapArray
from .loadarray import NewArray
def CSHIO\
	(
		parent,
		beta,
		startiter,
		numiter,
		cs_p,
		cs_epsilon,
		cs_epsilon_min,
		cs_d,
		cs_eta,
		relax
	):
	from bonsu.phasing.CSHIO import CSHIO
	cshio = CSHIO(parent)
	cshio.SetStartiter(startiter)
	cshio.SetNumiter(numiter)
	cshio.SetBeta(beta)
	cshio.SetPnorm(cs_p)
	cshio.SetEpsilon(cs_epsilon)
	cshio.SetEpsilonmin(cs_epsilon_min)
	cshio.SetDivisor(cs_d)
	cshio.SetEta(cs_eta)
	cshio.SetRelax(relax)
	cshio.Prepare()
	cshio.Start()
	cshio.CleanData()
