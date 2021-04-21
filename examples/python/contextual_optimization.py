# # Contextual optimisation

# This notebook will illustrate the techniques of "contextual optimisation" available in TKET.

# See the user manaul for an introduction to the concept and methods. Here we will present an example showing how we can save some gates at the beginnning and end of a circuit, making no assumptions about the structure of the circuit.

# We will take as an example an ansatz circuit consisting of alternating layers of Ry and CX gates, where some proportion of the Ry angles are zero. This is a typical ansatz for variational algorithms, used for solving diagonal Hamiltonians for combinatorial optimisation.

from pytket.circuit import Circuit
from random import random, randrange, seed


def random_sparse_ansatz(n_qubits, n_layers, p, rng_seed=None):
    seed(rng_seed)
    circ = Circuit(n_qubits)
    for q in range(n_qubits):
        if random() < p:
            circ.Ry(0.1 * randrange(20), q)
    for l in range(n_layers):
        for q in range(0, n_qubits - 1, 2):
            circ.CX(q, q + 1)
        for q in range(2 * (n_qubits // 2)):
            if random() < p:
                circ.Ry(0.1 * randrange(20), q)
        for q in range(1, n_qubits - 1, 2):
            circ.CX(q, q + 1)
        for q in range(2 * ((n_qubits - 1) // 2)):
            if random() < p:
                circ.Ry(0.1 * randrange(20), q + 1)
    circ.measure_all()
    return circ


# Let's examine a smallish example:

from pytket.circuit import OpType
from pytket.extensions.qiskit import tk_to_qiskit

c = random_sparse_ansatz(4, 3, 0.5, rng_seed=0)
print(tk_to_qiskit(c))
print("Number of CX:", c.n_gates_of_type(OpType.CX))

# Contextual optimizations allow us to shave some gates from the beginning and end of the circuit. Those at the end get commuted through the Measure gates into a classical post-processing circuit, which we can then pass to `BackendResult` methods to have the postprocessing performed automatically.

# The `prepare_circuit()` method returns a pair of circuits, the first of which is what we actually run and the second of specifies the required postprocessing.

from pytket.utils import prepare_circuit

c0, ppcirc = prepare_circuit(c)
print(tk_to_qiskit(c0))
print("Number of CX:", c0.n_gates_of_type(OpType.CX))

# In this case, one CX has been shaved from the beginning of the circuit and two from the end.

# We can run the processed circuit on our backend:

from pytket.extensions.qiskit import AerBackend

b = AerBackend()
b.compile_circuit(c0)
h = b.process_circuit(c0, n_shots=10)
r = b.get_result(h)

# And finally get the counts or shots, accounting for the classical postprocessing:

counts = r.get_counts(ppcirc=ppcirc)
print(counts)

# See the [pytket user manual](https://cqcl.github.io/pytket/build/html/manual/manual_compiler.html#contextual-optimisations) for more details about contextual optimisations and how to apply them in TKET.
