#############################################
##   Filename: HPR.py
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
def HPR\
	(
		parent,
		beta,
		startiter,
		numiter,
		numiter_relax
	):
	from bonsu.phasing.HPR import HPR
	hpr = HPR(parent)
	hpr.SetStartiter(startiter)
	hpr.SetNumiter(numiter)
	hpr.SetNumiterRelax(numiter_relax)
	hpr.SetBeta(beta)
	hpr.Prepare()
	hpr.Start()
	hpr.CleanData()
def HPRMaskPC\
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
	from bonsu.phasing.HPR import HPRPC
	hpr = HPRPC(parent)
	hpr.SetStartiter(startiter)
	hpr.SetNumiter(numiter)
	hpr.SetNumiterRLpre(niterrlpre)
	hpr.SetNumiterRL(niterrl)
	hpr.SetNumiterRLinterval(niterrlinterval)
	hpr.SetGammaHWHM(gammaHWHM)
	hpr.SetPSFZeroEnd([zex,zey,zez])
	hpr.SetResetGamma(reset_gamma)
	hpr.SetAccel(accel)
	hpr.SetBeta(beta)
	hpr.Prepare()
	hpr.Start()
	hpr.CleanData()
