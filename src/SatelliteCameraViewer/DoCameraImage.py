""" DoCameraImage """

from .misc import mag_map

from .CameraImage import CameraImage

class DoCameraImage:
	""" DoCameraImage """

	def __init__(self, label=None, nx:int=400, ny:int=300, w:int=400, h:int=300):
		""" DoCameraImage """
		if label is None:
			raise ValueError('DoCameraImage() needs label value') from None
		self._label = label
		# camera sensor ...
		self.nx = nx
		self.ny = ny
		# painting area in ui ...
		self.w = w
		self.h = h
		# scaling factors ...
		self.scale_x = float(self.nx)/float(self.w)
		self.scale_y = float(self.ny)/float(self.h)
		# get camera image ready
		self._ci = CameraImage(self.w, self.h)
		self.reset()

	def reset(self):
		""" reset """
		self.stars()

	def resize(self, nx:int=400, ny:int=300):
		""" resize - simply rescale the view and clear all the displayed info """
		# camera sensor ...
		self.nx = nx
		self.ny = ny
		# scaling factors ...
		self.scale_x = float(self.nx)/float(self.w)
		self.scale_y = float(self.ny)/float(self.h)
		self.reset()

	def stars(self, xy_list=None, mag_list=None):
		""" stars """
		if self._label is None or self._ci is None:
			raise ValueError('DoCameraImage() needs register first') from None
		self._ci.clear(color=(0,0,0))
		# self.outline()
		if xy_list is not None:
			ii = 0
			for x1,y1 in xy_list:
				x = ((self.nx-1) - x1)/self.scale_x
				y = ((self.ny-1) - y1)/self.scale_y
				mag = mag_list[ii]
				diameter = mag_map(mag, multiplier=4.0) / self.scale_x
				self._ci.circle((x,y), radius=diameter/2, color=(255,255,255))
				ii += 1
		self._ci.paint(self._label)

	def outline(self):
		""" outline """
		# red outline
		self._ci.line((       0,        0), (       0, self.h-1), color=(255,0,0))
		self._ci.line((       0, self.h-1), (self.w-1, self.h-1), color=(255,0,0))
		self._ci.line((self.w-1, self.h-1), (self.w-1,        0), color=(255,0,0))
		self._ci.line((self.w-1,        0), (       0,        0), color=(255,0,0))
		# crosshairs
		self._ci.line((       0,        0), (self.w-1, self.h-1), color=(255,0,0))
		self._ci.line((self.w-1,        0), (       0, self.h-1), color=(255,0,0))
		# optional circle in center
		self._ci.circle((self.w/2, self.h/2), 10, color=(255,0,0))
