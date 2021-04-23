# # Integrating `pytket` into Qiskit software

# In this tutorial, we will focus on:
# - Using `pytket` for compilation or providing devices/simulators within Qiskit workflows;
# - Adapting Qiskit code to use `pytket` directly.

# This example assumes some familiarity with the Qiskit algorithms library. We have chosen a small variational quantum eigensolver (VQE) for our example, but the same principles apply to a wide range of quantum algorithms.
#
# To run this example, you will need `pytket-qiskit`, as well as the separate `qiskit-optimization` package. You will also need IBMQ credentials stored on your local machine.
#
# Qiskit has risen to prominence as the most popular platform for the development of quantum software, providing an open source, full-stack solution with a large feature list and extensive examples from the developers and community. For many researchers who have already invested in building a large codebase built on top of Qiskit, the idea of switching entirely to a new platform can look like a time-sink and may require reversion to take advantage of the new tools that get regularly added to Qiskit.
#
# The interoperability provided by `pytket-qiskit` allows Qiskit users to start taking advantage of some of the unique features of `pytket` without having to completely rewrite their software.

# Let's take as an example an ansatz for computing the ground-state energy of a hydrogen molecule.

from qiskit.opflow.primitive_ops import PauliSumOp

H2_op = PauliSumOp.from_list(
    [
        ("II", -1.052373245772859),
        ("IZ", 0.39793742484318045),
        ("ZI", -0.39793742484318045),
        ("ZZ", -0.01128010425623538),
        ("XX", 0.18093119978423156),
    ]
)

# First let's use qiskit's NumPyEigensolver to compute the exact answer:

from qiskit.algorithms import NumPyEigensolver

es = NumPyEigensolver(k=1)
exact_result = es.compute_eigenvalues(H2_op).eigenvalues[0].real
print("Exact result:", exact_result)

# The following function will attempt to find an approximation to this using VQE, given a qiskit QuantumInstance on which to run circuits:

from qiskit.algorithms import VQE
from qiskit.algorithms.optimizers import SPSA
from qiskit.circuit.library import EfficientSU2


def vqe_solve(op, maxiter, quantum_instance):
    optimizer = SPSA(maxiter=maxiter)
    ansatz = EfficientSU2(op.num_qubits, entanglement="linear")
    vqe = VQE(ansatz=ansatz, optimizer=optimizer, quantum_instance=quantum_instance)
    return vqe.compute_minimum_eigenvalue(op).eigenvalue


# We will run this on a pytket `IBMQEmulatorBackend`. This is a noisy simulator whose characteristics match those of the real device, in this case "ibmq_belem" (a 5-qubit machine). The characteristics are retrieved from the device when the backend is constructed, so we must first load our IBMQ account.

from pytket.extensions.qiskit import IBMQEmulatorBackend
from qiskit import IBMQ

IBMQ.load_account()
b_emu = IBMQEmulatorBackend("ibmq_belem", hub="ibm-q", group="open", project="main")

# Most qiskit algorithms require a qiskit `QuantumInstance` as input; this in turn is constructed from a `qiskit.providers.Backend`. The `TketBackend` class wraps a pytket backend as a `qiskit.providers.Backend`.

from pytket.extensions.qiskit.tket_backend import TketBackend
from qiskit.utils import QuantumInstance

qis_backend = TketBackend(b_emu)
qi = QuantumInstance(qis_backend, shots=8192, wait=0.1)

# Note that we could have used any other pytket shots backend instead of `b_emu` here. The `pytket` extension modules provide an interface to a wide variety of devices and simulators from different quantum software platforms.
#
# We can now run the VQE algorithm. In this example we use only 10 iterations, but greater accuracy may be achieved by increasing this number:

print("VQE result:", vqe_solve(H2_op, 20, qi))

# Another way to improve the accuracy of results is to apply optimisations to the circuit in an attempt to reduce the overall noise. When we construct our qiskit backend, we can pass in a pytket compilation pass as an additional parameter. There is a wide range of options here; in this example we will use `FullPeepholeOptimise` which is a powerful general-purpose pass.

from pytket.passes import FullPeepholeOptimise

qis_backend2 = TketBackend(b_emu, FullPeepholeOptimise())
qi2 = QuantumInstance(qis_backend2, shots=8192, wait=0.1)

# Let's run the optimisation again:

print("VQE result (with FullPeepholeOptimise):", vqe_solve(H2_op, 20, qi2))

# These are small two-qubit circuits, so the improvement may be small, but with larger, more complex circuits, the reduction in noise from compilation will make a greater difference and allow VQE experiments to converge with fewer iterations.
