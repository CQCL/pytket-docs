# Copyright 2019 Cambridge Quantum Computing
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Engine for the Quantum Subspace Expansion algorithm
"""

import time
import logging
import itertools
from typing import List

import numpy as np
from multiprocessing import Pool, cpu_count
from _pickle import PicklingError
from qiskit import QuantumCircuit, ClassicalRegister

from pytket.chemistry.aqua.qse_subs import QseMatrices

from qiskit.aqua import QuantumAlgorithm, AquaError, Operator
from qiskit.aqua.components.variational_forms import VariationalForm
logger = logging.getLogger(__name__)
logger = logging.getLogger('qiskit.aqua')


class QSE(QuantumAlgorithm):
    """
    :py:class:`qiskit.aqua.QuantumAlgorithm` implementation for Quantum Subspace Expansion (QSE)
    [See Phys. Rev. A 95, 042308 (2017)].
    """

    CONFIGURATION = {
        'name': 'QSE',
        'description': 'QSE Algorithm',
        'input_schema': {
            '$schema': 'http://json-schema.org/schema#',
            'id': 'qse_schema',
            'type': 'object',
            'properties': {
                'operator_mode': {
                    'type': 'string',
                    'default': 'matrix',
                    'oneOf': [
                        {'enum': ['matrix', 'paulis', 'grouped_paulis']}
                    ]
                },
                'initial_point': {
                    'type': ['array', 'null'],
                    "items": {
                        "type": "number"
                    },
                    'default': None
                }
            },
            'additionalProperties': False
        },
        'problems': ['energy', 'ising'],
        'depends': ['variational_form', 'initial_state'],
        'defaults': {
            'variational_form': {
                'name': 'UCCSD'
            },
            'initial_state': {
                'name': 'ZERO'
            }
        }
    }

    def __init__(self, qse_operators:QseMatrices, operator_mode:str, var_form:VariationalForm,
                  opt_init_point:np.ndarray=None, aux_operators:List[Operator]=[]):
        """
        :param qse_operators: Qubit operator generator
        :param operator_mode: Operator mode to be used for evaluation of the operator
        :param var_form: Parametrized variational form
        :param opt_init_point: Initial point for the optimisation
        :param aux_operators: Auxiliary operators to be evaluated at each eigenvalue
        """
        super().__init__()
        self._qse_operators = qse_operators
        self._operator = None
        self._operator_mode = operator_mode
        self._var_form = var_form
        self.opt_var_params = opt_init_point
        self._aux_operators = aux_operators
        self._ret = {}
        self._eval_count = 0
        self._eval_time = 0
        if opt_init_point is None:
            self.opt_var_params = var_form.preferred_init_points
        else:
            self.opt_circuit = self._var_form.construct_circuit(self.opt_var_params)
        self._quantum_state = None

    @property
    def setting(self):
        ret = "Algorithm: {}\n".format(self._configuration['name'])
        params = ""
        for key, value in self.__dict__.items():
            if key != "_configuration" and key[0] == "_":
                if "opt_init_point" in key and value is None:
                    params += "-- {}: {}\n".format(key[1:], "Random seed")
                else:
                    params += "-- {}: {}\n".format(key[1:], value)
        ret += "{}".format(params)
        return ret

    def print_setting(self) -> str:
        """
        Presents the QSE settings as a string.

        :return: The formatted settings of the QSE instance
        """
        ret = "\n"
        ret += "==================== Setting of {} ============================\n".format(self.configuration['name'])
        ret += "{}".format(self.setting)
        ret += "===============================================================\n"
        ret += "{}".format(self._var_form.setting)
        ret += "===============================================================\n"
        return ret

    def _energy_evaluation(self, operator):
        """
        Evaluate the energy of the current input circuit with respect to the given operator.

        :param operator: Hamiltonian of the system

        :return: Energy of the Hamiltonian
        """
        if self._quantum_state is not None:
            input_circuit = self._quantum_state
        else:
            input_circuit = [self.opt_circuit]
        if operator._paulis:
            mean_energy, std_energy = operator.evaluate_with_result(self._operator_mode, input_circuit,
                                                                    self._quantum_instance.backend, self.ret)
        else:
            mean_energy = 0.0
            std_energy = 0.0
        operator.disable_summarize_circuits()
        logger.debug('Energy evaluation {} returned {}'.format(self._eval_count, np.real(mean_energy)))
        return np.real(mean_energy), np.real(std_energy)

    def _h_qse_finder(self, pair):
        i, j = pair

        term = self._qse_operators.hamiltonian_term(i, j)
        term.chop(1e-10)
        
        result, std_ij = self._energy_evaluation(term)

        return result

    #Measure elements of the overlap matrix


    def _s_qse_finder(self, pair):
        i, j = pair
        term = self._qse_operators.overlap_term(i, j)
        result, std_ij = self._energy_evaluation(term)

        return result

    def _linear_compute(self, terms, _n_qubits):
        matrix = np.zeros((_n_qubits**2, _n_qubits**2), dtype=np.float)
        pairs = filter(lambda x: x[1]>=x[0], itertools.product(range(_n_qubits**2), repeat=2))
        completed = 0
        total = _n_qubits**4
        for pair, term in zip(pairs, terms):
            i, j = pair
            result, std = self._energy_evaluation(term)
            matrix[[i,j], [j,i]] = result
            completed += 2
            if completed % 1 ==0:
                logger.info("Matrix Filled: {0:.2%}".format(completed/total))
        return matrix

    def _parallel_compute(self, terms, _n_qubits):
        matrix = np.zeros((_n_qubits**2, _n_qubits**2), dtype=np.float)
        N_CORES = cpu_count()
        pairs = filter(lambda x: x[1]>=x[0], itertools.product(range(_n_qubits**2), repeat=2))
        n_calcs = N_CORES*5
        next_terms = list(itertools.islice(terms, n_calcs))
        next_pairs = list(itertools.islice(pairs, n_calcs))
        completed = 0
        total = _n_qubits**4
        with Pool(N_CORES) as p:
            while next_terms:
                start = time.time()
                results, stdev = zip(*p.map(self._energy_evaluation, next_terms))
                i_s, j_s = zip(*next_pairs)
                results = np.array(list(results))
                matrix[i_s, j_s] = results
                matrix[j_s, i_s] = results
                next_terms = list(itertools.islice(terms, n_calcs))
                next_pairs = list(itertools.islice(pairs, n_calcs))

                completed += n_calcs*2
                logger.debug("{} calculations in {}".format(n_calcs, time.time() - start))
                logger.info("Matrix Filled: {0:.2%}".format(completed/total))
        return matrix

    def _generate_terms(self):
        n_qubits = self._qse_operators.n_qubits
        pairs = list(filter(lambda x: x[1]>=x[0], itertools.product(range(n_qubits**2), repeat=2)))
        def chop(term):
            term.chop(1e-10)
            return term
        h_terms = (chop(term) for term in(self._qse_operators.hamiltonian_term(i, j) for i, j in pairs))
        s_terms = (self._qse_operators.overlap_term(i, j) for i, j in pairs)

        return h_terms, s_terms

    def _solve(self, parallel=True):
        
        h_terms, s_terms = self._generate_terms()
        n_qubits = self._qse_operators.n_qubits
        
        if parallel:
            h_qse_matrix = self._parallel_compute(h_terms, n_qubits)
            s_qse_matrix = self._parallel_compute(s_terms, n_qubits)
        else:
            h_qse_matrix = self._linear_compute(h_terms, n_qubits)
            s_qse_matrix = self._linear_compute(s_terms, n_qubits)
        
        eigvals, vectors = np.linalg.eig(np.matmul(np.linalg.pinv(s_qse_matrix),h_qse_matrix))

        eigvals = np.real(eigvals)
        eigvals.sort()

        self._ret['eigvals'] = eigvals



    def _eval_aux_ops(self, threshold=1e-12):
        wavefn_circuit = self._var_form.construct_circuit(self._ret['opt_params'])
        values = []
        for operator in self._aux_operators:
            mean, std = 0.0, 0.0
            if not operator.is_empty():
                mean, std = operator.eval(self._operator_mode, wavefn_circuit,
                                          self._backend, self._execute_config, self._qjob_config)
                mean = mean.real if abs(mean.real) > threshold else 0.0
                std = std.real if abs(std.real) > threshold else 0.0
            values.append((mean, std))
        if len(values) > 0:
            aux_op_vals = np.empty([1, len(self._aux_operators), 2])
            aux_op_vals[0, :] = np.asarray(values)
            self._ret['aux_ops'] = aux_op_vals

    def _run(self) -> dict:
        """
        Runs the QSE algorithm to compute the eigenvalues of the Hamiltonian.

        :return: Dictionary of results
        """
        if not self._quantum_instance.is_statevector:
            raise AquaError("Can only calculate state for QSE with statevector backends")
        ret = self._quantum_instance.execute(self.opt_circuit)
        self.ret = ret
        self._eval_count = 0
        self._solve()
        self._ret['eval_count'] = self._eval_count
        self._ret['eval_time'] = self._eval_time
        return self._ret
