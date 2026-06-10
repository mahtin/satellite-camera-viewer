""" StarCatalog """

import math
import logging

class StarCatalog():
    """ StarCatalog """

    _known_catalogs = {}

    @classmethod
    def import_all(cls):
        """ import_all() """

        # Presently there are four catalogs supported - this is the name to class mapping:

        try:
            # BSC5P - The Yale Bright Star Catalog, 5th Edition
            from .catalog_bsc5 import CatalogBSC5             # pylint: disable=C0415
            cls._known_catalogs['BSC5'] = CatalogBSC5
        except ImportError:
            pass

        try:
            # HYG (Hipparcos, Yale, Gliese)
            from .catalog_hyg import CatalogHYG               # pylint: disable=C0415
            cls._known_catalogs['HYG'] = CatalogHYG
        except ImportError:
            pass

        try:
            # Smithsonian Astrophysical Observatory
            from .catalog_sao import CatalogSAO               # pylint: disable=C0415
            cls._known_catalogs['SAO'] = CatalogSAO
        except ImportError:
            pass

        try:
            # The Tycho-2 Catalogue of the 2.5 Million Brightest Stars
            from .catalog_tycho_2 import CatalogTycho_2       # pylint: disable=C0415
            cls._known_catalogs['Tycho-2'] = CatalogTycho_2
        except ImportError:
            pass

    log = None

    @classmethod
    def catalogs(cls):
        """ catalogs() """

        if len(cls._known_catalogs) == 0:
            cls.import_all()

        if len(cls._known_catalogs) == 0:
            raise ValueError('No Star Catalog imported') from None
        return list(sorted(cls._known_catalogs.keys()))

    @classmethod
    def catalog(cls, which):
        """ catalog() """

        return cls._known_catalogs[which]

    def __init__(self, which=None, max_mag=None, directory=None, force_reload=False,  use_database=False, debug=False):
        """ StarCatalog """

        self._debug = debug
        if self._debug:
            self.__class__.log.setLevel(logging.DEBUG)

        if len(self.__class__._known_catalogs) == 0:
            self.__class__.import_all()
        if which is None:
            which = self.__class__.catalogs()[0]

        try:
            self._catalog_class = self.__class__.catalog(which)
        except IndexError as exc:
            raise ValueError('Star Catalog unsupported') from exc

        self._stars = None

        self._max_mag = max_mag
        self._force_reload = force_reload
        self._directory = directory
        self._use_database = use_database

        self._catalog = self._catalog_class(self.__class__.log, max_mag=self._max_mag, directory=self._directory, force_reload=force_reload, use_database=self._use_database)

        # these methods need to be brought into class
        self.stars = self._catalog.stars
        self.name = self._catalog.name
        self.directory = self._catalog.directory

    def __call__(self):
        """ __call__() """

        return self.stars()

    def __len__(self):
        """ __len__() """

        return self._catalog.__len__()

    def __str__(self):
        """ __str__ """

        return self._catalog.__str__()

    def __repr__(self):
        """ __repr__ """

        return self._catalog.__repr__()

    def select_max_mag(self, mag):
        """ select_max_mag() """

        found_stars = []
        for star in self._catalog():
            if star.mag and star.mag <= mag:
                found_stars.append(star)
        return sorted(found_stars, key=lambda v: (v.ra, v.dec))

    def select_by_mag(self, mag):
        """ select_by_mag() """

        found_stars = []
        if mag < 0:
            for star in self.stars():
                if star.mag and star.mag > mag-1 and star.mag <= mag:
                    found_stars.append(star)
        else:
            for star in self._catalog():
                if star.mag and star.mag >= mag and star.mag < mag+1:
                    found_stars.append(star)
        return sorted(found_stars, key=lambda v: (v.ra, v.dec))

    def segment(self, ra_center, dec_center, ra_width, dec_width, max_mag=None):
        """ segment() """

        ra_center, dec_center = math.radians(ra_center), math.radians(dec_center)
        ra_width, dec_width = math.radians(ra_width), math.radians(dec_width)

        found_stars = []
        for star in self.stars():

            if max_mag and star.mag > max_mag:
                # the stars are sorted by magnitude; so we know we are done!
                break

            if star.mag and self._max_mag and star.mag > self._max_mag:
                # happens if stars are read in from database or pickle
                break

            if ra_center - ra_width/2 < 0:
                # counterclockwise from zero
                if star.ra < (ra_center - ra_width/2 + math.pi*2) and star.ra > (ra_center + ra_width/2):
                    ## print('????: ', ra_center - ra_width/2, star.ra, ra_center + ra_width/2)
                    continue
            elif ra_center + ra_width/2 >= math.pi*2:
                # clockwise from zero
                if star.ra < (ra_center - ra_width/2) and star.ra > (ra_center + ra_width/2 - math.pi*2):
                    continue
            else:
                if star.ra < (ra_center - ra_width/2) or star.ra > (ra_center + ra_width/2):
                    continue

            if star.dec < (dec_center - dec_width/2) or star.dec > (dec_center + dec_width/2):
                continue

            found_stars.append(star)
        return sorted(found_stars, key=lambda v: (v.ra, v.dec))
