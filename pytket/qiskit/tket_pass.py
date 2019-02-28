import qiskit
from qiskit.dagcircuit import DAGCircuit
from qiskit.providers import BaseBackend
from qiskit.transpiler._basepasses import TransformationPass, BasePass
from qiskit_aqua_cmd import Preferences

from pytket._circuit import optimise_pre_routing, optimise_post_routing
from pytket._routing import route
from pytket.qiskit import dagcircuit_to_tk, tk_to_dagcircuit, coupling_to_arc

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
        num_qubits = circ.n_qubits()
        if num_qubits == 1 or self.coupling_map == "all-to-all":
            coupling_map = None
        else:
            coupling_map = self.coupling_map
        
        # pre-routing optimise
        optimise_pre_routing(circ)

        circlay = list(range(num_qubits))

        if coupling_map:
            directed_arc = coupling_to_arc(coupling_map)
            # route_ibm fnction that takes directed Arc, returns dag with cnots etc. 
            circ, circlay = route(circ,directed_arc)
            circ.apply_boundary_map(circlay[0])
        
        # post route optimise
        optimise_post_routing(circ)
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