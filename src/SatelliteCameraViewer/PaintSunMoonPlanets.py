""" PaintSunMoonPlanets """

from .misc import ra_fix, mag_map
from .ecliptic import body, planets, moon_illumination

class PaintSunMoonPlanets:
	""" PaintSunMoonPlanets """

	def __init__(self, ax, color_sun='red', color_moon='red', color_planets='red', fontdict=None):
		""" PaintSunMoonPlanets """
		self._ax = ax
		self._color_sun = color_sun
		self._color_moon = color_moon
		self._color_planets = color_planets
		self._fontdict = fontdict
		self._sun = None

	def change(self, value, obs_time, eci_position_vector):
		""" change """
		if value:
			self._enable(obs_time, eci_position_vector)
		else:
			self._disable()

	def _enable(self, obs_time, eci_position_vector):
		""" _enable """
		sun_ra_rad, sun_dec_rad = body('sun', obs_time, eci_position_vector)
		sun_ra_rad = ra_fix([sun_ra_rad])[0]
		# sun diameter is 0.533 degrees
		moon_ra_rad, moon_dec_rad = body('moon', obs_time, eci_position_vector)
		moon_ra_rad = ra_fix([moon_ra_rad])[0]
		planets_names, planets_ra_rad, planets_dec_rad, planets_mags = planets(obs_time, eci_position_vector)
		planets_ra_rad = ra_fix(planets_ra_rad)
		planets_size_pixels = mag_map(planets_mags)
		if self._sun is not None:
			# already painted
			self._sun.set_offsets([(sun_ra_rad, sun_dec_rad)])
			# no text needed for the sun
			# self._sun_text.set_position((sun_ra_rad, sun_dec_rad))
			self._moon.set_offsets([(moon_ra_rad, moon_dec_rad)])
			self._moon_text.set_position((moon_ra_rad, moon_dec_rad))
			v = [(planets_ra_rad[ii], planets_dec_rad[ii]) for ii in range(len(planets_ra_rad))]
			self._planets.set_offsets(v)
			# self._planets.set_sizes(planets_sie_pixels)
			for ii in range(len(planets_ra_rad)):
				self._planets_texts[ii].set_position((planets_ra_rad[ii], planets_dec_rad[ii]))
		else:
			self._sun = self._ax.scatter([sun_ra_rad], [sun_dec_rad], color=self._color_sun, alpha=0.5, s=500.0, marker='*')
			# no text needed for the sun
			# self._sun_text = self._ax.text(sun_ra_rad, sun_dec_rad, '  ' + 'sun', color=self._color_sun, rotation=90, ha='center', va=bottom', alpha=0.5, fontdict=self._fontdict)
			self._moon = self._ax.scatter([moon_ra_rad], [moon_dec_rad], color=self._color_moon, alpha=1.0, s=50.0)
			self._moon_text = self._ax.text(moon_ra_rad, moon_dec_rad, '  ' + 'Moon', color=self._color_moon, rotation=90, alpha=0.5, fontdict=self._fontdict, ha='center', va='bottom')
			self._planets = self._ax.scatter(planets_ra_rad, planets_dec_rad, s=planets_size_pixels, color=self._color_planets, alpha=0.5)
			# paint names just once - planets don't move that much.
			self._planets_texts = []
			for ii in range(len(planets_ra_rad)):
				p = self._ax.text(planets_ra_rad[ii], planets_dec_rad[ii], '  ' + planets_names[ii], color=self._color_planets, rotation=90, ha='center', va='bottom', alpha=0.5, fontdict=self._fontdict)
				self._planets_texts.append(p)

	def _disable(self):
		""" _disable """
		if self._sun is None:
			# nothimg painted
			return
		self._sun.remove()
		self._sun = None
		# no text needed for the sun
		# self._sun_text.remove()
		# self._sun_text = None
		self._moon.remove()
		self._moon = None
		self._moon_text.remove()
		self._moon_text = None
		self._planets.remove()
		self._planets = None
		for p in self._planets_texts:
			p.remove()
		self._planets_texts = []
