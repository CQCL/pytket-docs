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
from pytket import PI

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
    "CPHASE" : OpType.CRz,
    "PHASE" : OpType.Rz,
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
    reg_name = None
    qubits = prog.get_qubits()
    n_qubits = max(qubits) + 1
    tkc = Circuit(n_qubits)
    for i in prog.instructions:
        if isinstance(i, Gate):
            name = i.name
            try:
                optype = _known_quil_gate[name]
            except KeyError as error:
                raise NotImplementedError("Operation not supported by tket: " + str(i)) from error
            if len(i.params) == 0:
                tkc.add_operation(optype, [q.index for q in i.qubits])
            else:
                params = [p/PI for p in i.params]
                op = tkc._get_op(optype,params)
                tkc._add_operation(op, [q.index for q in i.qubits])
        elif isinstance(i, Measurement):
            if not i.classical_reg:
                raise NotImplementedError("Program has no defined classical register for measurement on qubit: ", i.qubits[0])
            reg = i.classical_reg
            if reg_name and reg_name != reg.name:
                raise NotImplementedError("Program has multiple classical registers: ", reg_name, reg.name)
            reg_name = reg.name
            op = tkc._get_op(OpType.Measure,str(reg.offset))
            tkc._add_operation(op, [i.qubit.index])
        elif isinstance(i, Declare):
            continue
        elif isinstance(i, Pragma):
            continue
        elif isinstance(i, Halt):
            return tkc
        else:
            raise NotImplementedError("Pyquil instruction is not a gate: " + str(i))
    return tkc

def tk_to_pyquil(circ: Union[Circuit,PhysicalCircuit]) -> Program:
    """
       Convert a :math:`\\mathrm{t|ket}\\rangle` :py:class:`Circuit` to a :py:class:`pyquil.Program` .
    
    :param circ: A circuit to be converted

    :return: The converted circuit
    """
    p = Program()
    ro = p.declare('ro', 'BIT', circ.n_qubits)
    for command in circ:
        op = command.op
        optype = op.get_type()
        if optype == OpType.Input or optype == OpType.Output:
            continue
        elif optype == OpType.Measure:
            reg = op.get_desc()
            if str.isnumeric(reg) :
                reg = int(reg)
            else :
                reg = command.qubits[0]
            p += Measurement(Qubit(command.qubits[0]), ro[reg])
            continue
        try:
            gatetype = _known_quil_gate_rev[optype]
        except KeyError as error:
            raise NotImplementedError("Cannot convert tket Op to pyquil gate: " + op.get_name()) from error
        params = []
        for par in op.get_params():
            try:
                params.append(par.evalf()*PI)
            except:
                params.append(par*PI)
        g = Gate(gatetype, params, [Qubit(q) for q in command.qubits])
        p += g
    return p
