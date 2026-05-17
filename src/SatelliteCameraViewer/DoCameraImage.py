""" DoCameraImage """

from .misc import mag_map

from .CameraImage import CameraImage

class DoCameraImage:
	""" DoCameraImage """

	def __init__(cls, label=None, nx:int=400, ny:int=300, w:int=400, h:int=300):
		""" DoCameraImage """
		if label is None:
			raise ValueError('DoCameraImage() needs label value')
		cls._label = label
		cls.nx = nx
		cls.ny = ny
		cls.w = w
		cls.h = h
		cls.scale_x = float(cls.nx)/float(cls.w)
		cls.scale_y = float(cls.ny)/float(cls.h)
		# get camera image ready
		cls._ci = CameraImage(cls.w, cls.h)
		cls.reset()

	def reset(cls):
		""" reset """
		cls.stars()

	def stars(cls, xy_list=None, mag_list=None):
		""" stars """
		if cls._label is None or cls._ci is None:
			raise ValueError('DoCameraImage() needs register first')
		cls._ci.clear(color=(0,0,0))
		# cls.outline()
		if xy_list is not None:
			ii = 0
			for x1,y1 in xy_list:
				x = ((cls.nx-1) - x1)/cls.scale_x
				y = ((cls.ny-1) - y1)/cls.scale_y
				mag = mag_list[ii]
				diameter = mag_map(mag, multiplier=4.0) / cls.scale_x
				cls._ci.circle((x,y), radius=diameter/2, color=(255,255,255))
				# print('\tcamera=[%4d,%4d] -> pixel=[%3d,%3d]' % (x1, y1, x, y))
				ii += 1
		cls._ci.paint(cls._label)

	def outline(cls):
		""" outline """
		# red outline
		cls._ci.line((      0,       0), (      0, cls.h-1), color=(255,0,0))
		cls._ci.line((      0, cls.h-1), (cls.w-1, cls.h-1), color=(255,0,0))
		cls._ci.line((cls.w-1, cls.h-1), (cls.w-1,       0), color=(255,0,0))
		cls._ci.line((cls.w-1,       0), (      0,       0), color=(255,0,0))
		# crosshairs
		cls._ci.line((      0,       0), (cls.w-1, cls.h-1), color=(255,0,0))
		cls._ci.line((cls.w-1,       0), (      0, cls.h-1), color=(255,0,0))
		# optional circle in center
		cls._ci.circle((cls.w/2, cls.h/2), 10, color=(255,0,0))
