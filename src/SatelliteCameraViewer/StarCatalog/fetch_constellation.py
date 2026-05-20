""" fetch_constellation """
# https://en.wikipedia.org/wiki/List_of_stars_in_Ursa_Major
# List of stars in Ursa Major
# This is the list of notable stars in the constellation Ursa Major, sorted by decreasing brightness.

import re
import sys
import math
from pathlib import Path

from .star import Star

#
# This code used the HD numbering scheme. HIP is dropped (becuase)
# HD (Henry Draper)
# HIP (Hipparcos)
#

class FetchConstellationError(Exception):
	""" FetchConstellationError """

class FetchConstellation:
	""" FetchConstellation """

	# This should not be a built-in value; however, it is for now
	MIN_VISIBILITY = 4.0

	def __init__(self, name, min_visibility=None):
		""" FetchConstellation """

		self._name = name
		if min_visibility:
			self._min_visibility = min_visibility
		else:
			self._min_visibility = FetchConstellation.MIN_VISIBILITY
		self._path = Path('data/constellation/%s.txt' % (name))
		if not self._path.is_file():
			raise FetchConstellationError(self._name) from None
		self._s = None

	def name(self):
		""" name """
		if not self._s:
			self._read()
		return self._name

	def stars(self):
		""" stars """
		if not self._s:
			self._read()
		return self._s

	def _read(self):
		""" _read """
		try:
			fd = self._path.open(encoding='utf-8')
		except (FileNotFoundError,PermissionError):
			raise FetchConstellationError(self._path) from None
		self._s = []
		for l in fd.readlines():
			if len(l) == 0 or '#' == l[0] or 'Name' == l[0:4]:
				# blank line, comment, or title line - skip
				continue
			star = self._decode_line(l)
			if star:
				self._s.append(star)
		# descending brightless - as magniture is negative there's no - here
		self._s.sort(key=lambda v: v.mag)

	#
	# Name    B       F       Var     HD      HIP     RA      Dec     vis. mag.       abs. mag.       Dist. (ly)      Sp. class       Notes
	#
	def _decode_line(self, l):
		""" _decode_line """
		# empty fields have nothing in them - this fixes that
		while '\t\t' in l:
			l = l.replace('\t\t', '\t-\t')
		if '\u2212' in l:
			# becuase copying from webpages sometimes exposes special characters
			# U+2212 Minus Sign
			l = l.replace('\u2212', '-')
		v = l.split('\t')
		star_name = v[0]
		if len(v[0]) > 0:
			star_name = v[0]
		else:
			star_name = None

		try:
			if v[4][-1].isalpha():
				# binary star etc - so strip it for now
				star_hd = int(v[4][0:-1])
			else:
				star_hd = int(v[4])
		except ValueError:
			star_hd = None
		# 12h 54m 01.63s	+55° 57′ 35.4″
		# 05h 14m 32.27s	−08° 12′ 05.9″
		# degree symbol - ascii decimal 176, '\xb0', or '\u00b0', ditto for ′ and ″ (vs ' and ")
		h, m, s, _ = re.split(r'[hms]', v[6])
		ra = math.radians((float(h) + float(m)/60.0 + float(s)/3600.0)/24.0*360.0)
		d, m, s, _ = re.split(r'[°′″]', v[7])
		dec = math.radians(float(d) + float(m)/60.0 + float(s)/3600.0)
		try:
			vis_mag = float(v[8])
		except ValueError:
			vis_mag = math.nan
		if math.isnan(vis_mag) or vis_mag > self._min_visibility:
			return None
		return Star(star_hd, star_name, self._name, ra, dec, vis_mag)

def _main():
	""" _main() """
	if len(sys.argv) > 1:
		c = FetchConstellation(sys.argv[1])
		stars = c.stars()
		print('%s: %d' % (c.name(), len(stars)))
		print('%s' % ('\n'.join(['\t' + str(v) for v in stars])))
		print('')
	else:
		for name in ['Ursa Minor', 'Ursa Major', 'Gemini', 'Orion']:
			c = FetchConstellation(name)
			stars = c.stars()
			print('%s: %d' % (c.name(), len(stars)))
			print('%s' % ('\n'.join(['\t' + str(v) for v in stars])))
			print('')

if __name__ == '__main__':
	_main()
