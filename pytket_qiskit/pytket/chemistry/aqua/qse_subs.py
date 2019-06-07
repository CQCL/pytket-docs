# import common packages
import itertools
import numpy as np
from numpy import array, concatenate, zeros
import qiskit
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.quantum_info import Pauli

# lib from Qiskit AQUA Chemistry
from qiskit.chemistry import FermionicOperator

# lib from optimizer and algorithm
from qiskit.aqua.operator import Operator

# lib for driver
from collections import OrderedDict

from abc import ABC, abstractmethod


import time


def _jordan_wigner_mode(n):
        """
        Jordan_Wigner mode.
        Args:
            n (int): number of modes
        """
        a = []
        for i in range(n):
            xv = np.asarray([1] * i + [0] + [0] * (n - i - 1))
            xw = np.asarray([0] * i + [1] + [0] * (n - i - 1))
            yv = np.asarray([1] * i + [1] + [0] * (n - i - 1))
            yw = np.asarray([0] * i + [1] + [0] * (n - i - 1))
            a.append((Pauli(xv, xw), Pauli(yv, yw)))
        return a

def _one_body_mapping(a_i, a_j, threshold=0.000001):
        """
        Subroutine for one body mapping.
        Args:
            a_i (Pauli): pauli at index i
            a_j (Pauli): pauli at index j
            threshold: (float): threshold to remove a pauli
        Returns:
            Operator: Operator for those paulis
        """
        pauli_list = []
        for alpha in range(2):
            for beta in range(2):
                pauli_prod = Pauli.sgn_prod(a_i[alpha], a_j[beta])
                coeff = 1.0/4 * pauli_prod[1] * np.power(-1j, alpha) * np.power(1j, beta)
                pauli_term = [coeff, pauli_prod[0]]
                if np.absolute(pauli_term[0]) > threshold:
                    pauli_list.append(pauli_term)
        return Operator(paulis=pauli_list)

class QseMatrices():
    def __init__(self, qubit_hamiltonian, n_qubits):
        self.qubit_hamiltonian = qubit_hamiltonian
        self.n_qubits = n_qubits
        self.c_i = None

        paulis_test = _jordan_wigner_mode(n_qubits)
        excit_operator = []
        excit_operator_conjugated = []

        #Construct operators C_i C_j^+ and conjugated operators
        #C_i : 2nd quantization annihilation operator
        #C_i^+ : 2nd quantization creation operator
        
        k = 0
        for i, j in itertools.product(range(n_qubits), repeat=2):
            second_q_operator = _one_body_mapping(paulis_test[i],paulis_test[j])
            excit_operator.append(second_q_operator)
            second_q_op_conjugated = _one_body_mapping(paulis_test[j],paulis_test[i])
            excit_operator_conjugated.append(second_q_op_conjugated)
            k += 1
        self.excit_operator = excit_operator
        self.excit_operator_conjugated = excit_operator_conjugated

    def overlap(self):
        return np.outer(self.excit_operator_conjugated, self.excit_operator)
    def overlap_term(self, i, j):
        return self.excit_operator_conjugated[j]*self.excit_operator[i]
    def hamiltonian_term(self, i, j):

        return self.excit_operator_conjugated[j]*self.qubit_hamiltonian*self.excit_operator[i]

def unroll_paulis(paulis):

    coeffs = np.zeros(len(paulis), dtype=np.complex)
    bools = np.zeros((len(paulis), 2*paulis[0][1].numberofqubits), dtype=np.int)
    for i, pauli in enumerate(paulis):
        coeffs[i] = pauli[0]
        bools[i, :4] = pauli[1].v
        bools[i, 4:] = pauli[1].w
    
    return coeffs, bools


