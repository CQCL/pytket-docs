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


"""Methods to allow conversion between Qiskit and pytket circuit graphs
"""

import qiskit
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.circuit import Instruction, Measure
from qiskit.dagcircuit import DAGCircuit
from qiskit.converters import circuit_to_dag
from qiskit.extensions.standard import *

import sympy
from sympy import N, pi

from pytket._circuit import OpType, Op, Circuit
from pytket._routing import Architecture, PhysicalCircuit

import time
from typing import List, Union
from collections import OrderedDict

import logging
logger = logging.getLogger(__name__)

DEBUG=False
"""Turn on debugging output to console.
"""

BOX_UNKNOWN=True
"""If True then tket will interpret any unknown ops as OpType.Box and
   store the name of the op in the desc field of the Box.
"""

DROP_CONDS=False
"""If True, tket will silently discard any classical conditions attached to 
   any op (If DEBUG is True then a warning message will be emitted.)  If False,
   an exception will be raised for any op with classical conditions.
"""



_name_index=0
def _fresh_name(prefix="tk_c") :
    global _name_index
    _name_index+=1
    return prefix + str(_name_index)

def dagcircuit_to_tk(dag:DAGCircuit, _BOX_UNKNOWN:bool=BOX_UNKNOWN, _DROP_CONDS:bool=DROP_CONDS) -> Circuit :
    """Converts a :py:class:`qiskit.DAGCircuit` into a :math:`\\mathrm{t|ket}\\rangle` :py:class:`Circuit`.
    Note that not all Qiskit operations are currently supported by pytket. Classical registers are supported only as 
    the output of measurements. This does not attempt to preserve the structure 
    of the quantum registers, instead creating one big quantum register.

    :param dag: A circuit to be converted

    :return: The converted circuit
    """
    qs = dag.qubits()
    qnames = ["%s[%d]" % (r.name, i) for r, i in qs]
    g = dag._multi_graph
    circ = Circuit()
    if DEBUG :
        print("new graph w " + str(len(qs)) + " qubits")
        print(str(qs))

    # process vertices
    tk_vs = dict()
    for n in list(g.nodes(data=True)) :
        node = n[0]
        if DEBUG : 
            print(str(node.type)+ " " + str(node.name))
        if ((node.type=="in" or node.type=="out") and not node.name in qnames) :
            # don't create vertices for in/outs of classical registers
            if DEBUG:
                print("Dropping node " + str(node))
            continue
        else :
            tk_vs[node] = circ._add_vertex(_node_converter(circ, node, _BOX_UNKNOWN=_BOX_UNKNOWN, _DROP_CONDS=_DROP_CONDS))
            if DEBUG:
                print("qiskit vertex " + str(node) + " is t|ket> vertex " +str(tk_vs[node]))
    # process edges
    for e in g.edges(data=True) :
        wire = e[2]["wire"]
        if wire in qs : # ignore classical wires
            src_port = _get_port_for_edge(e[0], wire)
            tgt_port = _get_port_for_edge(e[1], wire)
            if DEBUG : 
                print(_make_edge_str(tk_vs[e[0]],src_port,tk_vs[e[1]],tgt_port))
            circ._add_edge(tk_vs[e[0]],src_port,tk_vs[e[1]],tgt_port)                

    return circ

def _get_port_for_edge(node, qbit) :
    if node.type != 'op' :
        return 0
    ports = node.qargs
    if len(ports) <= 1 :
        return 0
    for i in range(len(ports)) :
        if ports[i] == qbit :
            return i
    raise RuntimeError("Can't find port " + str(qbit) + " on op " + str(node))


### pretty priting for edges
def _make_edge_str(src,src_port,tgt,tgt_port):
    return str(src) + "." + str(src_port) + " --> " + str(tgt) + "." + str(tgt_port)
    

def _node_converter(circuit, node, _BOX_UNKNOWN=BOX_UNKNOWN, _DROP_CONDS=DROP_CONDS) :
    if node.type=="in" :
        return Op.Input()
    elif node.type=="out":
        return Op.Output()
    elif node.type=="op" :
        if type(node.op) in _known_ops :
            ### TODO : cannot handle non-trivial conditions
            if node.condition :
                if _DROP_CONDS :
                    if DEBUG :
                        print("WARNING : dropped the condition from op " + str(node))
                    else :
                        pass
                else :
                    raise NotImplementedError("Conditional ops are not supported : " + str(node))
            ### TODO : support for classical wires to be added
            ### Classical regsisters are inferred from the measurements only
            if node.name == "measure" :
                return _make_measure_op(circuit, node)
            else :
                if len(node.cargs) > 0 :
                    raise NotImplementedError("Classical arguments not supported for op type " + node.name)
                nparams = len(node.op.params)
                if nparams == 0 :
                    return _const_ops[type(node.op)]
                elif nparams == 1 :
                    return _make_one_param_op(circuit, node)
                else:
                    return _make_multi_param_op(circuit, node)
        else:
            if _BOX_UNKNOWN :
                return _make_box_node(circuit, node)
            else :
                raise NotImplementedError("Unknown Op type : " + node.name)
    else :
        raise NotImplementedError("Unknown node type : " + node.type)        

_known_ops = {
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
    ToffoliGate : OpType.CCX,
    CrzGate : OpType.CRz,
    Cu1Gate : OpType.CU1,
    Cu3Gate : OpType.CU3,
    Measure : OpType.Measure
}

_known_ops_rev = {v : k for k, v in _known_ops.items() }

_const_ops = {
    IdGate  : Op.noop(),
    XGate   : Op.X(),
    YGate   : Op.Y(),
    ZGate   : Op.Z(),
    SGate   : Op.S(),
    SdgGate : Op.Sdg(),    
    TGate   : Op.T(),
    TdgGate : Op.Tdg(),    
    HGate   : Op.H(),    
    CnotGate    : Op.CX(),
    CyGate  : Op.CY(),        
    CzGate  : Op.CZ(),
    CHGate  : Op.CH(),        
    ToffoliGate : Op.CCX()
}

def _normalise_param_in(p) :
    # need to strip factors of pi from float valued params
    ## sympy is kind of a pain
    try :
        val = p.evalf() # if this works we have a sympy expression
        return val / pi.evalf()
    except AttributeError :
        if type(p) == float or type(p) == sympy.core.numbers:
            return p / pi.evalf()
        else :
            return p

def _make_one_param_op (circuit, node) :
    param = _normalise_param_in(node.op.params[0])
    return circuit._get_op(_known_ops[type(node.op)],param)

def _make_multi_param_op (circuit, node) :
    params = list(map(_normalise_param_in, node.op.params))
    return circuit._get_op(_known_ops[type(node.op)],params)

def _make_measure_op (circuit, node ) :
    if DEBUG : 
        print("made " + str(node.cargs))
    return circuit._get_op(OpType.Measure,str(node.cargs))
    

def _make_box_node(circuit, node) :
    if DEBUG : 
        print("WARNING : Don't know how to handle node : " + str(node))
        print("WARNING : Making a box instead")   
    return circuit._get_op(OpType.Box,node.name)


def _read_qasm_file(filename) :
    """Read a qasm file and return the corresponding tket Circuit.
    Not all QASM constructs are supported."""
    qasm = QuantumCircuit.from_qasm_file(filename)
    return dagcircuit_to_tk(circuit_to_dag(qasm))

##### ===== Conversion tk --> DAGCircuit #######

def tk_to_dagcircuit(circ:Union[Circuit, PhysicalCircuit],_qreg_name:str="q") -> DAGCircuit :
    """
       Convert a :math:`\\mathrm{t|ket}\\rangle` :py:class:`Circuit` to a :py:class:`qiskit.DAGCircuit` . Requires
       that the circuit only conatins :py:class:`OpType` s from the qelib set.
    
    :param circ: A circuit to be converted

    :return: The converted circuit
    """
    if isinstance(circ, PhysicalCircuit) :
        c = circ._get_circuit()
    else :
        c = circ
    dc = DAGCircuit()
    qreg = QuantumRegister(c.n_qubits, name=_qreg_name)
    dc.add_qreg(qreg)
    in_boundary = c._get_boundary()[0]
    out_boundary = c._get_boundary()[1]
    for command in c:
        o = command.op
        qargs = [ (qreg, i) for i in command.qubits ]
        gate, cargs, params = _translate_ops(c,o,qargs)
        if cargs :
            _extend_cregs(dc,cargs)
        if gate :
            ins = gate(*list(map(_normalise_param_out, params)))
            dc.apply_operation_back(ins ,qargs=qargs,
                                    cargs=cargs)
    tk2dg_outs = {}
    
    for i, v in enumerate(out_boundary):
        tk2dg_outs[v] = dc.output_map[(qreg, i)]
    for i, v in enumerate(out_boundary):
        dc._multi_graph.node[tk2dg_outs[v]]["wire"] = [(qreg, i)]
        dc.output_map[(qreg, i)] = tk2dg_outs[v]
    # Force order of shot readout to be in qubit/register name order
    dc.cregs = OrderedDict(sorted(dc.cregs.items(), key = lambda x: int(x[0][1:])))
    return dc

def _paths_to_qubits_bis(paths,qreg_name="q") :
    lut = {}
    for i in range(len(paths)) :
        for x in paths[i] :
            lut[x] = qreg_name + "[" + str(i) + "]"
    return lut


def _normalise_param_out(p) :
    # tk float params are implicitly fractions of pi
    return p*pi
    
def _translate_ops(circ,o,qargs) :
    if o.get_type() == OpType.Input or o.get_type() == OpType.Output :
        # don't need to create vertices for input and output
        return (None, None, None) 

    # if o.get_type() == OpType.Box :
    #     gate = o.get_desc()
    if o.get_type() in _known_ops_rev :
        gate = _known_ops_rev[o.get_type()]
    else :
        raise NotImplementedError("OpType " + o.get_name() + " not supported")

    if o.get_type() == OpType.Measure :
        # this is a temporary hack - to be removed once tket supports classical wires.
        if o.get_desc():
            cargs = eval(o.get_desc()) # TODO: tut tut tut. Who was this? *Looks at git blame* Me from 3 months ago was bad programmer
            if isinstance(cargs,str) :
                cargs = [(ClassicalRegister(1,cargs),0)]
        else:
            # cargs = [(ClassicalRegister(1,_fresh_name()),0)]
            qreg, index = qargs[0]
            reg = qreg.name + str(index)
            cargs = [(ClassicalRegister(1,reg),0)]
    else : 
        cargs = []
    # if DEBUG and gate == "measure" :
    #     print(cargs)
    return (gate, cargs, o.get_params())


def _extend_cregs(dc,cargs) :
    for reg, idx in dict(sorted(cargs)).items() :
        if reg.name not in dc.cregs:
            dc.add_creg(reg)
        elif idx >= dc.cregs[reg.name].size :
            old_size = dc.cregs[reg].size
            dc.cregs[reg].size = idx+1
            for j in range(idx+1 - old_size) : 
                dc._add_wire((reg,j+old_size),True)
