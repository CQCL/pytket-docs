# pytket
[![PyPI version](https://badge.fury.io/py/pytket.svg)](https://badge.fury.io/py/pytket)
[![Documentation Status](https://readthedocs.org/projects/pytket/badge/?version=latest)](https://pytket.readthedocs.io/en/latest/?badge=latest)

`pytket` is a python module for interfacing with CQC t|ket>, a set of quantum programming tools. We currently support circuits and device architectures from both Google [Cirq](https://www.github.com/quantumlib/cirq) and [Qiskit](https://qiskit.org), allowing the t|ket> tools to be used in conjunction with projects on these platforms.

#### Getting Started
``pytket`` is available for ``python3.5`` or higher, on Linux and Macos.
To install run

``pip install pytket``

Note, installation from source will not work, you must use pip.

See [examples/cirq_routing_example.ipynb](https://github.com/CQCL/pytket-docs/blob/master/examples/cirq_routing_example.ipynb) for a quick introduction to using `pytket`. 

Documentation of the soure code can be found at [pytket.readthedocs.io](https://pytket.readthedocs.io)

**Support**

Cirq 0.4.0
    Circuits composed of operations from [`cirq.ops.common_gates`](https://github.com/quantumlib/Cirq/blob/master/cirq/ops/common_gates.py) are currently supported. 
Qiskit
    Terra commit 259c10580d22122e739ed466d306dcd5adb2027f,
    Aqua commit dfc7dcf5834c12fcedb90e9ab6ccf526d69fa1f7,
    Aqua-Chemistry commit 04a9f7e893fc2780ea0eb086c174918dc2214862
