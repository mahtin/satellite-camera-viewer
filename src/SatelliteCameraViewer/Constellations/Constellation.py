""" Constellation """

from dataclasses import dataclass

@dataclass(frozen=True)
class Constellation:
    """ Constellation """
    constellation: str = None
    iau_abbreviations: str = None
    nasa_abbreviations: str = None
    genitive: str = None
    origin: str = None
    meaning: str = None
    brightest_star_name: str = None
    brightest_star_vis_mag: str = None

    def __str__(self):
        """ __str__() """

        return '%s (%s,%s) %s | %s ; %s' % (self.constellation, self.iau_abbreviations, self.nasa_abbreviations, self.genitive, self.meaning, self.origin)
