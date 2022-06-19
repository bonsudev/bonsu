###################################################
## Filename: plotcanvas.py
##
## Modified version of plotcanvas.py, from the wx library
##
## Marcus C. Newton 2022
##
##
##
##
##
##
##
##
##
##
##
##
## Contact: Bonsu.Devel@gmail.com
###################################################
import sys
import time as _time
import wx
import numpy as np
from wx.lib.plot.polyobjects import PlotPrintout
from wx.lib.plot.polyobjects import PolyPoints, PolyMarker, PolyBoxPlot
from wx.lib.plot.utils import DisplaySide
from wx.lib.plot.utils import set_displayside
from wx.lib.plot.utils import TempStyle
from wx.lib.plot.utils import scale_and_shift_point
class Pen(wx.Pen):
	def __init__(self, colour, width=1, style=wx.PENSTYLE_SOLID):
		super().__init__()
		super().SetColour(colour)
		super().SetWidth(int(width))
		super().SetStyle(style)
class BufferedDC(wx.BufferedDC):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
	def DrawText(self, text, x, y):
		super().DrawText(text, int(x), int(y))
	def DrawRotatedText(self, text, x, y, angle):
		super().DrawRotatedText(text, int(x), int(y), angle)
	def DrawLine(self, x1, y1, x2, y2):
		super().DrawLine(int(x1), int(y1), int(x2), int(y2))
	def DrawTextList(self, textList, coords, *args):
		super().DrawTextList(textList, [(int(coord[0]),int(coord[1])) for coord in coords], *args)
	def SetClippingRegion(self, x, y, width, height):
		super().SetClippingRegion(int(x), int(y), int(width), int(height))
class PolyLine(PolyPoints):
	_attributes = {'colour': 'black',
							'width': 1,
							'style': wx.PENSTYLE_SOLID,
							'legend': '',
							'drawstyle': 'line',
							}
	_drawstyles = ("line", "steps-pre", "steps-post",
							"steps-mid-x", "steps-mid-y")
	def __init__(self, points, **attr):
		PolyPoints.__init__(self, points, attr)
	def draw(self, dc, printerScale, coord=None):
		colour = self.attributes['colour']
		width = self.attributes['width'] * printerScale * self._pointSize[0]
		style = self.attributes['style']
		drawstyle = self.attributes['drawstyle']
		if not isinstance(colour, wx.Colour):
			colour = wx.Colour(colour)
		pen = Pen(colour, width, style)
		pen.SetCap(wx.CAP_BUTT)
		dc.SetPen(pen)
		if coord is None:
			if len(self.scaled):
				for c1, c2 in zip(self.scaled, self.scaled[1:]):
					self._path(dc, c1, c2, drawstyle)
		else:
			dc.DrawLines(coord)
	def getSymExtent(self, printerScale):
		h = self.attributes['width'] * printerScale * self._pointSize[0]
		w = 5 * h
		return (w, h)
	def _path(self, dc, coord1, coord2, drawstyle):
		line = [coord1, coord2]
		dc.DrawLine(*line[0], *line[1])
class PlotCanvas(wx.Panel):
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
				 size=wx.DefaultSize, style=0, name="plotCanvas"):
		wx.Panel.__init__(self, parent, id, pos, size, style, name)
		sizer = wx.FlexGridSizer(2, 2, 0, 0)
		self.canvas = wx.Window(self, -1)
		self.sb_vert = wx.ScrollBar(self, -1, style=wx.SB_VERTICAL)
		self.sb_vert.SetScrollbar(0, 1000, 1000, 1000)
		self.sb_hor = wx.ScrollBar(self, -1, style=wx.SB_HORIZONTAL)
		self.sb_hor.SetScrollbar(0, 1000, 1000, 1000)
		sizer.Add(self.canvas, 1, wx.EXPAND)
		sizer.Add(self.sb_vert, 0, wx.EXPAND)
		sizer.Add(self.sb_hor, 0, wx.EXPAND)
		sizer.Add((0, 0))
		self.sb_vert.Show(False)
		self.sb_hor.Show(False)
		self.SetSizer(sizer)
		sizer.AddGrowableRow(0, 1)
		sizer.AddGrowableCol(0, 1)
		self.Fit()
		self.border = (1, 1)
		self.SetBackgroundColour("white")
		self.canvas.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
		self.canvas.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
		self.canvas.Bind(wx.EVT_MOTION, self.OnMotion)
		self.canvas.Bind(wx.EVT_LEFT_DCLICK, self.OnMouseDoubleClick)
		self.canvas.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseRightDown)
		self.Bind(wx.EVT_SCROLL_THUMBTRACK, self.OnScroll)
		self.Bind(wx.EVT_SCROLL_PAGEUP, self.OnScroll)
		self.Bind(wx.EVT_SCROLL_PAGEDOWN, self.OnScroll)
		self.Bind(wx.EVT_SCROLL_LINEUP, self.OnScroll)
		self.Bind(wx.EVT_SCROLL_LINEDOWN, self.OnScroll)
		self.defaultCursor = wx.Cursor(wx.CURSOR_ARROW)
		self.HandCursor = wx.Cursor(wx.CURSOR_SIZING)
		self.GrabHandCursor = wx.Cursor(wx.CURSOR_SIZING)
		self.MagCursor = wx.Cursor(wx.CURSOR_MAGNIFIER)
		self.canvas.SetCursor(self.defaultCursor)
		self._print_data = None
		self._pageSetupData = None
		self.printerScale = 1
		self.parent = parent
		self._sb_ignore = False
		self._sb_show = False
		self._adjustingSB = False
		self._sb_xfullrange = 0
		self._sb_yfullrange = 0
		self._sb_xunit = 0
		self._sb_yunit = 0
		self._screenCoordinates = np.array([0.0, 0.0])
		self._zoomInFactor = 0.5
		self._zoomOutFactor = 2
		self._zoomCorner1 = np.array([0.0, 0.0])
		self._zoomCorner2 = np.array([0.0, 0.0])
		self._zoomEnabled = False
		self._hasDragged = False
		self.last_draw = None
		self._pointScale = 1
		self._pointShift = 0
		self._xSpec = 'auto'
		self._ySpec = 'auto'
		self._dragEnabled = False
		self._logscale = (False, False)
		self._absScale = (False, False)
		self._gridEnabled = (True, True)
		self._legendEnabled = False
		self._titleEnabled = True
		self._xAxisLabelEnabled = True
		self._yAxisLabelEnabled = True
		self._axesLabelsEnabled = True
		self._centerLinesEnabled = False
		self._diagonalsEnabled = False
		self._ticksEnabled = DisplaySide(False, False, False, False)
		self._axesEnabled = DisplaySide(True, True, True, True)
		self._axesValuesEnabled = DisplaySide(True, True, False, False)
		self._fontCache = {}
		self._fontSizeAxis = 10
		self._fontSizeTitle = 15
		self._fontSizeLegend = 7
		self._pointLabelEnabled = False
		self.last_PointLabel = None
		self._pointLabelFunc = None
		self.canvas.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeave)
		if sys.platform != "darwin":
			self._logicalFunction = wx.EQUIV
		else:
			self._logicalFunction = wx.COPY
		self._useScientificNotation = False
		self._antiAliasingEnabled = False
		self._hiResEnabled = False
		self._pointSize = (1.0, 1.0)
		self._fontScale = 1.0
		self.canvas.Bind(wx.EVT_PAINT, self.OnPaint)
		self.canvas.Bind(wx.EVT_SIZE, self.OnSize)
		self.OnSize(None)
		self._gridPen = Pen(wx.Colour(180, 180, 180, 255),
							   self._pointSize[0],
							   wx.PENSTYLE_DOT)
		self._centerLinePen = Pen(wx.RED,
									 self._pointSize[0],
									 wx.PENSTYLE_SHORT_DASH)
		self._axesPen = Pen(wx.BLACK,
							   self._pointSize[0],
							   wx.PENSTYLE_SOLID)
		self._tickPen = Pen(wx.BLACK,
							   self._pointSize[0],
							   wx.PENSTYLE_SOLID)
		self._tickLength = tuple(-x * 2 for x in self._pointSize)
		self._diagonalPen = Pen(wx.BLUE,
								   self._pointSize[0],
								   wx.PENSTYLE_DOT_DASH)
	def SetCursor(self, cursor):
		self.canvas.SetCursor(cursor)
	@property
	def gridPen(self):
		return self._gridPen
	@gridPen.setter
	def gridPen(self, pen):
		if not isinstance(pen, wx.Pen):
			raise TypeError("pen must be an instance of wx.Pen")
		self._gridPen = pen
	@property
	def diagonalPen(self):
		return self._diagonalPen
	@diagonalPen.setter
	def diagonalPen(self, pen):
		if not isinstance(pen, wx.Pen):
			raise TypeError("pen must be an instance of wx.Pen")
		self._diagonalPen = pen
	@property
	def centerLinePen(self):
		return self._centerLinePen
	@centerLinePen.setter
	def centerLinePen(self, pen):
		if not isinstance(pen, wx.Pen):
			raise TypeError("pen must be an instance of wx.Pen")
		self._centerLinePen = pen
	@property
	def axesPen(self):
		return self._axesPen
	@axesPen.setter
	def axesPen(self, pen):
		if not isinstance(pen, wx.Pen):
			raise TypeError("pen must be an instance of wx.Pen")
		self._axesPen = pen
	@property
	def tickPen(self):
		return self._tickPen
	@tickPen.setter
	def tickPen(self, pen):
		if not isinstance(pen, wx.Pen):
			raise TypeError("pen must be an instance of wx.Pen")
		self._tickPen = pen
	@property
	def tickLength(self):
		return self._tickLength
	@tickLength.setter
	def tickLength(self, length):
		if not isinstance(length, (tuple, list)):
			raise TypeError("`length` must be a 2-tuple of ints or floats")
		self._tickLength = length
	@property
	def tickLengthPrinterScale(self):
		return (3 * self.printerScale * self._tickLength[0],
				3 * self.printerScale * self._tickLength[1])
	def SaveFile(self, fileName=''):
		extensions = {
			"bmp": wx.BITMAP_TYPE_BMP,
			"xbm": wx.BITMAP_TYPE_XBM,
			"xpm": wx.BITMAP_TYPE_XPM,
			"jpg": wx.BITMAP_TYPE_JPEG,
			"png": wx.BITMAP_TYPE_PNG,
		}
		fType = fileName[-3:].lower()
		dlg1 = None
		while fType not in extensions:
			msg_txt = ('File name extension\n'
					   'must be one of\nbmp, xbm, xpm, png, or jpg')
			if dlg1:
				dlg2 = wx.MessageDialog(self, msg_txt, 'File Name Error',
										wx.OK | wx.ICON_ERROR)
				try:
					dlg2.ShowModal()
				finally:
					dlg2.Destroy()
			else:
				msg_txt = ("Choose a file with extension bmp, "
						   "gif, xbm, xpm, png, or jpg")
				wildcard_str = ("BMP files (*.bmp)|*.bmp|XBM files (*.xbm)|"
								"*.xbm|XPM file (*.xpm)|*.xpm|"
								"PNG files (*.png)|*.png|"
								"JPG files (*.jpg)|*.jpg")
				dlg1 = wx.FileDialog(self,
									 msg_txt,
									 ".",
									 "",
									 wildcard_str,
									 wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
									 )
			if dlg1.ShowModal() == wx.ID_OK:
				fileName = dlg1.GetPath()
				fType = fileName[-3:].lower()
			else:
				dlg1.Destroy()
				return False
		if dlg1:
			dlg1.Destroy()
		res = self._Buffer.SaveFile(fileName, extensions[fType])
		return res
	@property
	def print_data(self):
		if not self._print_data:
			self._print_data = wx.PrintData()
			self._print_data.SetPaperId(wx.PAPER_LETTER)
			self._print_data.SetOrientation(wx.LANDSCAPE)
		return self._print_data
	@property
	def pageSetupData(self):
		if not self._pageSetupData:
			self._pageSetupData = wx.PageSetupDialogData()
			self._pageSetupData.SetMarginBottomRight((25, 25))
			self._pageSetupData.SetMarginTopLeft((25, 25))
			self._pageSetupData.SetPrintData(self.print_data)
		return self._pageSetupData
	def PageSetup(self):
		data = self.pageSetupData
		data.SetPrintData(self.print_data)
		dlg = wx.PageSetupDialog(self.parent, data)
		try:
			if dlg.ShowModal() == wx.ID_OK:
				data = dlg.GetPageSetupData()
				self.pageSetupData.SetMarginBottomRight(
					data.GetMarginBottomRight())
				self.pageSetupData.SetMarginTopLeft(data.GetMarginTopLeft())
				self.pageSetupData.SetPrintData(data.GetPrintData())
				self._print_data = wx.PrintData(
					data.GetPrintData())
		finally:
			dlg.Destroy()
	def Printout(self, paper=None):
		if paper is not None:
			self.print_data.SetPaperId(paper)
		pdd = wx.PrintDialogData(self.print_data)
		printer = wx.Printer(pdd)
		out = PlotPrintout(self)
		print_ok = printer.Print(self.parent, out)
		if print_ok:
			self._print_data = wx.PrintData(
				printer.GetPrintDialogData().GetPrintData())
		out.Destroy()
	def PrintPreview(self):
		printout = PlotPrintout(self)
		printout2 = PlotPrintout(self)
		self.preview = wx.PrintPreview(printout, printout2, self.print_data)
		if not self.preview.IsOk():
			wx.MessageDialog(self, "Print Preview failed.\n"
							 "Check that default printer is configured\n",
							 "Print error", wx.OK | wx.CENTRE).ShowModal()
		self.preview.SetZoom(40)
		frameInst = self
		while not isinstance(frameInst, wx.Frame):
			frameInst = frameInst.GetParent()
		frame = wx.PreviewFrame(self.preview, frameInst, "Preview")
		frame.Initialize()
		frame.SetPosition(self.GetPosition())
		frame.SetSize((600, 550))
		frame.Centre(wx.BOTH)
		frame.Show(True)
	def setLogScale(self, logscale):
		self.logScale = logscale
	def getLogScale(self):
		return self.logScale
	@property
	def logScale(self):
		return self._logscale
	@logScale.setter
	def logScale(self, logscale):
		if type(logscale) != tuple:
			raise TypeError(
				'logscale must be a tuple of bools, e.g. (False, False)'
			)
		if self.last_draw is not None:
			graphics, xAxis, yAxis = self.last_draw
			graphics.logScale = logscale
			self.last_draw = (graphics, None, None)
		self.xSpec = 'min'
		self.ySpec = 'min'
		self._logscale = logscale
	@property
	def absScale(self):
		return self._absScale
	@absScale.setter
	def absScale(self, absscale):
		if not isinstance(absscale, tuple):
			raise TypeError(
				"absscale must be tuple of bools, e.g. (False, False)"
			)
		if self.last_draw is not None:
			graphics, xAxis, yAxis = self.last_draw
			graphics.absScale = absscale
			self.last_draw = (graphics, None, None)
		self.xSpec = 'min'
		self.ySpec = 'min'
		self._absScale = absscale
	def SetFontSizeAxis(self, point=10):
		self.fontSizeAxis = point
	def GetFontSizeAxis(self):
		return self.fontSizeAxis
	@property
	def fontSizeAxis(self):
		return self._fontSizeAxis
	@fontSizeAxis.setter
	def fontSizeAxis(self, value):
		self._fontSizeAxis = value
	def SetFontSizeTitle(self, point=15):
		self.fontSizeTitle = point
	def GetFontSizeTitle(self):
		return self.fontSizeTitle
	@property
	def fontSizeTitle(self):
		return self._fontSizeTitle
	@fontSizeTitle.setter
	def fontSizeTitle(self, pointsize):
		self._fontSizeTitle = pointsize
	def SetFontSizeLegend(self, point=7):
		self.fontSizeLegend = point
	def GetFontSizeLegend(self):
		return self.fontSizeLegend
	@property
	def fontSizeLegend(self):
		return self._fontSizeLegend
	@fontSizeLegend.setter
	def fontSizeLegend(self, point):
		self._fontSizeLegend = point
	def SetShowScrollbars(self, value):
		self.showScrollbars = value
	def GetShowScrollbars(self):
		return self.showScrollbars
	@property
	def showScrollbars(self):
		return self._sb_show
	@showScrollbars.setter
	def showScrollbars(self, value):
		if not isinstance(value, bool):
			raise TypeError("Value should be True or False")
		if value == self._sb_show:
			return
		self._sb_show = value
		self.sb_vert.Show(value)
		self.sb_hor.Show(value)
		def _do_update():
			self.Layout()
			self._adjustScrollbars()
		wx.CallAfter(_do_update)
	def SetUseScientificNotation(self, useScientificNotation):
		self.useScientificNotation = useScientificNotation
	def GetUseScientificNotation(self):
		return self.useScientificNotation
	@property
	def useScientificNotation(self):
		return self._useScientificNotation
	@useScientificNotation.setter
	def useScientificNotation(self, value):
		if not isinstance(value, bool):
			raise TypeError("Value should be True or False")
		self._useScientificNotation = value
	def SetEnableAntiAliasing(self, enableAntiAliasing):
		self.enableAntiAliasing = enableAntiAliasing
	def GetEnableAntiAliasing(self):
		return self.enableAntiAliasing
	@property
	def enableAntiAliasing(self):
		return self._antiAliasingEnabled
	@enableAntiAliasing.setter
	def enableAntiAliasing(self, value):
		if not isinstance(value, bool):
			raise TypeError("Value should be True or False")
		self._antiAliasingEnabled = value
		self.Redraw()
	def SetEnableHiRes(self, enableHiRes):
		self.enableHiRes = enableHiRes
	def GetEnableHiRes(self):
		return self._hiResEnabled
	@property
	def enableHiRes(self):
		return self._hiResEnabled
	@enableHiRes.setter
	def enableHiRes(self, value):
		if not isinstance(value, bool):
			raise TypeError("Value should be True or False")
		self._hiResEnabled = value
		self.Redraw()
	def SetEnableDrag(self, value):
		self.enableDrag = value
	def GetEnableDrag(self):
		return self.enableDrag
	@property
	def enableDrag(self):
		return self._dragEnabled
	@enableDrag.setter
	def enableDrag(self, value):
		if not isinstance(value, bool):
			raise TypeError("Value must be a bool.")
		if value:
			if self.enableZoom:
				self.enableZoom = False
			self.SetCursor(self.HandCursor)
		else:
			self.SetCursor(self.defaultCursor)
		self._dragEnabled = value
	def SetEnableZoom(self, value):
		self.enableZoom = value
	def GetEnableZoom(self):
		return self.enableZoom
	@property
	def enableZoom(self):
		return self._zoomEnabled
	@enableZoom.setter
	def enableZoom(self, value):
		if not isinstance(value, bool):
			raise TypeError("Value must be a bool.")
		if value:
			if self.enableDrag:
				self.enableDrag = False
			self.SetCursor(self.MagCursor)
		else:
			self.SetCursor(self.defaultCursor)
		self._zoomEnabled = value
	def SetEnableGrid(self, value):
		self.enableGrid = value
	def GetEnableGrid(self):
		return self.enableGrid
	@property
	def enableGrid(self):
		return self._gridEnabled
	@enableGrid.setter
	def enableGrid(self, value):
		if isinstance(value, bool):
			value = (value, value)
		elif isinstance(value, tuple) and len(value) == 2:
			pass
		else:
			err_txt = "Value must be a bool or 2-tuple of bool."
			raise TypeError(err_txt)
		self._gridEnabled = value
		self.Redraw()
	def SetEnableCenterLines(self, value):
		self.enableCenterLines = value
	def GetEnableCenterLines(self):
		return self.enableCenterLines
	@property
	def enableCenterLines(self):
		return self._centerLinesEnabled
	@enableCenterLines.setter
	def enableCenterLines(self, value):
		if value not in [True, False, 'Horizontal', 'Vertical']:
			raise TypeError(
				"Value should be True, False, 'Horizontal' or 'Vertical'")
		self._centerLinesEnabled = value
		self.Redraw()
	def SetEnableDiagonals(self, value):
		self.enableDiagonals = value
	def GetEnableDiagonals(self):
		return self.enableDiagonals
	@property
	def enableDiagonals(self):
		return self._diagonalsEnabled
	@enableDiagonals.setter
	def enableDiagonals(self, value):
		if value not in [True, False,
						 'Bottomleft-Topright', 'Bottomright-Topleft']:
			raise TypeError(
				"Value should be True, False, 'Bottomleft-Topright' or "
				"'Bottomright-Topleft'"
			)
		self._diagonalsEnabled = value
		self.Redraw()
	def SetEnableLegend(self, value):
		self.enableLegend = value
	def GetEnableLegend(self):
		return self.enableLegend
	@property
	def enableLegend(self):
		return self._legendEnabled
	@enableLegend.setter
	def enableLegend(self, value):
		if value not in [True, False]:
			raise TypeError("Value should be True or False")
		self._legendEnabled = value
		self.Redraw()
	def SetEnableTitle(self, value):
		self.enableTitle = value
	def GetEnableTitle(self):
		return self.enableTitle
	@property
	def enableTitle(self):
		return self._titleEnabled
	@enableTitle.setter
	def enableTitle(self, value):
		if not isinstance(value, bool):
			raise TypeError("Value must be a bool.")
		self._titleEnabled = value
		self.Redraw()
	def SetEnablePointLabel(self, value):
		self.enablePointLabel = value
	def GetEnablePointLabel(self):
		return self.enablePointLabel
	@property
	def enablePointLabel(self):
		return self._pointLabelEnabled
	@enablePointLabel.setter
	def enablePointLabel(self, value):
		if not isinstance(value, bool):
			raise TypeError("Value must be a bool.")
		self._pointLabelEnabled = value
		self.Redraw()
		self.last_PointLabel = None
	@property
	def enableAxes(self):
		return self._axesEnabled
	@enableAxes.setter
	def enableAxes(self, value):
		self._axesEnabled = set_displayside(value)
		self.Redraw()
	@property
	def enableAxesValues(self):
		return self._axesValuesEnabled
	@enableAxesValues.setter
	def enableAxesValues(self, value):
		self._axesValuesEnabled = set_displayside(value)
		self.Redraw()
	@property
	def enableTicks(self):
		return self._ticksEnabled
	@enableTicks.setter
	def enableTicks(self, value):
		self._ticksEnabled = set_displayside(value)
		self.Redraw()
	@property
	def enablePlotTitle(self):
		return self._titleEnabled
	@enablePlotTitle.setter
	def enablePlotTitle(self, value):
		if not isinstance(value, bool):
			raise TypeError("`value` must be boolean True or False")
		self._titleEnabled = value
		self.Redraw()
	@property
	def enableXAxisLabel(self):
		return self._xAxisLabelEnabled
	@enableXAxisLabel.setter
	def enableXAxisLabel(self, value):
		if not isinstance(value, bool):
			raise TypeError("`value` must be boolean True or False")
		self._xAxisLabelEnabled = value
		self.Redraw()
	@property
	def enableYAxisLabel(self):
		return self._yAxisLabelEnabled
	@enableYAxisLabel.setter
	def enableYAxisLabel(self, value):
		if not isinstance(value, bool):
			raise TypeError("`value` must be boolean True or False")
		self._yAxisLabelEnabled = value
		self.Redraw()
	@property
	def enableAxesLabels(self):
		return self._axesLabelsEnabled
	@enableAxesLabels.setter
	def enableAxesLabels(self, value):
		if not isinstance(value, bool):
			raise TypeError("`value` must be boolean True or False")
		self._axesLabelsEnabled = value
		self.Redraw()
	def SetPointLabelFunc(self, func):
		self.pointLabelFunc = func
	def GetPointLabelFunc(self):
		return self.pointLabelFunc
	@property
	def pointLabelFunc(self):
		return self._pointLabelFunc
	@pointLabelFunc.setter
	def pointLabelFunc(self, func):
		self._pointLabelFunc = func
	def Reset(self):
		self.last_PointLabel = None
		if self.last_draw is not None:
			self._Draw(self.last_draw[0])
	def ScrollRight(self, units):
		self.last_PointLabel = None
		if self.last_draw is not None:
			graphics, xAxis, yAxis = self.last_draw
			xAxis = (xAxis[0] + units, xAxis[1] + units)
			self._Draw(graphics, xAxis, yAxis)
	def ScrollUp(self, units):
		self.last_PointLabel = None
		if self.last_draw is not None:
			graphics, xAxis, yAxis = self.last_draw
			yAxis = (yAxis[0] + units, yAxis[1] + units)
			self._Draw(graphics, xAxis, yAxis)
	def GetXY(self, event):
		x, y = self._getXY(event)
		if self.logScale[0]:
			x = np.power(10, x)
		if self.logScale[1]:
			y = np.power(10, y)
		return x, y
	def _getXY(self, event):
		x, y = self.PositionScreenToUser(event.GetPosition())
		return x, y
	def PositionUserToScreen(self, pntXY):
		userPos = np.array(pntXY)
		x, y = userPos * self._pointScale + self._pointShift
		return x, y
	def PositionScreenToUser(self, pntXY):
		screenPos = np.array(pntXY)
		x, y = (screenPos - self._pointShift) / self._pointScale
		return x, y
	def SetXSpec(self, spectype='auto'):
		self.xSpec = spectype
	def SetYSpec(self, spectype='auto'):
		self.ySpec = spectype
	def GetXSpec(self):
		return self.xSpec
	def GetYSpec(self):
		return self.ySpec
	@property
	def xSpec(self):
		return self._xSpec
	@xSpec.setter
	def xSpec(self, value):
		ok_values = ('none', 'min', 'auto')
		if value not in ok_values and not isinstance(value, (int, float)):
			if not isinstance(value, (list, tuple)) and len(value != 2):
				err_str = ("xSpec must be 'none', 'min', 'auto', "
						   "a number, or sequence of numbers (length 2)")
				raise TypeError(err_str)
		self._xSpec = value
	@property
	def ySpec(self):
		return self._ySpec
	@ySpec.setter
	def ySpec(self, value):
		ok_values = ('none', 'min', 'auto')
		if value not in ok_values and not isinstance(value, (int, float)):
			if not isinstance(value, (list, tuple)) and len(value != 2):
				err_str = ("ySpec must be 'none', 'min', 'auto', "
						   "a number, or sequence of numbers (length 2)")
				raise TypeError(err_str)
		self._ySpec = value
	def GetXMaxRange(self):
		return self.xMaxRange
	@property
	def xMaxRange(self):
		xAxis = self._getXMaxRange()
		if self.logScale[0]:
			xAxis = np.power(10, xAxis)
		return xAxis
	def _getXMaxRange(self):
		graphics = self.last_draw[0]
		p1, p2 = graphics.boundingBox()
		xAxis = self._axisInterval(self._xSpec, p1[0], p2[0])
		return xAxis
	def GetYMaxRange(self):
		return self.yMaxRange
	@property
	def yMaxRange(self):
		yAxis = self._getYMaxRange()
		if self.logScale[1]:
			yAxis = np.power(10, yAxis)
		return yAxis
	def _getYMaxRange(self):
		graphics = self.last_draw[0]
		p1, p2 = graphics.boundingBox()
		yAxis = self._axisInterval(self._ySpec, p1[1], p2[1])
		return yAxis
	def GetXCurrentRange(self):
		return self.xCurrentRange
	@property
	def xCurrentRange(self):
		xAxis = self._getXCurrentRange()
		if self.logScale[0]:
			xAxis = np.power(10, xAxis)
		return xAxis
	def _getXCurrentRange(self):
		return self.last_draw[1]
	def GetYCurrentRange(self):
		return self.yCurrentRange
	@property
	def yCurrentRange(self):
		yAxis = self._getYCurrentRange()
		if self.logScale[1]:
			yAxis = np.power(10, yAxis)
		return yAxis
	def _getYCurrentRange(self):
		return self.last_draw[2]
	def Draw(self, graphics, xAxis=None, yAxis=None, dc=None):
		graphics.logScale = self.logScale
		err_txt = "xAxis should be None or (minX, maxX). Got type `{}`."
		if type(xAxis) not in [type(None), tuple]:
			raise TypeError(err_txt .format(type(xAxis)))
		err_txt = "yAxis should be None or (minY, maxY). Got type `{}`."
		if type(yAxis) not in [type(None), tuple]:
			raise TypeError(err_txt.format(type(yAxis)))
		if xAxis is not None:
			if xAxis[0] == xAxis[1]:
				return
			if self.logScale[0]:
				xAxis = np.log10(xAxis)
		if yAxis is not None:
			if yAxis[0] == yAxis[1]:
				return
			if self.logScale[1]:
				yAxis = np.log10(yAxis)
		self._Draw(graphics, xAxis, yAxis, dc)
	def _Draw(self, graphics, xAxis=None, yAxis=None, dc=None):
		if dc is None:
			dc = BufferedDC(wx.ClientDC(self.canvas), self._Buffer)
			bbr = wx.Brush(self.GetBackgroundColour(), wx.BRUSHSTYLE_SOLID)
			dc.SetBackground(bbr)
			dc.SetBackgroundMode(wx.SOLID)
			dc.Clear()
		if self._antiAliasingEnabled:
			if not isinstance(dc, wx.GCDC):
				try:
					dc = wx.GCDC(dc)
				except Exception:
					pass
				else:
					if self._hiResEnabled:
						dc.SetMapMode(wx.MM_TWIPS)
					self._pointSize = tuple(
						1.0 / lscale for lscale in dc.GetLogicalScale())
					self._setSize()
		elif self._pointSize != (1.0, 1.0):
			self._pointSize = (1.0, 1.0)
			self._setSize()
		if (sys.platform in ("darwin", "win32")
				or not isinstance(dc, wx.GCDC)
				or wx.VERSION >= (2, 9)):
			self._fontScale = sum(self._pointSize) / 2.0
		else:
			screenppi = map(float, wx.ScreenDC().GetPPI())
			ppi = dc.GetPPI()
			self._fontScale = (
				(screenppi[0] / ppi[0] * self._pointSize[0]
				 + screenppi[1] / ppi[1] * self._pointSize[1])
				/ 2.0
			)
		graphics._pointSize = self._pointSize
		dc.SetTextForeground(self.GetForegroundColour())
		dc.SetTextBackground(self.GetBackgroundColour())
		dc.SetFont(self._getFont(self._fontSizeAxis))
		if xAxis is None or yAxis is None:
			p1, p2 = graphics.boundingBox()
			if xAxis is None:
				xAxis = self._axisInterval(
					self._xSpec, p1[0], p2[0])
			if yAxis is None:
				yAxis = self._axisInterval(self._ySpec, p1[1], p2[1])
			p1[0], p1[1] = xAxis[0], yAxis[0]
			p2[0], p2[1] = xAxis[1], yAxis[1]
		else:
			p1 = np.array([xAxis[0], yAxis[0]])
			p2 = np.array([xAxis[1], yAxis[1]])
		self.last_draw = (graphics, np.array(xAxis), np.array(yAxis))
		xticks = yticks = None
		xTextExtent = yTextExtent = (0, 0)
		if self._xSpec != 'none':
			xticks = self._xticks(xAxis[0], xAxis[1])
			xTextExtent = dc.GetTextExtent(xticks[-1][1])
		if self._ySpec != 'none':
			yticks = self._yticks(yAxis[0], yAxis[1])
			if self.logScale[1]:
				yTextExtent = dc.GetTextExtent('-2e-2')
			else:
				yTextExtentBottom = dc.GetTextExtent(yticks[0][1])
				yTextExtentTop = dc.GetTextExtent(yticks[-1][1])
				yTextExtent = (max(yTextExtentBottom[0], yTextExtentTop[0]),
							   max(yTextExtentBottom[1], yTextExtentTop[1]))
		titleWH, xLabelWH, yLabelWH = self._titleLablesWH(dc, graphics)
		legendBoxWH, legendSymExt, legendTextExt = self._legendWH(
			dc,
			graphics
		)
		rhsW = max(xTextExtent[0], legendBoxWH[0]) + 5 * self._pointSize[0]
		lhsW = yTextExtent[0] + yLabelWH[1] + 3 * self._pointSize[0]
		bottomH = (max(xTextExtent[1], yTextExtent[1] / 2.)
				   + xLabelWH[1] + 2 * self._pointSize[1])
		topH = yTextExtent[1] / 2. + titleWH[1]
		textSize_scale = np.array([rhsW + lhsW, bottomH + topH])
		textSize_shift = np.array([lhsW, bottomH])
		self._drawPlotAreaLabels(dc, graphics, lhsW, rhsW, titleWH,
								 bottomH, topH, xLabelWH, yLabelWH)
		if self._legendEnabled:
			self._drawLegend(dc,
							 graphics,
							 rhsW,
							 topH,
							 legendBoxWH,
							 legendSymExt,
							 legendTextExt)
		scale = ((self.plotbox_size - textSize_scale) / (p2 - p1)
				 * np.array((1, -1)))
		shift = (-p1 * scale + self.plotbox_origin
				 + textSize_shift * np.array((1, -1)))
		self._pointScale = scale / self._pointSize
		self._pointShift = shift / self._pointSize
		self._drawPlotAreaItems(dc, p1, p2, scale, shift, xticks, yticks)
		graphics.scaleAndShift(scale, shift)
		graphics.printerScale = self.printerScale
		ptx, pty, rectWidth, rectHeight = self._point2ClientCoord(p1, p2)
		dc.SetClippingRegion(ptx * self._pointSize[0],
							 pty * self._pointSize[1],
							 rectWidth * self._pointSize[0] + 2,
							 rectHeight * self._pointSize[1] + 1)
		graphics.draw(dc)
		dc.DestroyClippingRegion()
		self._adjustScrollbars()
	def Redraw(self, dc=None):
		if self.last_draw is not None:
			graphics, xAxis, yAxis = self.last_draw
			self._Draw(graphics, xAxis, yAxis, dc)
	def Clear(self):
		self.last_PointLabel = None
		dc = BufferedDC(wx.ClientDC(self.canvas), self._Buffer)
		bbr = wx.Brush(self.GetBackgroundColour(), wx.SOLID)
		dc.SetBackground(bbr)
		dc.SetBackgroundMode(wx.SOLID)
		dc.Clear()
		if self._antiAliasingEnabled:
			try:
				dc = wx.GCDC(dc)
			except Exception:
				pass
		dc.SetTextForeground(self.GetForegroundColour())
		dc.SetTextBackground(self.GetBackgroundColour())
		self.last_draw = None
	def Zoom(self, Center, Ratio):
		self.last_PointLabel = None
		x, y = Center
		if self.last_draw is not None:
			(graphics, xAxis, yAxis) = self.last_draw
			w = (xAxis[1] - xAxis[0]) * Ratio[0]
			h = (yAxis[1] - yAxis[0]) * Ratio[1]
			xAxis = (x - w / 2, x + w / 2)
			yAxis = (y - h / 2, y + h / 2)
			self._Draw(graphics, xAxis, yAxis)
	def GetClosestPoints(self, pntXY, pointScaled=True):
		if self.last_draw is None:
			return []
		graphics, xAxis, yAxis = self.last_draw
		l = []
		for curveNum, obj in enumerate(graphics):
			if len(obj.points) == 0:
				continue
			cn = ([curveNum] +
				  [obj.getLegend()] + obj.getClosestPoint(pntXY, pointScaled))
			l.append(cn)
		return l
	def GetClosestPoint(self, pntXY, pointScaled=True):
		closestPts = self.GetClosestPoints(pntXY, pointScaled)
		if closestPts == []:
			return []
		dists = [c[-1] for c in closestPts]
		mdist = min(dists)
		i = dists.index(mdist)
		return closestPts[i]
	def UpdatePointLabel(self, mDataDict):
		if self.last_PointLabel is not None:
			if np.sometrue(
					mDataDict["pointXY"] != self.last_PointLabel["pointXY"]):
				self._drawPointLabel(self.last_PointLabel)
				self._drawPointLabel(mDataDict)
		else:
			self._drawPointLabel(mDataDict)
		self.last_PointLabel = mDataDict
	def OnMotion(self, event):
		if self._zoomEnabled and event.LeftIsDown():
			if self._hasDragged:
				self._drawRubberBand(
					self._zoomCorner1, self._zoomCorner2)
			else:
				self._hasDragged = True
			self._zoomCorner2[0], self._zoomCorner2[1] = self._getXY(event)
			self._drawRubberBand(
				self._zoomCorner1, self._zoomCorner2)
		elif self._dragEnabled and event.LeftIsDown():
			coordinates = event.GetPosition()
			newpos, oldpos = map(
				np.array,
				map(self.PositionScreenToUser,
					[coordinates, self._screenCoordinates]
					)
			)
			dist = newpos - oldpos
			self._screenCoordinates = coordinates
			if self.last_draw is not None:
				graphics, xAxis, yAxis = self.last_draw
				yAxis -= dist[1]
				xAxis -= dist[0]
				self._Draw(graphics, xAxis, yAxis)
	def OnMouseLeftDown(self, event):
		self._zoomCorner1[0], self._zoomCorner1[1] = self._getXY(event)
		self._screenCoordinates = np.array(event.GetPosition())
		if self._dragEnabled:
			self.SetCursor(self.GrabHandCursor)
			self.canvas.CaptureMouse()
	def OnMouseLeftUp(self, event):
		if self._zoomEnabled:
			if self._hasDragged is True:
				self._drawRubberBand(
					self._zoomCorner1, self._zoomCorner2)
				self._zoomCorner2[0], self._zoomCorner2[1] = self._getXY(event)
				self._hasDragged = False
				minX, minY = np.minimum(self._zoomCorner1, self._zoomCorner2)
				maxX, maxY = np.maximum(self._zoomCorner1, self._zoomCorner2)
				self.last_PointLabel = None
				if self.last_draw is not None:
					self._Draw(self.last_draw[0],
							   xAxis=(minX, maxX),
							   yAxis=(minY, maxY),
							   dc=None)
		if self._dragEnabled:
			self.SetCursor(self.HandCursor)
			if self.canvas.HasCapture():
				self.canvas.ReleaseMouse()
	def OnMouseDoubleClick(self, event):
		if self._zoomEnabled:
			wx.CallLater(200, self.Reset)
	def OnMouseRightDown(self, event):
		if self._zoomEnabled:
			X, Y = self._getXY(event)
			self.Zoom((X, Y), (self._zoomOutFactor, self._zoomOutFactor))
	def OnPaint(self, event):
		if self.last_PointLabel is not None:
			self._drawPointLabel(self.last_PointLabel)
			self.last_PointLabel = None
		dc = wx.BufferedPaintDC(self.canvas, self._Buffer)
		if self._antiAliasingEnabled:
			try:
				dc = wx.GCDC(dc)
			except Exception:
				pass
	def OnSize(self, event):
		Size = self.canvas.GetClientSize()
		Size.width = max(1, Size.width)
		Size.height = max(1, Size.height)
		self._Buffer = wx.Bitmap(Size.width, Size.height)
		self._setSize()
		self.last_PointLabel = None
		if self.last_draw is None:
			self.Clear()
		else:
			graphics, xSpec, ySpec = self.last_draw
			self._Draw(graphics, xSpec, ySpec)
	def OnLeave(self, event):
		if self.last_PointLabel is not None:
			self._drawPointLabel(self.last_PointLabel)
			self.last_PointLabel = None
	def OnScroll(self, evt):
		if not self._adjustingSB:
			self._sb_ignore = True
			sbpos = evt.GetPosition()
			if evt.GetOrientation() == wx.VERTICAL:
				fullrange = self.sb_vert.GetRange()
				pagesize = self.sb_vert.GetPageSize()
				sbpos = fullrange - pagesize - sbpos
				dist = (sbpos * self._sb_yunit -
						(self._getYCurrentRange()[0] - self._sb_yfullrange[0]))
				self.ScrollUp(dist)
			if evt.GetOrientation() == wx.HORIZONTAL:
				dist = (sbpos * self._sb_xunit -
						(self._getXCurrentRange()[0] - self._sb_xfullrange[0]))
				self.ScrollRight(dist)
	def _setSize(self, width=None, height=None):
		if width is None:
			(self.width, self.height) = self.canvas.GetClientSize()
		else:
			self.width, self.height = width, height
		self.width *= self._pointSize[0]
		self.height *= self._pointSize[1]
		self.plotbox_size = 0.97 * np.array([self.width, self.height])
		xo = 0.5 * (self.width - self.plotbox_size[0])
		yo = self.height - 0.5 * (self.height - self.plotbox_size[1])
		self.plotbox_origin = np.array([xo, yo])
	def _setPrinterScale(self, scale):
		self.printerScale = scale
	def _printDraw(self, printDC):
		if self.last_draw is not None:
			graphics, xSpec, ySpec = self.last_draw
			self._Draw(graphics, xSpec, ySpec, printDC)
	def _drawPointLabel(self, mDataDict):
		width = self._Buffer.GetWidth()
		height = self._Buffer.GetHeight()
		if sys.platform != "darwin":
			tmp_Buffer = wx.Bitmap(width, height)
			dcs = wx.MemoryDC()
			dcs.SelectObject(tmp_Buffer)
			dcs.Clear()
		else:
			tmp_Buffer = self._Buffer.GetSubBitmap((0, 0, width, height))
			dcs = wx.MemoryDC(self._Buffer)
		self._pointLabelFunc(dcs, mDataDict)
		dc = wx.ClientDC(self.canvas)
		dc = BufferedDC(dc, self._Buffer)
		dc.Blit(0, 0, width, height, dcs, 0, 0, self._logicalFunction)
		if sys.platform == "darwin":
			self._Buffer = tmp_Buffer
	def _drawLegend(self, dc, graphics, rhsW, topH, legendBoxWH,
					legendSymExt, legendTextExt):
		trhc = (self.plotbox_origin +
				(self.plotbox_size - [rhsW, topH]) * [1, -1])
		legendLHS = .091 * legendBoxWH[0]
		lineHeight = max(legendSymExt[1], legendTextExt[1]) * 1.1
		dc.SetFont(self._getFont(self._fontSizeLegend))
		for i in range(len(graphics)):
			o = graphics[i]
			s = i * lineHeight
			if isinstance(o, PolyMarker) or isinstance(o, PolyBoxPlot):
				pnt = (trhc[0] + legendLHS + legendSymExt[0] / 2.,
					   trhc[1] + s + lineHeight / 2.)
				o.draw(dc, self.printerScale, coord=np.array([pnt]))
			elif isinstance(o, PolyLine):
				pnt1 = (trhc[0] + legendLHS, trhc[1] + s + lineHeight / 2.)
				pnt2 = (trhc[0] + legendLHS + legendSymExt[0],
						trhc[1] + s + lineHeight / 2.)
				o.draw(dc, self.printerScale, coord=np.array([pnt1, pnt2]))
			else:
				raise TypeError(
					"object is neither PolyMarker or PolyLine instance")
			pnt = ((trhc[0] + legendLHS + legendSymExt[0]
					+ 5 * self._pointSize[0]),
					trhc[1] + s + lineHeight / 2. - legendTextExt[1] / 2)
			dc.DrawText(o.getLegend(), pnt[0], pnt[1])
		dc.SetFont(self._getFont(self._fontSizeAxis))
	def _titleLablesWH(self, dc, graphics):
		dc.SetFont(self._getFont(self._fontSizeTitle))
		if self.enablePlotTitle:
			title = graphics.title
			titleWH = dc.GetTextExtent(title)
		else:
			titleWH = (0, 0)
		dc.SetFont(self._getFont(self._fontSizeAxis))
		xLabel, yLabel = graphics.xLabel, graphics.yLabel
		xLabelWH = dc.GetTextExtent(xLabel)
		yLabelWH = dc.GetTextExtent(yLabel)
		return titleWH, xLabelWH, yLabelWH
	def _legendWH(self, dc, graphics):
		if self._legendEnabled is not True:
			legendBoxWH = symExt = txtExt = (0, 0)
		else:
			symExt = graphics.getSymExtent(self.printerScale)
			dc.SetFont(self._getFont(self._fontSizeLegend))
			txtList = graphics.getLegendNames()
			txtExt = dc.GetTextExtent(txtList[0])
			for txt in graphics.getLegendNames()[1:]:
				txtExt = np.maximum(txtExt, dc.GetTextExtent(txt))
			maxW = symExt[0] + txtExt[0]
			maxH = max(symExt[1], txtExt[1])
			maxW = maxW * 1.1
			maxH = maxH * 1.1 * len(txtList)
			dc.SetFont(self._getFont(self._fontSizeAxis))
			legendBoxWH = (maxW, maxH)
		return (legendBoxWH, symExt, txtExt)
	def _drawRubberBand(self, corner1, corner2):
		ptx, pty, rectWidth, rectHeight = self._point2ClientCoord(
			corner1, corner2)
		dc = wx.ClientDC(self.canvas)
		dc.SetPen(wx.Pen(wx.BLACK))
		dc.SetBrush(wx.Brush(wx.WHITE, wx.BRUSHSTYLE_TRANSPARENT))
		dc.SetLogicalFunction(wx.INVERT)
		dc.DrawRectangle(ptx, pty, rectWidth, rectHeight)
		dc.SetLogicalFunction(wx.COPY)
	def _getFont(self, size):
		s = size * self.printerScale * self._fontScale
		of = self.GetFont()
		key = (int(s), of.GetFamily(), of.GetStyle(), of.GetWeight())
		font = self._fontCache.get(key, None)
		if font:
			return font
		else:
			font = wx.Font(
				int(s), of.GetFamily(), of.GetStyle(), of.GetWeight())
			self._fontCache[key] = font
			return font
	def _point2ClientCoord(self, corner1, corner2):
		c1 = np.array(corner1)
		c2 = np.array(corner2)
		pt1 = c1 * self._pointScale + self._pointShift
		pt2 = c2 * self._pointScale + self._pointShift
		pul = np.minimum(pt1, pt2)
		plr = np.maximum(pt1, pt2)
		rectWidth, rectHeight = plr - pul
		ptx, pty = pul
		return ptx, pty, rectWidth, rectHeight
	def _axisInterval(self, spec, lower, upper):
		if spec == 'none' or spec == 'min' or isinstance(spec, (float, int)):
			if lower == upper:
				return lower - 0.5, upper + 0.5
			else:
				return lower, upper
		elif spec == 'auto':
			range = upper - lower
			if range == 0.:
				return lower - 0.5, upper + 0.5
			log = np.log10(range)
			power = np.floor(log)
			fraction = log - power
			if fraction <= 0.05:
				power = power - 1
			grid = 10. ** power
			lower = lower - lower % grid
			mod = upper % grid
			if mod != 0:
				upper = upper - mod + grid
			return lower, upper
		elif isinstance(spec, tuple):
			lower, upper = spec
			if lower <= upper:
				return lower, upper
			else:
				return upper, lower
		else:
			raise ValueError(str(spec) + ': illegal axis specification')
	@TempStyle('pen')
	def _drawGrid(self, dc, p1, p2, scale, shift, xticks, yticks):
		pen = self.gridPen
		penWidth = self.printerScale * pen.GetWidth()
		pen.SetWidth(penWidth)
		dc.SetPen(pen)
		x, y, width, height = self._point2ClientCoord(p1, p2)
		if self._xSpec != 'none':
			if self.enableGrid[0]:
				for x, _ in xticks:
					pt = scale_and_shift_point(x, p1[1], scale, shift)
					dc.DrawLine(pt[0], pt[1], pt[0], pt[1] - height)
		if self._ySpec != 'none':
			if self.enableGrid[1]:
				for y, label in yticks:
					pt = scale_and_shift_point(p1[0], y, scale, shift)
					dc.DrawLine(pt[0], pt[1], pt[0] + width, pt[1])
	@TempStyle('pen')
	def _drawTicks(self, dc, p1, p2, scale, shift, xticks, yticks):
		pen = self.tickPen
		penWidth = self.printerScale * pen.GetWidth()
		pen.SetWidth(penWidth)
		dc.SetPen(pen)
		xTickLength = self.tickLengthPrinterScale[0]
		yTickLength = self.tickLengthPrinterScale[1]
		ticks = self.enableTicks
		if self.xSpec != 'none':
			if ticks.bottom:
				lines = []
				for x, label in xticks:
					pt = scale_and_shift_point(x, p1[1], scale, shift)
					lines.append((pt[0], pt[1], pt[0], pt[1] - xTickLength))
				dc.DrawLineList(lines)
			if ticks.top:
				lines = []
				for x, label in xticks:
					pt = scale_and_shift_point(x, p2[1], scale, shift)
					lines.append((pt[0], pt[1], pt[0], pt[1] + xTickLength))
				dc.DrawLineList(lines)
		if self.ySpec != 'none':
			if ticks.left:
				lines = []
				for y, label in yticks:
					pt = scale_and_shift_point(p1[0], y, scale, shift)
					lines.append((pt[0], pt[1], pt[0] + yTickLength, pt[1]))
				dc.DrawLineList(lines)
			if ticks.right:
				lines = []
				for y, label in yticks:
					pt = scale_and_shift_point(p2[0], y, scale, shift)
					lines.append((pt[0], pt[1], pt[0] - yTickLength, pt[1]))
				dc.DrawLineList(lines)
	@TempStyle('pen')
	def _drawCenterLines(self, dc, p1, p2, scale, shift):
		pen = self.centerLinePen
		penWidth = self.printerScale * pen.GetWidth()
		pen.SetWidth(penWidth)
		dc.SetPen(pen)
		if self._centerLinesEnabled in ('Horizontal', True):
			y1 = scale[1] * p1[1] + shift[1]
			y2 = scale[1] * p2[1] + shift[1]
			y = (y1 - y2) / 2.0 + y2
			dc.DrawLine(scale[0] * p1[0] + shift[0],
						y,
						scale[0] * p2[0] + shift[0],
						y)
		if self._centerLinesEnabled in ('Vertical', True):
			x1 = scale[0] * p1[0] + shift[0]
			x2 = scale[0] * p2[0] + shift[0]
			x = (x1 - x2) / 2.0 + x2
			dc.DrawLine(x,
						scale[1] * p1[1] + shift[1],
						x,
						scale[1] * p2[1] + shift[1])
	@TempStyle('pen')
	def _drawDiagonals(self, dc, p1, p2, scale, shift):
		pen = self.diagonalPen
		penWidth = self.printerScale * pen.GetWidth()
		pen.SetWidth(penWidth)
		dc.SetPen(pen)
		if self._diagonalsEnabled in ('Bottomleft-Topright', True):
			dc.DrawLine(scale[0] * p1[0] + shift[0],
						scale[1] * p1[1] + shift[1],
						scale[0] * p2[0] + shift[0],
						scale[1] * p2[1] + shift[1])
		if self._diagonalsEnabled in ('Bottomright-Topleft', True):
			dc.DrawLine(scale[0] * p1[0] + shift[0],
						scale[1] * p2[1] + shift[1],
						scale[0] * p2[0] + shift[0],
						scale[1] * p1[1] + shift[1])
	@TempStyle('pen')
	def _drawAxes(self, dc, p1, p2, scale, shift):
		pen = self.axesPen
		penWidth = self.printerScale * pen.GetWidth()
		pen.SetWidth(penWidth)
		dc.SetPen(pen)
		axes = self.enableAxes
		if self.xSpec != 'none':
			if axes.bottom:
				lower, upper = p1[0], p2[0]
				a1 = scale_and_shift_point(lower, p1[1], scale, shift)
				a2 = scale_and_shift_point(upper, p1[1], scale, shift)
				dc.DrawLine(a1[0], a1[1], a2[0], a2[1])
			if axes.top:
				lower, upper = p1[0], p2[0]
				a1 = scale_and_shift_point(lower, p2[1], scale, shift)
				a2 = scale_and_shift_point(upper, p2[1], scale, shift)
				dc.DrawLine(a1[0], a1[1], a2[0], a2[1])
		if self.ySpec != 'none':
			if axes.left:
				lower, upper = p1[1], p2[1]
				a1 = scale_and_shift_point(p1[0], lower, scale, shift)
				a2 = scale_and_shift_point(p1[0], upper, scale, shift)
				dc.DrawLine(a1[0], a1[1], a2[0], a2[1])
			if axes.right:
				lower, upper = p1[1], p2[1]
				a1 = scale_and_shift_point(p2[0], lower, scale, shift)
				a2 = scale_and_shift_point(p2[0], upper, scale, shift)
				dc.DrawLine(a1[0], a1[1], a2[0], a2[1])
	@TempStyle('pen')
	def _drawAxesValues(self, dc, p1, p2, scale, shift, xticks, yticks):
		xTickLength = self.tickLengthPrinterScale[0]
		yTickLength = self.tickLengthPrinterScale[1]
		xTickLength = xTickLength if xTickLength < 0 else 0
		yTickLength = yTickLength if yTickLength < 0 else 0
		axes = self.enableAxesValues
		if self.xSpec != 'none':
			if axes.bottom:
				labels = [tick[1] for tick in xticks]
				coords = []
				for x, label in xticks:
					w = dc.GetTextExtent(label)[0]
					pt = scale_and_shift_point(x, p1[1], scale, shift)
					coords.append(
						(pt[0] - w/2,
						 pt[1] + 2 * self._pointSize[1] - xTickLength)
					)
				dc.DrawTextList(labels, coords)
			if axes.top:
				labels = [tick[1] for tick in xticks]
				coords = []
				for x, label in xticks:
					w, h = dc.GetTextExtent(label)
					pt = scale_and_shift_point(x, p2[1], scale, shift)
					coords.append(
						(pt[0] - w/2,
						 pt[1] - 2 * self._pointSize[1] - h - xTickLength)
					)
				dc.DrawTextList(labels, coords)
		if self.ySpec != 'none':
			if axes.left:
				h = dc.GetCharHeight()
				labels = [tick[1] for tick in yticks]
				coords = []
				for y, label in yticks:
					w = dc.GetTextExtent(label)[0]
					pt = scale_and_shift_point(p1[0], y, scale, shift)
					coords.append(
						(pt[0] - w - 3 * self._pointSize[0] + yTickLength,
						 pt[1] - 0.5 * h)
					)
				dc.DrawTextList(labels, coords)
			if axes.right:
				h = dc.GetCharHeight()
				labels = [tick[1] for tick in yticks]
				coords = []
				for y, label in yticks:
					w = dc.GetTextExtent(label)[0]
					pt = scale_and_shift_point(p2[0], y, scale, shift)
					coords.append(
						(pt[0] + 3 * self._pointSize[0] + yTickLength,
						 pt[1] - 0.5 * h)
					)
				dc.DrawTextList(labels, coords)
	@TempStyle('pen')
	def _drawPlotAreaItems(self, dc, p1, p2, scale, shift, xticks, yticks):
		if self._gridEnabled:
			self._drawGrid(dc, p1, p2, scale, shift, xticks, yticks)
		if self._ticksEnabled:
			self._drawTicks(dc, p1, p2, scale, shift, xticks, yticks)
		if self._centerLinesEnabled:
			self._drawCenterLines(dc, p1, p2, scale, shift)
		if self._diagonalsEnabled:
			self._drawDiagonals(dc, p1, p2, scale, shift)
		if self._axesEnabled:
			self._drawAxes(dc, p1, p2, scale, shift)
		if self._axesValuesEnabled:
			self._drawAxesValues(dc, p1, p2, scale, shift, xticks, yticks)
	@TempStyle('pen')
	def _drawPlotTitle(self, dc, graphics, lhsW, rhsW, titleWH):
		dc.SetFont(self._getFont(self._fontSizeTitle))
		titlePos = (
			self.plotbox_origin[0] + lhsW
			+ (self.plotbox_size[0] - lhsW - rhsW) / 2. - titleWH[0] / 2.,
			self.plotbox_origin[1] - self.plotbox_size[1]
		)
		dc.DrawText(graphics.title, titlePos[0], titlePos[1])
	def _drawAxesLabels(self, dc, graphics, lhsW, rhsW, bottomH, topH,
						xLabelWH, yLabelWH):
		xTickLength = self.tickLengthPrinterScale[0]
		yTickLength = self.tickLengthPrinterScale[1]
		xTickLength = xTickLength if xTickLength < 0 else 0
		yTickLength = yTickLength if yTickLength < 0 else 0
		dc.SetFont(self._getFont(self._fontSizeAxis))
		xLabelPos = (
			self.plotbox_origin[0] + lhsW
			+ (self.plotbox_size[0] - lhsW - rhsW) / 2. - xLabelWH[0] / 2.,
			self.plotbox_origin[1] - xLabelWH[1] - yTickLength
		)
		dc.DrawText(graphics.xLabel, xLabelPos[0], xLabelPos[1])
		yLabelPos = (
			self.plotbox_origin[0] - 3 * self._pointSize[0] + xTickLength,
			self.plotbox_origin[1] - bottomH
			- (self.plotbox_size[1] - bottomH - topH) / 2. + yLabelWH[0] / 2.
		)
		if graphics.yLabel:
			dc.DrawRotatedText(
				graphics.yLabel, yLabelPos[0], yLabelPos[1], 90)
	@TempStyle('pen')
	def _drawPlotAreaLabels(self, dc, graphics, lhsW, rhsW, titleWH,
							bottomH, topH, xLabelWH, yLabelWH):
		if self._titleEnabled:
			self._drawPlotTitle(dc, graphics, lhsW, rhsW, titleWH)
		if self._axesLabelsEnabled:
			self._drawAxesLabels(dc, graphics, lhsW, rhsW,
								 bottomH, topH, xLabelWH, yLabelWH)
	def _xticks(self, *args):
		if self._logscale[0]:
			return self._logticks(*args)
		else:
			attr = {'numticks': self._xSpec}
			return self._ticks(*args, **attr)
	def _yticks(self, *args):
		if self._logscale[1]:
			return self._logticks(*args)
		else:
			attr = {'numticks': self._ySpec}
			return self._ticks(*args, **attr)
	def _logticks(self, lower, upper):
		ticks = []
		mag = np.power(10, np.floor(lower))
		if upper - lower > 6:
			t = np.power(10, np.ceil(lower))
			base = np.power(10, np.floor((upper - lower) / 6))
			def inc(t):
				return t * base - t
		else:
			t = np.ceil(np.power(10, lower) / mag) * mag
			def inc(t):
				return 10 ** int(np.floor(np.log10(t) + 1e-16))
		majortick = int(np.log10(mag))
		while t <= pow(10, upper):
			if majortick != int(np.floor(np.log10(t) + 1e-16)):
				majortick = int(np.floor(np.log10(t) + 1e-16))
				ticklabel = '1e%d' % majortick
			else:
				if upper - lower < 2:
					minortick = int(t / pow(10, majortick) + .5)
					ticklabel = '%de%d' % (minortick, majortick)
				else:
					ticklabel = ''
			ticks.append((np.log10(t), ticklabel))
			t += inc(t)
		if len(ticks) == 0:
			ticks = [(0, '')]
		return ticks
	def _ticks(self, lower, upper, numticks=None):
		if isinstance(numticks, (float, int)):
			ideal = (upper - lower) / float(numticks)
		else:
			ideal = (upper - lower) / 7.
		log = np.log10(ideal)
		power = np.floor(log)
		if isinstance(numticks, (float, int)):
			grid = ideal
		else:
			fraction = log - power
			factor = 1.
			error = fraction
			for f, lf in self._multiples:
				e = np.fabs(fraction - lf)
				if e < error:
					error = e
					factor = f
			grid = factor * 10. ** power
		if self._useScientificNotation and (power > 4 or power < -4):
			format = '%+7.1e'
		elif power >= 0:
			digits = max(1, int(power))
			format = '%' + repr(digits) + '.0f'
		else:
			digits = -int(power)
			format = '%' + repr(digits + 2) + '.' + repr(digits) + 'f'
		ticks = []
		t = -grid * np.floor(-lower / grid)
		while t <= upper:
			if t == -0:
				t = 0
			ticks.append((t, format % (t,)))
			t = t + grid
		return ticks
	_multiples = [(2., np.log10(2.)), (5., np.log10(5.))]
	def _adjustScrollbars(self):
		if self._sb_ignore:
			self._sb_ignore = False
			return
		if not self.showScrollbars:
			return
		self._adjustingSB = True
		needScrollbars = False
		r_current = self._getXCurrentRange()
		r_max = list(self._getXMaxRange())
		sbfullrange = float(self.sb_hor.GetRange())
		r_max[0] = min(r_max[0], r_current[0])
		r_max[1] = max(r_max[1], r_current[1])
		self._sb_xfullrange = r_max
		unit = (r_max[1] - r_max[0]) / float(self.sb_hor.GetRange())
		pos = int((r_current[0] - r_max[0]) / unit)
		if pos >= 0:
			pagesize = int((r_current[1] - r_current[0]) / unit)
			self.sb_hor.SetScrollbar(pos, pagesize, sbfullrange, pagesize)
			self._sb_xunit = unit
			needScrollbars = needScrollbars or (pagesize != sbfullrange)
		else:
			self.sb_hor.SetScrollbar(0, 1000, 1000, 1000)
		r_current = self._getYCurrentRange()
		r_max = list(self._getYMaxRange())
		sbfullrange = float(self.sb_vert.GetRange())
		r_max[0] = min(r_max[0], r_current[0])
		r_max[1] = max(r_max[1], r_current[1])
		self._sb_yfullrange = r_max
		unit = (r_max[1] - r_max[0]) / sbfullrange
		pos = int((r_current[0] - r_max[0]) / unit)
		if pos >= 0:
			pagesize = int((r_current[1] - r_current[0]) / unit)
			pos = (sbfullrange - 1 - pos - pagesize)
			self.sb_vert.SetScrollbar(pos, pagesize, sbfullrange, pagesize)
			self._sb_yunit = unit
			needScrollbars = needScrollbars or (pagesize != sbfullrange)
		else:
			self.sb_vert.SetScrollbar(0, 1000, 1000, 1000)
		self.sb_hor.Show(needScrollbars)
		self.sb_vert.Show(needScrollbars)
		self._adjustingSB = False
