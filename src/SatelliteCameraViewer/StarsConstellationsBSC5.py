""" StarsConstellationsBSC5 """

import math

from .BSC5Stars import BSC5Stars
from .misc import ra_fix, mag_map

class StarsConstellationsBSC5:
	""" StarsConstellationsBSC5 """

	def __init__(self, ax, star_colors='red', constellation_colors='red', constellations=None, mag=5.0):
		""" StarsConstellationsBSC5 """
		self._ax = ax
		self._star_colors = star_colors
		self._constellation_colors = constellation_colors
		self._constellations = constellations
		if self._constellations is None:
			# Orion and Sagittarius because they are not next to each other
			self._constellations = ['Ori', 'Sgr']
		self._bsc5 = BSC5Stars(max_mag=mag)
		self._stars_plot = None

	@property
	def stars(self):
		""" stars """
		return self._bsc5.stars

	@property
	def skycoords(self):
		""" skycoords """
		return self._bsc5.skycoords

	@property
	def max_mag(self):
		""" max_mag """
		return self._bsc5.max_mag

	@max_mag.setter
	def max_mag(self, value):
		""" max_mag """
		self._bsc5.max_mag = value

	def get_stars(self):
		""" get_stars """
		return self._bsc5.get_stars()

	def get_constellations(self):
		""" get_constellations """
		return self._bsc5.get_constellations(constellations=self._constellations)

	def plot_stars(self):
		""" plot_star - add all the stars to the sky plot """
		if self._stars_plot is not None:
			# already plotted
			return
		self._stars_plot = []

		# stars ...
		stars_ra_rad, stars_dec_rad, stars_mag = self.get_stars()
		stars_ra_rad = ra_fix(stars_ra_rad)
		stars_size_pixels = mag_map(stars_mag)
		p1 = self._ax.scatter(stars_ra_rad, stars_dec_rad, s=stars_size_pixels, alpha=1, color=self._star_colors, zorder=5)
		self._stars_plot.append(p1)

		# constellations ...
		constellations_ra_rad, constellations_dec_rad, constellations_mag = self.get_constellations()
		constellations_ra_rad = ra_fix(constellations_ra_rad)
		constellations_size_pixels = mag_map(constellations_mag)
		p2 = self._ax.scatter(constellations_ra_rad, constellations_dec_rad, s=constellations_size_pixels, alpha=1, color=self._constellation_colors, zorder=5)
		self._stars_plot.append(p2)

	def clear_stars(self):
		""" clear_stars """
		if self._stars_plot is None:
			# already not plotted
			return
		for p in self._stars_plot:
			p.remove()
		self._stars_plot = None

