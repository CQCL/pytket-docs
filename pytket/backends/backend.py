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
    def run(self, circuit, shots) :
        """
        Returns table showing results for each shot
        Rows are shots, columns are qubits/measurements (column i corresponds to bit i in the classical register)
        Each cell is the readout from each measurement, with 0 being |0> and 1 for |1>
        """
        pass
    
    def get_pauli_expectation_value(self, state_circuit, pauli, shots=1000) :
        """
        Calculates expectation value for pauli term by preparing basis change circuit and measuring
        """
        if len(pauli) == 0 :
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