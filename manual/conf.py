# -*- coding: utf-8 -*-

# Configuration file for the Sphinx documentation builder.
# See https://www.sphinx-doc.org/en/master/usage/configuration.html

project = "pytket-manual"
copyright = "2020-2022 Cambridge Quantum Computing Ltd"
author = "Cambridge Quantum Computing Ltd"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "jupyter_sphinx",
]

html_theme = "sphinx_book_theme"

pygments_style = "pastie"

html_theme = "sphinx_book_theme"

html_theme_options = {
    "repository_url": "https://github.com/CQCL/tket",
    "use_repository_button": True,
    "use_issues_button": True
}

html_static_path = ["_static"]

html_css_files = ["custom.css"]

# -- Extension configuration -------------------------------------------------

pytketdoc_base = "https://cqcl.github.io/tket/pytket/api/"

intersphinx_mapping = {
    "https://docs.python.org/3/": None,
    pytketdoc_base: None,
}
