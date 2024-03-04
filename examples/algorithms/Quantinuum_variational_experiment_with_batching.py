r"""Variational Experiment on H-Series
======================================
"""

######################################################################
# Hybrid Quantum-Classical variational quantum algorithms consist of optimising a trial parametric
# wavefunction, :math:`| \psi (\vec{\theta}) \rangle`, to estimate the lowest eigenvalue (or
# expectation value) of a Hamiltonian, :math:`\hat{H}`. This could be an Electronic Structure
# Hamiltonian or a Hamiltonian defining a QUBO (quadratic unconstrained binary optimisation) or MAXCUT
# problem. The optimal parameters of the wavefunction, :math:`(\vec{\theta})` are an estimation of the
# lowest eigenvector of the Hamiltonian.
# 

######################################################################
# Further details can be found in the following articles: \* `A variational eigenvalue solver on a
# quantum processor <https://arxiv.org/abs/1304.3061>`__\  \* `Towards Practical Quantum Variational
# Algorithms <https://arxiv.org/abs/1507.08969>`__
# 

######################################################################
# For the problem today, we will evaluate the ground-state energy (lowest eigenvalue) of a
# di-Hydrodgen molecule. A Hamiltonian is defined over two-qubits
# (`PhysRevX.6.031007 <https://journals.aps.org/prx/abstract/10.1103/PhysRevX.6.031007>`__). A
# state-preparation (or Ansatz) circuit, a sequence of single-qubit and two-qubit gates, is used to
# generate a trial wavefunction. The wavefunction parameters are rotations on the circuit.
# 

######################################################################
# The hardware-efficient state-preparation method is used for today’s problem
# (`nature23879 <https://www.nature.com/articles/nature23879>`__). The variational experiment
# optimises the parameters on this circuit, over multiple iterations, in order to minimise the
# expectation value of the Hamiltonian,
# :math:`\langle \psi (\vec{\theta}) | \hat{H} | \psi (\vec{\theta}) \rangle`.
# 

######################################################################
# Workflow and Tools
# ------------------
# 

######################################################################
# ``pytket`` is used to synthesise a state-preparation circuit, prepare measurement circuits with
# ``pytket-quantinuum`` being used to submit (retrieve) jobs in a batch to (from) the H-Series
# service. The variational experiment requires the following as inputs: \* a symbolic
# state-preparation circuit. \* an Hamiltonian defining the problem to be solved.
# 

######################################################################
# The state-preparation, described above, consists of fixed-angle single-qubit and two-qubit gates in
# addition to variable-angle single-qubit gates. In pytket, variable-angle single-qubit gates can have
# two types of parameters: \* numerical parameters (``float``); \* symbolic parameters
# (``sympy.symbol``).
# 

######################################################################
# Numerical parameters are native python ``float``\ s. Symbolic parameters require the use of the
# symbolic library, ``sympy``, which is also a dependency of ``pytket``. Throughout the variational
# experiment, symbolic parameters on the state-preparation circuit are replaced with additional
# numerical parameters.
# 

######################################################################
# The variational procedure consists of :math:`n` iterations until a specific criterion is satisfied.
# A batch session will run over these :math:`n` iterations. Inactivity for over 1 minutes will lead to
# the batch session ending, given how the batch feature works for H-Series devices.
# 

######################################################################
# During the variational experiment, each iteration updates the numerical values in the parameter set,
# as described above. Subsequently, these are substituted into a new copy of the original symbolic
# state-preparation circuit. A set of sub-circuits, each containing measurement information defined by
# the input Hamiltonian, are appended to the numerical state-preparation circuit, leading to a set of
# measurement circuits. Finally, these circuits are submitted to H-Series.
# 

######################################################################
# Specifically, each iteration consists of: \* classical pre-processing to define measurement
# circuits; \* batch submission to H-Series; \* retrieval of measurement results; \* classical
# post-processing to evaluate the cost function;
# 

######################################################################
# determining whether to stop or continue the variational procedure.
# 

######################################################################
# The ``SciPy`` minimiser is used to control the optimisation of the cost function. The minimised
# value of the cost function and the optimal parameters can be retrieved at the end of the variational
# experiment.
# 

######################################################################
# The observable is a sum of Pauli-strings (tensor product over ``m`` qubits of Pauli-:math:`\hat{X}`,
# Pauli-:math:`\hat{Y}`, Pauli-:math:`\hat{Z}` & Pauli-:math:`\hat{I}`) multiplied by numerical
# coefficients. \* a set of initial numerical parameters to substitute into the symbolic
# state-preparation circuit. For example, this can be a set of random numerical floating-point
# numbers. \* ``pytket.backends.Backend`` object to interface with the H-Series quantum computing
# service. \* Number of shots to simulate each circuit with to generate a distribution of
# measurements. \* Maximum batch cost to limit the credit cost of the variational experiment.
# 

######################################################################
# QuantinuumBackend
# -----------------
# 

######################################################################
# The ``QuantinuumBackend`` is used to submit and retreive all circuits required for the variational
# experiment. This backend is included in the ``pytket-quantinuum`` extension. With this backend, the
# end-user can access H-series hardware, emulators, syntax checkers. The Quantinuum user portal lists
# all devices and emulators the end-user can access.
# 

######################################################################
# In the code cell below, the instance of QuantinuumBackend uses the H-Series emulator, ``H1-1E``. The
# H1 syntax checker’s target is ``H1-1SC`` and the quantum device’s target is ``H1-1``. The H-Series
# emulators are a useful utility to test and cost the performance of an algorithm before any hardware
# session.
# 

######################################################################
# The ``QuantinuumBackend`` instance requires the user to be authenticated before any jobs can be
# submitted. The ``login`` method will allow authentication.

# sphinx_gallery_thumbnail_path = '_static/images/vqe.png'

from pytket.extensions.quantinuum import QuantinuumBackend

quantinuum_backend = QuantinuumBackend(device_name="H1-1E")
quantinuum_backend.login()

######################################################################
# Contents
# --------
# 

######################################################################
# 1. `Synthesise Symbolic State-Preparation Circuit <#state-prep>`__\ 
# 2. `Hamiltonian Definition & Analysis <#hamiltonian>`__\ 
# 3. `Computing Expectation Values <#expval>`__\ 
# 4. `Variational Procedure with Batches <#variational>`__\  
#     The code-cell below synthesises a two-qubit circuit consisting of
#    arbitrary-angle two-qubit ``ZZPhase`` gates (``pytket.circuit.OpType.ZZPhase``) and fixed-angle
#    single-qubit ``X`` gate (``pytket.circuit.OpType.X``). This state-preparation technique is
#    inspired by the Hardware-Efficient Ansatz (HEA)
#    (`nature23879 <https://www.nature.com/articles/nature23879>`__), instead of the usual chemistry
#    state-preparation method, Unitary Coupled Cluster (UCC)
#    (`arxiv.1701.02691 <https://arxiv.org/abs/1701.02691>`__). The hardware-efficient
#    state-preparation method requires alternating layers of two-qubit gates and single-qubit gates.
#    Ultimately, this leads to fewer two-qubit gates, but requires a greater number of variational
#    parameters, compared to UCC. The optimal parameters for HEA are governed by the noise profile of
#    the device. The HEA circuit used in this example consists of one-layer ``ZZPhase`` gates.
# 

from pytket.circuit import Circuit
from sympy import Symbol

symbols = [Symbol(f"p{0}")]
symbolic_circuit = Circuit(2)
symbolic_circuit.X(0)
symbolic_circuit.ZZPhase(symbols[0], 0, 1)

######################################################################
# The symbolic state-preparation circuit can be visualised using the ``pytket.circuit.display``
# submodule.
# 

from pytket.circuit.display import render_circuit_jupyter

render_circuit_jupyter(symbolic_circuit)

######################################################################
# 2. Hamiltonian Definition and Analysis 
# ---------------------------------------
# 

######################################################################
# A problem hamiltonian is defined using the
# `pytket.utils.operator.QubitPauliOperator <https://tket.quantinuum.com/api-docs/utils.html#pytket.utils.QubitPauliOperator>`_
# class. Each ``QubitPauliOperator`` consists of complex coefficients and tensor products of
# Pauli-operations. The tensor products are referred to as Pauli-strings. This particular Hamiltonian
# consists of 5 terms operating on qubits ``q[0]`` and ``q[1]``. The problem Hamiltonian,
# :math:`\hat{H}`, is defined as:
# 

######################################################################
# .. math::
#
#   \hat{H} = g_0 \hat{I}_{q[0]} \otimes \hat{I}_{q[1]} + g_1 \hat{Z}_{q[0]} \otimes \hat{I}_{q[1]} + g_2 \hat{I}_{q[0]} \otimes \hat{Z}_{q[1]} + g_3 \hat{Z}_{q[0]} \otimes \hat{Z}_{q[1]} + g_4 \hat{X}_{q[0]} \otimes \hat{X}_{q[1]} + g_5 \hat{Y}_{q[0]} \otimes \hat{Y}_{q[1]}
# 

######################################################################
# where :math:`g_0, g_1, g_2`, :math:`g_3`, :math:`g_4` and :math:`g_5` are real numercial
# coefficients.
# 

######################################################################
# The ``QubitPauliOperator`` is a dictionary mapping
# `pytket.pauli.QubitPauliString <https://tket.quantinuum.com/api-docs/pauli.html#pytket.pauli.QubitPauliString>`_
# to a complex coefficient. These coefficients are sympified (converted from python ``complex`` types
# to sympy ``complex`` types).
# 

######################################################################
# The ``QubitPauliString`` is a map from ``pytket.circuit.Qubit`` to ``pytket.pauli.Pauli``.
# 

######################################################################
# The coefficients in the Hamiltonian are obtained from
# `PhysRevX.6.031007 <https://journals.aps.org/prx/abstract/10.1103/PhysRevX.6.031007>`__.
# 

from pytket.utils.operators import QubitPauliOperator
from pytket.pauli import Pauli, QubitPauliString
from pytket.circuit import Qubit

coeffs = [-0.4804, 0.3435, -0.4347, 0.5716, 0.0910, 0.0910]
term0 = {
    QubitPauliString(
        {
            Qubit(0): Pauli.I,
            Qubit(1): Pauli.I,
        }
    ): coeffs[0]
}
term1 = {QubitPauliString({Qubit(0): Pauli.Z, Qubit(1): Pauli.I}): coeffs[1]}
term2 = {QubitPauliString({Qubit(0): Pauli.I, Qubit(1): Pauli.Z}): coeffs[2]}
term3 = {QubitPauliString({Qubit(0): Pauli.Z, Qubit(1): Pauli.Z}): coeffs[3]}
term4 = {QubitPauliString({Qubit(0): Pauli.X, Qubit(1): Pauli.X}): coeffs[4]}
term5 = {QubitPauliString({Qubit(0): Pauli.Y, Qubit(1): Pauli.Y}): coeffs[5]}
term_sum = {}
term_sum.update(term0)
term_sum.update(term1)
term_sum.update(term2)
term_sum.update(term3)
term_sum.update(term4)
term_sum.update(term5)
hamiltonian = QubitPauliOperator(term_sum)
print(hamiltonian)

######################################################################
# This Hamiltonian can be converted into a ``numpy.ndarray`` instance, and the lowest eigenvalue can
# be obtained using ``numpy.linalg.eig``. This value is used as a benchmark for the VQE result. The
# ground-state energy is measured in units of Hartrees (Ha).
# 

from scipy.linalg import eig

sm = hamiltonian.to_sparse_matrix().toarray()
ground_state_energy = eig(sm)[0].real[0]
print(f"{ground_state_energy} Ha")

######################################################################
# To measure :math:`\hat{H}` on hardware, naively 5 measurement circuits are required. The Identity
# term does not need to measured, since its expectation value always equals 1. With pytket,
# :math:`\hat{H}` only requires simulating 2 measurement circuit, thanks to measurement reduction. The
# four terms :math:`\hat{X}_{q[0]} \otimes \hat{X}_{q[1]}`,
# :math:`\hat{Y}_{q[0]} \otimes \hat{Y}_{q[1]}`, :math:`\hat{Z}_{q[0]} \otimes \hat{Z}_{q[1]}`,
# :math:`\hat{Z}_{q[0]} \otimes \hat{Z}_{q[1]}` and :math:`\hat{I}_{q[0]} \otimes \hat{Z}_{q[1]}`,
# form a commuting set and can be measured with two circuits instead of three. This partitioning can
# be performed automatically using the
# `measurement_reduction <https://tket.quantinuum.com/api-docs/partition.html#pytket.partition.measurement_reduction>`_
# function available in
# `pytket.partition <https://tket.quantinuum.com/api-docs/partition.html#module-pytket.partition>`_
# submodule.
# 

######################################################################
# The measurement operations for the two commuting set, \*
# :math:`\left\{ \hat{X}_{q[0]} \otimes \hat{X}_{q[1]}, \hat{Y}_{q[0]} \otimes \hat{Y}_{q[1]} \right\}`,
# \*
# :math:`\left\{ \hat{Z}_{q[0]} \otimes \hat{Z}_{q[1]}, \hat{Z}_{q[0]} \otimes \hat{I}_{q[1]}, \hat{I}_{q[0]} \otimes \hat{Z}_{q[1]}\right\}`
# 

######################################################################
# include additional two-qubit gate resources.
# 

from pytket.partition import (
    measurement_reduction,
    PauliPartitionStrat,
)

strat = PauliPartitionStrat.CommutingSets
pauli_strings = [term for term in hamiltonian._dict.keys()]
measurement_setup = measurement_reduction(pauli_strings, strat)

######################################################################
# A measurement subcircuit contains the necessary operations to measure the terms in a commuting set.
# The subcircuit is appended to the numerical state-preparation circuit. Combining the numerical
# state-preparation circuit and the measurement subcircuits results in a set of measurement circuits
# required to solve the problem. The
# `MeasurementSetup <https://tket.quantinuum.com/api-docs/partition.html#pytket.partition.MeasurementSetup>`_
# instance contains all the necessary sub-circuits to measure :math:`\hat{H}`. The next code cell
# lists and visualises all measurement subcircuits.
# 

from pytket.circuit.display import render_circuit_jupyter

for measurement_subcircuit in measurement_setup.measurement_circs:
    render_circuit_jupyter(measurement_subcircuit)

######################################################################
# Once the quantum computation has been completed, the measurement results can be mapped back to the
# Pauli-operations and coefficients in the Hamiltonian. This enables calculation of the expectation
# value for the Hamiltonian. The results attribute in the
# `pytket.partition.MeasurementSetup <https://tket.quantinuum.com/api-docs/partition.html#pytket.partition.MeasurementSetup>`_
# lists:
# 

######################################################################
# -  all the Pauli-strings that have been measured;
# -  information to process the quantum computed measurement result in order
# 

######################################################################
# to estimate the expectation value of each Pauli-strings.
# 

for i, (term, bitmap_list) in enumerate(measurement_setup.results.items()):
    print(f"{term}\t{bitmap_list}\n")

######################################################################
# 3. Computing Expectation Values 
# --------------------------------
# 

######################################################################
# Once the Hamiltonian has been partitioned into commuting sets, measurement circuits need to be
# constructed. These measurement circuits are submitted to hardware or emulators for simulation. Once
# the simulation is complete, a result is available to request, and can be retrieved using ``pytket``.
# These results are the outcomes of the measurement circuit simulation. Each result is a distribution
# of outcomes, specifically, the probability of observing specific bitstring. This distribution is
# post-processed to compute the expectation value of the Hamiltonian, a necessity to evaluate the cost
# function in a Hybrid Quantum-Classical variational procedure.
# 

######################################################################
# 3.1 Computing Expectation Values for Pauli-Strings
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 

######################################################################
# The Hamiltonian we are interested in consists of Pauli-strings. The expectation value of the
# Pauli-string is in the interval :math:`[-1, 1]`.
# 

######################################################################
# In the code cell below, a function is provided that calculates the expectation value of Pauli-string
# from a measured distribution. The
# `MeasurementBitmap <https://tket.quantinuum.com/api-docs/partition.html#pytket.partition.MeasurementBitMap>`_
# is used to extract the necessary data from the measured distribution. The resulting distribution can
# be summed over to estimate the expectation value of one Pauli-string.
# 

from typing import Dict, Tuple
from pytket.partition import MeasurementBitMap

def compute_expectation_paulistring(
    distribution: Dict[Tuple[int, ...], float], bitmap: MeasurementBitMap
) -> float:
    value = 0
    for bitstring, probability in distribution.items():
        value += probability * (sum(bitstring[i] for i in bitmap.bits) % 2)
    return ((-1) ** bitmap.invert) * (-2 * value + 1)

######################################################################
# In the example below, the function ``compute_expectation_paulistring`` is called to calculate the
# expectation for the :math:`\hat{Z} \otimes \hat{Z}`. First the ``QubitPauliString`` is initialised,
# and that is used to extract the relevant data from the MeasurementSetup object defined in section 2.
# This data is used for postprocessing.
# 

from pytket.pauli import Pauli, QubitPauliString
from pytket.circuit import Qubit

distribution = {(0, 0): 0.45, (1, 1): 0.3, (0, 1): 0.1, (1, 0): 0.15}
zz = QubitPauliString([Qubit(0), Qubit(1)], [Pauli.Z, Pauli.Z])
bitmap_list = measurement_setup.results.get(zz)
for bitmap in bitmap_list:
    ev = compute_expectation_paulistring(distribution, bitmap)
    print(ev)

######################################################################
# 3.2 Computing Expectation Values for sums of Pauli-strings multiplied by coefficients
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# In this step, we will submit circuits to the H-Series emulator (``H1-1E``). This circuit will
# produce a result. The result can be retrieved with the ``ResultHandle`` object. First, the symbolic
# circuit is converted into a numerical circuit. The symbols in the circuit are substituted for
# numerical parameters.
# 

symbol_map = {sym: 0.1 for sym in symbolic_circuit.free_symbols()}
numerical_circuit = symbolic_circuit.copy()
numerical_circuit.symbol_substitution(symbol_map)

######################################################################
# 3.3 Using QuantinuumBackend
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# The Quantinuum backend was initialised at the start of the notebook to use the H1-1E emulator. This
# backend will now be used to calculate the expectation value. The measurement operations from the
# ``MeasurementSetup`` object are appended to the numerical circuit. Once this step is complete, the
# circuit is ready for submission if tket optimisation in the H-Series stack is selected.
# 

circuit_list = []
for mc in measurement_setup.measurement_circs:
    c = numerical_circuit.copy()
    c.append(mc)
    circuit_list += [c]
compiled_circuit_list = quantinuum_backend.get_compiled_circuits(
    circuit_list, optimisation_level=2
)

######################################################################
# Before submitting to the emulator, the total cost of running the set of circuits can be checked
# beforehand.
# 

cost_list = []

n_shots = 500
for comp_circ in compiled_circuit_list:
    cost = quantinuum_backend.cost(comp_circ, n_shots=n_shots, syntax_checker="H1-1SC")
    cost_list.append(cost)

print("Cost of experiment in HQCs:", sum(cost_list))

######################################################################
# Now we run the circuits.
# 

handles = quantinuum_backend.process_circuits(
    compiled_circuit_list, n_shots=10, options={"tket-opt-level": None}
)

######################################################################
# The status of the jobs can be checked with ``ciruit_status`` method. This method requires the
# ``ResultHandle`` to be passed as input. In this example, the job has completed and the results are
# reported as being ready to request.
# 

for h in handles:
    circuit_status = quantinuum_backend.circuit_status(h)
    print(circuit_status)

######################################################################
# The expectation value of the operator can be evaluated with the function
# ``compute_expectation_value`` in the next code cell. This function requires a list of
# ``BackendResult`` objects, a ``MeasurementSetup`` instance, and the ``QubitPauliOperator`` instance
# for the expectation value computation. It is assumed the ``MeasurementSetup`` instance contains the
# measurement info of all the Pauli-strings in the ``QubitPauliOperator`` instance. Otherwise the
# ``compute_expectation_value`` function will return zero.
# 

from typing import List
from pytket.utils.operators import QubitPauliOperator
from pytket.partition import MeasurementSetup
from pytket.backends.backendresult import BackendResult

from sympy import Abs

def compute_expectation_value(
    results: List[BackendResult],
    measurement_setup: MeasurementSetup,
    operator: QubitPauliOperator,
) -> float:
    energy = 0
    for pauli_string, bitmaps in measurement_setup.results.items():
        string_coeff = operator.get(pauli_string, 0.0)
        if Abs(string_coeff) > 0:
            value = 0
            for bm in bitmaps:
                index = bm.circ_index
                distribution = results[index].get_distribution()
                value += compute_expectation_paulistring(distribution, bm)
            energy += value * string_coeff / len(bitmaps)
    return energy

######################################################################
# The results of the previously submitted circuits can be retrieved with the ``get_results`` method on
# ``QuantinuumBackend``.
# 

results = quantinuum_backend.get_results(handles)

######################################################################
# Finally, the expectation value,
# :math:`\langle{\psi (\vec{\theta}_r)} | \hat{H} | { \psi (\vec{\theta}_r)} \rangle`, of the
# ``QubitPauliOperator`` instance, :math:`\hat{H}`, is calculated with respect to
# :math:`| { \psi (\vec{\theta}_r)} \rangle`. The state, :math:`| \psi \rangle`, is prepared with the
# state-preparation circuit, and :math:`\vec{\theta}_r` is a random parameter set.
# 

expectation_value = compute_expectation_value(results, measurement_setup, hamiltonian)
print(f"Expectation Value: {expectation_value}")

######################################################################
# 4. Variational Procedure 
# -------------------------
# 

######################################################################
# A hybrid quantum-classical variational procedure consists of multiple iterations, controlled by a
# classical parameter optimiser. The parameters are gate-angles on quantum circuits submitted to
# H-Series for simulation. In `step 3 <#expval>`__, a procedure is showcased to calculate the
# expectation value of a Hamiltonian with respect to a quantum state. It is shown how to use the
# measurement reduction and Pauli-string partitioning facility in ``pytket`` to reduce measurement
# resources for the experiments. For the variational procedure demonstrated below, the cost function
# calculates the expectation of an input Hamiltonian. The aim is to find the optimal parameters that
# minimise this expectation value.
# 

######################################################################
# 4.1. Objective function
# ~~~~~~~~~~~~~~~~~~~~~~~
# 

######################################################################
# The ``Objective`` class defined in the code cell performs the following utilities: \* Measurement
# Reduction; \* Creation of a Batch session to use across the variational experiment; \* Submission
# and retrieval of quantum circuits using ``QuantinuumBackend``; \* Expectation Value evaluation.
# 

######################################################################
# The ``Objective`` class requires the following inputs: \* Input symbolic state-preparation circuit;
# \* A ``QubitPauliOperator`` instance of the Hamiltonian characterising the use-case of interest; \*
# The backend to use. ``QuantinuumBackend`` is used to access H-Series service. The backend needs to
# be instantiated and the user needs to login within previous code cell. \* Number of shots to perform
# per circuit. H-Series devices have an upper limit of 10000 shots per job. \* Maximum consumable HQC
# credit before the batch is terminated. \* Number of iterations before the variational experiment is
# terminated.
# 

######################################################################
# The ``Objective`` class instance can be passed as a callable to ``scipy.optimize.minimize``.
# 

from typing import Callable
from numpy import ndarray
from numpy.random import random_sample
from pytket.extensions.quantinuum import QuantinuumBackend
from pytket.partition import PauliPartitionStrat
from pytket.backends.resulthandle import ResultHandle

class Objective:
    def __init__(
        self,
        symbolic_circuit: Circuit,
        problem_hamiltonian: QubitPauliOperator,
        quantinuum_backend: QuantinuumBackend,
        n_shots_per_circuit: int,
        max_batch_cost: float = 300,
        n_iterations: int = 10,
    ) -> None:
        r"""Returns the objective function needed for a variational
        procedure on H-Series.
        Args:
            symbolic_circuit
            (pytket.circuit.Circuit): State-preparation
                circuit with symbolic parameters
            problem_hamiltonian (pytket.utils.operators.QubitPauliOperator):
                QubitPauliOperator instance defining the Hamiltonian of the
                problem.
            quantinuum_backend (pytket.extensions.quantinuum.QuantinuumBackend): Backend
                instance to use for the simulation. This will be
                QuantinuumBackend from the pytket.extensions.quantinuum
                package to run experiments on H-Series devices and emulators.
            n_shots_per_circuit (int): Number of shots per circuit.
            max_batch_cost (float): Maximum cost of all jobs in batch. If
                exceeded the batch will terminate.
            n_iterations (int): Total number of iterations before ending
                the batch session.
        Returns:
            Callable[[ndarray], float]
        """
        terms = [term for term in problem_hamiltonian._dict.keys()]
        self._symbolic_circuit: Circuit = symbolic_circuit
        self._symbols: List[Symbol] = symbolic_circuit.free_symbols()
        self._hamiltonian: QubitPauliOperator = problem_hamiltonian
        self._backend: QuantinuumBackend = quantinuum_backend
        self._nshots: int = n_shots_per_circuit
        self._max_batch_cost: float = max_batch_cost
        self._measurement_setup: MeasurementSetup = measurement_reduction(
            terms, strat=PauliPartitionStrat.CommutingSets
        )
        self._iteration_number: int = 0
        self._niters: int = n_iterations

    def __call__(self, parameter: ndarray) -> float:
        value = self._objective_function(parameter, self._iteration_number)
        self._iteration_number += 1
        if self._iteration_number >= self._niters:
            self._iteration_number = 0
        return value

    def circuit_cost(self, syntax_checker: str = "H1-1SC") -> float:
        n = len(self._symbolic_circuit.free_symbols())
        random_parameters = random_sample(n)
        return sum(
            [
                self._backend.cost(c, self._nshots, syntax_checker=syntax_checker)
                for c in self._build_circuits(random_parameters)
            ]
        )

    def _objective_function(
        self,
        parameters: ndarray,
        iteration_number: int,
    ) -> float:
        r"""Substitutes input parameters into the
        symbolic state-preparation circuit, and
        calculates the expectation value.
        Args:
            parameters (ndarray): A list of numpy.ndarray
        Returns:
            float
        """
        assert len(parameters) == len(self._symbolic_circuit.free_symbols())
        circuit_list = self._build_circuits(parameters)
        if not isinstance(self._backend, QuantinuumBackend):
            raise RuntimeError(
                "Batching is not supported for any backend other than QuantinuumBackend."
            )
        if iteration_number == 0:
            self._startjob = self._backend.start_batch(
                self._max_batch_cost,
                circuit_list[0],
                self._nshots,
                noisy_simulation=False,
                options={"tket-opt-level": None},
            )
            handles = [self._startjob] + self._submit_batch(circuit_list[1:])
        else:
            handles = self._submit_batch(circuit_list)
        results = self._backend.get_results(handles)
        expval = compute_expectation_value(
            results, self._measurement_setup, self._hamiltonian
        )
        return expval

    def _build_circuits(self, parameters: ndarray) -> List[Circuit]:
        circuit = self._symbolic_circuit.copy()
        symbol_dict = {s: p for s, p in zip(self._symbols, parameters)}
        circuit.symbol_substitution(symbol_dict)
        circuit_list = []
        for mc in self._measurement_setup.measurement_circs:
            c = circuit.copy()
            c.append(mc)
            circuit_list.append(c)
        cc_list = self._backend.get_compiled_circuits(
            circuit_list, optimisation_level=2
        )
        return cc_list

    def _submit_batch(
        self,
        circuits: List[Circuit],
    ) -> List[ResultHandle]:
        r"""Submit a list of circuits with N shots each
        to the H-Series batch.
        Args:
            circuits (List[Circuit]): A list of circuits
                to submit to the batch on H-Series.
            first job (ResultHandle): The result handle for the
                first job submitted in the batch.
        Returns:
            List[ResultHandle]
        """
        return [
            self._backend.add_to_batch(
                self._startjob,
                c,
                self._nshots,
                options={"tket-opt-level": None},
                noisy_simulation=False,
            )
            for c in circuits
        ]

######################################################################
# The ``Objective`` class is initialised with the essential data needed to perform the variational
# experiment. The object contains all the necessary information to compute the value of the objective
# function.
# 

######################################################################
# A convenience method ``circuit_cost`` can be used to estimate the total number of HQCs required to
# estimate the objective function. The variational loop will be multiples of this value (number of
# function calls across the variational procedure multiplied by the HQC cost of evaluating the
# objective function).
# 

n_shots_per_circuit = 500
n_iterations = 10
max_batch_cost = 500
objective = Objective(
    symbolic_circuit,
    hamiltonian,
    quantinuum_backend,
    n_shots_per_circuit,
    max_batch_cost=max_batch_cost,
    n_iterations=n_iterations,
)

objective.circuit_cost("H1-1SC")

######################################################################
# 4.2. Execute the Objective Function
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# The SciPy minimiser is used to optimise the value of the objective function. Initial parameters are
# pseudo-random. Passing the ``Objective`` instance into ``scipy.optimize.minimize`` will start the
# variational experiment.
# 

######################################################################
# The first iteration creates a batch session, and all subsequent circuit submission are added to this
# batch. If additional circuits are not submitted within 1 minute, the batch session will terminate.
# 

######################################################################
# Remember that the status of the batch can be checked at any time on the Quantinuum User Portal.
# 

from scipy.optimize import minimize
from numpy.random import random_sample

method = "COBYLA"
initial_parameters = random_sample(len(symbolic_circuit.free_symbols()))

result = minimize(
    objective,
    initial_parameters,
    method=method,
    options={"disp": True, "maxiter": objective._niters},
    tol=1e-2,
)

######################################################################
# The minimal value of the objective function can be retrieved with the ``fun`` attribute.
# 

print(f"VQE Energy:\t{result.fun} Ha")

######################################################################
# The ground-state energy estimated with VQE can be compared with the value obtained from the
# ``numpy.linalg`` computation. The absolute error and the relative error is calculated here.
# 

import numpy as np

abs_err = lambda experiment, benchmark: np.absolute(experiment - benchmark)
rel_err = (
    lambda experiment, benchmark: abs_err(experiment, benchmark)
    / np.absolute(benchmark)
    * 100
)

ae = abs_err(result.fun, ground_state_energy)
re = rel_err(result.fun, ground_state_energy)
print(f"Absolute error:\t{ae} Ha\nRelative error:\t{re}%")

######################################################################
# The optimal parameters can be retreived with the ``x`` attribute.
# 

result.x

######################################################################
# The Symbols can be mapped to the optimal parameter by iterating through both lists:
# 

optimal_parameters = {s.name: p for s, p in zip(objective._symbols, result.x)}
print(optimal_parameters)

######################################################################
# These symbols can be saved to an output file for further use if necessary using json. See the
# example below.
# 

import json

json_io = open("parameters.json", "w")
json.dump(optimal_parameters, json_io)