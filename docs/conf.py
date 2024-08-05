# -*- coding: utf-8 -*-

# Configuration file for the Sphinx documentation builder.
# See https://www.sphinx-doc.org/en/master/usage/configuration.html

copyright = "2020-2024, Quantinuum"
author = "Quantinuum"


html_title = "pytket user guide"

extensions = [
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
    "pytket-qujax": ("https://tket.quantinuum.com/extensions/pytket-qujax/", None),
    "pytket-cirq": ("https://tket.quantinuum.com/extensions/pytket-cirq/", None),
    "sympy": ("https://docs.sympy.org/latest/", None),
}


nb_execution_mode = "cache"

nb_execution_excludepatterns = [
    "examples/backends/Forest_portability_example.ipynb",
    "examples/backends/backends_example.ipynb",
    "examples/backends/qiskit_integration.ipynb",
    "examples/backends/comparing_simulators.ipynb",
    "examples/algorithms_and_protocols/expectation_value_example.ipynb",
    "examples/algorithms_and_protocols/pytket-qujax_heisenberg_vqe.ipynb",
    "examples/algorithms_and_protocols/pytket-qujax-classification.ipynb",
    "examples/algorithms_and_protocols/spam_example.ipynb",
    "examples/algorithms_and_protocols/entanglement_swapping.ipynb",
]

exclude_patterns = ["jupyter_execute/*", ".jupyter_cache", "manual/README.md"]
