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

from qiskit import Aer
from qiskit.converters import dag_to_circuit
from qiskit.compiler import assemble
from qiskit.providers.aer.noise import NoiseModel

from pytket.backends import Backend
from pytket.qiskit import tk_to_dagcircuit
from pytket.backends.ibm.ibm import _convert_bin_str
from pytket._circuit import Circuit
from pytket._transform import Transform
from pytket._simulation import pauli_tensor_matrix, operator_matrix

import numpy as np

class AerBackend(Backend) :
    def __init__(self, noise_model:NoiseModel=None) :
        """Backend for running simulations on Qiskit Aer Qasm simulator.
        
        :param noise_model: Noise model to use in simulation, defaults to None.
        :type noise_model: NoiseModel, optional
        """
        self._backend = Aer.get_backend('qasm_simulator')
        self.noise_model = noise_model
    
    def run(self, circuit:Circuit, shots:int, fit_to_constraints=True, seed:int=None) -> np.ndarray:
        """Run a circuit on Qiskit Aer Qasm simulator.
        
        :param circuit: The circuit to run
        :type circuit: Circuit
        :param shots: Number of shots (repeats) to run
        :type shots: int
        :param fit_to_constraints: Compile the circuit to meet the constraints of the backend, defaults to True
        :type fit_to_constraints: bool, optional
        :param seed: random seed to for simulator
        :type seed: int
        :return: Table of shot results, each row is a shot, columns are ordered by qubit ordering. Values are 0 or 1, corresponding to qubit basis states.
        :rtype: numpy.ndarray
        """
        c = circuit.copy()
        if fit_to_constraints :
            Transform.RebaseToQiskit().apply(c)
        dag = tk_to_dagcircuit(c)
        qc = dag_to_circuit(dag)
        qobj = assemble(qc, shots=shots, seed_simulator=seed, memory=True)
        job = self._backend.run(qobj, noise_model=self.noise_model)
        shot_list = job.result().get_memory(qc)
        return np.asarray([_convert_bin_str(shot) for shot in shot_list])
    
    def get_counts(self, circuit, shots, fit_to_constraints=True, seed=None) :
        """
        Run the circuit on the backend and accumulate the results into a summary of counts

        :param circuit: The circuit to run
        :param shots: Number of shots (repeats) to run
        :param fit_to_constraints: Compile the circuit to meet the constraints of the backend, defaults to True
        :param seed: Random seed to for simulator
        :return: Dictionary mapping bitvectors of results to number of times that result was observed (zero counts are omitted)
        """
        c = circuit.copy()
        if fit_to_constraints :
            Transform.RebaseToQiskit().apply(c)
        dag = tk_to_dagcircuit(c)
        qc = dag_to_circuit(dag)
        qobj = assemble(qc, shots=shots, seed_simulator=seed)
        job = self._backend.run(qobj, noise_model=self.noise_model)
        counts = job.result().get_counts(qc)
        return {tuple(_convert_bin_str(b)) : c for b, c in counts.items()}

class AerStateBackend(Backend) :
    def __init__(self) :
        self._backend = Aer.get_backend('statevector_simulator')
    
    def get_state(self, circuit, fit_to_constraints=True) :
        """
        Calculate the statevector for a circuit.


        :param circuit: circuit to calculate
        :return: complex numpy array of statevector
        """
        c = circuit.copy()
        if fit_to_constraints :
            Transform.RebaseToQiskit().apply(c)
        dag = tk_to_dagcircuit(c)
        qc = dag_to_circuit(dag)
        qobj = assemble(qc)
        job = self._backend.run(qobj)
        return np.asarray(job.result().get_statevector(qc, decimals=16))
    
    def run(self, circuit, shots, fit_to_constraints=True) :
        raise Exception("Aer State Backend cannot currently generate shots. Use `get_state` instead.")
    
    def get_pauli_expectation_value(self, state_circuit, pauli, shots=1000) :
        state = self.get_state(state_circuit)
        pauli_op = pauli_tensor_matrix(pauli, state_circuit.n_qubits)
        return np.vdot(state, pauli_op.dot(state))
    
    def get_operator_expectation_value(self, state_circuit, operator, shots=1000) :
        """
        Calculates expectation value for an OpenFermion QubitOperator by summing over pauli expectations
        Note: This method is significantly faster using the ProjectQBackend than the AerStateBackend.
        """
        state = self.get_state(state_circuit)
        n_qubits = state_circuit.n_qubits
        op_as_lists = [(list(p),c) for p,c in operator.terms.items()]
        op = operator_matrix(op_as_lists, n_qubits)
        return np.vdot(state, op.dot(state))