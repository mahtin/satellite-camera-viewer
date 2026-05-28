""" NikonD5Camera """

from .SatelliteCamera import SatelliteCamera
from .static_tles import static_tles

class NikonD5Camera:
	""" NikonD5Camera """

	def __init__(self, tle=None, focal_length:float=50.0):
		self._obs_time = None
		self._attitude = None

		# Example distortion (small or none actually)
		self._bcc = SatelliteCamera.BrownConradyCoeffs(k1=0.0, k2=0.0, p1=0.0, p2=0.0, k3=0.0)

		# The Nikon D5 features a 20.8-megapixel full-frame (FX-format) CMOS sensor, measuring approximately 35.9 x 23.9 mm.
		# This high-performance sensor is designed for professional photography,
		# offering a maximum resolution of 5568 x 3712 pixels and a native ISO range up to 102,400

		# Define camera
		self._sc = SatelliteCamera(
			focal_length_mm=focal_length,
			sensor_size_x_mm = 35.9, sensor_size_y_mm = 23.9,
			nx=5568, ny=3712,
			bcc=self._bcc
		)

		if tle is None:
			# Define satellite orbit from TLE from a static set
			tle = static_tles[0].as_array

		# map SatelliteCamera() into this class (yes - there's a more pythonic way to do this)

		self.now                        = self._sc.now
		self.datetime                   = self._sc.datetime

		self.adjust_by_seconds          = self._sc.adjust_by_seconds
		self.choose_attitude            = self._sc.choose_attitude
		self.pixel_to_radec             = self._sc.pixel_to_radec
		self.sensor_to_radec            = self._sc.sensor_to_radec
		self.radec_to_pixel             = self._sc.radec_to_pixel

		self.lon_lat_alt                = self._sc.lon_lat_alt

		self.earth_center_vector        = self._sc.earth_center_vector
		self.earth_center_vector_icrs   = self._sc.earth_center_vector_icrs
		self.earth_center_radec_simple  = self._sc.earth_center_radec_simple
		self.earth_center_radec         = self._sc.earth_center_radec
		self.earth_angular_radius       = self._sc.earth_angular_radius
		self.camera_fov_intercept_earth = self._sc.camera_fov_intercept_earth

		# set everything up
		self.tle = tle
		self.now()
		self.choose_attitude('vv')

	@property
	def obs_time(self):
		""" obs_time """
		return self._sc.obs_time

	@property
	def camera(self):
		""" camera """
		return self._sc

	@property
	def tle(self):
		""" tle """
		return self._sc.tle

	@tle.setter
	def tle(self, value=None):
		""" tle """
		self._sc.tle = value

	def find_tle(self, satellite_name):
		""" find_tle """
		ii = 0
		for t in static_tles:
			if satellite_name == t.name:
				break
			ii += 1
		if ii >= len(static_tles):
			raise ValueError('%s not in satellites list' % (satellite_name))
		self.tle = static_tles[ii].as_array

	def camera_fov_radec_box(self):
		""" camera_fov_radec_box """
		self._box = self._sc.camera_fov_radec_box()
		ra_deg = [float(v) for v in self._box['polygon'].ra.value.tolist()]
		dec_deg = [float(v) for v in self._box['polygon'].dec.value.tolist()]
		return self._box, [ra_deg, dec_deg]

	def camera_fov_angular_width_height(self):
		""" camera_fov_angular_width_height """
		self._angular_width, self._angular_height = self._sc.camera_fov_angular_width_height()
		self._solid_angle_steradians = self._sc.camera_fov_solid_angle()
		return self._angular_width.degree, self._angular_height.degree, self._solid_angle_steradians

	def camera_fov_convex_hull(self):
		""" camera_fov_convex_hull """
		hull_coords, _ = self._sc.camera_fov_convex_hull(border_step=100)
		return [[v.ra.degree for v in hull_coords], [v.dec.degree for v in hull_coords]]

	def camera_fov_border_vectors(self, border_step:int):
		""" camera_fov_border_vectors """
		polygon = self._sc.camera_fov_border_vectors(border_step=border_step)
		return [(float(v.ra.value), float(v.dec.value)) for v in polygon]
