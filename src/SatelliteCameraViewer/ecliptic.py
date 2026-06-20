""" ecliptic """

import math
from datetime import datetime
import numpy as np
from astropy.coordinates import SkyCoord, get_body, EarthLocation
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
	equatorial_coords = ecl_coords.gcrs
	# 3. wrap as needed
	ra_rad = equatorial_coords.ra.wrap_at(180*u.deg).radian  # Wrap to -pi to pi for Mollweide
	dec_rad = equatorial_coords.dec.radian
	# return a simple lists - use transpose to build an array of [ra,dec]'s
	#return np.array([ra_rad, dec_rad]).T
	return np.array([ra_rad, dec_rad])

def body(which:str, obs_time:datetime, location=None):
	"""
	body - return the position (in RA/DEC) for a specific solar system body (Sun and Moon being the use cases).

	:param which: Which body (sun, moon, etc).
	:type which: str
	:param obs_time: Time of observation.
	:type obs_time: datetime`
	:param location: Location of observer on the Earth in x,y,z coords.
	:type location: tuple[float, float, float]
	:return: The RA/DEC of the body
	:rtype: tuple(float, float)
	"""
	t = Time(obs_time)
	if location is not None:
		# Location on Earth, initialized from geocentric coordinates.
		location = EarthLocation.from_geocentric(location[0], location[1], location[2], unit='km')
	# Get sun or moon or planets  position in GCRS frame
	body_gcrs = get_body(which, t, location=location)
	# Transform to ICRS (Equatorial) and extract RA/Dec in degrees
	return float(body_gcrs.ra.rad), float(body_gcrs.dec.rad)

def sun(obs_time:datetime, location=None):
	"""
	sun - return the position (in RA/DEC) for the sun. Using `body()` would be preferred.

	:param obs_time: Time of observation.
	:type obs_time: datetime`
	:return: The RA/DEC of the sun
	:rtype: tuple(float, float)
	"""
	# now handled by body('sun')
	return body('sun', obs_time, location=location)

def planets(obs_time:datetime, location=None):
	"""
	planets - return the position (in RA/DEC) for the planets.

	:param obs_time: Time of observation.
	:type obs_time: datetime`
	:return: The RA/DEC of the planets
	:rtype: list(tuple(float, float))
	"""

	_planets = [
		# Planet	Max	Min Brightness
		('Mercury',	-2.5,	+5.5),
		('Venus',	-4.9,	-3.8),
		# Not actual brighness of Earth. It's -20 to -23 from LEO satellite and -17 to -22 from GEO
		('Earth',	-3.8,	-3.8),
		('Mars',	-3.0,	+1.8),
		('Jupiter',	-2.9,	-1.6),
		('Saturn',	+0.2,	+1.2),
		# Removed becuase 1) can't see them. 2) the astropy function body() isn't perfect.
		# ('Uanus',	+5.3,	+5.9),
		# ('Neptune',	+7.7,	+8.0),
		# ('Pluto',	+14.5,	+14.5),
	]

	names = []
	ra_rad = []
	dec_rad = []
	mags = []
	for p in _planets:
		try:
			ra, dec =  body(p[0], obs_time, location=location)
		except KeyError:
			# some planets are supported
			continue
		mag = (p[1] + p[2])/2
		names.append(p[0])
		ra_rad.append(ra)
		dec_rad.append(dec)
		mags.append(mag)
	return names, ra_rad, dec_rad, mags

def earth_vector(obs_time:datetime, location=None):
	""" earth_vector """
	t = Time(obs_time)
	if location:
		# Location on Earth, initialized from geocentric coordinates.
		location = EarthLocation.from_geocentric(location[0], location[1], location[2], unit='km')
	earth_icrs = get_body('earth', t, location=location).transform_to("icrs")
	earth_vec = earth_icrs.cartesian.xyz.value
	return earth_vec

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
	the_sun = get_body('sun', t)
	the_moon = get_body('moon', t)
	elongation = the_sun.separation(the_moon)
	i = np.arctan2(the_sun.distance*np.sin(elongation), the_moon.distance - the_sun.distance*np.cos(elongation))
	k = (1 + np.cos(i))/2.0
	return k.value

def _main(args=None):
	""" _main """
	import math                               # pylint: disable=C0415
	from datetime import timezone, timedelta  # pylint: disable=C0415

	location = [1000000.0, 1000000.0, 1000000000.0]
	location = None
	now_utc = datetime.now(timezone.utc)
	midnight_utc = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
	for d in range(31):
		new_date = midnight_utc + timedelta(days=d)
		ev = earth_vector(new_date, location)
		print(ev)
		continue
		illum_percent = moon_illumination(new_date)
		moon_ra_rad, moon_dec_rad = body('moon', new_date, location)
		moon_ra_deg = math.degrees(moon_ra_rad)
		moon_dec_deg = math.degrees(moon_dec_rad)
		earth_ra_rad, earth_dec_rad = body('earth', new_date, location)
		earth_ra_deg = math.degrees(earth_ra_rad)
		earth_dec_deg = math.degrees(earth_dec_rad)
		print('%3d: %s [%5.1f,%5.1f] [%5.1f,%5.1f] Moon Illumination: %5.1f%% %s' % (
			d,
			new_date.strftime('%Y-%m-%d %H:%M'),
			earth_ra_deg, earth_dec_deg,
			moon_ra_deg, moon_dec_deg,
			illum_percent*100,
			'\u2592' * int(illum_percent*100+0.5)))

if __name__ == '__main__':
	_main()
