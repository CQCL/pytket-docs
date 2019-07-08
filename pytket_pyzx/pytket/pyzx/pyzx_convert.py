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

"""Methods to allow conversion between pyzx and t|ket> data types
"""

try:
    import pyzx as zx
    from pyzx.circuit import Circuit as pyzxCircuit
except ImportError:
    raise ImportError("Could not find PyZX. You must install PyZX from https://github.com/Quantomatic/pyzx")

from pytket import PI
from pytket._circuit import OpType, Op, Circuit
from pytket._routing import PhysicalCircuit

from typing import Union

_tk_to_pyzx_gates = {OpType.Rz: "ZPhase",
                    OpType.Rx: "XPhase",
                    OpType.X: "NOT",
                    OpType.Z: "Z",
                    OpType.S: "S",
                    OpType.T: "T",
                    OpType.CX: "CNOT",
                    OpType.CZ: "CZ",
                    OpType.H: "HAD",
                    OpType.SWAP: "SWAP",
                    }

_pyzx_to_tk_gates = dict((reversed(item) for item in _tk_to_pyzx_gates.items()))

_parameterised_gates = {OpType.Rz, OpType.Rx}

def tk_to_pyzx(tkcircuit:Union[Circuit,PhysicalCircuit]) -> pyzxCircuit:
    """
    Convert a :math:`\\mathrm{t|ket}\\rangle` :py:class:`Circuit` to a :py:class:`pyzx.Circuit`.
    
    :param prog: A circuit to be converted

    :return: The converted circuit
    """
    c = pyzxCircuit(tkcircuit.n_qubits)
    for command in tkcircuit:
        op = command.op
        if not op.get_type() in _tk_to_pyzx_gates:
            raise Exception("Cannot parse tket gate: " + str(op))
        gate_string = _tk_to_pyzx_gates[op.get_type()]
        qbs = command.qubits
        n_params = len(op.get_params())
        if (n_params==0):
            c.add_gate(gate_string, *qbs)
        elif (n_params==1):
            try:
                c.add_gate(gate_string, *qbs, phase=op.get_params()[0].evalf())
            except:
                c.add_gate(gate_string, *qbs, phase=op.get_params()[0])
        else :
            raise Exception("Cannot parse gate with " + str(n_params) + " parameters")
    return c

def pyzx_to_tk(pyzx_circ:pyzxCircuit) -> Circuit:
    """
    Convert a :py:class:`pyzx.Circuit` to a :math:`\\mathrm{t|ket}\\rangle` :py:class:`Circuit` .
    All PyZX basic gate operations are currently supported by pytket. Run `pyzx_circuit_name.to_basic_gates()`
    before conversion.
    
    :param prog: A circuit to be converted

    :return: The converted circuit
    """
    c = Circuit(pyzx_circ.qubits)
    for g in pyzx_circ.gates:
        if not g.name in _pyzx_to_tk_gates:
            raise Exception("Cannot parse PyZX gate of type " + g.name + "into tket Circuit")
        op_type = _pyzx_to_tk_gates[g.name]
        if (hasattr(g,'control')):
            num_qubits = 2
            qbs = [getattr(g,'control'),getattr(g,'target')]
        else: 
            num_qubits = 1
            qbs = [getattr(g,'target')]

        if (hasattr(g,"printphase") and op_type in _parameterised_gates):
            op = c._get_op(OpType=op_type,param=float(g.phase))
        else:
            op = c._get_op(OpType=op_type,parameters=[])

        c._add_operation(Op=op,qubits=qbs)
    return c