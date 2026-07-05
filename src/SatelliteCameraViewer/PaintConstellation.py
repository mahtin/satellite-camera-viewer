""" PaintConstellation """

from .Constellations import ConstellationBoundaries, ConstellationDatabase, ConstellationLocations

class PaintConstellation:
	""" PaintConstellation """

	def __init__(self, ax, color='red', show_names=False):
		""" PaintConstellation """
		self._ax = ax
		self._color = color
		self._cb = None
		self._p = []
		self._show_names = show_names
		self._cl = None
		self._t = []

	def change(self, value):
		""" change """
		if self._cb is None:
			self._cb = ConstellationBoundaries()
			if self._show_names:
				self._cl = ConstellationLocations()
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
			p = self._ax.plot(
				segment[0], segment[1],
				label='Constellation Boundary',
				color=self._color, alpha=0.75,
				linewidth=1, linestyle='dashed')
			self._p.append(p[0])
		if self._show_names:
			for constellation in self._cl.data.values():
				t = self._ax.text(constellation.ra_rad, constellation.dec_rad, constellation.name, rotation=45, color=self._color, alpha=1.0, clip_on=True)
				self._t.append(t)

	def _disable(self):
		""" _disable """
		if len(self._p) == 0:
			# nothimg painted
			return
		for p in self._p:
			p.remove()
		self._p = []
		for t in self._t:
			t.remove()
		self._t = []
