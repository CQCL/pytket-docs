pytket-projectq
==================================

`ProjectQ <https://github.com/ProjectQ-Framework/ProjectQ>`_ is an open-source
library for quantum circuit compilation and simulation.

``pytket-projectq`` is an extension to ``pytket`` that allows ``pytket`` circuits to
be run on ProjectQ simulators, as well as conversion to the ProjectQ
representation.

``pytket-projectq`` is available for Python 3.7, 3.8 and 3.9, on Linux, MacOS and Windows.
To install, run:

``pip install pytket-projectq``

.. warning::
    ``pytket-projectq`` currently cannot be installed on MacOS Big Sur due to a compatibility issue in ProjectQ <= 0.5.1.

pytket.backends.projectq
~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: pytket.backends.projectq
    :members: ProjectQBackend

pytket.extensions.projectq
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: pytket.extensions.projectq
    :members: tk_to_projectq, tketBackendEngine, tketOptimiser
