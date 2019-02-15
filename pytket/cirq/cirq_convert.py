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

"""Methods to allow conversion between Cirq and t|ket> data types
"""

from typing import List, Generator, Iterator, Dict
import cirq
from cirq.google import XmonDevice
from cirq.devices import UnconstrainedDevice
from cirq import QubitId, LineQubit, GridQubit
from pytket import PI
from pytket._circuit import Circuit, Op, OpType
from pytket._routing import SquareGrid, Architecture
from .qubits import _indexed_qubits_from_circuit

cirq_common = cirq.ops.common_gates

# map cirq common gates to pytket gates
_cirq2ops_mapping = {
    cirq_common.CNOT : OpType.CX,
    cirq_common.H : OpType.H,
    cirq_common.MeasurementGate : OpType.Measure,
    cirq_common.XPowGate: OpType.Rx,
    cirq_common.YPowGate: OpType.Ry,
    cirq_common.ZPowGate: OpType.Rz,
    cirq_common.S: OpType.S,
    cirq_common.SWAP: OpType.SWAP,
    cirq_common.T : OpType.T,
    cirq_common.X : OpType.X,
    cirq_common.Y : OpType.Y,
    cirq_common.Z : OpType.Z,
    cirq_common.CZPowGate : OpType.CRz,
    cirq_common.CZ : OpType.CZ,
    cirq_common.ISwapPowGate : OpType.ISWAP
}
# reverse mapping for convenience
_ops2cirq_mapping = dict((reversed(item) for item in _cirq2ops_mapping.items()))
# spot special rotation gates
_special_rotations = (cirq_common.T, cirq_common.S, cirq_common.X, cirq_common.Y, cirq_common.Z)
_rotation_types = (cirq_common.XPowGate, cirq_common.YPowGate, cirq_common.ZPowGate, cirq_common.CZPowGate, cirq_common.ISwapPowGate)

def _grid_to_qubits(grid):
    lut = {}
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j][0]:
                lut[grid[i][j]] = j
    return lut

def get_grid_qubits(arc: SquareGrid, nodes: Iterator[int]) -> List[cirq.GridQubit]:
    """Gets a list of :py:class:GridQubit` s corresponding to the qubit nodes provided on the given Architecture.

       :param arc: The grid Architecture
       :param nodes: An iterator of node index values

       :return: The list of qubits
    """

    return [cirq.GridQubit(*arc.qind_to_squind(i)) for i in nodes]

def cirq_to_tk(circuit: cirq.Circuit) -> Circuit:
    """Converts a Cirq :py:class:`Circuit` to a :math:`\\mathrm{t|ket}\\rangle` :py:class:`Circuit` object.
    
       :param circuit: The input Cirq :py:class:`Circuit`

       :raises NotImplementedError: If the input contains a Cirq :py:class:`Circuit` operation which is not yet supported by pytket

       :return: The :math:`\\mathrm{t|ket}\\rangle` :py:class:`Circuit` corresponding to the input circuit
    """
    qubit_list = _indexed_qubits_from_circuit(circuit)
    qid_to_num = {q : i for i, q in enumerate(qubit_list)}
    n_qubits = len(circuit.all_qubits())
    tkcirc = Circuit(n_qubits)
    for moment in circuit:
        for op in moment.operations:
            gate = op.gate
            gatetype = type(gate)

            qb_lst = [qid_to_num[q] for q in op.qubits]

            n_qubits = len(op.qubits)

            if gatetype == cirq_common.HPowGate and gate.exponent == 1:
                gatetype = cirq_common.H
            elif gatetype == cirq_common.CNotPowGate and gate.exponent == 1:
                gatetype = cirq_common.CNOT

            try:
                optype = _cirq2ops_mapping[gatetype]
            except KeyError as error:
                raise NotImplementedError("Operation not supported by tket: " + str(op.gate)) from error
            if isinstance(gate, _rotation_types):
                o = tkcirc._get_op(optype,n_qubits,n_qubits,gate.exponent)
            elif isinstance(gate, cirq_common.MeasurementGate) :
                o = tkcirc._get_op(optype,n_qubits,n_qubits,gate.key)
            else:
                o = tkcirc._get_op(optype)
            tkcirc._add_operation(o,qb_lst)
    return tkcirc

def tk_to_cirq(tkcirc: Circuit, indexed_qubits: List[QubitId]) -> cirq.Circuit:
    """Converts a :math:`\\mathrm{t|ket}\\rangle` :py:class:`Circuit` object to a Cirq :py:class:`Circuit`.
    
    :param tkcirc: The input :math:`\\mathrm{t|ket}\\rangle` :py:class:`Circuit`
    :param indexed_qubits: Map from :math:`\\mathrm{t|ket}\\rangle` qubit indices to Cirq :py:class:`QubitId` s
    
    :return: The Cirq :py:class:`Circuit` corresponding to the input circuit
    """

    grid = tkcirc._int_routing_grid()
    qubits = _grid_to_qubits(grid)
    oplst = []
    slices = []
    for s in grid:
        news = set()
        for pair in s:
            if pair[0]>-1:
                news.add(pair[0])
        slices.append(news)
    for s in slices:
        for v in s:
            op = tkcirc._unsigned_to_op(v)
            optype = op.get_type()
            if optype == OpType.Input or optype == OpType.Output:
                continue
            try:
                gatetype = _ops2cirq_mapping[optype]
            except KeyError as error:
                raise NotImplementedError("Cannot convert tket Op to cirq gate: " + op.get_name()) from error
            n_qubits = op.get_n_inputs()
            qids = []
            for i in range(n_qubits):
                qbit = qubits[(v,i)]
                qids.append(indexed_qubits[qbit])
            params = op.get_params()
            if gatetype in _rotation_types:
                cirqop = gatetype(exponent=params[0])(*qids)
            elif gatetype == cirq_common.MeasurementGate:
                for q in qids:
                    cirqop = cirq_common.measure(q, key=op.get_desc())
            else:
                cirqop = gatetype(*qids)
            oplst.append(cirqop)

    return cirq.Circuit.from_ops(*oplst)
