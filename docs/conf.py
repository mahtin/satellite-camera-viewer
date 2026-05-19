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

_dotdot = '.' + '.'
sys.path.insert(0, os.path.abspath(_dotdot))
_src = _dotdot + '/' + 'src'
sys.path.insert(0, os.path.abspath(_src))
_version_file = _src + '/' + 'SatelliteCameraViewer/__init__.py'
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
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx_rtd_theme',
    'myst_parser',
    'sphinx_copybutton',
    'sphinx_design',
    'sphinx_togglebutton',
    'numpydoc',
]

autosummary_generate = True

#autodoc_default_options = {
#    'members': True,
#    'undoc-members': True,
#    'show-inheritance': True,
#}

#autodoc_mock_imports = [
#    'numpy',
#    'pyvista',
#    'astropy',
#    'scipy',
#    'sgp4',
#]


# removed ... don't work ...
#   'sphinx.ext.todo',
#   'sphinx.ext.intersphinx',
#   'sphinx.ext.viewcode',

#intersphinx_mapping = {
#    'python': ('https://docs.python.org/3', None),
#}

#   'PyVista': ('https://docs.pyvista.org/', None),
#   'SciPy': ('https://docs.scipy.org/doc/scipy/', None),

# removed ... don't work ...
#   'matplotlib.pyplot': ('https://matplotlib.org/3.5.3/api/_as_gen/matplotlib.pyplot.html', None),
#   'astropy': ('https://docs.astropy.org/', None),
#   'NumPy': ('https://numpy.org/doc/stable/dev/', None),
#   'SGP4': ('https://pypi.org/project/sgp4/', None),

templates_path = ['_templates']
exclude_patterns = [
    # 'src/SatelliteCameraViewer/__init__.py',
    '_build',
    'Thumbs.db',
    '.DS_Store'
]

master_doc = 'index'

autoclass_content = 'both'

todo_include_todos = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

#html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_build/_static/']

html_use_index = True
html_domain_indices = True
html_copy_source = True
html_show_sourcelink = False
html_search_language = 'en'
