""" StarCatalog """

import math
import gzip

from .star import Star
from .catalog import Catalog

# class name should be "Catalog" following by the name of the catalog - this is used elsewhere

class CatalogSAO(Catalog):
    """ CatalogSAO()

    Smithsonian Astrophysical Observatory
    https://heasarc.gsfc.nasa.gov/W3Browse/star-catalog/sao.html
    http://tdc-www.harvard.edu/catalogs/sao.html

    """

    base_url = 'https://heasarc.gsfc.nasa.gov/FTP/heasarc/dbase/dump/'
    source_files = [
        'heasarc_sao.tdat.gz',
    ]

    def _readstarfile(self, directory, max_mag, star_append):
        """ _readstarfile() """

        filename = directory / self.source_files[0]

        # <HEADER>
        # ...
        # field[name] = char10  [meta.id;meta.main] (index) // SAO Catalog Designation
        # field[ra] = float8:.6f_degree [pos.eq.ra;meta.main] (key) // Right Ascension
        # field[proper_motion_ra] = float8:7.4f_arcsec/yr [pos.pm;pos.eq.ra]  // Annual RA Proper Motion (FK4 System)
        # field[proper_motion_ra_error] = int1:2d_mas/yr [stat.error;pos.pm;pos.eq.ra]  // Standard Deviation in RA Proper Motion (FK4 System)
        # field[ra_epoch] = float8:6.1f_yr [time.start;obs]  // RA Original Epoch
        # field[dec] = float8:.6f_degree [pos.eq.dec;meta.main] (key) // Declination
        # field[proper_motion_dec] = float8:6.3f_arcsec/yr [pos.pm;pos.eq.dec]  // Annual Declination Proper Motion (FK4 System)
        # field[proper_motion_dec_error] = int1:2d_mas/yr [stat.error;pos.pm;pos.eq.dec]  // Standard Deviation of Declination Proper Motion (FK4 System)
        # field[dec_epoch] = float8:6.1f_yr [time.start;obs]  // Declination Original Epoch
        # field[position_error] = float8:4.2f_arcsec [stat.error;pos]  // Standard Deviation of Position at Epoch 1950.0
        # field[lii] = float8:.6f_degree [pos.galactic.lon] (index) // Galactic Longitude
        # field[bii] = float8:.6f_degree [pos.galactic.lat] (index) // Galactic Latitude
        # field[pg_mag] = float8:4.1f  [phot.mag;em.opt] (index) // Photographic Magnitude
        # field[vmag] = float8:4.1f  [phot.mag;em.opt.V] (index) // Visual Magnitude
        # ...
        # <DATA>
        # SAO 258660|218.82525833|-0.1169|3|1903.6|-89.771625|-0.004|2|1903|0.13|303.04406295|-26.92288489||6.6|M0|14|3|0|1|0|0|70|17838|CP-89   37|110994|0|17838|-0.3021|-0.003|2700|
        # SAO 258546|130.4839375|0.0507|9|1904|-89.46084444|-0.025|9|1903.7|0.42|302.3963721|-26.8772436||7.5|K2|14|3|0|1|0|0|70|13496|CP-88   95|90105|0|13496|0.0294|-0.024|2620|

        n_lines = 0
        in_data_section = False
        with gzip.open(filename, 'rt', encoding='utf-8') as fd:
            for line in fd.readlines():
                line = line.rstrip()
                if not in_data_section:
                    if '<DATA>' == line:
                        in_data_section = True
                    continue
                if '<HEADER>' == line:
                    in_data_section = False
                    continue
                if '<END>' == line:
                    break
                n_lines += 1
                a = line.split('|')
                name = a[1-1]
                hd = int(name[4:])
                ra = a[2-1]
                dec = a[6-1]
                vmag = a[14-1]

                try:
                    hd = int(hd)
                except ValueError:
                    hd = None

                try:
                    ra_hrs, ra_min, ra_sec = [float(x) for x in (ra[0:2], ra[3:5], ra[6:])]
                    ra_f = math.radians((ra_hrs + ra_min/60.0 + ra_sec/3600.0) * 15.0)
                except ValueError as e:
                    # self.__class__.log.debug(type(e).__name__, e, 'RA:', ra[0:2], line[3:5], line[6:], 'Line:', line.rstrip())
                    ra_f = float('nan')

                try:
                    dec_deg, dec_min, dec_sec = [float(x) for x in (dec[0:3], dec[4:6], dec[7:])]
                    # NB in the Southern Hemisphere be careful to subtract the minutes and seconds from the (negative) degrees.
                    dec_sign = math.copysign(1, dec_deg)
                    dec_f = math.radians(dec_deg + dec_sign * dec_min/60.0 + dec_sign * dec_sec/3600.0)
                except ValueError as e:
                    # self.__class__.log.debug(type(e).__name__, e, 'DEC:', dec[0:3], dec[4:6], dec[7:], 'Line:', line.rstrip())
                    dec_f = float('nan')

                try:
                    mag_f = float(vmag)
                    if max_mag and mag_f >= max_mag:
                        continue
                except ValueError as e:
                    # some stars do not have magnitudes
                    # self.__class__.log.debug(type(e).__name__, e, 'Mag:', vmag, 'Line:', line.rstrip())
                    if max_mag:
                        continue
                    mag_f = float('nan')

                star_append(Star(hd, None, None, ra_f, dec_f, mag_f))

        return n_lines
