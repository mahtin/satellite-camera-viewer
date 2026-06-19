""" PrecomputedCatalog """

#;Spel-UChile

import os
import sys
import math

from .StarCatalog.star import Star

class SpelUChileStars:
	""" SpelUChileStars """

	_stars_ra_rad = []
	_stars_dec_rad = []
	_stars_size_pixels = []

	def __init__(self):
		""" SpelUChileStars """
		self._pc = PrecomputedCatalog(pattern=None)
		# XXX TODO not correct

class PrecomputedCatalog:
	""" PrecomputedCatalog """

	_CATALOG_DIR = './../RPI/Catalog'

	_precompute_cats = [
		'cat_RA_0_DEC_-90',
		'cat_RA_0_DEC_-60', 'cat_RA_0_DEC_-30', 'cat_RA_0_DEC_0', 'cat_RA_0_DEC_30', 'cat_RA_0_DEC_60',
		'cat_RA_0_DEC_90',
		'cat_RA_30_DEC_-60', 'cat_RA_30_DEC_-30', 'cat_RA_30_DEC_0', 'cat_RA_30_DEC_30', 'cat_RA_30_DEC_60',
		'cat_RA_60_DEC_-60', 'cat_RA_60_DEC_-30', 'cat_RA_60_DEC_0', 'cat_RA_60_DEC_30', 'cat_RA_60_DEC_60',
		'cat_RA_90_DEC_-60', 'cat_RA_90_DEC_-30', 'cat_RA_90_DEC_0', 'cat_RA_90_DEC_30', 'cat_RA_90_DEC_60',
		'cat_RA_120_DEC_-60', 'cat_RA_120_DEC_-30', 'cat_RA_120_DEC_0', 'cat_RA_120_DEC_30', 'cat_RA_120_DEC_60',
		'cat_RA_150_DEC_-60', 'cat_RA_150_DEC_-30', 'cat_RA_150_DEC_0', 'cat_RA_150_DEC_30', 'cat_RA_150_DEC_60',
		'cat_RA_180_DEC_-60', 'cat_RA_180_DEC_-30', 'cat_RA_180_DEC_0', 'cat_RA_180_DEC_30', 'cat_RA_180_DEC_60',
		'cat_RA_210_DEC_-60', 'cat_RA_210_DEC_-30', 'cat_RA_210_DEC_0', 'cat_RA_210_DEC_30', 'cat_RA_210_DEC_60',
		'cat_RA_240_DEC_-60', 'cat_RA_240_DEC_-30', 'cat_RA_240_DEC_0', 'cat_RA_240_DEC_30', 'cat_RA_240_DEC_60',
		'cat_RA_270_DEC_-60', 'cat_RA_270_DEC_-30', 'cat_RA_270_DEC_0', 'cat_RA_270_DEC_30', 'cat_RA_270_DEC_60',
		'cat_RA_300_DEC_-60', 'cat_RA_300_DEC_-30', 'cat_RA_300_DEC_0', 'cat_RA_300_DEC_30', 'cat_RA_300_DEC_60',
		'cat_RA_330_DEC_-60', 'cat_RA_330_DEC_-30', 'cat_RA_330_DEC_0', 'cat_RA_330_DEC_30', 'cat_RA_330_DEC_60',
	]

	def __init__(self, pattern=None, collection='Normal'):
		""" PrecomputedCatalog """

		self._collection = collection
		if pattern is None or pattern == '':
			self._all_found = self._find_stars_by_list()
		else:
			self._all_found = self._find_stars_by_search(pattern)

	def _find_stars_by_search(self, pattern):
		""" find_stars_by_search """
		directory_path = self._CATALOG_DIR + '/' + self._collection

		all_found = {}
		for file_name in os.listdir(directory_path):
			if file_name not in pattern:
				continue
			# decode file using format: cat_RA_130_DEC_60
			_, _, file_ra, _, file_dec = file_name.split('_')
			file_ra = int(file_ra)
			file_dec = int(file_dec)
			file_path = '%s/cat_RA_%d_DEC_%d' % (directory_path, file_ra, file_dec)
			with open(file_path, encoding='utf-8') as fd:
				# The file contains four numbers per line:
				# 109.20750 -67.95722 3.98 511
				# RA DEC MAG REF#
				star_list = []
				for line in fd:
					v = [float(x) for x in line.split()]
					star_list.append(Star(int(v[3]), None, None, math.radians(v[0]), math.radians(v[1]), v[2]))
			all_found[(file_ra, file_dec)] = star_list
		# return list bucketed by file RA/DEC
		return all_found

	def _find_stars_by_list(self):
		""" _find_stars_by_list """
		pc = self._find_stars_by_search(self._precompute_cats)
		# uniq the stars ...
		all_found = {}
		for v in pc.stars.values():
			for star in v:
				if star in all_stars:
					continue
				all_found[star] = star
		# return list bucketed by 0/0
		return {(0,0): all_found}

	def _find_radec_mag(self):
		""" _find_radec_mag """

		ra_rad = []
		dec_rad = []
		size_pixels = []
		for star in all_stars.keys():
			ra_rad.append(star.ra)
			dec_rad.append(star.dec)
			size_pixels.append(mag_map(star.mag))
		# ra_rad = ra_fix(ra_rad)

		return ra_rad, dec_rad, size_pixels

	@property
	def collections(self):
		""" collections """
		return self._all_found.keys()

	@property
	def stars(self):
		""" stars """
		return self._all_found

def _main(args=None):
	""" _main """

	if args is None:
		args = sys.argv[1:]

	p = PrecomputedCatalog(args)
	print('')
	print(list(sorted(p.collections)))
	print('')
	for k,v in p.stars.items():
		print(k)
		print('\t', v)
	print('')

if __name__ == '__main__':
	_main()
