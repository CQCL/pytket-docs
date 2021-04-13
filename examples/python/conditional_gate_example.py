# # Conditional Execution

# Whilst any quantum process can be created by performing "pure" operations delaying all measurements to the end, this is not always practical and can greatly increase the resource requirements. It is much more convenient to alternate quantum gates and measurements, especially if we can use the measurement results to determine which gates to apply (we refer to this more generic circuit model as "mixed" circuits, against the usual "pure" circuits). This is especially crucial for error correcting codes, where the correction gates are applied only if an error is detected.
#
# Measurements on many NISQ devices are often slow and it is hard to maintain other qubits in a quantum state during the measurement operation. Hence they may only support a single round of measurements at the end of the circuit, removing the need for conditional gate support. However, the ability to work with mid-circuit measurement and conditional gates is a feature in high demand for the future, and tket is ready for it.
#
# Not every circuit language specification supports conditional gates in the same way. The most popular circuit model at the moment is that provided by the OpenQASM language. This permits a very restricted model of classical logic, where we can apply a gate conditionally on the exact value of a classical register. There is no facility in the current spec for Boolean logic or classical operations to apply any function to the value prior to the equality check.
#
# For example, quantum teleportation can be performed by the following QASM:
# `OPENQASM 2.0;`
# `include "qelib1.inc";`
# `qreg a[2];`
# `qreg b[1];`
# `creg c[2];`
# `// Bell state between Alice and Bob`
# `h a[1];`
# `cx a[1],b[0];`
# `// Bell measurement of Alice's qubits`
# `cx a[0],a[1];`
# `h a[0];`
# `measure a[0] -> c[0];`
# `measure a[1] -> c[1];`
# `// Correction of Bob's qubit`
# `if(c==1) z b[0];`
# `if(c==3) z b[0];`
# `if(c==2) x b[0];`
# `if(c==3) x b[0];`

# tket supports a slightly more general form of conditional gates, where the gate is applied conditionally on the exact value of any list of bits. When adding a gate to a `Circuit` object, pass in the kwargs `condition_bits` and `condition_value` and the gate will only be applied if the state of the bits yields the binary representation of the value.

from pytket import Circuit

c = Circuit()
alice = c.add_q_register("a", 2)
bob = c.add_q_register("b", 1)
cr = c.add_c_register("c", 2)

# Bell state between Alice and Bob:

c.H(alice[1])
c.CX(alice[1], bob[0])

# Bell measurement of Alice's qubits:

c.CX(alice[0], alice[1])
c.H(alice[0])
c.Measure(alice[0], cr[0])
c.Measure(alice[1], cr[1])

# Correction of Bob's qubit:

c.Z(bob[0], condition_bits=[cr[0]], condition_value=1)
c.X(bob[0], condition_bits=[cr[1]], condition_value=1)

# Performing individual gates conditionally is sufficient, but can get cumbersome for larger circuits. Fortunately, tket's Box structures can also be performed conditionally, enabling this to be applied to large circuits with ease.
#
# For the sake of example, assume our device struggles to perform $X$ gates. We can surround it by $CX$ gates onto an ancilla, so measuring the ancilla will either result in the identity or $X$ being applied to the target qubit. If we detect that the $X$ fails, we can retry.

from pytket.circuit import CircBox, Qubit, Bit

checked_x = Circuit(2, 1)
checked_x.CX(0, 1)
checked_x.X(0)
checked_x.CX(0, 1)
checked_x.Measure(1, 0)
x_box = CircBox(checked_x)

c = Circuit()
target = Qubit("t", 0)
ancilla = Qubit("a", 0)
success = Bit("s", 0)
c.add_qubit(target)
c.add_qubit(ancilla)
c.add_bit(success)

# Try the X gate:

c.add_circbox(x_box, args=[target, ancilla, success])
# Try again if the X failed
c.add_circbox(
    x_box, args=[target, ancilla, success], condition_bits=[success], condition_value=0
)

# tket is able to apply essential compilation passes on circuits containing conditional gates. This includes decomposing any boxes into primitive gates and rebasing to other gatesets whilst preserving the conditional data.

from pytket.passes import DecomposeBoxes, RebaseIBM, SequencePass

comp_pass = SequencePass([DecomposeBoxes(), RebaseIBM()])

comp_pass.apply(c)

c

# A tket circuit can be converted to OpenQASM or other languages following the same classical model (e.g. Qiskit) when all conditional gates are dependent on the exact state of a single, whole classical register.

from pytket.extensions.qiskit import tk_to_qiskit

qc = tk_to_qiskit(c)

print(qc)

# This allows us to test our mixed programs using the `AerBackend`.

from pytket.extensions.qiskit import AerBackend

c = Circuit(2, 1)
c.Rx(0.3, 0)
c.Measure(0, 0)
# Set qubit 1 to be the opposite result and measure
c.X(1, condition_bits=[0], condition_value=0)
c.Measure(1, 0)

backend = AerBackend()
backend.compile_circuit(c)
counts = backend.get_counts(c, 1024)
print(counts)

# Beyond the ability to perform conditional gates, we might want to include more complex classical logic in the form of control flow, including loops, branching code, and jumps. Again, several proposed low-level quantum programming languages have sufficient expressivity to capture these, such as the Quil language.
#
# This control flow is hard to represent from within the circuit model, so tket contains the `Program` class, which builds up a flow graph whose basic blocks are individual circuits. Currently, you can add conditional blocks and loops, where the conditions are whether an individual classical bit is 1.

from pytket.program import Program

checked_x_p = Program(2, 1)
checked_x_p.append_circuit(checked_x)

p = Program(2, 1)
p.append(checked_x_p)
p.append_if_else(Bit(0), Program(2, 1), checked_x_p)

p

# Support for compiling and optimising `Program`s and full classical data manipulation will be added in a future version of tket.

# Try out mid-circuit measurement and conditional gate support on the `AerBackend` simulator, or ask about accessing the `HoneywellBackend` to try on a hardware device.
