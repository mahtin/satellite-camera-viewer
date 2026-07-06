""" StarCatalog """

__version__ = '0.6.1'

import logging
from .StarCatalog import StarCatalog

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)

StarCatalog.log = log
StarCatalog.log.info('Initializing %s, version %s', StarCatalog.__name__, __version__)

__all__ = ['Star', 'StarCatalog', '__version__']
