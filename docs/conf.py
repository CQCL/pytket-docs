# -*- coding: utf-8 -*-

# Configuration file for the Sphinx documentation builder.
# See https://www.sphinx-doc.org/en/master/usage/configuration.html

copyright = "2020-2024, Quantinuum"
author = "Quantinuum"


html_title = "pytket user guide"

extensions = [
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx_copybutton",
    "sphinx.ext.autosectionlabel",
    "myst_nb",
]

myst_enable_extensions = ["dollarmath", "html_image", "attrs_inline"]

html_theme = "furo"
templates_path = ["./quantinuum-sphinx/_templates/"]
html_static_path = ["./quantinuum-sphinx/_static/", "_static/"]

pytketdoc_base = "https://docs.quantinuum.com/tket/"
ext_url = pytketdoc_base + "extensions/"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "pytket": (pytketdoc_base + "api-docs/", None),
    "qiskit": ("https://docs.quantum.ibm.com/api/qiskit", None),
    "pytket-qiskit": (ext_url + "pytket-qiskit/", None),
    "pytket-quantinuum": (ext_url + "pytket-quantinuum/", None,),
    "pytket-pennylane": (ext_url + "pytket-pennylane/", None),
    "pytket-qujax": (ext_url + "pytket-qujax/", None),
    "pytket-cirq": (ext_url + "pytket-cirq/", None),
    "pytket-braket": (ext_url + "pytket-braket/", None),
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
    "examples/algorithms_and_protocols/pytket-qujax_qaoa.ipynb",
    "examples/algorithms_and_protocols/ucc_vqe.ipynb",
    "examples/algorithms_and_protocols/spam_example.ipynb",
    "examples/algorithms_and_protocols/entanglement_swapping.ipynb",
]

exclude_patterns = [
    "jupyter_execute/*",
    ".jupyter_cache",
    "**/README.md",
    "README.md",
    ".venv",
]
