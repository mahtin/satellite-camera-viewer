"""
ISSAttitude - ISS International Space Station functions
"""

from datetime import datetime, timezone

import numpy as np
from scipy.spatial.transform import Rotation as R
from astropy.coordinates import get_sun, GCRS
from astropy.time import Time
import astropy.units as u
from sgp4.api import Satrec, jday

class ISSAttitude:
	"""
	ISSAttitude - ISS International Space Station functions
	"""

	_iss_docking_port_axes_body = {
		# Body-frame unit vectors for ISS docking ports.
		# Based on ISS body axes defined in ESA reference frames.
		# https://www.nasa.gov/wp-content/uploads/2022/06/508318main_iss_ref_guide_nov2010.pdf
		# Unity (Node 1)
		# Harmony (Node 2)
		# Tranquility (Node 3 - except it's not really called Node 3)

		# PORT NAME		[X (Velocity Vector), Y (left, perpendicular to the orbital plane), Z (Zenith or -Nadir)]
		'N1_QUEST_AIRLOCK':	np.array([ 0,-1, 0]),	# Unity (Node 1) Starboard (right)
		'N1_STARBOARD':		np.array([ 0,-1, 0]),

		'HARMONY_FORWARD':	np.array([+1, 0, 0]),	# Dragon/Starliner/Space Shuttle berthing
		'N2_FORWARD':		np.array([+1, 0, 0]),

		'HARMONY_ZENITH':	np.array([ 0, 0,+1]),	# Dragon/Starliner berthing
		'N2_ZENITH':		np.array([ 0, 0,+1]),

		'HARMONY_NADIR':	np.array([ 0, 0,-1]),	# Dragon/HTV/Cygnus berthing
		'N2_NADIR':		np.array([ 0, 0,-1]),

		'KIBO':			np.array([ 0,+1, 0]),	# Japanese Experiment Module (JAXA) (left)
		'N2_PORT':		np.array([ 0,+1, 0]),

		'COLUMBUS':		np.array([ 0,-1, 0]),	# The Columbus Laboratory Module (ESA) (right)
		'N2_STARBOARD':		np.array([ 0,-1, 0]),

		'CUPOLA':		np.array([ 0, 0,-1]),	# Tranquility (Node 3) Nadir port
		'N3_NADIR':		np.array([ 0, 0,-1]),
	}

	@classmethod
	def propagate_from_tle(cls, tle_line1: str, tle_line2: str):
		"""
		:param tle_line1: TLE line one.
		:type tle_line1: str
		:param tle_line2: TLE line one.
		:type tle_line2: str

		:return: A tuple (r_eci_km in Km, v_eci_km_s in Km/s) from a two-line TLE.
		:rtype: (float, float)
		"""
		sat = Satrec.twoline2rv(tle_line1, tle_line2)
		now_utc = datetime.now(timezone.utc)
		jd, fr = jday(now_utc.year, now_utc.month, now_utc.day, now_utc.hour, now_utc.minute, now_utc.second + now_utc.microsecond/1e6)
		error, r_eci, v_eci = sat.sgp4(jd, fr)
		if error != 0:
			raise RuntimeError('SGP4 propagation error code: %s' % (error)) from None
		return r_eci, v_eci

	# ------------------------------------------------------------
	# LVLH FRAME (ESA Reference Frame Definition)
	# ------------------------------------------------------------

	@classmethod
	def lvlh_frame(cls, r_eci, v_eci):
		"""
		:param r_eci: ECI position.
		:type r_eci: float
		:param v_eci: ECI velocity.
		:type v_eci: float

		:return: Returns LVLH frame unit vectors from ECI position and velocity.
			Based on ESA ISS Reference Frames:
			Z_LVLH = -r_hat (nadir or -zenith)
			Y_LVLH = -h_hat (opposite orbit normal)
			X_LVLH = Y × Z (velocity direction)
		:rtype: dict
		"""
		r = np.array(r_eci)
		v = np.array(v_eci)

		z_lvlh = -r / np.linalg.norm(r)
		h = np.cross(r, v)
		y_lvlh = -h / np.linalg.norm(h)
		x_lvlh = np.cross(y_lvlh, z_lvlh)

		return {'X': x_lvlh, 'Y': y_lvlh, 'Z': z_lvlh}

	# ------------------------------------------------------------
	# XVV ATTITUDE (X-axis aligned with velocity)
	# ------------------------------------------------------------

	@classmethod
	def xvv_attitude_quaternion(cls, r_eci, v_eci):
		"""
		Construct quaternion for XVV attitude:
		  +X = velocity direction
		  +Z = nadir
		  +Y = completes RH frame
		"""
		lvlh = cls.lvlh_frame(r_eci, v_eci)
		R_body = np.vstack([lvlh['X'], lvlh['Y'], lvlh['Z']])
		return R.from_matrix(R_body).as_quat()

	# ------------------------------------------------------------
	# TEA (Torque Equilibrium Attitude) OFFSETS (NASA MCS)
	# ------------------------------------------------------------

	@classmethod
	def tea_offsets_deg(cls, port_config='DEFAULT'):
		"""
		TEA values from NASA ISS Motion Control System documentation:
		Current +XVV TEA: yaw=-4 deg, roll=0.9 deg
		Pitch varies from -12 to -2 deg depending on visiting vehicles.
		"""
		if port_config == 'DEFAULT':
			pitch = -7.0	# midpoint of NASA's -12 to -2 deg range
		else:
			pitch = port_config

		return {'yaw': -4.0, 'pitch': pitch, 'roll': 0.9}

	@classmethod
	def apply_tea_to_quaternion(cls, q, tea_deg):
		"""
		Apply TEA yaw/pitch/roll offsets to a base attitude quaternion.
		"""
		r_base = R.from_quat(q)
		r_tea = R.from_euler('ZYX', [tea_deg['yaw'], tea_deg['pitch'], tea_deg['roll']], degrees=True)
		return (r_tea * r_base).as_quat()

	# ------------------------------------------------------------
	# SUN VECTOR + SOLAR BETA ANGLE
	# ------------------------------------------------------------

	@classmethod
	def _sun_vector_eci(cls):
		"""
		Returns Sun vector in ECI (GCRS) coordinates, km.
		Works across all modern Astropy versions.
		"""
		now = Time(datetime.now(timezone.utc))
		sun = get_sun(now).transform_to(GCRS(obstime=now))

		# Use the cartesian representation (always available)
		x = sun.cartesian.x.to(u.km).value
		y = sun.cartesian.y.to(u.km).value
		z = sun.cartesian.z.to(u.km).value

		return np.array([x, y, z])

	@classmethod
	def solar_beta_angle(cls, r_eci, v_eci):
		"""
		In orbital mechanics, the beta angle (β) is the angle between a satellite's orbital plane around
		Earth and the geocentric position of the Sun.  The beta angle determines the percentage of time
		that a satellite in low Earth orbit (LEO) spends in direct sunlight, absorbing solar radiation

		Yearly Variation: The ISS beta angle fluctuates between roughly -75 and +75 degrees over a 60-day
		precession period and on an annual cycle.
		"""
		sun_eci = cls._sun_vector_eci()
		s_hat = sun_eci / np.linalg.norm(sun_eci)
		h = np.cross(r_eci, v_eci)
		h_hat = h / np.linalg.norm(h)
		beta = np.arcsin(np.dot(h_hat, s_hat))
		return np.degrees(beta)

	# ------------------------------------------------------------
	# DOCKING PORT GEOMETRY (Derived from ISS body axes)
	# ------------------------------------------------------------

	@classmethod
	def docking_port_vector_eci(cls, port_name, quaternion_xyzw):
		"""
		Body-frame unit vectors for ISS docking ports.
		Based on ISS body axes defined in ESA reference frames.

		Parameters:
			port_name  : ISS port name
		"""
		try:
			iss_body_vec = cls._iss_docking_port_axes_body[port_name]
		except KeyError:
			raise ValueError('Unknown port: %s' % (port_name)) from None
		r = R.from_quat(quaternion_xyzw)
		return r.apply(iss_body_vec)

	@classmethod
	def iss_in_eclipse(cls, r_eci):
		"""
		Returns True if ISS is in Earth's umbra (full shadow).

		Parameters:
			r_eci  : ISS position vector (km)
		"""

		sun_eci = cls._sun_vector_eci()

		r = np.array(r_eci)
		s = np.array(sun_eci)

		# Unit vector from Earth to Sun
		s_hat = s / np.linalg.norm(s)

		# Projection of ISS position onto Sun direction
		d = np.dot(r, s_hat)

		# If ISS is on the sunward side of Earth → cannot be in shadow
		if d > 0:
			return False

		# Perpendicular distance from ISS to Sun line
		r_perp = np.linalg.norm(r - d * s_hat)

		earth_radius_km = u.R_earth.to(u.km)

		# Inside Earth's shadow cylinder?
		return r_perp < earth_radius_km

def _main(args=None):
	""" _main """

	# from ISSAttitude import ISSAttitude

	tle = [
		# https://live.ariss.org/iss.txt
		'ISS (ZARYA)',
		'1 25544U 98067A   26109.48996334  .00010082  00000-0  19194-3 0  9992',
		'2 25544  51.6329 230.6068 0006631 325.6576  34.3983 15.48833250562656'
	]
	r_eci, v_eci = ISSAttitude.propagate_from_tle(tle[1], tle[2])

	lvlh = ISSAttitude.lvlh_frame(r_eci, v_eci)
	q_xvv = ISSAttitude.xvv_attitude_quaternion(r_eci, v_eci)
	tea = ISSAttitude.tea_offsets_deg()
	q_tea = ISSAttitude.apply_tea_to_quaternion(q_xvv, tea)
	beta = ISSAttitude.solar_beta_angle(r_eci, v_eci)
	port_vec = ISSAttitude.docking_port_vector_eci('N2_FORWARD', q_tea)
	in_eclipse = ISSAttitude.iss_in_eclipse(r_eci)

	print('lvlh', end=' ')
	for k, xyz_lvlh in lvlh.items():
		print(k, [round(v,2) for v in xyz_lvlh], end=', ')
	print('q_xvv', [round(v,2) for v in q_xvv], end=', ')
	print('tea(ypr)', [tea['yaw'], tea['pitch'], tea['roll']], end=', ')
	print('q_tea', [round(v,2) for v in q_tea], end=', ')
	print('port_vec', [round(v,2) for v in port_vec], end=', ')
	print('beta%', round(beta,2), end=', ')
	if in_eclipse:
		print('in_eclipse', end='')
	else:
		print('in_sun', end='')
	print('')

if __name__ == '__main__':
	_main()
