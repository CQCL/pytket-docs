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
from typing import Iterator, List

import cirq
from cirq.google import XmonDevice, Foxtail
from cirq.devices import UnconstrainedDevice
from cirq.value import Duration
from cirq.line.placement.line import _line_placement_on_device
from pytket.cirq_convert import cirq2coms, coms2cirq, get_grid_qubits
from pytket.qubits import xmon2arc, IndexedQubit, sort_row_col
from pytket._cpptket import qubit_lines
from pytket import route, SquareGrid

def route_circuit(circuit: cirq.Circuit, arc: SquareGrid) -> cirq.Circuit:
    """Route the cirq circuit on the given architecture by adding swaps (satisfy adjacency constraints).
    
    Arguments:
        circuit {cirq.Circuit} -- Input circuit
        arc {SquareGrid} -- architecture to route on
    
    Keyword Arguments:
        place {bool} -- Whether to remap qubit positions initially (default: {False})
    
    Returns:
        cirq.Circuit -- output circuit
    """
    device = XmonDevice(Duration(nanos=0), Duration(nanos=0),
                        Duration(nanos=0), qubits=get_grid_qubits(arc, arc.get_columns()*arc.get_rows()))
    indexed_qubits = sort_row_col(device.qubits)
    def map_xmon_index(qb):
        return IndexedQubit(indexed_qubits.index(qb))

    newcirc = circuit.with_device(UnconstrainedDevice, map_xmon_index)
    arc = xmon2arc(device)
    coms = cirq2coms(newcirc, device)
    init_map = list(range(coms.n_qubits()))
    routed_coms = route(coms, arc, init_map)
    return coms2cirq(routed_coms, device)

def route_circuit_xmon(circuit: cirq.Circuit, device: XmonDevice, place=False) -> cirq.Circuit:
    indexed_qubits = sort_row_col(device.qubits)
    def map_xmon_index(qb):
        return IndexedQubit(indexed_qubits.index(qb))

    newcirc = circuit.with_device(UnconstrainedDevice, map_xmon_index)
    arc = xmon2arc(device)
    coms = cirq2coms(newcirc, device)

    if place:
        try:
            indexlines = sorted(qubit_lines(coms, len(indexed_qubits)), key=len, reverse=True)

            placed_line = _line_placement_on_device(device, 0).get().line
            if sum(map(len, filter(lambda x: len(x)>1, indexlines))) > len(placed_line):
                raise ValueError("Found line is not long enough to carry out placement, aborting", 13)
            unplaced_qubits = [qb for qb in indexed_qubits if qb not in placed_line]
            mapping = {}
            for line in indexlines:
                for qbindex in line:
                    if placed_line:
                        mapping[indexed_qubits[qbindex]] = placed_line.pop()
                    else:
                        mapping[indexed_qubits[qbindex]] = unplaced_qubits.pop()
            newcirc = circuit.with_device(UnconstrainedDevice, lambda x: map_xmon_index(mapping[x]))
            coms = cirq2coms(newcirc, device)
            
        except ValueError as error:
            if error.args[1] != 13:
                raise
    
    init_map = list(range(coms.n_qubits()))
    routed_coms = route(coms, arc, init_map)
    return coms2cirq(routed_coms, device)