""" static_tles """

from dataclasses import dataclass

@dataclass
class TLE:
    """ TLE """
    name: str = ''
    line1: str = ''
    line2: str = ''

    def __str__(self):
        return '[%s,%s,%s]' % (self.name, self.line1, self.line2)

    @property
    def as_array(self):
        return [self.name, self.line1, self.line2]

# Define satellite orbit from TLE (these static values are for fallback reasons
static_tles = [
    TLE(
        'GOES-15',
        '1 36411U          26143.85253292 +.00000000 +00000-0 +00000-0 0 00000',
        '2 36411   1.2141  83.2604 0004882  32.1672 136.3549  1.00274404    05'
    ),
    TLE(
        'ARKTIKA-M 2',
        '1 58584U          26143.33645041 +.00000000 +00000-0 +00000-0 0 00005',
        '2 58584  63.2255 157.1366 6895679 267.5005  18.7905  2.00593415    08'
    ),
    TLE(
        'LANDSAT 9',
        '1 49260U          26144.09348698 +.00000000 +00000-0 +48872-4 0 00001',
        '2 49260  98.1858 214.6197 0001464  97.9881 262.1484 14.57114581    03'
    ),
    TLE(
        'ISS (ZARYA)',
        '1 25544U 98067A   26132.19887560  .00004713  00000-0  93039-4 0  9991',
        '2 25544  51.6312 118.2489 0007476  49.7974 310.3668 15.49191856566178'
    ) # from https://live.ariss.org/iss.txt
]
