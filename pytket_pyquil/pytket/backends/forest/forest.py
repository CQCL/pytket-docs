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

from pyquil import get_qc
from pyquil.api import WavefunctionSimulator
from pyquil.paulis import PauliTerm, ID, PauliSum

from pytket import Circuit
from pytket.backends import Backend
from pytket._transform import Transform
from pytket._routing import route, Architecture
from pytket.pyquil import tk_to_pyquil

import numpy as np

def _gen_PauliTerm(term, coeff=1.) :
    pauli_term = ID() * coeff
    for q, p in term :
        pauli_term *= PauliTerm(p, q)
    return pauli_term

class ForestBackend(Backend) :
    def __init__(self, qc_name, simulator=True) :
        """Backend for running simulations on the Rigetti QVM or a QCS device
        
        :param qc_name: The name of the particular QuantumComputer to use. See the pyQuil docs for more details.
        :param simulator: Whether to simulate the architecture or try to connect to a physical device"""
        self._qc = get_qc(qc_name, as_qvm=simulator)
        coupling = [[n, ni] for n, neigh_dict in self._qc.qubit_topology().adjacency() for ni, _ in neigh_dict.items()]
        self._architecture = Architecture(coupling)
    
    def run(self, circuit:Circuit, shots:int, fit_to_constraints:bool=True) -> np.ndarray :
        """Run a circuit on the Rigetti QVM or a QCS device.

        :param circuit: The circuit to run
        :param shots: Number of shots (repeats) to run
        :param fit_to_constraints: Compile the circuit to meet the constraints of the backend, defaults to True
        :return: Table of shot results, each row is a shot, columns are ordered by qubit ordering. Values are 0 or 1, corresponding to qubit basis states.
        """
        c = circuit.copy()
        if fit_to_constraints :
            phys_c = route(c, self._architecture)
            phys_c.decompose_SWAP_to_CX()
            Transform.OptimisePostRouting().apply(phys_c)
            Transform.RebaseToQuil().apply(c)
        p = tk_to_pyquil(c)
        p.wrap_in_numshots_loop(shots)
        ex = self._qc.compiler.native_quil_to_executable(p)
        return np.asarray(self._qc.run(ex))

class ForestStateBackend(Backend) :
    def __init__(self) :
        """Backend for running simulations on the Rigetti QVM Wavefunction Simulator.
        """
        self._sim = WavefunctionSimulator()
    
    def get_state(self, circuit, fit_to_constraints=True) :
        """Calculate the statevector for a circuit.
        :param circuit: circuit to calculate
        :return: complex numpy array of statevector
        """
        c = circuit.copy()
        if fit_to_constraints :
            Transform.RebaseToQuil().apply(c)
        p = tk_to_pyquil(c)
        wf = self._sim.wavefunction(p)
        return wf.amplitudes
    
    def run(self, circuit, shots, fit_to_constraints=True) :
        pass
    
    def get_pauli_expectation_value(self, state_circuit, pauli, shots=1000) :
        c = state_circuit.copy()
        Transform.RebaseToQuil().apply(c)
        prog = tk_to_pyquil(c)
        pauli_term = _gen_PauliTerm(pauli)
        return self._sim.expectation(prog, [pauli_term])
    
    def get_operator_expectation_value(self, state_circuit, operator, shots=1000) :
        c = state_circuit.copy()
        Transform.RebaseToQuil().apply(c)
        prog = tk_to_pyquil(c)
        pauli_sum = PauliSum([_gen_PauliTerm(term, coeff) for term, coeff in operator.terms.items()])
        return self._sim.expectation(prog, pauli_sum)