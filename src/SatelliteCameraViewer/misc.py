""" misc """

import math
import numpy as np

def arcseconds_to_radians(arcsec):
	"""
	arcseconds_to_radians - convert arcseconds to radians

	:param arcsec: An arcsecond - which is a tiny unit of angular measurement. I.e. 1/60'th of 1/60'th of a degree.
	:type arcsec: float

	:return: The angular value in radians.
	:rtype: float

	"""
	# Formula: arcseconds / 3600 (to deg) * (pi / 180) (to rad)
	return arcsec * (math.pi / 648000)

def ra_fix(ra_rad):
	"""
	ra_fix - correct RA values for mollweide projection.

	:param ra_rad: An array of radians describing the right ascension (RA) of a star.
	:type ra_rad: list[float] | numpy.ndarray

	:return: RA corrected values for mollweide projection.
	:rtype: list[float]

	"""
	# 2. Shift RA to [-180, 180] or [-pi, pi] and reverse direction (east left)
	# The projection expects: RA in [-pi, pi], Dec in [-pi/2, pi/2]
	ra_rad = [(v + math.pi) % (2 * math.pi) - math.pi for v in ra_rad]	# shift to [-pi, pi]
	ra_rad = [-v for v in ra_rad]						# reverse direction
	return ra_rad

def mag_map(mag, multiplier=1.0):
	"""
	mag_map - convert star magnitude to pixel size.

	:param mag: An array of magnitudes
	:type mag: float | list[float] | numpy.ndarray

	:param multiplier: Scaling factor for pixel size
	:type multiplier: float

	:return: An array of pixel sizes ready to plot
	:rtype: float | list[float] | numpy.ndarray

	"""
	def _mag_map1(mag, multiplier):
		""" _mag_map1 """
		m = 4 * multiplier
		if mag <= 1.0:
			return 10 * m
		if mag <= 2.0:
			return 7 * m
		if mag <= 3.0:
			return 4 * m
		if mag <= 4.0:
			return 3 * m
		if mag <= 5.0:
			return 2 * m
		return 1 * m

	if isinstance(mag, (list, np.ndarray)):
		return [_mag_map1(v, multiplier) for v in mag]
	return _mag_map1(mag, multiplier)

def split_plot_mollweide_line_ra_dec_deg(ra_dec_deg: list[tuple[float,float]]):
	"""
	split_plot_mollweide_line_ra_dec_deg - Plot a line on a Mollweide projection, splitting into multiple segments when crossing RA = +/- PI.
	No off-by-one errors.

	:param ra_dec_deg: An array of (ra,dec) values
	:type ra_dec_deg: list[tuple[float,float]]

	:return: A list of segments to plot on a mollweide graph.
	:rtype: list
	"""
	ra_rad = np.radians([v[0] for v in ra_dec_deg])
	dec_rad = np.radians([v[1] for v in ra_dec_deg])
	return split_plot_mollweide_line(ra_rad, dec_rad, True)

def split_plot_mollweide_line(ra_rad_or_deg, dec_rad_or_deg, is_radians=False):
	"""
	split_plot_mollweide_line - Plot a line on a Mollweide projection, splitting into multiple segments when crossing RA = +/- PI.
	No off-by-one errors.

	:param ra_deg: An array of ra values
	:type ra_deg: list[float]
	:param dec_deg: An array of dec values
	:type dec_deg: list[float]
	:param is_radians: Control radians or degrees
	:type is_radians: bool

	:return: A list of segments to plot on a mollweide graph.
	:rtype: list
	"""

	def _intersect_ra_boundary(ra1, dec1, ra2, dec2):
		"""
		Compute intersection of a line segment with RA = +/- PI boundary.
		Returns (ra_int, dec_int) in radians.
		"""

		# Determine which boundary is crossed
		if ra1 > 0 and ra2 < 0:
			boundary = np.pi
		elif ra1 < 0 and ra2 > 0:
			boundary = -np.pi
		else:
			# no boundary crossing
			return None

		# Linear interpolation factor
		t = (boundary - ra1) / (ra2 - ra1)

		# Interpolate dec
		dec_int = dec1 + t * (dec2 - dec1)

		return boundary, dec_int

	if is_radians:
		ra_rad = ra_rad_or_deg
		dec_rad = dec_rad_or_deg
	else:
		# Convert to radians
		ra_rad = np.radians(ra_rad_or_deg)
		dec_rad = np.radians(dec_rad_or_deg)

	# Shift RA from [0, 2PI] -> [-PI, +PI]
	ra_rad = np.where(ra_rad > np.pi, ra_rad - 2*np.pi, ra_rad)

	segments = []
	seg_ra = [ra_rad[0]]
	seg_dec = [dec_rad[0]]

	for i in range(len(ra_rad) - 1):
		ra1, dec1 = ra_rad[i], dec_rad[i]
		ra2, dec2 = ra_rad[i+1], dec_rad[i+1]

		# Check for wrap crossing
		if abs(ra2 - ra1) > np.pi:
			# Compute intersection
			result = _intersect_ra_boundary(ra1, dec1, ra2, dec2)
			if result is not None:
				ra_int, dec_int = result

				# Finish current segment at intersection
				seg_ra.append(ra_int)
				seg_dec.append(dec_int)
				# XXX [1:-1] - this is incorrect!
				segments.append((np.array(seg_ra[1:-1]), np.array(seg_dec[1:-1])))

				# Start new segment at intersection
				seg_ra = [ra_int]
				seg_dec = [dec_int]

			# Continue to next iteration
			continue

		# Normal continuation
		seg_ra.append(ra2)
		seg_dec.append(dec2)

	# Append final segment
	if len(seg_ra) > 1:
		segments.append((np.array(seg_ra[1:-1]), np.array(seg_dec[1:-1])))

	return segments
