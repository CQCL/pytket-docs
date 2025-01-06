## EXAMPLE FILE FOR THE OXFORD QIS WORKSHOP FROM 22 FEB 2020
## THIS IS WRITTEN TO WORK WITH PYTKET v0.4.1 AND WILL NOT BE UPDATED IN FUTURE

from pytket.circuit import Circuit, PauliExpBox, Pauli
from pytket.predicates import CompilationUnit
from pytket.passes import DecomposeBoxes, PauliSimp, SequencePass
from pytket.utils import expectation_from_counts
from pytket.extensions.qiskit import AerBackend, AerStateBackend

from sympy import Symbol
from scipy.optimize import minimize
from openfermion import QubitOperator, FermionOperator, jordan_wigner


# Generate a parametric ansatz
def h2_JW_sto3g_ansatz():
    symbols = [Symbol("s0"), Symbol("s1"), Symbol("s2")]
    ansatz = Circuit(4)
    # Initialise in Hartree-Fock state
    ansatz.X(0)
    ansatz.X(1)
    # Single excitations
    ansatz.add_pauliexpbox(
        PauliExpBox([Pauli.X, Pauli.Z, Pauli.Y, Pauli.I], -symbols[0]), [0, 1, 2, 3]
    )
    ansatz.add_pauliexpbox(
        PauliExpBox([Pauli.Y, Pauli.Z, Pauli.X, Pauli.I], symbols[0]), [0, 1, 2, 3]
    )
    ansatz.add_pauliexpbox(
        PauliExpBox([Pauli.I, Pauli.X, Pauli.Z, Pauli.Y], -symbols[1]), [0, 1, 2, 3]
    )
    ansatz.add_pauliexpbox(
        PauliExpBox([Pauli.I, Pauli.Y, Pauli.Z, Pauli.X], symbols[1]), [0, 1, 2, 3]
    )
    # Double excitations
    ansatz.add_pauliexpbox(
        PauliExpBox([Pauli.X, Pauli.X, Pauli.X, Pauli.Y], -symbols[2]), [0, 1, 2, 3]
    )
    ansatz.add_pauliexpbox(
        PauliExpBox([Pauli.X, Pauli.X, Pauli.Y, Pauli.X], -symbols[2]), [0, 1, 2, 3]
    )

    ansatz.add_pauliexpbox(
        PauliExpBox([Pauli.X, Pauli.Y, Pauli.X, Pauli.X], symbols[2]), [0, 1, 2, 3]
    )
    ansatz.add_pauliexpbox(
        PauliExpBox([Pauli.Y, Pauli.X, Pauli.X, Pauli.X], symbols[2]), [0, 1, 2, 3]
    )

    ansatz.add_pauliexpbox(
        PauliExpBox([Pauli.X, Pauli.Y, Pauli.Y, Pauli.Y], -symbols[2]), [0, 1, 2, 3]
    )
    ansatz.add_pauliexpbox(
        PauliExpBox([Pauli.Y, Pauli.X, Pauli.Y, Pauli.Y], -symbols[2]), [0, 1, 2, 3]
    )

    ansatz.add_pauliexpbox(
        PauliExpBox([Pauli.Y, Pauli.Y, Pauli.X, Pauli.Y], symbols[2]), [0, 1, 2, 3]
    )
    ansatz.add_pauliexpbox(
        PauliExpBox([Pauli.Y, Pauli.Y, Pauli.Y, Pauli.X], symbols[2]), [0, 1, 2, 3]
    )
    # Synthesise structures into primitive gates
    DecomposeBoxes().apply(ansatz)
    return ansatz, symbols


# Compile ansatz symbolically for the target backend
def compile_ansatz(ansatz, backend):
    # Solve for device constraints
    cu = CompilationUnit(ansatz)
    backend.default_compilation_pass.apply(cu)
    return cu.circuit, cu.final_map


# Construct a measurement circuit for each (non-trivial) term in the Hamiltonian
def measurement_circuits(hamiltonian, n_qubits):
    all_circs = []
    for pauli, _ in hamiltonian.terms.items():
        if not pauli:
            continue  # Ignore the constant term
        measure_circ = Circuit(n_qubits, n_qubits)
        for qb, p in pauli:
            if p == "I":
                continue  # Discard I qubits
            elif p == "X":
                measure_circ.H(qb)
            elif p == "Y":
                measure_circ.Rx(0.5, qb)
            measure_circ.Measure(qb, qb)
        all_circs.append(measure_circ)
    return all_circs


# Compile each measurement circuit for the backend
def compile_measurements(all_measures, backend, ansatz_final_map):
    compiled_measures = []
    for measure_circ in all_measures:
        cu = CompilationUnit(measure_circ)
        backend.default_compilation_pass.apply(cu)
        measure_circ = cu.circuit
        # Permute qubits to match their locations after the ansatz
        qb_map = {
            cu.final_map[m_qb]: original_qb
            for original_qb, m_qb in ansatz_final_map.items()
        }
        measure_circ.rename_units(qb_map)
        compiled_measures.append(measure_circ)
    return compiled_measures


# Routine for calculating expectation value from a shot-based backend
def expectation_value(state_circuit, all_measures, hamiltonian, backend):
    # Add each measurement to the state in a new circuit
    all_circuits = []
    for measure in all_measures:
        measured_circ = state_circuit.copy()
        measured_circ.append(measure)
        all_circuits.append(measured_circ)
    # Send off all circuits to the backend
    backend.process_circuits(all_circuits, n_shots=8000)

    # Calculate energy by summing expectation values
    if () in hamiltonian.terms:
        energy = hamiltonian.terms[()]
    else:
        energy = 0
    coeffs = [c for p, c in hamiltonian.terms.items() if p]
    for circ, coeff in zip(all_circuits, coeffs):
        counts = backend.get_counts(circ)
        energy += coeff * expectation_from_counts(counts)
    return energy


# Set up objective function for the VQE optimisation
def gen_objective_function(ansatz, symbols, hamiltonian, backend):
    n_qubits = ansatz.n_qubits
    ansatz, final_map = compile_ansatz(ansatz, backend)
    all_measures = measurement_circuits(hamiltonian, n_qubits)
    all_measures = compile_measurements(all_measures, backend, final_map)

    # Calculate the expectation value of the ansatz at some given parameter values
    def objective_function(params):
        ansatz_at_params = ansatz.copy()
        symbol_map = dict(zip(symbols, params))
        ansatz_at_params.symbol_substitution(symbol_map)
        return expectation_value(
            ansatz_at_params, all_measures, hamiltonian, backend
        ).real

    return objective_function


# Number operator for exercise 5
number_operator = (
    FermionOperator("0^ 0")
    + FermionOperator("1^ 1")
    + FermionOperator("2^ 2")
    + FermionOperator("3^ 3")
)

# Hamiltonian for H2 (Jordan-Wigner, sto-3g)
hamiltonian = QubitOperator(
    "-0.10973055606700793 [] + -0.04544288414432624 [X0 X1 Y2 Y3] + 0.04544288414432624 [X0 Y1 Y2 X3] + 0.04544288414432624 [Y0 X1 X2 Y3] + -0.04544288414432624 [Y0 Y1 X2 X3] + 0.16988452027940334 [Z0] + 0.16821198673715726 [Z0 Z1] + 0.1200514307254604 [Z0 Z2] + 0.16549431486978664 [Z0 Z3] + 0.1698845202794033 [Z1] + 0.16549431486978664 [Z1 Z2] + 0.1200514307254604 [Z1 Z3] + -0.21886306781219583 [Z2] + 0.17395378776494158 [Z2 Z3] + -0.21886306781219583 [Z3]"
)


# Set up and run a VQE experiment
ansatz, symbols = h2_JW_sto3g_ansatz()
backend = AerBackend()
obj = gen_objective_function(ansatz, symbols, hamiltonian, backend)
initial_params = [1e-6, 1e-6, 1e-1]

result = minimize(obj, initial_params, method="Nelder-Mead")
print("Final parameter values", result.x)
print("Final energy value", result.fun)
