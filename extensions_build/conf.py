# -*- coding: utf-8 -*-

# Configuration file for the Sphinx documentation builder.
# See https://www.sphinx-doc.org/en/master/usage/configuration.html

copyright = "2024 Quantinuum"
author = "Quantinuum"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_favicon",
    "sphinx.ext.mathjax",
    "sphinx_copybutton",
    "enum_tools.autoenum",
]

html_theme = "sphinx_book_theme"

html_theme_options = {
    "show_toc_level": 2,
    "navigation_with_keys": True,
    "repository_url": "https://github.com/CQCL/pytket-quantinuum",
    "use_repository_button": True,
    "use_issues_button": True,
    "logo": {
        "image_light": "_static/Quantinuum_logo_black.png",
        "image_dark": "_static/Quantinuum_logo_white.png",
    },
}

html_static_path = ["_static"]

html_css_files = ["custom.css"]

favicons = [
    "favicon.svg",
]

pytketdoc_base = "https://tket.quantinuum.com/api-docs/"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "pytket": (pytketdoc_base, None),
    "qiskit": ("https://qiskit.org/documentation/", None),
    "qulacs": ("http://docs.qulacs.org/en/latest/", None),
}

autodoc_member_order = "groupwise"
