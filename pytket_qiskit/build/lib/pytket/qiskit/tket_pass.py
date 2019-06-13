import qiskit
from qiskit.dagcircuit import DAGCircuit
from qiskit.providers import BaseBackend
from qiskit.transpiler.basepasses import TransformationPass, BasePass

from pytket._transform import Transform
from pytket._routing import route, Architecture
from pytket.qiskit import dagcircuit_to_tk, tk_to_dagcircuit

class TketPass(TransformationPass):
    """The :math:`\\mathrm{t|ket}\\rangle` compiler to be plugged in to the Qiskit compilation sequence"""
    filecount = 0

    def __init__(self,backend:BaseBackend, DROP_CONDS:bool=False,BOX_UNKNOWN:bool=True,name:str="T|KET>") :
        BasePass.__init__(self)
        self.DROP_CONDS=DROP_CONDS
        self.BOX_UNKNOWN=BOX_UNKNOWN
        self.name = name
        my_backend =  None
        if isinstance(backend, BaseBackend):
            my_backend = backend
        else:
            raise RuntimeError("Requires BaseBackend instance")
        self.coupling_map = my_backend.configuration().to_dict().get('coupling_map', None)

    def process_circ(self, circ):
        num_qubits = circ.n_qubits
        if num_qubits == 1 or self.coupling_map == "all-to-all":
            coupling_map = None
        else:
            coupling_map = self.coupling_map
        
        # pre-routing optimise
        Transform.OptimisePhaseGadgets().apply(circ)

        circlay = list(range(num_qubits))

        if coupling_map:
            directed_arc =  Architecture(coupling_map)
            # route_ibm fnction that takes directed Arc, returns dag with cnots etc. 
            circ, circlay = route(circ,directed_arc)
            circ.apply_boundary_map(circlay[0])
        
        # post route optimise
        Transform.OptimisePostRouting().apply(circ)
        circ.remove_blank_wires()

        return circ, circlay

    def run(self, dag:DAGCircuit) -> DAGCircuit:
        """
           Run one pass of optimisation on the circuit and route for the given backend.

        :param dag: The circuit to optimise and route

        :return: The modified circuit
        """

        circ = dagcircuit_to_tk(dag, _DROP_CONDS=self.DROP_CONDS,_BOX_UNKNOWN=self.BOX_UNKNOWN)
        circ, circlay = self.process_circ(circ)
        newdag = tk_to_dagcircuit(circ)
        newdag.name = dag.name 
        finlay = dict()
        for i, qi in enumerate(circlay):
            finlay[('q', i)] = ('q', qi)
        newdag.final_layout = finlay
        return newdag