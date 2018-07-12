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

"""Wrapper module for routing interface
"""

from pytket.cirq_convert import cirq2coms, coms2cirq
from pytket import route, SquareGrid
import cirq

def route_circuit(circuit: cirq.Circuit, arc: SquareGrid) -> cirq.Circuit:
    """Route the cirq circuit on the given architecture by adding swaps (satisfy adjacency constraints)
    
    Arguments:
        circuit {cirq.Circuit} -- Input circuit
        arc {SquareGrid} -- architecture to route on
    
    Keyword Arguments:
        place {bool} -- Whether to remap qubit positions initially (default: {True})
    
    Returns:
        cirq.Circuit -- output circuit
    """

    coms = cirq2coms(circuit, arc)
    init_map = list(range(coms.n_qubits()))
    # print(init_map)
    routed_coms = route(coms, arc, init_map)
    return coms2cirq(routed_coms, arc)