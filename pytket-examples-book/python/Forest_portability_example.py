# # Code Portability and Intro to Forest

# The quantum hardware landscape is incredibly competitive and rapidly changing. Many full-stack quantum software platforms lock users into them in order to use the associated devices and simulators. This notebook demonstrates how `pytket` can free up your existing high-level code to be used on devices from other providers. We will take a state-preparation and evolution circuit generated using `qiskit`, and enable it to be run on several Rigetti backends.
#
# To use a real hardware device, this notebook should be run from a Rigetti QMI instance. Look [here](https://www.rigetti.com/qcs/docs/intro-to-qcs) for information on how to set this up. Otherwise, make sure you have QuilC and QVM running in server mode. You will need to have `pytket`, `pytket_pyquil`, and `pytket_qiskit` installed, which are all available from PyPI.

# We will start by using `qiskit` to build a random initial state over some qubits. (We remove the initial "reset" gates from the circuit since these are not recognized by the Forest backends, which assume an all-zero initial state.)

from qiskit import QuantumCircuit
from qiskit.quantum_info.states.random import random_statevector

n_qubits = 3
state = random_statevector((1 << n_qubits, 1)).data
state_prep_circ = QuantumCircuit(n_qubits)
state_prep_circ.initialize(state)
state_prep_circ = state_prep_circ.decompose().decompose()
state_prep_circ.data = [
    datum for datum in state_prep_circ.data if datum[0].name != "reset"
]

print(state_prep_circ)

# We can now evolve this state under an operator for a given duration.

from qiskit.opflow import PauliTrotterEvolution
from qiskit.opflow.primitive_ops import PauliSumOp
from qiskit.quantum_info import Pauli

duration = 1.2
op = PauliSumOp.from_list([("XXI", 0.3), ("YYI", 0.5), ("ZZZ", -0.4)])
evolved_op = (duration * op).exp_i()
evolution_circ = PauliTrotterEvolution(reps=1).convert(evolved_op).to_circuit()
print(evolution_circ)

for op in evolution_circ:
    state_prep_circ.append(op)

# Now that we have a circuit, `pytket` can take this and start operating on it directly. For example, we can apply some basic compilation passes to simplify it.

from pytket.extensions.qiskit import qiskit_to_tk

tk_circ = qiskit_to_tk(state_prep_circ)

from pytket.passes import (
    SequencePass,
    CliffordSimp,
    DecomposeBoxes,
    KAKDecomposition,
    SynthesiseTket,
)

DecomposeBoxes().apply(tk_circ)
optimise = SequencePass([KAKDecomposition(), CliffordSimp(False), SynthesiseTket()])
optimise.apply(tk_circ)

# Display the optimised circuit:

from pytket.circuit.display import render_circuit_jupyter

render_circuit_jupyter(tk_circ)

# The Backends in `pytket` abstract away the differences between different devices and simulators as much as possible, allowing painless switching between them. The `pytket_pyquil` package provides two Backends: `ForestBackend` encapsulates both running on physical devices via Rigetti QCS and simulating those devices on the QVM, and `ForestStateBackend` acts as a wrapper to the pyQuil Wavefunction Simulator.
#
# Both of these still have a few restrictions on the circuits that can be run. Each only supports a subset of the gate types available in `pytket`, and a real device or associated simulation will have restricted qubit connectivity. The Backend objects will contain a default compilation pass that will statisfy these constraints as much as possible, with minimal or no optimisation.
#
# The `ForestStateBackend` will allow us to view the full statevector (wavefunction) expected from a perfect execution of the circuit.

from pytket.extensions.pyquil import ForestStateBackend

state_backend = ForestStateBackend()
tk_circ = state_backend.get_compiled_circuit(tk_circ)

handle = state_backend.process_circuit(tk_circ)
state = state_backend.get_result(handle).get_state()
print(state)

# For users who are familiar with the Forest SDK, the association of qubits to indices of bitstrings (and consequently the ordering of statevectors) used by default in `pytket` Backends differs from that described in the [Forest docs](http://docs.rigetti.com/en/stable/wavefunction_simulator.html#multi-qubit-basis-enumeration). You can recover the ordering used by the Forest systems with `BackendResult.get_state(tk_circ, basis:pytket.BasisOrder.dlo)` (see our docs on the `BasisOrder` enum for more details).

# Connecting to real devices works very similarly. Instead of obtaining the full statevector, we are only able to measure the quantum state and sample from the resulting distribution. Beyond that, the process is pretty much the same.
#
# The following shows how to run the circuit on the "9q-square" lattice. The `as_qvm` switch on the `get_qc` method will switch between connecting to the real Aspen device and the QVM, allowing you to test your code with a simulator before you reserve your slot with the device.

tk_circ.measure_all()

from pyquil import get_qc
from pytket.extensions.pyquil import ForestBackend

aspen_qc = get_qc("9q-square", as_qvm=True)
aspen_backend = ForestBackend(aspen_qc)
tk_circ = aspen_backend.get_compiled_circuit(tk_circ)

counts = aspen_backend.run_circuit(tk_circ, 2000).get_counts()
print(counts)

# Note that attempting to connect to a live quantum device (using a `QuantumComputer` constructed with `as_qvm=False`) will fail unless it is running from a QMI instance during a reservation for the named lattice.
