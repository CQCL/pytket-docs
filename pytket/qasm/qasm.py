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

#TODO: Add classical register interaction (for measures especially)
#TODO: Add ability to interpret gates acting on whole register
#TODO: Add custom gates
#TODO: Figure out nice way to make these class methods of Circuit
import os
from pytket import Circuit, OpType
from sympy import sympify
# from types import MethodType
import math

NOPARAM_COMMANDS = {
    "cx": OpType.CX,
    "x": OpType.X,
    "y": OpType.Y,
    "z": OpType.Z,
    "h": OpType.H,
    "s": OpType.S,
    "sdg": OpType.Sdg,
    "t": OpType.T,
    "tdg": OpType.Tdg,
    "cz": OpType.CZ,
    "cy": OpType.CY,
    "ch": OpType.CH,
    "ccx": OpType.CCX,
    "measure": OpType.Measure,
    "id": OpType.noop
}

PARAM_COMMANDS = {
    "u3": OpType.U3,
    "u2": OpType.U2,
    "u1": OpType.U1,
    "rx": OpType.Rx,
    "ry": OpType.Ry,
    "rz": OpType.Rz,
    "crz": OpType.CRz,
    "cu1": OpType.CU1,
    "cu3": OpType.CU3
}

_tk_to_qasm_noparams = dict((reversed(item) for item in NOPARAM_COMMANDS.items()))
_tk_to_qasm_params = dict((reversed(item) for item in PARAM_COMMANDS.items()))

class QASMParser(object):
    """Class for parsing OpenQASM files into CQC t|ket> Circuits."""

    def __init__(self):
        self.circuit = Circuit()
        self.register_dict = dict()

    def parse_qasm(self, qasm):
        lines = qasm.splitlines()
        rows = []

        #first, get rid of comments and whitespace lines
        for l in lines:
            i = l.find("//")
            if i!=-1:
                s = l[0:i].strip()
            else: s = l.strip()
            if s: rows.append(s)
        
        #now, throw away OPENQASM descriptor etc.
        if not (rows[0].startswith("OPENQASM 2.0") and rows[1].startswith('include "qelib1.inc";')):
            raise TypeError("File must declare OPENQASM version and its includes.")
        data = "\n".join(rows[2:])

        #now, separate out the custom gates to deal with elsewhere
        while True:
            i = data.find("gate ")
            if i == -1: break
            j = data.find("}", i)
            if j == -1: raise TypeError("Custom gate definition is invalid.")
            self.parse_custom_gate(data[i:j+1]) #TODO: deal with custom gate
            data = data[:i] + data[j+1:]

        #now, parse the regular instructions
        instructions = [s.strip() for s in data.split(";") if s.strip()]
        for i in instructions:
            self.parse_instruction(i)
        return self.circuit

    def parse_custom_gate(self, data):
        raise TypeError("Cannot currently parse custom gates")

    def parse_instruction(self, instruction):
        if instruction.find("->") != -1:
            ###handle measure gates
            ###currently assumes that there is just 1 qb being read to 1 bit
            name_and_qbs, bits = instruction.split("->",1)
            if (name_and_qbs.find("measure") == -1):
                raise Exception("Error in parsing: cannot accept a non-Measure gate writing to classical register")
            name_and_qbs = name_and_qbs.replace("measure","")
            name_and_qbs = name_and_qbs.replace(" ","")

            name_and_qbs.strip()
            qregname, qbindex = name_and_qbs.split("[")
            qbindex = int(qbindex[0])
            qubit = self.circuit.q_regs[qregname][qbindex]

            bits = bits.replace(" ", "")
            bitreg, bitindex = bits.split("[")
            bitindex = int(bitindex[0])
            bit = self.circuit.c_regs[bitreg][bitindex]

            self.circuit.add_measure(qubit,bit)
            return

        if instruction.find("(") != -1:
            name, rest = instruction.split(") ", 1)
            name = name.replace(" ","")
        else:
            name, rest = instruction.split(" ", 1)
        args = [s.strip() for s in rest.split(",") if s.strip()]

        #deal with qubit register declarations
        if name == "qreg" or name == "creg":
            regname, size = args[0].split("[",1)
            regname.strip()
            size = int(size[:-1])
            if name == "qreg":
                self.circuit.add_q_register(regname,size)
            else:
                self.circuit.add_c_register(regname,size)
            return
        
        #get qubits to append operation to
        qubits = []
        for a in args:
            if "[" in a:
                regname, val = a.split("[",1)
                val = int(val[:-1])
                qubits.append(self.circuit.q_regs[regname][val])
            else:
                raise Exception("Unknown error in parsing: Cannot parse argument {}".format(a))

        #if the gate is parameterised, get these parameters
        if name.find("(") != -1:
            name, params = name.split("(",1)
            if name in PARAM_COMMANDS:
                angles = [s.strip() for s in params.split(",") if s.strip()]
                halfturn_angles = []
                for ang in angles:
                    ang = ang.replace("pi",str(math.pi))
                    try:
                        halfturns = sympify(ang)/math.pi
                        halfturn_angles.append(halfturns)
                    except:
                        raise TypeError("Cannot parse angle: {}".format(ang))
                self.circuit.add_gate(PARAM_COMMANDS[name],halfturn_angles,qubits,[])

            else:
                raise TypeError("Cannot parse gate of type: {}".format(name))
            
        else:
            if name in NOPARAM_COMMANDS:
                self.circuit.add_gate(NOPARAM_COMMANDS[name],[],qubits,[])
            else:
                raise TypeError("Cannot parse gate of type: {}".format(name))
        
    
def circuit_from_qasm(input_file:str) -> Circuit :
    """A method to generate a tket Circuit from a qasm file"""
    ext = os.path.splitext(input_file)[-1]
    if (ext != ".qasm"):
        raise TypeError("Can only convert .qasm files")
    p = QASMParser()
    with open(input_file, 'r') as f:
        circ = p.parse_qasm(f.read())
    return circ

def circuit_to_qasm(circ:Circuit,output_file:str):
    """A method to generate a qasm file from a tket Circuit"""
    with open(output_file, 'w') as out:
        out.write("OPENQASM 2.0;\ninclude \"qelib1.inc\";\n\n")
        for qregname in circ.q_regs:
            out.write("qreg {}[{}];\n".format(qregname,circ.q_regs[qregname].size()))
        for command in circ:
            op = command.op
            optype = op.get_type()
            has_params = False
            if optype in _tk_to_qasm_noparams:
                opstr = _tk_to_qasm_noparams[optype]
            elif optype in _tk_to_qasm_params:
                has_params = True
                opstr = _tk_to_qasm_params[optype]
            else:
                raise TypeError("Cannot print command of type: {}".format(op.get_name()))
            qbs = command.qubits
            out.write(opstr)
            if has_params:
                params = op.get_params()
                out.write("(")
                for i in range(len(params)):
                    reduced = True
                    try:
                        p = float(params[i])
                    except TypeError:
                        reduced = False
                        p = params[i]
                    if i < len(params)-1:
                        if reduced:
                            out.write("{}*pi,".format(p))
                        else:
                            out.write("({})*pi,".format(p))
                            
                    else:
                        if reduced:
                            out.write("{}*pi)".format(p))
                        else:
                            out.write("({})*pi)".format(p))
            out.write(" ")
            for i in range(len(qbs)):
                out.write("{}[{}]".format(qbs[i].reg.name,qbs[i].index))
                if optype == OpType.Measure:
                    out.write(" -> ")
                elif i < len(qbs)-1 :
                    out.write(",")
                else:
                    out.write(";\n")
            if optype == OpType.Measure: ###assume written to only 1 bit
                bits = command.bits
                out.write("{}[{}];\n".format(bits[0].reg.name,bits[0].index))
        
# Circuit.to_qasm = MethodType(circuit_to_qasm,Circuit)
# Circuit.__init__ = circuit_from_qasm