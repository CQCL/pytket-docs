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
    "myst_nb",
]

html_theme = "pydata_sphinx_theme"

html_title = "Manual"

html_theme_options = {
    "navigation_with_keys": True,
    "logo": {
        "image_light": "_static/Quantinuum_logo_black.png",
        "image_dark": "_static/Quantinuum_logo_white.png",
    },
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/CQCL/tket",
            "icon": "fa-brands fa-github",
        }
    ],
}

html_static_path = ["_static"]

html_css_files = ["custom.css"]

# -- Extension configuration -------------------------------------------------

pytketdoc_base = "https://tket.quantinuum.com/api-docs/"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "pytket": (pytketdoc_base, None),
    "qiskit": ("https://docs.quantum.ibm.com/api/qiskit", None),
    "pytket-qiskit": ("https://tket.quantinuum.com/extensions/pytket-qiskit/", None),
    "pytket-quantinuum": (
        "https://tket.quantinuum.com/extensions/pytket-quantinuum/",
        None,
    ),
    "sympy": ("https://docs.sympy.org/latest/", None),
}


exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    ".venv/*",
    "examples/Forest_portability_example.ipynb",
    "examples/backends_example.ipynb",
    "examples/qiskit_integration.ipynb",
    "examples/comparing_simulators.ipynb",
    "examples/expectation_value_example.ipynb",
    "examples/pytket-qujax_heisenberg_vqe.ipynb",
    "examples/spam_example.ipynb",
    "examples/entanglement_swapping.ipynb",
    "examples/pytket-qujax-classification.ipynb",
    "jupyter_execute/",
]