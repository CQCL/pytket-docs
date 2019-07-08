# Copyright 2018 Cambridge Quantum Computing
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

"""Methods to allow t|ket> circuits to be ran on ProjectQ simulator
"""
import projectq
from projectq.cengines import ForwarderEngine
from projectq import MainEngine
from projectq.ops import *
from projectq.backends import *

from pytket._circuit import Circuit
from pytket._transform import Transform
from pytket._simulation import pauli_tensor_matrix
from pytket.backends import Backend
from pytket.projectq import tk_to_projectq

import numpy as np

def projectq_expectation_value(circuit:Circuit,hamiltonian:QubitOperator) -> float :
    ProjectQback = Simulator()
    fwd = ForwarderEngine(ProjectQback)
    eng = MainEngine(backend=ProjectQback,engine_list=[fwd])
    qureg = eng.allocate_qureg(circuit.n_qubits)
    c = circuit.copy()
    Transform.RebaseToProjectQ().apply(c)
    tk_to_projectq(eng,qureg,c)
    eng.flush()
    energy = eng.backend.get_expectation_value(hamiltonian,qureg)
    All(Measure) | qureg
    return energy

class ProjectQBackend(Backend) :
    def __init__(self) :
        self._backend = Simulator()

    def get_state(self,circuit:Circuit, fit_to_constraints=True) -> list:
        c = circuit.copy()
        if fit_to_constraints :
            Transform.RebaseToProjectQ().apply(c)
        fwd = ForwarderEngine(self._backend)
        eng = MainEngine(backend=self._backend,engine_list=[fwd])
        qureg = eng.allocate_qureg(c.n_qubits)
        tk_to_projectq(eng,qureg,c)
        eng.flush()
        state = self._backend.cheat()[1] #`cheat()` returns tuple:(a dictionary of qubit indices, statevector)
        All(Measure) | qureg
        return state #list of complex numbers

    def run(self, circuit:Circuit, shots:int, fit_to_constraints=True) -> np.ndarray:
        state = self.get_state(circuit, fit_to_constraints)
        fwd = ForwarderEngine(self._backend)
        eng = MainEngine(backend=self._backend,engine_list=[fwd])
        qb_results = []
        qureg = eng.allocate_qureg(circuit.n_qubits)

        for _ in range(shots):
            self._backend.set_wavefunction(state,qureg)
            All(Measure) | qureg
            eng.flush()
            results = (list(map(int,qureg)))
            qb_results.append(results)
        
        return np.asarray(qb_results)

    def get_pauli_expectation_value(self, state_circuit, pauli, shots=10000) -> float:
        state = self.get_state(state_circuit)
        pauli_op = pauli_tensor_matrix(pauli,state_circuit.n_qubits)
        return np.vdot(state,pauli_op.dot(state))

    def get_operator_expectation_value(self, state_circuit, operator, shots=10000) -> float:
        """
        Calculates expectation value for an OpenFermion QubitOperator by summing over pauli expectations
        Note: This method is significantly faster using the ProjectQBackend than the AerStateBackend.
        """
        #turn operator into QubitOperator object
        return projectq_expectation_value(state_circuit,operator)
