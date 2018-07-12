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

"""Methods to allow conversion between Cirq and t|ket> data types (circuit <-> QCommands)
"""

from typing import List, Generator, Iterator
import cirq
from pytket import SquareGrid, Command, Gates, QCommands


cirq_common = cirq.ops.common_gates
PI = 3.14159265359

# map cirq common gates to pytket gates
cirq2coms_mapping = {
    cirq_common.CNOT : Gates.CX,
    cirq_common.H : Gates.H,
    cirq_common.measure : Gates.measure,
    cirq_common.RotXGate: Gates.Rx,
    cirq_common.RotYGate: Gates.Ry,
    cirq_common.RotZGate: Gates.Rz,
    cirq_common.S: Gates.S,
    cirq_common.SWAP: Gates.Swap,
    cirq_common.T : Gates.T,
    cirq_common.X : Gates.X,
    cirq_common.Y : Gates.Y,
    cirq_common.Z : Gates.Z,
}

# reverse mapping for convenience
coms2cirq_mapping = dict((reversed(item) for item in cirq2coms_mapping.items()))
# spot special rotation gates
special_rotations = (cirq_common.T, cirq_common.S, cirq_common.X, cirq_common.Y, cirq_common.Z)
rotation_types = (cirq_common.RotXGate, cirq_common.RotYGate, cirq_common.RotZGate)


def get_grid_qubits(arc: SquareGrid, nodes: Iterator[int]) -> List[cirq.GridQubit]:
    """Get a list of GridQubits corresponding to the qubit nodes provided on arc.
    
    Arguments:
        arc {SquareGrid} -- architecture
        nodes {Iterator[int]} -- iterator of node index values
    
    Returns:
        List[cirq.GridQubit]
    """

    return [cirq.GridQubit(*arc.qind_to_squind(i)) for i in nodes]



def cirq2coms(circuit: cirq.Circuit, arc: SquareGrid) -> QCommands:
    """Convert cirq circuit to QCommands object
    
    Arguments:
        circuit {cirq.Circuit} -- input circuit
        arc {SquareGrid} -- architecture, for converting from grid values to node indices
    
    Raises:
        NotImplementedError -- If a cirq circuit operation is not yet supported by pytket
    
    Returns:
        QCommands -- Output list of commands
    """

    qcoms = QCommands()
    for moment in circuit:
        for op in moment.operations:
            params = {}
            rot_typemap = {cirq_common.RotXGate: cirq_common.X, cirq_common.RotYGate: cirq_common.Y, cirq_common.RotZGate: cirq_common.Z}
            gate = op.gate
            gatetype = type(gate)
            if op.gate not in special_rotations and isinstance(op.gate, rotation_types):
                if op.gate.half_turns == 1:
                    gate = rot_typemap[gatetype]
                else:
                    gate = gatetype
                    params["angle"] = op.gate.half_turns*PI

            if isinstance(gate, cirq_common.MeasurementGate):
                gate = cirq_common.measure
            
            qb_lst = (arc.squind_to_qind(q.row, q.col, 0) for q in op.qubits)
            
            try:
                c = Command(*qb_lst, cirq2coms_mapping[gate])
            except KeyError:
                raise NotImplementedError("Operation not supported by sarisa: "+ str(op.gate))
            
            if "angle" in params:
                c.set_parameter(params["angle"])
            
            qcoms.add_command(c)
    return qcoms

def coms2cirq(qcoms: QCommands, arc: SquareGrid) -> cirq.Circuit:
    """Convert QCommands object to cirq circuit.
    
    Arguments:
        qcoms {QCommands} -- Input QCommands
        arc {SquareGrid} -- architecture
    
    Returns:
        cirq.Circuit -- Circuit translated from QCommands. 
    """

    oplst = []
    qubit_map = {}
    for com in qcoms:
        qindices = [arc.qind_to_squind(com.control)]
        if com.is_two_qubit():
            qindices.append(arc.qind_to_squind(com.target))
        for qbs in qindices:
            if qbs not in qubit_map:
                qubit_map[qbs] = cirq.GridQubit(qbs[0], qbs[1])

        cirqgate = coms2cirq_mapping[com.gate]
        if com.is_parametrized():
            halfturns = com.get_parameter()/PI
            cirqop = cirqgate(half_turns=halfturns)(*[qubit_map[ind] for ind in qindices])

        else:
            cirqop = cirqgate(*[qubit_map[ind] for ind in qindices])
        oplst.append(cirqop)

    circuit = cirq.Circuit.from_ops(*oplst)
    return circuit

