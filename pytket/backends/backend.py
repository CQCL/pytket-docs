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

from abc import ABC, abstractmethod
from pytket._circuit import Circuit
from pytket.backends.measurements import pauli_measurement
import numpy as np

class Backend(ABC) :
    """
    This abstract class defines the structure of a backend as something that
    can run quantum circuits and produce a per-shot output
    """
    @abstractmethod
    def __init__(self) :
        pass
    
    @abstractmethod
    def run(self, circuit:Circuit, shots:int, fit_to_constraints=True) -> np.ndarray :
        """Run the circuit on the backend and return results, optionally fitting the circuit to the constraints of the backend.
        
        :param circuit: The circuit to run
        :type circuit: Circuit
        :param shots: Number of shots (repeats) to run
        :type shots: int
        :param fit_to_constraints: Compile the circuit to meet the constraints of the backend, defaults to True
        :type fit_to_constraints: bool, optional
        :return: Table of shot results, each row is a shot, columns are ordered by qubit ordering. Values are 0 or 1 corresponding to qubit basis states.
        :rtype: numpy.ndarray
        """
        
        pass
    
    def get_pauli_expectation_value(self, state_circuit, pauli, shots=1000) :
        """
        Calculates expectation value for pauli term by preparing basis change circuit and measuring
        """
        if not pauli:
            return 1
        measured_circ = state_circuit.copy()
        pauli_measurement(pauli, measured_circ)
        results_table = self.run(measured_circ, shots)
        aritysum = 0.
        for row in results_table :
            aritysum += np.sum(row) % 2
        return -2*aritysum/shots + 1
    
    def get_operator_expectation_value(self, state_circuit, operator, shots=1000) :
        """
        Calculates expectation value for an OpenFermion QubitOperator by summing over pauli expectations
        """
        energy = 0
        for pauli, coeff in operator.terms.items() :
            energy += coeff*self.get_pauli_expectation_value(state_circuit, pauli, shots)
        return energy
    
    def get_counts(self, circuit, shots, fit_to_constraints=True) :
        """
        Run the circuit on the backend and accumulate the results into a summary of counts

        :param circuit: The circuit to run
        :param shots: Number of shots (repeats) to run
        :param fit_to_constraints: Compile the circuit to meet the constraints of the backend, defaults to True
        :return: Dictionary mapping bitvectors of results to number of times that result was observed (zero counts are omitted)
        """
        shot_table = self.run(circuit, shots, fit_to_constraints)
        shots, counts = np.unique(shot_table, axis=0, return_counts=True)
        return {tuple(s):c for s, c in zip(shots, counts)}