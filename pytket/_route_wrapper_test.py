
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

from pytket.cirq_convert import SquareGrid, get_grid_qubits,cirq2coms
from pytket._route_wrapper import route_circuit_xmon, route_circuit_arc
from pytket import Gates, QCommands, Architecture
from pytket._cpptket import check_routing_solution, qubit_lines, route
from pytket.qubits import IndexedQubit, sort_row_col, xmon2arc

import cirq
from cirq.google import Bristlecone, Foxtail

def test_route_xmon_circuit():
    device = Bristlecone
    qubits = list(device.qubits)
    circuit = cirq.Circuit.from_ops(
        cirq.X(qubits[0]),
        cirq.X(qubits[1]),
        cirq.CNOT(qubits[0], qubits[4]),
        cirq.X(qubits[4]),
        cirq.CNOT(qubits[2], qubits[4]),
        cirq.CNOT(qubits[3], qubits[4]),
        cirq.X(qubits[4]),
        cirq.CNOT(qubits[3], qubits[5]),
        cirq.X(qubits[4])
    )
    routed_circuit = route_circuit_xmon(circuit,device)
    assert check_routing_solution(cirq2coms(circuit),cirq2coms(routed_circuit),xmon2arc(device),list(range(len(qubits)))) == True

def test_route_xmon_circuit_place():
    device = Bristlecone
    qubits = list(device.qubits)
    circuit = cirq.Circuit.from_ops(
        cirq.X(qubits[0]),
        cirq.X(qubits[1]),
        cirq.CNOT(qubits[0], qubits[4]),
        cirq.X(qubits[4]),
        cirq.CNOT(qubits[2], qubits[4]),
        cirq.CNOT(qubits[3], qubits[4]),
        cirq.X(qubits[4]),
        cirq.CNOT(qubits[3], qubits[5]),
        cirq.X(qubits[4])
    )

    indexed_qubits = sort_row_col(device.qubits)
    def map_xmon_index(qb):
        return IndexedQubit(indexed_qubits.index(qb))
    
    # tests functionality of place method in route_circuit_xmon
    # get a list of lines of qubit indices
    coms = cirq2coms(circuit)
    indexlines = sorted(qubit_lines(coms, len(indexed_qubits)), key=len, reverse=True)
    line_needed_length = sum(map(len, filter(lambda x: len(x)>1, indexlines)))
    placed_line = list(cirq.line_on_device(device, length=line_needed_length))
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
    
    init_map = list(range(len(qubits)))
    arc = xmon2arc(device)
    routed_coms = route(coms, arc, init_map)
    assert check_routing_solution(coms,routed_coms,arc,init_map) == True


def test_route_circuit_arc():
    number_nodes = 5
    custom_arch = Architecture([(0, 1), (0, 2), (0, 3), (1, 4), (2, 4), (3, 4)], number_nodes)
    qubits = [IndexedQubit(i) for i in range(number_nodes)]
    circuit = cirq.Circuit.from_ops(
        cirq.X(qubits[0]),
        cirq.X(qubits[1]),
        cirq.CNOT(qubits[0], qubits[4]),
        cirq.X(qubits[4]),
        cirq.CNOT(qubits[2], qubits[4]),
        cirq.CNOT(qubits[3], qubits[4]),
        cirq.CNOT(qubits[2], qubits[1]),
        cirq.X(qubits[4]),
        cirq.CNOT(qubits[3], qubits[1]),
        cirq.CNOT(qubits[2], qubits[3]),
        cirq.X(qubits[4])
    )
    routed_circuit = route_circuit_arc(circuit,custom_arch,qubits)
    assert check_routing_solution(cirq2coms(circuit),cirq2coms(routed_circuit),custom_arch,list(range(len(qubits)))) == True



# if __name__ =='__main__':
    # test_route_xmon_circuit(Bristlecone)
    # test_route_xmon_circuit(Foxtail)
    # test_route_xmon_circuit_place(Bristlecone)
    # test_route_xmon_circuit_place(Foxtail)
    # test_route_circuit_arc()