""" NikonD5Camera """

from .SatelliteCamera import SatelliteCamera, SatelliteCameraError

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

		# 1. Define camera
		self._sc = SatelliteCamera(
			focal_length_mm=focal_length,
			sensor_size_x_mm = 35.9, sensor_size_y_mm = 23.9,
			nx=5568, ny=3712,
			bcc=self._bcc
		)

		if tle is None:
			# 3. Define satellite orbit from TLE
			geos15_tle = [
				'GOES-15',
				'1 25338U          26100.31887920 +.00000000 +00000-0 +76021-4 0 00001',
				'2 25338  98.5125 122.7694 0010246 179.7285 180.3903 14.27125825    07'
			]
			iss_tle = [
				# https://live.ariss.org/iss.txt
				'ISS (ZARYA)',
				'1 25544U 98067A   26132.19887560  .00004713  00000-0  93039-4 0  9991',
				'2 25544  51.6312 118.2489 0007476  49.7974 310.3668 15.49191856566178'
			]
			tle = iss_tle

		# map SatelliteCamera() into this class
		self.now = self._sc.now
		self.datetime = self._sc.datetime
		self.adjust_by_seconds = self._sc.adjust_by_seconds
		self.choose_attitude = self._sc.choose_attitude
		self.pixel_to_radec = self._sc.pixel_to_radec
		self.sensor_to_radec = self._sc.sensor_to_radec
		self.radec_to_pixel = self._sc.radec_to_pixel

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

	def camera_fov_border_vectors(self, border_step=40):
		""" camera_fov_border_vectors """
		polygon = self._sc.camera_fov_border_vectors(border_step=border_step)
		return [(float(v.ra.value), float(v.dec.value)) for v in polygon]
