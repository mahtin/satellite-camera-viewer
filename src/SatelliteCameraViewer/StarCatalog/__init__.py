""" StarCatalog """

__version__ = '0.4.0'

import logging
logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)

from .StarCatalog import StarCatalog

StarCatalog.log = log
StarCatalog.log.info('Initializing %s, version %s', StarCatalog.__name__, __version__)

__all__ = ['Star', 'Constellation', 'StarCatalog', '__version__']
