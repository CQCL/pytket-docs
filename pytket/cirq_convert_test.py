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

from pytket.cirq_convert import SquareGrid, cirq2coms, coms2cirq, get_grid_qubits
from pytket import route, initial_placement, route_circuit
import cirq
import pytest
import numpy as np

def get_circuit(arc):
    row_col = []
    qubits = get_grid_qubits(arc, range(9))
    circ = cirq.Circuit.from_ops(
        cirq.H(qubits[0]),
        cirq.X(qubits[1]),
        cirq.Y(qubits[2]),
        cirq.Z(qubits[3]),
        cirq.T(qubits[3]),
        cirq.S(qubits[4]),
        cirq.CNOT(qubits[1], qubits[4]),
        # cirq.SWAP(qubits[1], qubits[6]),
        cirq.CNOT(qubits[6], qubits[8]),
        cirq.RotXGate(half_turns=0.1)(qubits[5]),
        cirq.RotYGate(half_turns=0.1)(qubits[6]),
        cirq.RotZGate(half_turns=0.1)(qubits[7]),
        cirq.measure_each(*qubits[3:-2])
    )
    return circ


def get_demo_circuit(arc):
    qubits = get_grid_qubits(arc, range(6))
    circ = cirq.Circuit.from_ops(
        cirq.H(qubits[0]),
        cirq.X(qubits[1]),
        cirq.CNOT(qubits[0], qubits[4]),
        cirq.Y(qubits[4]),
        cirq.CNOT(qubits[2], qubits[4]),
        cirq.CNOT(qubits[3], qubits[4]),
        cirq.Y(qubits[4]),
        cirq.CNOT(qubits[3], qubits[5]),
        cirq.Z(qubits[4])
    )
    return circ

def deterministic_circuit(arc):
    qubits = get_grid_qubits(arc, range(6))
    circ = cirq.Circuit.from_ops(
        cirq.X(qubits[0]),
        cirq.X(qubits[1]),
        cirq.CNOT(qubits[0], qubits[4]),
        cirq.X(qubits[4]),
        cirq.CNOT(qubits[2], qubits[4]),
        cirq.CNOT(qubits[3], qubits[4]),
        cirq.X(qubits[4]),
        cirq.CNOT(qubits[3], qubits[5]),
        cirq.X(qubits[4]),
        cirq.measure_each(*qubits)

    )
    return circ

def test_get_grid_qubits():
    arc = SquareGrid(4, 4)
    qbs = get_grid_qubits(arc, [0, 8, 7, 15])
    expected = [cirq.GridQubit(0, 0), cirq.GridQubit(2, 0), cirq.GridQubit(1, 3), cirq.GridQubit(3, 3)]

    assert qbs == expected

def test_conversions():
    
    arc = SquareGrid(3, 3)
    
    circ = get_circuit(arc)
    coms = cirq2coms(circ, arc)
    assert str(circ) == str(coms2cirq(coms, arc))

if __name__ =='__main__':
    test_conversions()
