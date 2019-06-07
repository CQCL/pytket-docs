# pytket
[![PyPI version](https://badge.fury.io/py/pytket.svg)](https://badge.fury.io/py/pytket)
[![Documentation Status](https://readthedocs.org/projects/pytket/badge/?version=latest)](https://pytket.readthedocs.io/en/latest/?badge=latest)

`pytket` is a python module for interfacing with CQC t|ket>, a set of quantum programming tools. We currently support circuits and device architectures from Google [Cirq](https://www.github.com/quantumlib/cirq), IBM [Qiskit](https://qiskit.org), [Pyzx](https://github.com/Quantomatic/pyzx), [ProjectQ](https://github.com/ProjectQ-Framework/ProjectQ) and Rigetti [pyQuil](http://rigetti.com/forest), allowing the t|ket> tools to be used in conjunction with projects on these platforms.

#### Getting Started
``pytket`` is available for ``python3.6`` or higher, on Linux and MacOS.
To install, run 

``pip install pytket``

Note: attempting to install from source will not set up the required binaries for the :math:`\mathrm{t|ket}\rangle` compiler, so we recommend the PyPI installation.

See [examples/cirq_routing_example.ipynb](https://github.com/CQCL/pytket/blob/master/examples/cirq_routing_example.ipynb) for a quick introduction to using `pytket`. 

Documentation of the soure code can be found at [pytket.readthedocs.io](https://pytket.readthedocs.io)
