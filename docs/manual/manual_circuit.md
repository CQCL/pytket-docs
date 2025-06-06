---
file_format: mystnb
kernelspec:
  name: python3
---

# Circuit Construction

% Open DAG; equivalence up to trivial commutations/topological orderings

The {py:class}`~pytket.circuit.Circuit` class forms the unit of computation that we can send off to a quantum co-processor. Each instruction is to be performed in order, potentially parallelising when they use disjoint sets of (qu)bits. To capture this freedom of parallelisation, we treat the circuit as a Directed Acyclic Graph with a vertex for each instruction and directed edges following the paths of resources (e.g. qubits and bits) between them. This DAG representation describes the abstract circuit ignoring these trivial commutations/parallel instructions.

% Abstract computational model and semantics - map on combined quantum/classical state space

In general, we consider {py:class}`~pytket.circuit.Circuit` instances to represent open circuits; that is, they can be used within arbitrary contexts, so any input state can be supplied and there is no assumption on how the output state should be used. In practice, when we send a {py:class}`~pytket.circuit.Circuit` off to be executed, it will be run with all qubits in the initial state $|0\rangle^{\otimes n}$ and all bits set to $0$, then the classical outputs returned and the quantum state discarded.

Each circuit can be represented as a POVM on the combined quantum/classical state space by composing the representations assigned to each basic instruction. However, many use cases will live predominantly in the pure quantum space where the operations are simply unitaries acting on the quantum state. One practical distinction between these cases is the relevance of global phase: something that cannot be identified at the POVM level but has importance for pure states as it affects how we interpret the system and has an observable difference when the system is then coherently controlled. For example, an Rz gate and a U1 gate give equivalent effects on the quantum state but have a different global phase, meaning their unitaries *look* different, and a controlled-Rz is different from a controlled-U1. A {py:class}`~pytket.circuit.Circuit` will track global phase to make working with pure quantum processes easier, though this becomes meaningless once measurements and other classical interaction are applied and has no impact on the instructions sent to a quantum device when we eventually run it.

% There is no strict notion of control-flow or branching computation within a :py:class:`~pytket.circuit.Circuit`, meaning there is no facility to consider looping or arbitrary computation trees. This is likely to be an engineering limitation of all quantum devices produced in the near future, but this does not sacrifice the ability to do meaningful and interesting computation.

% Resource linearity - no intermediate allocation/disposal of (qu)bits

% Constructors (for integer-indexing)

Given the small scale and lack of dynamic quantum memories for both devices and simulations, we assume each qubit and bit is statically registered and hence each {py:class}`~pytket.circuit.Circuit` has the same number of inputs as outputs. The set of data units (qubits and bits) used by the {py:class}`~pytket.circuit.Circuit` is hence going to be constant, so we can define it up-front when we construct one. We can also optionally give it a name for easy identification.


```{code-cell} ipython3

from pytket import Circuit

trivial_circ = Circuit()        # no qubits or bits
quantum_circ = Circuit(4)       # 4 qubits and no bits
mixed_circ   = Circuit(4, 2)    # 4 qubits and 2 bits
named_circ   = Circuit(2, 2, "my_circ")
```

## Basic Gates

% Build up by appending to the end of the circuit

The bulk of the interaction with a {py:class}`~pytket.circuit.Circuit` object will be in building up the sequence of instructions to be run. The simplest way to do this is by adding each instruction in execution order to the end of the circuit.

% Constant gates

Basic quantum gates represent some unitary operation applied to some qubits. Adding them to a {py:class}`~pytket.circuit.Circuit` just requires specifying which qubits you want to apply them to. For controlled-gates, the convention is to give the control qubit(s) first, followed by the target qubit(s).


```{code-cell} ipython3

from pytket import Circuit

circ = Circuit(4)   # qubits are numbered 0-3
circ.X(0)           # first apply an X gate to qubit 0
circ.CX(1, 3)       # and apply a CX gate with control qubit 1 and target qubit 3
circ.Z(3)           # then apply a Z gate to qubit 3
circ.get_commands() # show the commands of the built circuit
```

% parameterised gates; parameter first, always in half-turns

For parameterised gates, such as rotations, the parameter is always given first. Because of the prevalence of rotations with angles given by fractions of $\pi$ in practical quantum computing, the unit for all angular parameters is the half-turn (1 half-turn is equal to $\pi$ radians).


```{code-cell} ipython3

from pytket import Circuit

circ = Circuit(2)
circ.Rx(0.5, 0)     # Rx of angle pi/2 radians on qubit 0
circ.CRz(0.3, 1, 0) # Controlled-Rz of angle 0.3pi radians with
                    #   control qubit 1 and target qubit 0
```

% Table of common gates, with circuit notation, unitary, and python command

% Wider variety of gates available via OpType

A large selection of common gates are available in this way, as listed in the API reference for the {py:class}`~pytket.circuit.Circuit` class. However, for less commonly used gates, a wider variety is available using the {py:class}`~pytket.circuit.OpType` enum, which can be added using the {py:meth}`~pytket.circuit.Circuit.add_gate` method.

% Example of adding gates using `add_gate`


```{code-cell} ipython3

from pytket import Circuit, OpType

circ = Circuit(5)
circ.add_gate(OpType.CnX, [0, 1, 4, 3])
    # add controlled-X with control qubits 0, 1, 4 and target qubit 3
circ.add_gate(OpType.XXPhase, 0.7, [0, 2])
    # add e^{-i (0.7 pi / 2) XX} on qubits 0 and 2
circ.add_gate(OpType.PhasedX, [-0.1, 0.5], [3])
    # adds Rz(-0.5 pi); Rx(-0.1 pi); Rz(0.5 pi) on qubit 3
```

The API reference for the {py:class}`~pytket.OpType` class details all available operations that can exist in a circuit.

In the above example, we asked for a `PhasedX` with angles `[-0.1, 0.5]`, but received `PhasedX(3.9, 0.5)`. `pytket` will freely map angles into the range $\left[0, r\right)$ for some range parameter $r$ that depends on the {py:class}`~pytket.circuit.OpType`, preserving the unitary matrix (including global phase).

% The vast majority of gates will also have the same number of inputs as outputs (following resource-linearity), with the exceptions being instructions that are read-only on some classical data.

## Measurements

% Non-destructive, single-qubit Z-measurements

Measurements go a step further by interacting with both the quantum and classical data. The convention used in `pytket` is that all measurements are non-destructive, single-qubit measurements in the $Z$ basis; other forms of measurements can be constructed by combining these with other operations.

% Adding measure gates

Adding a measurement works just like adding any other gate, where the first argument is the qubit to be measured and the second specifies the classical bit to store the result in.


```{code-cell} ipython3

from pytket import Circuit

circ = Circuit(4, 2)
circ.Measure(0, 0)  # Z-basis measurement on qubit 0, saving result in bit 0
circ.CX(1, 2)
circ.CX(1, 3)
circ.H(1)
circ.Measure(1, 1)  # Measurement of IXXX, saving result in bit 1
```

% Overwriting data in classical bits

Because the classical bits are treated as statically assigned locations, writing to the same bit multiple times will overwrite the previous value.


```{code-cell} ipython3

from pytket import Circuit

circ = Circuit(2, 1)
circ.Measure(0, 0)  # measure the first measurement
circ.CX(0, 1)
circ.Measure(1, 0)  # overwrites the first result with a new measurement
```

% Measurement on real devices could require a single layer at end, or sufficiently noisy that they appear destructive so require resets

Depending on where we plan on running our circuits, the backend or simulator might have different requirements on the structure of measurements in the circuits. For example, statevector simulators will only work deterministically for pure-quantum circuits, so will fail if any measures are present at all. More crucially, near-term quantum hardware almost always requires all measurements to occur in a single parallel layer at the end of the circuit (i.e. we cannot measure a qubit in the middle of the circuit).


```{code-cell} ipython3

from pytket import Circuit

circ0 = Circuit(2, 2)    # all measurements at end
circ0.H(1)
circ0.Measure(0, 0)
circ0.Measure(1, 1)

circ1 = Circuit(2, 2)    # this is DAG-equivalent to circ1, so is still ok
circ1.Measure(0, 0)
circ1.H(1)
circ1.Measure(1, 1)

circ2 = Circuit(2, 2)
    # reuses qubit 0 after measuring, so this may be rejected by a device
circ2.Measure(0, 0)
circ2.CX(0, 1)
circ2.Measure(1, 1)

circ3 = Circuit(2, 1)
    # overwriting the classical value means we have to measure qubit 0
    # before qubit 1; they won't occur simultaneously so this may be rejected
circ3.Measure(0, 0)
circ3.Measure(1, 0)
```

% `measure_all`

The simplest way to guarantee this is to finish the circuit by measuring all qubits. There is a short-hand function {py:meth}`~pytket.circuit.Circuit.measure_all` to make this easier.


```{code-cell} ipython3

from pytket import Circuit

# measure qubit 0 in Z basis and 1 in X basis
circ = Circuit(2, 2)
circ.H(1)
circ.measure_all()

# measure_all() adds bits if they are not already defined, so equivalently
circ = Circuit(2)
circ.H(1)
circ.measure_all()
```

On devices where mid-circuit measurements are available, they may be highly noisy and not apply just a basic projector on the quantum state. We can view these as "effectively destructive" measurements, where the qubit still exists but is in a noisy state. In this case, it is recommended to actively reset a qubit after measurement if it is intended to be reused.


```{code-cell} ipython3

from pytket import Circuit, OpType

circ = Circuit(2, 2)
circ.Measure(0, 0)
# Actively reset state to |0>
circ.Reset(0)
# Conditionally flip state to |1> to reflect measurement result
circ.X(0, condition_bits=[0], condition_value=1)
# Use the qubit as if the measurement was non-destructive
circ.CX(0, 1)
```

## Barriers

% Prevent compilation from rearranging gates around the barrier

% Some devices may use to provide timing information (no gate after the barrier will be started until all gates before the barrier have completed)

The concept of barriers comes from low-level classical programming. They exist as instructions but perform no active operation. Instead, their function is twofold:

- At compile-time, prevent the compiler from reordering operations around the barrier.
- At runtime, ensure that all operations before the barrier must have finished before any operations after the barrier start.

The intention is the same for {py:class}`~pytket.circuit.Circuit` s. Inserting barriers can be used to segment the program to easily spot how it is modified during compilation, and some quantum hardware uses barriers as the primary method of embedding timing information.

% `add_barrier`

Adding a barrier to a {py:class}`~pytket.circuit.Circuit` is done using the {py:meth}`~pytket.circuit.Circuit.add_barrier` method. In general, a barrier is placed on some subset of the (qu)bits to impose these ordering restrictions on those (qu)bits specifically (i.e. we don't care about reorders on the other (qu)bits).


```{code-cell} ipython3

from pytket import Circuit

circ = Circuit(4, 2)
circ.H(0)
circ.CX(1, 2)
circ.add_barrier([0, 1, 2, 3], [0, 1]) # add a barrier on all qubits and bits
circ.Measure(0, 0)
circ.Measure(2, 1)
```

## Registers and IDs

% When scaling up, want to attach semantic meaning to the names of resources and group them sensibly into related collections; IDs give names and registers allow grouping via indexed arrays; each id is a name and (n-dimensional) index

Using integer values to refer to each of our qubits and bits works fine for small-scale experiments, but when building up larger and more complicated programs, it is much easier to manage if we are able to name the resources to attach semantic meaning to them and group them into related collections. `pytket` enables this by supporting registers and named IDs.

Each unit resource is associated with a {py:class}`~pytket.unit_id.UnitID` (typically the subclasses {py:class}`~pytket.circuit.Qubit` or {py:class}`~pytket.circuit.Bit`), which gives a name and some ($n$-dimensional) index. A (quantum/classical) register is hence some collection of {py:class}`UnitID` s with the same name, dimension of index, and type of associated resource. These identifiers are not necessarily tied to a specific {py:class}`~pytket.circuit.Circuit` and can be reused between many of them.

% Can add to circuits individually or declare a 1-dimensional register (map from unsigned to id)

% Using ids to add gates

Named resources can be added to {py:class}`~pytket.circuit.Circuit` s individually, or by declaring a 1-dimensional register. Any of the methods for adding gates can then use these IDs.


```{code-cell} ipython3

from pytket import Circuit, Qubit, Bit

circ = Circuit()
qreg = circ.add_q_register("reg", 2)    # add a qubit register

anc = Qubit("ancilla")                  # add a named qubit
circ.add_qubit(anc)

par = Bit("parity", [0, 0])             # add a named bit with a 2D index
circ.add_bit(par)

circ.CX(qreg[0], anc)                   # add gates in terms of IDs
circ.CX(qreg[1], anc)
circ.Measure(anc, par)
```

% Query circuits to identify what qubits and bits it contains

A {py:class}`~pytket.circuit.Circuit` can be inspected to identify what qubits and bits it contains.


```{code-cell} ipython3

from pytket import Circuit, Qubit

circ = Circuit()
circ.add_q_register("a", 4)
circ.add_qubit(Qubit("b"))
circ.add_c_register("z", 3)

print(circ.qubits)
print(circ.bits)
```

% Restrictions on registers (circuit will reject ids if they are already in use or the index dimension/resource type is inconsistent with existing ids of that name)

To help encourage consistency of identifiers, a {py:class}`~pytket.circuit.Circuit` will reject a new (qu)bit or register if it disagrees with existing IDs with the same name; that is, it refers to a different resource type (qubit vs bit), the index has a different dimension, or some resource already exists with the exact same ID in the {py:class}`~pytket.circuit.Circuit`. Identifiers with the same register name do not have to have contiguous indices (many devices require non-contiguous indices because qubits may be taken offline over the lifetime of the device).


```{code-cell} ipython3
---
tags: [raises-exception]
---

from pytket import Circuit, Qubit, Bit

circ = Circuit()
# set up a circuit with qubit a[0]
circ.add_qubit(Qubit("a", 0))

# rejected because "a" is already a qubit register
circ.add_bit(Bit("a", 1))
```


```{code-cell} ipython3
---
tags: [raises-exception]
---

# rejected because "a" is already a 1D register
circ.add_qubit(Qubit("a", [1, 2]))
circ.add_qubit(Qubit("a"))
```


```{code-cell} ipython3
---
tags: [raises-exception]
---

# rejected because a[0] is already in the circuit
circ.add_qubit(Qubit("a", 0))
```

% Integer labels correspond to default registers (example of using explicit labels from `Circuit(n)`)

The basic integer identifiers are actually a special case, referring to the default qubit (`q[i]`) and bit (`c[i]`) registers. We can create the {py:class}`~pytket.unit_id.UnitID` using the nameless {py:class}`~pytket.unit_id.Qubit` and {py:class}`~pytket.unit_id.Bit` constructors.


```{code-cell} ipython3

from pytket import Circuit, Qubit, Bit

circ = Circuit(4, 2)
circ.CX(Qubit(0), Qubit("q", 1))    # same as circ.CX(0, 1)
circ.Measure(Qubit(2), Bit("c", 0)) # same as circ.Measure(2, 0)
```

% Rename with `rename_units` as long as the names after renaming would be unique and have consistent register typings

In some circumstances, it may be useful to rename the resources in the {py:class}`~pytket.circuit.Circuit`. Given a partial map on {py:class}`UnitID` s, {py:meth}`~pytket.circuit.Circuit.rename_units` will change the association of IDs to resources (as long as the final labelling would still have consistent types for all registers). Any unspecified IDs will be preserved.


```{code-cell} ipython3

from pytket import Circuit, Qubit, Bit

circ = Circuit(2, 2)
circ.add_qubit(Qubit("a", 0))

qubit_map = {
    Qubit("a", 0) : Qubit(3),
    Qubit(1) : Qubit("a", 0),
    Bit(0) : Bit("z", [0, 1]),
}
circ.rename_units(qubit_map)
print(circ.qubits)
print(circ.bits)
```

## Composing Circuits

% Appending matches units of the same id




Because {py:class}`Circuit` s are defined to have open inputs and outputs, it is perfectly natural to compose them by unifying the outputs of one with the inputs of another. Appending one {py:class}`Circuit` to the end of another matches the inputs and outputs with the same {py:class}`UnitID`.


```{code-cell} ipython3

from pytket import Circuit, Qubit, Bit

circ = Circuit(2, 2)
circ.CX(0, 1)
circ.Rz(0.3, 1)
circ.CX(0, 1)

measures = Circuit(2, 2)
measures.H(1)
measures.measure_all()

circ.append(measures)
circ
```

% If a unit does not exist in the other circuit, treated as composing with identity

```{note}
If one {py:class}`Circuit` lacks some unit present in the other, then we treat it as if it is an identity on that unit. In the extreme case where the {py:class}`Circuit` s are defined with disjoint sets of {py:class}`UnitID` s, the {py:meth}`Circuit.append` method will compose them in parallel.
```

To compose two circuits in parallel we can take tensor product using the * operator. This requires that the qubits in the circuits have distinct names.


```{code-cell} ipython3

from pytket import Circuit
from pytket.circuit.display import render_circuit_jupyter as draw

circ1 = Circuit()
j = circ1.add_q_register("j", 1)
circ1.Y(j[0])

circ2 = Circuit()
k = circ2.add_q_register("k", 2)
circ2.X(k[1])
circ2.CRz(0.64, k[1], k[0])

circ3 = circ1 * circ2 # Take the tensor product

draw(circ3)
```

If we attempt to form the tensor product of two circuits without distinct qubit names then we will get a {py:class}`RuntimeError` as the composition is not defined.


```{code-cell} ipython3
---
tags: [raises-exception]
---

from pytket import Circuit

circ_x = Circuit()
l_reg1 = circ_x.add_q_register("l", 1)

circ_y = Circuit()
l_reg2 = circ_y.add_q_register("l", 1)

circ_x * circ_y # Error as both circuits have l[0]

```

% Append onto different qubits with `append_with_map` (equivalent under `rename_units`)

% To change which units get unified, :py:meth:`~pytket.circuit.Circuit.append_with_map` accepts a dictionary of :py:class:`UnitID` s, mapping the units of the argument to units of the main :py:class:`~pytket.circuit.Circuit`.

% ```{code-cell} ipython3

% from pytket import Circuit, Qubit

% circ = Circuit()

% a = circ.add_q_register("a", 2)

% circ.Rx(0.2, a[0])

% circ.CX(a[0], a[1])

% next = Circuit()

% b = next.add_q_register("b", 2)

% next.Z(b[0])

% next.CZ(b[1], b[0])

% circ.append_with_map(next, {b[1] : a[0]})

% # This is equivalent to:

% # temp = next.copy()

% # temp.rename_units({b[1] : a[0]})

% # circ.append(temp)

To change which units get unified, we could use {py:meth}`Circuit.rename_units` as seen before. In the case where we just want to append a subcircuit like a gate, we can do this with {py:meth}`Circuit.add_circuit`.


```{code-cell} ipython3

from pytket import Circuit, Qubit

circ = Circuit()
a = circ.add_q_register("a", 2)
circ.Rx(0.2, a[0])
circ.CX(a[0], a[1])

next_circ = Circuit(2)
next_circ.Z(0)
next_circ.CZ(1, 0)

circ.add_circuit(next_circ, [a[1], a[0]])

# This is equivalent to:
# temp = next_circ.copy()
# temp.rename_units({Qubit(0) : a[1], Qubit(1) : a[0]})
# circ.append(temp)

draw(circ)
```

```{note}
This requires the subcircuit to be defined only over the default registers so that the list of arguments given to {py:meth}`Circuit.add_circuit` can easily be mapped.
```

## Statevectors and Unitaries

When working with quantum circuits we may want access to the quantum state prepared by our circuit. This can be helpful if we want to check whether our circuit construction is correct. The {py:meth}`Circuit.get_statevector` method will produce the statevector of our system after the circuit is applied. Here it is assumed that all the qubits are initialised in the $|0\rangle^{\otimes n}$ state.


```{code-cell} ipython3

from pytket import Circuit

circ = Circuit(2)
circ.H(0).CX(0, 1)
circ.get_statevector()
```

In addition {py:meth}`Circuit.get_unitary` can be used to numerically calculate the unitary matrix that will be applied by the circuit.


```{code-cell} ipython3

from pytket import Circuit

circ = Circuit(2)
circ.H(0).CZ(0, 1).H(1)
circ.get_unitary()
```

```{warning}
The unitary matrix of a quantum circuit is of dimension $(2^n \times 2^n)$ where $n$ is the number of qubits. The statevector will be a column vector with $2^n$ entries . Due to this exponential scaling it will in general be very inefficient to compute the unitary (or statevector) of a circuit. These functions are intended to be used for sanity checks and spotting mistakes in small circuits.
```

## Analysing Circuits

% Most basic form is to ask for the sequence of operations in the circuit; iteration produces `Command`s, containing an `Op` acting on `args`

After creating a {py:class}`~pytket.circuit.Circuit`, we will typically want to inspect what we have constructed to ensure that it agrees with the design we planned. The most basic form of this is to just get the object to return the sequence of operations back to us. Iterating through the {py:class}`~pytket.circuit.Circuit` object will give back the operations as {py:class}`~pytket.circuit.Command` s (specifying the operations performed and what (qu)bits they are performed on).

Because the {py:class}`~pytket.circuit.Circuit` class identifies circuits up to DAG equivalence, the sequence will be some topological sort of the DAG, but not necessarily identical to the order the operations were added to the {py:class}`~pytket.circuit.Circuit`.


```{code-cell} ipython3

from pytket import Circuit

circ = Circuit(3)
circ.CX(0, 1).CZ(1, 2).X(1).Rx(0.3, 0)

for com in circ: # equivalently, circ.get_commands()
    print(com.op, com.op.type, com.args)
    # NOTE: com is not a reference to something inside circ; this cannot be used to modify the circuit
```

% To see more succinctly, can visualise in circuit form or the underlying DAG

If you are working in a Jupyter environment, a {py:class}`~pytket.circuit.Circuit` can be rendered using html for inline display.


```{code-cell} ipython3

from pytket import Circuit
from pytket.circuit.display import render_circuit_jupyter as draw

circ = Circuit(3)
circ.CX(0, 1).CZ(1, 2).X(1).Rx(0.3, 0)
draw(circ) # Render interactive circuit diagram
```

```{note}
The pytket circuit renderer can represent circuits in the standard circuit model or in the ZX representation. Other interactive features include adjustable zoom, circuit wrapping and image export.
```

`pytket` also features methods to visualise the underlying circuit DAG graphically for easier visual inspection.


```{code-cell} ipython3

from pytket import Circuit
from pytket.utils import Graph

circ = Circuit(3)
circ.CX(0, 1).CZ(1, 2).X(1).Rx(0.3, 0)
Graph(circ).get_DAG()   # Displays in interactive python notebooks
```

The visualisation tool can also describe the interaction graph of a {py:class}`~pytket.circuit.Circuit` consisting of only one- and two-qubit gates -- that is, the graph of which qubits will share a two-qubit gate at some point during execution.

```{note}
The visualisations above are shown in ipython notebook cells. When working with a normal python script one can view rendered circuits in the browser with the {py:meth}`~pytket.circuit.display.view_browser` function from the display module.

There are also the methods {py:meth}`~pytket.utils.Graph.save_DAG` and {py:meth}`~pytket.utils.Graph.view_DAG` for saving and visualising the circuit DAG.
```


```{code-cell} ipython3

from pytket import Circuit
from pytket.utils import Graph

circ = Circuit(4)
circ.CX(0, 1).CZ(1, 2).ZZPhase(0.63, 2, 3).CX(1, 3).CY(0, 1)
Graph(circ).get_qubit_graph()
```

% Won't always want this much detail, so can also query for common metrics (gate count, specific ops, depth, T-depth and 2q-depth)

The full instruction sequence may often be too much detail for a lot of needs, especially for large circuits. Common circuit metrics like gate count and depth are used to approximate the difficulty of running it on a device, providing some basic tools to help distinguish different implementations of a given algorithm.


```{code-cell} ipython3

from pytket import Circuit

circ = Circuit(3)
circ.CX(0, 1).CZ(1, 2).X(1).Rx(0.3, 0)

print("Total gate count =", circ.n_gates)
print("Circuit depth =", circ.depth())
```

As characteristics of a {py:class}`~pytket.circuit.Circuit` go, these are pretty basic. In terms of approximating the noise level, they fail heavily from weighting all gates evenly when, in fact, some will be much harder to implement than others. For example, in the NISQ era, we find that most technologies provide good single-qubit gate times and fidelities, with two-qubit gates being much slower and noisier. On the other hand, looking forward to the fault-tolerant regime we will expect Clifford gates to be very cheap but the magic $T$ gates to require expensive distillation procedures [^cite_brav2005] [^cite_brav2012].

We can use the {py:class}`~pytket.circuit.OpType` enum class to look for the number of gates of a particular type. Additionally, the methods {py:meth}`~pytket.circuit.Circuit.n_1qb_gates`, {py:meth}`~pytket.circuit.Circuit.n_2qb_gates` and {py:meth}`~pytket.circuit.Circuit.n_nqb_gates` can be used to count the number of gates in terms of how many qubits they act upon irrespective of type.

We also define $G$-depth (for a subset of gate types $G$) as the minimum number of layers of gates in $G$ required to run the {py:class}`~pytket.circuit.Circuit`, allowing for topological reorderings. Specific cases of this like $T$-depth and $CX$-depth are common to the literature on circuit simplification [^cite_amy2014] [^cite_meij2020].


```{code-cell} ipython3

from pytket import Circuit, OpType
from pytket.circuit.display import render_circuit_jupyter as draw

circ = Circuit(3)
circ.T(0)
circ.CX(0, 1)
circ.CX(2, 0)
circ.add_gate(OpType.CnRy, [0.6], [0, 1, 2])
circ.T(2)
circ.CZ(0, 1)
circ.CZ(1, 2)
circ.T(1)

draw(circ) # draw circuit diagram

print("T gate count =", circ.n_gates_of_type(OpType.T))
print("#1qb gates =", circ.n_1qb_gates())
print("#2qb gates =", circ.n_2qb_gates())
print("#3qb gates =", circ.n_nqb_gates(3)) # count the single CnRy gate (n=3)
print("T gate depth =", circ.depth_by_type(OpType.T))
print("2qb gate depth =", circ.depth_by_type({OpType.CX, OpType.CZ}))
```

```{note}
Each of these metrics will analyse the {py:class}`~pytket.circuit.Circuit` "as is", so they will consider each Box as a single unit rather than breaking it down into basic gates, nor will they perform any non-trivial gate commutations (those that don't just follow by deformation of the DAG) or gate decompositions (e.g. recognising that a $CZ$ gate would contribute 1 to $CX$-count in practice).
```

Its also possible to count all the occurrences of each {py:class}`~pytket.circuit.OpType` using the {py:func}`~pytket.utils.stats.gate_counts` function from the {py:mod}`pytket.utils` module.


```{code-cell} ipython3

from pytket.utils.stats import gate_counts

gate_counts(circ)
```

We obtain a {py:class}`collections.Counter` object where the keys are the various {py:class}`~pytket.circuit.OpType` s and the values represent how frequently each {py:class}`~pytket.circuit.OpType` appears in our {py:class}`~pytket.circuit.Circuit`. This method summarises the gate counts obtained for the circuit shown above.

## Boxes

Working with individual basic gates is sufficient for implementing arbitrary circuits, but that doesn't mean it is the most convenient option. It is generally far easier to argue the correctness of a circuit's design when it is constructed using higher-level constructions. In `pytket`, the concept of a "Box" is to abstract away such complex structures as black-boxes within larger circuits.

Defining higher level subroutines as boxes is also beneficial from a circuit optimisation point of view. If the compiler can identify higher level structure in the circuit, this can be exploited to reduce the number of elementary gates in the compiled circuit. Examples of such optimisations can be seen in {py:class}`~pytket.circuit.ToffoliBox` which permutes the computational basis states and {py:class}`~pytket.circuit.ConjugationBox` which allows for more efficient controlled gates by exploiting circuit symmetry.

### Circuit Boxes

% Boxes abstract away complex structures as black-box units within larger circuits

% Simplest case is the `CircBox`

The simplest example of this is a {py:class}`~pytket.circuit.CircBox`, which wraps up another {py:class}`~pytket.circuit.Circuit` defined elsewhere into a single black-box. The difference between adding a {py:class}`~pytket.circuit.CircBox` and just appending the {py:class}`~pytket.circuit.Circuit` is that the {py:class}`~pytket.circuit.CircBox` allows us to wrap up and abstract away the internal structure of the subcircuit we are adding so it appears as if it were a single gate when we view the main {py:class}`~pytket.circuit.Circuit`.

Let's first build a basic quantum circuit which implements a simplified version of a Grover oracle and then add
it to another circuit as part of a larger algorithm.


```{code-cell} ipython3

from pytket.circuit import Circuit, OpType
from pytket.circuit.display import render_circuit_jupyter as draw

oracle_circ = Circuit(3, name="Oracle")
oracle_circ.X(0)
oracle_circ.X(1)
oracle_circ.X(2)
oracle_circ.add_gate(OpType.CnZ, [0, 1, 2])
oracle_circ.X(0)
oracle_circ.X(1)
oracle_circ.X(2)

draw(oracle_circ)
```

Now that we've built our circuit we can wrap it up in a {py:class}`~pytket.circuit.CircBox` and add it to a another circuit as a subroutine.


```{code-cell} ipython3

from pytket.circuit import CircBox

oracle_box = CircBox(oracle_circ)
circ = Circuit(3)
circ.H(0).H(1).H(2)
circ.add_gate(oracle_box, [0, 1, 2])

draw(circ)
```

See how the name of the circuit appears in the rendered circuit diagram. Clicking on the box will show the underlying circuit.

```{Note}
Despite the {py:class}`~pytket.circuit.Circuit` class having methods for adding each type of box, the {py:meth}`Circuit.add_gate` is sufficiently general to append any pytket OpType to a {py:class}`~pytket.circuit.Circuit`.
```

When constructing subroutines to implement quantum algorithms it is natural to distinguish different groups of qubits. For instance, in the quantum phase estimation algorithm (QPE) we would want to distinguish between state preparation qubits and ancillary qubits which are measured to yield an approximation of the phase.
The QPE can then be used as a subroutine in other algorithms: for example, integer factoring or estimating the ground state energy of some molecule. For more on the phase estimation algorithm see the [QPE example notebook](https://docs.quantinuum.com/tket/user-guide/examples/algorithms_and_protocols/phase_estimation.html)

For such algorithms we may wish to create a {py:class}`~pytket.circuit.CircBox` containing qubit registers with distinct names. Below we will show construction of a simplified quantum phase estimation circuit which we will then turn into a subroutine.


```{code-cell} ipython3

from pytket.circuit import Circuit

# Set up circuit registers
qpe_circ = Circuit(name="QPE")
a = qpe_circ.add_q_register("a", 2)
s = qpe_circ.add_q_register("s", 1)
c = qpe_circ.add_c_register("c", 2)

# Initial superposition
qpe_circ.H(a[0])
qpe_circ.H(a[1])

# Sequence of controlled unitaries
qpe_circ.CU1(0.94, a[1], s[0])
qpe_circ.CU1(0.94, a[0], s[0])
qpe_circ.CU1(0.94, a[0], s[0])

# 2-qubit QFT (simplified)
qpe_circ.H(a[0])
qpe_circ.CU1(0.5, a[1], a[0])
qpe_circ.H(a[1])
qpe_circ.SWAP(a[0], a[1])

# Measure qubits writing to the classical register
qpe_circ.measure_register(a, "c")

draw(qpe_circ)
```

Now that we have defined our phase estimation circuit we can use a {py:class}`CircBox` to define a reusable subroutine. This {py:class}`CircBox` will contain the state preparation and ancilla registers.


```{code-cell} ipython3

from pytket.circuit import CircBox

# Construct QPE subroutine
qpe_box = CircBox(qpe_circ)
```

Let's now create a circuit to implement the QPE algorithm where we prepare the $|1\rangle$ state in the state prep register with a single X gate.


```{code-cell} ipython3

# Construct simplified state preparation circuit
algorithm_circ = Circuit()
ancillas = algorithm_circ.add_q_register("ancillas", 2)
state = algorithm_circ.add_q_register("state", 1)
c = algorithm_circ.add_c_register("c", 2)
algorithm_circ.X(state[0])

draw(algorithm_circ)
```

We can then compose our subroutine registerwise by using {py:meth}`Circuit.add_circbox_with_regmap` method.

To use the method, we pass in a python dictionary which maps the registers inside the box to those outside. The keys are the register names inside the {py:class}`CircBox` and the values are the register names of the external {py:class}`Circuit`.
Note that the sizes of the registers used as keys and values must be equal.


```{code-cell} ipython3

# Append QPE subroutine to algorithm_circ registerwise
algorithm_circ.add_circbox_with_regmap(
    qpe_box, qregmap={"a": "ancillas", "s": "state"}, cregmap={"c": "c"}
)

draw(algorithm_circ)
```

Click on the QPE box in the diagram above to view the underlying circuit.

If we want add a {py:class}`~pytket.circuit.CircBox` across multiple registers we can do this with the {py:meth}`Circuit.add_circbox_regwise` method.

Lets first define a circuit with the register names `a`, `b` and `c`.


```{code-cell} ipython3

# Set up Circuit with registers a_reg, b_reg and c_reg
abc_circuit = Circuit()
a_reg = abc_circuit.add_q_register("a", 2)
b_reg = abc_circuit.add_q_register("b", 2)
c_reg = abc_circuit.add_q_register("c", 2)

# Add some gates
abc_circuit.H(a_reg[0])
abc_circuit.Ry(0.46, a_reg[1])
abc_circuit.CCX(a_reg[0], a_reg[1], c_reg[0])
draw(abc_circuit)
```

Now lets create a {py:class}`CircBox` containing some elementary gates and append it across the `b` and `c` registers with {py:meth}`Circuit.add_circbox_regwise`.


```{code-cell} ipython3

# Create subroutine
sub_circuit = Circuit(4, name="BC")
sub_circuit.CX(3, 2).CX(3, 1).CX(3, 0)
sub_circuit.H(3)
bc_subroutine = CircBox(sub_circuit)

# Append CircBox to the b_reg and c_reg registers (note empty list for classical registers)
abc_circuit.add_circbox_regwise(bc_subroutine, [b_reg, c_reg], [])

draw(abc_circuit)

```

### Boxes for Unitary Synthesis

It is possible to specify small unitaries from `numpy` arrays and embed them directly into circuits as boxes, which can then be synthesised into gate sequences during compilation.


```{code-cell} ipython3

from pytket.circuit import Circuit, Unitary1qBox, Unitary2qBox
import numpy as np

u1 = np.asarray([[2/3, (-2+1j)/3],
                    [(2+1j)/3, 2/3]])
u1box = Unitary1qBox(u1)

u2 = np.asarray([[0, 1, 0, 0],
                    [0, 0, 0, -1],
                    [1, 0, 0, 0],
                    [0, 0, -1j, 0]])
u2box = Unitary2qBox(u2)

circ = Circuit(3)
circ.add_unitary1qbox(u1box, 0)
circ.add_unitary2qbox(u2box, 1, 2)
circ.add_unitary1qbox(u1box, 2)
circ.add_unitary2qbox(u2box, 1, 0)

draw(circ)
```

```{note}
For performance reasons pytket currently only supports unitary synthesis up to three qubits. Three-qubit synthesis can be accomplished with {py:class}`~pytket.circuit.Unitary3qBox` using a similar syntax.
```

% `PauliExpBox` for simulations and general interactions

Also in this category of synthesis boxes is {py:class}`~pytket.circuit.DiagonalBox`. This allows synthesis of circuits for diagonal unitaries.
This box can be constructed by passing in a $(1 \times 2^n)$ numpy array representing the diagonal entries of the desired unitary matrix.

### Controlled Box Operations

If our subcircuit is a pure quantum circuit (i.e. it corresponds to a unitary operation), we can construct the controlled version that is applied coherently according to some set of control qubits. If all control qubits are in the $|1\rangle$ state, then the unitary is applied to the target system, otherwise it acts as an identity.


```{code-cell} ipython3

from pytket.circuit import Circuit, CircBox, QControlBox

sub = Circuit(2, name="V")
sub.CX(0, 1).Rz(0.2, 1).CX(0, 1)
sub_box = CircBox(sub)

# Define the controlled operation with 2 control qubits
cont = QControlBox(sub_box, 2)

circ = Circuit(4)
circ.add_gate(sub_box, [2, 3])
circ.Ry(0.3, 0).Ry(0.8, 1)

# Add to circuit with controls q[0], q[1], and targets q[2], q[3]
circ.add_gate(cont, [0, 1, 2, 3])

draw(circ)
```

As well as creating controlled boxes, we can create a controlled version of an arbitrary {py:class}`~pytket.circuit.Op` as follows.


```{code-cell} ipython3

from pytket.circuit import Op, OpType, QControlBox

op = Op.create(OpType.S)
ccs = QControlBox(op, 2)
```

```{note}
Whilst adding a control qubit is asymptotically efficient, the gate overhead is significant and can be hard to synthesise optimally, so using these constructions in a NISQ context should be done with caution.
```

In addition, we can construct a {py:class}`~pytket.circuit.QControlBox` from any other pure quantum box type in pytket.
For example, we can construct a multicontrolled $\sqrt{Y}$ operation as by first synthesising the base unitary with {py:class}`~pytket.circuit.Unitary1qBox` and then constructing a {py:class}`~pytket.circuit.QControlBox` from the box implementing $\sqrt{Y}$.


```{code-cell} ipython3

from pytket.circuit import Unitary1qBox, QControlBox
import numpy as np

# Unitary for sqrt(Y)
sqrt_y = np.asarray([[1/2+1j/2, -1/2-1j/2],
                        [1/2+1j/2, 1/2+1j/2]])

sqrt_y_box = Unitary1qBox(sqrt_y)
c2_root_y = QControlBox(sqrt_y_box, 2)
```

Normally when we deal with controlled gates we implicitly assume that the control state is the "all $|1\rangle$" state. So that the base gate is applied when all of the control qubits are all set to $|1\rangle$.

However its often useful to the flexibility to define the control state as some string of zeros and ones. Certain approaches to quantum algorithms with linear combination of unitaries (LCU) frequently make use of such gates.

A {py:class}`~pytket.circuit.QControlBox` accepts an optional `control_state` argument in the constructor. This is either a list of binary values or a single (big-endian) integer representing the binary string.

Lets now construct a multi-controlled Rz gate with the control state $|0010\rangle$. This means that the base operation will only be applied if the control qubits are in the state $|0010\rangle$.


```{code-cell} ipython3

from pytket.circuit import Circuit, Op, OpType, QControlBox

rz_op = Op.create(OpType.Rz, 0.61)
multi_controlled_rz = QControlBox(rz_op, n_controls=4, control_state=[False, False, True, False])

test_circ = Circuit(5)
test_circ.add_gate(multi_controlled_rz, test_circ.qubits)

draw(test_circ)
```

Notice how the circuit renderer shows both filled and unfilled circles on the control qubits. Filled circles correspond to $|1\rangle$ controls whereas empty circles represent $|0\rangle$. As pytket uses the big-endian ordering convention we read off the control state from the top to the bottom of the circuit.

### Pauli Exponential Boxes

Another notable construct that is common to many algorithms and high-level circuit descriptions is the exponential of a Pauli tensor:

$$
\begin{equation}
e^{-i \frac{\pi}{2} \theta P}\,, \quad P \in \{I, X, Y, Z\}^{\otimes n}
\end{equation}
$$

These occur very naturally in Trotterising evolution operators and native device operations.


```{code-cell} ipython3

from pytket.circuit import PauliExpBox
from pytket.pauli import Pauli

# Construct a PauliExpBox with a list of Paulis followed by the phase theta
xyyz = PauliExpBox([Pauli.X, Pauli.Y, Pauli.Y, Pauli.Z], -0.2)

pauli_circ = Circuit(4)

pauli_circ.add_gate(xyyz, [0, 1, 2, 3])
draw(pauli_circ)
```

To understand what happens inside a {py:class}`~pytket.circuit.PauliExpBox` let's take a look at the underlying circuit for $e^{-i \frac{\pi}{2}\theta XYYZ}$


```{code-cell} ipython3

from pytket.passes import DecomposeBoxes

DecomposeBoxes().apply(pauli_circ)

draw(pauli_circ)
```

All Pauli exponentials of the form above can be implemented in terms of a single Rz($\theta$) rotation and a symmetric chain of CX gates on either side together with some single qubit basis rotations. This class of circuit is called a Pauli gadget. The subset of these circuits corresponding to "Z only" Pauli strings are referred to as phase gadgets.

We see that the Pauli exponential $e^{i\frac{\pi}{2} \theta \text{XYYZ}}$ has basis rotations on the first three qubits. The V and Vdg gates rotate from the default Z basis to the Y basis and the Hadamard gate serves to change to the X basis.

These Pauli gadget circuits have interesting algebraic properties which are useful for circuit optimisation.

A Pauli gadget can be expressed as $V \, A \, V^\dagger$ where $V$ is the the circuit composed of CX gates and single qubit basis rotations on the right hand side of the Rz gate and $A$ is the Rz gate itself. This observation allows one to construct controlled Pauli gadgets much more efficiently. See the [blog post](https://docs.quantinuum.com/tket/blog/posts/controlled_gates/) on the {py:class}`~pytket.circuit.ConjugationBox` construct for more details.

For further discussion see the research publication on phase gadget synthesis [^cite_cowt2020]. Ideas from this paper are implemented in TKET as the {py:class}`~pytket.passes.OptimisePhaseGadgets` and {py:class}`~pytket.passes.PauliSimp` optimisation passes.

### Phase Polynomials

Now we move on to discuss another class of quantum circuits known as phase polynomials. Phase polynomial circuits are a special type of circuits that use the {CX, Rz} gateset.

A phase polynomial $p(x)$ is defined as a weighted sum of Boolean linear functions $f_i(x)$:

$$
\begin{equation}
p(x) = \sum_{i=1}^{2^n} \theta_i f_i(x)
\end{equation}
$$

A phase polynomial circuit $C$ has the following action on computational basis states $|x\rangle$:

$$
\begin{equation}
C: |x\rangle \longmapsto e^{2\pi i p(x)}|g(x)\rangle
\end{equation}
$$

Such a phase polynomial circuit can be synthesisied in pytket using the {py:class}`~pytket.circuit.PhasePolyBox`. A {py:class}`~pytket.circuit.PhasePolyBox` is constructed using the number of qubits, the qubit indices and a dictionary indicating whether or not a phase should be applied to specific qubits.

Finally a `linear_transformation` parameter needs to be specified:  this is a matrix encoding the linear permutation between the bitstrings $|x\rangle$ and $|g(x)\rangle$ in the equation above.


```{code-cell} ipython3

from pytket.circuit import PhasePolyBox

phase_poly_circ = Circuit(3)

qubit_indices = {Qubit(0): 0, Qubit(1): 1, Qubit(2): 2}

phase_polynomial = {
    (True, False, True): 0.333,
    (False, False, True): 0.05,
    (False, True, False): 1.05,
}

n_qb = 3

linear_transformation = np.array([[1, 1, 0], [0, 1, 0], [0, 0, 1]])

p_box = PhasePolyBox(n_qb, qubit_indices, phase_polynomial, linear_transformation)

phase_poly_circ.add_gate(p_box, [0, 1, 2])

draw(p_box.get_circuit())
```

### Multiplexors, Arbitrary State Preparation and {py:class}`~pytket.circuit.ToffoliBox`

In the context of quantum circuits a multiplexor is type of generalised multicontrolled gate. Multiplexors grant us the flexibility to specify different operations on target qubits for different control states.
To create a multiplexor we simply construct a dictionary where the keys are the state of the control qubits and the values represent the operation performed on the target.

Lets implement a multiplexor with the following logic. Here we treat the first two qubits as controls and the third qubit as the target.

> if control qubits in $|00\rangle$:
>
> : do Rz(0.3) on the third qubit
>
> else if control qubits in $|11\rangle$:
>
> : do H on the third qubit
>
> else:
>
> : do identity (i.e. do nothing)


```{code-cell} ipython3

from pytket.circuit import Op, OpType, MultiplexorBox

# Define both gates as an Op
rz_op = Op.create(OpType.Rz, 0.3)
h_op = Op.create(OpType.H)

op_map = {(False, False): rz_op, (True, True): h_op}
multiplexor = MultiplexorBox(op_map)

multi_circ = Circuit(3)
multi_circ.X(0).X(1)  # Put both control qubits in the state |1>
multi_circ.add_gate(multiplexor, [0, 1, 2])

draw(multi_circ)

```

Notice how in the example above the control qubits are both in the $|1\rangle$ state and so the multiplexor applies the Hadamard operation to the third qubit. If we calculate our statevector we see that the third qubit is in the
$|+\rangle = H|0\rangle$ state.


```{code-cell} ipython3

# Assume all qubits initialised to |0> here
# Amplitudes of |+> approx 0.707...
print("Statevector =", np.round(multi_circ.get_statevector().real, 4))
```

In addition to the general {py:class}`~pytket.circuit.MultiplexorBox` pytket has several other type of multiplexor box operations available.

| Multiplexor                                          | Description                                                                                      |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| {py:class}`~pytket.circuit.MultiplexorBox`           | The most general type of multiplexor (see above).                                                |
| {py:class}`~pytket.circuit.MultiplexedRotationBox`   | Multiplexor where the operation applied to the target is a rotation gate about a single axis.    |
| {py:class}`~pytket.circuit.MultiplexedU2Box`         | Multiplexor for uniformly controlled single qubit gates ( $U(2)$ operations).                    |
| {py:class}`~pytket.circuit.MultiplexedTensoredU2Box` | Multiplexor where the operation applied to the target is a tensor product of single qubit gates. |

One place where multiplexor operations are useful is in state preparation algorithms.

TKET supports the preparation of arbitrary quantum states via the {py:class}`~pytket.circuit.StatePreparationBox`. This box takes a  $(1\times 2^n)$ numpy array representing the $n$ qubit statevector where the entries represent the amplitudes of the quantum state.

Given the vector of amplitudes TKET will construct a box containing a sequence of multiplexors using the method outlined in [^cite_shen2004].

To demonstrate {py:class}`~pytket.circuit.StatePreparationBox` let's use it to prepare the W state.

$$
\begin{equation}
|W\rangle = \frac{1}{\sqrt{3}} \big(|001\rangle + |010\rangle + |100\rangle \big)
\end{equation}
$$


```{code-cell} ipython3

from pytket.circuit import StatePreparationBox

w_state = 1 / np.sqrt(3) * np.array([0, 1, 1, 0, 1, 0, 0, 0])

w_state_box = StatePreparationBox(w_state)

state_circ = Circuit(3)
state_circ.add_gate(w_state_box, [0, 1, 2])
```


```{code-cell} ipython3

# Verify state preparation
np.round(state_circ.get_statevector().real, 3) # 1/sqrt(3) approx 0.577
```

```{Note}
Generic state preparation circuits can be very complex with the gatecount and depth increasing rapidly with the size of the state. In the special case where the desired state has only real-valued amplitudes, only multiplexed Ry operations are needed to accomplish the state preparation.
```

For some use cases it may be desirable to reset all qubits to the $|0\rangle$ state prior to state preparation. This can be done using the `with_initial_reset` flag.


```{code-cell} ipython3

# Ensure all qubits initialised to |0>
w_state_box_reset = StatePreparationBox(w_state, with_initial_reset=True)

```

Finally let's consider another box type, namely the {py:class}`~pytket.circuit.ToffoliBox`. This box can be used to prepare an arbitrary permutation of the computational basis states.
To construct the box we need to specify the permutation as a key-value pair where the key is the input basis state and the value is output.
Let's construct a {py:class}`~pytket.circuit.ToffoliBox` to perform the following mapping:

$$
\begin{gather}
|001\rangle \longmapsto |111\rangle \\
|111\rangle \longmapsto |001\rangle \\
|100\rangle \longmapsto |000\rangle \\
|000\rangle \longmapsto |100\rangle
\end{gather}
$$

We can construct a {py:class}`~pytket.circuit.ToffoliBox` with a python dictionary where the basis states above are entered as key-value pairs.
For correctness if a basis state appears as key in the permutation dictionary then it must also appear and a value.


```{code-cell} ipython3

from pytket.circuit import ToffoliBox

# Specify the desired permutation of the basis states
mapping = {
    (False, False, True): (True, True, True),
    (True, True, True): (False, False, True),
    (True, False, False): (False, False, False),
    (False, False, False): (True, False, False),
}

# Define box to perform the permutation
perm_box = ToffoliBox(permutation=mapping)
```

This permutation of basis states can be achieved with purely classical operations {X, CCX}, hence the name {py:class}`~pytket.circuit.ToffoliBox`.
In pytket however, the permutation is implemented efficiently using a sequence of multiplexed rotations followed by a {py:class}`~pytket.circuit.DiagonalBox`.


```{code-cell} ipython3

draw(perm_box.get_circuit())

```

Finally let's append the {py:class}`~pytket.circuit.ToffoliBox` onto our circuit preparing our w state to perform the permutation of basis states specified above.


```{code-cell} ipython3

state_circ.add_gate(perm_box, [0, 1, 2])

draw(state_circ)
```


```{code-cell} ipython3

np.round(state_circ.get_statevector().real, 3)

```

Looking at the statevector calculation we see that our {py:class}`~pytket.circuit.ToffoliBox` has exchanged the coefficients of our w state so that the non-zero coefficients are now on the $|000\rangle$ and $|111\rangle$ bitstrings with the coefficient of $|010\rangle$ remaining unchanged.

## Importing/Exporting Circuits




`pytket` {py:class}`~pytket.circuit.Circuit` s can be natively serialized and deserialized from JSON-compatible dictionaries, using the {py:meth}`Circuit.to_dict` and {py:meth}`Circuit.from_dict` methods. This is the method of serialization which supports the largest class of circuits, and provides the highest fidelity.


```{code-cell} ipython3

import tempfile
import json
from pytket import Circuit, OpType

circ = Circuit(2)
circ.Rx(0.1, 0)
circ.CX(0, 1)
circ.YYPhase(0.2, 0, 1)

circ_dict = circ.to_dict()
print(circ_dict)

with tempfile.TemporaryFile('w+') as fp:
    json.dump(circ_dict, fp)
    fp.seek(0)
    new_circ = Circuit.from_dict(json.load(fp))

draw(new_circ)
```

% Support other frameworks for easy conversion of existing code and enable freedom to choose preferred input system and use available high-level packages

`pytket` also supports interoperability with a number of other quantum software frameworks and programming languages for easy conversion of existing code and to provide users the freedom to choose their preferred input system and use available high-level packages.

% OpenQASM (doubles up as method of serialising circuits)

OpenQASM is one of the current industry standards for low-level circuit description languages, featuring named quantum and classical registers, parameterised subroutines, and a limited form of conditional execution. Having bidirectional conversion support allows this to double up as a method of serializing circuits for later use.
Though less expressive than native dictionary serialization, it is widely supported and so serves as a platform-independent method of storing circuits.


```{code-cell} ipython3

from pytket.qasm import circuit_from_qasm, circuit_to_qasm_str
import tempfile, os

fd, path = tempfile.mkstemp(".qasm")
os.write(fd, """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0], q[1];
cz q[1], q[0];
measure q -> c;
""".encode())
os.close(fd)
circ = circuit_from_qasm(path)
os.remove(path)

print(circuit_to_qasm_str(circ)) # print QASM string
```

% Quipper

The OpenQASM converters do not support circuits with [implicit qubit permutations](#implicit-qubit-permutations). This means that if a circuit contains such a permutation it will be ignored when exported to OpenQASM format.


The core `pytket` package additionally features a converter from Quipper, another circuit description language.


```{code-cell} ipython3

from pytket.quipper import circuit_from_quipper
import tempfile, os

fd, path = tempfile.mkstemp(".quip")
os.write(fd, """Inputs: 0:Qbit, 1:Qbit, 2:Qbit
QGate["X"](0)
QGate["Y"](1)
QGate["Z"](2)
Outputs: 0:Qbit, 1:Qbit, 2:Qbit
""".encode())
os.close(fd)
circ = circuit_from_quipper(path)
draw(circ)
os.remove(path)
```

```{note}
There are a few features of the Quipper language that are not supported by the converter, which are outlined in the {py:mod}`pytket.quipper` documentation.
```

% Extension modules; example with qiskit, cirq, pyquil; caution that they may not support all gate sets or features (e.g. conditional gates with qiskit only)

Converters for other quantum software frameworks can optionally be included by installing the corresponding extension module. These are additional PyPI packages with names `pytket-X`, which extend the `pytket` namespace with additional features to interact with other systems, either using them as a front-end for circuit construction and high-level algorithms or targeting simulators and devices as backends.

For example, installing the `pytket-qiskit` package will add the {py:func}`~pytket.extensions.qiskit.tk_to_qiskit` and {py:func}`~pytket.extensions.qiskit.qiskit_to_tk` methods which convert between the {py:class}`~pytket.circuit.Circuit` class from `pytket` and {py:class}`~qiskit.circuit.QuantumCircuit`.


```{code-cell} ipython3

from qiskit import QuantumCircuit
from math import pi

qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 1)
qc.rz(pi/2, 1)
print(qc)
```

We can convert this {py:class}`~qiskit.circuit.QuantumCircuit` to a pytket {py:class}`Circuit`, append some gates and then convert back.


```{code-cell} ipython3

from pytket.extensions.qiskit import qiskit_to_tk, tk_to_qiskit

circ = qiskit_to_tk(qc)
circ.CX(1, 2)
circ.measure_all()

qc2 = tk_to_qiskit(circ)
print(qc2)
```

## Symbolic Circuits

% Common pattern to construct many circuits with a similar shape and different gate parameters

% Main example of ansatze for variational algorithms

In practice, it is very common for an experiment to use many circuits with similar structure but with varying gate parameters. In variational algorithms like VQE and QAOA, we are trying to explore the energy landscape with respect to the circuit parameters, realised as the angles of rotation gates. The only differences between iterations of the optimisation procedure are the specific angles of rotations in the circuits. Because the procedures of generating and compiling the circuits typically won't care what the exact angles are, we can define the circuits abstractly, treating each parameter as an algebraic symbol. The circuit generation and compilation can then be pulled outside of the optimisation loop, being performed once and for all rather than once for each set of parameter values.

% Symbolic parameters of circuits defined as sympy symbols

% Gate parameters can use arbitrary symbolic expressions

[sympy](https://docs.sympy.org/latest/index.html) is a widely-used python package for symbolic expressions and algebraic manipulation, defining a sympy {py:class}`~sympy.core.symbol.Symbol` objects to represent algebraic variables and using them in sympy [Expression](https://docs.sympy.org/latest/explanation/glossary.html#term-Expression) s to build mathematical statements and arithmetic expressions. Symbolic circuits are managed in `pytket` by defining the circuit parameters as {py:class}`sympy.Symbol` s, which can be passed in as arguments to the gates and later substituted for concrete values.


```{code-cell} ipython3

from pytket import Circuit, OpType
from sympy import Symbol

a = Symbol("alpha")
b = Symbol("beta")

circ = Circuit(2)
circ.Rx(a, 0)
circ.Rx(-2*a, 1)
circ.CX(0, 1)
circ.YYPhase(b, 0, 1)

draw(circ)

s_map = {a:0.3, b:1.25}
circ.symbol_substitution(s_map)
print(circ.free_symbols())
```

% Instantiate by mapping symbols to values (in half-turns)

It is important to note that the units of the parameter values will still be in half-turns, and so may need conversion to/from radians if there is important semantic meaning to the parameter values. This can either be done at the point of interpreting the values, or by embedding the conversion into the {py:class}`~pytket.circuit.Circuit`.


```{code-cell} ipython3

from pytket import Circuit
from sympy import Symbol, pi

a = Symbol("alpha")     # suppose that alpha is given in radians
circ = Circuit(2)       # convert alpha to half-turns when adding gates
circ.Rx(a/pi, 0).CX(0, 1).Ry(-a/pi, 0)

s_map = {a: pi/4}
circ.symbol_substitution(s_map)
draw(circ)
```

% Can use substitution to replace by arbitrary expressions, including renaming alpha-conversion

Substitution need not be for concrete values, but is defined more generally to allow symbols to be replaced by arbitrary expressions, including other symbols. This allows for alpha-conversion or to look at special cases with redundant parameters.


```{code-cell} ipython3

from pytket import Circuit
from sympy import symbols

a, b, c = symbols("a b c")
circ = Circuit(2)
circ.Rx(a, 0).Rx(b, 1).CX(0, 1).Ry(c, 0).Ry(c, 1)

s_map = {a: 2*a, c: a}  # replacement happens simultaneously, and not recursively
circ.symbol_substitution(s_map)
draw(circ)
```

% Can query circuit for its free symbols

% Warning about devices and some optimisations will not function with symbolic gates

There are currently no simulators or devices that can run symbolic circuits algebraically, so every symbol must be instantiated before running. At any time, you can query the {py:class}`~pytket.circuit.Circuit` object for the set of free symbols it contains to check what would need to be instantiated before it can be run.


```{code-cell} ipython3

from pytket import Circuit
from sympy import symbols

a, b = symbols("a, b")
circ = Circuit(2)
circ.Rx(a, 0).Rx(b, 1).CZ(0, 1)
circ.symbol_substitution({a:0.2})

print(circ.free_symbols())
print(circ.is_symbolic())   # returns True when free_symbols() is non-empty
```

```{note}
There are some minor drawbacks associated with symbolic compilation. When using {py:class}`~pytket.passes.EulerAngleReduction` or quaternions for merging adjacent rotation gates, the resulting angles are given by some lengthy trigonometric expressions which cannot be evaluated down to just a number when one of the original angles was parameterised; this can lead to unhelpfully long expressions for the angles of some gates in the compiled circuit. It is also not possible to apply the {py:class}`pytket.passes.KAKDecomposition` pass to simplify a parameterised circuit, so that pass will only apply to non-parameterised subcircuits, potentially missing some valid opportunities for optimisation.
```

```{seealso}
To see how to use symbolic compilation in a variational experiment, have a look at our [VQE (UCCSD) example](https://docs.quantinuum.com/tket/user-guide/examples/algorithms_and_protocols/ucc_vqe.html).
```

### Symbolic unitaries and states

In {py:mod}`pytket.utils.symbolic` we provide functions {py:func}`~pytket.utils.symbolic.circuit_to_symbolic_unitary`, which can calculate the unitary representation of a possibly symbolic circuit, and {py:func}`~pytket.utils.symbolic.circuit_apply_symbolic_statevector`, which can apply a symbolic circuit to an input statevector and return the output state (effectively simulating it).


```{code-cell} ipython3

from pytket.utils.symbolic import circuit_apply_symbolic_statevector, circuit_to_symbolic_unitary
from sympy import Symbol, pi

a = Symbol("alpha")
circ = Circuit(2)
circ.Rx(a/pi, 0).CX(0, 1)

# All zero input state is assumed if no initial state is provided
display(circuit_apply_symbolic_statevector(circ))
circuit_to_symbolic_unitary(circ)

```

The unitaries are calculated using the unitary representation of each [OpType](inv:pytket:*:doc#optype) , and according to the default ILO BasisOrder convention used in backends ILO BasisOrder convention used in backends(manual_backend.md#interpreting-results).

The outputs are sympy [ImmutableMatrix](https://docs.sympy.org/latest/modules/matrices/immutablematrices.html) objects, and use the same symbols as in the circuit, so can be further substituted and manipulated.
The conversion functions use the [sympy Quantum Mechanics module](https://docs.sympy.org/latest/modules/physics/quantum/index.html), see also the {py:func}`~pytket.utils.symbolic.circuit_to_symbolic_gates` and {py:func}`~pytket.utils.symbolic.circuit_apply_symbolic_qubit` functions to see how to work with those objects directly.

```{warning}
Unitaries corresponding to circuits with $n$ qubits have dimensions $2^n \times 2^n$, so are computationally very expensive to calculate. Symbolic calculation is also computationally costly, meaning calculation of symbolic unitaries is only really feasible for very small circuits (of up to a few qubits in size). These utilities are provided as way to test the design of small subcircuits to check they are performing the intended unitary. Note also that as mentioned above, compilation of a symbolic circuit can generate long symbolic expressions; converting these circuits to a symbolic unitary could then result in a matrix object that is very hard to work with or interpret.
```

## Advanced Circuit Construction Topics

### Custom parameterised Gates

% Custom gates can also be defined with custom parameters

% Define by giving a symbolic circuit and list of symbols to bind

% Instantiate upon inserting into circuit by providing concrete parameters

% Any symbols that are not bound are treated as free symbols in the global scope

The {py:class}`~pytket.circuit.CircBox` construction is good for subroutines where the instruction sequence is fixed. The {py:class}`~pytket.circuit.CustomGateDef` construction generalises this to construct parameterised subroutines by binding symbols in the definition circuit and instantiating them at each instance. Any symbolic {py:class}`~pytket.circuit.Circuit` can be provided as the subroutine definition. Remaining symbols that are not bound are treated as free symbols in the global scope.


```{code-cell} ipython3

from pytket.circuit import Circuit, CustomGateDef
from sympy import symbols

a, b = symbols("a b")
def_circ = Circuit(2)
def_circ.CZ(0, 1)
def_circ.Rx(a, 1)
def_circ.CZ(0, 1)
def_circ.Rx(-a, 1)
def_circ.Rz(b, 0)

gate_def = CustomGateDef.define("MyCRx", def_circ, [a])
circ = Circuit(3)
circ.add_custom_gate(gate_def, [0.2], [0, 1])
circ.add_custom_gate(gate_def, [0.3], [0, 2])

draw(circ)
print(circ.free_symbols()) # Print remaining free symbols
```

### Clifford Tableaux

The Clifford (a.k.a. stabilizer) fragment of quantum theory is known to exhibit efficient classical representations of states and unitaries. This allows for short descriptions that can fully characterise a state/unitary and efficient circuit simulation. Whilst the Clifford group can be characterised as the operations generated by `CX`, `H`, and `S` gates with qubit initialisation in the $|0\rangle$ state, it is also the largest group of operations under which the Pauli group is closed, i.e. for any tensor of Paulis $P$ and Clifford operation $C$, $CPC^\dagger$ is also a tensor of Paulis.

Any state $|\psi\rangle$ in the Clifford fragment is uniquely identified by those tensors of Pauli operators that stabilize it (those $P$ such that $P|\psi\rangle = |\psi\rangle$). These stabilizers form a group of size $2^n$ for an $n$ qubit state, but it is sufficient to identify $n$ independent generators to specify the group. If a Clifford gate $C$ is applied to the state, each generator $P$ can be updated to $P' = CPC^\dagger$ since $C|\psi\rangle = CP|\psi\rangle = (CPC^\dagger)C|\psi\rangle$. We can therefore characterise each Clifford operation by its actions on generators of the Pauli group, giving us the Clifford tableau form. In `pytket`, the {py:class}`~pytket.tableau.UnitaryTableau` class uses the binary symplectic representation from Aaronson and Gottesman [^cite_aaro2004].


```{code-cell} ipython3

from pytket.circuit import OpType, Qubit
from pytket.tableau import UnitaryTableau

tab = UnitaryTableau(3)
tab.apply_gate_at_end(OpType.S, [Qubit(0)])
tab.apply_gate_at_end(OpType.CX, [Qubit(1), Qubit(2)])
print(tab)
```

The way to interpret this format is that, for example, the top rows state that the unitary transforms $X_0 I_1 I_2$ at its input to $-Y_0 I_1 I_2$ at its output, and it transforms $I_0 X_1 I_2$ to $I_0 X_1 X_2$.

The primary use for tableaux in `pytket` is as a scalable means of specifying a Clifford unitary for insertion into a circuit as a Box. This can then be decomposed into basic gates during compilation.


```{code-cell} ipython3

from pytket.circuit import Circuit
from pytket.tableau import UnitaryTableauBox

box = UnitaryTableauBox(
    np.asarray([[1, 1, 0], [0, 1, 0], [0, 0, 1]], dtype=bool),
    np.asarray([[0, 0, 0], [0, 0, 0], [0, 0, 1]], dtype=bool),
    np.asarray([0, 0, 1], dtype=bool),
    np.asarray([[0, 0, 0], [0, 1, 0], [0, 0, 0]], dtype=bool),
    np.asarray([[1, 0, 0], [1, 1, 0], [0, 0, 1]], dtype=bool),
    np.asarray([1, 0, 1], dtype=bool)
)

circ = Circuit(3)
circ.add_gate(box, [0, 1, 2])
draw(circ)
```

After the tableau is added to a circuit, it can be readily decomposed to Clifford gates.


```{code-cell} ipython3

from pytket.passes import DecomposeBoxes, RemoveRedundancies

DecomposeBoxes().apply(circ)
RemoveRedundancies().apply(circ) # Eliminate some redundant gates

draw(circ)
```

```{note}
The current decomposition method for tableaux is not particularly efficient in terms of gate count, so consider using higher optimisation levels when compiling to help reduce the gate cost.
```

The data structure used here for tableaux is intended for compilation use. For fast simulation of Clifford circuits, we recommend using the {py:class}`StimBackend` from `pytket-stim`, the {py:class}`SimplexBackend` from `pytket-pysimplex` (optimized for large sparse circuits), or the {py:class}`~pytket.extensions.qiskit.AerBackend` from `pytket-qiskit`. Future versions of `pytket` may include improved decompositions from tableaux, as well as more flexible tableaux to represent stabilizer states, isometries, and diagonalisation circuits.

### Classical and conditional operations

Moving beyond toy circuit examples, many applications of quantum computing
require looking at circuits as POVMs for extra expressivity, or introducing
error-correcting schemes to reduce the effective noise. Each of these requires
performing measurements mid-circuit and then performing subsequent gates
conditional on the classical value of the measurement result, or on the results
of calculations on the results.

Any `pytket` operation can be made conditional at the point of adding it to
the {py:class}`~pytket.circuit.Circuit` by providing the `condition` kwarg. The interpretation
of `circ.G(q, condition=reg[0])` is: "if the  bit `reg[0]` is set to 1, then
perform `G(q)`".
Conditions on more complicated expressions over the values of {py:class}`~pytket.unit_id.Bit` and {py:class}`~pytket.unit_id.BitRegister` are also
possible, expressed as conditions on the results of expressions involving
bitwise AND (&), OR (|) and XOR (^) operations. In the case of registers, you
can also express arithmetic operations: add (+), subtract (-), multiply (\*),
floor/integer division (//), left shift (\<\<) and right shift (>>).
For example a gate can be made conditional on the result of a bitwise XOR of
registers `a`, `b`, and `c` being larger than 4 by writing `circ.G(q,
condition=reg_gt(a ^ b ^ c, 4))`.
When such a condition is added, the result of the expression is written to a
scratch bit or register, and the gate is made conditional on the value of the
scratch variable.
For comparison of registers, a special `RangePredicate` type is used to encode
the result of the comparison onto a scratch bit.
See the {py:mod}`pytket.circuit.logic_exp` documentation for more on the
possible expressions and predicates.


```{code-cell} ipython3

from pytket.circuit import (
    Circuit,
    BitRegister,
    if_bit,
    if_not_bit,
    reg_eq,
    reg_geq,
    reg_gt,
    reg_leq,
    reg_lt,
    reg_neq,
)

# create a circuit and add quantum and classical registers
circ = Circuit()
qreg = circ.add_q_register("q", 10)
reg_a = circ.add_c_register("a", 4)
# another way of adding a register to the Circuit
reg_b = BitRegister("b", 3)
circ.add_c_register(reg_b)
reg_c = circ.add_c_register("c", 3)

# if (reg_a[0] == 1)
circ.H(qreg[0], condition=reg_a[0])
circ.X(qreg[0], condition=if_bit(reg_a[0]))

# if (reg_a[2] == 0)
circ.T(qreg[1], condition=if_not_bit(reg_a[2]))

# compound logical expressions
circ.Z(qreg[0], condition=(reg_a[2] & reg_a[3]))
circ.Z(qreg[1], condition=if_not_bit(reg_a[2] & reg_a[3]))
big_exp = reg_a[0] | reg_a[1] ^ reg_a[2] & reg_a[3]
# syntactic sugar for big_exp = BitOr(reg_a[0], BitXor(reg_a[1], BitAnd(reg_a[2], reg_a[3])))
circ.CX(qreg[1], qreg[2], condition=big_exp)

# Register comparisons

# if (reg_a == 3)
circ.H(qreg[2], condition=reg_eq(reg_a, 3))
# if (reg_c != 6)
circ.Y(qreg[4], condition=reg_neq(reg_c, 5))
# if (reg_b < 6)
circ.X(qreg[3], condition=reg_lt(reg_b, 6))
# if (reg_b > 3)
circ.Z(qreg[5], condition=reg_gt(reg_b, 3))
# if (reg_c <= 6)
circ.S(qreg[6], condition=reg_leq(reg_c, 6))
# if (reg_a >= 3)
circ.T(qreg[7], condition=reg_geq(reg_a, 3))
# compound register expressions
big_reg_exp = (reg_a & reg_b) | reg_c
circ.CX(qreg[3], qreg[4], condition=reg_eq(big_reg_exp, 3))
```

So far we've looked at conditioning the application of a gate on bits,
registers, or expressions over those. We can also write some more standard
classical computations by assigning the result of some computation to output
bits or registers. We can also set the value or copy the contents of one resource
in to another. Note in the examples below to express something like `<var> =
<exp>` we use circuit methods (like {py:meth}`~pytket.circuit.Circuit.add_c_setreg`, or
{py:meth}`~pytket.circuit.Circuit.add_clexpr_from_logicexp`) that take `<exp>` as the first input and `<var>`
as the second. Note that these classical operations can be conditional on other
classical operations, just like quantum operations.


```{code-cell} ipython3

from pytket.circuit import Circuit, reg_gt

# create a circuit and add some classical registers
circ = Circuit()
reg_a = circ.add_c_register("a", 4)
reg_b = circ.add_c_register("b", 3)
reg_c = circ.add_c_register("c", 3)


# Write to classical registers

# a = 3
circ.add_c_setreg(3, reg_a)
# a[0] = 1
circ.add_c_setbits([True], [reg_a[0]])
# Copy: b = a
# b is smaller than a so the first 3 bits of a will be copied
circ.add_c_copyreg(reg_a, reg_b)
# b[1] = a[2]
circ.add_c_copybits([reg_a[2]], [reg_b[1]])

# Conditional classical operation

# if (a > 1) b = 3
circ.add_c_setreg(3, reg_b, condition=reg_gt(reg_a, 1))

# Write out the results of logical expressions

# c = a ^ b
circ.add_clexpr_from_logicexp(reg_a ^ reg_b, reg_c)
# c[0] = a[1] & b[2]
circ.add_clexpr_from_logicexp(reg_a[1] & reg_b[2], [reg_c[0]])

# Register arithmetic

# c = a + b // c (note the use of the floor divide symbol)
circ.add_clexpr_from_logicexp(reg_a + reg_b // reg_c, reg_c)
# a = a - b * c
circ.add_clexpr_from_logicexp(reg_a - reg_b * reg_c, reg_a)
# a = a << 2
circ.add_clexpr_from_logicexp(reg_a << 2, reg_a)
# c = b >> 1
circ.add_clexpr_from_logicexp(reg_b >> 1, reg_c)

```

```{warning}
Unlike most uses of readouts in `pytket`, register comparisons expect a little-endian value, e.g. in the above example `condition=reg_eq(reg_a, 3)` (representing the little-endian binary string `110000...`) is triggered when `reg_a[0]` and `reg_a[1]` are in state `1` and the remainder of the register is in state `0`.
```

```{note}
This feature is only usable on a limited selection of devices and simulators which support conditional gates or classical operations.

The {py:class}`~pytket.extensions.qiskit.AerBackend` (from [pytket-qiskit](inv:pytket-qiskit:std:doc#index)) can support the OpenQasm model,
where gates can only be conditional on an entire classical register being an
exact integer value. Bitwise logical operations and register arithmetic are not supported.
Therefore only conditions of the form
`condition=reg_eq(reg, val)` are valid.

The {py:class}`~pytket.extensions.quantinuum.QuantinuumBackend` (from [pytket-quantinuum](inv:pytket-quantinuum:std:doc#index))
can support the full range of expressions and comparisons shown above.
```

### Circuit-Level Operations

% Produce a new circuit, related by some construction

% Dagger and transpose of unitary circuits

Systematic modifications to a {py:class}`~pytket.circuit.Circuit` object can go beyond simply adding gates one at a time. For example, given a unitary {py:class}`~pytket.circuit.Circuit`, we may wish to generate its inverse for the purposes of uncomputation of ancillae or creating conjugation circuits to diagonalise an operator as in the sample below.


```{code-cell} ipython3

from pytket import Circuit

# we want a circuit for E = exp(-i pi (0.3 XX + 0.1 YY))
circ = Circuit(2)

# find C such that C; Rx(a, 0); C^dagger performs exp(-i a pi XX/2)
# and C; Rz(b, 1); C^dagger performs exp(-i b pi YY/2)
conj = Circuit(2)
conj.V(0).V(1).CX(0, 1)
conj_dag = conj.dagger()

circ.append(conj)
circ.Rx(0.6, 0).Rz(0.2, 1)
circ.append(conj_dag)
```

Generating the transpose of a unitary works similarly using {py:meth}`~pytket.circuit.Circuit.transpose`.

```{note}
Since it is not possible to construct the inverse of an arbitrary POVM, the {py:meth}`~pytket.circuit.Circuit.dagger` and {py:meth}`~pytket.circuit.Circuit.transpose` methods will fail if there are any measurements, resets, or other operations that they cannot directly invert.
```

% Gradients wrt symbolic parameters
### Implicit Qubit Permutations

% DAG is used to help follow paths of resources and represent circuit up to trivial commutations

% SWAPs (and general permutations) can be treated as having the same effect as physically swapping the wires, so can be reduced to edges connecting predecessors and successors; makes it possible to spot more commutations and interacting gates for optimisations

The {py:class}`~pytket.circuit.Circuit` class is built as a DAG to help follow the paths of resources and represent the circuit canonically up to trivial commutations. Each of the edges represents a resource passing from one instruction to the next, so we could represent SWAPs (and general permutations) by connecting the predecessors of the SWAP instruction to the opposite successors. This eliminates the SWAP instruction from the graph (meaning we would no longer perform the operation at runtime) and could enable the compiler to spot additional opportunities for simplification. One example of this in practice is the ability to convert a pair of CXs in opposite directions to just a single CX (along with an implicit SWAP that isn't actually performed).


```{code-cell} ipython3

from pytket import Circuit
from pytket.utils import Graph

circ = Circuit(4)
circ.CX(0, 1)
circ.CX(1, 0)
circ.Rx(0.2, 1)
circ.CZ(0, 1)

print(circ.get_commands())
Graph(circ).get_DAG()
```


```{code-cell} ipython3

from pytket.passes import CliffordSimp

CliffordSimp().apply(circ)
print(circ.get_commands())
print(circ.implicit_qubit_permutation())
Graph(circ).get_DAG()
```

% This encapsulates naturality of the symmetry in the resource theory, effectively shifting the swap to the end of the circuit

This procedure essentially exploits the naturality of the symmetry operator in the resource theory to push it to the end of the circuit: the `Rx` gate has moved from qubit `q[1]` to `q[0]` and can be commuted through to the start. This is automatically considered when composing two {py:class}`~pytket.circuit.Circuit` s together.

% Means that tracing the path from an input might reach an output labelled by a different resource

% Can inspect the implicit permutation at the end of the circuit

% Two circuits can have the same sequence of gates but different unitaries (and behave differently under composition) because of implicit permutations

The permutation has been reduced to something implicit in the graph, and we now find that tracing a path from an input can reach an output with a different {py:class}`UnitID`. Since this permutation is missing in the command sequence, simulating the circuit would only give the correct state up to a permutation of the qubits. This does not matter when running on real devices where the final quantum system is discarded after use, but is detectable when using a statevector simulator. This is handled automatically by `pytket` backends, but care should be taken when reading from the {py:class}`~pytket.circuit.Circuit` directly - two quantum {py:class}`~pytket.circuit.Circuit` s can have the same sequence of instructions but different unitaries because of implicit permutations. This permutation information is typically dropped when exporting to another software framework. The {py:meth}`~pytket.circuit.Circuit.implicit_qubit_permutation` method can be used to inspect such a permutation.

### Modifying Operations Within Circuits

Symbolic parameters allow one to construct a circuit with some not-yet-assigned parameters, and later (perhaps after some optimization), to instantiate them with different values. Occasionally, however, one may desire more flexibility in substituting operations within a circuit. For example, one may wish to apply controls from a certain qubit to certain operations, or to insert or remove certain operations.

This can be achieved with `pytket`, provided the mutable operations are tagged during circuit construction with identifying names (which can be arbitrary strings). If two operations are given the same name then they belong to the same "operation group"; they can (and must) then be substituted simultaneously.

Both primitive gates and boxes can be tagged and substituted in this way. The only constraint is that the signature (number and order of quantum and classical wires) of the substituted operation must match that of the original operation in the circuit. (It follows that all operations in the same group must have the same signature. An attempt to add an operation with an existing name with a mismatching signature will fail.)

To add gates or boxes to a circuit with specified op group names, simply pass the name as a keyword argument `opgroup` to the method that adds the gate or box. To substitute all operations in a group, use the {py:meth}`~pytket.circuit.Circuit.substitute_named` method. This can be used to substitute a circuit, an operation or a box into the existing circuit.


```{code-cell} ipython3

from pytket.circuit import Circuit, CircBox

circ = Circuit(3)
circ.Rz(0.25, 0, opgroup="rotations")
circ.CX(0, 1)
circ.Ry(0.75, 1, opgroup="rotations")
circ.H(2, opgroup="special one")
circ.CX(2, 1)
cbox = CircBox(Circuit(2, name="P").S(0).CY(0, 1))
circ.add_gate(cbox, [0, 1], opgroup="Fred")
circ.CX(1, 2, opgroup="Fred")

draw(circ)
```


```{code-cell} ipython3

from pytket.circuit import Op

# Substitute a new 1-qubit circuit for all ops in the "rotations" group:
newcirc = Circuit(1).Rx(0.125, 0).Ry(0.875, 0)
circ.substitute_named(newcirc, "rotations")

# Replace the "special one" with a different op:
newop = Op.create(OpType.T)
circ.substitute_named(newop, "special one")

# Substitute a box for the "Fred" group:
newcbox = CircBox(Circuit(2, name="Q").H(1).CX(1, 0))
circ.substitute_named(newcbox, "Fred")

draw(circ)
```

Note that when an operation or box is substituted in, the op group name is retained (and further substitutions can be made). When a circuit is substituted in, the op group name disappears.

To remove an operation, one can replace it with an empty circuit.

To add a control to an operation, one can add the original operation as a {py:class}`~pytket.circuit.CircBox` with one unused qubit, and substitute it with a {py:class}`~pytket.circuit.QControlBox`.


```{code-cell} ipython3

from pytket.circuit import QControlBox

def with_empty_qubit(op: Op) -> CircBox:
    n_qb = op.n_qubits
    return CircBox(Circuit(n_qb + 1).add_gate(op, list(range(1, n_qb + 1))))

def with_control_qubit(op: Op) -> QControlBox:
    return QControlBox(op, 1)

c = Circuit(3)
h_op = Op.create(OpType.H)
cx_op = Op.create(OpType.CX)
h_0_cbox = with_empty_qubit(h_op)
h_q_qbox = with_control_qubit(h_op)
cx_0_cbox = with_empty_qubit(cx_op)
cx_q_qbox = with_control_qubit(cx_op)
c.X(0).Y(1)
c.add_gate(h_0_cbox, [2, 0], opgroup="hgroup")
c.add_gate(cx_0_cbox, [2, 0, 1], opgroup="cxgroup")
c.Y(0).X(1)
c.add_gate(h_0_cbox, [2, 1], opgroup="hgroup")
c.add_gate(cx_0_cbox, [2, 1, 0], opgroup="cxgroup")
c.X(0).Y(1)
c.substitute_named(h_q_qbox, "hgroup")
c.substitute_named(cx_q_qbox, "cxgroup")

draw(c)
```

[^cite_cowt2020]: Cowtan, A. and Dilkes, S. and Duncan and R., Simmons, W and Sivarajah, S., 2020. Phase Gadget Synthesis for Shallow Circuits. Electronic Proceedings in Theoretical Computer Science

[^cite_shen2004]: V.V. Shende and S.S. Bullock and I.L. Markov, 2004. Synthesis of quantum-logic circuits. \{IEEE} Transactions on Computer-Aided Design of Integrated Circuits and Systems

[^cite_aaro2004]: Aaronson, S. and Gottesman, D., 2004. Improved Simulation of Stabilizer Circuits. Physical Review A, 70(5), p.052328.

[^cite_brav2005]: Bravyi, S. and Kitaev, A., 2005. Universal quantum computation with ideal Clifford gates and noisy ancillas. Physical Review A, 71(2), p.022316.

[^cite_brav2012]: Bravyi, S. and Haah, J., 2012. Magic-state distillation with low overhead. Physical Review A, 86(5), p.052329.

[^cite_amy2014]: Amy, M., Maslov, D. and Mosca, M., 2014. Polynomial-time T-depth optimization of Clifford+ T circuits via matroid partitioning. IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems, 33(10), pp.1476-1489.

[^cite_meij2020]: de Griend, A.M.V. and Duncan, R., 2020. Architecture-aware synthesis of phase polynomials for NISQ devices. arXiv preprint arXiv:2004.06052.
