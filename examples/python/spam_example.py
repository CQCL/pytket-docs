# # Calibration and Correction of State Preparation and Measurement (SPAM)

# Quantum Computers available in the NISQ-era are limited by significant sources of device noise which cause errors in computation. One such noise source is errors in the preparation and measurement of quantum states, more commonly know as SPAM.
#
# If device SPAM error can be characterised, then device results can be modified to mitigate the error. Characterisation proceeds by determining overlap between different prepared basis states when measured, and mitigation modifies the distribution over output states of the corrected circuit. No modification of the quantum circuit being corrected is required. The ``` pytket```  ```SpamCorrecter```  class supports characterisation and mitigation of device SPAM error.
#
# In this tutorial we will show how the ```SpamCorrecter```  class can be used to modify real results and improve device performance when running experiments.
#
# This tutorial will require installation of ```pytket```, ```pytket_qiskit``` and ```qiskit```, all available on pip.
#
# First, import the ```SpamCorrecter``` class.

from pytket.utils.spam import SpamCorrecter

# The SpamCorrecter class has methods for generating State Preparation and Measurement (SPAM) calibration experiments for pytket backends and correcting counts generated from those same backends.
#
# Let's first mitigate error from a noisy simulation, using a noise model straight from the 5-qubit IBMQ Santiago device. This will require a preloaded IBMQ account.

from qiskit import IBMQ

IBMQ.load_account()

from pytket.extensions.qiskit import process_characterisation

ibmq_bogota_backend = IBMQ.providers()[0].get_backend("ibmq_bogota")
pytket_santiago_characterisation = process_characterisation(ibmq_bogota_backend)
pytket_santiago_architecture = pytket_santiago_characterisation["Architecture"]

import networkx as nx
import matplotlib.pyplot as plt

santiago_graph = nx.Graph(pytket_santiago_architecture.coupling)
nx.draw(santiago_graph, labels={node: node for node in santiago_graph.nodes()})

# SPAM correction requires subsets of qubits which are assumed to only have SPAM errors correlated with each other, and no other qubits.
#
# Correlated errors are usually dependent on the connectivity layout of devices, as shown above.
#
# As Santiago is a small 5-qubit device with few connections, let's assume that all qubits have correlated SPAM errors. The number of calibration circuits produced is exponential in the maximum number of correlated circuits, so finding good subsets of correlated qubits is important for characterising larger devices with smaller experimental overhead.
#
# We can produce an ```IBMQEmulatorBackend``` to run this. This uses a noise model from ```ibmq_bogota``` produced using qiskit-aer. We can then execute all calibration circuits through the backend.

from pytket.extensions.qiskit import IBMQEmulatorBackend, AerBackend

n_shots = 8192
pytket_noisy_sim_backend = IBMQEmulatorBackend("ibmq_bogota")
santiago_node_subsets = pytket_noisy_sim_backend.backend_info.architecture.nodes
santiago_spam = SpamCorrecter([santiago_node_subsets], pytket_noisy_sim_backend)

# The SpamCorrecter uses these subsets of qubits to produce calibration circuits.

calibration_circuits = santiago_spam.calibration_circuits()
print("Number of calibration circuits: ", len(calibration_circuits))

sim_handles = pytket_noisy_sim_backend.process_circuits(calibration_circuits, n_shots)

# Count results from the simulator are then used to calculate the matrices used for SPAM correction for ```ibmq_bogota```.

sim_count_results = pytket_noisy_sim_backend.get_results(sim_handles)
santiago_spam.calculate_matrices(sim_count_results)

from pytket import Circuit

ghz_circuit = (
    Circuit(len(pytket_noisy_sim_backend.backend_info.architecture.nodes))
    .H(0)
    .CX(0, 1)
    .CX(1, 2)
    .measure_all()
)
ghz_circuit = pytket_noisy_sim_backend.get_compiled_circuit(ghz_circuit)
ghz_noisy_handle = pytket_noisy_sim_backend.process_circuit(ghz_circuit, n_shots)
ghz_noisy_result = pytket_noisy_sim_backend.get_result(ghz_noisy_handle)

# We also run a noiseless simulation so we can compare performance.

pytket_noiseless_sim_backend = AerBackend()
ghz_noiseless_handle = pytket_noiseless_sim_backend.process_circuit(
    ghz_circuit, n_shots
)
ghz_noiseless_result = pytket_noiseless_sim_backend.get_result(ghz_noiseless_handle)

# Noisy simulator counts are corrected using the ```SpamCorrecter``` objects ```correct_counts``` method.
#
# To correctly amend counts, the ```correct_counts``` method requires a ``ParallelMeasures`` type object, a list of ``Dict[Qubit, Bit]`` where each dictionary denotes a set of Qubit measured in parallel and the Bit their measured values are assigned to.
#
# The ``SpamCorrecter`` class has a helper method ``get_parallel_measure`` for retrieving this object for a Circuit.

ghz_parallel_measure = santiago_spam.get_parallel_measure(ghz_circuit)

ghz_spam_corrected_result = santiago_spam.correct_counts(
    ghz_noisy_result, ghz_parallel_measure
)

# Import and define the Jensen-Shannon divergence, which we will use for comparing performance. The Jensen-Shannon divergence is a symmetric and finite measure of similarity between two probability distributions. A smaller divergence implies more similarity between two probability distributions.

from scipy.stats import entropy
import numpy as np
import itertools


def binseq(k):
    return ["".join(x) for x in itertools.product("01", repeat=k)]


def probs_from_counts(result):
    counts = result.get_counts()
    counts_dict = dict()
    for x in counts:
        counts_dict["".join(str(e) for e in x)] = counts[x]
    converted = []
    binary_strings = binseq(len(list(counts.keys())[0]))
    for b in binary_strings:
        converted.append(counts_dict.get(b, 0))
    return converted / np.sum(converted)


def JSD(P, Q):
    _P = P / np.linalg.norm(P, ord=1)
    _Q = Q / np.linalg.norm(Q, ord=1)
    _M = 0.5 * (_P + _Q)
    return 0.5 * (entropy(_P, _M) + entropy(_Q, _M))


# Convert our counts results to a probability distribution over the basis states for comparison.

ghz_noiseless_probabilities = probs_from_counts(ghz_noiseless_result)
ghz_noisy_probabilities = probs_from_counts(ghz_noisy_result)
ghz_spam_corrected_probabilities = probs_from_counts(ghz_spam_corrected_result)

print(
    "Jensen-Shannon Divergence between noiseless simulation probability distribution and noisy simulation probability distribution: ",
    JSD(ghz_noiseless_probabilities, ghz_noisy_probabilities),
)
print(
    "Jensen-Shannon Divergence between noiseless simulation probability distribution and spam corrected noisy simulation probability distribution: ",
    JSD(ghz_noiseless_probabilities, ghz_spam_corrected_probabilities),
)

# In our noisy simulated case, spam corrected results produced a distribution closer to the expected distribution.
#
# There are two methods available for correcting counts: the default ```bayesian```, and ```invert```. Further information on each method is available at our [documentation](https://cqcl.github.io/tket/pytket/api/utils.html#module-pytket.utils.spam).
#
# Let's look at how the ```invert``` method performs.

ghz_invert_corrected_result = santiago_spam.correct_counts(
    ghz_noisy_result, ghz_parallel_measure, method="invert"
)
ghz_invert_probabilities = probs_from_counts(ghz_invert_corrected_result)

print(
    "Jensen-Shannon Divergence between noiseless simulation probability distribution and Bayesian-corrected noisy simulation probability distribution: ",
    JSD(ghz_noiseless_probabilities, ghz_spam_corrected_probabilities),
)
print(
    "Jensen-Shannon Divergence between noiseless simulation probability distribution and invert-corrected noisy simulation probability distribution: ",
    JSD(ghz_noiseless_probabilities, ghz_invert_probabilities),
)

# To see how SPAM correction performs on results from a real IBMQ quantum device, try replacing `IBMQEmulatorBackend` with `IBMQBackend`.

from pytket.extensions.qiskit import IBMQBackend

ibm_backend = IBMQBackend("ibmq_bogota")
