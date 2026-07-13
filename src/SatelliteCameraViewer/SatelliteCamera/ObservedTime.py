"""
ObservedTime

ObservedTime model
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from astropy.time import Time

#
# ObservedTime - specifically allow for a single call to Astropy's Time() vs calling it way-too-many times.
#

@dataclass
class ObservedTime:
    """ ObservedTime """
    observed_time:datetime = None

    def __post_init__(self):
        """ ObservedTime """
        if self.observed_time is None:
            # default is 'now'
            self.observed_time = datetime.now(timezone.utc).replace(microsecond=0)
        self.t = Time(self.observed_time)

    @property
    def datetime(self):
        """ datetime """
        return self.observed_time

    @property
    def timestamp(self):
        """ timestamp """
        return self.observed_time.timestamp()

    def timedelta(self, seconds):
        """ timedelta """
        self.observed_time = self.observed_time + timedelta(seconds=seconds)
        self.t = Time(self.observed_time)

    def __str__(self):
        """ __str__ """
        return self.observed_time.strftime('%Y-%m-%d %H:%M:%S')
