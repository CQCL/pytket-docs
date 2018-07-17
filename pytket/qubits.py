from typing import Iterator

from cirq import QubitId, GridQubit
from cirq.google import XmonDevice

from pytket import Architecture

class IndexedQubit(QubitId):
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

def sort_row_col(qubits: Iterator[GridQubit]) -> Iterator[GridQubit]:
    """Sort grid qubits first by row then by column"""

    return sorted(qubits, key=lambda x: (x.row, x.col))

def xmon2arc(xmon: XmonDevice) -> Architecture:
    """Generate an Architecture object for an XmonDevice"""

    nodes = len(xmon.qubits)
    indexed_qubits = sort_row_col(xmon.qubits)
    pairs = []
    for i, qb in enumerate(indexed_qubits):
        qb.index = i
    for qb in indexed_qubits:
        neighbours = xmon.neighbors_of(qb)
        #filter only higher index neighbours to avoid double counting edges
        forward_neighbours = filter(lambda x: indexed_qubits.index(x)>indexed_qubits.index(qb), neighbours)
        for x in forward_neighbours:
            pairs.append((indexed_qubits.index(qb), indexed_qubits.index(x)))
    return Architecture(pairs, nodes)