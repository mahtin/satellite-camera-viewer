""" static_tles """

from datetime import datetime, timezone, timedelta
from dataclasses import dataclass

@dataclass
class TLE:
    """ TLE """
    name: str = ''
    """ name - optional comment line naming the satellite if using TLE/3LE """
    line1: str = ''
    """ line1 - first line of 2LE, second line of TLE/3LE """
    line2: str = ''
    """ line2 - second line of 2LE, third line of TLE/3LE """

    def __str__(self):
        """ __str__ """
        return '[%s,%s,%s]' % (self.name, self.line1, self.line2)

    @property
    def as_array(self):
        """ as_array """
        return [self.name, self.line1, self.line2]

    @property
    def age(self):
        """ age - Extract the epoch string """

	# line1, chars 18-31 (0-indexed)
        epoch_str = self.line1[18:32].strip()

        # Parse the year and the day of the year (including fractional day)
        year_two_digit = int(epoch_str[:2])
        day_fraction = float(epoch_str[2:])

        # Determine the full 4-digit year (assumes post-1957 for space age)
        year = (1900 if year_two_digit >= 57 else 2000) + year_two_digit

        # Convert fractional day to hours, minutes, seconds
        total_seconds = day_fraction * 24 * 60 * 60
        days = int(total_seconds // (24 * 60 * 60))
        remainder = total_seconds % (24 * 60 * 60)
        hours = int(remainder // (60 * 60))
        remainder %= (60 * 60)
        minutes = int(remainder // 60)
        seconds = int(remainder % 60)

        # Create a datetime object for the epoch
        epoch_date = datetime(year, 1, 1, tzinfo=timezone.utc) + timedelta(days=days - 1, hours=hours, minutes=minutes, seconds=seconds)

        # Calculate the age
        tle_age = datetime.now(timezone.utc) - epoch_date

        return epoch_date, tle_age

# Define satellite orbit from TLE (these static values are for fallback reasons
# Make ISS the default (i.e. first position) - just because
static_tles = [
    TLE(
        'ISS (ZARYA)',
        '1 25544U 98067A   26146.19619863  .00012013  00000+0  22272-3 0  9996',
        '2 25544  51.6332  48.9673 0007420  99.1432 261.0396 15.49386458568346',
    ),
    TLE(
        'EWS-G2 (GOES 15)',
        '1 36411U 10008A   26146.16668523  .00000022  00000+0  00000+0 0  9992',
        '2 36411   1.2201  83.2277 0005079  32.1945 251.7589  1.00274994 59419',
    ),
    TLE(
        'ARKTIKA-M 2',
        '1 58584U 23198A   26144.33347125  .00000154  00000+0  00000+0 0  9996',
        '2 58584  63.2201 157.0242 6895752 267.5045  18.7884  2.00593321 17849',
    ),
    TLE(
        'LANDSAT 9',
        '1 49260U 21088A   26146.22223750  .00000335  00000+0  84282-4 0  9990',
        '2 49260  98.1857 216.7121 0001454  97.6294 262.5069 14.57116693247806',
    ),
    TLE(
        'CSS (TIANHE)',
        '1 48274U 21035A   26146.21496744  .00016782  00000+0  20616-3 0  9993',
        '2 48274  41.4680  95.6204 0010995 283.3018  76.6594 15.59835875289737',
    ),
    TLE(
        'HST',
        '1 20580U 90037B   26146.30085647  .00006627  00000+0  21072-3 0  9991',
        '2 20580  28.4732 230.1289 0001284 261.2187  98.8263 15.30494849785216',
    ),
]

def _main(args=None):
    """ _main """
    print('%-30s %-23s %30s' % ('Name', 'Epoch', 'Age'))
    for s in static_tles:
        epoch, age = s.age
        print('%-30s %23s %30s' % (s.name, epoch.strftime('%Y-%m-%d %H:%M:%S %Z'), age))

    print('')
    print(static_tles[0].as_array)

if __name__ == '__main__':
    _main()
