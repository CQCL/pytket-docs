Getting Started
===============

The tket compiler is a powerful tool for optimizing and manipulating
platform-agnostic quantum circuits, focused on enabling superior performance on
NISQ (noisy intermediate-scale quantum) devices. The pytket package provides an
API for interacting with tket and transpiling to and from other popular quantum
circuit specifications.

Pytket is compatible with 64-bit Python 3.7, 3.8 and 3.9, on Linux, MacOS (10.14
or later) and Windows. Install pytket from PyPI using:

::

    pip install pytket

This will install the tket compiler binaries as well as the pytket package. For
those using an older version of pytket, keep up to date by installing with the
``--upgrade`` flag for additional features and bug fixes.

There are separate packages for managing the interoperability between pytket and
other quantum software packages which can also be installed via PyPI. For
details of these, see the
`pytket-extensions <https://github.com/CQCL/pytket-extensions>`_ repo.


The quantum circuit is an abstraction of computation using quantum resources,
designed by initializing a system into a fixed state, then mutating it via
sequences of instructions (gates).

The native circuit interface built into pytket allows us to build circuits and
use them directly.

::

    from pytket import Circuit
    c = Circuit(2,2) # define a circuit with 2 qubits and 2 bits
    c.H(0)           # add a Hadamard gate to qubit 0
    c.Rz(0.25, 0)    # add an Rz gate of angle 0.25*pi to qubit 0
    c.CX(1,0)        # add a CX gate with control qubit 1 and target qubit 0
    c.measure_all()  # measure qubits 0 and 1, recording the results in bits 0 and 1

Pytket provides many handy shortcuts and higher-level components for building
circuits, including custom gate definitions, circuit composition, gates with
symbolic parameters, and conditional gates.

On the other hand, pytket's flexibile interface allows you to take circuits
defined in a number of languages, including raw source code languages such as
OpenQASM and Quipper, or embedded python frameworks such as Qiskit and Cirq.

::

    from pytket.qasm import circuit_from_qasm
    c = circuit_from_qasm("my_qasm_file.qasm")

Or, if an extension module like ``pytket-qiskit`` is installed:

::

    from qiskit import QuantumCircuit
    qc = QuantumCircuit()
    # ...
    from pytket.extensions.qiskit import qiskit_to_tk
    c = qiskit_to_tk(qc)

See the
`Pytket User Manual <https://cqcl.github.io/pytket/build/html/manual/index.html>`_
for an extensive tutorial on pytket, providing a gentle introduction to its
features and how to run circuits on backend devices, with worked examples.
