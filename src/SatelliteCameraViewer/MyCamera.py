""" MyCamera """

from .SatelliteCamera import SatelliteCamera
from .TLEFetch import TLEFetch
from .static_list_satellites import static_list_satellites

class MyCamera:
	""" MyCamera """

	def __init__(self, satellite_name=None, camera_name:str=None, focal_length_mm:float=None):
		# Define camera on satellite
		self._sc = SatelliteCamera(camera_name=camera_name, focal_length_mm=focal_length_mm)

		# map SatelliteCamera() into this class (yes - there's a more pythonic way to do this)
		self.now                        = self._sc.now

		self.adjust_by_seconds          = self._sc.adjust_by_seconds
		self.choose_attitude            = self._sc.choose_attitude
		self.pixel_to_radec             = self._sc.pixel_to_radec
		self.sensor_to_radec            = self._sc.sensor_to_radec
		self.radec_to_pixel             = self._sc.radec_to_pixel

		self.sat_lon_lat_alt            = self._sc.sat_lon_lat_alt
		self.sat_in_eclipse             = self._sc.sat_in_eclipse

		self.earth_center_vector        = self._sc.earth_center_vector
		self.earth_center_vector_icrs   = self._sc.earth_center_vector_icrs
		self.earth_center_radec_simple  = self._sc.earth_center_radec_simple
		self.earth_center_radec         = self._sc.earth_center_radec
		self.earth_angular_radius       = self._sc.earth_angular_radius
		self.camera_fov_intercept_earth = self._sc.camera_fov_intercept_earth

		# set everything up
		if satellite_name is not None:
			self.find_tle(satellite_name)
		else:
			# Define satellite orbit from TLE from a static set
			self.tle = TLEFetch(static_list_satellites[0].sat_id).tle.as_array
		self.now()
		self.choose_attitude('vv')

	@property
	def observed_time(self):
		""" observed_time """
		return self._sc.observed_time

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
		for t in static_list_satellites:
			if satellite_name == t.name:
				break
			ii += 1
		if ii >= len(static_list_satellites):
			raise ValueError('%s not in satellites list' % (satellite_name))
		self.tle = TLEFetch(static_list_satellites[ii].sat_id).tle.as_array

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

	def camera_fov_border_vectors_radec_deg(self, border_step:int):
		""" camera_fov_border_vectors_radec_deg """
		polygon = self._sc.camera_fov_border_vectors(border_step=border_step)
		return [(float(v.ra.value), float(v.dec.value)) for v in polygon]

	def camera_fov_border_vectors(self, border_step:int):
		""" camera_fov_border_vectors """
		return self._sc.camera_fov_border_vectors(border_step=border_step)
