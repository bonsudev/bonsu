#############################################
##   Filename: RAAR.py
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
def RAAR\
	(
		parent,
		beta,
		startiter,
		numiter,
		numiter_relax
	):
	from bonsu.phasing.RAAR import RAAR
	raar = RAAR(parent)
	raar.SetStartiter(startiter)
	raar.SetNumiter(numiter)
	raar.SetNumiterRelax(numiter_relax)
	raar.SetBeta(beta)
	raar.Prepare()
	raar.Start()
	raar.CleanData()
def RAARMaskPC\
	(
	parent,
	beta,
	startiter,
	numiter,
	niterrlpre,
	niterrl,
	niterrlinterval,
	gammaHWHM,
	zex, zey, zez,
	reset_gamma,
	accel
	):
	from bonsu.phasing.RAAR import RAARPC
	raar = RAARPC(parent)
	raar.SetStartiter(startiter)
	raar.SetNumiter(numiter)
	raar.SetNumiterRLpre(niterrlpre)
	raar.SetNumiterRL(niterrl)
	raar.SetNumiterRLinterval(niterrlinterval)
	raar.SetGammaHWHM(gammaHWHM)
	raar.SetPSFZeroEnd([zex,zey,zez])
	raar.SetResetGamma(reset_gamma)
	raar.SetAccel(accel)
	raar.SetBeta(beta)
	raar.Prepare()
	raar.Start()
	raar.CleanData()
