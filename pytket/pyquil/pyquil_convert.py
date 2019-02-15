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
from pytket import PI

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
                op = tkc._get_op(optype,len(i.qubits),len(i.qubits),params)
                tkc._add_operation(op, [q.index for q in i.qubits])
        elif isinstance(i, Measurement):
            if not i.classical_reg:
                raise NotImplementedError("Program has no defined classical register for measurement on qubit: ", i.qubits[0])
            reg = i.classical_reg
            if reg_name and reg_name != reg.name:
                raise NotImplementedError("Program has multiple classical registers: ", reg_name, reg.name)
            reg_name = reg.name
            op = tkc._get_op(OpType.Measure,1,1,str(reg.offset))
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

def _grid_to_qubits(grid):
    lut = {}
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j][0]:
                lut[grid[i][j]] = Qubit(j)
    return lut

def tk_to_pyquil(circ: Circuit) -> Program:
    """
       Convert a :math:`\\mathrm{t|ket}\\rangle` :py:class:`Circuit` to a :py:class:`pyquil.Program` .
    
    :param circ: A circuit to be converted

    :return: The converted circuit
    """
    p = Program()
    ro = p.declare('ro', 'BIT', circ.n_qubits())
    grid = circ._int_routing_grid()
    qubits = _grid_to_qubits(grid)
    slices = []
    for s in grid:
        news = set()
        for pair in s:
            if pair[0]>-1:
                news.add(pair[0])
        slices.append(news)
    for s in slices:
        for v in s:
            op = circ._unsigned_to_op(v)
            optype = op.get_type()
            if optype == OpType.Input or optype == OpType.Output:
                continue
            elif optype == OpType.Measure:
                p += Measurement(qubits[(v, 0)], ro[int(op.get_desc())])
                continue
            try:
                gatetype = _known_quil_gate_rev[optype]
            except KeyError as error:
                raise NotImplementedError("Cannot convert tket Op to pyquil gate: " + op.get_name()) from error
            params = [p*PI for p in op.get_params()]
            g = Gate(gatetype, params, [qubits[(v,port)] for port in range(op.get_n_inputs())])
            p += g
    return p
