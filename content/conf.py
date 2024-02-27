# -*- coding: utf-8 -*-

# Configuration file for the Sphinx documentation builder.
# See https://www.sphinx-doc.org/en/master/usage/configuration.html

copyright = "2020-2024, Quantinuum"
author = "Quantinuum"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "jupyter_sphinx",
    "sphinx_copybutton",
    "sphinx.ext.autosectionlabel",
    "ablog", 
    "myst_parser",
    "sphinx_favicon",
]

html_theme = "pydata_sphinx_theme"

html_title = "pytket docs"

html_theme_options = {
    "navigation_with_keys": True,
    "logo": {
        "link": "https://tket.quantinuum.com/",
        "image_light": "_static/tketlogo_white.svg",
        "image_dark": "_static/tketlogo_black.svg",
    },
    "icon_links": [{
            "name": "GitHub",
            "url": "https://github.com/CQCL/tket",
            "icon": "fa-brands fa-github",
        }],
}

html_show_sourcelink = False

html_show_sphinx = False

html_show_copyright = True

html_static_path = ["_static"]

html_css_files = ["custom.css"]

favicons = [
    "favicon.svg",
]

# -- Extension configuration -------------------------------------------------

pytketdoc_base = "https://tket.quantinuum.com/api-docs/"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "pytket": (pytketdoc_base, None),
}

# ----- ablog config settings -----
ablog_website = "_website"

ablog_builder = "dirhtml"

blog_path = "blog"
blog_baseurl = "https://tket.quantinuum.com/blog/"
blog_title = "TKET Developer Blog"

blog_authors = {
    "Callum Macpherson": ("Callum Macpherson", "https://github.com/CalMacCQ"),
}

blog_post_pattern = ["posts/*.rst", "posts/*.md"]

blog_feed_archives = True
blog_feed_fulltext = True

blog_post_pattern = "blog/*/*"

# ----- MyST parser config -----

myst_enable_extensions = ["dollarmath", "html_image", "attrs_inline"]

myst_update_mathjax = False

suppress_warnings = ["myst.xref_missing"]

# Exclude README from blog build
exclude_patterns = ["README.md"]
