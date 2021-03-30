# # Code Portability and Intro to Forest

# The quantum hardware landscape is incredibly competitive and rapidly changing. Many full-stack quantum software platforms lock users into them in order to use the associated devices and simulators. This notebook demonstrates how `pytket` can free up your existing high-level code to be used on devices from other providers. We will take a state-preparation and evolution circuit designed using the Qiskit Aqua package and enable it to be run on several Rigetti backends.
# To use a real hardware device, this notebook should be run from a Rigetti QMI instance. Look [here](https://www.rigetti.com/qcs/docs/intro-to-qcs) for information on how to set this up. Otherwise, make sure you have QuilC and QVM running in server mode. You will need to have `pytket`, `pytket_pyquil`, and `pytket_qiskit` installed, which are all available from PyPI.

# IBM's Qiskit Aqua package is a toolkit for high-level circuit synthesis and quantum algorithms. We will start by building a random initial state over some qubits.

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.aqua.components.initial_states import Custom

n_qubits = 3
state_prep = Custom(n_qubits, state="random")
qreg = QuantumRegister(n_qubits)
state_prep_circ = state_prep.construct_circuit("circuit", qreg)
print(state_prep_circ)

# We can now evolve this state under an operator for a given duration.

from qiskit.aqua.operators import WeightedPauliOperator
from qiskit.quantum_info import Pauli

duration = 1.2
paulis = list(map(Pauli.from_label, ["XXI", "YYI", "ZZZ"]))
weights = [0.3, 0.5 + 1j * 0.2, -0.4]
op = WeightedPauliOperator.from_list(paulis, weights)
evolution_circ = op.evolve(None, duration, num_time_slices=1, quantum_registers=qreg)
print(evolution_circ)

state_prep_circ += evolution_circ

# Now that we have a circuit, `pytket` can take this and start operating on it directly. For example, we can apply some basic compilation passes to simplify it.

from pytket.extensions.qiskit import qiskit_to_tk, tk_to_qiskit

tk_circ = qiskit_to_tk(state_prep_circ)

from pytket.passes import (
    SequencePass,
    CliffordSimp,
    DecomposeBoxes,
    KAKDecomposition,
    SynthesiseIBM,
)

DecomposeBoxes().apply(tk_circ)
optimise = SequencePass([KAKDecomposition(), CliffordSimp(False), SynthesiseIBM()])
optimise.apply(tk_circ)

# Display the optimised circuit
print(tk_to_qiskit(tk_circ))

# The Backends in `pytket` abstract away the differences between different devices and simulators as much as possible, allowing painless switching between them. The `pytket_pyquil` package provides two Backends: `ForestBackend` encapsulates both running on physical devices via Rigetti QCS and simulating those devices on the QVM, and `ForestStateBackend` acts as a wrapper to the pyQuil Wavefunction Simulator.
# Both of these still have a few restrictions on the circuits that can be run. Each only supports a subset of the gate types available in `pytket`, and a real device or associated simulation will have restricted qubit connectivity. The Backend objects will contain a default compilation pass that will statisfy these constraints as much as possible, with minimal or no optimisation.
# The `ForestStateBackend` will allow us to view the full statevector (wavefunction) expected from a perfect execution of the circuit.

from pytket.extensions.pyquil import ForestStateBackend

state_backend = ForestStateBackend()
state_backend.compile_circuit(tk_circ)

state = state_backend.get_state(tk_circ)
print(state)

# For users who are familiar with the Forest SDK, the association of qubits to indices of bitstrings (and consequently the ordering of statevectors) used by default in `pytket` Backends differs from that described in the [Forest docs](http://docs.rigetti.com/en/stable/wavefunction_simulator.html#multi-qubit-basis-enumeration). You can recover the ordering used by the Forest systems with `state_backend.get_state(tk_circ, basis:pytket.BasisOrder.dlo)` (see our docs on the `BasisOrder` enum for more details).

# Connecting to real devices works very similarly. Instead of obtaining the full statevector, we are only able to measure the quantum state and sample from the resulting distribution. Beyond that, the process is pretty much the same.
# The following shows how to run the circuit on the "9q-square" lattice. The `simulator` switch on the `ForestBackend` will switch between connecting to the real Aspen device and the QVM, allowing you to test your code with a simulator before you reserve your slot with the device.

tk_circ.measure_all()

from pytket.extensions.pyquil import ForestBackend

aspen_backend = ForestBackend("9q-square", simulator=True)
aspen_backend.compile_circuit(tk_circ)

counts = aspen_backend.get_counts(tk_circ, 2000)
print(counts)

# Note that attempting to connect to a live quantum device (using a `ForestBackend` with `as_simulator=False`) will fail unless it is running from a QMI instance during a reservation for the named lattice.
