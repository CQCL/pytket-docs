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

"""Wrapper module for routing interface. Provides functions for routing on XmonDevice and Architecture.
"""
from typing import Iterator, List

import cirq
from pytket._cpptket import qubit_lines, route, Architecture
from pytket.cirq_convert import cirq2coms, coms2cirq, get_grid_qubits
from pytket.qubits import IndexedQubit, sort_row_col, xmon2arc


def route_circuit_xmon(circuit: cirq.Circuit, device: cirq.google.XmonDevice, place=False) -> cirq.Circuit:
    """Route a cicuit on an XmonDevice, optionally remapping the qubits initially for fewer swaps. 
    
    Arguments:
        circuit {cirq.Circuit} -- Input circuit acting on Xmon/Grid qubits.
        device {cirq.google.XmonDevice} -- Device with adjacency constraints to be satisfied
    
    Keyword Arguments:
        place {bool} -- toggle qubit remapping before routing (default: {False})
    
    Raises:
        ValueError -- If placement fails, but is caught and ignored for now.
    
    Returns:
        cirq.Circuit -- Routed circuit
    """

    indexed_qubits = sort_row_col(device.qubits)

    def map_xmon_index(qb):
        return IndexedQubit(indexed_qubits.index(qb))

    newcirc = circuit.with_device(cirq.devices.UnconstrainedDevice, map_xmon_index)
    arc = xmon2arc(device)
    coms = cirq2coms(newcirc)
    if place:
        try:
            # get a list of lines of qubit indices
            indexlines = sorted(qubit_lines(coms, len(indexed_qubits)), key=len, reverse=True)
            # count the number of qubits that need to be placed contiguously 
            line_needed_length = sum(map(len, filter(lambda x: len(x)>1, indexlines)))
            # get a line on the device 
            placed_line = list(cirq.line_on_device(device, length=line_needed_length))

            if line_needed_length > len(placed_line):
                raise ValueError("Found line is not long enough to carry out placement, aborting", 13)
            unplaced_qubits = [qb for qb in indexed_qubits if qb not in placed_line]
            # qubit remapping dictionary 
            mapping = {}
            for line in indexlines:
                for qbindex in line:
                    if placed_line:
                        mapping[indexed_qubits[qbindex]] = placed_line.pop()
                    else:
                        mapping[indexed_qubits[qbindex]] = unplaced_qubits.pop()
            newcirc = circuit.with_device(cirq.devices.UnconstrainedDevice, lambda x: map_xmon_index(mapping[x]))
            coms = cirq2coms(newcirc)
            
        except ValueError as error:
            if error.args[1] != 13:
                raise
    
    init_map = list(range(coms.n_qubits()))
    routed_coms = route(coms, arc, init_map)
    return coms2cirq(routed_coms, indexed_qubits)

def route_circuit_arc(circuit: cirq.Circuit, arc: Architecture, qubits: List[cirq.QubitId]) -> cirq.Circuit:
    """Route circuit on arbitrary architecture.
    
    Arguments:
        circuit {cirq.Circuit} -- Input circuit, must act on IndexedQubit qubits
        arc {Architecture} -- arbitrary architecture
        qubits {List[cirq.QubitId]} -- qubits the cicuit acts on.
    
    Returns:
        cirq.Circuit -- Output circuit acting on same qubits as input
    """

    coms = cirq2coms(circuit)
    init_map = list(range(coms.n_qubits()))
    routed_coms = route(coms, arc, init_map)
    return coms2cirq(routed_coms, sorted(qubits, key=lambda x: x.index))
