# Script for generating the example circuits in the Unitary Coupled Cluster 
# optimisation benchmark set
#
# Requires qiskit-aqua~=0.4.1, qiskit-chemistry~=0.4.2

from qiskit_chemistry.drivers.pyscfd import PySCFDriver
from qiskit_chemistry import FermionicOperator
from qiskit_aqua.components.variational_forms import RYRZ
from qiskit_chemistry.aqua_extensions.components.initial_states import HartreeFock
from qiskit_chemistry.aqua_extensions.components.variational_forms import UCCSD

molecules = {
    # 'H2' : 'H .0 .0 .0; H .0 .0 0.75',
    'LiH' : 'Li .0 .0 .0; H .0 .0 0.75',
    # 'CH2' : 'H 0. 1.004 -0.35615; C 0. 0. 0.05982; H 0. -1.004 -0.35615',
    # 'C2H4' : 'C .000000 .000000 .667480; C .000000 .000000 -.667480; H .000000 .922832 1.237695; H .000000 -.922832 1.237695; H .000000 .922832 -1.237695; H .000000 -.922832 -1.237695'
}
bases = [
    # 'sto3g'
    '631g',
    # 'ccpvdz',
    # 'ccpvtz'
]
qubit_mappings = {
    'JW':'jordan_wigner'
    # 'P':'parity'
    # 'BK':'bravyi_kitaev'
}

for basis in bases :
    for qm_name, qubit_mapping in qubit_mappings.items() :
        for var_form_name, var_form_class in var_forms.items() :
            for mol_name, molecule_str in molecules.items() :
                driver = PySCFDriver(molecule_str, basis=basis)
                mol = driver.run()
                n_qubits = mol.one_body_integrals.shape[0]
                n_electrons = mol.num_alpha + mol.num_beta - mol.molecular_charge
                ferOp = FermionicOperator(h1=mol.one_body_integrals, h2=mol.two_body_integrals)
                qubitOp = ferOp.mapping(map_type=qubit_mapping, threshold=1e-8)
                qubitOp.chop(1e-10)
                initial_hf = HartreeFock(num_qubits=n_qubits, num_orbitals=n_qubits, qubit_mapping=qubit_mapping, two_qubit_reduction=False, num_particles=n_electrons)
                var_form = UCCSD(num_qubits=n_qubits, num_orbitals=n_qubits, num_particles=n_electrons, depth=1, initial_state=initial_hf, qubit_mapping=qubit_mapping)
                number_amplitudes = len(var_form._single_excitations) + len(var_form._double_excitations)
                amplitudes = [1e-4]*number_amplitudes
                circuit = var_form.construct_circuit(amplitudes)
                qasm = circuit.qasm()
                filename = '{m}_{v}_{q}_{b}.qasm'.format(m=mol_name, v=var_form_name, q=qm_name, b=basis)
                with open(filename, 'w') as ofile :
                    ofile.write(qasm)
                print(filename)