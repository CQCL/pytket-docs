# # VQE example with `pytket-qujax`

# See the docs for [qujax](https://cqcl.github.io/qujax/) and [pytket-qujax](https://cqcl.github.io/pytket-qujax/api/index.html).

from jax import numpy as jnp, random, value_and_grad, jit
from pytket import Circuit
from pytket.circuit.display import render_circuit_jupyter
import matplotlib.pyplot as plt


# ## Let's start with a TKET circuit

import qujax
from pytket.extensions.qujax.qujax_convert import tk_to_qujax

# We place barriers to stop tket automatically rearranging gates and we also store the number of circuit parameters as we'll need this later.


def get_circuit(n_qubits, depth):
    n_params = 2 * n_qubits * (depth + 1)

    param = jnp.zeros((n_params,))

    circuit = Circuit(n_qubits)

    k = 0
    for i in range(n_qubits):
        circuit.H(i)
    for i in range(n_qubits):
        circuit.Rx(param[k], i)
        k += 1
    for i in range(n_qubits):
        circuit.Ry(param[k], i)
        k += 1

    for _ in range(depth):
        for i in range(0, n_qubits - 1):
            circuit.CZ(i, i + 1)
        circuit.add_barrier(range(0, n_qubits))
        for i in range(n_qubits):
            circuit.Rx(param[k], i)
            k += 1
        for i in range(n_qubits):
            circuit.Ry(param[k], i)
            k += 1
    return circuit, n_params


n_qubits = 4
depth = 2
circuit, n_params = get_circuit(n_qubits, depth)
render_circuit_jupyter(circuit)

# ## Now let's invoke qujax
# The `pytket.extensions.qujax.tk_to_qujax` function will generate a parameters -> statetensor function for us.

param_to_st = tk_to_qujax(circuit)

# Let's try it out on some random parameters values. Be aware that's JAX's random number generator requires a `jax.random.PRNGkey` every time it's called - more info on that [here](https://jax.readthedocs.io/en/latest/jax.random.html).
# Be aware that we still have convention where parameters are specified as multiples of $\pi$ - that is in [0,2].

params = random.uniform(random.PRNGKey(0), shape=(n_params,), minval=0.0, maxval=2.0)
statetensor = param_to_st(params)
print(statetensor)
print(statetensor.shape)

# Note that this function also has an optional second argument where an initiating `statetensor_in` can be provided. If it is not provided it will default to the all 0s state (as we use here).

# We can obtain statevector by simply calling `.flatten()`

statevector = statetensor.flatten()
statevector.shape

# And sampling probabilities by squaring the absolute value of the statevector

sample_probs = jnp.square(jnp.abs(statevector))
plt.bar(jnp.arange(statevector.size), sample_probs)

# ## Cost function

# Now we have our `param_to_st` function we are free to define a cost function that acts on bitstrings (e.g. maxcut) or integers by directly wrapping a function around `param_to_st`. However, cost functions defined via quantum Hamiltonians are a bit more involved.
# Fortunately, we can encode an Hamiltonian in JAX via the `qujax.get_statetensor_to_expectation_func` function which generates a statetensor -> expected value function for us.
# It takes three arguments as input
# - `gate_seq_seq`: A list of string (or array) lists encoding the gates in each term of the Hamiltonian. I.e. `[['X','X'], ['Y','Y'], ['Z','Z']]` corresponds to $H = aX_iX_j +  bY_kY_l + cZ_mZ_n$ with qubit indices $i,j,k,l,m,n$ specified in the second argument and coefficients $a,b,c$ specified in the third argument
# - `qubit_inds_seq`: A list of integer lists encoding which qubit indices to apply the aforementioned gates. I.e. `[[0, 1],[0,1],[0,1]]`. Must have the same structure as `gate_seq_seq` above.
# - `coefficients`: A list of floats encoding any coefficients in the Hamiltonian. I.e. `[2.3, 0.8, 1.2]` corresponds to $a=2.3,b=0.8,c=1.2$ above. Must have the same length as the two above arguments.

# More specifically let's consider the problem of finding the ground state of the quantum Heisenberg Hamiltonian

# $$
# \begin{equation}
# H = \sum_{i=1}^{n_\text{qubits}-1} X_i X_{i+1} + Y_i Y_{i+1} + Z_i Z_{i+1}.
# \end{equation}
# $$
#
# As described, we define the Hamiltonian via its gate strings, qubit indices and coefficients.

hamiltonian_gates = [["X", "X"], ["Y", "Y"], ["Z", "Z"]] * (n_qubits - 1)
hamiltonian_qubit_inds = [
    [int(i), int(i) + 1] for i in jnp.repeat(jnp.arange(n_qubits), 3)
]
coefficients = [1.0] * len(hamiltonian_qubit_inds)

print("Gates:\t", hamiltonian_gates)
print("Qubits:\t", hamiltonian_qubit_inds)
print("Coefficients:\t", coefficients)

# Now let's get the Hamiltonian as a pure JAX function

st_to_expectation = qujax.get_statetensor_to_expectation_func(
    hamiltonian_gates, hamiltonian_qubit_inds, coefficients
)

# Let's check it works on the statetensor we've already generated.

expected_val = st_to_expectation(statetensor)
expected_val

# Now let's wrap the `param_to_st` and `st_to_expectation` together to give us an all in one `param_to_expectation` cost function.

param_to_expectation = lambda param: st_to_expectation(param_to_st(param))

param_to_expectation(params)

# Sanity check that a different, randomly generated set of parameters gives us a new expected value.

new_params = random.uniform(
    random.PRNGKey(1), shape=(n_params,), minval=0.0, maxval=2.0
)
param_to_expectation(new_params)

# ## Exact gradients within a VQE algorithm
# The `param_to_expectation` function we created is a pure JAX function and outputs a scalar. This means we can pass it to `jax.grad` (or even better `jax.value_and_grad`).

cost_and_grad = value_and_grad(param_to_expectation)

# The `cost_and_grad` function returns a tuple with the exact cost value and exact gradient evaluated at the parameters.

cost_and_grad(params)

# ## Now we have all the tools we need to design our VQE!
# We'll just use vanilla gradient descent with a constant stepsize


def vqe(init_param, n_steps, stepsize):
    params = jnp.zeros((n_steps, n_params))
    params = params.at[0].set(init_param)

    cost_vals = jnp.zeros(n_steps)
    cost_vals = cost_vals.at[0].set(param_to_expectation(init_param))

    for step in range(1, n_steps):
        cost_val, cost_grad = cost_and_grad(params[step - 1])
        cost_vals = cost_vals.at[step].set(cost_val)

        new_param = params[step - 1] - stepsize * cost_grad
        params = params.at[step].set(new_param)

        print("Iteration:", step, "\tCost:", cost_val, end="\r")
    print("\n")
    return params, cost_vals


# Ok enough talking, let's run (and whilst we're at it we'll time it too)

# %time
vqe_params, vqe_cost_vals = vqe(params, n_steps=250, stepsize=0.01)

# Let's plot the results...

plt.plot(vqe_cost_vals)
plt.xlabel("Iteration")
plt.ylabel("Cost")

# Pretty good!

# ## `jax.jit` speedup
# One last thing... We can significantly speed up the VQE above via the `jax.jit`. In our current implementation, the expensive `cost_and_grad` function is compiled to [XLA](https://www.tensorflow.org/xla)  and then executed at each call. By invoking `jax.jit` we ensure that the function is compiled only once (on the first call) and then simply executed at each future call - this is much faster!

cost_and_grad = jit(cost_and_grad)

# We'll demonstrate this using the second set of initial parameters we randomly generated (to be sure of no caching).

# %time
new_vqe_params, new_vqe_cost_vals = vqe(new_params, n_steps=250, stepsize=0.01)

# That's some speedup!
# But let's also plot the training to be sure it converged correctly

plt.plot(new_vqe_cost_vals)
plt.xlabel("Iteration")
plt.ylabel("Cost")
