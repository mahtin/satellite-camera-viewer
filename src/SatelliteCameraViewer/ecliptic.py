""" ecliptic """

import numpy as np
from astropy.coordinates import SkyCoord, get_sun, get_body
from astropy.time import Time
import astropy.units as u

def ecliptic(nsteps=180):
	""" ecliptic """
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

def body(which, obs_time):
	""" body """
	t = Time(obs_time)
	# Get Sun position in GCRS frame
	body_gcrs = get_body(which, t)
	# Transform to ICRS (Equatorial) and extract RA/Dec in degrees
	body_icrs = body_gcrs.transform_to('icrs')
	return body_icrs.ra.rad, body_icrs.dec.rad

# handled by body('sun')
#def sun(obs_time):
#	""" sun """
#	t = Time(obs_time)
#	sun_gcrs = get_sun(t)
#	return body('sun', obs_time)

def galactic_plane(nsteps=180):
	""" galactic_plane """

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
def moon_illumination(obs_time):
	"""
	Calculate fraction of the moon illuminated.

	Parameters
	----------
	obs_time : `datetime`
		Time of observation

	Returns
	-------
	i : `~astropy.units.Quantity`
		Phase angle of the moon [radians]
	"""
	t = Time(obs_time)
	sun = get_sun(t)
	moon = get_body('moon', t)
	elongation = sun.separation(moon)
	i = np.arctan2(sun.distance*np.sin(elongation), moon.distance - sun.distance*np.cos(elongation))
	k = (1 + np.cos(i))/2.0
	return k.value
