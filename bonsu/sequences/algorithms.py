#############################################
##   Filename: algorithms.py
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
import sys
import wx
import numpy
from numpy.distutils.system_info import get_info
import vtk
from ..interface.render import wxVTKRenderWindowInteractor
from vtk.util import numpy_support
import threading
from ..operations.HIO import HIO
from ..operations.HIO import HIOMask
from ..operations.HIO import HIOPlus
from ..operations.HIO import PCHIO
from ..operations.HIO import PGCHIO
from ..operations.HIO import HIOMaskPC
from ..operations.CSHIO import CSHIO
from ..operations.SO2D import SO2D
from ..operations.ER import ER
from ..operations.ER import ERMask
from ..operations.ER import ERMaskPC
from ..operations.POER import POER
from ..operations.HPR import HPR
from ..operations.HPR import HPRMaskPC
from ..operations.RAAR import RAAR
from ..operations.RAAR import RAARMaskPC
from ..operations.wrap import WrapArray
from ..operations.compact import CompactArray
from ..operations.loadarray import NewArray
from ..operations.loadarray import LoadArray
from ..interface.common import CNTR_CLIP
def PrepareVisualisation(self,pipelineitem):
	panelvisual = self.ancestor.GetPage(1)
	panelvisual.data = None
	panelvisual.widget.SetInteractor(panelvisual.renWin)
	panelvisual.widget.SetEnabled( 0 )
	r = float(panelvisual.r)/255.0
	g = float(panelvisual.g)/255.0
	b = float(panelvisual.b)/255.0
	panelvisual.renderer_amp_real.SetBackground(r, g, b)
	panelvisual.renderer_amp_recip.SetBackground(r, g, b)
	contour_real = CNTR_CLIP*numpy.max(numpy.abs(self.seqdata))
	contour_recip = contour_real
	if (self.visual_amp_real is not None) or (self.visual_amp_recip is not None) or (self.visual_support is not None):
		panelvisual.renderer_amp_real.RemoveAllViewProps()
		panelvisual.renderer_phase_real .RemoveAllViewProps()
		panelvisual.renderer_amp_recip.RemoveAllViewProps()
		panelvisual.renderer_phase_recip.RemoveAllViewProps()
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_recip)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_recip)
		panelvisual.renWin.GetRenderWindow().Modified()
		panelvisual.renWin.SetInteractorStyle(panelvisual.style3D)
		panelvisual.SetPhaseVisualButtons()
	if self.visual_amp_real is not None:
		self.visual_amp_real[:] = numpy.abs(self.seqdata)
		panelvisual.flat_data_amp_real = (self.visual_amp_real).transpose(2,1,0).flatten()
		panelvisual.vtk_data_array_amp_real = numpy_support.numpy_to_vtk(panelvisual.flat_data_amp_real)
		points_amp_real = panelvisual.image_amp_real.GetPointData()
		points_amp_real.SetScalars(panelvisual.vtk_data_array_amp_real)
		panelvisual.image_amp_real.SetDimensions(self.visual_amp_real.shape)
		panelvisual.image_amp_real.Modified()
		panelvisual.lut_amp_real.SetNumberOfTableValues(256)
		panelvisual.lut_amp_real.SetTableRange(panelvisual.image_amp_real.GetPointData().GetScalars().GetRange())
		lutsource = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[0][0]][1]
		if self.ancestor.GetPage(0).cmls[0][1] == 0:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(255-k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		panelvisual.lut_amp_real.SetRamp(0)
		panelvisual.lut_amp_real.Build()
		panelvisual.scalebar_amp_real.SetTitle("")
		panelvisual.scalebar_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		panelvisual.scalebar_amp_real.Modified()
		if panelvisual.VTKIsNot6:
			panelvisual.filter_amp_real.SetInput(panelvisual.image_amp_real)
		else:
			panelvisual.filter_amp_real.SetInputData(panelvisual.image_amp_real)
		panelvisual.filter_amp_real.ComputeNormalsOn()
		panelvisual.filter_amp_real.ComputeScalarsOn()
		panelvisual.filter_amp_real.SetNumberOfContours(1)
		panelvisual.filter_amp_real.SetValue( 0, contour_real)
		panelvisual.filter_amp_real.Modified()
		panelvisual.filter_amp_real.Update()
		panelvisual.smooth_filter_real.SetInputConnection(panelvisual.filter_amp_real.GetOutputPort())
		panelvisual.smooth_filter_real.SetNumberOfIterations(15)
		panelvisual.smooth_filter_real.SetRelaxationFactor(0.1)
		panelvisual.smooth_filter_real.FeatureEdgeSmoothingOff()
		panelvisual.smooth_filter_real.BoundarySmoothingOn()
		panelvisual.normals_amp_real.SetInputConnection(panelvisual.smooth_filter_real.GetOutputPort())
		panelvisual.normals_amp_real.SetFeatureAngle(90)
		panelvisual.normals_amp_real.ConsistencyOff()
		panelvisual.normals_amp_real.SplittingOff()
		panelvisual.normals_amp_real.AutoOrientNormalsOff()
		panelvisual.normals_amp_real.ComputePointNormalsOn()
		panelvisual.normals_amp_real.ComputeCellNormalsOff()
		panelvisual.normals_amp_real.NonManifoldTraversalOff()
		panelvisual.triangles_amp_real.SetInputConnection(panelvisual.normals_amp_real.GetOutputPort())
		panelvisual.strips_amp_real.SetInputConnection(panelvisual.triangles_amp_real.GetOutputPort())
		panelvisual.mapper_amp_real.SetInputConnection(panelvisual.strips_amp_real.GetOutputPort())
		panelvisual.mapper_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		panelvisual.mapper_amp_real.SetScalarRange(panelvisual.image_amp_real.GetPointData().GetScalars().GetRange())
		panelvisual.mapper_amp_real.SetScalarModeToUsePointData()
		panelvisual.mapper_amp_real.Modified()
		panelvisual.mapper_amp_real.Update()
		panelvisual.actor_amp_real.GetProperty().SetOpacity(1.0)
		panelvisual.actor_amp_real.SetMapper(panelvisual.mapper_amp_real)
		panelvisual.renderer_amp_real.AddActor(panelvisual.actor_amp_real)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.scalebar_amp_real)
		panelvisual.renderer_amp_real.GetActiveCamera().SetPosition(0,0,1)
		panelvisual.renderer_amp_real.GetActiveCamera().SetViewUp(0,1,0)
		panelvisual.renderer_amp_real.GetActiveCamera().SetFocalPoint(0,0,0)
	if self.visual_phase_real is not None:
		self.visual_phase_real[:] = numpy.angle(self.seqdata)
		panelvisual.flat_data_phase_real = (self.visual_phase_real).transpose(2,1,0).flatten()
		panelvisual.vtk_data_array_phase_real = numpy_support.numpy_to_vtk(panelvisual.flat_data_phase_real)
		panelvisual.vtk_data_array_phase_real.SetName("mapscalar")
		points_amp_real = panelvisual.image_amp_real.GetPointData()
		points_amp_real.AddArray(panelvisual.vtk_data_array_phase_real)
		panelvisual.image_amp_real.Modified()
		panelvisual.lut_phase_real.SetNumberOfTableValues(256)
		panelvisual.lut_phase_real.SetTableRange([-numpy.pi,numpy.pi])
		lutsource = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[1][0]][1]
		if self.ancestor.GetPage(0).cmls[1][1] == 0:
			for k in range(256):
				panelvisual.lut_phase_real.SetTableValue(k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_phase_real.SetTableValue(255-k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		panelvisual.lut_phase_real.SetRamp(0)
		panelvisual.lut_phase_real.Build()
		panelvisual.scalebar_amp_real.SetLookupTable(panelvisual.lut_phase_real)
		panelvisual.scalebar_amp_real.Modified()
		panelvisual.filter_amp_real.Modified()
		panelvisual.filter_amp_real.Update()
		panelvisual.mapper_amp_real.SetScalarRange([-numpy.pi,numpy.pi])
		panelvisual.mapper_amp_real.SetLookupTable(panelvisual.lut_phase_real)
		panelvisual.mapper_amp_real.SelectColorArray("mapscalar")
		panelvisual.mapper_amp_real.SetScalarModeToUsePointFieldData()
		panelvisual.mapper_amp_real.Modified()
		panelvisual.mapper_amp_real.Update()
	if self.visual_amp_recip is not None:
		self.visual_amp_recip[:] = numpy.abs(self.seqdata)
		panelvisual.flat_data_amp_recip= (self.visual_amp_recip).transpose(2,1,0).flatten();
		panelvisual.vtk_data_array_amp_recip = numpy_support.numpy_to_vtk(panelvisual.flat_data_amp_recip)
		panelvisual.points_amp_recip = panelvisual.image_amp_recip.GetPointData()
		panelvisual.points_amp_recip.SetScalars(panelvisual.vtk_data_array_amp_recip)
		panelvisual.image_amp_recip.SetDimensions(self.visual_amp_recip.shape)
		panelvisual.image_amp_recip.Modified()
		panelvisual.lut_amp_recip.SetNumberOfTableValues(256)
		panelvisual.lut_amp_recip.SetTableRange(panelvisual.image_amp_recip.GetPointData().GetScalars().GetRange())
		lutsource = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[2][0]][1]
		if self.ancestor.GetPage(0).cmls[2][1] == 0:
			for k in range(256):
				panelvisual.lut_amp_recip.SetTableValue(k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_amp_recip.SetTableValue(255-k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		panelvisual.lut_amp_recip.SetRamp(0)
		panelvisual.lut_amp_recip.Build()
		panelvisual.scalebar_amp_recip.SetTitle("")
		panelvisual.scalebar_amp_recip.SetLookupTable(panelvisual.lut_amp_recip)
		if panelvisual.VTKIsNot6:
			panelvisual.filter_amp_recip.SetInput(panelvisual.image_amp_recip)
		else:
			panelvisual.filter_amp_recip.SetInputData(panelvisual.image_amp_recip)
		panelvisual.filter_amp_recip.ComputeNormalsOn()
		panelvisual.filter_amp_recip.ComputeScalarsOn()
		panelvisual.filter_amp_recip.SetNumberOfContours(1)
		panelvisual.filter_amp_recip.SetValue( 0, contour_recip)
		panelvisual.filter_amp_recip.Modified()
		panelvisual.filter_amp_recip.Update()
		panelvisual.smooth_filter_recip.SetInputConnection(panelvisual.filter_amp_recip.GetOutputPort())
		panelvisual.smooth_filter_recip.SetNumberOfIterations(15)
		panelvisual.smooth_filter_recip.SetRelaxationFactor(0.1)
		panelvisual.smooth_filter_recip.FeatureEdgeSmoothingOff()
		panelvisual.smooth_filter_recip.BoundarySmoothingOn()
		panelvisual.normals_amp_recip.SetInputConnection(panelvisual.smooth_filter_recip.GetOutputPort())
		panelvisual.normals_amp_recip.SetFeatureAngle(90)
		panelvisual.normals_amp_recip.ConsistencyOff()
		panelvisual.normals_amp_recip.SplittingOff()
		panelvisual.normals_amp_recip.AutoOrientNormalsOff()
		panelvisual.normals_amp_recip.ComputePointNormalsOn()
		panelvisual.normals_amp_recip.ComputeCellNormalsOff()
		panelvisual.normals_amp_recip.NonManifoldTraversalOff()
		panelvisual.triangles_amp_recip.SetInputConnection(panelvisual.normals_amp_recip.GetOutputPort())
		panelvisual.strips_amp_recip.SetInputConnection(panelvisual.triangles_amp_recip.GetOutputPort())
		panelvisual.mapper_amp_recip.SetInputConnection(panelvisual.strips_amp_recip.GetOutputPort())
		panelvisual.mapper_amp_recip.SetLookupTable(panelvisual.lut_amp_recip)
		panelvisual.mapper_amp_recip.SetScalarRange(panelvisual.image_amp_recip.GetPointData().GetScalars().GetRange())
		panelvisual.mapper_amp_recip.SetScalarModeToUsePointData()
		panelvisual.mapper_amp_recip.Modified()
		panelvisual.mapper_amp_recip.Update()
		panelvisual.actor_amp_recip.SetMapper(panelvisual.mapper_amp_recip)
		panelvisual.actor_amp_recip.GetProperty().SetOpacity(1.0)
		panelvisual.renderer_amp_recip.AddActor(panelvisual.actor_amp_recip)
		panelvisual.renderer_amp_recip.AddActor2D(panelvisual.scalebar_amp_recip)
		panelvisual.renderer_amp_recip.GetActiveCamera().SetPosition(0,0,1)
		panelvisual.renderer_amp_recip.GetActiveCamera().SetViewUp(0,1,0)
		panelvisual.renderer_amp_recip.GetActiveCamera().SetFocalPoint(0,0,0)
	if self.visual_phase_recip is not None:
		self.visual_phase_recip[:] = numpy.angle(self.seqdata)
		panelvisual.flat_data_phase_recip = (self.visual_phase_recip).transpose(2,1,0).flatten()
		panelvisual.vtk_data_array_phase_recip = numpy_support.numpy_to_vtk(panelvisual.flat_data_phase_recip)
		panelvisual.vtk_data_array_phase_recip.SetName("mapscalar")
		points_amp_recip = panelvisual.image_amp_recip.GetPointData()
		points_amp_recip.AddArray(panelvisual.vtk_data_array_phase_recip)
		panelvisual.image_amp_recip.Modified()
		panelvisual.lut_phase_recip.SetNumberOfTableValues(256)
		panelvisual.lut_phase_recip.SetTableRange([-numpy.pi,numpy.pi])
		lutsource = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[3][0]][1]
		if self.ancestor.GetPage(0).cmls[3][1] == 0:
			for k in range(256):
				panelvisual.lut_phase_recip.SetTableValue(k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_phase_recip.SetTableValue(255-k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		panelvisual.lut_phase_recip.SetRamp(0)
		panelvisual.lut_phase_recip.Build()
		panelvisual.scalebar_amp_recip.SetLookupTable(panelvisual.lut_phase_recip)
		panelvisual.scalebar_amp_recip.Modified()
		panelvisual.filter_amp_recip.Modified()
		panelvisual.filter_amp_recip.Update()
		panelvisual.mapper_amp_recip.SetScalarRange([-numpy.pi,numpy.pi])
		panelvisual.mapper_amp_recip.SetLookupTable(panelvisual.lut_phase_recip)
		panelvisual.mapper_amp_recip.SelectColorArray("mapscalar")
		panelvisual.mapper_amp_recip.SetScalarModeToUsePointFieldData()
		panelvisual.mapper_amp_recip.Modified()
		panelvisual.mapper_amp_recip.Update()
	if self.visual_support is not None:
		self.visual_support[:] = numpy.array(self.support.real, copy=False)
		panelvisual.flat_data_support= (self.visual_support).transpose(2,1,0).flatten();
		panelvisual.vtk_data_array_support = numpy_support.numpy_to_vtk(panelvisual.flat_data_support)
		panelvisual.points_support = panelvisual.image_support.GetPointData()
		panelvisual.points_support.SetScalars(panelvisual.vtk_data_array_support)
		panelvisual.image_support.SetDimensions(self.visual_support.shape)
		panelvisual.image_support.Modified()
		if panelvisual.VTKIsNot6:
			panelvisual.filter_support.SetInput(panelvisual.image_support)
		else:
			panelvisual.filter_support.SetInputData(panelvisual.image_support)
		panelvisual.filter_support.ComputeNormalsOn()
		panelvisual.filter_support.ComputeScalarsOn()
		panelvisual.filter_support.SetNumberOfContours(1)
		panelvisual.filter_support.SetValue( 0, 1.0)
		panelvisual.filter_support.Update()
		panelvisual.smooth_filter_support.SetInputConnection(panelvisual.filter_support.GetOutputPort())
		panelvisual.smooth_filter_support.SetNumberOfIterations(15)
		panelvisual.smooth_filter_support.SetRelaxationFactor(0.1)
		panelvisual.smooth_filter_support.FeatureEdgeSmoothingOff()
		panelvisual.smooth_filter_support.BoundarySmoothingOn()
		panelvisual.normals_support.SetInputConnection(panelvisual.smooth_filter_support.GetOutputPort())
		panelvisual.normals_support.SetFeatureAngle(90)
		panelvisual.normals_support.ConsistencyOff()
		panelvisual.normals_support.SplittingOff()
		panelvisual.normals_support.AutoOrientNormalsOff()
		panelvisual.normals_support.ComputePointNormalsOn()
		panelvisual.normals_support.ComputeCellNormalsOff()
		panelvisual.normals_support.NonManifoldTraversalOff()
		panelvisual.triangles_support.SetInputConnection(panelvisual.normals_support.GetOutputPort())
		panelvisual.strips_support.SetInputConnection(panelvisual.triangles_support.GetOutputPort())
		panelvisual.mapper_support.SetInputConnection(panelvisual.strips_support.GetOutputPort())
		panelvisual.mapper_support.SetScalarRange(panelvisual.image_support.GetPointData().GetScalars().GetRange())
		panelvisual.actor_support.SetMapper(panelvisual.mapper_support)
		panelvisual.actor_support.GetProperty().SetOpacity(0.05)
		panelvisual.renderer_amp_real.AddActor( panelvisual.actor_support )
	if self.visual_amp_real is not None or self.visual_support is not None:
		if self.visual_phase_real is not None:
			panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_phase_real)
			panelvisual.renderer_phase_real.SetViewport(1,1,1,1)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_real)
		panelvisual.renderer_amp_real.ResetCamera()
		panelvisual.hboxrender.Layout()
		panelvisual.Layout()
		panelvisual.Show()
	if  self.visual_amp_recip is not None:
		if self.visual_phase_recip is not None:
			panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_phase_recip)
			panelvisual.renderer_phase_recip.SetViewport(1,1,1,1)
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_recip)
		panelvisual.renderer_amp_recip.ResetCamera()
		panelvisual.hboxrender.Layout()
		panelvisual.Layout()
		panelvisual.Show()
	if (self.visual_amp_real is not None or self.visual_support is not None) and self.visual_amp_recip is not None:
		panelvisual.renderer_amp_real.SetViewport(0,0,0.5,1)
		panelvisual.renderer_amp_recip.SetViewport(0.5,0,1,1)
	if (self.visual_amp_real is not None or self.visual_support is not None) and self.visual_amp_recip is None:
		panelvisual.renderer_amp_real.SetViewport(0,0,1,1)
		panelvisual.renderer_amp_recip.SetViewport(0,0,0,0)
	if (self.visual_amp_real is None and self.visual_support is None) and self.visual_amp_recip is not None:
		panelvisual.renderer_amp_real.SetViewport(0,0,0,0)
		panelvisual.renderer_amp_recip.SetViewport(0,0,1,1)
	panelvisual.RefreshSceneFull(gotovisual=True)
def PrepareVisualisation2D(self,pipelineitem):
	panelvisual = self.ancestor.GetPage(1)
	panelvisual.data = None
	panelvisual.widget.SetInteractor(panelvisual.renWin)
	panelvisual.widget.SetEnabled( 0 )
	r = float(panelvisual.r)/255.0
	g = float(panelvisual.g)/255.0
	b = float(panelvisual.b)/255.0
	panelvisual.renderer_amp_real.SetBackground(r, g, b)
	panelvisual.renderer_phase_real.SetBackground(r, g, b)
	panelvisual.renderer_amp_recip.SetBackground(r, g, b)
	panelvisual.renderer_phase_recip.SetBackground(r, g, b)
	if (self.visual_amp_real is not None) or (self.visual_amp_recip is not None) or (self.visual_support is not None):
		panelvisual.renderer_amp_real.RemoveAllViewProps()
		panelvisual.renderer_phase_real .RemoveAllViewProps()
		panelvisual.renderer_amp_recip.RemoveAllViewProps()
		panelvisual.renderer_phase_recip.RemoveAllViewProps()
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_real)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_amp_recip)
		panelvisual.renWin.GetRenderWindow().RemoveRenderer(panelvisual.renderer_phase_recip)
		panelvisual.renWin.GetRenderWindow().Modified()
		panelvisual.renWin.SetInteractorStyle(panelvisual.style2D)
		panelvisual.SetPhaseVisualButtons()
	if self.visual_amp_real is not None:
		panelvisual.flat_data_amp_real = (self.visual_amp_real).transpose(2,1,0).flatten();
		panelvisual.vtk_data_array_amp_real = numpy_support.numpy_to_vtk(panelvisual.flat_data_amp_real)
		points_amp_real = panelvisual.image_amp_real.GetPointData()
		points_amp_real.SetScalars(panelvisual.vtk_data_array_amp_real)
		panelvisual.image_amp_real.SetDimensions(self.visual_amp_real.shape)
		panelvisual.image_amp_real.Modified()
		panelvisual.lut_amp_real.SetNumberOfTableValues(256)
		panelvisual.lut_amp_real.SetTableRange(panelvisual.image_amp_real.GetPointData().GetScalars().GetRange())
		lutsource = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[0][0]][1]
		if self.ancestor.GetPage(0).cmls[0][1] == 0:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_amp_real.SetTableValue(255-k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		panelvisual.lut_amp_real.SetRamp(0)
		panelvisual.lut_amp_real.Build()
		panelvisual.scalebar_amp_real.SetTitle("")
		panelvisual.scalebar_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		panelvisual.color_amp_real.SetLookupTable(panelvisual.lut_amp_real)
		if panelvisual.VTKIsNot6:
			panelvisual.color_amp_real.SetInput(panelvisual.image_amp_real)
		else:
			panelvisual.color_amp_real.SetInputData(panelvisual.image_amp_real)
		panelvisual.color_amp_real.Update()
		if panelvisual.VTKIsNot6:
			panelvisual.mapper2D_amp_real.SetInputConnection(panelvisual.color_amp_real.GetOutputPort())
			panelvisual.actor2D_amp_real.SetInput(panelvisual.mapper2D_amp_real.GetInput())
		else:
			panelvisual.actor2D_amp_real.GetMapper().SetInputConnection(panelvisual.color_amp_real.GetOutputPort())
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.actor2D_amp_real)
		panelvisual.renderer_amp_real.AddActor2D(panelvisual.scalebar_amp_real)
		panelvisual.renderer_amp_real.GetActiveCamera().SetPosition(0,0,1)
		panelvisual.renderer_amp_real.GetActiveCamera().SetViewUp(0,1,0)
		panelvisual.renderer_amp_real.GetActiveCamera().SetFocalPoint(0,0,0)
	if self.visual_phase_real is not None:
		panelvisual.flat_data_phase_real = (self.visual_phase_real).transpose(2,1,0).flatten();
		panelvisual.vtk_data_array_phase_real = numpy_support.numpy_to_vtk(panelvisual.flat_data_phase_real)
		points_phase_real = panelvisual.image_phase_real.GetPointData()
		points_phase_real.SetScalars(panelvisual.vtk_data_array_phase_real)
		panelvisual.image_phase_real.SetDimensions(self.visual_phase_real.shape)
		panelvisual.image_phase_real.Modified()
		panelvisual.lut_phase_real.SetNumberOfTableValues(256)
		panelvisual.lut_phase_real.SetTableRange(panelvisual.image_phase_real.GetPointData().GetScalars().GetRange())
		lutsource = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[1][0]][1]
		if self.ancestor.GetPage(0).cmls[1][1] == 0:
			for k in range(256):
				panelvisual.lut_phase_real.SetTableValue(k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_phase_real.SetTableValue(255-k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		panelvisual.lut_phase_real.SetRamp(0)
		panelvisual.lut_phase_real.Build()
		panelvisual.scalebar_phase_real.SetTitle("")
		panelvisual.scalebar_phase_real.SetLookupTable(panelvisual.lut_phase_real)
		panelvisual.color_phase_real.SetLookupTable(panelvisual.lut_phase_real)
		if panelvisual.VTKIsNot6:
			panelvisual.color_phase_real.SetInput(panelvisual.image_phase_real)
		else:
			panelvisual.color_phase_real.SetInputData(panelvisual.image_phase_real)
		if panelvisual.VTKIsNot6:
			panelvisual.mapper2D_phase_real.SetInputConnection(panelvisual.color_phase_real.GetOutputPort())
			panelvisual.actor2D_phase_real.SetInput(panelvisual.mapper2D_phase_real.GetInput())
		else:
			panelvisual.actor2D_phase_real.GetMapper().SetInputConnection(panelvisual.color_phase_real.GetOutputPort())
		panelvisual.renderer_phase_real.AddActor2D(panelvisual.actor2D_phase_real)
		panelvisual.renderer_phase_real.AddActor2D(panelvisual.scalebar_phase_real)
		panelvisual.renderer_phase_real.GetActiveCamera().SetPosition(0,0,1)
		panelvisual.renderer_phase_real.GetActiveCamera().SetViewUp(0,1,0)
		panelvisual.renderer_phase_real.GetActiveCamera().SetFocalPoint(0,0,0)
	if self.visual_amp_recip is not None:
		panelvisual.flat_data_amp_recip= (self.visual_amp_recip).transpose(2,1,0).flatten();
		panelvisual.vtk_data_array_amp_recip = numpy_support.numpy_to_vtk(panelvisual.flat_data_amp_recip)
		panelvisual.points_amp_recip = panelvisual.image_amp_recip.GetPointData()
		panelvisual.points_amp_recip.SetScalars(panelvisual.vtk_data_array_amp_recip)
		panelvisual.image_amp_recip.SetDimensions(self.visual_amp_recip.shape)
		panelvisual.image_amp_recip.Modified()
		panelvisual.lut_amp_recip.SetNumberOfTableValues(256)
		panelvisual.lut_amp_recip.SetTableRange(panelvisual.image_amp_recip.GetPointData().GetScalars().GetRange())
		lutsource = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[2][0]][1]
		if self.ancestor.GetPage(0).cmls[2][1] == 0:
			for k in range(256):
				panelvisual.lut_amp_recip.SetTableValue(k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_amp_recip.SetTableValue(255-k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		panelvisual.lut_amp_recip.SetRamp(0)
		panelvisual.lut_amp_recip.Build()
		panelvisual.scalebar_amp_recip.SetTitle("")
		panelvisual.scalebar_amp_recip.SetLookupTable(panelvisual.lut_amp_recip)
		panelvisual.color_amp_recip.SetLookupTable(panelvisual.lut_amp_recip)
		if panelvisual.VTKIsNot6:
			panelvisual.color_amp_recip.SetInput(panelvisual.image_amp_recip)
		else:
			panelvisual.color_amp_recip.SetInputData(panelvisual.image_amp_recip)
		if panelvisual.VTKIsNot6:
			panelvisual.mapper2D_amp_recip.SetInputConnection(panelvisual.color_amp_recip.GetOutputPort())
			panelvisual.actor2D_amp_recip.SetInput(panelvisual.mapper2D_amp_recip.GetInput())
		else:
			panelvisual.actor2D_amp_recip.GetMapper().SetInputConnection(panelvisual.color_amp_recip.GetOutputPort())
		panelvisual.renderer_amp_recip.AddActor2D(panelvisual.actor2D_amp_recip)
		panelvisual.renderer_amp_recip.AddActor2D(panelvisual.scalebar_amp_recip)
		panelvisual.renderer_amp_recip.GetActiveCamera().SetPosition(0,0,1)
		panelvisual.renderer_amp_recip.GetActiveCamera().SetViewUp(0,1,0)
		panelvisual.renderer_amp_recip.GetActiveCamera().SetFocalPoint(0,0,0)
	if self.visual_phase_recip is not None:
		panelvisual.flat_data_phase_recip = (self.visual_phase_recip).transpose(2,1,0).flatten();
		panelvisual.vtk_data_array_phase_recip = numpy_support.numpy_to_vtk(panelvisual.flat_data_phase_recip)
		points_phase_recip = panelvisual.image_phase_recip.GetPointData()
		points_phase_recip.SetScalars(panelvisual.vtk_data_array_phase_recip)
		panelvisual.image_phase_recip.SetDimensions(self.visual_phase_recip.shape)
		panelvisual.image_phase_recip.Modified()
		panelvisual.lut_phase_recip.SetNumberOfTableValues(256)
		panelvisual.lut_phase_recip.SetTableRange(panelvisual.image_phase_recip.GetPointData().GetScalars().GetRange())
		lutsource = self.ancestor.GetPage(0).cms[self.ancestor.GetPage(0).cmls[3][0]][1]
		if self.ancestor.GetPage(0).cmls[3][1] == 0:
			for k in range(256):
				panelvisual.lut_phase_recip.SetTableValue(k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		else:
			for k in range(256):
				panelvisual.lut_phase_recip.SetTableValue(255-k, lutsource[k][0], lutsource[k][1], lutsource[k][2], 1)
		panelvisual.lut_phase_recip.SetRamp(0)
		panelvisual.lut_phase_recip.Build()
		panelvisual.scalebar_phase_recip.SetTitle("")
		panelvisual.scalebar_phase_recip.SetLookupTable(panelvisual.lut_phase_recip)
		panelvisual.color_phase_recip.SetLookupTable(panelvisual.lut_phase_recip)
		if panelvisual.VTKIsNot6:
			panelvisual.color_phase_recip.SetInput(panelvisual.image_phase_recip)
		else:
			panelvisual.color_phase_recip.SetInputData(panelvisual.image_phase_recip)
		if panelvisual.VTKIsNot6:
			panelvisual.mapper2D_phase_recip.SetInputConnection(panelvisual.color_phase_recip.GetOutputPort())
			panelvisual.actor2D_phase_recip.SetInput(panelvisual.mapper2D_phase_recip.GetInput())
		else:
			panelvisual.actor2D_phase_recip.GetMapper().SetInputConnection(panelvisual.color_phase_recip.GetOutputPort())
		panelvisual.renderer_phase_recip.AddActor2D(panelvisual.actor2D_phase_recip)
		panelvisual.renderer_phase_recip.AddActor2D(panelvisual.scalebar_phase_recip)
		panelvisual.renderer_phase_recip.GetActiveCamera().SetPosition(0,0,1)
		panelvisual.renderer_phase_recip.GetActiveCamera().SetViewUp(0,1,0)
		panelvisual.renderer_phase_recip.GetActiveCamera().SetFocalPoint(0,0,0)
	if self.visual_amp_real is not None:
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_real)
		panelvisual.renderer_amp_real.ResetCamera()
		panelvisual.hboxrender.Layout()
		panelvisual.Layout()
		panelvisual.Show()
	if self.visual_phase_real is not None:
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_phase_real)
		panelvisual.renderer_phase_real.ResetCamera()
		panelvisual.hboxrender.Layout()
		panelvisual.Layout()
		panelvisual.Show()
	if  self.visual_amp_recip is not None:
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_amp_recip)
		panelvisual.renderer_amp_recip.ResetCamera()
		panelvisual.hboxrender.Layout()
		panelvisual.Layout()
		panelvisual.Show()
	if  self.visual_phase_recip is not None:
		panelvisual.renWin.GetRenderWindow().AddRenderer(panelvisual.renderer_phase_recip)
		panelvisual.renderer_phase_recip.ResetCamera()
		panelvisual.hboxrender.Layout()
		panelvisual.Layout()
		panelvisual.Show()
	if (self.visual_amp_real is not None) and (self.visual_amp_recip is not None) and (self.visual_phase_real is not None) and (self.visual_phase_recip is not None):
		panelvisual.renderer_amp_real.SetViewport(0,0.5,0.5,1.0)
		panelvisual.renderer_phase_real.SetViewport(0.5,0.5,1,1.0)
		panelvisual.renderer_amp_recip.SetViewport(0,0,0.5,0.5)
		panelvisual.renderer_phase_recip.SetViewport(0.5,0,1,0.5)
	elif (self.visual_amp_real is not None) and (self.visual_phase_real is not None):
		panelvisual.renderer_amp_real.SetViewport(0,0,0.5,1)
		panelvisual.renderer_phase_real.SetViewport(0.5,0,1,1)
	elif (self.visual_amp_recip is not None) and (self.visual_phase_recip is not None):
		panelvisual.renderer_amp_recip.SetViewport(0,0,0.5,1)
		panelvisual.renderer_phase_recip.SetViewport(0.5,0,1,1)
	elif (self.visual_amp_real is not None) and (self.visual_amp_recip is not None):
		panelvisual.renderer_amp_real.SetViewport(0,0,0.5,1)
		panelvisual.renderer_amp_recip.SetViewport(0.5,0,1,1)
	elif (self.visual_amp_real is not None):
		panelvisual.renderer_amp_real.SetViewport(0,0,1,1)
	panelvisual.RefreshSceneFull(gotovisual=True)
class SequenceBase():
	def __init__(self, parent, pipelineitem):
		self.parent = parent
		self.pipelineitem = pipelineitem
		if parent.pipeline_started == True:
			if parent.citer_flow[1] == 2: return;
			self.expdata_path = pipelineitem.exp_amps.objectpath.GetValue()
			if self.LoadExpData():
				self.parent.pipeline_started = False
				return
			self.support_path = pipelineitem.support.objectpath.GetValue()
			if self.LoadSupport():
				self.parent.pipeline_started = False
				return
			if self.ShapeCheck():
				self.parent.pipeline_started = False
				return
			self.startiter = int(self.pipelineitem.start_iter)
			self.numiter = int(self.pipelineitem.niter.value.GetValue())
			self.Prepare()
	def LoadExpData(self):
		try:
			self.parent.expdata = LoadArray(self.parent, self.expdata_path)
			if self.pipelineitem.chkbox_sqrt_expamps.GetValue() == True:
				numpy.sqrt(self.parent.expdata, self.parent.expdata)
			self.parent.expdata[:] = WrapArray(self.parent.expdata).copy()
		except:
			msg = "Could not load array from: \n"+ self.expdata_path + "\nPlease check the log."
			self.MsgDlg(msg)
			return True
		else:
			return False
	def LoadSupport(self):
		if self.support_path == "":
			try:
				assert type(self.parent.support).__module__ == numpy.__name__
			except:
				msg = "No existing Support array found."
				self.MsgDlg(msg)
				return True
		else:
			try:
				self.parent.support = LoadArray(self.parent, self.support_path)
			except:
				msg = "Could not load array from: \n"+ self.support_path + "\nPlease check the log."
				self.MsgDlg(msg)
				return True
			else:
				return False
	def ShapeCheck(self):
		if (not self.parent.expdata.shape == self.parent.support.shape) == True:
			msg = "Array dimensions are inconsistent."
			self.MsgDlg(msg)
			self.parent.seqdata = None
			try:
				self.parent.visual_amp_real = None
			except:
				pass
			try:
				self.parent.visual_amp_recip = None
			except:
				pass
			try:
				self.parent.visual_amp_support = None
			except:
				pass
			return True
	def Prepare(self):
		if self.startiter == 0 and (self.parent.visual_amp_real is not None or self.parent.visual_support is not None or self.parent.visual_amp_recip is not None):
			if self.parent.expdata.shape[2] == 1:
				PrepareVisualisation2D(self.parent,self.pipelineitem)
			else:
				PrepareVisualisation(self.parent,self.pipelineitem)
	def MsgDlg(self, msg):
		dlg = wx.MessageDialog(self.parent, msg, "Pipeline Message", wx.OK)
		dlg.ShowModal()
		dlg.Destroy()
	def ThreadAlg(self):
		pass
	def StartPhasing(self):
		self.thread = threading.Thread(target=self.ThreadAlg)
		self.thread.daemon = True
		self.thread.start()
class SequenceBaseMask(SequenceBase):
	def __init__(self, parent, pipelineitem):
		self.parent = parent
		self.pipelineitem = pipelineitem
		if parent.pipeline_started == True:
			if parent.citer_flow[1] == 2: return;
			self.mask_path = self.pipelineitem.mask.objectpath.GetValue()
			if self.LoadMask():
				self.parent.pipeline_started = False
				return
		SequenceBase.__init__(self, parent, pipelineitem)
	def ShapeCheck(self):
		if (not (self.parent.expdata.shape == self.parent.support.shape and self.parent.expdata.shape == self.parent.mask.shape)) == True:
			msg = "Array dimensions are inconsistent."
			self.MsgDlg(msg)
			self.parent.seqdata = None
			try:
				self.parent.visual_amp_real = None
			except:
				pass
			try:
				self.parent.visual_amp_recip = None
			except:
				pass
			try:
				self.parent.visual_amp_support = None
			except:
				pass
			return True
	def LoadMask(self):
		try:
			self.parent.mask = LoadArray(self.parent, self.mask_path)
			self.parent.mask[:] = WrapArray(self.parent.mask).copy()
		except:
			msg = "Could not load array from: \n"+ self.mask_path + "\nPlease check the log."
			self.MsgDlg(msg)
			return True
		else:
			return False
class SequenceBasePC(SequenceBaseMask):
	def __init__(self, parent, pipelineitem):
		self.parent = parent
		self.pipelineitem = pipelineitem
		if parent.pipeline_started == True:
			if parent.citer_flow[1] == 2: return;
			self.expdata_path = pipelineitem.exp_amps.objectpath.GetValue()
			if self.LoadExpData():
				self.parent.pipeline_started = False
				return
			self.support_path = pipelineitem.support.objectpath.GetValue()
			if self.LoadSupport():
				self.parent.pipeline_started = False
				return
			self.gammaHWHM = float(self.pipelineitem.gammaHWHM.value.GetValue())
			if self.LoadPSF():
				self.parent.pipeline_started = False
				return
			self.mask_path = self.pipelineitem.mask.objectpath.GetValue()
			if self.LoadMask():
				self.parent.pipeline_started = False
				return
			if self.ShapeCheck():
				self.parent.pipeline_started = False
				return
			self.startiter = int(self.pipelineitem.start_iter)
			self.numiter = int(self.pipelineitem.niter.value.GetValue())
			self.Prepare()
			self.niterrlpre = int(self.pipelineitem.niterrlpre.value.GetValue())
			self.niterrl = int(self.pipelineitem.niterrl.value.GetValue())
			self.niterrlinterval = int(self.pipelineitem.niterrlinterval.value.GetValue())
			self.accel = int(self.pipelineitem.accel.value.GetValue())
			self.zex =  int(self.pipelineitem.zedims[0].value.GetValue())
			self.zey =  int(self.pipelineitem.zedims[1].value.GetValue())
			self.zez =  int(self.pipelineitem.zedims[2].value.GetValue())
			if self.pipelineitem.chkbox_reset_gamma.GetValue() == True:
				self.reset_gamma = 1
			else:
				self.reset_gamma = 0
	def ShapeCheck(self):
		if (not (self.parent.expdata.shape == self.parent.support.shape and self.parent.expdata.shape == self.parent.mask.shape and self.parent.expdata.shape == self.parent.psf.shape)) == True:
			msg = "Array dimensions are inconsistent."
			self.MsgDlg(msg)
			self.parent.seqdata = None
			try:
				self.parent.visual_amp_real = None
			except:
				pass
			try:
				self.parent.visual_amp_recip = None
			except:
				pass
			try:
				self.parent.visual_amp_support = None
			except:
				pass
			return True
	def LoadPSF(self):
		try:
			from ..lib.prfftw import lorentzftfill
			if self.parent.psf is None:
				self.parent.psf = NewArray(self.parent, *self.parent.seqdata.shape)
				lorentzftfill(self.parent.psf,self.gammaHWHM)
		except MemoryError:
			msg = "Could not load PSF array. Insufficient memory."
			self.MsgDlg(msg)
			return True
		else:
			return False
class Sequence_HIO(SequenceBase):
	def __init__(self, parent, pipelineitem):
		SequenceBase.__init__(self, parent, pipelineitem)
		if parent.pipeline_started == True:
			if parent.citer_flow[1] == 2: return;
			self.beta = float(self.pipelineitem.beta.value.GetValue())
			self.StartPhasing()
	def ThreadAlg(self):
		self.parent.ancestor.GetPage(0).queue_info.put("Starting HIO Algorithm...")
		self.parent.thread_register.put(1)
		HIO(self.parent, self.beta, self.startiter, self.numiter)
		self.parent.thread_register.get()
class Sequence_ER(SequenceBase):
	def __init__(self, parent, pipelineitem):
		SequenceBase.__init__(self, parent, pipelineitem)
		if parent.pipeline_started == True:
			if parent.citer_flow[1] == 2: return;
			self.StartPhasing()
	def ThreadAlg(self):
		self.parent.ancestor.GetPage(0).queue_info.put("Starting ER Algorithm...")
		self.parent.thread_register.put(1)
		ER(self.parent, self.startiter, self.numiter)
		self.parent.thread_register.get()
class Sequence_ERMask(SequenceBaseMask):
	def __init__(self, parent, pipelineitem):
		SequenceBaseMask.__init__(self, parent, pipelineitem)
		if parent.pipeline_started == True:
			if parent.citer_flow[1] == 2: return;
			if pipelineitem.chkbox.GetValue():
				self.numiter_relax = int(pipelineitem.niter_relax.value.GetValue())
			else:
				self.numiter_relax = 0
			self.StartPhasing()
	def ThreadAlg(self):
		self.parent.ancestor.GetPage(0).queue_info.put("Starting ER Mask Algorithm...")
		self.parent.thread_register.put(1)
		ERMask(self.parent, self.startiter, self.numiter, self.numiter_relax)
		self.parent.thread_register.get()
class Sequence_HIOMask(SequenceBaseMask):
	def __init__(self, parent, pipelineitem):
		SequenceBaseMask.__init__(self, parent, pipelineitem)
		if parent.pipeline_started == True:
			if parent.citer_flow[1] == 2: return;
			self.beta = float(self.pipelineitem.beta.value.GetValue())
			if pipelineitem.chkbox.GetValue():
				self.numiter_relax = int(pipelineitem.niter_relax.value.GetValue())
			else:
				self.numiter_relax = 0
			self.StartPhasing()
	def ThreadAlg(self):
		self.parent.ancestor.GetPage(0).queue_info.put("Starting HIO Algorithm...")
		self.parent.thread_register.put(1)
		HIOMask(self.parent, self.beta, self.startiter, self.numiter, self.numiter_relax)
		self.parent.thread_register.get()
class Sequence_HIOPlus(SequenceBaseMask):
	def __init__(self, parent, pipelineitem):
		SequenceBaseMask.__init__(self, parent, pipelineitem)
		if parent.pipeline_started == True:
			if parent.citer_flow[1] == 2: return;
			self.beta = float(self.pipelineitem.beta.value.GetValue())
			self.StartPhasing()
	def ThreadAlg(self):
		self.parent.ancestor.GetPage(0).queue_info.put("Starting HIO+ Algorithm...")
		self.parent.thread_register.put(1)
		HIOPlus(self.parent, self.beta, self.startiter, self.numiter)
		self.parent.thread_register.get()
class Sequence_HPR(SequenceBaseMask):
	def __init__(self, parent, pipelineitem):
		SequenceBaseMask.__init__(self, parent, pipelineitem)
		if parent.pipeline_started == True:
			if parent.citer_flow[1] == 2: return;
			self.beta = float(self.pipelineitem.beta.value.GetValue())
			if pipelineitem.chkbox.GetValue():
				self.numiter_relax = int(pipelineitem.niter_relax.value.GetValue())
			else:
				self.numiter_relax = 0
			self.StartPhasing()
	def ThreadAlg(self):
		self.parent.ancestor.GetPage(0).queue_info.put("Starting HPR Algorithm...")
		self.parent.thread_register.put(1)
		HPR(self.parent, self.beta, self.startiter, self.numiter, self.numiter_relax)
		self.parent.thread_register.get()
class Sequence_RAAR(SequenceBaseMask):
	def __init__(self, parent, pipelineitem):
		SequenceBaseMask.__init__(self, parent, pipelineitem)
		if parent.pipeline_started == True:
			if parent.citer_flow[1] == 2: return;
			self.beta = float(self.pipelineitem.beta.value.GetValue())
			if pipelineitem.chkbox.GetValue():
				self.numiter_relax = int(pipelineitem.niter_relax.value.GetValue())
			else:
				self.numiter_relax = 0
			self.StartPhasing()
	def ThreadAlg(self):
		self.parent.ancestor.GetPage(0).queue_info.put("Starting RAAR Algorithm...")
		self.parent.thread_register.put(1)
		RAAR(self.parent, self.beta, self.startiter, self.numiter, self.numiter_relax)
		self.parent.thread_register.get()
class Sequence_POER(SequenceBase):
	def __init__(self, parent, pipelineitem):
		SequenceBase.__init__(self, parent, pipelineitem)
		if parent.pipeline_started == True:
			if parent.citer_flow[1] == 2: return;
			self.StartPhasing()
	def ThreadAlg(self):
		self.parent.ancestor.GetPage(0).queue_info.put("Starting PO-ER Algorithm...")
		self.parent.thread_register.put(1)
		POER(self.parent, self.startiter, self.numiter)
		self.parent.thread_register.get()
class Sequence_PCHIO(SequenceBaseMask):
	def __init__(self, parent, pipelineitem):
		SequenceBaseMask.__init__(self, parent, pipelineitem)
		if parent.pipeline_started == True:
			if parent.citer_flow[1] == 2: return;
			self.beta = float(self.pipelineitem.beta.value.GetValue())
			self.phasemax = float(self.pipelineitem.phasemax.value.GetValue())
			self.phasemin = float(self.pipelineitem.phasemin.value.GetValue())
			self.StartPhasing()
	def ThreadAlg(self):
		self.parent.ancestor.GetPage(0).queue_info.put("Starting PCHIO Algorithm...")
		self.parent.thread_register.put(1)
		PCHIO(self.parent, self.beta, self.startiter, self.numiter, self.phasemax, self.phasemin)
		self.parent.thread_register.get()
class Sequence_PGCHIO(SequenceBaseMask):
	def __init__(self, parent, pipelineitem):
		SequenceBaseMask.__init__(self, parent, pipelineitem)
		if parent.pipeline_started == True:
			if parent.citer_flow[1] == 2: return;
			self.beta = float(self.pipelineitem.beta.value.GetValue())
			self.phasemax = float(self.pipelineitem.phasemax.value.GetValue())
			self.phasemin = float(self.pipelineitem.phasemin.value.GetValue())
			self.qx = float(self.pipelineitem.qx.value.GetValue())
			self.qy = float(self.pipelineitem.qy.value.GetValue())
			self.qz = float(self.pipelineitem.qz.value.GetValue())
			self.StartPhasing()
	def ThreadAlg(self):
		self.parent.ancestor.GetPage(0).queue_info.put("Starting PGCHIO Algorithm...")
		self.parent.thread_register.put(1)
		PGCHIO(self.parent, self.beta, self.startiter, self.numiter, self.phasemax, self.phasemin, self.qx, self.qy, self.qz)
		self.parent.thread_register.get()
class Sequence_CSHIO(SequenceBaseMask):
	def __init__(self, parent, pipelineitem):
		SequenceBaseMask.__init__(self, parent, pipelineitem)
		if parent.pipeline_started == True:
			if parent.citer_flow[1] == 2: return;
			self.beta = float(self.pipelineitem.beta.value.GetValue())
			self.cs_p = float(self.pipelineitem.cs_p.value.GetValue())
			self.cs_epsilon = float(self.pipelineitem.cs_epsilon.value.GetValue())
			self.cs_epsilon_min = float(self.pipelineitem.cs_epsilon_min.value.GetValue())
			self.cs_d = float(self.pipelineitem.cs_d.value.GetValue())
			self.cs_eta = float(self.pipelineitem.cs_eta.value.GetValue())
			if self.pipelineitem.chkbox_relax.GetValue() == True:
				self.relax = 1
			else:
				self.relax = 0
			self.StartPhasing()
	def ThreadAlg(self):
		self.parent.ancestor.GetPage(0).queue_info.put("Starting CSHIO Algorithm...")
		self.parent.thread_register.put(1)
		CSHIO(self.parent, self.beta, self.startiter, self.numiter, self.cs_p, self.cs_epsilon, self.cs_epsilon_min, self.cs_d, self.cs_eta, self.relax)
		self.parent.thread_register.get()
class Sequence_HIOMaskPC(SequenceBasePC):
	def __init__(self, parent, pipelineitem):
		SequenceBasePC.__init__(self, parent, pipelineitem)
		if parent.pipeline_started == True:
			if parent.citer_flow[1] == 2: return;
			self.beta = float(self.pipelineitem.beta.value.GetValue())
			self.StartPhasing()
	def ThreadAlg(self):
		self.parent.ancestor.GetPage(0).queue_info.put("Starting HIO Mask PC Algorithm...")
		self.parent.thread_register.put(1)
		HIOMaskPC(self.parent, self.beta, self.startiter, self.numiter, self.niterrlpre, self.niterrl, self.niterrlinterval, self.gammaHWHM, self.zex, self.zey, self.zez, self.reset_gamma, self.accel)
		self.parent.thread_register.get()
class Sequence_HPRMaskPC(SequenceBasePC):
	def __init__(self, parent, pipelineitem):
		SequenceBasePC.__init__(self, parent, pipelineitem)
		if parent.pipeline_started == True:
			if parent.citer_flow[1] == 2: return;
			self.beta = float(self.pipelineitem.beta.value.GetValue())
			self.StartPhasing()
	def ThreadAlg(self):
		self.parent.ancestor.GetPage(0).queue_info.put("Starting HPR Mask PC Algorithm...")
		self.parent.thread_register.put(1)
		HPRMaskPC(self.parent, self.beta, self.startiter, self.numiter, self.niterrlpre, self.niterrl, self.niterrlinterval, self.gammaHWHM, self.zex, self.zey, self.zez, self.reset_gamma, self.accel)
		self.parent.thread_register.get()
class Sequence_RAARMaskPC(SequenceBasePC):
	def __init__(self, parent, pipelineitem):
		SequenceBasePC.__init__(self, parent, pipelineitem)
		if parent.pipeline_started == True:
			if parent.citer_flow[1] == 2: return;
			self.beta = float(self.pipelineitem.beta.value.GetValue())
			self.StartPhasing()
	def ThreadAlg(self):
		self.parent.ancestor.GetPage(0).queue_info.put("Starting RAAR Mask PC Algorithm...")
		self.parent.thread_register.put(1)
		RAARMaskPC(self.parent, self.beta, self.startiter, self.numiter, self.niterrlpre, self.niterrl, self.niterrlinterval, self.gammaHWHM, self.zex, self.zey, self.zez, self.reset_gamma, self.accel)
		self.parent.thread_register.get()
class Sequence_ERMaskPC(SequenceBasePC):
	def __init__(self, parent, pipelineitem):
		SequenceBasePC.__init__(self, parent, pipelineitem)
		if parent.pipeline_started == True:
			if parent.citer_flow[1] == 2: return;
			self.StartPhasing()
	def ThreadAlg(self):
		self.parent.ancestor.GetPage(0).queue_info.put("Starting ER Mask PC Algorithm...")
		self.parent.thread_register.put(1)
		ERMaskPC(self.parent, self.startiter, self.numiter, self.niterrlpre, self.niterrl, self.niterrlinterval, self.gammaHWHM, self.zex, self.zey, self.zez, self.reset_gamma, self.accel)
		self.parent.thread_register.get()
class Sequence_ShrinkWrap(SequenceBaseMask):
	def __init__(self, parent, pipelineitem):
		SequenceBaseMask.__init__(self, parent, pipelineitem)
		if parent.pipeline_started == True:
			if parent.citer_flow[1] == 2: return;
			from ..lib.prfftw import threshold
			from ..lib.prfftw import rangereplace
			from ..lib.prfftw import convolve_sw
			from ..lib.prfftw import medianfilter
			from ..lib.prfftw import wrap_nomem
			from ..lib.prfftw import copy_amp
			from ..lib.prfftw import copy_abs
			from ..lib.prfftw import max_value
			self.threshold = threshold
			self.rangereplace = rangereplace
			self.convolve = convolve_sw
			self.medianfilter = medianfilter
			self.wrap = wrap_nomem
			self.copy_abs = copy_abs
			self.copy_amp = copy_amp
			self.maxvalue = numpy.zeros((2), dtype=numpy.double)
			self.max_value = max_value
			self.beta = float(self.pipelineitem.beta.value.GetValue())
			self.startiter = int(self.pipelineitem.start_iter)
			self.numiter = int(self.pipelineitem.niter.value.GetValue())
			self.cycle = int(self.pipelineitem.cycle.value.GetValue())
			self.phasemax = float(self.pipelineitem.phasemax.value.GetValue())
			self.phasemin = float(self.pipelineitem.phasemin.value.GetValue())
			self.cs_p = float(self.pipelineitem.cs_p.value.GetValue())
			self.cs_epsilon = float(self.pipelineitem.cs_epsilon.value.GetValue())
			self.cs_epsilon_min = float(self.pipelineitem.cs_epsilon_min.value.GetValue())
			self.cs_d = float(self.pipelineitem.cs_d.value.GetValue())
			self.cs_eta = float(self.pipelineitem.cs_eta.value.GetValue())
			if self.pipelineitem.chkbox_relax.GetValue() == True:
				self.cs_relax = 1
			else:
				self.cs_relax = 0
			self.gc_phasemax = float(self.pipelineitem.gc_phasemax.value.GetValue())
			self.gc_phasemin = float(self.pipelineitem.gc_phasemin.value.GetValue())
			self.qx = float(self.pipelineitem.qx.value.GetValue())
			self.qy = float(self.pipelineitem.qy.value.GetValue())
			self.qz = float(self.pipelineitem.qz.value.GetValue())
			self.sigma = float(self.pipelineitem.sigma.value.GetValue())
			self.frac = float(self.pipelineitem.frac.value.GetValue())
			if self.pipelineitem.chkbox_reweight.GetValue() == True:
				self.reweightiter = int(self.pipelineitem.reweightiter.value.GetValue())
			else:
				self.reweightiter = -1
			self.numsoiter = int(self.pipelineitem.nsoiter.value.GetValue())
			self.dtaumax = float(self.pipelineitem.dtaumax.value.GetValue())
			self.dtaumin = float(self.pipelineitem.dtaumin.value.GetValue())
			self.psiexitratio = float(self.pipelineitem.psiexitratio.value.GetValue())
			self.psiexiterror = float(self.pipelineitem.psiexiterror.value.GetValue())
			self.psiresetratio = float(self.pipelineitem.psiresetratio.value.GetValue())
			self.taumax = float(self.pipelineitem.taumax.value.GetValue())
			self.alpha = 1.0
			self.RSConst =  self.pipelineitem.rbrs.GetStringSelection()
			if self.LoadTmp():
				self.parent.pipeline_started = False
				return
			self.StartPhasing()
	def LoadTmp(self):
		try:
			from ..lib.prfftw import gaussian_fill
			self.parent.temparray = NewArray(self, *self.parent.support.shape)
			self.parent.temparray2 = NewArray(self, *self.parent.support.shape)
			gaussian_fill(self.parent.temparray, self.sigma)
			self.wrap(self.parent.temparray, self.parent.temparray2, 1)
		except:
			msg = "Insufficient memory for temporary arrays."
			self.MsgDlg(msg)
			return True
		else:
			return False
	def UpdateSupport(self):
		if self.parent.ancestor.GetPage(0).citer_flow[4] > 0:
			self.parent.ancestor.GetPage(0).queue_info.put("Updating support ...")
			self.copy_abs(self.parent.seqdata, self.parent.support)
			self.max_value(self.parent.support.real, self.maxvalue)
			self.threshold(self.parent.support, (self.frac*self.maxvalue[0]), self.maxvalue[0], 0.0)
			self.medianfilter(self.parent.support, self.parent.temparray2, 3,3,3, 0.0)
			self.wrap(self.parent.support, self.parent.temparray2, 1)
			self.convolve(self.parent.support, self.parent.temparray)
			self.wrap(self.parent.support, self.parent.temparray2, -1)
			self.rangereplace(self.parent.support, (self.frac*self.maxvalue[0]), sys.float_info.max, 0.0, 1.0)
			self.copy_amp(self.parent.support, self.parent.visual_support)
			self.parent.ancestor.GetPage(0).queue_info.put("... done.")
	def UpdateVisualSupport(self):
			if self.parent.ancestor.GetPage(0).citer_flow[4] > 0:
				wx.CallAfter(self.parent.ancestor.GetPage(1).UpdateSupport,)
	def GetIterVars(self, fstartiter, fnumiter, ii, fcycle):
			fsw_startiter = fstartiter + (ii * fcycle)
			if  fnumiter <  ((ii+1) * fcycle):
				fsw_numiter =  fnumiter - (ii * fcycle)
			else:
				fsw_numiter = fcycle
			return fsw_startiter, fsw_numiter
	def ThreadAlg(self):
		self.parent.ancestor.GetPage(0).queue_info.put("Starting shrink wrap algorithm using "+self.RSConst +"..." )
		self.parent.thread_register.put(1)
		IterLoops = (self.numiter + self.cycle - 1)//self.cycle
		if self.RSConst == 'HIO':
			for i in range( IterLoops ):
				sw_startiter, sw_numiter = self.GetIterVars(self.startiter, self.numiter, i, self.cycle)
				HIO(self.parent, self.beta, sw_startiter, sw_numiter)
				if self.parent.ancestor.GetPage(0).citer_flow[1] == 2:
					break
				self.UpdateSupport()
				self.UpdateVisualSupport()
		if self.RSConst == 'PCHIO':
			for i in range( IterLoops ):
				sw_startiter, sw_numiter = self.GetIterVars(self.startiter, self.numiter, i, self.cycle)
				PCHIO(self.parent, self.beta, sw_startiter, sw_numiter, self.phasemax, self.phasemin)
				if self.parent.ancestor.GetPage(0).citer_flow[1] == 2:
					break
				self.UpdateSupport()
				self.UpdateVisualSupport()
		if self.RSConst == 'PGCHIO':
			for i in range( IterLoops ):
				sw_startiter, sw_numiter = self.GetIterVars(self.startiter, self.numiter, i, self.cycle)
				PGCHIO(self.parent, self.beta, sw_startiter, sw_numiter, self.gc_phasemax, self.gc_phasemin, self.qx, self.qy, self.qz)
				if self.parent.ancestor.GetPage(0).citer_flow[1] == 2:
					break
				self.UpdateSupport()
				self.UpdateVisualSupport()
		if self.RSConst == 'HIOMask':
			for i in range( IterLoops ):
				sw_startiter, sw_numiter = self.GetIterVars(self.startiter, self.numiter, i, self.cycle)
				HIOMask(self.parent, self.beta, sw_startiter, sw_numiter, 0)
				if self.parent.ancestor.GetPage(0).citer_flow[1] == 2:
					break
				self.UpdateSupport()
				self.UpdateVisualSupport()
		if self.RSConst == 'HIOPlus':
			for i in range( IterLoops ):
				sw_startiter, sw_numiter = self.GetIterVars(self.startiter, self.numiter, i, self.cycle)
				HIOPlus(self.parent, self.beta, sw_startiter, sw_numiter)
				if self.parent.ancestor.GetPage(0).citer_flow[1] == 2:
					break
				self.UpdateSupport()
				self.UpdateVisualSupport()
		if self.RSConst == 'ER':
			for i in range( IterLoops ):
				sw_startiter, sw_numiter = self.GetIterVars(self.startiter, self.numiter, i, self.cycle)
				ER(self.parent, sw_startiter, sw_numiter)
				if self.parent.ancestor.GetPage(0).citer_flow[1] == 2:
					break
				self.UpdateSupport()
				self.UpdateVisualSupport()
		if self.RSConst == 'HPR':
			for i in range( IterLoops ):
				sw_startiter, sw_numiter = self.GetIterVars(self.startiter, self.numiter, i, self.cycle)
				HPR(self.parent, self.beta, sw_startiter, sw_numiter,0)
				if self.parent.ancestor.GetPage(0).citer_flow[1] == 2:
					break
				self.UpdateSupport()
				self.UpdateVisualSupport()
		if self.RSConst == 'RAAR':
			for i in range( IterLoops ):
				sw_startiter, sw_numiter = self.GetIterVars(self.startiter, self.numiter, i, self.cycle)
				RAAR(self.parent, self.beta, sw_startiter, sw_numiter,0)
				if self.parent.ancestor.GetPage(0).citer_flow[1] == 2:
					break
				self.UpdateSupport()
				self.UpdateVisualSupport()
		if self.RSConst == 'CSHIO':
			for i in range( IterLoops ):
				sw_startiter, sw_numiter = self.GetIterVars(self.startiter, self.numiter, i, self.cycle)
				CSHIO(self.parent, self.beta, sw_startiter, sw_numiter, self.cs_p, self.cs_epsilon, self.cs_epsilon_min, self.cs_d, self.cs_eta, self.cs_relax)
				if self.parent.ancestor.GetPage(0).citer_flow[1] == 2:
					break
				self.UpdateSupport()
				self.UpdateVisualSupport()
		if self.RSConst == 'SO2D':
			alpha1,beta1 = self.alpha,self.beta
			for i in range( IterLoops ):
				sw_startiter, sw_numiter = self.GetIterVars(self.startiter, self.numiter, i, self.cycle)
				alpha1,beta1 = SO2D(self.parent, alpha1, beta1, sw_startiter, sw_numiter, self.numsoiter, self.reweightiter, self.dtaumax, self.dtaumin, self.psiexitratio, self.psiexiterror, self.psiresetratio, self.taumax)
				if self.parent.ancestor.GetPage(0).citer_flow[1] == 2:
					break
				self.UpdateSupport()
				self.UpdateVisualSupport()
		self.parent.thread_register.get()
class Sequence_SO2D(SequenceBaseMask):
	def __init__(self, parent, pipelineitem):
		SequenceBaseMask.__init__(self, parent, pipelineitem)
		if parent.pipeline_started == True:
			if parent.citer_flow[1] == 2: return;
			self.beta = float(self.pipelineitem.beta.value.GetValue())
			self.startiter = int(self.pipelineitem.start_iter)
			self.numiter = int(self.pipelineitem.niter.value.GetValue())
			self.numsoiter = int(self.pipelineitem.nsoiter.value.GetValue())
			if self.pipelineitem.chkbox_reweight.GetValue() == True:
				self.reweightiter = int(self.pipelineitem.reweightiter.value.GetValue())
			else:
				self.reweightiter = -1
			self.dtaumax = float(self.pipelineitem.dtaumax.value.GetValue())
			self.dtaumin = float(self.pipelineitem.dtaumin.value.GetValue())
			self.psiexitratio = float(self.pipelineitem.psiexitratio.value.GetValue())
			self.psiexiterror = float(self.pipelineitem.psiexiterror.value.GetValue())
			self.psiresetratio = float(self.pipelineitem.psiresetratio.value.GetValue())
			self.taumax = float(self.pipelineitem.taumax.value.GetValue())
			self.alpha = 1.0
			self.StartPhasing()
	def ThreadAlg(self):
		self.parent.ancestor.GetPage(0).queue_info.put("Starting SO2D Algorithm...")
		self.parent.thread_register.put(1)
		SO2D(self.parent, self.alpha, self.beta, self.startiter, self.numiter, self.numsoiter, self.reweightiter, self.dtaumax, self.dtaumin, self.psiexitratio, self.psiexiterror, self.psiresetratio, self.taumax)
		self.parent.thread_register.get()
