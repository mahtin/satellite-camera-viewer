"""
Constellation Boundaries 
"""

# https://watcheroftheskies.net/welcome.html (or https://pbarbier.com/ maybe)
# https://watcheroftheskies.net/constellations/boundaries.html
#
# Merged edges ...
# https://watcheroftheskies.net/constellations/lines_in_20.txt
#
# Bytes Format  Unit    Explanation
# 1-10  F10.7   hrs     Right ascension J2000 (decimal hours)
# 12    A1              Declination J2000 (sign)
# 13-21 F9.6    deg     Declination J2000 (decimal degrees)
# 23-29 A7              Segment key
#
#  0.1022250 -81.803966 559:560
#  0.1068476 +10.696028 673:672
# 16.5663214 -42.267474 612:628
# 23.4455593 -36.312778 510:517
#

import os
import math
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Line:
    """ Attitude """
    ra_deg: float = 0.0
    dec_deg: float = 0.0
    segment_key: str = None

class ConstellationBoundariesError(Exception):
    """ ConstellationBoundariesError """

class ConstellationBoundaries:
    """ ConstellationBoundaries """

    _NAME = 'lines_in_20.txt'
    _DIR_ConstellationBoundaries = '~/.cache/constellation-boundaries'

    def __init__(self, directory=None):
        """ ConstellationBoundaries """

        self._name = self._NAME

        if directory:
            self._directory = directory
        else:
            self._directory = os.getenv('CONSTELLATION_BOUNDARIES')
            if not self._directory:
                self._directory = self._DIR_ConstellationBoundaries
        self._directory = Path(self._directory).expanduser()
        self._directory.mkdir(parents=True, exist_ok=True)
        if not self._directory.exists():
            raise ConstellationBoundariesError('%s: directory does not exist' % (self._directory)) from None

        try:
            self._readfile()
        except FileNotFoundError:
            raise ConstellationBoundariesError('%s: file does not exist' % (self._filename)) from None
        except PermissionError:
            raise ConstellationBoundariesError('%s: permission error - file not readable' % (self._filename)) from None

    def _readfile(self):
        self._a = {}
        n_lines = 0
        with self._filename.open('r', encoding='utf-8') as fd:
            for line in fd:
                # no need to strip the line as we are very explcit about the line usage ...
                ra_deg = float(line[0:10]) * 15.0 - 180.0    # converted from hours to degrees
                dec_deg = float(line[11:21])
                segment_key = line[22:29]
                line = Line(ra_deg, dec_deg, segment_key)
                if segment_key in self._a:
                    self._a[segment_key].append(line)
                else:
                    self._a[segment_key] = [line]
        return n_lines

    @property
    def _filename(self):
        """ _filename() """

        return self._directory / self._name

    def data(self):
        """ data() """
        return self._a

    def data2plot(self):
        """ data2plot() """
        r = []
        for segment,lines in self._a.items():
            x = []
            y = []
            for line in lines:
                # print('[%7.3f,%7.3f] <%s>' % (line.ra_deg, line.dec_deg, line.segment_key))
                x.append(math.radians(line.ra_deg))
                y.append(math.radians(line.dec_deg))
            r.append((x,y))
        return r

def _main(args=None):
    """ _main """
    import sys
    import matplotlib.pyplot as plt

    try:
        cb = ConstellationBoundaries()
    except ConstellationBoundariesError as e:
        sys.exit(e)

    fig = plt.figure(figsize=(14, 7))
    fig.patch.set_linewidth(0)
    fig.tight_layout(pad=0.0, h_pad=0.0, w_pad=0.0)
    fig.set_layout_engine(layout='tight')
    fig.patch.set_facecolor('#ebebeb')
    ax = fig.add_subplot(111, projection='mollweide')
    ax.set_facecolor('whitesmoke')
    ax.grid(color='lightgrey', alpha=0.5)

    for segment in cb.data2plot():
        ax.plot(segment[0], segment[1], label='Constellation Boundary', color='lightblue', alpha=0.75, linewidth=1, linestyle='dashed')

    ax.grid(True)
    ax.set_title('Constellation Boundaries')
    plt.show()

if __name__ == '__main__':
    _main() 
