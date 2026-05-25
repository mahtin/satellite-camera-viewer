""" StarCatalog """

import math
import gzip

from .star import Star
from .catalog import Catalog

# class name should be "Catalog" following by the name of the catalog - this is used elsewhere

class CatalogBSC5(Catalog):
    """ CatalogBSC5()

    BSC5P
    The Yale Bright Star Catalog, 5th Edition
    http://tdc-www.harvard.edu/catalogs/bsc5.html
    https://heasarc.gsfc.nasa.gov/W3Browse/star-catalog/bsc5p.html

    """

    base_url = 'http://tdc-www.harvard.edu/catalogs/'
    source_files = [
        'bsc5.dat.gz',
    ]

    def _readstarfile(self, directory, max_mag, star_append):
        """ _readstarfile() """

        # by using a sorted (by mag) file, we can shorten the search
        # filename = 'BSC5/bsc5.dat'

        filename = directory / self.source_files[0]

        n_lines = 0
        with gzip.open(filename, 'rt', encoding='utf-8') as fd:
            for line in fd.readlines():
                n_lines += 1

                #   1-  4  I4     ---     HR       [1/9110]+ Harvard Revised Number
                #                                    = Bright Star Number
                try:
                    hr = int(line[0:4])
                except ValueError:
                    hr = None

                #   5- 14  A10    ---     Name     Name, generally Bayer and/or Flamsteed name
                name_star = line[4:11].strip()
                name_constellation = line[11:14].strip()
                if not name_constellation.isalpha():
                    name_star = line[4:14].strip()
                    name_constellation = None

                # 103-107  F5.2   mag     Vmag     ?Visual magnitude (1)
                try:
                    mag_f = float(line[102:107])
                    if max_mag and mag_f >= max_mag:
                        continue
                except ValueError as e:
                    # some stars do not have magnitudes
                    # self.__class__.log.debug(type(e).__name__, e, 'Mag:', line[102:107], 'Line:', line.rstrip())
                    if max_mag:
                        continue
                    mag_f = float('nan')

                #  76- 77  I2     h       RAh      ?Hours RA, equinox J2000, epoch 2000.0 (1)
                #  78- 79  I2     min     RAm      ?Minutes RA, equinox J2000, epoch 2000.0 (1)
                #  80- 83  F4.1   s       RAs      ?Seconds RA, equinox J2000, epoch 2000.0 (1)

                # Right ascension (hrs, mins, secs), equinox J2000, epoch 2000.0
                try:
                    ra_hrs, ra_min, ra_sec = [float(x) for x in (line[75:77], line[77:79], line[79:83])]
                    ra_f = math.radians((ra_hrs + ra_min/60.0 + ra_sec/3600.0) * 15.0)
                except ValueError as e:
                    # self.__class__.log.debug(type(e).__name__, e, 'RA:', line[75:77], ':', line[77:79], ':', line[79:83], 'Line:', line.rstrip())
                    ra_f = float('nan')

                #      84  A1     ---     DE-      ?Sign Dec, equinox J2000, epoch 2000.0 (1)
                #  85- 86  I2     deg     DEd      ?Degrees Dec, equinox J2000, epoch 2000.0 (1)
                #  87- 88  I2     arcmin  DEm      ?Minutes Dec, equinox J2000, epoch 2000.0 (1)
                #  89- 90  I2     arcsec  DEs      ?Seconds Dec, equinox J2000, epoch 2000.0 (1)

                # Declination (hrs, mins, secs), equinox J2000, epoch 2000.0
                try:
                    dec_deg, dec_min, dec_sec = [float(x) for x in (line[83:86], line[86:88], line[88:90])]
                    # NB in the Southern Hemisphere be careful to subtract the minutes and seconds from the (negative) degrees.
                    dec_sign = math.copysign(1, dec_deg)
                    dec_f = math.radians(dec_deg + dec_sign * dec_min/60.0 + dec_sign * dec_sec/3600.0)
                except ValueError as e:
                    # self.__class__.log.debug(type(e).__name__, e, 'DEC:', line[83:86], ':', line[86:88], ':', line[88:90], 'Line:', line.rstrip())
                    dec_f = float('nan')

                # Create a new Star object and add it to the list of stars
                star_append(Star(hr, name_star, name_constellation, ra_f, dec_f, mag_f))

        return n_lines
