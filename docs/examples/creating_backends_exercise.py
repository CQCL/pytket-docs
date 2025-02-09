from pytket.circuit import Qubit, Bit, UnitID
from pytket.pauli import Pauli, QubitPauliString

from binarytree import Node
from typing import List, Optional, Iterator, Dict, Set, Tuple
from copy import copy
import numpy as np


class Gate:
    """Top-level class for Gates.
    Handles the shared behaviour for conditions
    """

    def __init__(self, condition: Optional[Dict[Bit, int]]):
        """Create a new blank gate, optionally with some condition

        :param condition: A basic condition for executing the gate.
        If a dictionary is given, the gate is only run if every Bit in
        the condition matches its given value
        :type condition: Optional[Dict[Bit, int]]
        """
        self.condition = condition

    def units(self) -> Set[UnitID]:
        """Returns the set of all Qubits and Bits used in executing the gate.
        This is used for identifying end-of-circuit measurements by seeing if
        any subsequent gate uses the Qubit/Bit.

        :return: The set of all Qubits and Bits used by the gate.
        :rtype: Set[UnitID]
        """
        if self.condition:
            return set(self.condition.keys())
        else:
            return set()


class Rotation(Gate):
    """A gate corresponding to a unitary rotation about some qubit string."""

    def __init__(
        self, qps: QubitPauliString, angle: float, condition: Optional[Dict[Bit, int]]
    ):
        """Creates a gate with the unitary e^{-i * (angle/2) * qps}

        :param qps: The basis to rotate around, expressed as a Pauli term
        :type qps: QubitPauliString
        :param angle: The angle of rotation in radians
        :type angle: float
        :param condition: An optional condition determining whether or not the gate will be run
        :type condition: Optional[Dict[Bit, int]]
        """
        super().__init__(condition)
        self.qps = qps
        self.angle = angle

    def units(self) -> Set[UnitID]:
        """See `Gate.units()`"""
        return super().units().union(set(self.qps.to_dict().keys()))


class Measure(Gate):
    """A gate corresponding to a non-destructive Z-basis measurement on a given Qubit"""

    def __init__(self, qubit: Qubit, bit: Bit, condition: Optional[Dict[Bit, int]]):
        """Measures the given qubit and records the result in the given Bit

        :param qubit: The qubit to be measured
        :type qubit: Qubit
        :param bit: The location to store the measurement result
        :type bit: Bit
        :param condition: An optional condition determining whether or not the gate will be run
        :type condition: Optional[Dict[Bit, int]]
        """
        super().__init__(condition)
        self.qubit = qubit
        self.bit = bit

    def units(self) -> Set[UnitID]:
        """See `Gate.units()`"""
        return super().units().union({self.qubit, self.bit})


class MyCircuit:
    """A minimal representation of a circuit as a sequence of gates,
    including unitary rotations and single-qubit measurements
    """

    def __init__(self, qubits: List[Qubit], bits: List[Bit]):
        """Creates a new blank circuit with some set of Qubits and Bits

        :param qubits: Qubits present in the circuit
        :type qubits: List[Qubit]
        :param bits: Bits present in the circuit
        :type bits: List[Bit]
        """
        self.qubits = sorted(qubits, reverse=True)
        self.bits = sorted(bits, reverse=True)
        self.gates = list()

    def _check_units(self, gate: Gate):
        """Helper method to assert that every Qubit and Bit used by a gate
        is defined to be present in the circuit

        :param gate: Gate to check
        :type gate: Gate
        :raises ValueError: If the gate uses a Qubit/Bit that is not present
        """
        for u in gate.units():
            if u not in self.qubits and u not in self.bits:
                raise ValueError("Gate refers to unit not present in MyCircuit")

    def add_gate(
        self,
        qps: QubitPauliString,
        angle: float,
        condition: Optional[Dict[Bit, int]] = None,
    ):
        """Add a unitary rotation gate to the end of the circuit

        :param qps: The basis to rotate around, expressed as a Pauli term
        :type qps: QubitPauliString
        :param angle: The angle of rotation in radians
        :type angle: float
        :param condition: An optional condition determining whether the gate will be run, defaults to None
        :type condition: Optional[Dict[Bit, int]], optional
        """
        g = Rotation(qps, angle, condition)
        self._check_units(g)
        self.gates.append(g)

    def add_measure(
        self, qubit: Qubit, bit: Bit, condition: Optional[Dict[Bit, int]] = None
    ):
        """Add a single-qubit non-destructive Z-basis measurement to the end of the circuit

        :param qubit: Qubit to be measured
        :type qubit: Qubit
        :param bit: Bit to be measured
        :type bit: Bit
        :param condition: An optional condition determining whether the gate will be run, defaults to None
        :type condition: Optional[Dict[Bit, int]], optional
        """
        g = Measure(qubit, bit, condition)
        self._check_units(g)
        self.gates.append(g)


class DecisionNodeData:
    """Abstract class for data of a node in a binary decision tree.
    Can be either an InternalNode, IncompleteNode, or CompleteNode
    """

    def __init__(self):
        """Data for a decision tree node for simulating a quantum Circuit"""
        pass


class InternalNode(DecisionNodeData):
    """Data for an internal branching node of a decision tree.
    This node represents the branching from a mid-circuit measurement.
    The left child is the result from the 0 outcome and the right child for 1.
    """

    def __init__(self, zero_prob: float):
        """A decision node corresponding to the branching from an internal measurement

        :param zero_prob: Probability of outcome 0
        :type zero_prob: float
        """
        self.zero_prob = zero_prob


class IncompleteNode(DecisionNodeData):
    """Data for a leaf node of a decision tree that has not been fully explored.
    This node represents a specific branch of the simulation in progress.
    """

    def __init__(
        self, qstate: np.ndarray, cstate: np.ndarray, gate_iter: Iterator[Gate]
    ):
        """A decision node for a simulation that has not yet reached the end-of-circuit measurements

        :param qstate: Current statevector of the quantum system
        :type qstate: np.ndarray
        :param cstate: Current classical state
        :type cstate: np.ndarray
        :param gate_iter: Current position through the list of internal gates
        :type gate_iter: Iterator[Gate]
        """
        self.qstate = qstate
        self.cstate = cstate
        self.gate_iter = gate_iter


class CompleteNode(DecisionNodeData):
    """Data for a lead node of a decision tree that has been fully simulated.
    This node captures the final state on a branch just before the end-of-circuit measurements.
    """

    def __init__(self, cum_probs: np.ndarray, cstate: np.ndarray):
        """A decision node for a completed simulation from which we can just sample the end-of-circuit measurements

        :param cum_probs: Cumulative probabilities of outcomes
        :type cum_probs: np.ndarray
        :param cstate: Classical state
        :type cstate: np.ndarray
        """
        self.cum_probs = cum_probs
        self.cstate = cstate


class MySimulator:
    """A sampling simulator for MyCircuit objects,
    allowing for mid-circuit measurement and conditional gates
    """

    def __init__(self, circ: MyCircuit):
        """Initialise the simulator for a given circuit

        :param circ: The circuit to simulate
        :type circ: MyCircuit
        """
        self.qubits = circ.qubits
        self.bits = circ.bits

        # Separate end-of-circuit measures from internal gates
        self.interior_gates = list()
        self.end_measures = list()
        used_units = set()
        for g in reversed(circ.gates):
            g_units = g.units()
            if isinstance(g, Measure) and len(used_units.intersection(g_units)) == 0:
                self.end_measures.append(g)
            else:
                self.interior_gates.insert(0, g)
            used_units.update(g_units)

        # Decision tree that branches on mid-circuit measurements
        # Internal nodes track the probability
        # Start with a single branch in the initial state
        self.tree = Node(0)
        initial_qstate = np.zeros((2 ** len(self.qubits),), dtype=complex)
        initial_qstate[0] = 1.0
        initial_cstate = np.zeros((len(self.bits),), dtype=int)
        self.tree.data = IncompleteNode(
            initial_qstate, initial_cstate, iter(self.interior_gates)
        )

    def sample(self, n_shots: int, seed: Optional[int] = None) -> np.ndarray:
        """Sample from the final classical distribution.
        For each sample, will pick a branch for each internal measurement and traverse
        the simulation tree until the end-of-circuit measurements are reached.
        The tree caches the state of the simulation for each branch to reuse for later shots.

        :param n_shots: The number of samples to take
        :type n_shots: int
        :param seed: Seed for the random sampling, defaults to None
        :type seed: Optional[int], optional
        :return: Shot table with each row corresponding to a shot. Columns correspond to Bits in
        decreasing lexicographical order, i.e. [0, 1] corresponds to {Bit(0) : 1, Bit(1) : 0}
        :rtype: np.ndarray
        """
        if seed is not None:
            np.random.seed(seed)
        table = np.zeros((n_shots, len(self.bits)), dtype=int)
        for s in range(n_shots):
            # Uniformly select a random point from the measurement distribution
            point = np.random.uniform(0.0, 1.0)

            # Traverse the tree until we reach the end-of-circuit measurements
            current_node = self.tree
            # The range of values `point` could take to end up in the current node
            current_lower = 0.0
            current_upper = 1.0
            while not isinstance(current_node.data, CompleteNode):
                if isinstance(current_node.data, IncompleteNode):
                    # When at an IncompleteNode, there are no future branches already considered
                    # but we still have computation to simulate on this branch
                    # Simulate new gates until either a mid-circuit measurement
                    # or we reach the end of the internal gates
                    while True:
                        try:
                            next_gate = next(current_node.data.gate_iter)
                        except StopIteration:
                            # There are no more internal gates, so cumulative probabilities for
                            # the final measurements of every qubit
                            cum_probs = (
                                current_node.data.qstate
                                * current_node.data.qstate.conjugate()
                            ).cumsum()
                            current_node.data = CompleteNode(
                                cum_probs, current_node.data.cstate
                            )
                            break

                        # Skip the gate if the classical condition is not met
                        if next_gate.condition:
                            condition_met = True
                            for b, v in next_gate.condition.items():
                                bi = self.bits.index(b)
                                if current_node.data.cstate[bi] != v:
                                    condition_met = False
                                    break
                            if not condition_met:
                                continue

                        if isinstance(next_gate, Rotation):
                            # Apply the rotation to the quantum state and continue to the next gate
                            pauli_tensor = next_gate.qps.to_sparse_matrix(self.qubits)
                            exponent = -0.5 * next_gate.angle
                            current_node.data.qstate = np.cos(
                                exponent
                            ) * current_node.data.qstate + 1j * np.sin(
                                exponent
                            ) * pauli_tensor.dot(
                                current_node.data.qstate
                            )
                        else:
                            # Otherwise, we have a measurement
                            # Compute the states after a 0-outcome and a 1-outcome and make a branch

                            # Project into measurement subspaces
                            identity = QubitPauliString().to_sparse_matrix(self.qubits)
                            z_op = QubitPauliString(
                                next_gate.qubit, Pauli.Z
                            ).to_sparse_matrix(self.qubits)
                            zero_proj = 0.5 * (identity + z_op)
                            one_proj = 0.5 * (identity - z_op)
                            zero_state = zero_proj.dot(current_node.data.qstate)
                            one_state = one_proj.dot(current_node.data.qstate)

                            # Find probability of measurement and normalise
                            zero_prob = np.vdot(zero_state, zero_state)
                            if zero_prob >= 1e-10:  # Prevent divide-by-zero errors
                                zero_state *= 1 / np.sqrt(zero_prob)
                            if 1 - zero_prob >= 1e-10:
                                one_state *= 1 / np.sqrt(1 - zero_prob)

                            # Update the classical state for each outcome
                            bit_index = self.bits.index(next_gate.bit)
                            zero_cstate = copy(current_node.data.cstate)
                            zero_cstate[bit_index] = 0
                            one_cstate = current_node.data.cstate
                            one_cstate[bit_index] = 1

                            # Replace current node in the tree by a branch, with each outcome as children
                            zero_node = Node(0)
                            zero_node.data = IncompleteNode(
                                zero_state,
                                zero_cstate,
                                copy(current_node.data.gate_iter),
                            )
                            one_node = Node(0)
                            one_node.data = IncompleteNode(
                                one_state, one_cstate, current_node.data.gate_iter
                            )
                            current_node.data = InternalNode(zero_prob)
                            current_node.left = zero_node
                            current_node.right = one_node
                            break
                else:
                    # Reached an internal measurement, so randomly pick a branch to traverse
                    current_decision = (
                        current_lower
                        + (current_upper - current_lower) * current_node.data.zero_prob
                    )
                    if point < current_decision:
                        current_node = current_node.left
                        current_upper = current_decision
                    else:
                        current_node = current_node.right
                        current_lower = current_decision
            # Finally reached the end of the circuit
            # Randomly sample from the final measurements
            index = np.searchsorted(
                current_node.data.cum_probs, point / (current_upper - current_lower)
            )
            bitstring = bin(index)[2:].zfill(len(self.qubits))

            # Update the classical state with final measurement outcomes
            table[s] = current_node.data.cstate
            for g in self.end_measures:
                if g.condition:
                    # If final measurements are conditioned, the classical state may not be updated
                    condition_met = True
                    for b, v in g.condition.items():
                        bi = self.bits.index(b)
                        if current_node.data.cstate[bi] != v:
                            condition_met = False
                            break
                    if not condition_met:
                        continue
                qi = self.qubits.index(g.qubit)
                bi = self.bits.index(g.bit)
                table[s, bi] = int(bitstring[qi])
        return table


import pytest


def get_counts(circ: MyCircuit, n_shots: int, seed: int) -> Dict[Tuple[int, ...], int]:
    """Helper method for tests to summarise the shot table from the simulator

    :param circ: The circuit to simulate
    :type circ: MyCircuit
    :param n_shots: The number of samples to take
    :type n_shots: int
    :param seed: Seed for the random sampling
    :type seed: int
    :return: Map from readout array to the number of instances observed in the shot table
    :rtype: Dict[Tuple[int, ...], int]
    """
    sim = MySimulator(circ)
    shots = sim.sample(n_shots=n_shots, seed=seed)
    rows, freqs = np.unique(shots, axis=0, return_counts=True)
    return {tuple(r): f for r, f in zip(rows, freqs)}


def test_empty() -> None:
    c = MyCircuit([Qubit(0), Qubit(1)], [Bit(0), Bit(1)])
    counts = get_counts(c, n_shots=100, seed=11)
    assert counts == {(0, 0): 100}


def test_hadamard() -> None:
    c = MyCircuit([Qubit(0), Qubit(1)], [Bit(0), Bit(1)])
    c.add_gate(QubitPauliString(Qubit(0), Pauli.Z), np.pi / 2)
    c.add_gate(QubitPauliString(Qubit(0), Pauli.X), np.pi / 2)
    c.add_gate(QubitPauliString(Qubit(0), Pauli.Z), np.pi / 2)
    c.add_measure(Qubit(0), Bit(0))
    counts = get_counts(c, n_shots=100, seed=11)
    assert counts == {(0, 0): 50, (0, 1): 50}


def test_bell() -> None:
    c = MyCircuit([Qubit(0), Qubit(1)], [Bit(0), Bit(1)])
    # Hadamard Q0
    c.add_gate(QubitPauliString(Qubit(0), Pauli.Z), np.pi / 2)
    c.add_gate(QubitPauliString(Qubit(0), Pauli.X), np.pi / 2)
    c.add_gate(QubitPauliString(Qubit(0), Pauli.Z), np.pi / 2)
    # CX Q0 Q1
    c.add_gate(QubitPauliString(Qubit(0), Pauli.Z), -np.pi / 2)
    c.add_gate(QubitPauliString(Qubit(1), Pauli.X), -np.pi / 2)
    c.add_gate(QubitPauliString([Qubit(0), Qubit(1)], [Pauli.Z, Pauli.X]), np.pi / 2)
    c.add_measure(Qubit(0), Bit(0))
    c.add_measure(Qubit(1), Bit(1))
    counts = get_counts(c, n_shots=100, seed=11)
    assert counts == {(0, 0): 50, (1, 1): 50}


def test_basic_ordering() -> None:
    # Test that final bit readouts are in the intended order (DLO)
    c = MyCircuit([Qubit(0)], [Bit(0), Bit(1), Bit(2)])
    c.add_measure(Qubit(0), Bit(0))
    c.add_gate(QubitPauliString(Qubit(0), Pauli.X), np.pi)
    c.add_measure(Qubit(0), Bit(2))
    c.add_gate(QubitPauliString(Qubit(0), Pauli.X), np.pi / 2)
    c.add_measure(Qubit(0), Bit(1))
    counts = get_counts(c, n_shots=100, seed=11)
    assert counts == {(1, 0, 0): 50, (1, 1, 0): 50}


def test_overwrite() -> None:
    # Test that classical data is overwritten by later measurements appropriately
    c = MyCircuit([Qubit(0)], [Bit(0), Bit(1)])
    c.add_measure(Qubit(0), Bit(0))
    c.add_gate(QubitPauliString(Qubit(0), Pauli.X), np.pi)
    c.add_measure(Qubit(0), Bit(0))
    c.add_measure(Qubit(0), Bit(1))
    c.add_gate(QubitPauliString(Qubit(0), Pauli.X), np.pi / 2)
    c.add_measure(Qubit(0), Bit(1))
    counts = get_counts(c, n_shots=100, seed=11)
    assert counts == {(0, 1): 50, (1, 1): 50}


def test_conditional_rotation() -> None:
    c = MyCircuit([Qubit(0)], [Bit(0), Bit(1)])
    # Randomise qubit state
    c.add_gate(QubitPauliString(Qubit(0), Pauli.X), np.pi / 2)
    c.add_measure(Qubit(0), Bit(0))
    # Correct qubit state to |1> - this should only happen when the measurement was 0
    c.add_gate(QubitPauliString(Qubit(0), Pauli.X), np.pi, {Bit(0): 0, Bit(1): 0})
    # Randomise final measurement - this should never happen
    c.add_gate(QubitPauliString(Qubit(0), Pauli.X), np.pi / 2, {Bit(0): 0, Bit(1): 1})
    c.add_measure(Qubit(0), Bit(1))
    counts = get_counts(c, n_shots=100, seed=11)
    assert counts == {(1, 0): 50, (1, 1): 50}


def test_conditional_measurement() -> None:
    c = MyCircuit([Qubit(0), Qubit(1)], [Bit(0), Bit(1), Bit(2), Bit(3)])
    # Get a random number
    c.add_gate(QubitPauliString(Qubit(0), Pauli.X), np.pi / 2)
    c.add_measure(Qubit(0), Bit(0))
    # If random number is 0 then flip to give |1>
    # Otherwise, randomly generate |+i> or |-i>
    c.add_gate(QubitPauliString(Qubit(0), Pauli.X), np.pi / 2)
    c.add_measure(Qubit(0), Bit(1), {Bit(0): 1})
    c.add_gate(QubitPauliString(Qubit(0), Pauli.X), np.pi / 2)
    # Deterministic if Bit(0) == 0, random if Bit(0) == 1
    c.add_measure(Qubit(0), Bit(2))
    # Test end-of-circuit conditions by copying Bit(2) to Bit(3)
    c.add_gate(QubitPauliString(Qubit(1), Pauli.X), np.pi)
    c.add_measure(Qubit(1), Bit(3), {Bit(2): 1})
    counts = get_counts(c, n_shots=10000, seed=11)
    assert counts[(1, 1, 0, 0)] == pytest.approx(5000, rel=0.02)
    assert counts[(0, 0, 0, 1)] == pytest.approx(1250, rel=0.02)
    assert counts[(1, 1, 0, 1)] == pytest.approx(1250, rel=0.02)
    assert counts[(0, 0, 1, 1)] == pytest.approx(1250, rel=0.02)
    assert counts[(1, 1, 1, 1)] == pytest.approx(1250, rel=0.02)
