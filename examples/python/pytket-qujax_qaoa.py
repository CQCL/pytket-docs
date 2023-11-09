# # Symbolic circuits with `pytket-qujax`
# In this notebook we will show how to manipulate symbolic circuits with the `pytket-qujax` extension. In particular, we will consider a QAOA and an Ising Hamiltonian.

from pytket import Circuit
from pytket.circuit.display import render_circuit_jupyter
from jax import numpy as jnp, random, value_and_grad, jit
from sympy import Symbol
import matplotlib.pyplot as plt

import qujax
from pytket.extensions.qujax import tk_to_qujax

# # QAOA
# The Quantum Approximate Optimization Algorithm (QAOA), first introduced by [Farhi et al.](https://arxiv.org/pdf/1411.4028.pdf), is a quantum variational algorithm used to solve optimization problems. It consists of a unitary $U(\beta, \gamma)$ formed by alternate repetitions of $U(\beta)=e^{-i\beta H_B}$ and $U(\gamma)=e^{-i\gamma H_P}$, where $H_B$ is the mixing Hamiltonian and $H_P$ the problem Hamiltonian. The goal is to find the optimal parameters that minimize $H_P$.
# Given a depth $d$, the expression of the final unitary is $U(\beta, \gamma) = U(\beta_d)U(\gamma_d)\cdots U(\beta_1)U(\gamma_1)$. Notice that for each repetition the parameters are different.
#
# ## Problem Hamiltonian
# QAOA uses a problem dependent ansatz. Therefore, we first need to know the problem that we want to solve. In this case we will consider an Ising Hamiltonian with only $Z$ interactions. Given a set of pairs (or qubit indices) $E$, the problem Hamiltonian will be:
#
# $$
# \begin{equation}
# H_P = \sum_{(i, j) \in E}\alpha_{ij}Z_iZ_j,
# \end{equation}
# $$
#
# where $\alpha_{ij}$ are the coefficients.
# Let's build our problem Hamiltonian with random coefficients and a set of pairs for a given number of qubits:

n_qubits = 4
hamiltonian_qubit_inds = [(0, 1), (1, 2), (0, 2), (1, 3)]
hamiltonian_gates = [["Z", "Z"]] * (len(hamiltonian_qubit_inds))

# Notice that in order to use the random package from jax we first need to define a seeded key

seed = 13
key = random.PRNGKey(seed)
coefficients = random.uniform(key, shape=(len(hamiltonian_qubit_inds),))

print("Gates:\t", hamiltonian_gates)
print("Qubits:\t", hamiltonian_qubit_inds)
print("Coefficients:\t", coefficients)

# ## Variational Circuit
# Before constructing the circuit, we still need to select the mixing Hamiltonian. In our case, we will be using $X$ gates in each qubit, so $H_B = \sum_{i=1}^{n}X_i$, where $n$ is the number of qubits. Notice that the unitary $U(\beta)$, given this mixing Hamiltonian, is an $X$ rotation in each qubit with angle $\beta$.
# As for the unitary corresponding to the problem Hamiltonian, $U(\gamma)$, it has the following form:
#
# $$
# \begin{equation}
# U(\gamma)=\prod_{(i, j) \in E}e^{-i\gamma\alpha_{ij}Z_i Z_j}
# \end{equation}
# $$
#
# The operation $e^{-i\gamma\alpha_{ij}Z_iZ_j}$ can be performed using two CNOT gates with qubit $i$ as control and qubit $j$ as target and a $Z$ rotation in qubit $j$ in between them, with angle $\gamma\alpha_{ij}$.
# Finally, the initial state used, in general, with the QAOA is an equal superposition of all the basis states. This can be achieved adding a first layer of Hadamard gates in each qubit at the beginning of the circuit.

# With all the building blocks, let's construct the symbolic circuit using tket. Notice that in order to define the parameters, we use the ```Symbol``` object from the `sympy` package. More info can be found in this [documentation](https://cqcl.github.io/pytket/manual/manual_circuit.html#symbolic-circuits). In order to later convert the circuit to qujax, we need to return the list of symbolic parameters as well.


def qaoa_circuit(n_qubits, depth):
    circuit = Circuit(n_qubits)
    p_keys = []

    # Initial State
    for i in range(n_qubits):
        circuit.H(i)

    for d in range(depth):
        # Hamiltonian unitary
        gamma_d = Symbol(f"γ_{d}")
        for index in range(len(hamiltonian_qubit_inds)):
            pair = hamiltonian_qubit_inds[index]
            coef = coefficients[index]

            circuit.CX(pair[0], pair[1])
            circuit.Rz(gamma_d * coef, pair[1])
            circuit.CX(pair[0], pair[1])
            circuit.add_barrier(range(0, n_qubits))
        p_keys.append(gamma_d)

        # Mixing unitary
        beta_d = Symbol(f"β_{d}")
        for i in range(n_qubits):
            circuit.Rx(beta_d, i)
        p_keys.append(beta_d)

    return circuit, p_keys


depth = 3
circuit, keys = qaoa_circuit(n_qubits, depth)

keys

# Let's check the circuit:

render_circuit_jupyter(circuit)

# # Now for `qujax`
# The `pytket.extensions.qujax.tk_to_qujax` function will generate a parameters -> statetensor function for us. However, in order to convert a symbolic circuit we first need to define the `symbol_map`. This object maps each symbol key to their corresponding index. In our case, since the object `keys` contains the symbols in the correct order, we can simply construct the dictionary as follows:

symbol_map = {keys[i]: i for i in range(len(keys))}

symbol_map

# Then, we invoke the `tk_to_qujax` with both the circuit and the symbolic map.

param_to_st = tk_to_qujax(circuit, symbol_map=symbol_map)

# And we also construct the expectation map using the problem Hamiltonian via qujax:

st_to_expectation = qujax.get_statetensor_to_expectation_func(
    hamiltonian_gates, hamiltonian_qubit_inds, coefficients
)

param_to_expectation = lambda param: st_to_expectation(param_to_st(param))

# # Training process
# We construct a function that, given a parameter vector, returns the value of the cost function and the gradient.
# We also `jit` to avoid recompilation, this means that the expensive `cost_and_grad` function is compiled once into a very fast XLA (C++) function which is then executed at each iteration. Alternatively, we could get the same speedup by replacing our `for` loop with `jax.lax.scan`. You can read more about JIT compilation in the [JAX documentation](https://jax.readthedocs.io/en/latest/jax-101/02-jitting.html).

cost_and_grad = jit(value_and_grad(param_to_expectation))

# For the training process we'll use vanilla gradient descent with a constant stepsize:

seed = 123
key = random.PRNGKey(seed)
init_param = random.uniform(key, shape=(len(symbol_map),))

n_steps = 150
stepsize = 0.01

param = init_param

cost_vals = jnp.zeros(n_steps)
cost_vals = cost_vals.at[0].set(param_to_expectation(init_param))

for step in range(1, n_steps):
    cost_val, cost_grad = cost_and_grad(param)
    cost_vals = cost_vals.at[step].set(cost_val)
    param = param - stepsize * cost_grad
    print("Iteration:", step, "\tCost:", cost_val, end="\r")

# Let's visualise the gradient descent

plt.plot(cost_vals)
plt.xlabel("Iteration")
plt.ylabel("Cost")
