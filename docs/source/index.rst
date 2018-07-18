.. pytket documentation master file, created by
   sphinx-quickstart on Thu Jul 12 16:00:09 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Pytket Documentation
==================================
`Pytket <https://www.github.com/CQCL/pytket>`_ is a python module for interfacing with CQC t|ket>, a set of quantum programming tools. This first version focusses on integration with Google Cirq (https://www.github.com/quantumlib/cirq), and provides functionality to use Cirq circuits with t|ket> tools. 

**Getting Started**

``pytket`` is available for ``python3.5`` or higher, on Linux and Macos. Windows support is under development.
To install run

``pip install pytket``

Note, installation from source does not work, you must use pip.

See `examples/cirq_routing_example.ipynb <https://github.com/CQCL/pytket/blob/master/examples/cirq_routing_example.ipynb>`_ for a quick introduction to using `pytket`. 
There is also a video introduction `here <https://www.youtube.com/watch?v=f4jhD4J3-W8>`_. 

**Support**

Circuits composed of operations from `cirq.ops.common_gates <https://github.com/quantumlib/Cirq/blob/master/cirq/ops/common_gates.py>`_ are currently supported. 

.. toctree::
   :caption: Contents:
   :maxdepth: 2
   
   cirq_convert
   qubits
   _route_wrapper
   _cpptket
   



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


