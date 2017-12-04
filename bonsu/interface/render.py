###################################################
## Filename: render.py
##
## Modified version of wxVTKRenderWindowInteractor.py, written by
## Prabhu Ramachandran, April 2002, Charl P. Botha 2003-2008,
## Andrea Gavana December 2006.
##
## Marcus C. Newton 2011
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
import math, os, sys
import wx
import vtk
from .common import IsNotWX4
baseClass = wx.Window
if wx.Platform == "__WXGTK__":
	import wx.glcanvas
	baseClass = wx.glcanvas.GLCanvas
_useCapture = (wx.Platform == "__WXMSW__")
class EventTimer(wx.Timer):
	def __init__(self, iren):
		wx.Timer.__init__(self)
		self.iren = iren
	def Notify(self):
		self.iren.TimerEvent()
class wxVTKRenderWindowInteractor(baseClass):
	USE_STEREO = False
	def __init__(self, parent, ID, *args, **kw):
		self.__RenderWhenDisabled = 0
		stereo = 0
		if 'stereo' in kw:
			if kw['stereo']:
				stereo = 1
			del kw['stereo']
		elif self.USE_STEREO:
			stereo = 1
		position, size = wx.DefaultPosition, wx.DefaultSize
		if 'position' in kw:
			position = kw['position']
			del kw['position']
		if 'size' in kw:
			size = kw['size']
			del kw['size']
		style = wx.WANTS_CHARS | wx.NO_FULL_REPAINT_ON_RESIZE
		if 'style' in kw:
			style = style | kw['style']
			del kw['style']
		if wx.Platform != '__WXMSW__':
			l = []
			p = parent
			while p:
				l.append(p)
				p = p.GetParent()
			l.reverse()
			for p in l:
				p.Show(1)
		if baseClass.__name__ == 'GLCanvas':
			attribList = [wx.glcanvas.WX_GL_RGBA,
				wx.glcanvas.WX_GL_MIN_RED, 1,
				wx.glcanvas.WX_GL_MIN_GREEN, 1,
				wx.glcanvas.WX_GL_MIN_BLUE, 1,
				wx.glcanvas.WX_GL_DEPTH_SIZE, 16,
				wx.glcanvas.WX_GL_DOUBLEBUFFER]
			if stereo:
				attribList.append(wx.glcanvas.WX_GL_STEREO)
			try:
				baseClass.__init__(self, parent, ID, pos=position, size=size, style=style, attribList=attribList)
			except wx.PyAssertionError:
				baseClass.__init__(self, parent, ID, pos=position, size=size, style=style)
				if stereo:
					stereo = 0
		else:
			baseClass.__init__(self, parent, ID, position, size, style)
		self._Iren = vtk.vtkGenericRenderWindowInteractor()
		self._Iren.SetRenderWindow( vtk.vtkRenderWindow() )
		self._Iren.AddObserver('CreateTimerEvent', self.CreateTimer)
		self._Iren.AddObserver('DestroyTimerEvent', self.DestroyTimer)
		self._Iren.GetRenderWindow().AddObserver('CursorChangedEvent', self.CursorChangedEvent)
		try:
			self._Iren.GetRenderWindow().SetSize(size.width, size.height)
		except AttributeError:
			self._Iren.GetRenderWindow().SetSize(size[0], size[1])
		if stereo:
			self._Iren.GetRenderWindow().StereoCapableWindowOn()
			self._Iren.GetRenderWindow().SetStereoTypeToCrystalEyes()
		self.__handle = None
		self.mouse_zone = False
		self.left_mouse_down = False
		self.mousex = 0
		self.mousey = 0
		self.BindEvents()
		self.__has_painted = False
		self._own_mouse = False
		self._mouse_capture_button = 0
		self._cursor_map = {0: wx.CURSOR_ARROW,
							1: wx.CURSOR_ARROW,
							2: wx.CURSOR_SIZENESW,
							3: wx.CURSOR_SIZENWSE,
							4: wx.CURSOR_SIZENESW,
							5: wx.CURSOR_SIZENWSE,
							6: wx.CURSOR_SIZENS,
							7: wx.CURSOR_SIZEWE,
							8: wx.CURSOR_SIZING,
							9: wx.CURSOR_HAND,
							10: wx.CURSOR_CROSS,
							}
	def BindEvents(self):
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)
		self.Bind(wx.EVT_RIGHT_DOWN, self.OnButtonDown)
		self.Bind(wx.EVT_LEFT_DOWN, self.OnButtonDown)
		self.Bind(wx.EVT_MIDDLE_DOWN, self.OnButtonDown)
		self.Bind(wx.EVT_RIGHT_UP, self.OnButtonUp)
		self.Bind(wx.EVT_LEFT_UP, self.OnButtonUp)
		self.Bind(wx.EVT_MIDDLE_UP, self.OnButtonUp)
		self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
		self.Bind(wx.EVT_MOTION, self.OnMotion)
		self.Bind(wx.EVT_ENTER_WINDOW, self.OnEnter)
		self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeave)
		self.Bind(wx.EVT_CHAR, self.OnKeyDown)
		self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
		if wx.Platform == "__WXGTK__":
			# wxGTK requires that the window be created before you can
			# set its shape, so delay the call to SetWindowShape until
			# this event.
			self.Bind(wx.EVT_WINDOW_CREATE, self.OnWindowCreate)
		else:
			# On wxMSW and wxMac the window has already been created.
			self.Bind(wx.EVT_SIZE, self.OnSize)
		if _useCapture and hasattr(wx, 'EVT_MOUSE_CAPTURE_LOST'):
			self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.OnMouseCaptureLost)
	def __getattr__(self, attr):
		if attr == '__vtk__':
			return lambda t=self._Iren: t
		elif hasattr(self._Iren, attr):
			return getattr(self._Iren, attr)
		else:
			raise AttributeError(self.__class__.__name__ + " has no attribute named " + attr)
	def CreateTimer(self, obj, evt):
		self._timer = EventTimer(self)
		self._timer.Start(10, True)
	def DestroyTimer(self, obj, evt):
		return 1
	def _CursorChangedEvent(self, obj, evt):
		cur = self._cursor_map[obj.GetCurrentCursor()]
		if IsNotWX4():
			c = wx.StockCursor(cur)
		else:
			c = wx.Cursor(cur)
		self.SetCursor(c)
	def CursorChangedEvent(self, obj, evt):
		wx.CallAfter(self._CursorChangedEvent, obj, evt)
	def HideCursor(self):
		if IsNotWX4():
			c = wx.StockCursor(wx.CURSOR_BLANK)
		else:
			c = wx.Cursor(wx.CURSOR_BLANK)
		self.SetCursor(c)
	def ShowCursor(self):
		rw = self._Iren.GetRenderWindow()
		cur = self._cursor_map[rw.GetCurrentCursor()]
		if IsNotWX4():
			c = wx.StockCursor(cur)
		else:
			c = wx.Cursor(cur)
		self.SetCursor(c)
	def GetDisplayId(self):
		d = None
		try:
			d = wx.GetXDisplay()
		except NameError:
			pass
		else:
			if d:
				d = hex(d)
				if not d.startswith('0x'):
					d = '0x' + d
				d = '_%s_%s\0' % (d[2:], 'p_void')
		return d
	def OnMouseCaptureLost(self, event):
		if _useCapture and self._own_mouse:
			self._own_mouse = False
	def OnMouseZone(self, obj):
		self.mouse_zone = obj
	def OnPaint(self,event):
		event.Skip()
		dc = wx.PaintDC(self)
		if IsNotWX4():
			self._Iren.GetRenderWindow().SetSize(self.GetSizeTuple())
		else:
			self._Iren.GetRenderWindow().SetSize(self.GetSize())
		if not self.__handle:
			self.__handle = self.GetHandle()
			self._Iren.GetRenderWindow().SetWindowInfo(str(self.__handle))
			self.__has_painted = True
		self.Render()
	def OnWindowCreate(self,event):
		event.Skip
		if IsNotWX4():
			width,height = self.GetSizeTuple()
		else:
			width,height = self.GetSize()
		self._Iren.SetSize(width, height)
		self._Iren.ConfigureEvent()
		self.Render()
	def OnSize(self,event):
		event.Skip()
		try:
			width, height = event.GetSize()
		except:
			width = event.GetSize().width
			height = event.GetSize().height
		self._Iren.SetSize(width, height)
		self._Iren.ConfigureEvent()
		self.Render()
	def OnMotion(self,event):
		event.Skip()
		self._Iren.SetEventInformationFlipY(event.GetX(), event.GetY(),
			event.ControlDown(), event.ShiftDown(), chr(0), 0, None)
		self._Iren.MouseMoveEvent()
	def OnEnter(self,event):
		event.Skip()
		self._Iren.SetEventInformationFlipY(event.GetX(), event.GetY(),
			event.ControlDown(), event.ShiftDown(), chr(0), 0, None)
		self._Iren.EnterEvent()
	def OnLeave(self,event):
		event.Skip()
		self._Iren.SetEventInformationFlipY(event.GetX(), event.GetY(),
			event.ControlDown(), event.ShiftDown(), chr(0), 0, None)
		self._Iren.LeaveEvent()
	def OnButtonDown(self,event):
		if self.mouse_zone and event.LeftDown():
			self.left_mouse_down = True
			return
		event.Skip()
		ctrl, shift = event.ControlDown(), event.ShiftDown()
		self._Iren.SetEventInformationFlipY(event.GetX(), event.GetY(),
			ctrl, shift, chr(0), 0, None)
		button = 0
		if event.RightDown():
			self._Iren.RightButtonPressEvent()
			button = 'Right'
		elif event.LeftDown():
			self._Iren.LeftButtonPressEvent()
			button = 'Left'
		elif event.MiddleDown():
			self._Iren.MiddleButtonPressEvent()
			button = 'Middle'
		if _useCapture and not self._own_mouse:
			self._own_mouse = True
			self._mouse_capture_button = button
			self.CaptureMouse()
	def OnButtonUp(self,event):
		event.Skip()
		button = 0
		if event.RightUp():
			button = 'Right'
		elif event.LeftUp():
			button = 'Left'
			self.left_mouse_down = False
		elif event.MiddleUp():
			button = 'Middle'
		if _useCapture and self._own_mouse and button==self._mouse_capture_button:
			self.ReleaseMouse()
			self._own_mouse = False
		ctrl, shift = event.ControlDown(), event.ShiftDown()
		self._Iren.SetEventInformationFlipY(event.GetX(), event.GetY(),
			ctrl, shift, chr(0), 0, None)
		if button == 'Right':
			self._Iren.RightButtonReleaseEvent()
		elif button == 'Left':
			self._Iren.LeftButtonReleaseEvent()
		elif button == 'Middle':
			self._Iren.MiddleButtonReleaseEvent()
	def OnMouseWheel(self,event):
		event.Skip()
		ctrl, shift = event.ControlDown(), event.ShiftDown()
		self._Iren.SetEventInformationFlipY(event.GetX(), event.GetY(),
			ctrl, shift, chr(0), 0, None)
		if event.GetWheelRotation() > 0:
			self._Iren.MouseWheelForwardEvent()
		else:
			self._Iren.MouseWheelBackwardEvent()
	def OnKeyDown(self,event):
		event.Skip()
		ctrl, shift = event.ControlDown(), event.ShiftDown()
		keycode, keysym = event.GetKeyCode(), None
		key = chr(0)
		if keycode < 256:
			key = chr(keycode)
		(x,y)= self._Iren.GetEventPosition()
		self._Iren.SetEventInformation(x, y,
			ctrl, shift, key, 0, keysym)
		self._Iren.KeyPressEvent()
		self._Iren.CharEvent()
	def OnKeyUp(self,event):
		event.Skip()
		ctrl, shift = event.ControlDown(), event.ShiftDown()
		keycode, keysym = event.GetKeyCode(), None
		key = chr(0)
		if keycode < 256:
			key = chr(keycode)
		self._Iren.SetEventInformationFlipY(event.GetX(), event.GetY(),
			ctrl, shift, key, 0, keysym)
		self._Iren.KeyReleaseEvent()
	def GetRenderWindow(self):
		return self._Iren.GetRenderWindow()
	def SetPicker(self, picker):
		self._Iren.SetPicker(picker)
	def Render(self):
		RenderAllowed = 1
		if not self.__RenderWhenDisabled:
			topParent = wx.GetTopLevelParent(self)
			if topParent:
				RenderAllowed = topParent.IsEnabled()
		if RenderAllowed:
			if self.__handle and self.__handle == self.GetHandle():
				self._Iren.GetRenderWindow().Render()
			elif self.GetHandle() and self.__has_painted:
				self._Iren.GetRenderWindow().SetNextWindowInfo(
					str(self.GetHandle()))
				d = self.GetDisplayId()
				if d:
					self._Iren.GetRenderWindow().SetDisplayId(d)
				self._Iren.GetRenderWindow().WindowRemap()
				self.__handle = self.GetHandle()
				self._Iren.GetRenderWindow().Render()
	def SetRenderWhenDisabled(self, newValue):
		self.__RenderWhenDisabled = bool(newValue)
