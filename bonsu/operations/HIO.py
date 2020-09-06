#############################################
##   Filename: HIO.py
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
def HIO\
	(
		parent,
		beta,
		startiter,
		numiter
	):
	from bonsu.phasing.HIO import HIO
	hio = HIO(parent)
	hio.SetStartiter(startiter)
	hio.SetNumiter(numiter)
	hio.SetBeta(beta)
	hio.Prepare()
	hio.Start()
	hio.CleanData()
def HIOMask\
	(
		parent,
		beta,
		startiter,
		numiter,
		numiter_relax
	):
	from bonsu.phasing.HIO import HIOMask
	hio = HIOMask(parent)
	hio.SetStartiter(startiter)
	hio.SetNumiter(numiter)
	hio.SetNumiterRelax(numiter_relax)
	hio.SetBeta(beta)
	hio.Prepare()
	hio.Start()
	hio.CleanData()
def HIOPlus\
	(
		parent,
		beta,
		startiter,
		numiter
	):
	from bonsu.phasing.HIO import HIOPlus
	hio = HIOPlus(parent)
	hio.SetStartiter(startiter)
	hio.SetNumiter(numiter)
	hio.SetBeta(beta)
	hio.Prepare()
	hio.Start()
	hio.CleanData()
def PCHIO\
	(
		parent,
		beta,
		startiter,
		numiter,
		phasemax,
		phasemin
	):
	from bonsu.phasing.HIO import PCHIO
	hio = PCHIO(parent)
	hio.SetStartiter(startiter)
	hio.SetNumiter(numiter)
	hio.SetMaxphase(phasemax)
	hio.SetMinphase(phasemin)
	hio.SetBeta(beta)
	hio.Prepare()
	hio.Start()
	hio.CleanData()
def PGCHIO\
	(
		parent,
		beta,
		startiter,
		numiter,
		phasemax,
		phasemin,
		qx,
		qy,
		qz
	):
	from bonsu.phasing.HIO import PGCHIO
	hio = PGCHIO(parent)
	hio.SetStartiter(startiter)
	hio.SetNumiter(numiter)
	hio.SetMaxphase(phasemax)
	hio.SetMinphase(phasemin)
	hio.SetBeta(beta)
	hio.SetQ([qx,qy,qz])
	hio.Prepare()
	hio.Start()
	hio.CleanData()
def HIOMaskPC\
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
	from bonsu.phasing.HIO import HIOMaskPC
	hio = HIOMaskPC(parent)
	hio.SetStartiter(startiter)
	hio.SetNumiter(numiter)
	hio.SetNumiterRLpre(niterrlpre)
	hio.SetNumiterRL(niterrl)
	hio.SetNumiterRLinterval(niterrlinterval)
	hio.SetGammaHWHM(gammaHWHM)
	hio.SetPSFZeroEnd([zex,zey,zez])
	hio.SetResetGamma(reset_gamma)
	hio.SetAccel(accel)
	hio.SetBeta(beta)
	hio.Prepare()
	hio.Start()
	hio.CleanData()
