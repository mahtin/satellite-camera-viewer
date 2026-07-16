""" StarCatalog """

import math
import glob
import gzip

from .star import Star
from .catalog import Catalog

# class name should be 'Catalog' following by the name of the catalog - this is used elsewhere

class CatalogTycho_2(Catalog):
    """ CatalogTycho_2()

    The Tycho-2 Catalogue of the 2.5 Million Brightest Stars
    https://www.astro.ku.dk/~erik/Tycho-2/
    http://cdsarc.u-strasbg.fr/ftp/pub/cats/i/259/ReadMe

    """

    base_url = 'http://cdsarc.u-strasbg.fr/ftp/pub/cats/i/259/'
    source_files = [
            'suppl_1.dat.gz',
            'suppl_2.dat.gz',
            'tyc2.dat.00.gz',
            'tyc2.dat.01.gz',
            'tyc2.dat.02.gz',
            'tyc2.dat.03.gz',
            'tyc2.dat.04.gz',
            'tyc2.dat.05.gz',
            'tyc2.dat.06.gz',
            'tyc2.dat.07.gz',
            'tyc2.dat.08.gz',
            'tyc2.dat.09.gz',
            'tyc2.dat.10.gz',
            'tyc2.dat.11.gz',
            'tyc2.dat.12.gz',
            'tyc2.dat.13.gz',
            'tyc2.dat.14.gz',
            'tyc2.dat.15.gz',
            'tyc2.dat.16.gz',
            'tyc2.dat.17.gz',
            'tyc2.dat.18.gz',
            'tyc2.dat.19.gz',
    ]

    def _readstarfile(self, directory, max_mag, star_append):
        """ _readstarfile() """

        n_lines = 0
        for filename in [directory / v for v in self.source_files]:
            if 'suppl_' in filename:
                # XXX TODO need to code up suppl files!
                continue
            n_lines_per_file = 0
            with gzip.open(filename, 'rt', encoding='utf-8') as fd:
                for line in fd.readlines():
                    n_lines_per_file += 1
                    a = line.rstrip().split('|')

                    #  1           1-  4  I4      ---     TYC1     [1,9537]+= TYC1 from TYC or GSC (1)
                    #              6- 10  I5      ---     TYC2     [1,12121]  TYC2 from TYC or GSC (1)
                    #         12  I1      ---     TYC3     [1,3]      TYC3 from TYC (1)
                    tyc = a[1-1].split(' ')

                    pflag, ramdeg, demdeg = a[2-1], a[3-1], a[4-1]
                    btmag, vtmag = a[18-1], a[20-1]
                    radeg, dedeg = a[25-1], a[26-1]
                    if pflag in ['P', 'X']:
                        # ' ' = normal mean position and proper motion.
                        # 'P' = Close double stars resolved in Tycho-2, but the epoch 2000 mean
                        #       position, proper motion, etc., refer to the photo-centre of the
                        #       two Tycho-2 entries, where the BT magnitudes were used in
                        #       weighting the positions.
                        # 'X' = stars, like Polaris, with no epoch 2000 mean position and no proper
                        #       motion.
                        pass
                    if ramdeg == '            ' or demdeg == '            ':
                        ramdeg = radeg
                        demdeg = dedeg

                    try:
                        tyc_i = [int(v) for v in tyc]
                    except ValueError as e:
                        # self.__class__.log.debug('%s %s: %s' % (type(e).__name__, e, tyc))
                        continue

                    try:
                        ra_f = float(ramdeg)
                        dec_f = float(demdeg)
                    except ValueError as e:
                        # self.__class__.log.debug('%s %s: %s' % (type(e).__name__, e, ramdeg, demdeg))
                        ra_f = float('nan')
                        dec_f = float('nan')

                    try:
                        vtmag_f = float(vtmag)
                        if max_mag and vtmag_f >= max_mag:
                            continue
                    except ValueError as e:
                        # self.__class__.log.debug('%s %s: %s' % (type(e).__name__, e, vtmag))
                        if max_mag:
                            continue
                        vtmag_f = float('nan')

                    star_append(Star(tyc_i, None, None, math.radians(ra_f), math.radians(dec_f), vtmag_f))

            n_lines += n_lines_per_file
        return n_lines
