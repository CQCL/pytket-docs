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

"""Methods to allow conversion between pyquil and t|ket> data types
"""

from pyquil import Program
from pyquil.quilbase import Gate, Measurement, Declare, Pragma, Halt
from pyquil.quilatom import Qubit
from pyquil.device import AbstractDevice, ISA, isa_to_graph, specs_from_graph
from collections import namedtuple

from pytket._circuit import Circuit, Op, OpType
from pytket._routing import PhysicalCircuit

from sympy import pi

from typing import Union

_known_quil_gate = {
    "X" : OpType.X,
    "Y" : OpType.Y,
    "Z" : OpType.Z,
    "H" : OpType.H,
    "S" : OpType.S,
    "T" : OpType.T,
    "RX" : OpType.Rx,
    "RY" : OpType.Ry,
    "RZ" : OpType.Rz,
    "CZ" : OpType.CZ,
    "CNOT" : OpType.CX,
    "CCNOT" : OpType.CCX,
    "CPHASE" : OpType.CU1,
    "PHASE" : OpType.U1,
    "SWAP" : OpType.SWAP
}

_known_quil_gate_rev = {v : k for k, v in _known_quil_gate.items() }

def pyquil_to_tk(prog: Program) -> Circuit:
    """
    Convert a :py:class:`pyquil.Program` to a :math:`\\mathrm{t|ket}\\rangle` :py:class:`Circuit` .
    Note that not all pyQuil operations are currently supported by pytket.
    
    :param prog: A circuit to be converted

    :return: The converted circuit
    """
    qubits = prog.get_qubits()
    n_qubits = max(qubits) + 1
    tkc = Circuit(n_qubits)
    qreg = tkc.q_regs["q"]
    cregmap = {}
    for i in prog.instructions:
        if isinstance(i, Gate):
            try:
                optype = _known_quil_gate[i.name]
            except KeyError as error:
                raise NotImplementedError("Operation not supported by tket: " + str(i)) from error
            qubits = [qreg[q.index] for q in i.qubits]
            params = [p/pi for p in i.params]
            tkc.add_gate(optype, params, qubits, [])
        elif isinstance(i, Measurement):
            qubit = qreg[i.qubit.index]
            reg = cregmap[i.classical_reg.name]
            bit = reg[i.classical_reg.offset]
            tkc.add_measure(qubit, bit)
        elif isinstance(i, Declare):
            if i.memory_type is not 'BIT' :
                raise NotImplementedError("Cannot handle memory of type " + i.memory_type)
            new_reg = tkc.add_c_register(i.name, i.memory_size)
            cregmap.update({i.name : new_reg})
        elif isinstance(i, Pragma):
            continue
        elif isinstance(i, Halt):
            return tkc
        else:
            raise NotImplementedError("Pyquil instruction is not a gate: " + str(i))
    return tkc

def tk_to_pyquil(tkcirc: Union[Circuit,PhysicalCircuit], active_reset:bool=False) -> Program:
    """
       Convert a :math:`\\mathrm{t|ket}\\rangle` :py:class:`Circuit` to a :py:class:`pyquil.Program` .
    
    :param tkcirc: A circuit to be converted

    :return: The converted circuit
    """
    circ = tkcirc
    if isinstance(tkcirc, PhysicalCircuit) :
        circ = tkcirc._get_circuit()
    p = Program()
    if len(circ.q_regs) != 1 :
        raise NotImplementedError("Cannot convert circuit with multiple quantum registers to PyQuil")
    cregmap = {}
    for _, reg in circ.c_regs.items() :
        if reg.size() == 0 :
            continue
        name = reg.name
        if name == 'c' :
            name = 'ro'
        quil_reg = p.declare(name, 'BIT', reg.size())
        cregmap.update({reg : quil_reg})
    if active_reset :
        p.reset()
    for command in circ:
        op = command.op
        qubits = [Qubit(qb.index) for qb in command.qubits]
        optype = op.get_type()
        if optype == OpType.Measure :
            bits = [cregmap[b.reg][b.index] for b in command.bits]
            p += Measurement(*qubits, *bits)
            continue
        try:
            gatetype = _known_quil_gate_rev[optype]
        except KeyError as error:
            raise NotImplementedError("Cannot convert tket Op to pyquil gate: " + op.get_name()) from error
        if len(command.controls) != 0 :
            raise NotImplementedError("Cannot convert conditional gates from tket to PyQuil")
        params = [float((p * pi).evalf()) for p in op.get_params()]
        g = Gate(gatetype, params, qubits)
        p += g
    return p
