# # Compilation passes: tket example

# There are numerous ways to optimize circuits in `pytket`. In this notebook we will introduce the basics of compilation passes and how to combine and apply them.
#
# We assume familiarity with the `pytket` `Circuit` class. The objective is to transform one `Circuit` into another, equivalent, `Circuit`, that:
# * satisfies the connectivity constraints of a given architecture;
# * satisfies some further user-defined constraints (such as restricted gate sets);
# * minimizes some cost function (such as CX count).

# ## Passes

# The basic mechanism of compilation is the 'pass', which is a transform that can be applied to a circuit. There is an extensive library of passes in `pytket`, and several standard ways in which they can be combined to form new passes. For example:

from pytket.passes import DecomposeMultiQubitsCX

pass1 = DecomposeMultiQubitsCX()

# This pass converts all multi-qubit gates into CX and single-qubit gates. So let's create a circuit containing some non-CX multi-qubit gates:

from pytket.circuit import Circuit

circ = Circuit(3)
circ.CRz(0.5, 0, 1)
circ.T(2)
circ.CSWAP(2, 0, 1)

# In order to apply a pass to a circuit, we must first create a `CompilationUnit` from it. We can think of this as a 'bridge' between the circuit and the pass. The `CompilationUnit` is constructed from the circuit; the pass is applied to the `CompilationUnit`; and the transformed circuit is extracted from the `CompilationUnit`:

from pytket.predicates import CompilationUnit

cu = CompilationUnit(circ)
pass1.apply(cu)
circ1 = cu.circuit

# Let's have a look at the result of the transformation:

print(circ1.get_commands())

# ## Predicates

# Every `CompilationUnit` has associated with it a set of 'predicates', which describe target properties that can be checked against the circuit. There are many types of predicates available in `pytket`. For example, the `GateSetPredicate` checks whether all gates in a circuit belong to a particular set:

from pytket.predicates import GateSetPredicate
from pytket.circuit import OpType

pred1 = GateSetPredicate({OpType.Rz, OpType.T, OpType.Tdg, OpType.H, OpType.CX})

# When we construct a `CompilationUnit`, we may pass a list of target predicates as well as the circuit:

cu = CompilationUnit(circ, [pred1])

# To check whether the circuit associated to a `CompilationUnit` satisfies its target predicates, we can call the `check_all_predicates()` method:

cu.check_all_predicates()

pass1.apply(cu)
cu.check_all_predicates()

# We can also directly check whether a given circuit satisfies a given predicate, using the predicate's `verify()` method:

pred1.verify(circ1)

# ### In-place compilation

# The example above produced a new circuit, leaving the original circuit untouched. It is also possible to apply a pass to a circuit in-place:

DecomposeMultiQubitsCX().apply(circ)
print(circ.get_commands())

# ## Combining passes

# There are various ways to combine the elementary passes into more complex ones.
#
# To combine several passes in sequence, we use a `SequencePass`:

from pytket.passes import SequencePass, OptimisePhaseGadgets

seqpass = SequencePass([DecomposeMultiQubitsCX(), OptimisePhaseGadgets()])

# This pass will apply the two transforms in succession:

cu = CompilationUnit(circ)
seqpass.apply(cu)
circ1 = cu.circuit
print(circ1.get_commands())

# The `apply()` method for an elementary pass returns a boolean indicating whether or not the pass had any effect on the circuit. For a `SequencePass`, the return value indicates whether _any_ of the constituent passes had some effect.
#
# A `RepeatPass` repeatedly calls `apply()` on a pass until it returns `False`, indicating that there was no effect:

from pytket.passes import CommuteThroughMultis, RemoveRedundancies, RepeatPass

seqpass = SequencePass([CommuteThroughMultis(), RemoveRedundancies()])
reppass = RepeatPass(seqpass)

# This pass will repeatedly apply `CommuteThroughMultis` (which commutes single-qubit operations through multi-qubit operations where possible towards the start of the circuit) and `RemoveRedundancies` (which cancels inverse pairs, merges coaxial rotations and removes redundant gates before measurement) until neither pass has any effect on the circuit.
#
# Let's use `pytket`'s built-in visualizer to see the effect on a circuit:

from pytket.circuit.display import render_circuit_jupyter

circ = Circuit(3)
circ.X(0).Y(1).CX(0, 1).Z(0).Rx(1.3, 1).CX(0, 1).Rz(0.4, 0).Ry(0.53, 0).H(1).H(2).Rx(
    1.5, 2
).Rx(0.5, 2).H(2)

render_circuit_jupyter(circ)

cu = CompilationUnit(circ)
reppass.apply(cu)
circ1 = cu.circuit

render_circuit_jupyter(circ1)

# If we want to repeat a pass until the circuit satisfies some desired property, we first define a boolean function to test for that property, and then pass this function to the constructor of a `RepeatUntilSatisfied` pass:

from pytket.passes import RepeatUntilSatisfiedPass


def no_CX(circ):
    return circ.n_gates_of_type(OpType.CX) == 0


circ = (
    Circuit(2)
    .CX(0, 1)
    .X(1)
    .CX(0, 1)
    .X(1)
    .CX(0, 1)
    .X(1)
    .CX(0, 1)
    .Z(1)
    .CX(1, 0)
    .Z(1)
    .CX(1, 0)
)

custom_pass = RepeatUntilSatisfiedPass(seqpass, no_CX)
cu = CompilationUnit(circ)
custom_pass.apply(cu)
circ1 = cu.circuit

render_circuit_jupyter(circ1)

# The `RepeatWithMetricPass` provides another way of generating more sophisticated passes. This is defined in terms of a cost function and another pass type; the pass is applied repeatedly until the cost function stops decreasing.
#
# For example, suppose we wish to associate a cost to each gate in out circuit, with $n$-qubit gates having a cost of $n^2$:


def cost(circ):
    return sum(pow(len(x.args), 2) for x in circ)


# Let's construct a new circuit:

circ = Circuit(2)
circ.CX(0, 1).X(1).Y(0).CX(0, 1).X(1).Z(0).CX(0, 1).X(1).Y(0).CX(0, 1).Z(1).CX(1, 0).Z(
    1
).X(0).CX(1, 0)

# We will repeatedly apply `CommuteThroughMultis`, `DecomposeMultiQubitsCX` and `RemoveRedundancies` until the `cost` function stops decreasing:

from pytket.passes import RepeatWithMetricPass

pass1 = SequencePass(
    [CommuteThroughMultis(), DecomposeMultiQubitsCX(), RemoveRedundancies()]
)
pass2 = RepeatWithMetricPass(pass1, cost)

cu = CompilationUnit(circ)
pass2.apply(cu)
print(cu.circuit.get_commands())

# ## Targeting architectures

# If we are given a target architecture, we can generate passes tailored to it.
#
# In `pytket` an architecture is defined by a connectivity graph, i.e. a list of pairs of qubits capable of executing two-qubit operations. For example, we can represent a 5-qubit linear architecture, with qubits labelled `n[i]`, as follows:

from pytket.routing import Architecture
from pytket.circuit import Node

n = [Node("n", i) for i in range(5)]

arc = Architecture([[n[0], n[1]], [n[1], n[2]], [n[2], n[3]], [n[3], n[4]]])

# Suppose we have a circuit that we wish to run on this architecture:

circ = Circuit(5)
circ.CX(0, 1)
circ.H(0)
circ.Z(1)
circ.CX(0, 3)
circ.Rx(1.5, 3)
circ.CX(2, 4)
circ.X(2)
circ.CX(1, 4)
circ.CX(0, 4)

render_circuit_jupyter(circ)

# A mapping pass lets us rewrite this circuit for our architecture:

from pytket.passes import DefaultMappingPass

mapper = DefaultMappingPass(arc)
cu = CompilationUnit(circ)
mapper.apply(cu)
circ1 = cu.circuit

render_circuit_jupyter(circ1)

# If we want to decompose all SWAP and BRIDGE gates to CX gates in the final circuit, we can use another pass:

from pytket.passes import DecomposeSwapsToCXs

pass1 = DecomposeSwapsToCXs(arc)
pass1.apply(cu)
circ2 = cu.circuit

render_circuit_jupyter(circ2)

# Note that the pass we just ran also performed some clean-up: the SWAP gate was decomposed into three CX gates, one of which was cancelled by a preceding CX gate; the cancelling gates were removed from the circuit.
#
# Every compilation pass has associated sets of preconditions and postconditions on the circuit. If all preconditions are satisfied before the pass, all postconditions are guaranteed to be satisfied afterwards. When we apply a pass to a circuit, we can optionally pass `SafetyMode.Audit` as the second parameter; this will tell the pass to check all preconditions explicitly. By default, there is only limited checking of preconditions and `pytket` relies on the programmer assuring these.
#
# For example, the `NoClassicalControl` predicate is a precondition of the `PauliSimp` pass. Let's add a classically controlled gate to our circuit:

from pytket.passes import PauliSimp, SafetyMode
from pytket.circuit import Qubit, Bit

q = [Qubit("q", i) for i in range(5)]
c = Bit("c")
circ.add_bit(c)
circ.Measure(q[3], c)
circ.CY(q[0], q[1], condition_bits=[c], condition_value=1)
cu = CompilationUnit(circ)
try:
    PauliSimp().apply(cu, safety_mode=SafetyMode.Audit)
except RuntimeError as e:
    print("Error:", str(e))


# The preconditions and postconditions of all the elementary predicates are documented in their string representations:

PauliSimp()

# ## Backends and default passes

# A `pytket` `Backend` may have a default compilation pass, which will guarantee that the circuit can run on it. This is given by the `default_compilation_pass` property. For example, the default pass for Qiskit's `AerBackend` just converts all gates to U1, U2, U3 and CX:

from pytket.extensions.qiskit import AerBackend

b = AerBackend()
b.default_compilation_pass

# To compile a circuit using the default pass of a `Backend` we can simply use the `compile_circuit()` method:

circ = Circuit(2).X(0).Y(1).CRz(0.5, 1, 0)
circ1 = circ.copy()
b.compile_circuit(circ1)
render_circuit_jupyter(circ1)

# Every `Backend` will have a certain set of requirements that must be met by any circuit in order to run. These are exposed via the `required_predicates` property:

b.required_predicates

# We can test whether a given circuit satisfies these requirements using the `valid_circuit()` method:

b.valid_circuit(circ)

b.valid_circuit(circ1)
