import os
import sys

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'edgar-wrapper-py'
copyright = '2023, carmacs'
author = 'carmacs'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Add this line to define the master document for LaTex only
master_doc = 'index'

sys.path.insert(0, os.path.abspath('.'))

extensions = [
    'sphinx.ext.autodoc'
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# Sphinx Themes
# html_theme = 'alabaster'
# html_theme = 'classic'
# html_theme = 'nature'
# html_theme = 'pyramid'
# ReadtheDocs theme (need to run pip install sphinx_rtd_theme)
html_theme = 'sphinx_rtd_theme'

html_static_path = ['_static']

# customize the navigation depth, display the logo, etc.. only possible for sphinx_rtd theme
html_theme_options = {
    'navigation_depth': 4,
    'logo_only': False,
    'display_version': True,
}
# use custom CSS if any
# html_css_files = [
#     'css/custom.css',
# ]

# ----- Customizing PDF Output ------ #

# LaTeX preamble to adjust the PDF's appearance.
# change the font size, paper size...etc, it assumes LaTeX for MacOs installed

latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',
    'preamble': r'''
    \usepackage{times}
    ''',
}

# LaTeX Document Class to specify a different document class such as howto or manual to change the layout:
latex_documents = [
  (master_doc, 'edgar-wrapper-py.tex', 'edgar-wrapper-py Documentation',
   'carmacs', 'manual'),
]
