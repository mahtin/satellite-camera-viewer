""" static_tles """

from datetime import datetime, timezone, timedelta
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
	'1 25544U 98067A   26144.19669721  .00007438  00000-0  14130-3 0  9992',
	'2 25544  51.6327  58.8652 0007496  92.3340 267.8507 15.49341091568031',
    ), # from https://live.ariss.org/iss.txt
    TLE(
        'GOES-15',
        '1 36411U          26143.85253292 +.00000000 +00000-0 +00000-0 0 00000',
        '2 36411   1.2141  83.2604 0004882  32.1672 136.3549  1.00274404    05',
    ),
    TLE(
        'ARKTIKA-M 2',
        '1 58584U          26143.33645041 +.00000000 +00000-0 +00000-0 0 00005',
        '2 58584  63.2255 157.1366 6895679 267.5005  18.7905  2.00593415    08',
    ),
    TLE(
        'LANDSAT 9',
        '1 49260U          26144.09348698 +.00000000 +00000-0 +48872-4 0 00001',
        '2 49260  98.1858 214.6197 0001464  97.9881 262.1484 14.57114581    03',
    ),
    TLE(
        'Tiangong',
	'1 48274U          26144.16609727 +.00000000 +00000-0 +16511-3 0 00000',
	'2 48274  41.4681 108.0715 0011114 271.1511  88.8054 15.59770572    00',
    ),
    TLE(
        'Hubble Space Telescope',
	'1 20580U          26143.56214551 +.00000000 +00000-0 +16332-3 0 00001',
	'2 20580  28.4737 248.8387 0001366 221.0087 139.0406 15.30462215    06',
    ),
]

def _main(args=None):
    """ _main """
    print('%-30s %-23s %30s' % ('Name', 'Epoch', 'Age'))
    for s in static_tles:
        epoch, age = s.age
        print('%-30s %23s %30s' % (s.name, epoch.strftime('%Y-%m-%d %H:%M:%S %Z'), age))

if __name__ == '__main__':
    _main()
