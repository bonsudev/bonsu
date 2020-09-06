#############################################
##   Filename: ER.py
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
def ER\
	(
		parent,
		startiter,
		numiter
	):
	from bonsu.phasing.ER import ER
	er = ER(parent)
	er.SetStartiter(startiter)
	er.SetNumiter(numiter)
	er.Prepare()
	er.Start()
	er.CleanData()
def ERMask\
	(
		parent,
		startiter,
		numiter,
		numiter_relax
	):
	from bonsu.phasing.ER import ERMask
	er = ERMask(parent)
	er.SetStartiter(startiter)
	er.SetNumiter(numiter)
	er.Prepare()
	er.Start()
	er.CleanData()
def ERMaskPC\
	(
	parent,
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
	from bonsu.phasing.ER import ERMaskPC
	er = ERMaskPC(parent)
	er.SetStartiter(startiter)
	er.SetNumiter(numiter)
	er.SetNumiterRLpre(niterrlpre)
	er.SetNumiterRL(niterrl)
	er.SetNumiterRLinterval(niterrlinterval)
	er.SetGammaHWHM(gammaHWHM)
	er.SetPSFZeroEnd([zex,zey,zez])
	er.SetResetGamma(reset_gamma)
	er.SetAccel(accel)
	er.Prepare()
	er.Start()
	er.CleanData()
