""" PaintConstellation """

import math

from .Constellations import ConstellationBoundaries, ConstellationDatabase, ConstellationLocations

class PaintConstellation:
	""" PaintConstellation """

	def __init__(self, ax, color='red'):
		""" PaintConstellation """
		self.ax = ax
		self.color = color
		self._cb = None
		self._p = []
		# self._cl = None
		# self._t = []

	def change(self, value):
		""" change """
		if self._cb is None:
			self._cb = ConstellationBoundaries()
			# text names not really needed
			# self._cl = ConstellationLocations()
		if value:
			self._enable()
		else:
			self._disable()

	def _enable(self):
		""" _enable """
		if len(self._p) > 0:
			# already painted
			return
		for segment in self._cb.data2plot():
			# segments are in radians
			p = self.ax.plot(
				segment[0], segment[1],
				label='Constellation Boundary',
				color=self.color, alpha=0.75,
				linewidth=1, linestyle='dashed')
			self._p.append(p[0])
		# text names not really needed
		#for constellation in self._cl.data.values():
		#	ra_rad = math.radians(constellation.ra_deg)
		#	dec_rad = math.radians(constellation.dec_deg)
		#	t = self.ax.text(ra_rad, dec_rad, constellation.name, rotation=45, color=self.color, alpha=1.0)
		#	self._t.append(t)

	def _disable(self):
		""" _disable """
		if len(self._p) == 0:
			# nothimg painted
			return
		for p in self._p:
			p.remove()
		self._p = []
		# for t in self._t:
		# 	t.remove()
		# self._t = []
