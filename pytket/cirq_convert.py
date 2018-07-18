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
from cirq.google import XmonDevice
from cirq.devices import UnconstrainedDevice
from cirq import QubitId
from pytket import SquareGrid, Command, Gates, QCommands, Architecture
from pytket.qubits import sort_row_col

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
    cirq_common.Rot11Gate : Gates.CPhase,
}
# reverse mapping for convenience
coms2cirq_mapping = dict((reversed(item) for item in cirq2coms_mapping.items()))
# spot special rotation gates
special_rotations = (cirq_common.T, cirq_common.S, cirq_common.X, cirq_common.Y, cirq_common.Z)
rotation_types = (cirq_common.RotXGate, cirq_common.RotYGate, cirq_common.RotZGate, cirq_common.Rot11Gate)



def get_grid_qubits(arc: SquareGrid, nodes: Iterator[int]) -> List[cirq.GridQubit]:
    """Get a list of GridQubits corresponding to the qubit nodes provided on arc.
    
    Arguments:
        arc {SquareGrid} -- architecture
        nodes {Iterator[int]} -- iterator of node index values
    
    Returns:
        List[cirq.GridQubit]
    """

    return [cirq.GridQubit(*arc.qind_to_squind(i)) for i in nodes]


def cirq2coms(circuit: cirq.Circuit) -> QCommands:
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
            if op.gate == cirq_common.ISWAP:
                temp_list = list(op.gate.default_decompose(op.qubits))
                temp_circuit = cirq.Circuit.from_ops()
                for g in temp_list:
                    temp_circuit.append(g)
                qcdum = cirq2coms(temp_circuit)
                for c in qcdum:
                    qcoms.add_command(c)
                continue
            
            params = {}
            rot_typemap = {cirq_common.RotXGate: cirq_common.X, cirq_common.RotYGate: cirq_common.Y, cirq_common.RotZGate: cirq_common.Z}
            gate = op.gate
            gatetype = type(gate)
            if op.gate == cirq_common.CZ:
                c = Command(*(qb_lst+[Gates.CPhase]))
                c.set_parameter(PI)
                qcoms.add_command(c)
                continue
            
            if op.gate not in special_rotations and isinstance(op.gate, rotation_types):
                if op.gate.half_turns == 1:
                    if op.gate == cirq_common.Rot11Gate:
                        gate = gatetype
                        params["angle"] = op.gate.half_turns*PI
                    else:
                        gate = rot_typemap[gatetype]
                else:
                    gate = gatetype
                    params["angle"] = op.gate.half_turns*PI

            if isinstance(gate, cirq_common.MeasurementGate):
                gate = cirq_common.measure
            
            try:
                qb_lst = [q.index for q in op.qubits]
            except AttributeError as error: 
                raise AttributeError("Qubit must be of IndexedQubit type.") from error
            
            try:
                c = Command(*(qb_lst+[cirq2coms_mapping[gate]]))
            except KeyError as error:
                raise NotImplementedError("Operation not supported by sarisa: "+ str(op.gate)) from error
            
            if "angle" in params:
                c.set_parameter(params["angle"])
            
            qcoms.add_command(c)
    return qcoms

def coms2cirq(qcoms: QCommands, indexed_qubits: List[QubitId]) -> cirq.Circuit:
    """Convert QCommands object to cirq circuit.
    
    Arguments:
        qcoms {QCommands} -- Input QCommands
        arc {SquareGrid} -- architecture
    
    Returns:
        cirq.Circuit -- Circuit translated from QCommands. 
    """
    
    oplst = []
    for com in qcoms:
        qubits = [indexed_qubits[com.control]]
        if com.gate == Gates.CPhase:
            qubits.append(indexed_qubits[com.target])
            if(com.get_parameter() == PI):
                cirqop = cirq.CZ(*qubits)
            else:
                halfturns = com.get_parameter()/PI
                cirqop = cirq.Rot11Gate(half_turns=halfturns)(*qubits)
            oplst.append(cirqop)
            continue
        
        if com.is_two_qubit():
            qubits.append(indexed_qubits[com.target])

        cirqgate = coms2cirq_mapping[com.gate]
        if com.is_parametrized():
            halfturns = com.get_parameter()/PI
            cirqop = cirqgate(half_turns=halfturns)(*qubits)

        else:
            cirqop = cirqgate(*qubits)
        oplst.append(cirqop)

    circuit = cirq.Circuit.from_ops(*oplst)
    return circuit
