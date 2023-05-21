#############################################
##   Filename: instance.py
##
##    Copyright (C) 2011 - 2023 Marcus C. Newton
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
import gzip
import pickle
import os
import sys
import inspect
from .subpanel import *
def NewInstance(self):
	panelphase = self.GetChildren()[1].GetPage(0)
	if panelphase.pipeline_started == False:
		print( "Creating new sequence ..." )
		for  i in range(len(panelphase.pipelineitems)):
			panelphase.pipelineitems[i].Hide()
		panelphase.menu_place_holder.Show()
		panelphase.memory = {}
		panelvisual = self.GetChildren()[1].GetPage(1)
		panelvisual.data = None
		panelvisual.flat_data = None
		panelvisual.flat_data2 = None
		panelvisual.flat_data_phase = None
		panelvisual.measure_data[0] = None
		panelvisual.measure_data[1][0] = None
		panelvisual.measure_data[1][1] = None
		panelvisual.measure_data[2] = None
		panelvisual.measure_data[3][0] = None
		panelvisual.measure_data[3][1] = None
		panelvisual.measure_data[3][2] = None
		panelscript = self.GetChildren()[1].GetPage(3)
		for k in panelscript.shell.interp.locals:
			panelscript.shell.interp.locals[k] = None
		panelscript.shell.interp.locals = {}
		try:
			panelphase.mainlist.DeleteAllItems()
		except:
			print( "Could not empty Main List" )
		try:
			panelphase.pipelineitems = []
		except:
			print( "Could not empty pipeline" )
		try:
			panelphase.seqdata = None
		except:
			print( "Could not delete sequence data" )
		try:
			panelphase.expdata = None
		except:
			print( "Could not delete experiment data" )
		try:
			panelphase.mask = None
		except:
			print( "Could not delete mask data" )
		try:
			panelphase.support= None
		except:
			print( "Could not delete support data" )
		try:
			panelphase.psf = None
		except:
			print( "Could not delete point spread function data" )
		try:
			panelphase.residual = None
		except:
			print( "Could not delete residual data" )
		try:
			panelphase.coordarray = None
		except:
			print( "Could not delete Co-ordinate data" )
		try:
			panelphase.visual_amp_real = None
		except:
			print( "Could not delete visual real data amp" )
		try:
			panelphase.visual_phase_real = None
		except:
			print( "Could not delete visual real data phase" )
		try:
			panelphase.visual_support = None
		except:
			print( "Could not delete visual support" )
		try:
			panelphase.visual_amp_recip = None
		except:
			print( "Could not delete visual reciprocal data amp" )
		try:
			panelphase.visual_phase_recip = None
		except:
			print( "Could not delete visual reciprocal data phase" )
		panelphase.compile = 1
		import gc
		gc.collect()
def GetInstanceObject(panelphase, i):
	mainlist = panelphase.mainlist.GetItem(i,1).GetText()
	object = []
	subpanelname = panelphase.pipelineitems[i].treeitem['name']
	if subpanelname == 'Python Script':
		object.append( panelphase.pipelineitems[i].txt.GetValue() )
	if subpanelname == 'Comments':
		object.append( panelphase.pipelineitems[i].txt.GetValue() )
	if subpanelname == 'Blank Line Fill':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].kdims[0].value.GetValue() )
		object.append( panelphase.pipelineitems[i].kdims[1].value.GetValue() )
		object.append( panelphase.pipelineitems[i].kdims[2].value.GetValue() )
	if subpanelname == 'Scale Array':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].scale.value.GetValue() )
	if subpanelname == 'SumDiff Array':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].input_filename1.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].addsub.GetStringSelection() )
	if subpanelname == 'Rotate Support':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].rotationaxis.value.GetValue() )
		object.append( panelphase.pipelineitems[i].rotationangle.value.GetValue() )
	if subpanelname == 'Transpose Array':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
	if subpanelname == 'SPE to Numpy':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
	if subpanelname == 'Image to Numpy':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
	if subpanelname == 'Crop Pad':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].csdims[0].value.GetValue() )
		object.append( panelphase.pipelineitems[i].csdims[1].value.GetValue() )
		object.append( panelphase.pipelineitems[i].csdims[2].value.GetValue() )
		object.append( panelphase.pipelineitems[i].cedims[0].value.GetValue() )
		object.append( panelphase.pipelineitems[i].cedims[1].value.GetValue() )
		object.append( panelphase.pipelineitems[i].cedims[2].value.GetValue() )
		object.append( panelphase.pipelineitems[i].psdims[0].value.GetValue() )
		object.append( panelphase.pipelineitems[i].psdims[1].value.GetValue() )
		object.append( panelphase.pipelineitems[i].psdims[2].value.GetValue() )
		object.append( panelphase.pipelineitems[i].pedims[0].value.GetValue() )
		object.append( panelphase.pipelineitems[i].pedims[1].value.GetValue() )
		object.append( panelphase.pipelineitems[i].pedims[2].value.GetValue() )
	if subpanelname == 'Mask':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].max.value.GetValue() )
		object.append( panelphase.pipelineitems[i].min.value.GetValue() )
	if subpanelname == 'Threshold Data':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].max.value.GetValue() )
		object.append( panelphase.pipelineitems[i].min.value.GetValue() )
	if subpanelname == 'Bin':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].bdims[0].value.GetValue() )
		object.append( panelphase.pipelineitems[i].bdims[1].value.GetValue() )
		object.append( panelphase.pipelineitems[i].bdims[2].value.GetValue() )
	if subpanelname == 'Auto Centre':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
	if subpanelname == 'Centred Resize':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].dims[0].value.GetValue() )
		object.append( panelphase.pipelineitems[i].dims[1].value.GetValue() )
		object.append( panelphase.pipelineitems[i].dims[2].value.GetValue() )
	if subpanelname == 'Wrap Data':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].rbdirection.GetStringSelection() )
	if subpanelname == 'HDF5 to Numpy':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
	if subpanelname == 'Array to VTK':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].rbampphase.GetStringSelection() )
	if subpanelname == 'Interpolate Object':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].coords_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].spacer[0].value.GetValue() )
		object.append( panelphase.pipelineitems[i].spacer[1].value.GetValue() )
		object.append( panelphase.pipelineitems[i].spacer[2].value.GetValue() )
		object.append( panelphase.pipelineitems[i].interp_range.value.GetValue() )
		object.append( panelphase.pipelineitems[i].bounds[0].value.GetValue() )
		object.append( panelphase.pipelineitems[i].bounds[1].value.GetValue() )
		object.append( panelphase.pipelineitems[i].bounds[2].value.GetValue() )
		object.append( panelphase.pipelineitems[i].bounds[3].value.GetValue() )
		object.append( panelphase.pipelineitems[i].bounds[4].value.GetValue() )
		object.append( panelphase.pipelineitems[i].bounds[5].value.GetValue() )
	if subpanelname == 'Affine Transform':
		object.append( panelphase.pipelineitems[i].coords_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].outputcoords_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].translate[0].value.GetValue() )
		object.append( panelphase.pipelineitems[i].translate[1].value.GetValue() )
		object.append( panelphase.pipelineitems[i].translate[2].value.GetValue() )
		object.append( panelphase.pipelineitems[i].scale[0].value.GetValue() )
		object.append( panelphase.pipelineitems[i].scale[1].value.GetValue() )
		object.append( panelphase.pipelineitems[i].scale[2].value.GetValue() )
		object.append( panelphase.pipelineitems[i].rotate[0].value.GetValue() )
		object.append( panelphase.pipelineitems[i].rotate[1].value.GetValue() )
		object.append( panelphase.pipelineitems[i].rotate[2].value.GetValue() )
	if subpanelname == 'Voxel Replace':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].sdims[0].value.GetValue() )
		object.append( panelphase.pipelineitems[i].sdims[1].value.GetValue() )
		object.append( panelphase.pipelineitems[i].sdims[2].value.GetValue() )
		object.append( panelphase.pipelineitems[i].edims[0].value.GetValue() )
		object.append( panelphase.pipelineitems[i].edims[1].value.GetValue() )
		object.append( panelphase.pipelineitems[i].edims[2].value.GetValue() )
		object.append( panelphase.pipelineitems[i].real.value.GetValue() )
		object.append( panelphase.pipelineitems[i].imag.value.GetValue() )
	if subpanelname == 'Conjugate Reflect':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
	if subpanelname == 'Gaussian Fill':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].sigma.value.GetValue() )
	if subpanelname == 'Fourier Transform':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].rbdirection.GetStringSelection() )
	if subpanelname == 'Convolve':
		object.append( panelphase.pipelineitems[i].input_filename1.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].input_filename2.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
	if subpanelname == 'Object to VTK':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].coords_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].rbampphase.GetStringSelection() )
	if subpanelname == 'Array to Memory':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
	if subpanelname == 'Memory to Array':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
	if subpanelname == 'Load PSF':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
	if subpanelname == 'Save PSF':
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
	if subpanelname == 'Median Filter':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].kdims[0].value.GetValue() )
		object.append( panelphase.pipelineitems[i].kdims[1].value.GetValue() )
		object.append( panelphase.pipelineitems[i].kdims[2].value.GetValue() )
		object.append( panelphase.pipelineitems[i].maxdev.value.GetValue() )
	if subpanelname == 'Cuboid Support' :
		object.append( panelphase.pipelineitems[i].filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].fromfile.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].dims[0].value.GetValue() )
		object.append( panelphase.pipelineitems[i].dims[1].value.GetValue() )
		object.append( panelphase.pipelineitems[i].dims[2].value.GetValue() )
		object.append( panelphase.pipelineitems[i].sdims[0].value.GetValue() )
		object.append( panelphase.pipelineitems[i].sdims[1].value.GetValue() )
		object.append( panelphase.pipelineitems[i].sdims[2].value.GetValue() )
	if subpanelname == 'Polyhedron Support' :
		object.append( panelphase.pipelineitems[i].filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].fromfile.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].dims[0].value.GetValue() )
		object.append( panelphase.pipelineitems[i].dims[1].value.GetValue() )
		object.append( panelphase.pipelineitems[i].dims[2].value.GetValue() )
		object.append( panelphase.pipelineitems[i].init_points.GetValue() )
		object.append( panelphase.pipelineitems[i].term_points.GetValue() )
	if subpanelname == 'Empty Array' :
		object.append( panelphase.pipelineitems[i].filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].fromfile.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].dims[0].value.GetValue() )
		object.append( panelphase.pipelineitems[i].dims[1].value.GetValue() )
		object.append( panelphase.pipelineitems[i].dims[2].value.GetValue() )
	if subpanelname == 'View Support':
		object.append( panelphase.pipelineitems[i].support.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].contour_support.value.GetValue() )
		object.append( panelphase.pipelineitems[i].contour.value.GetValue() )
		object.append( panelphase.pipelineitems[i].opacity.value.GetValue() )
		object.append( panelphase.pipelineitems[i].feature_angle.value.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_axes.GetValue() )
		object.append( panelphase.pipelineitems[i].axes_fontfactor.value.GetValue() )
	if subpanelname == 'Laxarus Viewer':
		object.append( panelphase.pipelineitems[i].filename.objectpath.GetValue() )
	if subpanelname == 'View Array':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].rbampphase.GetStringSelection() )
		object.append( panelphase.pipelineitems[i].contour.value.GetValue() )
		object.append( panelphase.pipelineitems[i].opacity.value.GetValue() )
		object.append( panelphase.pipelineitems[i].phasemax.value.GetValue() )
		object.append( panelphase.pipelineitems[i].phasemin.value.GetValue() )
		object.append( panelphase.pipelineitems[i].ox.value.GetValue() )
		object.append( panelphase.pipelineitems[i].oy.value.GetValue() )
		object.append( panelphase.pipelineitems[i].oz.value.GetValue() )
		object.append( panelphase.pipelineitems[i].nx.value.GetValue() )
		object.append( panelphase.pipelineitems[i].ny.value.GetValue() )
		object.append( panelphase.pipelineitems[i].nz.value.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_axes.GetValue() )
		object.append( panelphase.pipelineitems[i].feature_angle.value.GetValue() )
		object.append( panelphase.pipelineitems[i].sx.value.GetValue() )
		object.append( panelphase.pipelineitems[i].sy.value.GetValue() )
		object.append( panelphase.pipelineitems[i].sz.value.GetValue() )
		object.append( panelphase.pipelineitems[i].axes_fontfactor.value.GetValue() )
		object.append( panelphase.pipelineitems[i].meshsubiter.value.GetValue() )
	if subpanelname == 'View Object':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].coords_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].rbampphase.GetStringSelection() )
		object.append( panelphase.pipelineitems[i].contour.value.GetValue() )
		object.append( panelphase.pipelineitems[i].opacity.value.GetValue() )
		object.append( panelphase.pipelineitems[i].phasemax.value.GetValue() )
		object.append( panelphase.pipelineitems[i].phasemin.value.GetValue() )
		object.append( panelphase.pipelineitems[i].ox.value.GetValue() )
		object.append( panelphase.pipelineitems[i].oy.value.GetValue() )
		object.append( panelphase.pipelineitems[i].oz.value.GetValue() )
		object.append( panelphase.pipelineitems[i].nx.value.GetValue() )
		object.append( panelphase.pipelineitems[i].ny.value.GetValue() )
		object.append( panelphase.pipelineitems[i].nz.value.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_axes.GetValue() )
		object.append( panelphase.pipelineitems[i].feature_angle.value.GetValue() )
		object.append( panelphase.pipelineitems[i].axes_fontfactor.value.GetValue() )
		object.append( panelphase.pipelineitems[i].meshsubiter.value.GetValue() )
	if subpanelname == 'View VTK Array':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].rbampphase.GetStringSelection() )
		object.append( panelphase.pipelineitems[i].contour.value.GetValue() )
		object.append( panelphase.pipelineitems[i].feature_angle.value.GetValue() )
		object.append( panelphase.pipelineitems[i].phasemax.value.GetValue() )
		object.append( panelphase.pipelineitems[i].phasemin.value.GetValue() )
		object.append( panelphase.pipelineitems[i].ox.value.GetValue() )
		object.append( panelphase.pipelineitems[i].oy.value.GetValue() )
		object.append( panelphase.pipelineitems[i].oz.value.GetValue() )
		object.append( panelphase.pipelineitems[i].nx.value.GetValue() )
		object.append( panelphase.pipelineitems[i].ny.value.GetValue() )
		object.append( panelphase.pipelineitems[i].nz.value.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_axes.GetValue() )
		object.append( panelphase.pipelineitems[i].axes_fontfactor.value.GetValue() )
	if subpanelname == 'Random Start':
		object.append( panelphase.pipelineitems[i].amp_max.value.GetValue() )
	if subpanelname == 'Array Start':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
	if subpanelname == 'HIO':
		object.append( panelphase.pipelineitems[i].exp_amps.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_sqrt_expamps.GetValue() )
		object.append( panelphase.pipelineitems[i].support.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].beta.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niter.value.GetValue() )
	if subpanelname == 'ER':
		object.append( panelphase.pipelineitems[i].exp_amps.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_sqrt_expamps.GetValue() )
		object.append( panelphase.pipelineitems[i].support.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].niter.value.GetValue() )
	if subpanelname == 'RAAR':
		object.append( panelphase.pipelineitems[i].exp_amps.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_sqrt_expamps.GetValue() )
		object.append( panelphase.pipelineitems[i].support.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].mask.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].beta.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niter.value.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox.GetValue() )
		object.append( panelphase.pipelineitems[i].niter_relax.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niter_relax.IsEnabled)
	if subpanelname == 'HPR':
		object.append( panelphase.pipelineitems[i].exp_amps.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_sqrt_expamps.GetValue() )
		object.append( panelphase.pipelineitems[i].support.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].mask.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].beta.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niter.value.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox.GetValue() )
		object.append( panelphase.pipelineitems[i].niter_relax.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niter_relax.IsEnabled)
	if subpanelname == 'HIO Mask':
		object.append( panelphase.pipelineitems[i].exp_amps.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_sqrt_expamps.GetValue() )
		object.append( panelphase.pipelineitems[i].support.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].mask.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].beta.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niter.value.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox.GetValue() )
		object.append( panelphase.pipelineitems[i].niter_relax.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niter_relax.IsEnabled)
	if subpanelname == 'HIO Plus':
		object.append( panelphase.pipelineitems[i].exp_amps.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_sqrt_expamps.GetValue() )
		object.append( panelphase.pipelineitems[i].support.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].mask.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].beta.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niter.value.GetValue() )
	if subpanelname == 'PCHIO':
		object.append( panelphase.pipelineitems[i].exp_amps.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_sqrt_expamps.GetValue() )
		object.append( panelphase.pipelineitems[i].support.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].mask.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].beta.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niter.value.GetValue() )
		object.append( panelphase.pipelineitems[i].phasemax.value.GetValue() )
		object.append( panelphase.pipelineitems[i].phasemin.value.GetValue() )
	if subpanelname == 'POER':
		object.append( panelphase.pipelineitems[i].exp_amps.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_sqrt_expamps.GetValue() )
		object.append( panelphase.pipelineitems[i].support.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].mask.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].niter.value.GetValue() )
	if subpanelname == 'ER Mask':
		object.append( panelphase.pipelineitems[i].exp_amps.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_sqrt_expamps.GetValue() )
		object.append( panelphase.pipelineitems[i].support.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].mask.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].niter.value.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox.GetValue() )
		object.append( panelphase.pipelineitems[i].niter_relax.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niter_relax.IsEnabled)
	if subpanelname == 'Shrink Wrap':
		object.append( panelphase.pipelineitems[i].exp_amps.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_sqrt_expamps.GetValue() )
		object.append( panelphase.pipelineitems[i].support.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].mask.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].beta.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niter.value.GetValue() )
		object.append( panelphase.pipelineitems[i].cycle.value.GetValue() )
		object.append( panelphase.pipelineitems[i].phasemax.value.GetValue() )
		object.append( panelphase.pipelineitems[i].phasemin.value.GetValue() )
		object.append( panelphase.pipelineitems[i].sigma.value.GetValue() )
		object.append( panelphase.pipelineitems[i].frac.value.GetValue() )
		object.append( panelphase.pipelineitems[i].rbrs.GetStringSelection() )
		object.append( panelphase.pipelineitems[i].cs_p.value.GetValue() )
		object.append( panelphase.pipelineitems[i].cs_epsilon.value.GetValue() )
		object.append( panelphase.pipelineitems[i].cs_d.value.GetValue() )
		object.append( panelphase.pipelineitems[i].cs_eta.value.GetValue() )
		object.append( panelphase.pipelineitems[i].cs_epsilon_min.value.GetValue() )
		object.append( panelphase.pipelineitems[i].gc_phasemax.value.GetValue() )
		object.append( panelphase.pipelineitems[i].gc_phasemin.value.GetValue() )
		object.append( panelphase.pipelineitems[i].qx.value.GetValue() )
		object.append( panelphase.pipelineitems[i].qy.value.GetValue() )
		object.append( panelphase.pipelineitems[i].qz.value.GetValue() )
		object.append( panelphase.pipelineitems[i].ttheta )
		object.append( panelphase.pipelineitems[i].phi )
		object.append( panelphase.pipelineitems[i].waveln )
		object.append( panelphase.pipelineitems[i].chkbox_relax.GetValue() )
		object.append( panelphase.pipelineitems[i].taumax.value.GetValue() )
		object.append( panelphase.pipelineitems[i].dtaumax.value.GetValue() )
		object.append( panelphase.pipelineitems[i].dtaumin.value.GetValue() )
		object.append( panelphase.pipelineitems[i].psiexitratio.value.GetValue() )
		object.append( panelphase.pipelineitems[i].psiexiterror.value.GetValue() )
		object.append( panelphase.pipelineitems[i].psiresetratio.value.GetValue() )
		object.append( panelphase.pipelineitems[i].nsoiter.value.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_reweight.GetValue() )
		object.append( panelphase.pipelineitems[i].reweightiter.value.GetValue() )
	if subpanelname == 'PGCHIO':
		object.append( panelphase.pipelineitems[i].exp_amps.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_sqrt_expamps.GetValue() )
		object.append( panelphase.pipelineitems[i].support.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].mask.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].beta.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niter.value.GetValue() )
		object.append( panelphase.pipelineitems[i].phasemax.value.GetValue() )
		object.append( panelphase.pipelineitems[i].phasemin.value.GetValue() )
		object.append( panelphase.pipelineitems[i].qx.value.GetValue() )
		object.append( panelphase.pipelineitems[i].qy.value.GetValue() )
		object.append( panelphase.pipelineitems[i].qz.value.GetValue() )
		object.append( panelphase.pipelineitems[i].ttheta )
		object.append( panelphase.pipelineitems[i].phi )
		object.append( panelphase.pipelineitems[i].waveln )
	if subpanelname == 'CSHIO':
		object.append( panelphase.pipelineitems[i].exp_amps.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_sqrt_expamps.GetValue() )
		object.append( panelphase.pipelineitems[i].support.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].mask.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].beta.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niter.value.GetValue() )
		object.append( panelphase.pipelineitems[i].cs_p.value.GetValue() )
		object.append( panelphase.pipelineitems[i].cs_epsilon.value.GetValue() )
		object.append( panelphase.pipelineitems[i].cs_d.value.GetValue() )
		object.append( panelphase.pipelineitems[i].cs_eta.value.GetValue() )
		object.append( panelphase.pipelineitems[i].cs_epsilon_min.value.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_relax.GetValue() )
	if subpanelname == 'SO2D':
		object.append( panelphase.pipelineitems[i].exp_amps.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_sqrt_expamps.GetValue() )
		object.append( panelphase.pipelineitems[i].support.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].mask.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].beta.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niter.value.GetValue() )
		object.append( panelphase.pipelineitems[i].taumax.value.GetValue() )
		object.append( panelphase.pipelineitems[i].dtaumax.value.GetValue() )
		object.append( panelphase.pipelineitems[i].dtaumin.value.GetValue() )
		object.append( panelphase.pipelineitems[i].psiexitratio.value.GetValue() )
		object.append( panelphase.pipelineitems[i].psiexiterror.value.GetValue() )
		object.append( panelphase.pipelineitems[i].psiresetratio.value.GetValue() )
		object.append( panelphase.pipelineitems[i].nsoiter.value.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_reweight.GetValue() )
		object.append( panelphase.pipelineitems[i].reweightiter.value.GetValue() )
	if subpanelname == 'HIO Mask PC':
		object.append( panelphase.pipelineitems[i].exp_amps.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_sqrt_expamps.GetValue() )
		object.append( panelphase.pipelineitems[i].support.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].mask.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].beta.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niter.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niterrlpre.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niterrl.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niterrlinterval.value.GetValue() )
		object.append( panelphase.pipelineitems[i].gammaHWHM.value.GetValue() )
		object.append( panelphase.pipelineitems[i].zedims[0].value.GetValue() )
		object.append( panelphase.pipelineitems[i].zedims[1].value.GetValue() )
		object.append( panelphase.pipelineitems[i].zedims[2].value.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_reset_gamma.GetValue() )
		object.append( panelphase.pipelineitems[i].accel.value.GetValue() )
	if subpanelname == 'ER Mask PC':
		object.append( panelphase.pipelineitems[i].exp_amps.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_sqrt_expamps.GetValue() )
		object.append( panelphase.pipelineitems[i].support.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].mask.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].niter.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niterrlpre.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niterrl.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niterrlinterval.value.GetValue() )
		object.append( panelphase.pipelineitems[i].gammaHWHM.value.GetValue() )
		object.append( panelphase.pipelineitems[i].zedims[0].value.GetValue() )
		object.append( panelphase.pipelineitems[i].zedims[1].value.GetValue() )
		object.append( panelphase.pipelineitems[i].zedims[2].value.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_reset_gamma.GetValue() )
		object.append( panelphase.pipelineitems[i].accel.value.GetValue() )
	if subpanelname == 'HPR PC':
		object.append( panelphase.pipelineitems[i].exp_amps.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_sqrt_expamps.GetValue() )
		object.append( panelphase.pipelineitems[i].support.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].mask.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].beta.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niter.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niterrlpre.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niterrl.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niterrlinterval.value.GetValue() )
		object.append( panelphase.pipelineitems[i].gammaHWHM.value.GetValue() )
		object.append( panelphase.pipelineitems[i].zedims[0].value.GetValue() )
		object.append( panelphase.pipelineitems[i].zedims[1].value.GetValue() )
		object.append( panelphase.pipelineitems[i].zedims[2].value.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_reset_gamma.GetValue() )
		object.append( panelphase.pipelineitems[i].accel.value.GetValue() )
	if subpanelname == 'RAAR PC':
		object.append( panelphase.pipelineitems[i].exp_amps.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_sqrt_expamps.GetValue() )
		object.append( panelphase.pipelineitems[i].support.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].mask.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].beta.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niter.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niterrlpre.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niterrl.value.GetValue() )
		object.append( panelphase.pipelineitems[i].niterrlinterval.value.GetValue() )
		object.append( panelphase.pipelineitems[i].gammaHWHM.value.GetValue() )
		object.append( panelphase.pipelineitems[i].zedims[0].value.GetValue() )
		object.append( panelphase.pipelineitems[i].zedims[1].value.GetValue() )
		object.append( panelphase.pipelineitems[i].zedims[2].value.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_reset_gamma.GetValue() )
		object.append( panelphase.pipelineitems[i].accel.value.GetValue() )
	if subpanelname == 'Save Sequence':
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
	if subpanelname == 'Save Support':
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
	if subpanelname == 'Save Residual':
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
	if subpanelname == 'Co-ordinate Transformation':
		object.append( panelphase.pipelineitems[i].rbfrom.GetStringSelection() )
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename_amp.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].output_filename_phase.objectpath.GetValue() )
		object.append( panelphase.pipelineitems[i].rbcurve.GetStringSelection() )
		object.append( panelphase.pipelineitems[i].bdims[0].value.GetValue() )
		object.append( panelphase.pipelineitems[i].bdims[1].value.GetValue() )
		object.append( panelphase.pipelineitems[i].bdims[2].value.GetValue() )
		object.append( panelphase.pipelineitems[i].twotheta.value.GetValue() )
		object.append( panelphase.pipelineitems[i].dtheta.value.GetValue() )
		object.append( panelphase.pipelineitems[i].phi.value.GetValue() )
		object.append( panelphase.pipelineitems[i].dphi.value.GetValue() )
		object.append( panelphase.pipelineitems[i].pixelx.value.GetValue() )
		object.append( panelphase.pipelineitems[i].pixely.value.GetValue() )
		object.append( panelphase.pipelineitems[i].waveln.value.GetValue() )
		object.append( panelphase.pipelineitems[i].armln.value.GetValue() )
		object.append( panelphase.pipelineitems[i].chkbox_ccdflip.GetValue() )
		object.append( panelphase.pipelineitems[i].rbtype.GetStringSelection() )
	if subpanelname == 'Load Co-ordinates':
		object.append( panelphase.pipelineitems[i].input_filename.objectpath.GetValue() )
	if subpanelname == 'Save Co-ordinates':
		object.append( panelphase.pipelineitems[i].output_filename.objectpath.GetValue() )
	object.append( panelphase.mainlist.IsChecked(i) )
	return [mainlist, object, subpanelname]
def SetInstanceObject(panelphase, instance, idx, subpanel_items):
	subpanelname = instance[2]
	if subpanelname in subpanel_items:
		itemcount = panelphase.mainlist.GetItemCount()
		mainlistidx = panelphase.mainlist.InsertItem(idx,"")
		panelphase.mainlist.CheckItem(mainlistidx)
		panelphase.mainlist.SetItem(mainlistidx, 1, instance[0])
		object = instance[1]
		if subpanelname == 'Nexus Viewer I16':
			panelphase.pipelineitems.insert(idx, SubPanel_NEXUSView(panelphase.panel2, panelphase.ancestor))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Python Script':
			panelphase.pipelineitems.insert(idx, SubPanel_PyScript(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].txt.SetValue(object[0])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Comments':
			panelphase.pipelineitems.insert(idx, SubPanel_Comments(panelphase.panel2, panelphase.ancestor))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].txt.SetValue(object[0])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Blank Line Fill':
			panelphase.pipelineitems.insert(idx, SubPanel_BlankLineFill(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].objectpath.SetValue(object[1])
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[2])
			panelphase.pipelineitems[idx].kdims[0].value.SetValue(object[3])
			panelphase.pipelineitems[idx].kdims[1].value.SetValue(object[4])
			panelphase.pipelineitems[idx].kdims[2].value.SetValue(object[5])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Scale Array':
			panelphase.pipelineitems.insert(idx, SubPanel_Scale_Array(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[1])
			panelphase.pipelineitems[idx].scale.value.SetValue(object[2])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'SumDiff Array':
			panelphase.pipelineitems.insert(idx, SubPanel_SumDiff_Array(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].input_filename1.objectpath.SetValue(object[1])
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[2])
			panelphase.pipelineitems[idx].addsub.SetStringSelection(object[3])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Rotate Support':
			panelphase.pipelineitems.insert(idx, SubPanel_Rotate_Support(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[1])
			panelphase.pipelineitems[idx].rotationaxis.value.SetValue(object[2])
			panelphase.pipelineitems[idx].rotationangle.value.SetValue(object[3])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Transpose Array':
			panelphase.pipelineitems.insert(idx, SubPanel_Transpose_Array(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[1])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'SPE to Numpy':
			panelphase.pipelineitems.insert(idx, SubPanel_SPE_to_Numpy(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[1])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Image to Numpy':
			panelphase.pipelineitems.insert(idx, SubPanel_Image_to_Numpy(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[1])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Crop Pad':
			panelphase.pipelineitems.insert(idx, SubPanel_Crop_Pad(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[1])
			panelphase.pipelineitems[idx].csdims[0].value.SetValue(object[2])
			panelphase.pipelineitems[idx].csdims[1].value.SetValue(object[3])
			panelphase.pipelineitems[idx].csdims[2].value.SetValue(object[4])
			panelphase.pipelineitems[idx].cedims[0].value.SetValue(object[5])
			panelphase.pipelineitems[idx].cedims[1].value.SetValue(object[6])
			panelphase.pipelineitems[idx].cedims[2].value.SetValue(object[7])
			panelphase.pipelineitems[idx].psdims[0].value.SetValue(object[8])
			panelphase.pipelineitems[idx].psdims[1].value.SetValue(object[9])
			panelphase.pipelineitems[idx].psdims[2].value.SetValue(object[10])
			panelphase.pipelineitems[idx].pedims[0].value.SetValue(object[11])
			panelphase.pipelineitems[idx].pedims[1].value.SetValue(object[12])
			panelphase.pipelineitems[idx].pedims[2].value.SetValue(object[13])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Mask':
			panelphase.pipelineitems.insert(idx, SubPanel_Mask(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[1])
			panelphase.pipelineitems[idx].max.value.SetValue(object[2])
			panelphase.pipelineitems[idx].min.value.SetValue(object[3])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Threshold Data':
			panelphase.pipelineitems.insert(idx, SubPanel_Threshold(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[1])
			panelphase.pipelineitems[idx].max.value.SetValue(object[2])
			panelphase.pipelineitems[idx].min.value.SetValue(object[3])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Bin':
			panelphase.pipelineitems.insert(idx, SubPanel_Bin(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[1])
			panelphase.pipelineitems[idx].bdims[0].value.SetValue(object[2])
			panelphase.pipelineitems[idx].bdims[1].value.SetValue(object[3])
			panelphase.pipelineitems[idx].bdims[2].value.SetValue(object[4])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Auto Centre':
			panelphase.pipelineitems.insert(idx, SubPanel_AutoCentre(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[1])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Centred Resize':
			panelphase.pipelineitems.insert(idx, SubPanel_CentredResize(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[1])
			panelphase.pipelineitems[idx].dims[0].value.SetValue(object[2])
			panelphase.pipelineitems[idx].dims[1].value.SetValue(object[3])
			panelphase.pipelineitems[idx].dims[2].value.SetValue(object[4])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Wrap Data':
			panelphase.pipelineitems.insert(idx,SubPanel_Wrap(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[1])
			try:
				panelphase.pipelineitems[idx].rbdirection.SetStringSelection(object[2])
			except:
				pass
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'HDF5 to Numpy':
			panelphase.pipelineitems.insert(idx, SubPanel_HDF_to_Numpy(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].objectpath.SetValue(object[1])
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[2])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Array to VTK':
			panelphase.pipelineitems.insert(idx, SubPanel_ArraytoVTK(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[1])
			panelphase.pipelineitems[idx].rbampphase.SetStringSelection(object[2])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Interpolate Object':
			panelphase.pipelineitems.insert(idx, SubPanel_InterpolateObject(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].coords_filename.objectpath.SetValue(object[1])
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[2])
			panelphase.pipelineitems[idx].spacer[0].value.SetValue(object[3])
			panelphase.pipelineitems[idx].spacer[1].value.SetValue(object[4])
			panelphase.pipelineitems[idx].spacer[2].value.SetValue(object[5])
			panelphase.pipelineitems[idx].interp_range.value.SetValue(object[6])
			try:
				panelphase.pipelineitems[idx].bounds[0].value.SetValue(object[7])
				panelphase.pipelineitems[idx].bounds[1].value.SetValue(object[8])
				panelphase.pipelineitems[idx].bounds[2].value.SetValue(object[9])
				panelphase.pipelineitems[idx].bounds[3].value.SetValue(object[10])
				panelphase.pipelineitems[idx].bounds[4].value.SetValue(object[11])
				panelphase.pipelineitems[idx].bounds[5].value.SetValue(object[12])
			except:
				pass
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Affine Transform':
			panelphase.pipelineitems.insert(idx, SubPanel_AffineTransform(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].coords_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].outputcoords_filename.objectpath.SetValue(object[1])
			panelphase.pipelineitems[idx].translate[0].value.SetValue(object[2])
			panelphase.pipelineitems[idx].translate[1].value.SetValue(object[3])
			panelphase.pipelineitems[idx].translate[2].value.SetValue(object[4])
			panelphase.pipelineitems[idx].scale[0].value.SetValue(object[5])
			panelphase.pipelineitems[idx].scale[1].value.SetValue(object[6])
			panelphase.pipelineitems[idx].scale[2].value.SetValue(object[7])
			panelphase.pipelineitems[idx].rotate[0].value.SetValue(object[8])
			panelphase.pipelineitems[idx].rotate[1].value.SetValue(object[9])
			panelphase.pipelineitems[idx].rotate[2].value.SetValue(object[10])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Voxel Replace':
			panelphase.pipelineitems.insert(idx, SubPanel_Voxel_Replace(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[1])
			panelphase.pipelineitems[idx].sdims[0].value.SetValue(object[2])
			panelphase.pipelineitems[idx].sdims[1].value.SetValue(object[3])
			panelphase.pipelineitems[idx].sdims[2].value.SetValue(object[4])
			panelphase.pipelineitems[idx].edims[0].value.SetValue(object[5])
			panelphase.pipelineitems[idx].edims[1].value.SetValue(object[6])
			panelphase.pipelineitems[idx].edims[2].value.SetValue(object[7])
			panelphase.pipelineitems[idx].real.value.SetValue(object[8])
			panelphase.pipelineitems[idx].imag.value.SetValue(object[9])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Conjugate Reflect':
			panelphase.pipelineitems.insert(idx, SubPanel_Conjugate_Reflect(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[1])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Gaussian Fill':
			panelphase.pipelineitems.insert(idx, SubPanel_GaussianFill(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[1])
			panelphase.pipelineitems[idx].sigma.value.SetValue(object[2])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Fourier Transform':
			panelphase.pipelineitems.insert(idx, SubPanel_FFT(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[1])
			panelphase.pipelineitems[idx].rbdirection.SetStringSelection(object[2])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Convolve':
			panelphase.pipelineitems.insert(idx, SubPanel_Convolve(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename1.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].input_filename2.objectpath.SetValue(object[1])
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[2])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Object to VTK':
			panelphase.pipelineitems.insert(idx, SubPanel_ObjecttoVTK(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].coords_filename.objectpath.SetValue(object[1])
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[2])
			panelphase.pipelineitems[idx].rbampphase.SetStringSelection(object[3])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Array to Memory':
			panelphase.pipelineitems.insert(idx, SubPanel_Array_to_Memory(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[1])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Memory to Array':
			panelphase.pipelineitems.insert(idx, SubPanel_Memory_to_Array(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[1])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Load PSF':
			panelphase.pipelineitems.insert(idx, SubPanel_Load_PSF(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Save PSF':
			panelphase.pipelineitems.insert(idx, SubPanel_Save_PSF(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[0])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Median Filter':
			panelphase.pipelineitems.insert(idx, SubPanel_Median_Filter(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[1])
			panelphase.pipelineitems[idx].kdims[0].value.SetValue(object[2])
			panelphase.pipelineitems[idx].kdims[1].value.SetValue(object[3])
			panelphase.pipelineitems[idx].kdims[2].value.SetValue(object[4])
			panelphase.pipelineitems[idx].maxdev.value.SetValue(object[5])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Cuboid Support':
			panelphase.pipelineitems.insert(idx, SubPanel_Cuboid_Support(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].fromfile.objectpath.SetValue(object[1])
			panelphase.pipelineitems[idx].dims[0].value.SetValue(object[2])
			panelphase.pipelineitems[idx].dims[1].value.SetValue(object[3])
			panelphase.pipelineitems[idx].dims[2].value.SetValue(object[4])
			panelphase.pipelineitems[idx].sdims[0].value.SetValue(object[5])
			panelphase.pipelineitems[idx].sdims[1].value.SetValue(object[6])
			panelphase.pipelineitems[idx].sdims[2].value.SetValue(object[7])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Polyhedron Support':
			panelphase.pipelineitems.insert(idx, SubPanel_Polyhedron_Support(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].fromfile.objectpath.SetValue(object[1])
			panelphase.pipelineitems[idx].dims[0].value.SetValue(object[2])
			panelphase.pipelineitems[idx].dims[1].value.SetValue(object[3])
			panelphase.pipelineitems[idx].dims[2].value.SetValue(object[4])
			panelphase.pipelineitems[idx].init_points.SetValue(object[5])
			panelphase.pipelineitems[idx].term_points.SetValue(object[6])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Empty Array':
			panelphase.pipelineitems.insert(idx, SubPanel_Empty_Array(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].fromfile.objectpath.SetValue(object[1])
			panelphase.pipelineitems[idx].dims[0].value.SetValue(object[2])
			panelphase.pipelineitems[idx].dims[1].value.SetValue(object[3])
			panelphase.pipelineitems[idx].dims[2].value.SetValue(object[4])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'View Support':
			panelphase.pipelineitems.insert(idx, SubPanel_View_Support(panelphase.panel2, panelphase.ancestor))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].support.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[1])
			panelphase.pipelineitems[idx].contour_support.value.SetValue(object[2])
			panelphase.pipelineitems[idx].contour.value.SetValue(object[3])
			panelphase.pipelineitems[idx].opacity.value.SetValue(object[4])
			panelphase.pipelineitems[idx].feature_angle.value.SetValue(object[5])
			panelphase.pipelineitems[idx].chkbox_axes.SetValue(object[6])
			panelphase.pipelineitems[idx].axes_fontfactor.value.SetValue(object[7])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Laxarus Viewer':
			panelphase.pipelineitems.insert(idx, SubPanel_LaxarusView(panelphase.panel2, panelphase.ancestor))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].filename.objectpath.SetValue(object[0])
		if subpanelname == 'View Array':
			panelphase.pipelineitems.insert(idx, SubPanel_View_Array(panelphase.panel2, panelphase.ancestor))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].rbampphase.SetStringSelection(object[1])
			panelphase.pipelineitems[idx].contour.value.SetValue(object[2])
			panelphase.pipelineitems[idx].opacity.value.SetValue(object[3])
			panelphase.pipelineitems[idx].phasemax.value.SetValue(object[4])
			panelphase.pipelineitems[idx].phasemin.value.SetValue(object[5])
			panelphase.pipelineitems[idx].ox.value.SetValue(object[6])
			panelphase.pipelineitems[idx].oy.value.SetValue(object[7])
			panelphase.pipelineitems[idx].oz.value.SetValue(object[8])
			panelphase.pipelineitems[idx].nx.value.SetValue(object[9])
			panelphase.pipelineitems[idx].ny.value.SetValue(object[10])
			panelphase.pipelineitems[idx].nz.value.SetValue(object[11])
			panelphase.pipelineitems[idx].chkbox_axes.SetValue(object[12])
			try:
				panelphase.pipelineitems[idx].feature_angle.value.SetValue(object[13])
				panelphase.pipelineitems[idx].sx.value.SetValue(object[14])
				panelphase.pipelineitems[idx].sy.value.SetValue(object[15])
				panelphase.pipelineitems[idx].sz.value.SetValue(object[16])
				panelphase.pipelineitems[idx].axes_fontfactor.value.SetValue(object[17])
			except:
				pass
			try:
				panelphase.pipelineitems[idx].meshsubiter.value.SetValue(object[18])
			except:
				pass
			panelphase.pipelineitems[idx].OnRadioSelect(None)
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'View Object':
			panelphase.pipelineitems.insert(idx, SubPanel_View_Object(panelphase.panel2, panelphase.ancestor))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].coords_filename.objectpath.SetValue(object[1])
			panelphase.pipelineitems[idx].rbampphase.SetStringSelection(object[2])
			panelphase.pipelineitems[idx].contour.value.SetValue(object[3])
			panelphase.pipelineitems[idx].opacity.value.SetValue(object[4])
			panelphase.pipelineitems[idx].phasemax.value.SetValue(object[5])
			panelphase.pipelineitems[idx].phasemin.value.SetValue(object[6])
			panelphase.pipelineitems[idx].ox.value.SetValue(object[7])
			panelphase.pipelineitems[idx].oy.value.SetValue(object[8])
			panelphase.pipelineitems[idx].oz.value.SetValue(object[9])
			panelphase.pipelineitems[idx].nx.value.SetValue(object[10])
			panelphase.pipelineitems[idx].ny.value.SetValue(object[11])
			panelphase.pipelineitems[idx].nz.value.SetValue(object[12])
			panelphase.pipelineitems[idx].chkbox_axes.SetValue(object[13])
			try:
				panelphase.pipelineitems[idx].feature_angle.value.SetValue(object[14])
				panelphase.pipelineitems[idx].axes_fontfactor.value.SetValue(object[15])
			except:
				pass
			try:
				panelphase.pipelineitems[idx].meshsubiter.value.SetValue(object[16])
			except:
				pass
			panelphase.pipelineitems[idx].OnRadioSelect(None)
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'View VTK Array':
			panelphase.pipelineitems.insert(idx, SubPanel_View_VTK(panelphase.panel2, panelphase.ancestor))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].rbampphase.SetStringSelection(object[1])
			panelphase.pipelineitems[idx].contour.value.SetValue(object[2])
			panelphase.pipelineitems[idx].feature_angle.value.SetValue(object[3])
			panelphase.pipelineitems[idx].phasemax.value.SetValue(object[4])
			panelphase.pipelineitems[idx].phasemin.value.SetValue(object[5])
			panelphase.pipelineitems[idx].ox.value.SetValue(object[6])
			panelphase.pipelineitems[idx].oy.value.SetValue(object[7])
			panelphase.pipelineitems[idx].oz.value.SetValue(object[8])
			panelphase.pipelineitems[idx].nx.value.SetValue(object[9])
			panelphase.pipelineitems[idx].ny.value.SetValue(object[10])
			panelphase.pipelineitems[idx].nz.value.SetValue(object[11])
			panelphase.pipelineitems[idx].chkbox_axes.SetValue(object[12])
			try:
				panelphase.pipelineitems[idx].axes_fontfactor.value.SetValue(object[13])
			except:
				pass
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Random Start':
			panelphase.pipelineitems.insert(idx, SubPanel_Random(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].amp_max.value.SetValue(object[0])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Array Start':
			panelphase.pipelineitems.insert(idx, SubPanel_ArrayStart(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'HIO':
			panelphase.pipelineitems.insert(idx, SubPanel_HIO(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].exp_amps.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].chkbox_sqrt_expamps.SetValue(object[1])
			panelphase.pipelineitems[idx].support.objectpath.SetValue(object[2])
			panelphase.pipelineitems[idx].beta.value.SetValue(object[3])
			panelphase.pipelineitems[idx].niter.value.SetValue(object[4])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'ER':
			panelphase.pipelineitems.insert(idx, SubPanel_ER(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].exp_amps.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].chkbox_sqrt_expamps.SetValue(object[1])
			panelphase.pipelineitems[idx].support.objectpath.SetValue(object[2])
			panelphase.pipelineitems[idx].niter.value.SetValue(object[3])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'RAAR':
			panelphase.pipelineitems.insert(idx, SubPanel_RAAR(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].exp_amps.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].chkbox_sqrt_expamps.SetValue(object[1])
			panelphase.pipelineitems[idx].support.objectpath.SetValue(object[2])
			panelphase.pipelineitems[idx].mask.objectpath.SetValue(object[3])
			panelphase.pipelineitems[idx].beta.value.SetValue(object[4])
			panelphase.pipelineitems[idx].niter.value.SetValue(object[5])
			try:
				panelphase.pipelineitems[idx].chkbox.SetValue(object[6])
				panelphase.pipelineitems[idx].niter_relax.value.SetValue(object[7])
				if object[8] :
					panelphase.pipelineitems[idx].niter_relax.Enable()
			except:
				pass
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'HPR':
			panelphase.pipelineitems.insert(idx, SubPanel_HPR(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].exp_amps.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].chkbox_sqrt_expamps.SetValue(object[1])
			panelphase.pipelineitems[idx].support.objectpath.SetValue(object[2])
			panelphase.pipelineitems[idx].mask.objectpath.SetValue(object[3])
			panelphase.pipelineitems[idx].beta.value.SetValue(object[4])
			panelphase.pipelineitems[idx].niter.value.SetValue(object[5])
			try:
				panelphase.pipelineitems[idx].chkbox.SetValue(object[6])
				panelphase.pipelineitems[idx].niter_relax.value.SetValue(object[7])
				if object[8] :
					panelphase.pipelineitems[idx].niter_relax.Enable()
			except:
				pass
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'HIO Mask':
			panelphase.pipelineitems.insert(idx, SubPanel_HIOMask(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].exp_amps.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].chkbox_sqrt_expamps.SetValue(object[1])
			panelphase.pipelineitems[idx].support.objectpath.SetValue(object[2])
			panelphase.pipelineitems[idx].mask.objectpath.SetValue(object[3])
			panelphase.pipelineitems[idx].beta.value.SetValue(object[4])
			panelphase.pipelineitems[idx].niter.value.SetValue(object[5])
			try:
				panelphase.pipelineitems[idx].chkbox.SetValue(object[6])
				panelphase.pipelineitems[idx].niter_relax.value.SetValue(object[7])
				if object[8] :
					panelphase.pipelineitems[idx].niter_relax.Enable()
			except:
				pass
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'HIO Plus':
			panelphase.pipelineitems.insert(idx, SubPanel_HIOPlus(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].exp_amps.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].chkbox_sqrt_expamps.SetValue(object[1])
			panelphase.pipelineitems[idx].support.objectpath.SetValue(object[2])
			panelphase.pipelineitems[idx].mask.objectpath.SetValue(object[3])
			panelphase.pipelineitems[idx].beta.value.SetValue(object[4])
			panelphase.pipelineitems[idx].niter.value.SetValue(object[5])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'PCHIO':
			panelphase.pipelineitems.insert(idx, SubPanel_PCHIO(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].exp_amps.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].chkbox_sqrt_expamps.SetValue(object[1])
			panelphase.pipelineitems[idx].support.objectpath.SetValue(object[2])
			panelphase.pipelineitems[idx].mask.objectpath.SetValue(object[3])
			panelphase.pipelineitems[idx].beta.value.SetValue(object[4])
			panelphase.pipelineitems[idx].niter.value.SetValue(object[5])
			panelphase.pipelineitems[idx].phasemax.value.SetValue(object[6])
			panelphase.pipelineitems[idx].phasemin.value.SetValue(object[7])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'POER':
			panelphase.pipelineitems.insert(idx, SubPanel_POER(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].exp_amps.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].chkbox_sqrt_expamps.SetValue(object[1])
			panelphase.pipelineitems[idx].support.objectpath.SetValue(object[2])
			panelphase.pipelineitems[idx].mask.objectpath.SetValue(object[3])
			panelphase.pipelineitems[idx].niter.value.SetValue(object[4])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'ER Mask':
			panelphase.pipelineitems.insert(idx, SubPanel_ERMask(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].exp_amps.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].chkbox_sqrt_expamps.SetValue(object[1])
			panelphase.pipelineitems[idx].support.objectpath.SetValue(object[2])
			panelphase.pipelineitems[idx].mask.objectpath.SetValue(object[3])
			panelphase.pipelineitems[idx].niter.value.SetValue(object[4])
			try:
				panelphase.pipelineitems[idx].chkbox.SetValue(object[5])
				panelphase.pipelineitems[idx].niter_relax.value.SetValue(object[6])
				if object[7] :
					panelphase.pipelineitems[idx].niter_relax.Enable()
			except:
				pass
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Shrink Wrap':
			panelphase.pipelineitems.insert(idx, SubPanel_ShrinkWrap(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].exp_amps.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].chkbox_sqrt_expamps.SetValue(object[1])
			panelphase.pipelineitems[idx].support.objectpath.SetValue(object[2])
			panelphase.pipelineitems[idx].mask.objectpath.SetValue(object[3])
			panelphase.pipelineitems[idx].beta.value.SetValue(object[4])
			panelphase.pipelineitems[idx].niter.value.SetValue(object[5])
			panelphase.pipelineitems[idx].cycle.value.SetValue(object[6])
			panelphase.pipelineitems[idx].phasemax.value.SetValue(object[7])
			panelphase.pipelineitems[idx].phasemin.value.SetValue(object[8])
			panelphase.pipelineitems[idx].sigma.value.SetValue(object[9])
			panelphase.pipelineitems[idx].frac.value.SetValue(object[10])
			panelphase.pipelineitems[idx].rbrs.SetStringSelection(object[11])
			panelphase.pipelineitems[idx].cs_p.value.SetValue(object[12])
			panelphase.pipelineitems[idx].cs_epsilon.value.SetValue(object[13])
			panelphase.pipelineitems[idx].cs_d.value.SetValue(object[14])
			panelphase.pipelineitems[idx].cs_eta.value.SetValue(object[15])
			panelphase.pipelineitems[idx].cs_epsilon_min.value.SetValue(object[16])
			panelphase.pipelineitems[idx].gc_phasemax.value.SetValue(object[17])
			panelphase.pipelineitems[idx].gc_phasemin.value.SetValue(object[18])
			panelphase.pipelineitems[idx].qx.value.SetValue(object[19])
			panelphase.pipelineitems[idx].qy.value.SetValue(object[20])
			panelphase.pipelineitems[idx].qz.value.SetValue(object[21])
			panelphase.pipelineitems[idx].ttheta = object[22]
			panelphase.pipelineitems[idx].phi = object[23]
			panelphase.pipelineitems[idx].waveln = object[24]
			panelphase.pipelineitems[idx].chkbox_relax.SetValue(object[25])
			panelphase.pipelineitems[idx].taumax.value.SetValue(object[26])
			panelphase.pipelineitems[idx].dtaumax.value.SetValue(object[27])
			panelphase.pipelineitems[idx].dtaumin.value.SetValue(object[28])
			panelphase.pipelineitems[idx].psiexitratio.value.SetValue(object[29])
			panelphase.pipelineitems[idx].psiexiterror.value.SetValue(object[30])
			panelphase.pipelineitems[idx].psiresetratio.value.SetValue(object[31])
			panelphase.pipelineitems[idx].nsoiter.value.SetValue(object[32])
			panelphase.pipelineitems[idx].chkbox_reweight.SetValue(object[33])
			panelphase.pipelineitems[idx].reweightiter.value.SetValue(object[34])
			panelphase.pipelineitems[idx].OnChkbox(None)
			DoListCheck(panelphase, object, idx)
			panelphase.pipelineitems[idx].OnRadioSelect(None)
		if subpanelname == 'PGCHIO':
			panelphase.pipelineitems.insert(idx, SubPanel_PGCHIO(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].exp_amps.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].chkbox_sqrt_expamps.SetValue(object[1])
			panelphase.pipelineitems[idx].support.objectpath.SetValue(object[2])
			panelphase.pipelineitems[idx].mask.objectpath.SetValue(object[3])
			panelphase.pipelineitems[idx].beta.value.SetValue(object[4])
			panelphase.pipelineitems[idx].niter.value.SetValue(object[5])
			panelphase.pipelineitems[idx].phasemax.value.SetValue(object[6])
			panelphase.pipelineitems[idx].phasemin.value.SetValue(object[7])
			panelphase.pipelineitems[idx].qx.value.SetValue(object[8])
			panelphase.pipelineitems[idx].qy.value.SetValue(object[9])
			panelphase.pipelineitems[idx].qz.value.SetValue(object[10])
			panelphase.pipelineitems[idx].ttheta = object[11]
			panelphase.pipelineitems[idx].phi = object[12]
			panelphase.pipelineitems[idx].waveln = object[13]
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'CSHIO':
			panelphase.pipelineitems.insert(idx, SubPanel_CSHIO(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].exp_amps.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].chkbox_sqrt_expamps.SetValue(object[1])
			panelphase.pipelineitems[idx].support.objectpath.SetValue(object[2])
			panelphase.pipelineitems[idx].mask.objectpath.SetValue(object[3])
			panelphase.pipelineitems[idx].beta.value.SetValue(object[4])
			panelphase.pipelineitems[idx].niter.value.SetValue(object[5])
			panelphase.pipelineitems[idx].cs_p.value.SetValue(object[6])
			panelphase.pipelineitems[idx].cs_epsilon.value.SetValue(object[7])
			panelphase.pipelineitems[idx].cs_d.value.SetValue(object[8])
			panelphase.pipelineitems[idx].cs_eta.value.SetValue(object[9])
			try:
				panelphase.pipelineitems[idx].cs_epsilon_min.value.SetValue(object[10])
			except:
				pass
			try:
				panelphase.pipelineitems[idx].chkbox_relax.SetValue(object[11])
			except:
				pass
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'SO2D':
			panelphase.pipelineitems.insert(idx, SubPanel_SO2D(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].exp_amps.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].chkbox_sqrt_expamps.SetValue(object[1])
			panelphase.pipelineitems[idx].support.objectpath.SetValue(object[2])
			panelphase.pipelineitems[idx].mask.objectpath.SetValue(object[3])
			panelphase.pipelineitems[idx].beta.value.SetValue(object[4])
			panelphase.pipelineitems[idx].niter.value.SetValue(object[5])
			panelphase.pipelineitems[idx].taumax.value.SetValue(object[6])
			panelphase.pipelineitems[idx].dtaumax.value.SetValue(object[7])
			panelphase.pipelineitems[idx].dtaumin.value.SetValue(object[8])
			panelphase.pipelineitems[idx].psiexitratio.value.SetValue(object[9])
			panelphase.pipelineitems[idx].psiexiterror.value.SetValue(object[10])
			panelphase.pipelineitems[idx].psiresetratio.value.SetValue(object[11])
			panelphase.pipelineitems[idx].nsoiter.value.SetValue(object[12])
			panelphase.pipelineitems[idx].chkbox_reweight.SetValue(object[13])
			panelphase.pipelineitems[idx].reweightiter.value.SetValue(object[14])
			panelphase.pipelineitems[idx].OnChkbox(None)
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'HIO Mask PC':
			panelphase.pipelineitems.insert(idx, SubPanel_HIOMaskPC(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].exp_amps.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].chkbox_sqrt_expamps.SetValue(object[1])
			panelphase.pipelineitems[idx].support.objectpath.SetValue(object[2])
			panelphase.pipelineitems[idx].mask.objectpath.SetValue(object[3])
			panelphase.pipelineitems[idx].beta.value.SetValue(object[4])
			panelphase.pipelineitems[idx].niter.value.SetValue(object[5])
			panelphase.pipelineitems[idx].niterrlpre.value.SetValue(object[6])
			panelphase.pipelineitems[idx].niterrl.value.SetValue(object[7])
			panelphase.pipelineitems[idx].niterrlinterval.value.SetValue(object[8])
			panelphase.pipelineitems[idx].gammaHWHM.value.SetValue(object[9])
			panelphase.pipelineitems[idx].zedims[0].value.SetValue(object[10])
			panelphase.pipelineitems[idx].zedims[1].value.SetValue(object[11])
			panelphase.pipelineitems[idx].zedims[2].value.SetValue(object[12])
			panelphase.pipelineitems[idx].chkbox_reset_gamma.SetValue(object[13])
			try:
				panelphase.pipelineitems[idx].accel.value.SetValue(object[14])
			except:
				pass
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'ER Mask PC':
			panelphase.pipelineitems.insert(idx, SubPanel_ERMaskPC(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].exp_amps.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].chkbox_sqrt_expamps.SetValue(object[1])
			panelphase.pipelineitems[idx].support.objectpath.SetValue(object[2])
			panelphase.pipelineitems[idx].mask.objectpath.SetValue(object[3])
			panelphase.pipelineitems[idx].niter.value.SetValue(object[4])
			panelphase.pipelineitems[idx].niterrlpre.value.SetValue(object[5])
			panelphase.pipelineitems[idx].niterrl.value.SetValue(object[6])
			panelphase.pipelineitems[idx].niterrlinterval.value.SetValue(object[7])
			panelphase.pipelineitems[idx].gammaHWHM.value.SetValue(object[8])
			panelphase.pipelineitems[idx].zedims[0].value.SetValue(object[9])
			panelphase.pipelineitems[idx].zedims[1].value.SetValue(object[10])
			panelphase.pipelineitems[idx].zedims[2].value.SetValue(object[11])
			panelphase.pipelineitems[idx].chkbox_reset_gamma.SetValue(object[12])
			try:
				panelphase.pipelineitems[idx].accel.value.SetValue(object[13])
			except:
				pass
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'HPR PC':
			panelphase.pipelineitems.insert(idx, SubPanel_HPRMaskPC(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].exp_amps.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].chkbox_sqrt_expamps.SetValue(object[1])
			panelphase.pipelineitems[idx].support.objectpath.SetValue(object[2])
			panelphase.pipelineitems[idx].mask.objectpath.SetValue(object[3])
			panelphase.pipelineitems[idx].beta.value.SetValue(object[4])
			panelphase.pipelineitems[idx].niter.value.SetValue(object[5])
			panelphase.pipelineitems[idx].niterrlpre.value.SetValue(object[6])
			panelphase.pipelineitems[idx].niterrl.value.SetValue(object[7])
			panelphase.pipelineitems[idx].niterrlinterval.value.SetValue(object[8])
			panelphase.pipelineitems[idx].gammaHWHM.value.SetValue(object[9])
			panelphase.pipelineitems[idx].zedims[0].value.SetValue(object[10])
			panelphase.pipelineitems[idx].zedims[1].value.SetValue(object[11])
			panelphase.pipelineitems[idx].zedims[2].value.SetValue(object[12])
			panelphase.pipelineitems[idx].chkbox_reset_gamma.SetValue(object[13])
			try:
				panelphase.pipelineitems[idx].accel.value.SetValue(object[14])
			except:
				pass
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'RAAR PC':
			panelphase.pipelineitems.insert(idx, SubPanel_RAARMaskPC(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].exp_amps.objectpath.SetValue(object[0])
			panelphase.pipelineitems[idx].chkbox_sqrt_expamps.SetValue(object[1])
			panelphase.pipelineitems[idx].support.objectpath.SetValue(object[2])
			panelphase.pipelineitems[idx].mask.objectpath.SetValue(object[3])
			panelphase.pipelineitems[idx].beta.value.SetValue(object[4])
			panelphase.pipelineitems[idx].niter.value.SetValue(object[5])
			panelphase.pipelineitems[idx].niterrlpre.value.SetValue(object[6])
			panelphase.pipelineitems[idx].niterrl.value.SetValue(object[7])
			panelphase.pipelineitems[idx].niterrlinterval.value.SetValue(object[8])
			panelphase.pipelineitems[idx].gammaHWHM.value.SetValue(object[9])
			panelphase.pipelineitems[idx].zedims[0].value.SetValue(object[10])
			panelphase.pipelineitems[idx].zedims[1].value.SetValue(object[11])
			panelphase.pipelineitems[idx].zedims[2].value.SetValue(object[12])
			panelphase.pipelineitems[idx].chkbox_reset_gamma.SetValue(object[13])
			try:
				panelphase.pipelineitems[idx].accel.value.SetValue(object[14])
			except:
				pass
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Save Sequence' or subpanelname == 2010:
			panelphase.pipelineitems.insert(idx, SubPanel_Save_Sequence(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[0])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Save Support' or subpanelname == 2012:
			panelphase.pipelineitems.insert(idx, SubPanel_Save_Support(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[0])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Save Residual' or subpanelname == 2013:
			panelphase.pipelineitems.insert(idx, SubPanel_Save_Residual(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[0])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Co-ordinate Transformation' or subpanelname == 2001:
			panelphase.pipelineitems.insert(idx, SubPanel_Transform(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].rbfrom.SetStringSelection(object[0])
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[1])
			panelphase.pipelineitems[idx].output_filename_amp.objectpath.SetValue(object[2])
			panelphase.pipelineitems[idx].output_filename_phase.objectpath.SetValue(object[3])
			panelphase.pipelineitems[idx].rbcurve.SetStringSelection(object[4])
			panelphase.pipelineitems[idx].bdims[0].value.SetValue(object[5])
			panelphase.pipelineitems[idx].bdims[1].value.SetValue(object[6])
			panelphase.pipelineitems[idx].bdims[2].value.SetValue(object[7])
			panelphase.pipelineitems[idx].twotheta.value.SetValue(object[8])
			panelphase.pipelineitems[idx].dtheta.value.SetValue(object[9])
			panelphase.pipelineitems[idx].phi.value.SetValue(object[10])
			panelphase.pipelineitems[idx].dphi.value.SetValue(object[11])
			panelphase.pipelineitems[idx].pixelx.value.SetValue(object[12])
			panelphase.pipelineitems[idx].pixely.value.SetValue(object[13])
			panelphase.pipelineitems[idx].waveln.value.SetValue(object[14])
			panelphase.pipelineitems[idx].armln.value.SetValue(object[15])
			panelphase.pipelineitems[idx].chkbox_ccdflip.SetValue(object[16])
			try:
				panelphase.pipelineitems[idx].rbtype.SetStringSelection(object[17])
			except:
				pass
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Load Co-ordinates':
			panelphase.pipelineitems.insert(idx, SubPanel_Load_Coordinates(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].input_filename.objectpath.SetValue(object[0])
			DoListCheck(panelphase, object, idx)
		if subpanelname == 'Save Co-ordinates' or subpanelname == 2011:
			panelphase.pipelineitems.insert(idx, SubPanel_Save_Coordinates(panelphase.panel2))
			panelphase.pipelineitems[idx].Hide()
			panelphase.hbox2.Add(panelphase.pipelineitems[idx], 2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
			panelphase.pipelineitems[idx].output_filename.objectpath.SetValue(object[0])
			DoListCheck(panelphase, object, idx)
def SaveInstance(self):
	file_ext = os.path.splitext(self.filename)[1]
	if file_ext != ".fin":
		filename = self.filename + ".fin"
	else:
		filename = self.filename
	file = gzip.open(os.path.join(self.dirname, filename),'wb')
	instance_list = []
	panelphase = self.GetChildren()[1].GetPage(0)
	for i in range(len(panelphase.pipelineitems)):
		mainlist, object, subpanelname = GetInstanceObject(panelphase, i)
		instance_list.append([mainlist, object, subpanelname])
	pickle.dump(instance_list, file, protocol=2)
	file.close()
def DoListCheck(panelphase, object, idx):
	try:
		if (object[-1] == False):
			panelphase.mainlist.CheckItem(idx, check=False)
	except:
		pass
def RestoreInstance(self):
	subpanel_members = inspect.getmembers(sys.modules[ __name__ ], inspect.isclass)
	subpanel_items = []
	for item in subpanel_members:
		if hasattr(item[1], 'treeitem'):
			subpanel_items.append(item[1].treeitem['name'])
	file = gzip.open(os.path.join(self.dirname, self.filename),'rb')
	instance_list = pickle.load(file)
	panelphase = self.GetChildren()[1].GetPage(0)
	itemcount = panelphase.mainlist.GetItemCount()
	c = 0
	for i in range(len(instance_list)):
		if instance_list[i][2] in subpanel_items:
			SetInstanceObject(panelphase, instance_list[i], c+itemcount, subpanel_items)
			c += 1
	file.close()
