import os
import sys

sys.path.insert(0, os.path.abspath('..'))

project = 'django-openapi-tester'
author = 'Sondre Lillebø Gundersen'
copyright = '2020, Snok'

extensions = ['sphinx_rtd_theme', 'sphinx.ext.autodoc', 'sphinx.ext.coverage', 'sphinx.ext.napoleon']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'sphinx_rtd_theme'
html_theme_path = ['_themes']

# The master toctree document.
master_doc = 'index'
