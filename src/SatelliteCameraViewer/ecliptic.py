""" ecliptic """

from datetime import datetime
import numpy as np
from astropy.coordinates import SkyCoord, get_sun, get_body
from astropy.time import Time
import astropy.units as u

def ecliptic(nsteps:int=180):
	"""
	ecliptic - Caculate the ecliptic line.

	:param nsteps: Numer of steps to use in returned line.
	:type nsteps: int
	:return: a series of points to describe the ecliptic line.
	:rtype: np.array
	"""
	# 1. Generate ecliptic coordinates (longitude 0-360, latitude 0) in 'ecl' (Heliocentric/Barycentric Ecliptic) form
	lon_ecl = np.linspace(0, 360, num=nsteps)
	lat_ecl = np.zeros_like(lon_ecl)
	# 2. Transform to Equatorial (ICRS) coordinates
	ecl_coords = SkyCoord(lon=lon_ecl*u.deg, lat=lat_ecl*u.deg, frame='geocentrictrueecliptic')
	equatorial_coords = ecl_coords.icrs
	# 3. wrap as needed
	ra_rad = equatorial_coords.ra.wrap_at(180*u.deg).radian  # Wrap to -pi to pi for Mollweide
	dec_rad = equatorial_coords.dec.radian
	# return a simple lists - use transpose to build an array of [ra,dec]'s
	#return np.array([ra_rad, dec_rad]).T
	return np.array([ra_rad, dec_rad])

def body(which:str, obs_time:datetime):
	"""
	body - return the position (in RA/DEC) for a specific solar system body (Sun and Moon being the use cases).

	:param obs_time: Time of observation.
	:type obs_time: datetime`
	:return: The RA/DEC of the body
	:rtype: tuple(float, float)
	"""
	t = Time(obs_time)
	# Get Sun position in GCRS frame
	body_gcrs = get_body(which, t)
	# Transform to ICRS (Equatorial) and extract RA/Dec in degrees
	body_icrs = body_gcrs.transform_to('icrs')
	return float(body_icrs.ra.rad), float(body_icrs.dec.rad)

def sun(obs_time:datetime):
	"""
	sun - return the position (in RA/DEC) for the sun. Using `body()` would be preferred.

	:param obs_time: Time of observation.
	:type obs_time: datetime`
	:return: The RA/DEC of the sun
	:rtype: tuple(float, float)
	"""
	# now handled by body('sun')
	return body('sun', obs_time)

def galactic_plane(nsteps:int=180):
	"""
	galactic_plane - Caculate the galatic plane.

	:param nsteps: Numer of steps to use in returned line.
	:type nsteps: int
	:return: a series of points to describe the galatic plane.
	:rtype: np.array
	"""
	# Generate points along the galactic plane (b=0)
	l = np.linspace(-180, 180, nsteps) * u.deg
	b = np.zeros_like(l)
	galactic_galactic = SkyCoord(l=l, b=b, frame='galactic')
	galactic_icrs = galactic_galactic.icrs

	ra_rad = galactic_icrs.ra.wrap_at(180*u.deg).radian  # Wrap to -pi to pi for Mollweide
	dec_rad = galactic_icrs.dec.radian
	# return a simple lists - use transpose to build an array of [ra,dec]'s
	#return np.array([ra_rad, dec_rad]).T
	return np.array([ra_rad, dec_rad])

# https://github.com/astropy/astroplan/blob/main/astroplan/moon.py
def moon_illumination(obs_time:datetime):
	"""
	moon_illumination - Calculate fraction of the moon illuminated.

	:param obs_time: Time of observation.
	:type obs_time: datetime`
	:return: Phase angle of the moon [radians].
	:rtype: float
	"""
	t = Time(obs_time)
	sun = get_sun(t)
	moon = get_body('moon', t)
	elongation = sun.separation(moon)
	i = np.arctan2(sun.distance*np.sin(elongation), moon.distance - sun.distance*np.cos(elongation))
	k = (1 + np.cos(i))/2.0
	return k.value

def _main(args=None):
	""" _main """
	import math
	from datetime import timezone, timedelta
	now_utc = datetime.now(timezone.utc)
	midnight_utc = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
	for d in range(31):
		new_date = midnight_utc + timedelta(days=d)
		illum_percent = moon_illumination(new_date)
		ra_rad, dec_rad = body('moon', new_date)
		ra = math.degrees(ra_rad)
		dec = math.degrees(dec_rad)
		print('%3d: %s [%5.1f,%5.1f] Moon Illumination: %5.1f%% %s' % (d, new_date.strftime('%Y-%m-%d %H:%M'), ra, dec, illum_percent*100, '\u2592' * int(illum_percent*100+0.5)))

if __name__ == '__main__':
	_main()
