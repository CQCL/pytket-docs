Pytket Documentation
==================================

`Pytket <https://www.github.com/CQCL/pytket>`_ is a python module for interfacing with CQC t|ket>, a set of quantum programming tools. We currently support circuits and device architectures from both Google Cirq (https://www.github.com/quantumlib/cirq) and Qiskit (https://qiskit.org), allowing the t|ket> tools to be used in conjunction with projects on these platforms.

**Getting Started**

``pytket`` is available for ``python3.6`` or higher, on Linux and Macos.
To install run

``pip install pytket``

Note, installation from source will not work, you must use pip.

See `examples/cirq_routing_example.ipynb <https://github.com/CQCL/pytket/blob/master/examples/cirq_routing_example.ipynb>`_ for a quick introduction to using `pytket`. 

**Support**

Cirq 0.4.0
    Circuits composed of operations from `cirq.ops.common_gates <https://github.com/quantumlib/Cirq/blob/master/cirq/ops/common_gates.py>`_ are currently supported. 
Qiskit
    Terra commit 259c10580d22122e739ed466d306dcd5adb2027f,
    Aqua commit dfc7dcf5834c12fcedb90e9ab6ccf526d69fa1f7,
    Aqua-Chemistry commit 04a9f7e893fc2780ea0eb086c174918dc2214862

.. toctree::
   :caption: Contents:
   :maxdepth: 2

   circuit.rst
   cirq.rst
   qiskit.rst
   chemistry.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
