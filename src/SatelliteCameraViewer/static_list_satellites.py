""" static_list_satellites """

from dataclasses import dataclass

# Define which satellite we keep setup for all runs of the program
# Make ISS the default (i.e. first position) - just because

@dataclass
class StaticListSatellite:
    """ StaticListSatellite """
    sat_id: int = None
    """ sat_id - Satellite ID """
    name: str = ''
    """ name - name of the satellite """

static_list_satellites = [
        StaticListSatellite(25544, 'ISS (ZARYA)'),
        StaticListSatellite(36411, 'EWS-G2 (GOES 15)'),
        StaticListSatellite(58584, 'ARKTIKA-M 2'),
        StaticListSatellite(49260, 'LANDSAT 9'),
        StaticListSatellite(48274, 'CSS (TIANHE)'),
        StaticListSatellite(20580, 'HST'),
]
