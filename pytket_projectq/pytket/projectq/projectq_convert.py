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

"""Methods to allow conversion between ProjectQ and t|ket> data types
"""

import projectq
from projectq import ops as pqo
from projectq.cengines import BasicEngine, LastEngineException
from projectq import MainEngine
from projectq.meta import get_control_count
from projectq.ops._command import Command as ProjectQCommand, apply_command
from projectq.types._qubit import Qureg

from pytket import PI
from pytket._circuit import OpType, Op, Circuit, Command
from pytket._routing import PhysicalCircuit
from pytket._transform import Transform

from typing import Union

_pq_to_tk_singleqs = {pqo.XGate: OpType.X,
                    pqo.YGate: OpType.Y,
                    pqo.ZGate: OpType.Z,
                    pqo.Rx: OpType.Rx,
                    pqo.Ry: OpType.Ry,
                    pqo.Rz: OpType.Rz,
                    pqo.HGate: OpType.H,
                    pqo.SGate: OpType.S,
                    pqo.TGate: OpType.T,
                    pqo.SqrtXGate: OpType.V,
                    pqo.MeasureGate: OpType.Measure
                    }

# python can't hash projectq controlled gates...
_pq_to_tk_multiqs = {pqo.XGate: OpType.CX,
                    pqo.ZGate: OpType.CZ,
                    pqo.Rz: OpType.CRz
                    }

# other gates will be added here which are neither controlled operations nor valid tket Ops
# these gates are currently either ignored (Barrier) or used to determine flushing of tketOptimiser (FlushGate)
_OTHER_KNOWN_GATES = {pqo.Allocate: OpType.noop,
                    pqo.Deallocate: OpType.noop,
                    pqo.Barrier: OpType.Box,
                    pqo.FlushGate: OpType.noop,
                    pqo.SwapGate: OpType.SWAP
                    }
    

_ALLOWED_GATES = {**_pq_to_tk_singleqs,**_pq_to_tk_multiqs,**_OTHER_KNOWN_GATES}

_tk_to_pq_singleqs = dict((reversed(item) for item in _pq_to_tk_singleqs.items()))
_tk_to_pq_multiqs = dict((reversed(item) for item in _pq_to_tk_multiqs.items()))

def get_pq_command_from_tk_command(command:Command, engine:MainEngine, container):
        op = command.op
        optype = op.get_type()
        controlled = False
        if optype in _tk_to_pq_singleqs:
            gatetype = _tk_to_pq_singleqs[optype]
        elif optype in _tk_to_pq_multiqs:
            gatetype = _tk_to_pq_multiqs[optype]
            controlled = True
        else:
            raise Exception("Cannot convert op " + str(command) + " to projectq")
        
            # params = op.get_params()
        if issubclass(gatetype,pqo.BasicRotationGate):
            params = op.get_params()
            if len(params)!=1:
                raise Exception("A Rotation Gate has " + len(params) + " parameters")
            try:
                gate = gatetype(params[0].evalf()*PI)
            except:
                gate = gatetype(params[0]*PI)
        elif issubclass(gatetype,pqo.BasicGate):
            gate = gatetype()
        else:
            raise Exception("Gate of type: " + str(gatetype) + " cannot be converted")
        qubs = command.qubits
        if controlled:
            target = container[qubs[-1]]
            qubs.pop()
            controls = (container[i] for i in qubs)
            qubits = gate.make_tuple_of_qureg(target)
            cmd = ProjectQCommand(engine,gate,qubits,controls)
        else:
            qubits = gate.make_tuple_of_qureg(container[i] for i in qubs)
            cmd = ProjectQCommand(engine,gate,qubits)

        return cmd

def tk_to_projectq(engine:MainEngine,qureg:Qureg,circuit:Union[Circuit,PhysicalCircuit]) -> None :
    """Given a ProjectQ Qureg in an Engine, converts a Circuit to a series of ProjectQ Commands on this Qureg.
    
    :param engine: A ProjectQ MainEngine
    :type engine: MainEngine
    :param qureg: A ProjectQ Qureg in this MainEngine
    :type qureg: Qureg
    :param circuit: A tket Circuit
    :type circuit: Union[Circuit,PhysicalCircuit]
    """
    for command in circuit:
        cmd = get_pq_command_from_tk_command(command,engine,qureg)
        apply_command(cmd)


def _handle_gate(command:ProjectQCommand, engine): #must also be a tket Engine
    if command.gate in _OTHER_KNOWN_GATES or type(command.gate) in _OTHER_KNOWN_GATES:
        return
    elif (type(command.gate) in _pq_to_tk_multiqs and len(command.control_qubits)>0 and len(command.qubits)>0):
        engine._translate_multi_qubit_op(command)
    elif (type(command.gate) in _pq_to_tk_singleqs and len(command.control_qubits)==0 and len(command.qubits)==1):
        engine._translate_single_qubit_op(command)
    elif (type(command.gate) == pqo.DaggeredGate):
        engine._translate_daggered_op(command)
    else:
        raise Exception("uncaught option " + str(command.gate) + " controls = " + str(len(command.control_qubits)) + " targets = " + str(len(command.qubits)))

def _add_daggered_op_to_circuit(cmd:ProjectQCommand, circ:Circuit):
    undaggered_gate = cmd.gate.get_inverse()
    if (type(undaggered_gate) == pqo.TGate):
        op = circ._get_op(OpType=OpType.Tdg)
    elif (type(undaggered_gate) == pqo.SGate):
        op = circ._get_op(OpType=OpType.Sdg)
    else:
        raise Exception("cannot recognise daggered op of type " + str(cmd.gate))
    qubit_no = cmd.qubits[0][0].id
    assert len(cmd.qubits)==1
    assert len(cmd.qubits[0])==1
    new_qubit = False
    if (qubit_no >= circ.n_qubits):
        circ.add_blank_wires(1+qubit_no-circ.n_qubits)
        new_qubit = True
    circ._add_operation(Op=op,qubits=[qubit_no])
    return new_qubit

def _add_single_qubit_op_to_circuit(cmd:ProjectQCommand,circ:Circuit):
    assert len(cmd.qubits)==1
    assert len(cmd.qubits[0])==1
    qubit_no = cmd.qubits[0][0].id
    new_qubit = False
    if get_control_count(cmd) > 0:
        raise Exception("singleq gate " + str(cmd.gate) + " has " + str(get_control_count(cmd)) + " control qubits")
    else:
        if type(cmd.gate) in (pqo.Rx,pqo.Ry,pqo.Rz):
            op = circ._get_op(OpType=_pq_to_tk_singleqs[type(cmd.gate)],param=cmd.gate.angle/PI)
        else:
            op = circ._get_op(OpType=_pq_to_tk_singleqs[type(cmd.gate)])
        if (qubit_no >= circ.n_qubits):
            circ.add_blank_wires(1+qubit_no-circ.n_qubits)
            new_qubit = True
        circ._add_operation(Op=op,qubits=[qubit_no])
    return new_qubit

def _add_multi_qubit_op_to_circuit(cmd:ProjectQCommand,circ:Circuit):
    assert len(cmd.qubits) >0
    qubs = [qb for qr in cmd.all_qubits for qb in qr]
    if get_control_count(cmd) < 1:
        raise Exception("multiq gate " + str(cmd.gate) + " has no controls")
    else:
        new_qubits = []
        for q in qubs:
            qubit_no = q.id
            if (qubit_no>=circ.n_qubits):
                circ.add_blank_wires(1+qubit_no-circ.n_qubits)
                new_qubits.append(q)
        n_qubits = len(cmd.all_qubits)
        if (type(cmd.gate) == pqo.CRz):
            op = circ._get_op(OpType=_pq_to_tk_multiqs[type(cmd.gate)],param=cmd.gate.angle/PI)
        else:
            op = circ._get_op(OpType=_pq_to_tk_multiqs[type(cmd.gate)])
        qubit_nos = [qb.id for qr in cmd.all_qubits for qb in qr]
        circ._add_operation(Op = op, qubits=qubit_nos)
        return new_qubits

class tketBackendEngine(BasicEngine):
    """
    A projectq backend designed to translate from projectq commands
    to tket Circuits
    """

    def __init__(self):
        """
        Initialize the tketBackendEngine.

        Initializes local Circuit to an empty Circuit.
        """
        BasicEngine.__init__(self)
        self._circuit = Circuit()

    @property
    def circuit(self):
        """
        Returns:
            The :math:`\\mathrm{t|ket}\\rangle` Circuit from the engine.
        
        Raises:
            Exception:
            If the Circuit has no gates, assumes user forgot to flush engines.
        """
        if self._circuit.n_gates==0:
            raise Exception("Circuit has no gates. Have you flushed your engine?")
        return self._circuit
    
    def is_available(self,cmd):
        """
        Ask the next engine whether a command is available, i.e.,
        whether it can be executed by the next engine(s).

        Args:
            cmd (Command): Command for which to check availability.

        Returns:
            True if the command can be executed.

        Raises:
            LastEngineException: 
            If is_last_engine is True but is_available is not implemented.
        """
        try:
            return BasicEngine.is_available(self, cmd)
        except LastEngineException:
            return True

    def receive(self, command_list):
        """ Process commands from a list and append to local Circuit. 
        """
        for cmd in command_list:
            _handle_gate(cmd,self)

    def _translate_daggered_op(self,cmd):
        #assume it is a single qubit op
        _add_daggered_op_to_circuit(cmd,self._circuit)

    def _translate_single_qubit_op(self,cmd):
        _add_single_qubit_op_to_circuit(cmd,self._circuit)

    def _translate_multi_qubit_op(self,cmd):
        _add_multi_qubit_op_to_circuit(cmd,self._circuit)


class tketOptimiser(BasicEngine):
    """
    A ProjectQ BasicEngine designed to translate from ProjectQ commands
    to tket Circuits, optimise them, and then return other ProjectQ commands.
    """
    def __init__(self):
        BasicEngine.__init__(self)
        self._circuit = Circuit()
        self._qubit_dictionary = dict()

    def receive(self, command_list):
        """
        Receives a list of commands and appends to local Circuit. If a flush gate is received, 
        optimises the Circuit using a default Transform pass and then sends the commands from
        this optimised Circuit into the next engine.
        """
        for cmd in command_list:
            if cmd.gate == pqo.FlushGate(): #flush gate --> optimize and then flush
                cmd_list = self._optimise()
                cmd_list.append(cmd)
                self._circuit = Circuit()
                self._qubit_dictionary = dict()
                self.send(cmd_list)
                continue

            _handle_gate(cmd,self)

    def _optimise(self): #takes the circuit and optimises it before regurgitating it as a series of ProjectQ commands
        if self._circuit.n_qubits!=0:
            Transform.OptimisePhaseGadgets().apply(self._circuit)
            Transform.RebaseToProjectQ().apply(self._circuit)

        cmd_list = []

        for i in range(self._circuit.n_qubits):
            gate = pqo.Allocate
            cmd = ProjectQCommand(self.main_engine,gate,gate.make_tuple_of_qureg(self._qubit_dictionary[i]))
            cmd_list.append(cmd)

        if self._circuit.n_gates==0:
            return cmd_list
        for command in self._circuit:
            cmd = get_pq_command_from_tk_command(command,self.main_engine,self._qubit_dictionary)
            cmd_list.append(cmd)
        return cmd_list

    def _translate_daggered_op(self,cmd:ProjectQCommand):
        #assume it is a single qubit op, as the only daggered ops which are of the 
        # ProjectQ DaggeredGate class are single qubit
        new_qubit = _add_daggered_op_to_circuit(cmd,self._circuit)
        # if this qubit hasn't been seen before by the circuit, add to dictionary
        if new_qubit:
            self._qubit_dictionary[cmd.qubits[0][0].id] = cmd.qubits[0][0]

    def _translate_single_qubit_op(self,cmd:ProjectQCommand):
        new_qubit = _add_single_qubit_op_to_circuit(cmd,self._circuit)
        if new_qubit:
            self._qubit_dictionary[cmd.qubits[0][0].id] = cmd.qubits[0][0]

    def _translate_multi_qubit_op(self,cmd:ProjectQCommand):
        new_qubits = _add_multi_qubit_op_to_circuit(cmd,self._circuit)
        for q in new_qubits:
            self._qubit_dictionary[q.id] = q