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
from qiskit.converters import dag_to_circuit
from qiskit import IBMQ
from qiskit.compiler import assemble
from qiskit.tools.monitor import job_monitor

from pytket.backends.measurements import bin_str_2_table
from pytket.backends import Backend
from pytket.qiskit import coupling_to_arc, tk_to_dagcircuit
from pytket._routing import route
from pytket._transform import Transform

import numpy as np

class IBMQBackend(Backend) :
    def __init__(self, backend_name, monitor=True) :
        if len(IBMQ.stored_accounts()) ==0:
            raise ValueError('No IBMQ credentials found on disk. Store some first.')
        IBMQ.load_accounts()
        self._backend = IBMQ.get_backend(backend_name)
        coupling = self._backend.configuration().coupling_map
        self.architecture = coupling_to_arc(coupling)
        self._monitor = monitor
    
    def run(self, circuit, shots, fit_to_constraints=True) :
        c = circuit.copy()
        if fit_to_constraints :
            Transform.OptimisePhaseGadgets().apply(c)
            c = route(c, self.architecture)._get_circuit()
            Transform.OptimisePostRouting().apply(c)
        dag = tk_to_dagcircuit(c)
        qc = dag_to_circuit(dag)

        qobj = assemble(qc, shots=shots, memory=True)
        job = self._backend.run(qobj)
        if self._monitor :
            job_monitor(job)
        
        shot_table = bin_str_2_table(job.result().get_memory(qc))
        return shot_table
