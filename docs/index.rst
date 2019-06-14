pytket Documentation
==================================

`pytket <https://www.github.com/CQCL/pytket>`_ is a python module for interfacing with CQC :math:`\mathrm{t|ket}\rangle`, a set of quantum programming tools. We currently support circuits and device architectures from `Google Cirq <https://www.github.com/quantumlib/cirq>`_, `IBM's Qiskit <https://qiskit.org>`_, `ProjectQ <https://github.com/ProjectQ-Framework/ProjectQ>`_, `PyZX <https://github.com/Quantomatic/pyzx>`_, and the `Rigetti Forest SDK <http://rigetti.com/forest>`_, allowing the :math:`\mathrm{t|ket}\rangle` tools to be used in conjunction with projects on these platforms.

**Try it yourself**

pytket can be installed from PyPI by running ``pip install pytket`` from the command line. Note: attempting to install from source will not set up the required binaries for the :math:`\mathrm{t|ket}\rangle` compiler, so we recommend the PyPI installation.

For a quick introduction to pytket and the :py:class:`Circuit` interface, head to :ref:`start`, or have a look at our jupyter notebooks (such as `examples/cirq_routing_example.ipynb <https://github.com/CQCL/pytket/blob/master/examples/cirq_routing_example.ipynb>`_) for tutorials on routing, optimisation, and interfacing with other quantum SDKs.

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
    cirq.rst
    qiskit.rst
    pyquil.rst
    projectq.rst
    projectq_backend.rst
    pyzx.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
