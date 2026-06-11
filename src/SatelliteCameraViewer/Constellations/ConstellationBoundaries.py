"""
Constellation Boundaries
"""

# https://watcheroftheskies.net/welcome.html (or https://pbarbier.com/ maybe)
# https://watcheroftheskies.net/constellations/boundaries.html
#
# Interpolated merged edges (J2000, dec) ...
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
# See https://watcheroftheskies.net/constellations/9N.pdf for Orion map
#

import os
import math
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass

import requests

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

    _BASE_URL = 'https://watcheroftheskies.net/constellations'

    _NAME_J2000_BOUNDARIES = 'bound_in_20.txt'             # Interpolated boundaries (J2000, ccw, dec)
    _NAME_J2000_MERGED_EDGES = 'lines_in_20.txt'           # Interpolated merged edges (J2000, dec)
    _NAME_J2000_CONSTELLATION_CENTERS = 'centers_20.txt'   # Constellation centers (J2000, dec)

    _DIR_ConstellationBoundaries = '~/.cache/constellation-boundaries'

    def __init__(self, directory=None):
        """ ConstellationBoundaries """

        self._base_url = self._BASE_URL

        # we only process one of the image files on that website for now
        self._j2000_merged_edges = self._NAME_J2000_MERGED_EDGES

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

        self._read()

    def _read(self):
        """ _read() """
        # first pass - just try the local file - mostly successful after first run
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
            raise ConstellationBoundariesError('%s: permission error - file not readable' % (self._local_filename)) from None

        # second pass - go out to network and fetch contents
        try:
            r1 = self._network_fetch()
        except requests.exceptions.ConnectionError as e:
            # classic can't connect issue
            self._local_filename.unlink(missing_ok=True)
            try:
                root_os_error = e.args[0].reason.args[0]
            except (AttributeError, IndexError):
                root_os_error = e
            raise ConstellationBoundariesError('HTTP Error %s: %s' % (root_os_error, self._url)) from None
        except requests.exceptions.HTTPError as e:
            # this would be something like a 404 (Not Found) or 406 (Not Acceptable) response
            self._local_filename.unlink(missing_ok=True)
            if 400 <= e.response.status_code < 500:
                raise ConstellationBoundariesError('HTTP Client Error %d: %s' % (e.response.status_code, self._url)) from None
            raise ConstellationBoundariesError('HTTP Server Error %d: %s' % (e.response.status_code, self._url)) from None
        except requests.exceptions.RequestException:
            # something else happened - not great!
            self._local_filename.unlink(missing_ok=True)
            # let it pass up - it could be important to see what happened
            raise

        # a special case cleanup for network code - if a zero length result is returned
        if r1 == 0:
            # could happen - better clean up - just in case
            self._local_filename.unlink(missing_ok=True)
            raise ConstellationBoundariesError('network fetch zero length file') from None

        # third pass - back to the local file as-created by network code
        try:
            r2 = self._readfile()
        except FileNotFoundError:
            raise ConstellationBoundariesError('%s: file does not exist' % (self._local_filename)) from None

        # a sanity check to confirm that the network and the local file agree (in the simplest possible way)
        if r1 != r2:
            raise ConstellationBoundariesError('inconsistent length file') from None

        # we are successfully done!

    def _readfile(self):
        """ _readfile() """
        self._a = {}
        n_bytes = 0
        with self._local_filename.open('r', encoding='utf-8') as fd:
            for line in fd:
                n_bytes += len(line)
                # no need to strip the line as we are very explcit about the line usage ...
                ra_deg = float(line[0:10]) * 15.0            # converted from hours to degrees
                dec_deg = float(line[11:21])
                segment_key = line[22:29]
                line = Line(ra_deg, dec_deg, segment_key)
                if segment_key in self._a:
                    self._a[segment_key].append(line)
                else:
                    self._a[segment_key] = [line]
        return n_bytes

    def _network_fetch(self):
        """ _network_fetch() """
        headers = {
            # required to make website respond cleanly
            'Accept-Encoding': 'text/plain',
            'Referer': 'https://google.com/',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
        }
        response = requests.get(self._url, headers=headers, stream=True, timeout=20)
        response.raise_for_status()
        # partial network success at this point
        n_bytes = 0
        with self._local_filename.open('wb') as fd:
            for chunk in response.iter_content(chunk_size=32*1024):
                if chunk:
                    fd.write(chunk)
                    n_bytes += len(chunk)
            # total network success at this point

        # we should try to date the file correctly (do this after the file is closed above)
        try:
            # should be "Last-Modified: Mon, 31 Jan 2000 12:00:00 EST" style if headers are correct
            last_modified = response.headers['Last-Modified']
            last_modified_dt = datetime.strptime(last_modified, "%a, %d %b %Y %H:%M:%S %Z")
            last_modified_ts = int(last_modified_dt.timestamp())
            # change both atime and mtime on file
            os.utime(self._local_filename, (last_modified_ts, last_modified_ts))
        except (IndexError, ValueError):
            # if the header is missing, or badly formatted, we just continue
            pass

        # total network success and hopefully timestamp success at this point
        return n_bytes

    @property
    def _local_filename(self):
        """ _local_filename() """
        return self._directory / self._j2000_merged_edges

    @property
    def _url(self):
        """ _url() """
        return self._base_url + '/' + self._j2000_merged_edges

    def data(self):
        """ data() """
        return self._a

    def data2plot(self):
        """ data2plot() """
        r = []

        # TODO - remove this and move to main code - plus use numpy
        def ra_fix(ra_rad):
            """ ra_fix """
            return -((ra_rad + math.pi) % (2 * math.pi) - math.pi)      # shift to [-pi, pi]

        for lines in self._a.values():
            x = []
            y = []
            for line in lines:
                x.append(ra_fix(math.radians(line.ra_deg)))
                y.append(math.radians(line.dec_deg))
            r.append((x,y))
        return r

def _main(args=None):
    """ _main """
    import sys                       # pylint: disable=C0415
    import matplotlib.pyplot as plt  # pylint: disable=C0415

    try:
        cb = ConstellationBoundaries()
    except ConstellationBoundariesError as e:
        sys.exit(e)
    except KeyboardInterrupt as e:
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
