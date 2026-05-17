#
# Copyright (C) 2023-2026 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin
#

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
import re

_src = '.' + '.' + '/' + 'src'
_version_file = _src + '/' + 'SatelliteCameraViewer/__init__.py'

sys.path.insert(0, os.path.abspath(_src))

with open(_version_file, 'r') as f:
    _version_re = re.compile(r"__version__\s=\s'(.*)'")
    version = _version_re.search(f.read()).group(1)

project = 'SatelliteCameraViewer'
copyright = '2023-2026, Martin J Levy'
author = 'Martin J Levy'
release = str(version)

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx_rtd_theme',
    'myst_parser',
    'sphinx_copybutton',
    'sphinx_design',
    'sphinx_togglebutton',
]

templates_path = ['_templates']
exclude_patterns = [
    'src/SatelliteCameraViewer/__init__.py',
    '_build',
    'Thumbs.db',
    '.DS_Store'
]

autoclass_content = 'both'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

#html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

html_use_index = False
html_domain_indices = False
html_copy_source = True
html_show_sourcelink = False
html_search_language = ''
