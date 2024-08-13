Getting Started
===============

Building a circuit with the ``Circuit`` class
---------------------------------------------

You can create a circuit by creating an instance of the ``Circuit``
class and adding gates manually.

.. jupyter-execute:: 

    from pytket import Circuit
    
    ghz_circ = Circuit(3)
    ghz_circ.H(0)
    ghz_circ.CX(0, 1)
    ghz_circ.CX(1, 2)
    ghz_circ.add_barrier(ghz_circ.qubits)
    ghz_circ.measure_all()

Now let’s draw a nice picture of the circuit with the circuit renderer

.. jupyter-execute:: 

    from pytket.circuit.display import render_circuit_jupyter
    
    render_circuit_jupyter(ghz_circ)

See also the `Circuit
construction <https://tket.quantinuum.com/user-manual/manual_circuit.html>`__
section of the user manual.

Build a ``Circuit`` from a QASM file
------------------------------------

Alternatively we can import a circuit from a QASM file using
`pytket.qasm <https://tket.quantinuum.com/api-docs/qasm.html>`__. There
are also functions for generating a circuit from a QASM string or
exporting to a qasm file.

Note that its also possible to import a circuit from quipper using
`pytket.quipper <https://tket.quantinuum.com/api-docs/quipper.html>`__
module.

.. jupyter-execute:: 

    from pytket.qasm import circuit_from_qasm
    
    w_state_circ = circuit_from_qasm("examples/qasm/W-state.qasm")
    render_circuit_jupyter(w_state_circ)

Import a circuit from qiskit (or other SDK)
-------------------------------------------

Its possible to generate a circuit directly from a qiskit
``QuantumCircuit`` using the
`qiskit_to_tk <https://tket.quantinuum.com/extensions/pytket-qiskit/api.html#pytket.extensions.qiskit.tk_to_qiskit>`__
function.

.. jupyter-execute:: 

    from qiskit import QuantumCircuit
    
    qiskit_circ = QuantumCircuit(3)
    qiskit_circ.h(range(3))
    qiskit_circ.ccx(2, 1 ,0)
    qiskit_circ.cx(0, 1)
    print(qiskit_circ)

.. jupyter-execute:: 

    from pytket.extensions.qiskit import qiskit_to_tk
    
    tket_circ = qiskit_to_tk(qiskit_circ)
    
    render_circuit_jupyter(tket_circ)

Note that pytket and qiskit use opposite qubit ordering conventions. So
circuits which look identical may correspond to different unitary
operations.

Circuit conversion functions are also available for
`pytket-cirq <https://tket.quantinuum.com/extensions/pytket-cirq/>`_,
`pytket-pennylane <https://tket.quantinuum.com/extensions/pytket-pennylane/>`_,
`pytket-braket <https://tket.quantinuum.com/extensions/pytket-braket/>`_
and more.

Using Backends
--------------

In pytket a ``Backend`` represents an interface to a quantum device or
simulator.

We will show a simple example of running the ``ghz_circ`` defined above
on the ``AerBackend`` simulator.

.. jupyter-execute:: 

    render_circuit_jupyter(ghz_circ)

.. jupyter-execute:: 

    from pytket.extensions.qiskit import AerBackend
    
    backend = AerBackend()
    result = backend.run_circuit(ghz_circ)
    print(result.get_counts())

The ``AerBackend`` simulator is highly idealised having a broad gateset,
and no restrictive connectivity or device noise.

The Hadamard and CX gate are supported operations of the simulator so we
can run the GHZ circuit without changing any of the operations. For more
realistic cases a compiler will have to solve for the limited gateset of
the target backend as well as other backend requirements.

See the `Running on
Backends <https://tket.quantinuum.com/user-manual/manual_backend.html>`__
section of the user manual and the `backends example
notebook <https://tket.quantinuum.com/examples/backends_example.html>`__
for more.




.. toctree::
    :caption: Manual
    :maxdepth: 2

    manual/manual_intro.rst
    manual/manual_circuit.rst
    manual/manual_backend.rst
    manual/manual_compiler.rst
    manual/manual_noise.rst
    manual/manual_assertion.rst
    manual/manual_zx.rst
    manual/tket_tips.md

.. toctree::
    :glob:
    :caption: Example Notebooks
    :maxdepth: 2

    examples/circuit_construction/*
    examples/backends/*
    examples/circuit_compilation/*
    examples/algorithms_and_protocols/*
