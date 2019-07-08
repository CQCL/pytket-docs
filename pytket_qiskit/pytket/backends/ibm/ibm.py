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

import itertools
import qiskit
from typing import Tuple, Iterable
from qiskit.converters import dag_to_circuit
from qiskit import IBMQ, QuantumCircuit
from qiskit.compiler import assemble
from qiskit.tools.monitor import job_monitor

from pytket.backends import Backend
from pytket.qiskit import tk_to_dagcircuit
from pytket._routing import route, Architecture
from pytket._transform import Transform
from pytket._circuit import Circuit
import numpy as np

VALID_BACKEND_GATES = (
    qiskit.extensions.standard.u1.U1Gate,
    qiskit.extensions.standard.u2.U2Gate,
    qiskit.extensions.standard.u3.U3Gate,
    qiskit.extensions.standard.cx.CnotGate,
    qiskit.circuit.measure.Measure
    )

def _qiskit_circ_valid(qc: QuantumCircuit, coupling:Iterable[Tuple[int]] ) -> bool:
    valid = True
    measure_count = 0
    for instruction in qc:
        if type(instruction[0]) not in VALID_BACKEND_GATES:
            valid = False
            break
        if isinstance(instruction[0], qiskit.circuit.measure.Measure):
            measure_count += 1
        if len(instruction[1]) > 1:
            control = instruction[1][0][1]
            target = instruction[1][1][1]
            if [control, target] not in coupling:
                valid =False
                break
    return valid, (measure_count > 0)

def _routed_ibmq_circuit(circuit:Circuit, arc: Architecture) -> QuantumCircuit:
    c = circuit.copy()
    Transform.RebaseToQiskit().apply(c)
    physical_c = route(c, arc)
    physical_c.decompose_SWAP_to_CX()
    physical_c.redirect_CX_gates(arc)
    Transform.OptimisePostRouting().apply(physical_c)
    dag = tk_to_dagcircuit(physical_c)
    qc = dag_to_circuit(dag)

    return qc

def _convert_bin_str(string) :
    return [int(b) for b in string.replace(' ', '')][::-1]

class IBMQBackend(Backend) :
    def __init__(self, backend_name:str, monitor:bool=True) :
        """A backend for running circuits on remote IBMQ devices.

        :param backend_name: name of ibmq device. e.g. `ibmqx4`, `ibmq_16_melbourne`.
        :type backend_name: str
        :param monitor: Use IBM job monitor, defaults to True
        :type monitor: bool, optional
        :raises ValueError: If no IBMQ account has been set up.
        """
        if len(IBMQ.stored_accounts()) ==0:
            raise ValueError('No IBMQ credentials found on disk. Store some first.')
        IBMQ.load_accounts()
        self._backend = IBMQ.get_backend(backend_name)
        self.config = self._backend.configuration()
        self.coupling = self.config.coupling_map
        self.architecture = Architecture(self.coupling)
        self._monitor = monitor
    
    def run(self, circuit:Circuit, shots:int, fit_to_constraints:bool=True) -> np.ndarray :
        if fit_to_constraints:
            qc = _routed_ibmq_circuit(circuit, self.architecture)
        else:
            dag = tk_to_dagcircuit(circuit)
            qc = dag_to_circuit(dag)
        valid, measures = _qiskit_circ_valid(qc, self.coupling)
        if not valid:
            raise RuntimeWarning("QuantumCircuit does not pass validity test, will likely fail on remote backend.")
        if not measures:
            raise RuntimeWarning("Measure gates are required for output.")
        
        qobj = assemble(qc, shots=shots, memory=self.config.memory)
        job = self._backend.run(qobj)
        if self._monitor :
            job_monitor(job)
        
        shot_list = []
        if self.config.memory:
            shot_list = job.result().get_memory(qc)
        else:
            for string, count in job.result().get_counts().items():
                shot_list += [string]*count
        return np.asarray([_convert_bin_str(shot) for shot in shot_list])
    
    def get_counts(self, circuit, shots, fit_to_constraints=True) :
        """
        Run the circuit on the backend and accumulate the results into a summary of counts

        :param circuit: The circuit to run
        :param shots: Number of shots (repeats) to run
        :param fit_to_constraints: Compile the circuit to meet the constraints of the backend, defaults to True
        :param seed: Random seed to for simulator
        :return: Dictionary mapping bitvectors of results to number of times that result was observed (zero counts are omitted)
        """
        if fit_to_constraints:
            qc = _routed_ibmq_circuit(circuit, self.architecture)
        else:
            dag = tk_to_dagcircuit(circuit)
            qc = dag_to_circuit(dag)
        valid, measures = _qiskit_circ_valid(qc, self.coupling)
        if not valid:
            raise RuntimeWarning("QuantumCircuit does not pass validity test, will likely fail on remote backend.")
        if not measures:
            raise RuntimeWarning("Measure gates are required for output.")
        qobj = assemble(qc, shots=shots)
        job = self._backend.run(qobj)
        counts = job.result().get_counts(qc)
        return {tuple(_convert_bin_str(b)) : c for b, c in counts.items()}