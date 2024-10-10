---
file_format: mystnb
kernelspec:
  name: python3
---

# Getting Started

## Building a circuit with the `Circuit` class

You can create a circuit by creating an instance of the `Circuit`
class and adding gates manually.


```{code-cell} ipython3

from pytket import Circuit

ghz_circ = Circuit(3)
ghz_circ.H(0)
ghz_circ.CX(0, 1)
ghz_circ.CX(1, 2)
ghz_circ.add_barrier(ghz_circ.qubits)
ghz_circ.measure_all()
```

Now let’s draw a nice picture of the circuit with the circuit renderer


```{code-cell} ipython3

from pytket.circuit.display import render_circuit_jupyter

render_circuit_jupyter(ghz_circ)
```

See also the [Circuit construction](../docs/manual/manual_circuit.md)
section of the user manual.

## Build a `Circuit` from a QASM file

Alternatively we can import a circuit from a QASM file using
[pytket.qasm](inv:pytket:*:doc#qasm). There
are also functions for generating a circuit from a QASM string or
exporting to a qasm file.

Note that its also possible to import a circuit from quipper using
[pytket.quipper](inv:pytket:*:doc#quipper)
module.


```{code-cell} ipython3

from pytket.qasm import circuit_from_qasm

w_state_circ = circuit_from_qasm("examples/qasm/W-state.qasm")
render_circuit_jupyter(w_state_circ)
```

## Import a circuit from qiskit (or other SDK)

Its possible to generate a circuit directly from a qiskit
`QuantumCircuit` using the
[qiskit_to_tk](inv:#*.qiskit_to_tk)
function.


```{code-cell} ipython3

from qiskit import QuantumCircuit

qiskit_circ = QuantumCircuit(3)
qiskit_circ.h(range(3))
qiskit_circ.ccx(2, 1 ,0)
qiskit_circ.cx(0, 1)
print(qiskit_circ)
```


```{code-cell} ipython3

from pytket.extensions.qiskit import qiskit_to_tk

tket_circ = qiskit_to_tk(qiskit_circ)

render_circuit_jupyter(tket_circ)
```

Note that pytket and qiskit use opposite qubit ordering conventions. So
circuits which look identical may correspond to different unitary
operations.

Circuit conversion functions are also available for
[pytket-cirq](https://docs.quantinuum.com/tket/extensions/pytket-cirq/),
[pytket-pennylane](https://docs.quantinuum.com/tket/extensions/pytket-pennylane/),
[pytket-braket](https://docs.quantinuum.com/tket/extensions/pytket-braket/)
and more.

## Using Backends

In pytket a `Backend` represents an interface to a quantum device or
simulator.

We will show a simple example of running the `ghz_circ` defined above
on the `AerBackend` simulator.


```{code-cell} ipython3

render_circuit_jupyter(ghz_circ)
```


```{code-cell} ipython3

from pytket.extensions.qiskit import AerBackend

backend = AerBackend()
result = backend.run_circuit(ghz_circ)
print(result.get_counts())
```

The `AerBackend` simulator is highly idealised having a broad gateset,
and no restrictive connectivity or device noise.

The Hadamard and CX gate are supported operations of the simulator so we
can run the GHZ circuit without changing any of the operations. For more
realistic cases a compiler will have to solve for the limited gateset of
the target backend as well as other backend requirements.
See the [Running on Backends](../docs/manual/manual_backend.md) section of the user manual and the [backends example notebook](../docs/examples/backends/backends_example.ipynb)
for more.

```{toctree}
:caption: Manual
:maxdepth: 2

manual/manual_intro.rst
manual/manual_circuit.rst
manual/manual_backend.rst
manual/manual_compiler.rst
manual/manual_noise.rst
manual/manual_assertion.rst
manual/manual_zx.rst
```

```{toctree}
:caption: Example Notebooks
:glob: true
:maxdepth: 2

examples/circuit_construction/*
examples/backends/*
examples/circuit_compilation/*
examples/algorithms_and_protocols/*
```
