""" DoCubesatViewer """

from .Cubesat import CubesatViewer

class DoCubesatViewer:
	""" DoCubesatViewer """

	def __init__(self, u=3, label=None, w=300, h=200):
		""" DoCubesatViewer """
		# build a 3D cubesat model
		# cubesat_model = Cubesat(u=u, width=w, height=h)
		# build the viewer for the cubesat 3D model
		# cls._cv = CubesatViewer(image_canvas=sat_label, cubesat=cubesat_model, width=w, height=h)
		self._cv = CubesatViewer(u=u, image_canvas=label, width=w, height=h, show_axes=True)

	def update_orientation(self, pitch=0.0, roll=0.0, yaw=0.0):
		""" update_orientation """
		# XXX TODO roll, pitch, yaw are swapped because camera is on Y axiz (should be programatic)
		# self._cv.update_orientation(roll=pitch, pitch=roll, yaw=yaw)
		self._cv.update_orientation(roll=roll, pitch=pitch, yaw=yaw)
