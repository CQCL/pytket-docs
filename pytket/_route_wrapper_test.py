
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

from pytket.cirq_convert import SquareGrid, get_grid_qubits
from pytket._route_wrapper import route_circuit
import cirq

def test_route_circuit():
    arc = SquareGrid(3, 3)
    # circuit = get_circuit(arc)
    qubits = get_grid_qubits(arc, range(6))
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
    out_circuit = cirq.Circuit.from_ops(
        cirq.X(qubits[0]),
        cirq.X(qubits[1]),
        cirq.SWAP(qubits[0], qubits[1]),
        cirq.CNOT(qubits[1], qubits[4]),
        cirq.SWAP(qubits[1], qubits[2]),
        cirq.X(qubits[4]),
        cirq.CNOT(qubits[1], qubits[4]),
        cirq.CNOT(qubits[3], qubits[4]),
        cirq.X(qubits[4]),
        cirq.X(qubits[4]),
        cirq.SWAP(qubits[3], qubits[4]),
        cirq.CNOT(qubits[4], qubits[5])
    )
    print(circuit)
    print(out_circuit)
    assert str(route_circuit(circuit, arc)) == str(out_circuit)

if __name__ =='__main__':
    test_route_circuit()