# pytket
[![PyPI version](https://badge.fury.io/py/pytket.svg)](https://badge.fury.io/py/pytket)

`pytket` is a python module for interfacing with CQC t|ket>, a set of quantum programming tools. We currently support circuits and device architectures from Google [Cirq](https://www.github.com/quantumlib/cirq), IBM [Qiskit](https://qiskit.org), [Pyzx](https://github.com/Quantomatic/pyzx), [ProjectQ](https://github.com/ProjectQ-Framework/ProjectQ) and Rigetti [pyQuil](http://rigetti.com/forest), allowing the t|ket> tools to be used in conjunction with projects on these platforms.

### Getting Started
``pytket`` is available for ``python3.6`` or higher, on Linux and MacOS.
To install, run 

``pip install pytket``

Note: attempting to install from source will not set up the required binaries for the t|ket> compiler, so we recommend the PyPI installation.

See the [Getting Started](https://cqcl.github.io/pytket/build/html/getting_started.html) page for a quick introduction to using `pytket`. 

**Documentation** can be found at [cqcl.github.io/pytket](https://cqcl.github.io/pytket)

To get more in depth on features, see the [examples](https://github.com/CQCL/pytket/blob/master/examples).

### Interfaces
To use pytket in conjunction with other platforms you must download an additional separate module for each.
This can be done from pip, or from source, as the binaries are included with the core `pytket` package.

For each subpackage:

Qiskit: ``pip install pytket-qiskit`` 

Cirq: ``pip install pytket-cirq``

PyQuil: ``pip install pytket-pyquil``

ProjectQ: ``pip install pytket-projectq``

PyZX: ``pip install pytket-pyzx`` 

Note:this will need a separate install of `pyzx` from [source](https://github.com/Quantomatic/pyzx).


