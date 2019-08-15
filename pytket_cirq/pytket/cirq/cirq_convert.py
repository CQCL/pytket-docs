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

from typing import List, Generator, Iterator, Dict, Union
import cirq
from cirq.google import XmonDevice
from cirq.devices import UnconstrainedDevice
from cirq import Qid, LineQubit, GridQubit
from cirq.ops import NamedQubit
from pytket._circuit import Circuit, Op, OpType, Qubit
from pytket._routing import SquareGrid, Architecture, PhysicalCircuit
from .qubits import _indexed_qubits_from_circuit
from sympy import pi, Expr

cirq_common = cirq.ops.common_gates
cirq_pauli = cirq.ops.pauli_gates

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
    # cirq_pauli._PauliX : OpType.X,
    # cirq_pauli._PauliY : OpType.Y,
    # cirq_pauli._PauliZ : OpType.Z,
    cirq_pauli.X : OpType.X,
    cirq_pauli.Y : OpType.Y,
    cirq_pauli.Z : OpType.Z,
    cirq_common.CZPowGate : OpType.CRz,
    cirq_common.CZ : OpType.CZ,
    cirq_common.ISwapPowGate : OpType.ISWAP,
    cirq.ops.parity_gates.ZZPowGate : OpType.ZZPhase,
    cirq.ops.parity_gates.XXPowGate : OpType.XXPhase,
    cirq.ops.parity_gates.YYPowGate : OpType.YYPhase,
    cirq.ops.PhasedXPowGate : OpType.PhasedX
}
# reverse mapping for convenience
_ops2cirq_mapping = dict((reversed(item) for item in _cirq2ops_mapping.items()))
# _ops2cirq_mapping[OpType.X] = cirq_pauli.X
# _ops2cirq_mapping[OpType.Y] = cirq_pauli.Y
# _ops2cirq_mapping[OpType.Z] = cirq_pauli.Z
# spot special rotation gates
_constant_gates = (cirq_common.CNOT,
    cirq_common.H,
    cirq_common.S,
    cirq_common.SWAP,
    cirq_common.T,
    cirq_pauli.X,
    cirq_pauli.Y,
    cirq_pauli.Z,
    cirq_common.CZ)
_rotation_types = (cirq_common.XPowGate, cirq_common.YPowGate, cirq_common.ZPowGate, cirq_common.CZPowGate, cirq_common.ISwapPowGate, cirq.ops.parity_gates.ZZPowGate,cirq.ops.parity_gates.XXPowGate,cirq.ops.parity_gates.YYPowGate)

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
    n_qubits = len(circuit.all_qubits())
    tkcirc = Circuit(n_qubits)
    qreg = tkcirc.q_regs["q"]
    qmap = {q : qreg[i] for i, q in enumerate(qubit_list)}
    for moment in circuit:
        for op in moment.operations:
            gate = op.gate
            gatetype = type(gate)

            qb_lst = [qmap[q] for q in op.qubits]

            n_qubits = len(op.qubits)

            if gatetype == cirq_common.HPowGate and gate.exponent == 1:
                gate = cirq_common.H
            elif gatetype == cirq_common.CNotPowGate and gate.exponent == 1:
                gate = cirq_common.CNOT
            elif gatetype == cirq_pauli._PauliX and gate.exponent == 1:
                gate = cirq_pauli.X
            elif gatetype == cirq_pauli._PauliY and gate.exponent == 1:
                gate = cirq_pauli.Y
            elif gatetype == cirq_pauli._PauliZ and gate.exponent == 1:
                gate = cirq_pauli.Z

            if gate in _constant_gates:
                try:
                    optype = _cirq2ops_mapping[gate]
                except KeyError as error:
                    raise NotImplementedError("Operation not supported by tket: " + str(op.gate)) from error
                params = []
            elif isinstance(gate, cirq_common.MeasurementGate) :
                creg = tkcirc.add_c_register(gate.key, 1)
                tkcirc.add_measure(*qb_lst, creg[0])
                continue
            elif isinstance(gate, cirq.PhasedXPowGate) :
                optype = OpType.PhasedX
                pe = gate.phase_exponent
                e = gate.exponent
                params = [e, pe]
            else:
                try:
                    optype = _cirq2ops_mapping[gatetype]
                except KeyError as error:
                    raise NotImplementedError("Operation not supported by tket: " + str(op.gate)) from error
                params = [gate.exponent]
            tkcirc.add_gate(optype, params, qb_lst, [])
    return tkcirc

def tk_to_cirq(tkcirc: Union[Circuit,PhysicalCircuit], indexed_qubits: List[Qid] = None) -> cirq.Circuit:
    """Converts a :math:`\\mathrm{t|ket}\\rangle` :py:class:`Circuit` object to a Cirq :py:class:`Circuit`.
    
    :param tkcirc: The input :math:`\\mathrm{t|ket}\\rangle` :py:class:`Circuit`
    
    :return: The Cirq :py:class:`Circuit` corresponding to the input circuit
    """

    oplst = []
    for command in tkcirc:
        op = command.op
        optype = op.get_type()
        try:
            gatetype = _ops2cirq_mapping[optype]
        except KeyError as error:
            raise NotImplementedError("Cannot convert tket Op to Cirq gate: " + op.get_name()) from error
        if len(command.controls) != 0 :
            raise NotImplementedError("Cannot convert conditional gate to Cirq")
        qids = [_convert_qubit(qbit, indexed_qubits) for qbit in command.qubits]
        if optype == OpType.Measure:
            bit = command.bits[0]
            cirqop = cirq_common.measure(qids[0],key=bit.reg.name)
        else:
            params = op.get_params()
            if len(params)==0 :
                cirqop = gatetype(*qids)
            elif optype == OpType.PhasedX :
                cirqop = gatetype(phase_exponent=params[1],exponent=params[0])(*qids)
            else:
                cirqop = gatetype(exponent=params[0])(*qids)
        oplst.append(cirqop)

    return cirq.Circuit.from_ops(*oplst)

def _convert_qubit(qb: Qubit, indexed_qubits: List[Qid]) -> cirq.Qid :
    if qb.reg.name == "q" :
        if indexed_qubits :
            return indexed_qubits[qb.index]
        return LineQubit(qb.index)
    else :
        return NamedQubit(qb.__repr__())