# # Comparison of the simulators available through tket

# In this tutorial, we will focus on:
# - exploring the wide array of simulators available through the extension modules for `pytket`;
# - comparing their unique features and capabilities.

# This example assumes the reader is familiar with the basics of circuit construction and evaluation.
#
# To run every option in this example, you will need `pytket`, `pytket-qiskit`, `pytket-pyquil`, `pytket-qsharp`, `pytket-qulacs`, and `pytket-projectq`.
#
# With the number of simulator `Backend`s available across the `pytket` extension modules, we are often asked why to use one over another. Surely, any two simulators are equivalent if they are able to sample the circuits in the same way, right? Not quite. In this notebook we go through each of the simulators in turn and describe what sets them apart from others and how to make use of any unique features.
#
# But first, to demonstrate the significant overlap in functionality, we'll just give some examples of common usage for different types of backends.

# ## Sampling simulator usage

from pytket import Circuit
from pytket.extensions.qiskit import AerBackend

# Define a circuit:

c = Circuit(3, 3)
c.Ry(0.7, 0)
c.CX(0, 1)
c.X(2)
c.measure_all()

# Run on the backend:

backend = AerBackend()
c = backend.get_compiled_circuit(c)
handle = backend.process_circuit(c, n_shots=2000)
counts = backend.get_result(handle).get_counts()
print(counts)

# ## Statevector simulator usage

from pytket import Circuit
from pytket.extensions.qiskit import AerStateBackend

# Build a quantum state:

c = Circuit(3)
c.H(0).CX(0, 1)
c.Rz(0.3, 0)
c.Rz(-0.3, 1)
c.Ry(0.8, 2)

# Examine the statevector:

backend = AerStateBackend()
c = backend.get_compiled_circuit(c)
handle = backend.process_circuit(c)
state = backend.get_result(handle).get_state()
print(state)

# ## Expectation value usage

from pytket import Circuit, Qubit
from pytket.extensions.qiskit import AerBackend, AerStateBackend
from pytket.pauli import Pauli, QubitPauliString
from pytket.utils.operators import QubitPauliOperator

# Build a quantum state:

c = Circuit(3)
c.H(0).CX(0, 1)
c.Rz(0.3, 0)
c.Rz(-0.3, 1)
c.Ry(0.8, 2)

# Define the measurement operator:

xxi = QubitPauliString({Qubit(0): Pauli.X, Qubit(1): Pauli.X})
zzz = QubitPauliString({Qubit(0): Pauli.Z, Qubit(1): Pauli.Z, Qubit(2): Pauli.Z})
op = QubitPauliOperator({xxi: -1.8, zzz: 0.7})

# Run on the backend:

backend = AerBackend()
c = backend.get_compiled_circuit(c)
exp = backend.get_operator_expectation_value(c, op)
print(exp)

# ## `pytket.extensions.qiskit.AerBackend`

# `AerBackend` wraps up the `qasm_simulator` from the Qiskit Aer package. It supports an extremely flexible set of circuits and uses many effective simulation methods making it a great all-purpose sampling simulator.
#
# Unique features:
# - supports mid-circuit measurement and OpenQASM-style conditional gates;
# - encompasses a variety of underlying simulation methods and automatically selects the best one for each circuit (including statevector, density matrix, (extended) stabilizer and matrix product state);
# - can be provided with a `qiskit.providers.Aer.noise.NoiseModel` on instantiation to perform a noisy simulation.

# Useful features:
# - support for fast expectation value calculations according to `QubitPauliString`s or `QubitPauliOperator`s.

from pytket import Circuit
from pytket.extensions.qiskit import AerBackend
from itertools import combinations
from qiskit.providers.aer.noise import NoiseModel, depolarizing_error

# Quantum teleportation circuit:

c = Circuit()
alice = c.add_q_register("a", 2)
bob = c.add_q_register("b", 1)
data = c.add_c_register("d", 2)
final = c.add_c_register("f", 1)

# Start in an interesting state:

c.Rx(0.3, alice[0])

# Set up a Bell state between Alice and Bob:

c.H(alice[1]).CX(alice[1], bob[0])

# Measure Alice's qubits in the Bell basis:

c.CX(alice[0], alice[1]).H(alice[0])
c.Measure(alice[0], data[0])
c.Measure(alice[1], data[1])

# Correct Bob's qubit:

c.X(bob[0], condition_bits=[data[0], data[1]], condition_value=1)
c.X(bob[0], condition_bits=[data[0], data[1]], condition_value=3)
c.Z(bob[0], condition_bits=[data[0], data[1]], condition_value=2)
c.Z(bob[0], condition_bits=[data[0], data[1]], condition_value=3)

# Measure Bob's qubit to observe the interesting state:

c.Measure(bob[0], final[0])

# Set up a noisy simulator:

model = NoiseModel()
dep_err = depolarizing_error(0.04, 2)
for i, j in combinations(range(3), r=2):
    model.add_quantum_error(dep_err, ["cx"], [i, j])
    model.add_quantum_error(dep_err, ["cx"], [j, i])
backend = AerBackend(noise_model=model)

# Run circuit:

c = backend.get_compiled_circuit(c)
handle = backend.process_circuit(c, n_shots=2000)
result = backend.get_result(handle)
counts = result.get_counts([final[0]])
print(counts)

# ## `pytket.extensions.qiskit.AerStateBackend`

# `AerStateBackend` provides access to Qiskit Aer's `statevector_simulator`. It supports a similarly large gate set and has competitive speed for statevector simulations.
#
# Useful features:
# - no dependency on external executables, making it easy to install and run on any computer;
# - support for fast expectation value calculations according to `QubitPauliString`s or `QubitPauliOperator`s.

# ## `pytket.extensions.qiskit.AerUnitaryBackend`

# Finishing the set of simulators from Qiskit Aer, `AerUnitaryBackend` captures the `unitary_simulator`, allowing for the entire unitary of a pure quantum process to be calculated. This is especially useful for testing small subcircuits that will be used many times in a larger computation.
#
# Unique features:
# - provides the full unitary matrix for a pure quantum circuit.

from pytket import Circuit
from pytket.extensions.qiskit import AerUnitaryBackend
from pytket.predicates import NoClassicalControlPredicate

# Define a simple quantum incrementer:

c = Circuit(3)
c.CCX(2, 1, 0)
c.CX(2, 1)
c.X(2)

# Examine the unitary:

backend = AerUnitaryBackend()
c = backend.get_compiled_circuit(c)
result = backend.run_circuit(c)
unitary = result.get_unitary()
print(unitary.round(1).real)

# ## `pytket.extensions.pyquil.ForestBackend`

# Whilst it can, with suitable credentials, be used to access the Rigetti QPUs, the `ForestBackend` also features a simulator mode which turns it into a noiseless sampling simulator that matches the constraints of the simulated device (e.g. the same gate set, restricted connectivity, measurement model, etc.). This is useful when playing around with custom compilation strategies to ensure that your final circuits are suitable to run on the device and for checking that your overall program works fine before you invest in reserving a QPU.
#
# Unique features:
# - faithful recreation of the circuit constraints of Rigetti QPUs.

# If trying to use the `ForestBackend` locally (i.e. not on a Rigetti QMI), you will need to have `quilc` and `qvm` running as separate processes in server mode. One easy way of doing this is with `docker` (see the `quilc` and `qvm` documentation for alternative methods of running them):
# `docker run --rm -it -p 5555:5555 rigetti/quilc -R`
# `docker run --rm -it -p 5000:5000 rigetti/qvm -S`

# ## `pytket.extensions.pyquil.ForestStateBackend`

# The Rigetti `pyquil` package also provides the `WavefunctionSimulator`, which we present as the `ForestStateBackend`. Functionally, it is very similar to the `AerStateBackend` so can be used interchangeably. It does require that `quilc` and `qvm` are running as separate processes when not running on a Rigetti QMI.
#
# Useful features:
# - support for fast expectation value calculations according to `QubitPauliString`s or Hermitian `QubitPauliOperator`s.

# ## `pytket.extensions.qsharp.QsharpSimulatorBackend`

# The `QsharpSimulatorBackend` is another basic sampling simulator that is interchangeable with others, using the Microsoft QDK simulator. Note that the `pytket-qsharp` package is dependent on the `dotnet` SDK and `iqsharp` tool. Please consult the `pytket-qsharp` installation instructions for recommendations.

# ## `pytket.extensions.qsharp.QsharpToffoliSimulatorBackend`

# Toffoli circuits form a strict fragment of quantum circuits and can be efficiently simulated. The `QsharpToffoliSimulatorBackend` can only operate on these circuits, but scales much better with system size than regular simulators.
#
# Unique features:
# - efficient simulation of Toffoli circuits.

from pytket import Circuit
from pytket.extensions.qsharp import QsharpToffoliSimulatorBackend

# Define a circuit - start in a basis state:

c = Circuit(3)
c.X(0).X(2)
# Define a circuit - incrementer
c.CCX(2, 1, 0)
c.CX(2, 1)
c.X(2)

# Run on the backend:

backend = QsharpToffoliSimulatorBackend()
c = backend.get_compiled_circuit(c)
handle = backend.process_circuit(c, n_shots=10)
counts = backend.get_result(handle).get_counts()
print(counts)

# ## `pytket.extensions.qsharp.QsharpEstimatorBackend`

# The `QsharpEstimatorBackend` is not strictly a simulator, as it doesn't model the state of the quantum system and try to identify the final state, but instead analyses the circuit to estimate the required resources to run it. It does not support any of the regular outcome types (e.g. shots, counts, statevector), just the summary of the estimated resources.
#
# Unique features:
# - estimates resources to perform the circuit, without actually simulating/running it.

from pytket import Circuit

# from pytket.extensions.qsharp import QsharpEstimatorBackend

# Define a circuit - start in a basis state:

c = Circuit(3)
c.X(0).X(2)
# Define a circuit - incrementer
c.CCX(2, 1, 0)
c.CX(2, 1)
c.X(2)

# Run on the backend:

# (disabled because of https://github.com/CQCL/pytket-qsharp/issues/37)
# backend = QsharpEstimatorBackend()
# c = backend.get_compiled_circuit(c)
# handle = backend.process_circuit(c, n_shots=10)
# resources = backend.get_resources(handle)
# print(resources)

# ## `pytket.extensions.qulacs.QulacsBackend`

# The `QulacsBackend` is an all-purpose simulator with both sampling and statevector modes, using the basic CPU simulator from Qulacs.
#
# Unique features:
# - supports both sampling (shots/counts) and complete statevector outputs.

# Useful features:
# - support for fast expectation value calculations according to `QubitPauliString`s or Hermitian `QubitPauliOperator`s.

# ## `pytket.extensions.qulacs.QulacsGPUBackend`

# If the GPU version of Qulacs is installed, the `QulacsGPUBackend` will use that to benefit from even faster speeds. It is very easy to get started with using a GPU, as it only requires a CUDA installation and the `qulacs-gpu` package from `pip`. Functionally, it is identical to the `QulacsBackend`, but potentially faster if you have GPU resources available.
#
# Unique features:
# - GPU support for very fast simulation.

# ## `pytket.extensions.projectq.ProjectQBackend`

# ProjectQ is a popular quantum circuit simulator, thanks to its availability and ease of use. It provides a similar level of performance and features to `AerStateBackend`.
#
# Useful features:
# - support for fast expectation value calculations according to `QubitPauliString`s or Hermitian `QubitPauliOperator`s.
