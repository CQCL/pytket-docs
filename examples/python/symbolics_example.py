# # Symbolic compilation: tket example
#
# Motivation: in compilation, particularly of hybrid classical-quantum variational algorithms in which the structure of a circuit remains constant but the parameters of some gates change, it can be useful to compile using symbolic parameters and optimise the circuit without knowledge of what these parameters will be instantiated to afterwards.
#
# In this tutorial, we will show how to compile a circuit containing mathematical symbols, and then instantiate the symbols afterwards. To do this, you need to have `pytket` installed. Run:
#
# `pip install pytket`
#
# We will also be using the circuit drawing tool from IBM's Qiskit, although this is only for visualisation and is not necessary to do symbolic compilation using pytket. To use the converter:
# ```
# `pip install pytket_qiskit`
# ```
# To begin, we will import the `Circuit` and `Transform` classes from `pytket`, and the `fresh_symbol` method from `pytket.circuit`.

from pytket.circuit import Circuit, fresh_symbol
from pytket.transform import Transform

# Now, we can construct a circuit containing symbols. You can ask for symbols by calling the `fresh_symbol` method with a string as an argument. This string represents the preferred symbol name; if this has already been used elsewhere, an appropriate suffix of the form `_x`, with `x` a natural number, will be added to generate a new symbol, as shown below:

a = fresh_symbol("a")
a1 = fresh_symbol("a")
print(a)
print(a1)

# We are going to make a circuit using just three 'phase gadgets': `Rz` gates surrounded by ladders of `CX` gates.

b = fresh_symbol("b")
circ = Circuit(4)
circ.CX(0, 1)
circ.CX(1, 2)
circ.CX(2, 3)
circ.Rz(a, 3)
circ.CX(2, 3)
circ.CX(1, 2)
circ.CX(0, 1)
circ.CX(3, 2)
circ.CX(2, 1)
circ.CX(1, 0)
circ.Rz(b, 0)
circ.CX(1, 0)
circ.CX(2, 1)
circ.CX(3, 2)
circ.CX(0, 1)
circ.CX(1, 2)
circ.CX(2, 3)
circ.Rz(0.5, 3)
circ.CX(2, 3)
circ.CX(1, 2)
circ.CX(0, 1)

# Now we can use IBM's Qiskit visualiser to display the circuit. For more explanation of our converters, see the `transform_example` notebook. Note that Qiskit can, conveniently, use symbolics as well.

from pytket.extensions.qiskit import tk_to_qiskit


def print_tkcirc_via_qiskit(tkcirc):
    qiskit_qcirc = tk_to_qiskit(tkcirc)
    print(qiskit_qcirc)


print_tkcirc_via_qiskit(circ)

# Now let's use a transform to shrink the circuit. For more detail on transforms, see the `transform_example` notebook.

Transform.OptimisePhaseGadgets().apply(circ)
print_tkcirc_via_qiskit(circ)

# Note that the type of gate has changed to `U1`, but the phase gadgets have been successfully combined. The `U1` gate is an IBM-specific gate that is equivalent to an `Rz`.
#
# We can now instantiate the symbols with some desired values. We make a dictionary, with each key a symbol name, and each value a double. Note that this value is in units of 'half-turns', in which a value of $1$ corresponds to a rotation of $\pi$.
#
# Before instantiating our parameters we make a copy of the circuit, so that we can repeat the exercise without the need for recompilation.

symbol_circ = circ.copy()

symbol_dict = {a: 0.5, b: 0.75}
circ.symbol_substitution(symbol_dict)

print_tkcirc_via_qiskit(circ)

# Because this symbol substitution was called on the copy, we still have our original symbolic circuit.

print_tkcirc_via_qiskit(symbol_circ)

# Note: the expression tree for this symbolic expression is very small, consisting of only a couple of different operations, but tket is capable of handling large and complex expressions containing many different types of operation, such as trigonometric functions.
#
# It is usually possible to instantiate a symbolic circuit with specific values that allow further optimisation: for example, if we had chosen $a=1.5$ and $b=0$, this circuit would be reduce to the identity. If there are likely to be many parameters set to trivial values (such as $0$ or $1$), it can be beneficial to perform further optimisation after instantiation.
