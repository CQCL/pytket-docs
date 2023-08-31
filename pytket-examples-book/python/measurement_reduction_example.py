# # Advanced Expectation Values and Measurement Reduction

# This notebook is an advanced follow-up to the "expectation_value_example" notebook, focussing on reducing the number of circuits required for measurement.
#
# When calculating the expectation value $\langle \psi \vert H \vert \psi \rangle$ of some operator $H$ on a quantum computer, we prepare $\vert \psi \rangle$ using a circuit, and the operator $H$ is first decomposed into a sum of smaller, tractable operators of the form $\alpha P$, where $P \in \mathcal{G}_n$, the multi-qubit Pauli group. Naively, one would obtain the expectation value of each of these smaller operators individually by doing shots on the quantum computer and measuring in the correct Pauli bases. Assuming the device measures only single qubits in the $Z$-basis, this basis change requires single-qubit Clifford gates, which are "cheaper" (less noisy and quicker) than entangling gates. The sum of these smaller operator expectation values is then used to obtain the desired $\langle \psi \vert H \vert \psi \rangle$.
#
# However, the scaling of this process can be poor, meaning that many shots are required. Instead, several of these smaller operators can be measured simultaneously, reducing the total number of measurements. For some sets of measurements, it can be done "for free", meaning that no extra entangling gates are required to perform simultaneous measurement. For general commuting sets of Pauli measurements, Clifford gates are required for simultaneous measurement, including entangling gates.

# There are several strategies for measurement reduction throughout the literature. Examples include https://arxiv.org/abs/1908.06942, https://arxiv.org/abs/1908.08067 and https://arxiv.org/abs/1907.07859.

# In `pytket`, we provide tools to perform measurement reduction. The most accessible way is to use the utils method, `get_operator_expectation_value`. This method wraps up some under-the-hood processes to allow users to calculate expectation values, agnostic to the backend, operator, or circuit. In this tutorial we will use the Qiskit Aer simulators via the `AerBackend`, for shots, and the `AerStateBackend`, for statevector simulation.
#
# We use the `QubitPauliOperator` class to represent the operator $H$.

from pytket.circuit import Circuit, Qubit
from pytket.pauli import Pauli, QubitPauliString
from pytket.utils import QubitPauliOperator
from pytket.utils.expectations import get_operator_expectation_value
from pytket.extensions.qiskit import AerBackend, AerStateBackend

# First, let's get some results on a toy circuit without using any measurement reduction:

shots_backend = AerBackend()
n_shots = 10000

c = Circuit(5)
c.H(4)
c.V(2)

c = shots_backend.get_compiled_circuit(c)
op = QubitPauliOperator(
    {
        QubitPauliString([Qubit(0)], [Pauli.Z]): 0.1,
        QubitPauliString(
            [Qubit(0), Qubit(1), Qubit(2), Qubit(3), Qubit(4)],
            [Pauli.Y, Pauli.Z, Pauli.X, Pauli.X, Pauli.Y],
        ): 0.4,
        QubitPauliString([Qubit(0), Qubit(1)], [Pauli.X, Pauli.X]): 0.2,
    }
)

shots_result = get_operator_expectation_value(c, op, shots_backend, n_shots)
print(shots_result)

# The result should be around 0.1, although as the shot simulator is stochastic this will be inexact. Let's test to check what the exact result should be using the statevector simulator:

state_backend = AerStateBackend()
state_result = get_operator_expectation_value(c, op, state_backend)
print(state_result)

# Now we can introduce measurement reduction. First we need to choose a strategy:

from pytket.partition import PauliPartitionStrat

# This first one only performs measurements on simultaneous Pauli operators when there is no cost incurred to do so.

strat = PauliPartitionStrat.NonConflictingSets
shots_result = get_operator_expectation_value(c, op, shots_backend, n_shots, strat)
print(shots_result)

# The other strategy we use groups together arbitrary Pauli operators, with the condition that all Pauli operators within a group commute. For an input circuit with $n$ qubits, our method requires the addition of up to $\frac{n(n-1)}{2}$ $CX$ gates to "diagonalise" the Pauli operators, although in practice we find that our techniques tend to give far lower gate overhead than this bound. We describe the procedure in an upcoming paper.

strat = PauliPartitionStrat.CommutingSets
shots_result = get_operator_expectation_value(c, op, shots_backend, n_shots, strat)
print(shots_result)

# Obviously, the `AerBackend` can be swapped out for the backend of a real machine.

# We will now demonstrate how to manually use the methods that are being called by `get_operator_expectation_value`. These methods are primarily intended for internal use, but we show them here for advanced users who may wish to have more information about the number of CX gates being added to each circuit, the number of circuits being run and other diagnostics.

from pytket.circuit import OpType
from pytket.partition import measurement_reduction

id_string = QubitPauliString()
qpt_list = [p for p in op._dict.keys() if (p != id_string)]
setup_1 = measurement_reduction(qpt_list, PauliPartitionStrat.NonConflictingSets)
print("Circuits required for measurement: {}".format(len(setup_1.measurement_circs)))

# This produced a `MeasurementSetup` object using the `NonConflictingSets` strategy of measurement reduction. This object holds a set of circuits which perform different basis changes, and the measurements associated with these circuits.
#
# There are 3 circuits held within the `MeasurementSetup` object, meaning that our original `QubitOperator` has been reduced from the 5 originally required measurements to 3.

for circ in setup_1.measurement_circs:
    print("CX gates for measurement: {}".format(circ.n_gates_of_type(OpType.CX)))

# No CX gates have been added for any of the required measurements. Now, we will change to the `CommutingSets` strategy.

setup_2 = measurement_reduction(qpt_list, PauliPartitionStrat.CommutingSets)
print("Circuits required for measurement: {}".format(len(setup_2.measurement_circs)))

# There are only 2 circuits required when expanding the scope of allowed simultaneous measurements. However, this comes at a cost:

for circ in setup_2.measurement_circs:
    print("CX gates for measurement: {}".format(circ.n_gates_of_type(OpType.CX)))

# A CX gate has been introduced to one of the measurement circuits, to convert to the correct Pauli basis set. On current devices which are extremely constrained in the number of entangling gates, the reduction in number of shots may not be worth the gate overhead.
