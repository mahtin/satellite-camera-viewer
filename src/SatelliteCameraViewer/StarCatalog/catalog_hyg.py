""" StarCatalog """

import math

from .star import Star
from .catalog import Catalog

# class name should be 'Catalog' following by the name of the catalog - this is used elsewhere

class CatalogHYG(Catalog):
    """ CatalogHYG()

    HYG (Hipparcos, Yale, Gliese)
    http://www.astronexus.com/hyg
    https://github.com/astronexus/HYG-Database

    """

    # base_url = 'https://github.com/astronexus/HYG-Database/' + 'raw/master/hyg/v3/'
    base_url = 'https://github.com/astronexus/HYG-Database/' + 'raw/main/hyg/CURRENT/'
    source_files = [
        # 'hyg_v37.csv',
        'hygdata_v41.csv'
    ]

    def _readstarfile(self, directory, max_mag, star_append):
        """ _readstarfile() """

        filename = directory / self.source_files[0]

        # "id","hip","hd","hr","gl","bf","proper","ra","dec","dist","pmra","pmdec","rv","mag", ...
        # 0,,,,"","",Sol,0.0,0.0,0.0,0.0,0.0,0.0,-26.7, ...
        # 1,1,224700,,"","","",0.00006,1.089009,219.7802,-5.2,-1.88,0.0, ...
        # 2,2,224690,,"","","",0.000283,-19.49884,47.9616,181.21,-0.93,0.0, ...

        n_lines = 0
        with open(filename, 'r', encoding='utf-8') as fd:
            for line in fd.readlines():
                n_lines += 1
                if n_lines == 1:
                    continue
                # This CSV file does not have quotes - so we we can do this quickly
                a = line.rstrip().split(',')
                proper = a[7-1]
                if proper == 'Sol':
                    continue
                hip = a[3-1]
                ra = a[8-1]
                dec = a[9-1]
                mag = a[14-1]

                try:
                    hip = int(hip)
                except ValueError:
                    hip = None

                if len(proper) > 2 and proper[0] == '"' and proper[-1] == '"':
                    proper = proper[1:-1]
                if len(proper) == 0:
                    proper = None

                try:
                    ra_f = math.radians(float(ra)*15)
                except ValueError:
                    ra_f = float('nan')

                try:
                    dec_f = math.radians(float(dec))
                except ValueError:
                    dec_f = float('nan')

                try:
                    mag_f = float(mag)
                    if max_mag and mag_f >= max_mag:
                        continue
                except ValueError:
                    mag_f = float('nan')

                star_append(Star(hip, proper, None, ra_f, dec_f, mag_f))

        return n_lines
