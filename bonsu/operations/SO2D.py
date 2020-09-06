#############################################
##   Filename: SO2D.py
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
def SO2D\
	(
		parent,
		alpha,
		beta,
		startiter,
		numiter,
		numsoiter,
		reweightiter,
		dtaumax,
		dtaumin,
		psiexitratio,
		psiexiterror,
		psiresetratio,
		taumax
	):
	from ..phasing.SO2D import SO2D
	so2d = SO2D(parent)
	so2d.SetStartiter(startiter)
	so2d.SetNumiter(numiter)
	so2d.SetNumsoiter(numsoiter)
	so2d.SetReweightiter(reweightiter)
	so2d.SetDtaumax(dtaumax)
	so2d.SetDtaumin(dtaumin)
	so2d.SetPsiexitratio(psiexitratio)
	so2d.SetPsiexiterror(psiexiterror)
	so2d.SetPsiresetratio(psiresetratio)
	so2d.SetTaumax(taumax)
	so2d.Prepare()
	so2d.Start()
	so2d.CleanData()
	return so2d.epsilon[2],so2d.epsilon[3]
