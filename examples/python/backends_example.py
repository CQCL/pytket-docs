# # TKET `Backend` tutorial

# This example shows how to use `pytket` to execute quantum circuits on both simulators and real devices, and how to interpret the results. As tket is designed to be platform-agnostic, we have unified the interfaces of different providers as much as possible into the `Backend` class for maximum portability of code.

# For the full list of supported backends see the pytket [extensions index page](https://tket.quantinuum.com/extensions/).

# In this notebook we will focus on the Aer, IBMQ and ProjectQ backends.
#
# To get started, we must install the core pytket package and the subpackages required to interface with the desired providers. We will also need the `QubitOperator` class from `openfermion` to construct operators for a later example. To get everything run the following in shell:
#
# `pip install pytket pytket-qiskit pytket-projectq openfermion`
#
# First, import the backends that we will be demonstrating.

from pytket.extensions.qiskit import (
    AerStateBackend,
    AerBackend,
    AerUnitaryBackend,
    IBMQBackend,
    IBMQEmulatorBackend,
)
from pytket.extensions.projectq import ProjectQBackend

# We are also going to be making a circuit to run on these backends, so import the `Circuit` class.

from pytket import Circuit, Qubit

# Below we generate a circuit which will produce a Bell state, assuming the qubits are all initialised in the |0> state:

circ = Circuit(2)
circ.H(0)
circ.CX(0, 1)

# As a sanity check, we will use the `AerStateBackend` to verify that `circ` does actually produce a Bell state.
#
# To submit a circuit for excution on a backend we can use `process_circuit` with appropriate arguments. If we have multiple circuits to excecute, we can use `process_circuits` (note the plural), which will attempt to batch up the circuits if possible. Both methods return a `ResultHandle` object per submitted `Circuit` which you can use with result retrieval methods to get the result type you want (as long as that result type is supported by the backend).
#
# Calling `get_state` will return a `numpy` array corresponding to the statevector.
#
# This style of usage is used consistently in the `pytket` backends.

aer_state_b = AerStateBackend()
state_handle = aer_state_b.process_circuit(circ)
statevector = aer_state_b.get_result(state_handle).get_state()
print(statevector)

# As we can see, the output state vector $\lvert \psi_{\mathrm{circ}}\rangle$ is $(\lvert00\rangle + \lvert11\rangle)/\sqrt2$.
#
# This is a symmetric state. For non-symmetric states, we default to an ILO-BE format (increasing lexicographic order of (qu)bit ids, big-endian), but an alternative convention can be specified when retrieving results from backends. See the docs for the `BasisOrder` enum for more information.

# A lesser-used simulator available through Qiskit Aer is their unitary simulator. This will be somewhat more expensive to run, but returns the full unitary matrix for the provided circuit. This is useful in the design of small subcircuits that will be used multiple times within other larger circuits - statevector simulators will only test that they act correctly on the $\lvert 0 \rangle^{\otimes n}$ state, which is not enough to guarantee the circuit's correctness.
#
# The `AerUnitaryBackend` provides a convenient access point for this simulator for use with `pytket` circuits. The unitary of the circuit can be retrieved from backends that support it using the `BackendResult.get_unitary` interface. In this example, we chose to use `Backend.run_circuit`, which is equivalent to calling `process_circuit` followed by `get_result`.

aer_unitary_b = AerUnitaryBackend()
result = aer_unitary_b.run_circuit(circ)
print(result.get_unitary())

# Note that state vector and unitary simulations are also available in pytket directly. In general, we recommend you use these unless you require another Backend explicitly.

statevector = circ.get_statevector()
unitary = circ.get_unitary()

# Now suppose we want to measure this Bell state to get some actual results out, so let's append some `Measure` gates to the circuit. The `Circuit` class has the `measure_all` utility function which appends `Measure` gates on every qubit. All of these results will be written to the default classical register ('c'). This function will automatically add the classical bits to the circuit if they are not already there.

circ.measure_all()

# We can get some measured counts out from the `AerBackend`, which is an interface to the Qiskit Aer QASM simulator. Suppose we would like to get 10 shots out (10 repeats of the circuit and measurement). We can seed the simulator's random-number generator in order to make the results reproducible, using an optional keyword argument to `process_circuit`.

aer_b = AerBackend()
handle = aer_b.process_circuit(circ, n_shots=10, seed=1)

counts = aer_b.get_result(handle).get_counts()
print(counts)

# What happens if we simulate some noise in our imagined device, using the Qiskit Aer noise model?

# To investigate this, we will require an import from Qiskit. For more information about noise modelling using Qiskit Aer, see the [Qiskit device noise](https://qiskit.org/documentation/apidoc/aer_noise.html) documentation.

from qiskit.providers.aer.noise import NoiseModel

my_noise_model = NoiseModel()
readout_error = 0.2
for q in range(2):
    my_noise_model.add_readout_error(
        [[1 - readout_error, readout_error], [readout_error, 1 - readout_error]], [q]
    )

# This simple noise model gives a 20% chance that, upon measurement, a qubit that would otherwise have been measured as $0$ would instead be measured as $1$, and vice versa. Let's see what our shot table looks like with this model:

noisy_aer_b = AerBackend(my_noise_model)
noisy_handle = noisy_aer_b.process_circuit(circ, n_shots=10, seed=1, valid_check=False)
noisy_counts = noisy_aer_b.get_result(noisy_handle).get_counts()
print(noisy_counts)

# We now have some spurious $01$ and $10$ measurements, which could never happen when measuring a Bell state on a noiseless device.
#
# The `AerBackend` class can accept any Qiskit noise model.
#
# All backends expose a generic `get_result` method which takes a `ResultHandle` and returns the respective result in the form of a `BackendResult` object. This object may hold measured results in the form of shots or counts, or an exact statevector from simulation. Measured results are stored as `OutcomeArray` objects, which compresses measured bit values into 8-bit integers. We can extract the bitwise values using `to_readouts`.
#
# Instead of an assumed ILO or DLO convention, we can use this object to request only the `Bit` measurements we want, in the order we want. Let's try reversing the bits of the noisy results.

backend_result = noisy_aer_b.get_result(noisy_handle)
bits = circ.bits

outcomes = backend_result.get_counts([bits[1], bits[0]])
print(outcomes)

# `BackendResult` objects can be natively serialized to and deserialized from a dictionary. This dictionary can be immediately dumped to `json` for storing results.

from pytket.backends.backendresult import BackendResult

result_dict = backend_result.to_dict()
print(result_dict)
print(BackendResult.from_dict(result_dict).get_counts())

# The last simulator we will demonstrate is the `ProjectQBackend`. ProjectQ offers fast simulation of quantum circuits with built-in support for fast expectation values from operators. The `ProjectQBackend` exposes this functionality to take in OpenFermion `QubitOperator` instances. These are convertible to and from `QubitPauliOperator` instances in Pytket.
#
# Note: ProjectQ can also produce statevectors in the style of `AerStateBackend`, and similarly Aer backends can calculate expectation values directly, consult the relevant documentation to see more.
#
# Let's create an OpenFermion `QubitOperator` object and a new circuit:

import openfermion as of

hamiltonian = 0.5 * of.QubitOperator("X0 X2") + 0.3 * of.QubitOperator("Z0")

circ2 = Circuit(3)
circ2.Y(0)
circ2.H(1)
circ2.Rx(0.3, 2)

# We convert the OpenFermion Hamiltonian into a pytket QubitPauliOperator:
from pytket.pauli import Pauli, QubitPauliString
from pytket.utils.operators import QubitPauliOperator


pauli_sym = {"I": Pauli.I, "X": Pauli.X, "Y": Pauli.Y, "Z": Pauli.Z}


def qps_from_openfermion(paulis):
    """Convert OpenFermion tensor of Paulis to pytket QubitPauliString."""
    qlist = []
    plist = []
    for q, p in paulis:
        qlist.append(Qubit(q))
        plist.append(pauli_sym[p])
    return QubitPauliString(qlist, plist)


def qpo_from_openfermion(openf_op):
    """Convert OpenFermion QubitOperator to pytket QubitPauliOperator."""
    tk_op = dict()
    for term, coeff in openf_op.terms.items():
        string = qps_from_openfermion(term)
        tk_op[string] = coeff
    return QubitPauliOperator(tk_op)


hamiltonian_op = qpo_from_openfermion(hamiltonian)

# Now we can create a `ProjectQBackend` instance and feed it our circuit and `QubitOperator`:

from pytket.utils.operators import QubitPauliOperator

projectq_b = ProjectQBackend()
expectation = projectq_b.get_operator_expectation_value(circ2, hamiltonian_op)
print(expectation)

# The last leg of this tour includes running a pytket circuit on an actual quantum computer. To do this, you will need an IBM quantum experience account and have your credentials stored on your computer. See https://quantum-computing.ibm.com to make an account and view available devices and their specs.
#
# Physical devices have much stronger constraints on the form of admissible circuits than simulators. They tend to support a minimal gate set, have restricted connectivity between qubits for two-qubit gates, and can have limited support for classical control flow or conditional gates. This is where we can invoke the tket compiler passes to transform our desired circuit into one that is suitable for the backend.
#
# To check our code works correctly, we can use the `IBMQEmulatorBackend` to run our code exactly as if it were going to run on a real device, but just execute on a simulator (with a basic noise model adapted from the reported device properties).


# Let's create an `IBMQEmulatorBackend` for the `ibmq_manila` device and check if our circuit is valid to be run.

ibmq_b_emu = IBMQEmulatorBackend("ibmq_manila")
ibmq_b_emu.valid_circuit(circ)

# It looks like we need to compile this circuit to be compatible with the device. To simplify this procedure, we provide minimal compilation passes designed for each backend (the `default_compilation_pass()` method) which will guarantee compatibility with the device. These may still fail if the input circuit has too many qubits or unsupported usage of conditional gates. The default passes can have their degree of optimisation by changing an integer parameter (optimisation levels 0, 1, 2), and they can be easily composed with any of tket's other optimisation passes for better performance.
#
# For convenience, we also wrap up this pass into the `get_compiled_circuit` method if you just want to compile a single circuit.

compiled_circ = ibmq_b_emu.get_compiled_circuit(circ)


# Let's create a backend for running on the actual device and check our compiled circuit is valid for this backend too.

ibmq_b = IBMQBackend("ibmq_manila")
ibmq_b.valid_circuit(compiled_circ)

# We are now good to run this circuit on the device. After submitting, we can use the handle to check on the status of the job, so that we know when results are ready to be retrieved. The `circuit_status` method works for all backends, and returns a `CircuitStatus` object. If we just run `get_result` straight away, the backend will wait for results to complete, blocking any other code from running.
#
# In this notebook we will use the emulated backend `ibmq_b_emu` to illustrate, but the workflow is the same as for the real backend `ibmq_b` (except that the latter will typically take much longer because of the size of the queue).

quantum_handle = ibmq_b_emu.process_circuit(compiled_circ, n_shots=10)

print(ibmq_b_emu.circuit_status(quantum_handle))

quantum_counts = ibmq_b_emu.get_result(quantum_handle).get_counts()
print(quantum_counts)

# These are from an actual device, so it's impossible to perfectly predict what the results will be. However, because of the problem of noise, it would be unsurprising to find a few $01$ or $10$ results in the table. The circuit is very short, so it should be fairly close to the ideal result.
#
# The devices available through the IBM Q Experience serve jobs one at a time from their respective queues, so a large amount of experiment time can be taken up by waiting for your jobs to reach the front of the queue. `pytket` allows circuits to be submitted to any backend in a single batch using the `process_circuits` method. For the `IBMQBackend`, this will collate the circuits into as few jobs as possible which will all be sent off into the queue for the device. The method returns a `ResultHandle` per submitted circuit, in the order of submission.

circuits = []
for i in range(5):
    c = Circuit(2)
    c.Rx(0.2 * i, 0).CX(0, 1)
    c.measure_all()
    circuits.append(ibmq_b_emu.get_compiled_circuit(c))
handles = ibmq_b_emu.process_circuits(circuits, n_shots=100)
print(handles)

# We can now retrieve the results and process them. As we measured each circuit in the $Z$-basis, we can obtain the expectation value for the $ZZ$ operator immediately from these measurement results. We can calculate this using the `expectation_from_counts` utility method in `pytket`.

from pytket.utils import expectation_from_counts

for handle in handles:
    counts = ibmq_b_emu.get_result(handle).get_counts()
    exp_val = expectation_from_counts(counts)
    print(exp_val)

# A `ResultHandle` can be easily stored in its string representaton and later reconstructed using the `from_str` method. For example, we could do something like this:

from pytket.backends import ResultHandle

c = Circuit(2).Rx(0.5, 0).CX(0, 1).measure_all()
c = ibmq_b_emu.get_compiled_circuit(c)
handle = ibmq_b_emu.process_circuit(c, n_shots=10)
handlestring = str(handle)
print(handlestring)
# ... later ...
oldhandle = ResultHandle.from_str(handlestring)
print(ibmq_b_emu.get_result(oldhandle).get_counts())

# For backends which support persistent handles (e.g. `IBMQBackend`, `QuantinuumBackend`, `BraketBackend` and `AQTBackend`) you can even stop your python session and use your result handles in a separate script to retrive results when they are ready, by storing the handle strings. For experiments with long queue times, this enables separate job submission and retrieval. Use `Backend.persistent_handles` to check whether a backend supports this feature.
#
# All backends will also cache all results obtained in the current python session, so you can use the `ResultHandle` to retrieve the results many times if you need to reuse the results. Over a long experiment, this can consume a large amount of RAM, so we recommend removing results from the cache when you are done with them. A simple way to achieve this is by calling `Backend.empty_cache` (e.g. at the end of each loop of a variational algorithm), or removing individual results with `Backend.pop_result`.

# The backends in `pytket` are designed to be as similar to one another as possible. The example above using physical devices can be run entirely on a simulator by swapping out the `IBMQBackend` constructor for any other backend supporting shot outputs (e.g. `AerBackend`, `ProjectQBackend`, `ForestBackend`), or passing it the name of a different device. Furthermore, using pytket it is simple to convert between handling shot tables, counts maps and statevectors.
#
# For more information on backends and other `pytket` features, read our [documentation](https://cqcl.github.io/pytket) or see the other examples on our [GitHub repo](https://github.com/CQCL/tket/pytket/api).
