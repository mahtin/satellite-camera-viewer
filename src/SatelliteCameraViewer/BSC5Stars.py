"""

BSC5Stars - a wrapper for The Yale Bright Star Catalog, 5th Edition (BSC5).

"""

import numpy as np
from astropy.coordinates import SkyCoord

from .StarCatalog import StarCatalog

class BSC5Stars:
	"""
	BSC5Stars - a wrapper for The Yale Bright Star Catalog, 5th Edition (BSC5).
	:param max_mag: Maximum star magnitude to process.
	:type max_mag: float
	"""

	def __init__(self, max_mag=4):
		"""
		BSC5Stars - a wrapper for The Yale Bright Star Catalog, 5th Edition (BSC5).
		:param max_mag: Maximum star magnitude to process.
		:type max_mag: float
		"""
		self._sc = StarCatalog('BSC5', use_database=True, force_reload=False)
		self._stars = None
		self._skycoords = None
		self._max_mag = math.floor(max_mag)

		self._stars_ra_rad = []
		self._stars_dec_rad = []
		self._stars_mag = []
		self._const_ra_rad = []
		self._const_dec_rad = []
		self._const_mag = []

	def _proceess_stars(self):
		""" _proceess_stars """
		if self._stars is not None:
			# done already
			return
		self._stars = self._sc.select_max_mag(self._max_mag)

	def _proceess_skycoords(self):
		""" _proceess_skycoords """
		if self._skycoords is not None:
			# done already
			return
		self._proceess_stars()
		# Use ICRS as there's no time represented
		self._skycoords = SkyCoord([(v.ra,v.dec) for v in self.stars], unit='rad', frame='icrs')

	def __len__(self):
		""" __len__ """
		self._proceess_stars()
		return len(self._stars)

	def __array__(self, dtype=None):
		"""Allows np.array(instance) to work."""
		self._proceess_stars()
		return np.array(self._stars, dtype=dtype)

	@property
	def max_mag(self):
		"""
		max_mag - get maximum magnitude.
		:return: Maximum star magnitude to process.
		:rtype: float
		"""
		return self._max_mag

	@max_mag.setter
	def max_mag(self, value):
		"""
		max_mag - set maximum magnitude.
		:param max_mag: Maximum star magnitude to process.
		:type max_mag: float
		"""
		if self._max_mag == value:
			return
		self._max_mag = value
		# now reset everything!
		self._stars = None
		self._skycoords = None

		self._stars_ra_rad = []
		self._stars_dec_rad = []
		self._stars_mag = []

		self._const_ra_rad = []
		self._const_dec_rad = []
		self._const_mag = []

	@property
	def stars(self):
		"""
		stars - return an array of stars.
		:return: array of stars.
		:rtype: list[Stars]
		"""
		self._proceess_stars()
		return self._stars

	@property
	def skycoords(self):
		"""
		skycoords - return an array of stars (in SkyCoord format).
		:return: array of stars in SkyCoord format.
		:rtype: list[SkyCoord]
		"""
		self._proceess_skycoords()
		return self._skycoords

	def get_stars(self):
		""" get_stars - return an array of stars.
		:return: array of stars.
		:rtype: np.array
		"""
		self._precompute_stars()
		return np.array(self._stars_ra_rad), np.array(self._stars_dec_rad), np.array(self._stars_mag)

	def get_constellations(self, constellations=['Ori','Lib']):
		"""
		get_constellations - return an array of constellations.
		:return: array of constellations.
		:rtype: np.array
		"""
		self._precompute_constellation(constellations)
		return np.array(self._const_ra_rad), np.array(self._const_dec_rad), np.array(self._const_mag)

	def _precompute_stars(self):
		""" _precompute_stars """
		if len(self._stars_ra_rad) > 0:
			return

		self._stars_ra_rad = []
		self._stars_dec_rad = []
		self._stars_mag = []

		for star in self.stars:
			self._stars_ra_rad.append(star.ra)
			self._stars_dec_rad.append(star.dec)
			self._stars_mag.append(star.mag)

	def _precompute_constellation(self, constellations):
		""" _precompute_constellation """
		if len(self._const_ra_rad) > 0:
			return

		self._const_ra_rad = []
		self._const_dec_rad = []
		self._const_mag = []

		for star in self.stars:
			if star.constellation not in constellations:
				continue
			self._const_ra_rad.append(star.ra)
			self._const_dec_rad.append(star.dec)
			self._const_mag.append(star.mag)


def _main(args=None):
	""" _main """
	b = BSC5Stars()
	s = b.stars
	print(s[0:10])
	#[
	#	Star(number=2491, name='9Alp',  constellation='CMa', ra=1.7677930939085398, dec=-0.29175117701809655, mag=-1.46),
	#	Star(number=7001, name='3Alp',  constellation='Lyr', ra=4.87356286460115,   dec=0.6769017097019452,   mag=0.03),
	#	Star(number=1708, name='13Alp', constellation='Aur', ra=1.3818208020352105, dec=0.802817518959714,    mag=0.08),
	#	Star(number=1713, name='19Bet', constellation='Ori', ra=1.3724323851005242, dec=-0.14314608748440158, mag=0.12),
	#	Star(number=2943, name='10Alp', constellation='CMi', ra=2.0040815858077057, dec=0.09119345341670373,  mag=0.38),
	#	Star(number=472,  name='Alp',   constellation='Eri', ra=0.4263621196465648, dec=-0.998968286199821,   mag=0.46),
	#	Star(number=2061, name='58Alp', constellation='Ori', ra=1.5497287482822817, dec=0.12927556806785778,  mag=0.5 ),
	#	Star(number=5267, name='Bet',   constellation='Cen', ra=3.6818738679550713, dec=-1.0537085989338988,  mag=0.61),
	#	Star(number=7557, name='53Alp', constellation='Aql', ra=5.195772461134952,  dec=0.15478161583103048,  mag=0.77),
	#	Star(number=1457, name='87Alp', constellation='Tau', ra=1.2039281180256884, dec=0.2881393150938305,   mag=0.85)
	#]

if __name__ == '__main__':
	_main()
