# pytket
[![PyPI version](https://badge.fury.io/py/pytket.svg)](https://badge.fury.io/py/pytket)

`pytket` is a python module for interfacing with CQC t|ket>, a set of quantum programming tools. We currently support circuits and device architectures from Google [Cirq](https://www.github.com/quantumlib/cirq), IBM [Qiskit](https://qiskit.org), [Pyzx](https://github.com/Quantomatic/pyzx), [ProjectQ](https://github.com/ProjectQ-Framework/ProjectQ) and Rigetti [pyQuil](http://rigetti.com/forest), allowing the t|ket> tools to be used in conjunction with projects on these platforms.

### Getting Started
``pytket`` is available for ``python3.6`` or higher, on Linux and MacOS.
To install, ensure that you have `pip` version 19 or above, and run

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

### LICENCE

Copyright 2019 Cambridge Quantum Computing

Licensed under a Non-Commercial Use Software Licence (the "Licence");
you may not use this product except in compliance with the Licence.
You may obtain a copy of the Licence in the LICENCE file accompanying
these documents or at:

    https://cqcl.github.io/pytket/build/html/licence.html

Unless required by applicable law or agreed to in writing, software
distributed under the Licence is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the Licence for the specific language governing permissions and
limitations under the Licence, but note it is strictly for non-commercial use.
