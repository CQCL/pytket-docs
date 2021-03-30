# ### Integrating `pytket` into Qiskit software
# In this tutorial, we will focus on:
# - Using `pytket` for compilation or providing devices/simulators within Qiskit Aer workflows;
# - Adapting Qiskit code to use `pytket` directly.
# This example assumes the reader is familiar with the Qiskit software platform and the Grover Adaptive Search optimisation method for Quadratic Unconstrained Binary Optimisation problems.
# To run this example, you will need `pytket`, `qiskit`, `pytket-qiskit`, `pytket-qulacs`, and `pytket-honeywell`. It also requires `qiskit-aqua` to be [installed from source](https://github.com/Qiskit/qiskit-aqua) for recent bug fixes (version incompatibility errors resulting from using a development version can be ignored for this notebook).
# Qiskit has risen to prominence as the most popular platform for the development of quantum software, providing an open source, full-stack solution with a large feature list and extensive examples from the developers and community. For many researchers who have already invested in building a large codebase built on top of Qiskit, the idea of switching entirely to a new platform can look like a time-sink and may require reversion to take advantage of the new tools that get regularly added to Qiskit.
# The interoperability provided by `pytket-qiskit` allows Qiskit users to start taking advantage of some of the unique features of `pytket` without having to completely rewrite their software. Here, we will demonstrate how to take one of the Qiskit tutorial notebooks and enhance it with minimal additional code.
# The following code was taken from the Qiskit tutorial on [Grover Adaptive Search](https://github.com/Qiskit/qiskit-tutorials/blob/master/tutorials/optimization/4_grover_optimizer.ipynb).

from qiskit.aqua import aqua_globals

aqua_globals.random_seed = 1

from qiskit.aqua.algorithms import NumPyMinimumEigensolver
from qiskit.optimization.algorithms import GroverOptimizer, MinimumEigenOptimizer
from qiskit.optimization.problems import QuadraticProgram
from qiskit import BasicAer
from docplex.mp.model import Model

backend = BasicAer.get_backend("statevector_simulator")

model = Model()
x0 = model.binary_var(name="x0")
x1 = model.binary_var(name="x1")
x2 = model.binary_var(name="x2")
model.minimize(-x0 + 2 * x1 - 3 * x2 - 2 * x0 * x2 - 1 * x1 * x2)
qp = QuadraticProgram()
qp.from_docplex(model)
print(qp.export_as_lp_string())

from qiskit.aqua import QuantumInstance

grover_optimizer = GroverOptimizer(6, num_iterations=10, quantum_instance=backend)
results = grover_optimizer.solve(qp)
print("x={}".format(results.x))
print("fval={}".format(results.fval))

exact_solver = MinimumEigenOptimizer(NumPyMinimumEigensolver())
exact_result = exact_solver.solve(qp)
print("x={}".format(exact_result.x))
print("fval={}".format(exact_result.fval))

# Since the `pytket` extension modules provide an interface to the widest variety of devices and simulators out of all major quantum software platforms, the simplest advantage to obtain through `pytket` is to try using some alternative backends.
# One such backend that becomes available is the Qulacs simulator, providing fast noiseless simulations, especially when exploiting an available GPU. We can wrap up the `QulacsBackend` (or `QulacsGPUBackend` if you have a GPU available) in a form that can be passed to any Qiskit Aqua algorithm.

from pytket.extensions.qulacs import QulacsBackend
from pytket.extensions.qiskit.tket_backend import TketBackend

qulacs = QulacsBackend()
backend = TketBackend(qulacs, qulacs.default_compilation_pass())

grover_optimizer = GroverOptimizer(6, num_iterations=10, quantum_instance=backend)
results = grover_optimizer.solve(qp)
print("x={}".format(results.x))
print("fval={}".format(results.fval))

# Adding extra backends to target is nice, but where `pytket` really shines is in its compiler passes. The ability to exploit a large number of sources of redundancy in the circuit structure to reduce the execution cost on a noisy device is paramount in the NISQ era. We can examine the effects of this by looking at how effectively the algorithm works on the `qasm_simulator` from Qiskit Aer with a given noise model.
# (Note: some versions of `qiskit-aqua` give an `AssertionError` when the `solve()` step below is run. If you encounter this, try updating `qiskit-aqua` or, as a workaround, reducing the number of iterations to 2.)

from qiskit.providers.aer import Aer
from qiskit.providers.aer.noise import NoiseModel, depolarizing_error
from qiskit.aqua import QuantumInstance

backend = Aer.get_backend("qasm_simulator")
model = NoiseModel()
model.add_all_qubit_quantum_error(depolarizing_error(0.01, 1), ["p", "u"])
model.add_all_qubit_quantum_error(depolarizing_error(0.05, 2), ["cx"])

qi = QuantumInstance(backend, noise_model=model, seed_transpiler=2, seed_simulator=2)

grover_optimizer = GroverOptimizer(6, num_iterations=10, quantum_instance=qi)
results = grover_optimizer.solve(qp)
print("x={}".format(results.x))
print("fval={}".format(results.fval))
print("n_circs={}".format(len(results.operation_counts)))

# We can insert compilation passes from `pytket` into Qiskit as `TranspilerPass`es, compose with others to form a `PassManager`, and embed into the `QuantumInstance`.

from pytket.passes import FullPeepholeOptimise
from pytket.extensions.qiskit.tket_pass import TketPass
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import Unroller

tp = TketPass(FullPeepholeOptimise())
pm = PassManager([Unroller(["cx", "p", "u"]), tp])
qi = QuantumInstance(backend, pass_manager=pm, noise_model=model, seed_simulator=2)

grover_optimizer = GroverOptimizer(6, num_iterations=10, quantum_instance=qi)
results = grover_optimizer.solve(qp)
print("x={}".format(results.x))
print("fval={}".format(results.fval))
print("n_circs={}".format(len(results.operation_counts)))

# For this particular run, the case of compiling with Qiskit converged with fewer circuit executions but the additional noise incurred in running the circuit caused the optimiser to miss the global optimum, whereas the case for `pytket` eventually reached the true minimum value.
# When using `TketPass` there is a conversion between `qiskit.DAGCircuit` and `pytket.Circuit`, meaning the circuit needs to be in a form suitable for conversion (i.e. the gates used have to be supported by both `qiskit` and `pytket`). If you encounter any issues with using this, we recommend using `Unroller(['cx', 'u1', 'u2', 'u3'])` and `RebaseIBM` at the point before conversion to guarantee appropriate gates are used.

from pytket.passes import RebaseIBM, SequencePass

seq = SequencePass(
    [
        # Insert pytket pass of choice
        RebaseIBM(),
    ]
)
tp = TketPass(seq)
pm = PassManager(
    [
        # Insert initial qiskit passes
        Unroller(["cx", "p", "u"]),
        tp,
        # Insert final qiskit passes
    ]
)
qi = QuantumInstance(backend, pass_manager=pm)

# Similarly, when using `TketBackend` it may be necessary to include some compilation in `qiskit` to enable the conversion into `pytket`, and then some further `pytket` compilation to get it suitable for the actual target backend. For example, `qiskit.circuit.library.standard_gates.DCXGate` currently does not have an equivalent elementary operation in `pytket`, so must be decomposed before we can map across, and likewise the `OpType.ZZMax` gate used by `pytket.extensions.honeywell.HoneywellBackend` (from the `pytket-honeywell` extension) has no equivalent in `qiskit` so the targeting of the final gateset must be performed by `pytket`.

from pytket.extensions.honeywell import HoneywellBackend

pm = PassManager(
    Unroller(["cx", "p", "u"])
)  # Map to a basic gateset to allow conversion to pytket

hb = HoneywellBackend(device_name="HQS-LT-1.0-APIVAL", machine_debug=True)
backend = TketBackend(
    hb, hb.default_compilation_pass(2)
)  # Then use pytket compilation with optimisation level 2

qi = QuantumInstance(backend, pass_manager=pm)

# Exercises:
# - Try running the GAS example using another device/simulator through the `TketBackend` wrapper. The simplest option is to just go full-circle and use the `AerBackend` from `pytket-qiskit` which itself is a wrapper around the `qasm_simulator`.
# - Take another example notebook from the Qiskit [official tutorials](https://github.com/Qiskit/qiskit-tutorials) or [community tutorials](https://github.com/qiskit-community/qiskit-community-tutorials) and try changing out the backend used to a `pytket` backend. For example, try running the [Qiskit Chemistry example](https://github.com/Qiskit/qiskit-tutorials/blob/master/tutorials/chemistry/1_programmatic_approach.ipynb) using a Rigetti device (or simulator) with `ForestBackend` from `pytket-pyquil`, and add in `pytket.passes.PauliSimp` to exploit the structure of the UCCSD ansatz.
