---
file_format: mystnb
kernelspec:
  name: python3
---


# TKET Tips

## 1. How do I take the tensor product between two circuits?

You can compose two circuits side by side by taking the tensor product with the `*` operator

```{code-cell} ipython3
---
tags: [skip-execution]
---
circ1 * circ2 
```

Note that the two circuits need to have qubits with distinct names.
See the docs on circuit composition.

## 2. How can I export an image of my circuit?

There are multiple ways to do this. Firstly you can use the image export button in the interactive circuit renderer.

Try clicking the export button in the top right of the circuit diagram below.

```{code-cell} ipython3
from pytket import Circuit
from pytket.circuit.display import render_circuit_jupyter as draw

circ = Circuit(2).CX(0, 1).Rz(0.61, 1).CX(0, 1) # Build circuit
draw(circ)
```

You can also export pytket circuits to LaTeX with the [Circuit.to_latex_file](inv:#*.Circuit.to_latex_file) method. This is handy for using circuit images in papers if you like using the Quantikz library.

```{code-cell} ipython3
---
tags: [skip-execution]
---
from pytket import Circuit

circ = Circuit(2).CX(0, 1).Rz(0.61, 1).CX(0, 1) # Build circuit

circ.to_latex_file("phase_gadget.tex") # Generates a phase_gadget.tex file
```


## 3. Can I do symbolic calculations in pytket?

Yes! You can use the `pytket.utils.symbolic` module to calculate symbolic unitaries and statevectors for small pytket circuits.
Here we can use the [circuit_to_symbolic_unitary](inv:#*.circuit_to_symbolic_unitary) function to calculate the unitary of a small parameterised circuit. If using a jupyter notebook we get a nice LaTeX rendering of the matrix (see image)

```{code-cell} ipython3
from pytket import Circuit
from pytket.circuit.display import render_circuit_jupyter as draw
from pytket.utils.symbolic import circuit_to_symbolic_unitary
from sympy import symbols

a, b = symbols("a b") 
circ = Circuit(2)
circ.X(0).CRy(a, 0, 1).Rz(b, 0) 

draw(circ) # Draw circuit diagram
circuit_to_symbolic_unitary(circ) # Get the symbolic unitary matrix
```

## 4. Do I have to use a jupyter notebook to use these interactive circuit diagrams?

No you don't have to!  if you prefer using python scripts or the terminal instead of jupyter notebooks you can use the [view_browser](inv:#*.CircuitRenderer.view_browser) function to view the rendered circuit in a pop up browser window.

## 5. Clifford circuit basics in pytket

Clifford circuits are an important (non-universal) subclass of quantum circuits known to exhibit efficient classical simulation. The $\{H, S, CX\}$ gates are the typical Clifford generators. These circuits are particularly relevant for quantum error correction.

Its easy to check whether your pytket Circuit is Clifford by using the [CliffordCircuitPredicate](inv:#*.CliffordCircuitPredicate).


```{code-cell} ipython3
from pytket import Circuit
from pytket.predicates import CliffordCircuitPredicate

circ = Circuit(2).H(0).CX(0, 1).S(0).CX(0, 1).H(0) # Build Clifford Circuit

print(CliffordCircuitPredicate().verify(circ)) # prints True, circ is Clifford

circ.Rz(0.91, 0) # Add non-Clifford gate

print(CliffordCircuitPredicate().verify(circ)) # prints False, circ is non-Clifford
```

Given a circuit operation, we can check whether it is Clifford by using the [Op.is_clifford](inv:#*.Op.is_clifford) method



```{code-cell} ipython3
for command in circ:
    print(command.op, command.op.is_clifford())
    # Only the Rz gate is non-Clifford
```

Finally if you want to simulate large Clifford circuits you can access the Stim and Simplex simulators from pytket through their extension modules.

pytket-stim - https://github.com/CQCL/pytket-stim
pytket-pysimplex - https://github.com/CQCL/pytket-pysimplex


## 6. How can I check two quantum circuits for unitary equivalence?


```{code-cell} ipython3
from pytket import Circuit
from pytket.utils import compare_unitaries

# Create two simple circuits
circ1 = Circuit(3).CX(0, 2).CX(1, 2).Rz(0.74, 2).CX(1, 2).CX(0, 2)
circ2 = Circuit(3).CX(0, 1).CX(1, 2).Rz(0.74, 2).CX(1, 2).CX(0, 1)

# Simulate circuits to calculate the unitaries
unitary1 = circ1.get_unitary()
unitary2 = circ2.get_unitary()


# Compare up to a global phase
compare_unitaries(unitary1, unitary2)
```








