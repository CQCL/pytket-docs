pytket-pyquil
==================================

Rigetti's `pyQuil <http://rigetti.com/forest>`_ is a library for generating
programs in the Quil language and running them on the Forest platform.

``pytket-pyquil`` is an extension to ``pytket`` that allows ``pytket`` circuits to be
run on Rigetti backends and simulators, as well as conversion to and from pyQuil
representations.

``pytket-pyquil`` is available for Python 3.7, 3.8 and 3.9, on Linux, MacOS and Windows. To
install, run:

``pip install pytket-pyquil``

pytket.extensions.pyquil
~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: pytket.extensions.pyquil
    :members: pyquil_to_tk, tk_to_pyquil, ForestBackend, ForestStateBackend
