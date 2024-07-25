# -*- coding: utf-8 -*-

# Configuration file for the Sphinx documentation builder.
# See https://www.sphinx-doc.org/en/master/usage/configuration.html

copyright = "2020-2024, Quantinuum"
author = "Quantinuum"


html_title = "User guide"

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

myst_enable_extensions = ["dollarmath", "html_image", "attrs_inline"]

html_theme = "furo"
templates_path = ["./quantinuum-sphinx/_templates/"]
html_static_path = ["./quantinuum-sphinx/_static/", "_static/"]

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


nb_execution_mode = "cache"

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
    "jupyter_execute/*",
    "manual/README.md",
    ".jupyter_cache",
]
