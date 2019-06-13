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

"""Qubit methods/classes for integration of cirq and :math:`\\mathrm{t|ket}\\rangle`
"""
from typing import List, Iterator

import cirq
from cirq import Qid, LineQubit, GridQubit
from cirq.google import XmonDevice

from pytket._routing import Architecture

class IndexedQubit(Qid):
    """A qubit identified by a number."""

    def __init__(self, index: int) -> None:
        self.index = index

    def __str__(self):
        return str(self.index)

    def __repr__(self):
        return 'IndexedQubit({})'.format(repr(self.index))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.index == other.index

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((IndexedQubit, self.index))

    def _comparison_key(self):
        return self.index

def _sort_row_col(qubits: Iterator[GridQubit]) -> List[GridQubit]:
    """Sort grid qubits first by row then by column"""

    return sorted(qubits, key=lambda x: (x.row, x.col))

def xmon_to_arc(xmon: XmonDevice) -> Architecture:
    """Generates a :math:`\\mathrm{t|ket}\\rangle` :py:class:`Architecture` object for a Cirq :py:class:`XmonDevice` .
    
    :param xmon: The device to convert

    :return: The corresponding :math:`\\mathrm{t|ket}\\rangle` :py:class:`Architecture`
    """

    nodes = len(xmon.qubits)
    indexed_qubits = _sort_row_col(xmon.qubits)
    pairs = []
    for qb in indexed_qubits:
        neighbours = xmon.neighbors_of(qb)
        #filter only higher index neighbours to avoid double counting edges
        forward_neighbours = filter(lambda x: indexed_qubits.index(x)>indexed_qubits.index(qb), neighbours)
        for x in forward_neighbours:
            pairs.append((indexed_qubits.index(qb), indexed_qubits.index(x)))
    return Architecture(pairs, nodes)

def _indexed_qubits_from_circuit(circuit : cirq.Circuit) -> List[Qid]:
    qubit_list = list(circuit.all_qubits())
    qubit_list = sorted(qubit_list, key=lambda q : q._comparison_key())
    return qubit_list