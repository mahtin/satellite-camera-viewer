""" StarCatalog """

import os
import time
from pathlib import Path
import hmac
import hashlib
import pickle
import sqlite3
import requests

from .star import Star
from .user_agent import user_agent

# Used by each catalog class - the class only needs to provide a _readstarfile() method

class CatalogError(Exception):
    """ CatalogError() """

class Catalog():
    """ Catalog() """

    # Yeah, yeah, yeah, this "known key" isn't optimal - but it's fit for purpose here.
    # We are only protecting from corupt file systems - which isn't really a thing anymore.
    _NOT_REALLY_A_SECRET_KEY = b'c351e1e1-4e9b-45f8-bf74-b08f5f13e9a9'

    log = None

    # all star catalogs live here:
    _DIR_STAR_CATALOG = '~/.cache/star-catalog'

    base_url = None
    source_files = None

    def __init__(self, log, max_mag=None, directory=None, force_reload=False,  use_database=False):
        """ GenericStarCatalog() """

        self.__class__.log = log

        self._name = self.__class__.__name__.replace('_', '-').replace('Catalog','')
        self._max_mag = max_mag
        self._force_reload = force_reload
        self._use_database = use_database

        if directory:
            self._directory = directory
        else:
            self._directory = os.getenv('STAR_CATALOG')
            if not self._directory:
                self._directory = Path(self._DIR_STAR_CATALOG).expanduser()

        if not os.path.exists(self._directory):
            raise CatalogError(self._directory) from None
        if not os.path.exists(self.directory()):
            os.mkdir(self.directory())

        self._key = self._NOT_REALLY_A_SECRET_KEY
        self._db = None
        self._stars = None

    def __len__(self):
        """ __len__() """

        if not self._stars:
            self._load_stars()
        return len(self._stars)

    def __call__(self):
        """ __call__ """

        if not self._stars:
            self._load_stars()
        return self.stars()

    def __str__(self):
        """ __str__ """

        if not self._stars:
            self._load_stars()
        return '[Star Catalog %s: length=%d]' % (self.name(), len(self))

    def __repr__(self):
        """ __repr__() """

        if not self._stars:
            self._load_stars()
        return '[Star Catalog %s: length=%d from %s]' % (self.name(), len(self), self.directory())

    def stars(self):
        """ stars() """

        if not self._stars:
            self._load_stars()
        return self._stars

    def name(self):
        """ name() """

        return self._name

    def directory(self):
        """ directory() """

        if not self._directory:
            raise CatalogError(self._directory) from None

        return self._directory / self._name

    def _star_set(self, v=None):
        """ _star_set() """

        # set/clear the star database
        if v:
            self._stars = v
        else:
            self._stars = []

    def _star_append(self, star):
        """ _star_append() """

        # append to the star database
        self._stars.append(star)

    def _load_stars(self):
        """ _read() """

        if not self._force_reload and not self._files_exist():
            self._force_reload = True

        if self._force_reload:
            _ = self._prime_from_files()

        # read the stars
        if self._use_database:
            if self._force_reload:
                l = self._database_open(fresh=True)
            else:
                l = self._database_open()
            if l is not None and l > 0:
                self._database_read()
            else:
                _ = self._prime_from_files(dont_pickle=True)
                self._database_write()
        else:
            _ = self._prime_from_files()
        self.__class__.log.info('%s opened from %s, %s records found', self.name(), self.directory(), format(len(self), ','))

    def _prime_from_web(self):
        """ _prime_from_web() """

        if not self.base_url or not self.source_files:
            raise NotImplementedError from None

        for filename in self.source_files:
            url = self.base_url + filename
            self.__class__.log.debug('start download url=%s, file=%s' % (url, filename))
            # The header is set to stop the file be un-gzipped in transfer
            headers = {
                'Accept-Encoding': 'identity',
                'User-Agent': user_agent(),
            }
            try:
                response = requests.get(url, headers=headers, stream=True)
            except Exception as e:
                self.__class__.log.debug('web requests() failed e=%s' % (e))
                continue
            try:
                n_bytes = 0
                file_path = self.directory() / filename
                with open(file_path, 'wb') as fd:
                    # this method will stop requests() from un-gzipping the contents!
                    for chunk in response.iter_content(chunk_size=16*1024):
                        fd.write(chunk)
                        n_bytes += len(chunk)
            except FileNotFoundError:
                self.__class__.log.debug('file save failed, file=%s' % (file_path))
                continue
            self.__class__.log.debug('download complete, file=%s, len=%d' % (file_path, n_bytes))

    def _files_exist(self):
        """ _files_exist() """

        for filename in self.source_files:
            if not os.path.exists(self.directory() / filename):
                return False
        return True

    def _files_age(self, suffix):
        """ _files_age() """

        filename = (self.directory() / self.name().lower()).with_suffix(suffix)
        try:
            age = int(time.time() - os.stat(filename).st_mtime)
        except:
            return None
        return age

    def _prime_from_files(self, dont_pickle=False):
        """ _prime_from_files() """

        if not self._force_reload:
            try:
                self._readpickle()
                return len(self._stars)
            except FileNotFoundError:
                # no worries - we continue
                stars = None

        if self._force_reload or not self._files_exist():
             self.__class__.log.debug('the very slow path - base star files downloading')
             self._prime_from_web()

        self.__class__.log.debug('the slow path - base star files used')
        # zero out the star database
        self._star_set(None)
        # fill the star database
        try:
            # _readstarfile will write into _stars
            n_lines = self._readstarfile(self.directory(), self._max_mag, self._star_append)
            self.__class__.log.debug('%s from %s with %s records' % (self.name(), self.directory(), n_lines))
        except FileNotFoundError:
            self.__class__.log.error('star catalog file: %s' % (self.directory()))
            return 0

        if n_lines == 0 or len(self._stars) == 0:
            # got nada!
            self.__class__.log.error('star catalog file: got zero lines, dir=%s' % (self.directory()))
            return 0

        self.__class__.log.debug('%s with %d records found' % (self.name(), n_lines))

        # we could do this - but for now, we don't
        # self._star_set(sorted(self._stars, key=lambda v: (v.mag)))

        # save it all away for later use - becuase we only get here if there's no pickle file
        if not dont_pickle:
            self._writepickle()
        return len(self._stars)

    def _readstarfile(self, directory, max_mag, star_append):
        """ _readstarfile() """

        # this is expected to be implemented by the catalog-specific code
        raise NotImplementedError from None

    def _readpickle(self):
        """ _readpickle() """

        filename = (self.directory() / self.name().lower()).with_suffix('.pickle')
        # read in the pickle file
        try:
            with open(filename, 'rb') as fd:
                stars_b = fd.read()
        except FileNotFoundError:
            raise CatalogError(filename) from None

        # check digest and only return stars if correct
        signature1 = hmac.new(self._key, stars_b, hashlib.sha256).hexdigest()
        filename = (self.directory() / self.name().lower()).with_suffix('.sha256')
        try:
            with open(filename, 'r', encoding='utf-8') as fd:
                signature2 = fd.read().rstrip()
        except FileNotFoundError as e:
            self.__class__.log.error('sig file:', type(e).__name__, e, self.directory())
            raise CatalogError(filename) from None

        if not hmac.compare_digest(signature1, signature2):
            # Danger Will Robinson - ignore it all!
            self.__class__.log.error('sig file mismatch: signature %s vs %s' % (signature1, signature2))
            raise CatalogError('%s: sig file mismatch' % (filename)) from None

        # We have a correct sig - lets proceed!
        stars = pickle.loads(stars_b)

        # yippee, we can use the saved away data
        self.__class__.log.debug('yippee - pickle file used')
        self._star_set(stars)

    def _writepickle(self):
        """ _writepickle() """

        stars_b = pickle.dumps(self._stars)

        # write the pickle file
        filename = (self.directory() / self.name().lower()).with_suffix('.pickle')
        try:
            with open(filename, 'wb') as fd:
                fd.write(stars_b)
        except FileNotFoundError:
            return

        # write digest based on stars
        filename = (self.directory() / self.name().lower()).with_suffix('.sha256')
        signature = hmac.new(self._key, stars_b, hashlib.sha256).hexdigest()
        with open(filename, 'w', encoding='utf-8') as fd:
            fd.write(signature)
            fd.write('\n')
        self.__class__.log.debug('signature written = %s' % (signature))

    def _database_open(self, memory=False, shared=False, fresh=False):
        """ _database_open() """

        if self._db:
            # we've already returned a count on the previous try - let's not do it again
            return None

        if memory:
            if shared:
                filename = ':memory:?cache=shared'
            else:
                filename = ':memory:'
        else:
            filename = (self.directory() / self.name().lower()).with_suffix('.db')
            if not os.path.exists(filename):
                fresh = True

        try:
            self._db = sqlite3.connect(filename)
        except sqlite3.OperationalError as e:
            self.__class__.log.error('db file:', type(e).__name__, e, self.directory())
            return None

        cur = self._db.cursor()
        if (memory and not shared) or fresh:
            cur.execute('DROP TABLE IF EXISTS stars')
        cur.execute('CREATE TABLE IF NOT EXISTS stars(number INTEGER, name_star TEXT, name_constellation TEXT, ra REAL, dec REAL, mag REAL)')
        self._db.commit()

        if fresh:
            return 0

        cur = self._db.cursor()
        cur.execute('SELECT COUNT(*) FROM stars')
        l = cur.fetchone()[0]
        self.__class__.log.info('database %s opened from %s, %s records found', self.name(), self.directory(), format(l, ','))
        return l

    def _database_read(self):
        """ _database_read() """

        self._star_set(None)
        cur = self._db.cursor()
        for row in cur.execute('SELECT * FROM stars'):
            # should deal with quotes here
            self._star_append(Star(*row))

    def _database_write(self):
        """ _database_write() """

        cur = self._db.cursor()
        data = []
        for star in self.stars():
            s = star()
            if s[0] and not isinstance(s[0], int):
                s = (s[0][1], s[1], s[2], s[3], s[4], s[5])
            data.append(s)
        cur.executemany('INSERT INTO stars VALUES(?, ?, ?, ?, ?, ?)', data)
        self._db.commit()
        self.__class__.log.info('database insert %s records', format(len(data), ','))

    def _database_truncate(self):
        """ _database_truncate() """

        cur = self._db.cursor()
        #cur.execute('DELETE FROM stars')
        cur.execute('TRUNCATE TABLE stars')
        self._db.commit()
        self.__class__.log.info('database truncate')

    def _database_dump(self):
        """ _database_dump() """

        if not self._use_database:
            return

        cur = self._db.cursor()
        for row in cur.execute('SELECT * FROM stars ORDER BY mag LIMIT 20'):
            print('%s' % (Star(*row)))
        self._db.commit()
