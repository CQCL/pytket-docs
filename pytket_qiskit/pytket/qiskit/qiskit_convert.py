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


"""Methods to allow conversion between Qiskit and pytket circuit classes
"""

from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.circuit import Instruction, Measure
from qiskit.extensions.standard import *

from pytket._circuit import Circuit, Op, OpType
from pytket._routing import PhysicalCircuit

from sympy import pi

_known_qiskit_gate = {
    IdGate  : OpType.noop,
    XGate   : OpType.X,
    YGate   : OpType.Y,
    ZGate   : OpType.Z,
    SGate   : OpType.S,
    SdgGate : OpType.Sdg,
    TGate   : OpType.T,
    TdgGate : OpType.Tdg,
    HGate   : OpType.H,
    RXGate  : OpType.Rx,
    RYGate  : OpType.Ry,
    RZGate  : OpType.Rz,
    U1Gate  : OpType.U1,
    U2Gate  : OpType.U2,
    U3Gate  : OpType.U3,
    CnotGate    : OpType.CX,
    CyGate  : OpType.CY,
    CzGate  : OpType.CZ,
    CHGate  : OpType.CH,
    SwapGate : OpType.SWAP,
    ToffoliGate : OpType.CCX,
    FredkinGate : OpType.CSWAP,
    CrzGate : OpType.CRz,
    Cu1Gate : OpType.CU1,
    Cu3Gate : OpType.CU3,
    Measure : OpType.Measure
}

_known_qiskit_gate_rev = {v : k for k, v in _known_qiskit_gate.items()}

def qiskit_to_tk(qcirc: QuantumCircuit) -> Circuit :
    """Convert a :py:class:`qiskit.QuantumCircuit` to a :py:class:`Circuit`.
    
    :param qcirc: A circuit to be converted
    :type qcirc: QuantumCircuit
    :return: The converted circuit
    :rtype: Circuit
    """
    tkc = Circuit()
    qregmap = {}
    for reg in qcirc.qregs :
        tk_reg = tkc.add_q_register(reg.name, len(reg))
        qregmap.update({reg : tk_reg})
    cregmap = {}
    for reg in qcirc.cregs :
        tk_reg = tkc.add_c_register(reg.name, len(reg))
        cregmap.update({reg : tk_reg})
    for i, qargs, cargs in qcirc.data :
        if i.control is not None :
            raise NotImplementedError("Cannot convert conditional gates from Qiskit to tket")
        optype = _known_qiskit_gate[type(i)]
        qubits = [qregmap[r][ind] for r, ind in qargs]
        bits = [cregmap[r][ind] for r, ind in cargs]
        if optype == OpType.Measure :
            tkc.add_measure(*qubits, *bits)
            continue
        params = [p/pi for p in i.params]
        tkc.add_gate(optype, params, qubits, [])
    return tkc

def tk_to_qiskit(tkcirc: Circuit) -> QuantumCircuit :
    """Convert back
    
    :param tkcirc: A circuit to be converted
    :type tkcirc: Circuit
    :return: The converted circuit
    :rtype: QuantumCircuit
    """
    tkc = tkcirc
    if isinstance(tkcirc, PhysicalCircuit) :
        tkc = tkcirc._get_circuit()
    qcirc = QuantumCircuit()
    qregmap = {}
    for _, reg in tkc.q_regs.items() :
        if reg.size() == 0 :
            continue
        name = reg.name
        if len(name) == 0 :
            name = None
        qis_reg = QuantumRegister(reg.size(), name)
        qregmap.update({reg : qis_reg})
        qcirc.add_register(qis_reg)
    cregmap = {}
    for _, reg in tkc.c_regs.items() :
        if reg.size() == 0 :
            continue
        name = reg.name
        if len(name) == 0 :
            name = None
        qis_reg = ClassicalRegister(reg.size(), name)
        cregmap.update({reg : qis_reg})
        qcirc.add_register(qis_reg)
    tempregmap = {}
    for command in tkc :
        op = command.op
        qubits = command.qubits
        qargs = [qregmap[q.reg][q.index] for q in qubits]
        if len(command.controls) != 0 :
            raise NotImplementedError("Cannot convert conditional gates from tket to Qiskit")
        if op.get_type() == OpType.Measure :
            bits = [_convert_bit(b, cregmap, qcirc, tempregmap) for b in command.bits]
            qcirc.measure(*qargs, *bits)
            continue
        params = [p * pi for p in op.get_params()]
        try :
            gatetype = _known_qiskit_gate_rev[op.get_type()]
        except KeyError as error :
            raise NotImplementedError("Cannot convert tket Op to Qiskit gate: " + op.get_name()) from error
        g = gatetype(*params)
        qcirc.append(g, qargs=qargs)
    return qcirc

def _convert_bit(bit, cregmap, qcirc, tempregmap) :
    index = bit.index
    if bit.temp :
        if bit not in tempregmap :
            new_reg = ClassicalRegister(1, "temp"+str(index))
            qcirc.add_register(new_reg)
            tempregmap.update({bit : new_reg})
            return new_reg[0]
        return tempregmap[bit][0]
    return cregmap[bit.reg][index]