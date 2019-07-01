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
def Sequence_HIO(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		if self.citer_flow[1] == 2: return;
		expdata_path = pipelineitem.exp_amps.objectpath.GetValue()
		try:
			self.expdata = LoadArray(self, expdata_path)
			if pipelineitem.chkbox_sqrt_expamps.GetValue() == True:
				numpy.sqrt(self.expdata, self.expdata)
			self.expdata[:] = WrapArray(self.expdata).copy()
		except:
			msg = "Could not load array from: \n"+ expdata_path + "\nPlease check the path."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			return
		support_path = pipelineitem.support.objectpath.GetValue()
		if support_path == "":
			try:
				self.support
			except AttributeError:
				msg = "No existing Support array found."
				dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()
				self.pipeline_started = False
				return
		else:
			try:
				self.support = LoadArray(self, support_path)
			except:
				msg = "Could not load array from: \n"+ support_path + "\nPlease check the path."
				dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()
				self.pipeline_started = False
				return
		if (not self.expdata.shape == self.support.shape) == True:
			msg = "Array dimensions are inconsistent."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			self.seqdata = None
			try:
				self.visual_amp_real = None
			except:
				pass
			try:
				self.visual_amp_recip = None
			except:
				pass
			try:
				self.visual_amp_support = None
			except:
				pass
			return
		beta = float(pipelineitem.beta.value.GetValue())
		startiter = int(pipelineitem.start_iter)
		numiter = int(pipelineitem.niter.value.GetValue())
		if startiter == 0 and (self.visual_amp_real is not None or self.visual_support is not None or self.visual_amp_recip is not None):
			if self.expdata.shape[2] == 1:
				PrepareVisualisation2D(self,pipelineitem)
			else:
				PrepareVisualisation(self,pipelineitem)
		def threadHIO(self):
			self.ancestor.GetPage(0).queue_info.put("Starting HIO Algorithm...")
			self.thread_register.put(1)
			HIO(self, beta, startiter, numiter)
			self.thread_register.get()
			return
		self.thread = threading.Thread(target=threadHIO, args=(self,))
		self.thread.daemon = True
		self.thread.start()
		return
def Sequence_ER(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		if self.citer_flow[1] == 2: return;
		expdata_path = pipelineitem.exp_amps.objectpath.GetValue()
		try:
			self.expdata = LoadArray(self, expdata_path)
			if pipelineitem.chkbox_sqrt_expamps.GetValue() == True:
				numpy.sqrt(self.expdata, self.expdata)
			self.expdata[:] = WrapArray(self.expdata).copy()
		except:
			msg = "Could not load array from: \n"+ expdata_path + "\nPlease check the path."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			return
		support_path = pipelineitem.support.objectpath.GetValue()
		if support_path == "":
			try:
				self.support
			except AttributeError:
				msg = "No existing Support array found."
				dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()
				self.pipeline_started = False
				return
		else:
			try:
				self.support = LoadArray(self, support_path)
			except:
				msg = "Could not load array from: \n"+ support_path + "\nPlease check the path."
				dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()
				self.pipeline_started = False
				return
		if (not self.expdata.shape == self.support.shape) == True:
			msg = "Array dimensions are inconsistent."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			self.seqdata = None
			try:
				self.visual_amp_real = None
			except:
				pass
			try:
				self.visual_amp_recip = None
			except:
				pass
			try:
				self.visual_amp_support = None
			except:
				pass
			return
		startiter = int(pipelineitem.start_iter)
		numiter = int(pipelineitem.niter.value.GetValue())
		if startiter == 0 and (self.visual_amp_real is not None or self.visual_support is not None or self.visual_amp_recip is not None):
			if self.expdata.shape[2] == 1:
				PrepareVisualisation2D(self,pipelineitem)
			else:
				PrepareVisualisation(self,pipelineitem)
		def threadER(self):
			self.ancestor.GetPage(0).queue_info.put("Starting ER Algorithm...")
			self.thread_register.put(1)
			ER(self, startiter, numiter)
			self.thread_register.get()
			return
		self.thread = threading.Thread(target=threadER, args=(self,))
		self.thread.daemon = True
		self.thread.start()
		return
def Sequence_ERMask(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		if self.citer_flow[1] == 2: return;
		expdata_path = pipelineitem.exp_amps.objectpath.GetValue()
		try:
			self.expdata = LoadArray(self, expdata_path)
			if pipelineitem.chkbox_sqrt_expamps.GetValue() == True:
				numpy.sqrt(self.expdata, self.expdata)
			self.expdata[:] = WrapArray(self.expdata).copy()
		except:
			msg = "Could not load array from: \n"+ expdata_path + "\nPlease check the path."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			return
		support_path = pipelineitem.support.objectpath.GetValue()
		if support_path == "":
			try:
				self.support
			except AttributeError:
				msg = "No existing Support array found."
				dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()
				self.pipeline_started = False
				return
		else:
			try:
				self.support = LoadArray(self, support_path)
			except:
				msg = "Could not load array from: \n"+ support_path + "\nPlease check the path."
				dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()
				self.pipeline_started = False
				return
		mask_path = pipelineitem.mask.objectpath.GetValue()
		try:
			self.mask = LoadArray(self, mask_path)
			self.mask[:] = WrapArray(self.mask).copy()
		except:
			msg = "Could not load array from: \n"+ mask_path + "\nPlease check the path."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			return
		if (not (self.expdata.shape == self.support.shape and self.expdata.shape == self.mask.shape)) == True:
			msg = "Array dimensions are inconsistent."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			self.seqdata = None
			try:
				self.visual_amp_real = None
			except:
				pass
			try:
				self.visual_amp_recip = None
			except:
				pass
			try:
				self.visual_amp_support = None
			except:
				pass
			return
		startiter = int(pipelineitem.start_iter)
		numiter = int(pipelineitem.niter.value.GetValue())
		if pipelineitem.chkbox.GetValue():
			numiter_relax = int(pipelineitem.niter_relax.value.GetValue())
		else:
			numiter_relax = 0
		if startiter == 0 and (self.visual_amp_real is not None or self.visual_support is not None or self.visual_amp_recip is not None):
			if self.expdata.shape[2] == 1:
				PrepareVisualisation2D(self,pipelineitem)
			else:
				PrepareVisualisation(self,pipelineitem)
		def threadERMask(self):
			self.ancestor.GetPage(0).queue_info.put("Starting ER Mask Algorithm...")
			self.thread_register.put(1)
			ERMask(self, startiter, numiter, numiter_relax)
			self.thread_register.get()
			return
		self.thread = threading.Thread(target=threadERMask, args=(self,))
		self.thread.daemon = True
		self.thread.start()
		return
def Sequence_POER(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		if self.citer_flow[1] == 2: return;
		expdata_path = pipelineitem.exp_amps.objectpath.GetValue()
		try:
			self.expdata = LoadArray(self, expdata_path)
			if pipelineitem.chkbox_sqrt_expamps.GetValue() == True:
				numpy.sqrt(self.expdata, self.expdata)
			self.expdata[:] = WrapArray(self.expdata).copy()
		except:
			msg = "Could not load array from: \n"+ expdata_path + "\nPlease check the path."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			return
		support_path = pipelineitem.support.objectpath.GetValue()
		if support_path == "":
			try:
				self.support
			except AttributeError:
				msg = "No existing Support array found."
				dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()
				self.pipeline_started = False
				return
		else:
			try:
				self.support = LoadArray(self, support_path)
			except:
				msg = "Could not load array from: \n"+ support_path + "\nPlease check the path."
				dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()
				self.pipeline_started = False
				return
		mask_path = pipelineitem.mask.objectpath.GetValue()
		try:
			self.mask = LoadArray(self, mask_path)
			self.mask[:] = WrapArray(self.mask).copy()
		except:
			msg = "Could not load array from: \n"+ mask_path + "\nPlease check the path."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			return
		if (not (self.expdata.shape == self.support.shape and self.expdata.shape == self.mask.shape)) == True:
			msg = "Array dimensions are inconsistent."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			self.seqdata = None
			try:
				self.visual_amp_real = None
			except:
				pass
			try:
				self.visual_amp_recip = None
			except:
				pass
			try:
				self.visual_amp_support = None
			except:
				pass
			return
		startiter = int(pipelineitem.start_iter)
		numiter = int(pipelineitem.niter.value.GetValue())
		if startiter == 0 and (self.visual_amp_real is not None or self.visual_support is not None or self.visual_amp_recip is not None):
			if self.expdata.shape[2] == 1:
				PrepareVisualisation2D(self,pipelineitem)
			else:
				PrepareVisualisation(self,pipelineitem)
		def threadPOER(self):
			self.ancestor.GetPage(0).queue_info.put("Starting PO-ER Algorithm...")
			self.thread_register.put(1)
			POER(self, startiter, numiter)
			self.thread_register.get()
			return
		self.thread = threading.Thread(target=threadPOER, args=(self,))
		self.thread.daemon = True
		self.thread.start()
		return
def Sequence_HPR(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		if self.citer_flow[1] == 2: return;
		expdata_path = pipelineitem.exp_amps.objectpath.GetValue()
		try:
			self.expdata = LoadArray(self, expdata_path)
			if pipelineitem.chkbox_sqrt_expamps.GetValue() == True:
				numpy.sqrt(self.expdata, self.expdata)
			self.expdata[:] = WrapArray(self.expdata).copy()
		except:
			msg = "Could not load array from: \n"+ expdata_path + "\nPlease check the path."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			return
		support_path = pipelineitem.support.objectpath.GetValue()
		if support_path == "":
			try:
				self.support
			except AttributeError:
				msg = "No existing Support array found."
				dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()
				self.pipeline_started = False
				return
		else:
			try:
				self.support = LoadArray(self, support_path)
			except:
				msg = "Could not load array from: \n"+ support_path + "\nPlease check the path."
				dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()
				self.pipeline_started = False
				return
		mask_path = pipelineitem.mask.objectpath.GetValue()
		try:
			self.mask = LoadArray(self, mask_path)
			self.mask[:] = WrapArray(self.mask).copy()
		except:
			msg = "Could not load array from: \n"+ mask_path + "\nPlease check the path."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			return
		if (not (self.expdata.shape == self.support.shape and self.expdata.shape == self.mask.shape)) == True:
			msg = "Array dimensions are inconsistent."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			self.seqdata = None
			try:
				self.visual_amp_real = None
			except:
				pass
			try:
				self.visual_amp_recip = None
			except:
				pass
			try:
				self.visual_amp_support = None
			except:
				pass
			return
		beta = float(pipelineitem.beta.value.GetValue())
		startiter = int(pipelineitem.start_iter)
		numiter = int(pipelineitem.niter.value.GetValue())
		if pipelineitem.chkbox.GetValue():
			numiter_relax = int(pipelineitem.niter_relax.value.GetValue())
		else:
			numiter_relax = 0
		if startiter == 0 and (self.visual_amp_real is not None or self.visual_support is not None or self.visual_amp_recip is not None):
			if self.expdata.shape[2] == 1:
				PrepareVisualisation2D(self,pipelineitem)
			else:
				PrepareVisualisation(self,pipelineitem)
		def threadHPR(self):
			self.ancestor.GetPage(0).queue_info.put("Starting HPR Algorithm...")
			self.thread_register.put(1)
			HPR(self, beta, startiter, numiter, numiter_relax)
			self.thread_register.get()
			return
		self.thread = threading.Thread(target=threadHPR, args=(self,))
		self.thread.daemon = True
		self.thread.start()
		return
def Sequence_RAAR(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		if self.citer_flow[1] == 2: return;
		expdata_path = pipelineitem.exp_amps.objectpath.GetValue()
		try:
			self.expdata = LoadArray(self, expdata_path)
			if pipelineitem.chkbox_sqrt_expamps.GetValue() == True:
				numpy.sqrt(self.expdata, self.expdata)
			self.expdata[:] = WrapArray(self.expdata).copy()
		except:
			msg = "Could not load array from: \n"+ expdata_path + "\nPlease check the path."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			return
		support_path = pipelineitem.support.objectpath.GetValue()
		if support_path == "":
			try:
				self.support
			except AttributeError:
				msg = "No existing Support array found."
				dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()
				self.pipeline_started = False
				return
		else:
			try:
				self.support = LoadArray(self, support_path)
			except:
				msg = "Could not load array from: \n"+ support_path + "\nPlease check the path."
				dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()
				self.pipeline_started = False
				return
		mask_path = pipelineitem.mask.objectpath.GetValue()
		try:
			self.mask = LoadArray(self, mask_path)
			self.mask[:] = WrapArray(self.mask).copy()
		except:
			msg = "Could not load array from: \n"+ mask_path + "\nPlease check the path."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			return
		if (not (self.expdata.shape == self.support.shape and self.expdata.shape == self.mask.shape)) == True:
			msg = "Array dimensions are inconsistent."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			self.seqdata = None
			try:
				self.visual_amp_real = None
			except:
				pass
			try:
				self.visual_amp_recip = None
			except:
				pass
			try:
				self.visual_amp_support = None
			except:
				pass
			return
		beta = float(pipelineitem.beta.value.GetValue())
		startiter = int(pipelineitem.start_iter)
		numiter = int(pipelineitem.niter.value.GetValue())
		if pipelineitem.chkbox.GetValue():
			numiter_relax = int(pipelineitem.niter_relax.value.GetValue())
		else:
			numiter_relax = 0
		if startiter == 0 and (self.visual_amp_real is not None or self.visual_support is not None or self.visual_amp_recip is not None):
			if self.expdata.shape[2] == 1:
				PrepareVisualisation2D(self,pipelineitem)
			else:
				PrepareVisualisation(self,pipelineitem)
		def threadRAAR(self):
			self.ancestor.GetPage(0).queue_info.put("Starting RAAR Algorithm...")
			self.thread_register.put(1)
			RAAR(self, beta, startiter, numiter, numiter_relax)
			self.thread_register.get()
			return
		self.thread = threading.Thread(target=threadRAAR, args=(self,))
		self.thread.daemon = True
		self.thread.start()
		return
def Sequence_HIOMask(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		if self.citer_flow[1] == 2: return;
		expdata_path = pipelineitem.exp_amps.objectpath.GetValue()
		try:
			self.expdata = LoadArray(self, expdata_path)
			if pipelineitem.chkbox_sqrt_expamps.GetValue() == True:
				numpy.sqrt(self.expdata, self.expdata)
			self.expdata[:] = WrapArray(self.expdata).copy()
		except:
			msg = "Could not load array from: \n"+ expdata_path + "\nPlease check the path."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			return
		support_path = pipelineitem.support.objectpath.GetValue()
		if support_path == "":
			try:
				self.support
			except AttributeError:
				msg = "No existing Support array found."
				dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()
				self.pipeline_started = False
				return
		else:
			try:
				self.support = LoadArray(self, support_path)
			except:
				msg = "Could not load array from: \n"+ support_path + "\nPlease check the path."
				dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()
				self.pipeline_started = False
				return
		mask_path = pipelineitem.mask.objectpath.GetValue()
		try:
			self.mask = LoadArray(self, mask_path)
			self.mask[:] = WrapArray(self.mask).copy()
		except:
			msg = "Could not load array from: \n"+ mask_path + "\nPlease check the path."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			return
		if (not (self.expdata.shape == self.support.shape and self.expdata.shape == self.mask.shape)) == True:
			msg = "Array dimensions are inconsistent."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			self.seqdata = None
			try:
				self.visual_amp_real = None
			except:
				pass
			try:
				self.visual_amp_recip = None
			except:
				pass
			try:
				self.visual_amp_support = None
			except:
				pass
			return
		beta = float(pipelineitem.beta.value.GetValue())
		startiter = int(pipelineitem.start_iter)
		numiter = int(pipelineitem.niter.value.GetValue())
		if pipelineitem.chkbox.GetValue():
			numiter_relax = int(pipelineitem.niter_relax.value.GetValue())
		else:
			numiter_relax = 0
		if startiter == 0 and (self.visual_amp_real is not None or self.visual_support is not None or self.visual_amp_recip is not None):
			if self.expdata.shape[2] == 1:
				PrepareVisualisation2D(self,pipelineitem)
			else:
				PrepareVisualisation(self,pipelineitem)
		def threadHIOMask(self):
			self.ancestor.GetPage(0).queue_info.put("Starting HIO Algorithm...")
			self.thread_register.put(1)
			HIOMask(self, beta, startiter, numiter, numiter_relax)
			self.thread_register.get()
			return
		self.thread = threading.Thread(target=threadHIOMask, args=(self,))
		self.thread.daemon = True
		self.thread.start()
		return
def Sequence_HIOPlus(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		if self.citer_flow[1] == 2: return;
		expdata_path = pipelineitem.exp_amps.objectpath.GetValue()
		try:
			self.expdata = LoadArray(self, expdata_path)
			if pipelineitem.chkbox_sqrt_expamps.GetValue() == True:
				numpy.sqrt(self.expdata, self.expdata)
			self.expdata[:] = WrapArray(self.expdata).copy()
		except:
			msg = "Could not load array from: \n"+ expdata_path + "\nPlease check the path."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			return
		support_path = pipelineitem.support.objectpath.GetValue()
		if support_path == "":
			try:
				self.support
			except AttributeError:
				msg = "No existing Support array found."
				dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()
				self.pipeline_started = False
				return
		else:
			try:
				self.support = LoadArray(self, support_path)
			except:
				msg = "Could not load array from: \n"+ support_path + "\nPlease check the path."
				dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()
				self.pipeline_started = False
				return
		mask_path = pipelineitem.mask.objectpath.GetValue()
		try:
			self.mask = LoadArray(self, mask_path)
			self.mask[:] = WrapArray(self.mask).copy()
		except:
			msg = "Could not load array from: \n"+ mask_path + "\nPlease check the path."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			return
		if (not (self.expdata.shape == self.support.shape and self.expdata.shape == self.mask.shape)) == True:
			msg = "Array dimensions are inconsistent."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			self.seqdata = None
			try:
				self.visual_amp_real = None
			except:
				pass
			try:
				self.visual_amp_recip = None
			except:
				pass
			try:
				self.visual_amp_support = None
			except:
				pass
			return
		beta = float(pipelineitem.beta.value.GetValue())
		startiter = int(pipelineitem.start_iter)
		numiter = int(pipelineitem.niter.value.GetValue())
		if startiter == 0 and (self.visual_amp_real is not None or self.visual_support is not None or self.visual_amp_recip is not None):
			if self.expdata.shape[2] == 1:
				PrepareVisualisation2D(self,pipelineitem)
			else:
				PrepareVisualisation(self,pipelineitem)
		def threadHIOPlus(self):
			self.ancestor.GetPage(0).queue_info.put("Starting HIO+ Algorithm...")
			self.thread_register.put(1)
			HIOPlus(self, beta, startiter, numiter)
			self.thread_register.get()
			return
		self.thread = threading.Thread(target=threadHIOPlus, args=(self,))
		self.thread.daemon = True
		self.thread.start()
		return
def Sequence_PCHIO(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		if self.citer_flow[1] == 2: return;
		expdata_path = pipelineitem.exp_amps.objectpath.GetValue()
		try:
			self.expdata = LoadArray(self, expdata_path)
			if pipelineitem.chkbox_sqrt_expamps.GetValue() == True:
				numpy.sqrt(self.expdata, self.expdata)
			self.expdata[:] = WrapArray(self.expdata).copy()
		except:
			msg = "Could not load array from: \n"+ expdata_path + "\nPlease check the path."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			return
		support_path = pipelineitem.support.objectpath.GetValue()
		if support_path == "":
			try:
				self.support
			except AttributeError:
				msg = "No existing Support array found."
				dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()
				self.pipeline_started = False
				return
		else:
			try:
				self.support = LoadArray(self, support_path)
			except:
				msg = "Could not load array from: \n"+ support_path + "\nPlease check the path."
				dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()
				self.pipeline_started = False
				return
		mask_path = pipelineitem.mask.objectpath.GetValue()
		try:
			self.mask = LoadArray(self, mask_path)
			self.mask[:] = WrapArray(self.mask).copy()
		except:
			msg = "Could not load array from: \n"+ mask_path + "\nPlease check the path."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			return
		if (not (self.expdata.shape == self.support.shape and self.expdata.shape == self.mask.shape)) == True:
			msg = "Array dimensions are inconsistent."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			self.seqdata = None
			try:
				self.visual_amp_real = None
			except:
				pass
			try:
				self.visual_amp_recip = None
			except:
				pass
			try:
				self.visual_amp_support = None
			except:
				pass
			return
		beta = float(pipelineitem.beta.value.GetValue())
		startiter = int(pipelineitem.start_iter)
		numiter = int(pipelineitem.niter.value.GetValue())
		phasemax = float(pipelineitem.phasemax.value.GetValue())
		phasemin = float(pipelineitem.phasemin.value.GetValue())
		if startiter == 0 and (self.visual_amp_real is not None or self.visual_support is not None or self.visual_amp_recip is not None):
			if self.expdata.shape[2] == 1:
				PrepareVisualisation2D(self,pipelineitem)
			else:
				PrepareVisualisation(self,pipelineitem)
		def threadPCHIO(self):
			self.ancestor.GetPage(0).queue_info.put("Starting PCHIO Algorithm...")
			self.thread_register.put(1)
			PCHIO(self, beta, startiter, numiter, phasemax, phasemin)
			self.thread_register.get()
			return
		self.thread = threading.Thread(target=threadPCHIO, args=(self,))
		self.thread.daemon = True
		self.thread.start()
		return
def Sequence_PGCHIO(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		if self.citer_flow[1] == 2: return;
		expdata_path = pipelineitem.exp_amps.objectpath.GetValue()
		try:
			self.expdata = LoadArray(self, expdata_path)
			if pipelineitem.chkbox_sqrt_expamps.GetValue() == True:
				numpy.sqrt(self.expdata, self.expdata)
			self.expdata[:] = WrapArray(self.expdata).copy()
		except:
			msg = "Could not load array from: \n"+ expdata_path + "\nPlease check the path."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			return
		support_path = pipelineitem.support.objectpath.GetValue()
		if support_path == "":
			try:
				self.support
			except AttributeError:
				msg = "No existing Support array found."
				dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()
				self.pipeline_started = False
				return
		else:
			try:
				self.support = LoadArray(self, support_path)
			except:
				msg = "Could not load array from: \n"+ support_path + "\nPlease check the path."
				dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()
				self.pipeline_started = False
				return
		mask_path = pipelineitem.mask.objectpath.GetValue()
		try:
			self.mask = LoadArray(self, mask_path)
			self.mask[:] = WrapArray(self.mask).copy()
		except:
			msg = "Could not load array from: \n"+ mask_path + "\nPlease check the path."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			return
		if (not (self.expdata.shape == self.support.shape and self.expdata.shape == self.mask.shape)) == True:
			msg = "Array dimensions are inconsistent."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			self.seqdata = None
			try:
				self.visual_amp_real = None
			except:
				pass
			try:
				self.visual_amp_recip = None
			except:
				pass
			try:
				self.visual_amp_support = None
			except:
				pass
			return
		beta = float(pipelineitem.beta.value.GetValue())
		startiter = int(pipelineitem.start_iter)
		numiter = int(pipelineitem.niter.value.GetValue())
		phasemax = float(pipelineitem.phasemax.value.GetValue())
		phasemin = float(pipelineitem.phasemin.value.GetValue())
		qx = float(pipelineitem.qx.value.GetValue())
		qy = float(pipelineitem.qy.value.GetValue())
		qz = float(pipelineitem.qz.value.GetValue())
		if startiter == 0 and (self.visual_amp_real is not None or self.visual_support is not None or self.visual_amp_recip is not None):
			if self.expdata.shape[2] == 1:
				PrepareVisualisation2D(self,pipelineitem)
			else:
				PrepareVisualisation(self,pipelineitem)
		def threadPGCHIO(self):
			self.ancestor.GetPage(0).queue_info.put("Starting PGCHIO Algorithm...")
			self.thread_register.put(1)
			PGCHIO(self, beta, startiter, numiter, phasemax, phasemin, qx, qy, qz)
			self.thread_register.get()
			return
		self.thread = threading.Thread(target=threadPGCHIO, args=(self,))
		self.thread.daemon = True
		self.thread.start()
		return
def Sequence_ShrinkWrap(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		if self.citer_flow[1] == 2: return;
		expdata_path = pipelineitem.exp_amps.objectpath.GetValue()
		try:
			self.expdata = LoadArray(self, expdata_path)
			if pipelineitem.chkbox_sqrt_expamps.GetValue() == True:
				numpy.sqrt(self.expdata, self.expdata)
			self.expdata[:] = WrapArray(self.expdata).copy()
		except:
			msg = "Could not load array from: \n"+ expdata_path + "\nPlease check the path."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			return
		support_path = pipelineitem.support.objectpath.GetValue()
		if support_path == "":
			try:
				self.support
			except AttributeError:
				msg = "No existing Support array found."
				dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()
				self.pipeline_started = False
				return
		else:
			try:
				self.support = LoadArray(self, support_path)
			except:
				msg = "Could not load array from: \n"+ support_path + "\nPlease check the path."
				dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()
				self.pipeline_started = False
				return
		mask_path = pipelineitem.mask.objectpath.GetValue()
		try:
			self.mask = LoadArray(self, mask_path)
			self.mask[:] = WrapArray(self.mask).copy()
		except:
			msg = "Could not load array from: \n"+ mask_path + "\nPlease check the path."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			return
		if (not (self.expdata.shape == self.support.shape and self.expdata.shape == self.mask.shape)) == True:
			msg = "Array dimensions are inconsistent."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			self.seqdata = None
			try:
				self.visual_amp_real = None
			except:
				pass
			try:
				self.visual_amp_recip = None
			except:
				pass
			try:
				self.visual_amp_support = None
			except:
				pass
			return
		try:
			temparray = NewArray(self, *self.support.shape)
			temparray2 = NewArray(self, *self.support.shape)
		except:
			msg = "Insufficient memory for temporary array."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			return
		beta = float(pipelineitem.beta.value.GetValue())
		startiter = int(pipelineitem.start_iter)
		numiter = int(pipelineitem.niter.value.GetValue())
		cycle = int(pipelineitem.cycle.value.GetValue())
		phasemax = float(pipelineitem.phasemax.value.GetValue())
		phasemin = float(pipelineitem.phasemin.value.GetValue())
		cs_p = float(pipelineitem.cs_p.value.GetValue())
		cs_epsilon = float(pipelineitem.cs_epsilon.value.GetValue())
		cs_epsilon_min = float(pipelineitem.cs_epsilon_min.value.GetValue())
		cs_d = float(pipelineitem.cs_d.value.GetValue())
		cs_eta = float(pipelineitem.cs_eta.value.GetValue())
		if pipelineitem.chkbox_relax.GetValue() == True:
			cs_relax = 1
		else:
			cs_relax = 0
		gc_phasemax = float(pipelineitem.gc_phasemax.value.GetValue())
		gc_phasemin = float(pipelineitem.gc_phasemin.value.GetValue())
		qx = float(pipelineitem.qx.value.GetValue())
		qy = float(pipelineitem.qy.value.GetValue())
		qz = float(pipelineitem.qz.value.GetValue())
		sigma = float(pipelineitem.sigma.value.GetValue())
		frac = float(pipelineitem.frac.value.GetValue())
		if startiter == 0 and (self.visual_amp_real is not None or self.visual_support is not None or self.visual_amp_recip is not None):
			if self.expdata.shape[2] == 1:
				PrepareVisualisation2D(self,pipelineitem)
			else:
				PrepareVisualisation(self,pipelineitem)
		RSConst =  pipelineitem.rbrs.GetStringSelection()
		from ..lib.prfftw import gaussian_fill
		from ..lib.prfftw import wrap
		gaussian_fill(temparray, sigma)
		wrap(temparray, 1)
		def threadShrinkWrap(self):
			self.ancestor.GetPage(0).queue_info.put("Starting shrink wrap algorithm using "+RSConst +"..." )
			self.thread_register.put(1)
			from ..lib.prfftw import threshold
			from ..lib.prfftw import rangereplace
			from ..lib.prfftw import convolve
			from ..lib.prfftw import medianfilter
			def UpdateSupport(self):
				if self.ancestor.GetPage(0).citer_flow[4] > 0:
					self.ancestor.GetPage(0).queue_info.put("Updating support ...")
					self.support[:] = numpy.abs(self.seqdata).copy()
					maxvalue = numpy.abs(self.support).max()
					threshold(self.support, (frac*maxvalue), maxvalue, 0.0)
					medianfilter(self.support, temparray2, 3,3,3, 0.0)
					wrap(self.support, 1)
					convolve(self.support, temparray)
					wrap(self.support, -1)
					rangereplace(self.support, (frac*maxvalue), sys.float_info.max, 0.0, 1.0)
					self.visual_support[:] = numpy.abs(self.support)
					self.ancestor.GetPage(0).queue_info.put("... done.")
			def UpdateVisualSupport(self):
				if self.ancestor.GetPage(0).citer_flow[4] > 0:
					wx.CallAfter(self.ancestor.GetPage(1).UpdateSupport,)
			def GetIterVars(fstartiter, fnumiter, ii, fcycle):
				fsw_startiter = fstartiter + (ii * fcycle)
				if  fnumiter <  ((ii+1) * fcycle):
					fsw_numiter =  fnumiter - (ii * fcycle)
				else:
					fsw_numiter = fcycle
				return fsw_startiter, fsw_numiter
			IterLoops = (numiter + cycle - 1)//cycle
			if RSConst == 'HIO':
				for i in range( IterLoops ):
					sw_startiter, sw_numiter = GetIterVars(startiter, numiter, i, cycle)
					HIO(self, beta, sw_startiter, sw_numiter)
					if self.ancestor.GetPage(0).citer_flow[1] == 2:
						break
					UpdateSupport(self)
					UpdateVisualSupport(self)
			if RSConst == 'PCHIO':
				for i in range( IterLoops ):
					sw_startiter, sw_numiter = GetIterVars(startiter, numiter, i, cycle)
					PCHIO(self, beta, sw_startiter, sw_numiter, phasemax, phasemin)
					if self.ancestor.GetPage(0).citer_flow[1] == 2:
						break
					UpdateSupport(self)
					UpdateVisualSupport(self)
			if RSConst == 'PGCHIO':
				for i in range( IterLoops ):
					sw_startiter, sw_numiter = GetIterVars(startiter, numiter, i, cycle)
					PGCHIO(self, beta, sw_startiter, sw_numiter, gc_phasemax, gc_phasemin, qx, qy, qz)
					if self.ancestor.GetPage(0).citer_flow[1] == 2:
						break
					UpdateSupport(self)
					UpdateVisualSupport(self)
			if RSConst == 'HIOMask':
				for i in range( IterLoops ):
					sw_startiter, sw_numiter = GetIterVars(startiter, numiter, i, cycle)
					HIOMask(self, beta, sw_startiter, sw_numiter, 0)
					if self.ancestor.GetPage(0).citer_flow[1] == 2:
						break
					UpdateSupport(self)
					UpdateVisualSupport(self)
			if RSConst == 'HIOPlus':
				for i in range( IterLoops ):
					sw_startiter, sw_numiter = GetIterVars(startiter, numiter, i, cycle)
					HIOPlus(self, beta, sw_startiter, sw_numiter)
					if self.ancestor.GetPage(0).citer_flow[1] == 2:
						break
					UpdateSupport(self)
					UpdateVisualSupport(self)
			if RSConst == 'ER':
				for i in range( IterLoops ):
					sw_startiter, sw_numiter = GetIterVars(startiter, numiter, i, cycle)
					ER(self, sw_startiter, sw_numiter)
					if self.ancestor.GetPage(0).citer_flow[1] == 2:
						break
					UpdateSupport(self)
					UpdateVisualSupport(self)
			if RSConst == 'HPR':
				for i in range( IterLoops ):
					sw_startiter, sw_numiter = GetIterVars(startiter, numiter, i, cycle)
					HPR(self, beta, sw_startiter, sw_numiter,0)
					if self.ancestor.GetPage(0).citer_flow[1] == 2:
						break
					UpdateSupport(self)
					UpdateVisualSupport(self)
			if RSConst == 'RAAR':
				for i in range( IterLoops ):
					sw_startiter, sw_numiter = GetIterVars(startiter, numiter, i, cycle)
					RAAR(self, beta, sw_startiter, sw_numiter,0)
					if self.ancestor.GetPage(0).citer_flow[1] == 2:
						break
					UpdateSupport(self)
					UpdateVisualSupport(self)
			if RSConst == 'CSHIO':
				for i in range( IterLoops ):
					sw_startiter, sw_numiter = GetIterVars(startiter, numiter, i, cycle)
					CSHIO(self, beta, sw_startiter, sw_numiter, cs_p, cs_epsilon, cs_epsilon_min, cs_d, cs_eta, cs_relax)
					if self.ancestor.GetPage(0).citer_flow[1] == 2:
						break
					UpdateSupport(self)
					UpdateVisualSupport(self)
			self.thread_register.get()
			return
		self.thread = threading.Thread(target=threadShrinkWrap, args=(self,))
		self.thread.daemon = True
		self.thread.start()
		return
def Sequence_CSHIO(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		if self.citer_flow[1] == 2: return;
		expdata_path = pipelineitem.exp_amps.objectpath.GetValue()
		try:
			self.expdata = LoadArray(self, expdata_path)
			if pipelineitem.chkbox_sqrt_expamps.GetValue() == True:
				numpy.sqrt(self.expdata, self.expdata)
			self.expdata[:] = WrapArray(self.expdata).copy()
		except:
			msg = "Could not load array from: \n"+ expdata_path + "\nPlease check the path."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			return
		support_path = pipelineitem.support.objectpath.GetValue()
		if support_path == "":
			try:
				self.support
			except AttributeError:
				msg = "No existing Support array found."
				dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()
				self.pipeline_started = False
				return
		else:
			try:
				self.support = LoadArray(self, support_path)
			except:
				msg = "Could not load array from: \n"+ support_path + "\nPlease check the path."
				dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()
				self.pipeline_started = False
				return
		mask_path = pipelineitem.mask.objectpath.GetValue()
		try:
			self.mask = LoadArray(self, mask_path)
			self.mask[:] = WrapArray(self.mask).copy()
		except:
			msg = "Could not load array from: \n"+ mask_path + "\nPlease check the path."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			return
		if (not (self.expdata.shape == self.support.shape and self.expdata.shape == self.mask.shape)) == True:
			msg = "Array dimensions are inconsistent."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			self.seqdata = None
			try:
				self.visual_amp_real = None
			except:
				pass
			try:
				self.visual_amp_recip = None
			except:
				pass
			try:
				self.visual_amp_support = None
			except:
				pass
			return
		beta = float(pipelineitem.beta.value.GetValue())
		startiter = int(pipelineitem.start_iter)
		numiter = int(pipelineitem.niter.value.GetValue())
		cs_p = float(pipelineitem.cs_p.value.GetValue())
		cs_epsilon = float(pipelineitem.cs_epsilon.value.GetValue())
		cs_epsilon_min = float(pipelineitem.cs_epsilon_min.value.GetValue())
		cs_d = float(pipelineitem.cs_d.value.GetValue())
		cs_eta = float(pipelineitem.cs_eta.value.GetValue())
		if pipelineitem.chkbox_relax.GetValue() == True:
			relax = 1
		else:
			relax = 0
		if startiter == 0 and (self.visual_amp_real is not None or self.visual_support is not None or self.visual_amp_recip is not None):
			if self.expdata.shape[2] == 1:
				PrepareVisualisation2D(self,pipelineitem)
			else:
				PrepareVisualisation(self,pipelineitem)
		def threadCSHIO(self):
			self.ancestor.GetPage(0).queue_info.put("Starting CSHIO Algorithm...")
			self.thread_register.put(1)
			CSHIO(self, beta, startiter, numiter, cs_p, cs_epsilon, cs_epsilon_min, cs_d, cs_eta, relax)
			self.thread_register.get()
			return
		self.thread = threading.Thread(target=threadCSHIO, args=(self,))
		self.thread.daemon = True
		self.thread.start()
		return
def Sequence_PhasePC(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		if self.citer_flow[1] == 2: return;
		expdata_path = pipelineitem.exp_amps.objectpath.GetValue()
		try:
			self.expdata = LoadArray(self, expdata_path)
			if pipelineitem.chkbox_sqrt_expamps.GetValue() == True:
				numpy.sqrt(self.expdata, self.expdata)
			self.expdata[:] = WrapArray(self.expdata).copy()
		except:
			msg = "Could not load array from: \n"+ expdata_path + "\nPlease check the path."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			return
		support_path = pipelineitem.support.objectpath.GetValue()
		if support_path == "":
			try:
				self.support
			except AttributeError:
				msg = "No existing Support array found."
				dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()
				self.pipeline_started = False
				return
		else:
			try:
				self.support = LoadArray(self, support_path)
			except:
				msg = "Could not load array from: \n"+ support_path + "\nPlease check the path."
				dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()
				self.pipeline_started = False
				return
		mask_path = pipelineitem.mask.objectpath.GetValue()
		try:
			self.mask = LoadArray(self, mask_path)
			self.mask[:] = WrapArray(self.mask).copy()
		except:
			msg = "Could not load array from: \n"+ mask_path + "\nPlease check the path."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			return
		gammaHWHM = float(pipelineitem.gammaHWHM.value.GetValue())
		try:
			from ..lib.prfftw import lorentzftfill
			if self.psf is None:
				self.psf = numpy.array( self.seqdata, copy=True, dtype=numpy.cdouble)
				lorentzftfill(self.psf,gammaHWHM)
		except MemoryError:
			msg = "Could not load PSF array. Insufficient memory."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			return
		if (not (self.expdata.shape == self.support.shape and self.expdata.shape == self.mask.shape and self.expdata.shape == self.psf.shape)) == True:
			msg = "Array dimensions are inconsistent."
			dlg = wx.MessageDialog(self, msg, "Pipeline Message", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
			self.pipeline_started = False
			self.seqdata = None
			try:
				self.visual_amp_real = None
			except:
				pass
			try:
				self.visual_amp_recip = None
			except:
				pass
			try:
				self.visual_amp_support = None
			except:
				pass
			return
		startiter = int(pipelineitem.start_iter)
		if startiter == 0 and (self.visual_amp_real is not None or self.visual_support is not None or self.visual_amp_recip is not None):
			if self.expdata.shape[2] == 1:
				PrepareVisualisation2D(self,pipelineitem)
			else:
				PrepareVisualisation(self,pipelineitem)
def Sequence_HIOMaskPC(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		if self.citer_flow[1] == 2: return;
		startiter = int(pipelineitem.start_iter)
		numiter = int(pipelineitem.niter.value.GetValue())
		beta = float(pipelineitem.beta.value.GetValue())
		niterrlpre = int(pipelineitem.niterrlpre.value.GetValue())
		niterrl = int(pipelineitem.niterrl.value.GetValue())
		niterrlinterval = int(pipelineitem.niterrlinterval.value.GetValue())
		accel = int(pipelineitem.accel.value.GetValue())
		gammaHWHM = float(pipelineitem.gammaHWHM.value.GetValue())
		zex =  int(pipelineitem.zedims[0].value.GetValue())
		zey =  int(pipelineitem.zedims[1].value.GetValue())
		zez =  int(pipelineitem.zedims[2].value.GetValue())
		if pipelineitem.chkbox_reset_gamma.GetValue() == True:
			reset_gamma = 1
		else:
			reset_gamma = 0
		def threadHIOMaskPC(self):
			self.ancestor.GetPage(0).queue_info.put("Starting HIO Mask PC Algorithm...")
			self.thread_register.put(1)
			HIOMaskPC(self, beta, startiter, numiter, niterrlpre, niterrl, niterrlinterval, gammaHWHM, zex, zey, zez, reset_gamma, accel)
			self.thread_register.get()
			return
		self.thread = threading.Thread(target=threadHIOMaskPC, args=(self,))
		self.thread.daemon = True
		self.thread.start()
def Sequence_ERMaskPC(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		if self.citer_flow[1] == 2: return;
		startiter = int(pipelineitem.start_iter)
		numiter = int(pipelineitem.niter.value.GetValue())
		niterrlpre = int(pipelineitem.niterrlpre.value.GetValue())
		niterrl = int(pipelineitem.niterrl.value.GetValue())
		niterrlinterval = int(pipelineitem.niterrlinterval.value.GetValue())
		accel = int(pipelineitem.accel.value.GetValue())
		gammaHWHM = float(pipelineitem.gammaHWHM.value.GetValue())
		zex =  int(pipelineitem.zedims[0].value.GetValue())
		zey =  int(pipelineitem.zedims[1].value.GetValue())
		zez =  int(pipelineitem.zedims[2].value.GetValue())
		if pipelineitem.chkbox_reset_gamma.GetValue() == True:
			reset_gamma = 1
		else:
			reset_gamma = 0
		def threadERMaskPC(self):
			self.ancestor.GetPage(0).queue_info.put("Starting ER Mask PC Algorithm...")
			self.thread_register.put(1)
			ERMaskPC(self, startiter, numiter, niterrlpre, niterrl, niterrlinterval, gammaHWHM, zex, zey, zez, reset_gamma, accel)
			self.thread_register.get()
			return
		self.thread = threading.Thread(target=threadERMaskPC, args=(self,))
		self.thread.daemon = True
		self.thread.start()
def Sequence_HPRMaskPC(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		if self.citer_flow[1] == 2: return;
		startiter = int(pipelineitem.start_iter)
		numiter = int(pipelineitem.niter.value.GetValue())
		beta = float(pipelineitem.beta.value.GetValue())
		niterrlpre = int(pipelineitem.niterrlpre.value.GetValue())
		niterrl = int(pipelineitem.niterrl.value.GetValue())
		niterrlinterval = int(pipelineitem.niterrlinterval.value.GetValue())
		accel = int(pipelineitem.accel.value.GetValue())
		gammaHWHM = float(pipelineitem.gammaHWHM.value.GetValue())
		zex =  int(pipelineitem.zedims[0].value.GetValue())
		zey =  int(pipelineitem.zedims[1].value.GetValue())
		zez =  int(pipelineitem.zedims[2].value.GetValue())
		if pipelineitem.chkbox_reset_gamma.GetValue() == True:
			reset_gamma = 1
		else:
			reset_gamma = 0
		def threadHPRMaskPC(self):
			self.ancestor.GetPage(0).queue_info.put("Starting HPR Mask PC Algorithm...")
			self.thread_register.put(1)
			HPRMaskPC(self, beta, startiter, numiter, niterrlpre, niterrl, niterrlinterval, gammaHWHM, zex, zey, zez, reset_gamma, accel)
			self.thread_register.get()
			return
		self.thread = threading.Thread(target=threadHPRMaskPC, args=(self,))
		self.thread.daemon = True
		self.thread.start()
def Sequence_RAARMaskPC(\
	self,
	pipelineitem
	):
	if self.pipeline_started == True:
		if self.citer_flow[1] == 2: return;
		startiter = int(pipelineitem.start_iter)
		numiter = int(pipelineitem.niter.value.GetValue())
		beta = float(pipelineitem.beta.value.GetValue())
		niterrlpre = int(pipelineitem.niterrlpre.value.GetValue())
		niterrl = int(pipelineitem.niterrl.value.GetValue())
		niterrlinterval = int(pipelineitem.niterrlinterval.value.GetValue())
		accel = int(pipelineitem.accel.value.GetValue())
		gammaHWHM = float(pipelineitem.gammaHWHM.value.GetValue())
		zex =  int(pipelineitem.zedims[0].value.GetValue())
		zey =  int(pipelineitem.zedims[1].value.GetValue())
		zez =  int(pipelineitem.zedims[2].value.GetValue())
		if pipelineitem.chkbox_reset_gamma.GetValue() == True:
			reset_gamma = 1
		else:
			reset_gamma = 0
		def threadRAARMaskPC(self):
			self.ancestor.GetPage(0).queue_info.put("Starting RAAR Mask PC Algorithm...")
			self.thread_register.put(1)
			RAARMaskPC(self, beta, startiter, numiter, niterrlpre, niterrl, niterrlinterval, gammaHWHM, zex, zey, zez, reset_gamma, accel)
			self.thread_register.get()
			return
		self.thread = threading.Thread(target=threadRAARMaskPC, args=(self,))
		self.thread.daemon = True
		self.thread.start()