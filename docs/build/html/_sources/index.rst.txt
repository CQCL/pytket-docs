pytket
======

``pytket`` is a python module for interfacing with CQC t|ket>, a set of
quantum programming tools. We currently support circuits and device
architectures from Google `Cirq`_, IBM `Qiskit`_, `Pyzx`_, `ProjectQ`_
and Rigetti `pyQuil`_, allowing the t|ket> tools to be used in
conjunction with projects on these platforms.

Getting Started
~~~~~~~~~~~~~~~

``pytket`` is available for ``python3.6`` or higher, on Linux and MacOS.
To install, run

``pip install pytket``

Note: attempting to install from source will not set up the required
binaries for the t|ket> compiler, so we recommend the PyPI installation.

See the `Getting Started`_ page for a quick introduction to using
``pytket``.

To get more in depth on features, see the `examples`_.

Interfaces
~~~~~~~~~~

To use pytket in conjunction with other platforms you must download an
additional separate module for each. This can be done from pip, or from
source, as they binaries are included with the core ``pytket`` package.

For each subpackage:

Qiskit: ``pip install pytket-qiskit``

Cirq: ``pip install pytket-cirq``

PyQuil: ``pip install pytket-pyquil``

ProjectQ: ``pip install pytket-projectq``

PyZX: ``pip install pytket-pyzx``

Note:this will need a separate install of ``pyzx`` from `source`_.

.. _Cirq: https://www.github.com/quantumlib/cirq
.. _Qiskit: https://qiskit.org
.. _Pyzx: https://github.com/Quantomatic/pyzx
.. _ProjectQ: https://github.com/ProjectQ-Framework/ProjectQ
.. _pyQuil: http://rigetti.com/forest
.. _Getting Started: getting_started.html
.. _examples: https://github.com/CQCL/pytket/blob/master/examples
.. _source: https://github.com/Quantomatic/pyzx

.. |PyPI version| image:: https://badge.fury.io/py/pytket.svg
   :target: https://badge.fury.io/py/pytket
.. |Documentation Status| image:: https://readthedocs.org/projects/pytket/badge/?version=latest
   :target: https://pytket.readthedocs.io/en/latest/?badge=latest
.. toctree::
    :caption: Contents:
    :maxdepth: 1

    getting_started.rst
    changelog.rst

.. toctree::
    :caption: API Reference:
    :maxdepth: 2

    circuit.rst
    routing.rst
    transform.rst
    backends.rst
    cirq.rst
    qiskit.rst
    pyquil.rst
    projectq.rst
    pyzx.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
