""" Constellation """

from dataclasses import dataclass

@dataclass(frozen=True)
class Constellation:
	""" Constellation """
	constellation: str
	iau_abbreviations: str
	nasa_abbreviations: str
	genitive: str
	origin: str
	meaning: str
	brightest_star_name: str
	brightest_star_vis_mag: str

	def __str__(self):
		""" __str__() """

		return '%s (%s,%s) %s | %s ; %s' % (self.constellation, self.iau_abbreviations, self.nasa_abbreviations, self.genitive, self.meaning, self.origin)
