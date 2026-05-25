"""
Star - A class to store important values for a star.

"""

import math
from dataclasses import dataclass

@dataclass(frozen=True)
class Star:
	"""
	Star - A class to store important values for a star.

	:param number: Star catalog number (if known).
	:type number: int | None
	:param name: Star name (if known).
	:type name: str | None
	:param constellation: Star constellation name (if known).
	:type constellation: str | None
	:param ra: Star Right Ascension (RA) in radians.
	:type ra: float
	:param dec: Star Declination (DEC) in radians.
	:type dec: float
	:param mag: Star magnitude (if known).
	:type mag: float | None

	:return: Star class.
	:rtype: Star

	"""

	number: int|list[int] = None
	""" Star catalog number (if known). """
	name: str = None
	""" Star name (if known). """
	constellation: str = None
	""" Star constellation name (if known). """
	ra: float = math.nan
	""" Star Right Ascension (RA) in radians. """
	dec: float = math.nan
	""" Star Declination (DEC) in radians. """
	mag: float = math.nan
	""" Star magnitude (if known). """

	def __str__(self):
		""" __str__() """
		if isinstance(self.number, int):
			num = str(self.number)
		else:
			if self.number is not None:
				num = '-'.join([str(v) for v in self.number])
			else:
				num = ''

		if self.name is not None and self.constellation is not None and self.constellation != '':
			name = self.name + ' in ' + self.constellation
		else:
			name = self.name

		if self.ra is not None and not math.isnan(self.ra) or self.dec is not None and not math.isnan(self.dec):
			pos = '[%9.5f,%9.5f]' % (round(math.degrees(self.ra), 5), round(math.degrees(self.dec), 5))
		else:
			pos = '[%9s,%9s]' % ('', '')

		if self.mag is not None and not math.isnan(self.mag):
			mag = '%6.3f' % (self.mag)
		else:
			mag = ''

		if name is None or len(name) == 0:
			r = '%s @ %6s ; %6s' % (pos, mag, num)
		elif name[0] == '"' and name[-1] == '"':
			r = '%s @ %6s ; %6s %s' % (pos, mag, num, name)
		else:
			r = '%s @ %6s ; %6s %s' % (pos, mag, num, '"' + name + '"')

		return r

	def __call__(self):
		""" __call__ """
		return [self.number, self.name, self.constellation, self.ra, self.dec, self.mag]

def _main(args=None):
	""" _main """
	s = Star()
	print(s)
	s = Star(1, 'Twinkle', 'Lullaby', 0.0, 0.0, 1.0)
	print(s)
	s = Star([1,2,3], 'Little Star', 'Poem', 0.0, 0.0, 1.0)
	print(s)
	print(s())


if __name__ == '__main__':
	_main()
