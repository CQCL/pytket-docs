# pytket

[![PyPI version](https://badge.fury.io/py/pytket.svg)](https://badge.fury.io/py/pytket)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/CQCL/pytket/master?filepath=examples)

`pytket` is a python module for interfacing with CQC t|ket>, a set of quantum programming tools.

This repo contains API documentation and example notebooks to get you started using `pytket`. It does not contain source code.

## Getting Started

``pytket`` is available for ``python3.6`` or higher, on Linux and MacOS.
To install, ensure that you have `pip` version 19 or above, and run

``pip install pytket``

Note: attempting to install from source will not set up the required binaries for the t|ket> compiler, so we recommend the PyPI installation.

See the [Getting Started](https://cqcl.github.io/pytket/build/html/getting_started.html) page for a quick introduction to using `pytket`.

**Documentation** can be found at [cqcl.github.io/pytket](https://cqcl.github.io/pytket)

To get more in depth on features, see the [examples](https://github.com/CQCL/pytket/blob/master/examples).

## Interfaces

We currently support circuits and device architectures from Google [Cirq](https://www.github.com/quantumlib/cirq), IBM [Qiskit](https://qiskit.org), [Pyzx](https://github.com/Quantomatic/pyzx), [ProjectQ](https://github.com/ProjectQ-Framework/ProjectQ), Rigetti [pyQuil](http://rigetti.com/forest), [AQT](https://www.aqt.eu/services/), [Honeywell](https://www.honeywell.com/en-us/company/quantum), Microsoft [QDK](https://docs.microsoft.com/en-us/quantum/), Amazon [Braket](https://aws.amazon.com/braket/), and [Qulacs](http://docs.qulacs.org/en/latest/#), allowing the t|ket> tools to be used in conjunction with projects on these platforms.

To use `pytket` in conjunction with other platforms you must download an additional separate module for each.
This can be done from `pip`.

For each subpackage:

* Qiskit: ``pip install pytket-qiskit``
* Cirq: ``pip install pytket-cirq``
* PyQuil: ``pip install pytket-pyquil``
* ProjectQ: ``pip install pytket-projectq``
* PyZX: ``pip install pytket-pyzx``
* AQT: ``pip install pytket-aqt``
* Honeywell: ``pip install pytket-honeywell``
* Q#: ``pip install pytket-qsharp``
* Braket: ``pip install pytket-braket``
* Qulacs: ``pip install pytket-qulacs``

## LICENCE

Copyright 2019-2020 Cambridge Quantum Computing

Licensed under a Non-Commercial Use Software Licence (the "Licence");
you may not use this product except in compliance with the Licence.
You may obtain a copy of the Licence in the LICENCE file accompanying
these documents or view them [here](https://cqcl.github.io/pytket/build/html/licence.html).

Unless required by applicable law or agreed to in writing, software
distributed under the Licence is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the Licence for the specific language governing permissions and
limitations under the Licence, but note it is strictly for non-commercial use.

## How To Cite

If you wish to cite tket in any academic publications, we generally recommend citing our [software overview paper](https://doi.org/10.1088/2058-9565/ab8e92) for most cases.

If your work is on the topic of specific compilation tasks, it may be more appropriate to cite one of our other papers:

- ["On the qubit routing problem"](https://doi.org/10.4230/LIPIcs.TQC.2019.5) for qubit placement (aka allocation, mapping) and routing (aka swap network insertion, connectivity solving).
- ["Phase Gadget Synthesis for Shallow Circuits"](https://doi.org/10.4204/EPTCS.318.13) for representing exponentiated Pauli operators in the ZX calculus and their circuit decompositions.
- ["A Generic Compilation Strategy for the Unitary Coupled Cluster Ansatz"](https://arxiv.org/abs/2007.10515) for sequencing of terms in Trotterisation and Pauli diagonalisation.

We are also keen for others to benchmark their compilation techniques against us. We recommend checking our [benchmark repository](https://github.com/CQCL/tket_benchmarking) for examples on how to run basic benchmarks with the latest version of `pytket`. Please list the release version of `pytket` with any benchmarks you give, and feel free to get in touch for any assistance needed in setting up fair and representative tests.
