""" CameraSensor.py """

import math
from itertools import count
from dataclasses import dataclass, field

from .BrownConradyCoeffs import BrownConradyCoeffs

_camera_id = count(start=1)

CameraSensors = {}

@dataclass
class CameraSensor:
	""" CameraSensor """
	name : str = field(default_factory=lambda:'Camera%d'%(next(_camera_id)))	# Camera name
	focal_length_mm : int|float					# focal length (mm)
	_focal_length_mm : float = field(init=False, repr=False)	# focal length (mm)
	effective_focal_length_mm : float = None			# effective focal length (mm)
	sensor_size_x_mm : float = None					# sensor width (mm)
	sensor_size_y_mm : float = None					# sensor height (mm)
	nx : int = None							# pixels in x
	ny : int = None							# pixels in y
	cx: float = None						# principal point x (pixels
	cy: float = None						# principal point y (pixels)
	bcc: BrownConradyCoeffs = None					# Brown Conrady Coeffs
	sensor_to_lens_mm: float = None					# distance from sensor to lens principal plane

	def __post_init__(self):
		""" __post_init__ """
		if self.sensor_size_x_mm is None or self.sensor_size_y_mm is None:
			raise ValueError('sensor_size_[xy]_mm cannot be empty')
		if self.nx is None or self.ny is None:
			raise ValueError('n[xy] cannot be empty')

		if self.cx is None:
			self.cx = self.nx / 2.0
		if self.cy is None:
			self.cy = self.ny / 2.0
		if self.bcc is None:
			if 50.0 <= self.focal_length_mm <= 70.0:
				# Found online - but I need a real reference/database
				self.bcc = BrownConradyCoeffs(k1=0.01, k2=0.005, p1=0.0001, p2=-0.0002, k3=0.0)
			else:
				# The default value for Brown-Conrady lens distortion coefficients (k1 ,k2 ,p1 ,p2 ,k3)
				# are typically zero for all parameters, representing an ideal, undistorted lens.
				self.bcc = BrownConradyCoeffs(k1=0.0, k2=0.0, p1=0.0, p2=0.0, k3=0.0)
		self._focal_recaculate()

		# convenience values
		self.sensor_size = [self.sensor_size_x_mm, self.sensor_size_y_mm]
		self.n = [self.nx, self.ny]
		self.c = [self.cx, self.cy]

		self.pixel_size_x_mm = self.sensor_size_x_mm / self.nx
		self.pixel_size_y_mm = self.sensor_size_y_mm / self.ny
		self.aspect_ratio = self.sensor_size_x_mm / self.sensor_size_y_mm

		self.fov_x_deg = 2 * math.degrees(math.atan((self.sensor_size_x_mm / 2) / self.focal_length_mm))
		self.fov_y_deg = 2 * math.degrees(math.atan((self.sensor_size_y_mm / 2) / self.focal_length_mm))

		diag = math.sqrt(self.sensor_size_x_mm**2 + self.sensor_size_y_mm**2)
		self.fov_diag_deg = 2 * math.degrees(math.atan((diag / 2) / self.focal_length_mm))

		# save away for finding globally
		CameraSensors[self.name] = self

	def _focal_recaculate(self):
		""" _focal_recaculate """
		if self.focal_length_mm is None:
			raise ValueError('focal_length_mm cannot be empty')
		if self.effective_focal_length_mm is None:
			# For a pinhole model, focal_length_mm == sensor_to_lens_mm
			# But we keep them separate so real lenses can be modeled.
			self.effective_focal_length_mm = self.focal_length_mm
		if self.sensor_to_lens_mm is None:
			self.sensor_to_lens_mm = self.focal_length_mm

	def __str__(self):
		""" __str__ """
		return '[%dx%d pixels %.1fx%.1f mm @ %.1f mm ; %s]' % (self.nx, self.ny, self.sensor_size_x_mm, self.sensor_size_y_mm, self.focal_length_mm, self.name)

	# The one property that can be changed on the fly is the camera focal length
	# This assumes that functions using this camera sensor class always come back here to read the new focal length
	@property
	def focal_length_mm(self) -> float:
		""" focal_length_mm """
		return self._focal_length_mm

	@focal_length_mm.setter
	def focal_length_mm(self, value:int|float):
		""" focal_length_mm """
		if not value:
			raise ValueError('focal_length_mm cannot be empty')
		try:
			self._focal_length_mm = float(value)
		except TypeError:
			raise ValueError('focal_length_mm cannot be empty')
		self._focal_recaculate()

	def pixel_to_sensor_mm(self, px: float, py: float, use_distortion=False):
		"""
		Convert pixel coordinates to sensor-plane coordinates (mm),
		with origin at principal point.
		"""
		x_mm = (px - self.cx) * self.pixel_size_x_mm
		y_mm = (py - self.cy) * self.pixel_size_y_mm
		if use_distortion:
			x_mm, y_mm = self._apply_distortion(x_mm, y_mm)
		return x_mm, y_mm

	def sensor_mm_to_pixel(self, x_mm: float, y_mm: float):
		"""
		Convert sensor-plane coordinates (mm) coordinates to pixels,
		with origin at principal point.
		"""
		# TODO should handle distortion
		px = self.cx + x_mm / self.pixel_size_x_mm
		py = self.cy + y_mm / self.pixel_size_y_mm
		return px, py

	def _apply_distortion(self, x_mm: float, y_mm: float):
		"""
		Apply radial + tangential distortion to sensor-plane coordinates.
		Model: Brown-Conrady in normalized coordinates.
		"""
		# Normalize by focal length to get dimensionless coords
		x = x_mm / self.effective_focal_length_mm
		y = y_mm / self.effective_focal_length_mm

		r2 = x * x + y * y
		r4 = r2 * r2
		r6 = r4 * r2

		radial = 1 + self.bcc.k1 * r2 + self.bcc.k2 * r4 + self.bcc.k3 * r6
		x_radial = x * radial
		y_radial = y * radial

		x_tangential = 2 * self.bcc.p1 * x * y + self.bcc.p2 * (r2 + 2 * x * x)
		y_tangential = self.bcc.p1 * (r2 + 2 * y * y) + 2 * self.bcc.p2 * x * y

		x_dist = x_radial + x_tangential
		y_dist = y_radial + y_tangential

		# Back to mm
		return x_dist * self.effective_focal_length_mm, y_dist * self.effective_focal_length_mm

#
# Known camera sensors (with default lens)
#

# Nikon D5
# The Nikon D5 features a 20.8-megapixel full-frame (FX-format) CMOS sensor, measuring approximately 35.9 x 23.9 mm.
# This high-performance sensor is designed for professional photography,
# offering a maximum resolution of 5568 x 3712 pixels and a native ISO range up to 102,400
NikonD5 = CameraSensor(
	name = 'Nikon D5',
	focal_length_mm = 50.0,
	sensor_size_x_mm = 35.9,
	sensor_size_y_mm = 23.9,
	nx = 5568,
	ny = 3712,
)

# Nikon Z9
NikonZ9 = CameraSensor(
	name = 'Nikon Z9',
	focal_length_mm = 50.0,
	sensor_size_x_mm = 35.9,
	sensor_size_y_mm = 23.9,
	nx = 8256,
	ny = 5504,
)

# Sony a7S II (ILCE-7SM2)
SonyA75II = CameraSensor(
	name = 'Sony a7S II',
	focal_length_mm = 50.0,
	sensor_size_x_mm = 35.6,
	sensor_size_y_mm = 23.8,
	nx = 4240,
	ny = 2832,
)

# Raspberry Pi High Quality (HQ) Camera (12.3 megapixel Sony IMX477 sensor, 7.9mm diagonal image size)
# 12.3-megapixel Sony IMX477
# https://www.sony-semicon.com/files/62/pdf/p-13_IMX477-AACK_Flyer.pdf
RPiHQCamera = CameraSensor(
	name = 'Raspberry Pi High Quality Camera',
	focal_length_mm = 12.0,
	sensor_size_x_mm = 6.287,
	sensor_size_y_mm = 4.712,
	nx = 4056,
	ny = 3040,
)

# Apple iPad Pro
AppleIPadProRearWide = CameraSensor(
	name = 'iPad Pro Rear Wide',
	focal_length_mm = 3.0,
	effective_focal_length_mm = 28.0,
	sensor_size_x_mm = 5.76,
	sensor_size_y_mm = 4.29,
	nx = 4000,
	ny = 3000,
)

# test camera
TestCamera1024x1024 = CameraSensor(
	focal_length_mm = 50,
	sensor_size_x_mm = 10.0,
	sensor_size_y_mm = 10.0,
	nx = 1024,
	ny = 1024,
)

def _main(args=None):
	""" _main """
	for name, camera in CameraSensors.items():
		print('%-35s: %s' % (name, camera))

if __name__ == '__main__':
	_main()
