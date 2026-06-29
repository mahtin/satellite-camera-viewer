"""
Constellation Locations
"""

import os
import math
from pathlib import Path
from dataclasses import dataclass

# constellation-locations.tsv
#
# Name                  IAU Abbr.       Center RA (h m s)       Center DEC (°)
# Andromeda             And             00h48m48s               +36d55m
# Antlia                Ant             10h16m00s               -35d16m

@dataclass
class ConstellationLocation:
    """ ConstellationLocation """
    name: str = None
    abbr: str = None
    ra_rad: float = 0.0
    dec_rad: float = 0.0

    def __str__(self):
        return '[%s [%6.2f,%6.2f] ; %s]' % (self.abbr, math.degrees(self.ra_rad), math.degrees(self.dec_rad), self.name)

class ConstellationLocationsError(Exception):
    """ ConstellationLocationsError """

class ConstellationLocations:
    """ ConstellationLocations """

    _NAME_ConstellationLocations = 'constellation-locations.tsv'
    _DIR_ConstellationLocations = '~/.cache/constellation-locations'

    def __init__(self, directory=None):
        """ ConstellationLocations """

        self._constellation_locations = self._NAME_ConstellationLocations

        if directory:
            self._directory = directory
        else:
            self._directory = os.getenv('CONSTELLATION_LOCATIONS')
            if not self._directory:
                self._directory = self._DIR_ConstellationLocations
        self._directory = Path(self._directory).expanduser()
        self._directory.mkdir(parents=True, exist_ok=True)
        if not self._directory.exists():
            raise ConstellationLocationsError('%s: directory does not exist' % (self._directory)) from None

        self._read()

    @property
    def _local_filename(self):
        """ _local_filename() """
        return self._directory / self._constellation_locations

    def _read(self):
        try:
            r = self._readfile()
            if r == 0:
                # a cheap way to continue to the network
                raise FileNotFoundError('zero length file') from None
            # we are successfully done!
            return
        except FileNotFoundError:
            # lets continue to the network section of the code and not throw an error
            pass
        except PermissionError:
            # hard to fix anything at this point - humans need to get involved
            raise ConstellationLocationsError('%s: permission error - file not readable' % (self._local_filename)) from None

        raise ConstellationLocationsError('network fetch not implemented') from None

    def _readfile(self):
        """ _readfile() """

        def _hms_to_degrees(s):
            """ _hms_to_degrees """
            return (int(s[0:0+2]) + int(s[3:3+2]) / 60.0 + int(s[6:6+2]) / 3600.0) * 15.0 - 180.0

        def _dm_to_degrees(s):
            """ _dm_to_degrees """
            return int(s[0:0+3]) + int(s[4:4+2]) / 60.0

        n_constellations = 0
        self._a = {}
        with self._local_filename.open('r', encoding='utf-8') as fd:
            for line in fd:
                n_constellations += 1
                if n_constellations <= 1:
                    # skip description line
                    continue
                items = [item for item in line.strip().split('\t') if item]
                # print(items)
                constellation = ConstellationLocation(items[0], items[1], math.radians(_hms_to_degrees(items[2])), math.radians(_dm_to_degrees(items[3])))
                self._a[constellation.abbr] = constellation
        return n_constellations

    @property
    def data(self):
        """ data() """
        return self._a

def _main(args=None):
    """ _main """
    import sys                       # pylint: disable=C0415
    import matplotlib.pyplot as plt  # pylint: disable=C0415

    try:
        cl = ConstellationLocations()
    except ConstellationLocationsError as e:
        sys.exit(e)
    except KeyboardInterrupt as e:
        sys.exit(e)

    fig = plt.figure(figsize=(14, 7))
    fig.patch.set_linewidth(0)
    fig.tight_layout(pad=0.0, h_pad=0.0, w_pad=0.0)
    fig.set_layout_engine(layout='tight')
    fig.patch.set_facecolor('#ebebeb')
    ax = fig.add_subplot(111, projection='mollweide')
    ax.set_title('Constellation Locations')
    ax.set_facecolor('whitesmoke')
    ax.grid(True)
    ax.grid(color='lightgrey', alpha=0.5)

    for constellation in cl.data.values():
        _ = ax.scatter(constellation.ra_rad, constellation.dec_rad, s=20, marker='*', color='red', alpha=0.5)
        _ = ax.text(constellation.ra_rad, constellation.dec_rad, constellation.name, rotation=45, color='red', alpha=0.5)

    plt.show()

if __name__ == '__main__':
    _main()
