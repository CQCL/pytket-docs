OPENQASM 2.0;
include "qelib1.inc";

qreg q[3];
creg c[1];
h q[0];
cx q[0],q[1];
cx q[1],q[2];
rz(0.25*pi) q[2];
measure q[2] -> c[0];
