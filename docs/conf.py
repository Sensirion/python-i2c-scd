# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from datetime import datetime

import pkg_resources

# Add project directory such that sphinx can detect the package.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# -- Project information -----------------------------------------------------
distribution = pkg_resources.get_distribution('<sensirion_package_name>')

project = distribution.project_name
copyright = u'{} Sensirion AG, Switzerland'.format(datetime.now().year)
author = 'Sensirion AG'
version = distribution.version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc'
]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Workaround for weirdly formatted function parameters. See https://github.com/readthedocs/sphinx_rtd_theme/issues/766
html4_writer = True
