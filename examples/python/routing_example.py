# # Respecting Architecture Connectivity Constraints - Advanced Routing in tket

# Very few current or planned quantum architectures have all-to-all qubit connectivity. In consequence, quantum circuits must be modified before execution to ensure that every multi-qubit gate in a circuit corresponds to a set of interactions that are permitted by the architecture.  The problem is solved for arbitrary architectures by adding ```SWAP``` gates and distributed ```CX``` gates, and through translation of multi-qubit gates in to architecture permitted ones.
#
# In this tutorial we will show how this routing problem is solved automatically in tket. The basic examples require only the installation of pytket, ```pip install pytket```, while further examples require the installation of some supported subpackages, ```pytket_qiskit``` & ```pytket_cirq```.
#
# Let's start by importing the Architecture class from ```pytket```:

from pytket.routing import Architecture

# The Architecture class is used in ```pytket``` to hold information about a quantum architectures connectivity constraints. An Architecture object requires a coupling map to be created i.e. a list of edges between qubits which defines where two-qubit primitives may be executed. A coupling map can be produced naively by the integer indexing of nodes and edges in your architecture. We also use networkx and matplotlib to draw a graph representation of our Architecture.

import networkx as nx
import matplotlib.pyplot as plt


def draw_graph(coupling_map):
    coupling_graph = nx.Graph(coupling_map)
    nx.draw(coupling_graph, labels={node: node for node in coupling_graph.nodes()})


simple_coupling_map = [(0, 1), (1, 2), (2, 3)]
simple_architecture = Architecture(simple_coupling_map)
draw_graph(simple_coupling_map)

# Alternatively we could use the `Node` class to assign our nodes - you will see why this can be helpful later. Lets create an Architecture with an identical graph in this manner.

from pytket.circuit import Node

node_0 = Node("example_register", 0)
node_1 = Node("example_register", 1)
node_2 = Node("example_register", 2)
node_3 = Node("example_register", 3)

id_coupling_map = [(node_0, node_1), (node_1, node_2), (node_2, node_3)]
id_architecture = Architecture(id_coupling_map)
draw_graph(id_coupling_map)

# We can also create an ID with an arbitrary-dimensional index. Lets make a 2x2x2 cube:

node_000 = Node("cube", [0, 0, 0])
node_001 = Node("cube", [0, 0, 1])
node_010 = Node("cube", [0, 1, 0])
node_011 = Node("cube", [0, 1, 1])
node_100 = Node("cube", [1, 0, 0])
node_101 = Node("cube", [1, 0, 1])
node_110 = Node("cube", [1, 1, 0])
node_111 = Node("cube", [1, 1, 1])

cube_coupling_map = [
    (node_000, node_001),
    (node_000, node_010),
    (node_010, node_011),
    (node_001, node_011),
    (node_000, node_100),
    (node_001, node_101),
    (node_010, node_110),
    (node_011, node_111),
    (node_100, node_101),
    (node_100, node_110),
    (node_110, node_111),
    (node_101, node_111),
]

cube_architecture = Architecture(cube_coupling_map)
draw_graph(cube_coupling_map)

# To avoid that tedium though we could just use our SquareGrid Architecture:

from pytket.routing import SquareGrid

alternative_cube_architecture = SquareGrid(2, 2, 2)
draw_graph(alternative_cube_architecture.coupling)

# In many cases, we are interested in the architectures of real devices. These are available directly from the device backends, available within tket's respective extension packages.

# In reality a Quantum Device has much more information to it than just its connectivity constraints. This includes information we can use in noise-aware methods such as gate errors and readout errors for each qubit. These methods can improve circuit performance when running on real hardware. If available from hardware providers, a device Backend will store this information via the `backend_info` attribute.

from qiskit import IBMQ

IBMQ.load_account()


# We can produce an IBMQ Backend object using ```process_characterisation```. This returns a dictionary containing characteriastion information provided by IBMQ, including t1 times, t2 times, qubit frequencies and gate times along with the coupling graph of the device as a pytket ```Architecture```.

from pytket.circuit import OpType
from pytket.extensions.qiskit.qiskit_convert import process_characterisation

provider = IBMQ.providers()[0]
quito_backend = provider.get_backend("ibmq_quito")
quito_characterisation = process_characterisation(quito_backend)
draw_graph(quito_characterisation["Architecture"].coupling)

# This characterisation contains a range of information such as gate fidelities. Let's look at two-qubit gate errors.
for key, val in quito_characterisation["EdgeErrors"].items():
    print(key, val)

# We've now seen how to create custom Architectures using indexing and nodes, how to use our built-in Architecture generators for typical connectivity graphs and how to access characterisation information using the ```process_characterisation``` method.
#
# Let's now see how we can use these objects are used for Routing circuits - we create a circuit for Routing to our original architectures and assume the only primitive constraint is the ```CX``` gate, which can only be executed on an edge in our coupling map.

from pytket import Circuit

example_circuit = Circuit(4)
example_circuit.CX(0, 1).CX(0, 2).CX(1, 2).CX(3, 2).CX(0, 3)
for gate in example_circuit:
    print(gate)

# We can also visualise the `Circuit` using, for example, IBM Qiskit's `QuantumCircuit` printer. To do this, we must use the `pytket.extensions.qiskit` subpackage and import a method from within Qiskit.

from pytket.extensions.qiskit import tk_to_qiskit

print(tk_to_qiskit(example_circuit))

# This circuit can not be executed on any of our Architectures without modification. We can see this by looking at the circuits interaction graph, a graph where nodes are logical qubits and edges are some two-qubit gate.

interaction_edges = [(0, 1), (0, 2), (1, 2), (3, 2), (0, 3)]
draw_graph(interaction_edges)

draw_graph(simple_coupling_map)

# Sometimes we can route a circuit just by labelling the qubits to nodes of our Architecture such that the interaction graph matches a subgraph of the Architecture - unfortunately this isn't possible here.
#
# Let's call ```pytket```'s automatic routing method, route our circuit for the first Architecture we made, and have a look at our new circuit:

from pytket.routing import route

simple_modified_circuit = route(example_circuit, simple_architecture)

for gate in simple_modified_circuit:
    print(gate)

print(tk_to_qiskit(simple_modified_circuit))

draw_graph(id_architecture.coupling)

# The route method has relabelled the qubits in our old circuit to nodes in simple_architecture, and has added ```SWAP``` gates that permute logical qubits on nodes of our Architecture.
#
# Let's repeat this for id_architecture:

id_modified_circuit = route(example_circuit, id_architecture)

for gate in id_modified_circuit:
    print(gate)

print(tk_to_qiskit(id_modified_circuit))

# Both simple_architecture and id_architecture had the same graph structure, and so we can see that the qubits have been relabelled and ```SWAP``` gates added identically - the only difference is the preservation of the node labelling of id_architecture.
#
# Let's repeat this one more time for cube_architecture:

cube_modified_circuit = route(example_circuit, cube_architecture)

for gate in cube_modified_circuit:
    print(gate)

cmc_copy = cube_modified_circuit.copy()
cmc_copy.flatten_registers()
print(tk_to_qiskit(cmc_copy))

# Similarly the circuits qubits have been relabelled and ```SWAP``` gates added. In this example though ```route``` is able to utilise the extra connectivity of cube_architecture to reduce the number of ```SWAP``` gates added from 3 to 1.
#
# We also route for the Quito architecture.

quito_modified_circuit = route(example_circuit, quito_characterisation["Architecture"])

for gate in quito_modified_circuit:
    print(gate)

print(tk_to_qiskit(quito_modified_circuit))

# The ```route``` method comes with a set of parameters that can be modified to tune the performance of routing for a circuit to a given Architecture.
#
# The 6 parameters are as follows:
# - (int) **swap_lookahead**, the depth of lookahead employed when trialling ```SWAP``` gates during Routing, default 50.
# - (int) **bridge_lookahead**, the depth of lookahead employed when comparing ```BRIDGE``` gates to ```SWAP``` gates during Routing, default 2.
# - (int) **bridge_interactions**, the number of interactions considered in a slice of multi-qubit gates when comparing ```BRIDGE``` gates to ```SWAP``` gates during routing, default 1.
# - (float) **bridge_exponent**, effects the weighting placed on future slices when comparing ```BRIDGE``` gates to ```SWAP``` gates, default 0.

# Let's change some of our basic routing parameters:

basic_parameters = dict(bridge_lookahead=4, bridge_interactions=4, swap_lookahead=0)
id_basic_modified_circuit = route(example_circuit, id_architecture, **basic_parameters)

for gate in id_basic_modified_circuit:
    print(gate)

# By changing the basic routing parameters we return a different routed circuit. To assess performance we must know the CX decomposition of both the ```SWAP``` and ```BRIDGE``` gates.

SWAP_c = Circuit(2)
SWAP_c.SWAP(0, 1)
SWAP_decomp_c = Circuit(2)
SWAP_decomp_c.CX(0, 1).CX(1, 0).CX(0, 1)
BRIDGE_c = Circuit(3)
BRIDGE_c.CX(0, 2)
BRIDGE_decomp_c = Circuit(3)
BRIDGE_decomp_c.CX(0, 1).CX(1, 2).CX(0, 1).CX(1, 2)

print(tk_to_qiskit(SWAP_c), "\n=\n", tk_to_qiskit(SWAP_decomp_c))
print(tk_to_qiskit(BRIDGE_c), "\n=\n", tk_to_qiskit(BRIDGE_decomp_c))

# The ```BRIDGE``` (or Distributed-CX gate distance 2) and ```SWAP``` both introduce a net three ```CX``` gates to the circuit.
#
# Considering this, by changing our basic parameters our routed circuit has one less gate added, and so should have net three fewer ```CX``` gates. We can confirm this by calling a ```Transformation``` pass that will decompose our additional gates to ```CX``` gates for us.

from pytket.transform import Transform

Transform.DecomposeSWAPtoCX().apply(id_modified_circuit)
Transform.DecomposeSWAPtoCX().apply(id_basic_modified_circuit)
Transform.DecomposeBRIDGE().apply(id_basic_modified_circuit)

print(
    "CX gates in id_modified_circuit: ", id_modified_circuit.n_gates_of_type(OpType.CX)
)
print(
    "CX gates in id_basic_modified_circuit: ",
    id_basic_modified_circuit.n_gates_of_type(OpType.CX),
)

# So, by changing the parameters we've managed to produce another suitable routed solution with three fewer ```CX``` gates.
#
# We may be able to reduce the number of ```CX``` gates in our routed circuits by using the ```RemovedRedundancies``` ```Transformation``` pass which will replace any adjacent identical ```CX``` gates with the Identity and remove them.

Transform.RemoveRedundancies().apply(id_modified_circuit)
Transform.RemoveRedundancies().apply(id_basic_modified_circuit)

print(
    "CX gates in id_modified_circuit: ", id_modified_circuit.n_gates_of_type(OpType.CX)
)
print(
    "CX gates in id_basic_modified_circuit: ",
    id_basic_modified_circuit.n_gates_of_type(OpType.CX),
)

# By changing the routing parameters and cleaning up our circuits after routing we've managed to reduce the number of ```CX``` gates in the final circuit by 5!

print(tk_to_qiskit(id_modified_circuit))
print(tk_to_qiskit(id_basic_modified_circuit))

# We can also confirm their validity:

print(id_modified_circuit.valid_connectivity(id_architecture, False))
print(id_basic_modified_circuit.valid_connectivity(id_architecture, False))

# Some circuits may not have bidirectional edges between qubits. We can check that our circuits respect unidirectional device edges by changing the directed flag in the ```Circuit.valid_connectivity``` method to True:

print(id_modified_circuit.valid_connectivity(id_architecture, True))
print(id_basic_modified_circuit.valid_connectivity(id_architecture, True))

# Neither of these circuits respect the id_architecture if its coupling map had a directed constraint. We can easily make them satisfy this constraint though by flipping the direction of some ```CX``` gates and adding ```H``` gates as suitable. The ```Transform``` pass ```DecomposeCXDirected``` does this automatically:

Transform.DecomposeCXDirected(id_architecture).apply(id_modified_circuit)
Transform.DecomposeCXDirected(id_architecture).apply(id_basic_modified_circuit)

print(id_modified_circuit.valid_connectivity(id_architecture, True))
print(id_basic_modified_circuit.valid_connectivity(id_architecture, True))

print("Total gates in id_modified_circuit: ", id_modified_circuit.n_gates)
print("Total gates in id_basic_modified_circuit: ", id_basic_modified_circuit.n_gates)

# As each flipped ```CX``` gate introduces 4 ```H``` gates, the number of additional ```H``` gates is large.
#
# We can reapply ```RemoveRedundancies``` to improve this.

Transform.RemoveRedundancies().apply(id_modified_circuit)
Transform.RemoveRedundancies().apply(id_basic_modified_circuit)

print("Total gates in id_modified_circuit: ", id_modified_circuit.n_gates)
print("Total gates in id_basic_modified_circuit: ", id_basic_modified_circuit.n_gates)

# We can see that by changing our basic parameters, we've managed to significantly improve routing performance for a directed architecture for this example.
#
# We can also use Placement objects to relabel logical circuit qubits to physical device qubits before routing, hopefully improving performance by reducing eventual number of ```SWAP``` gates added. Available options are ```Placement``` (as used by default route), ```LinePlacement```, ```GraphPlacement``` and ```NoiseAwarePlacement```.

from pytket.routing import Placement, LinePlacement, GraphPlacement, NoiseAwarePlacement

# The default ```Placement``` assigns logical qubits to physical qubits as they are encountered during routing. ```LinePlacement``` uses a strategy described in https://arxiv.org/abs/1902.08091. ```GraphPlacement``` and ```NoiseAwarePlacement``` are described in Section 7.1 of https://arxiv.org/abs/2003.10611. The ```NoiseAwarePlacement``` method uses the same subgraph monomorphism strategy as ```GraphPlacement``` to find potential mappings, but scores them using device information to anticpiate which initial mapping will produce a circuit with best overall fidelity.
#

# ```Placement```, ```LinePlacement``` and ```GraphPlacement``` only require an architecture device when producing placements.
# ```NoiseAwarePlacement``` requires additional information about the average single- and two-qubit gate error rates for each qubit and coupling, along with readout error rates.
# The ```get_avg_characterisation``` method can be used to convert the characterisation stored in the IBMQ provider backend object to the averaged error rates required.


from pytket.extensions.qiskit.qiskit_convert import get_avg_characterisation

quito_avg_characterisation = get_avg_characterisation(quito_characterisation)

# Define a function for printing our maps:


def print_qubit_mapping(the_map):
    print("Qubit to Node mapping:")
    for k, v in the_map.items():
        print(k, v)


# We can use the Placement objects to either modify the circuit in place, or return the mapping as a QubitMap.

lp_quito = LinePlacement(quito_characterisation["Architecture"])
graph_quito = GraphPlacement(quito_characterisation["Architecture"])
noise_quito = NoiseAwarePlacement(
    quito_characterisation["Architecture"],
    node_errors=quito_avg_characterisation["node_errors"],
    link_errors=quito_avg_characterisation["edge_errors"],
    readout_errors=quito_avg_characterisation["readout_errors"],
)


print("LinePlacement map:")
print_qubit_mapping(lp_quito.get_placement_map(example_circuit))
print("GraphPlacement map:")
print_qubit_mapping(graph_quito.get_placement_map(example_circuit))
print("NoiseAwarePlacement map:")
print_qubit_mapping(noise_quito.get_placement_map(example_circuit))

# Each of these methods produces a different qubit->node mapping.  Lets compare their performance:

lp_ex_circ = example_circuit.copy()
lp_quito.place(lp_ex_circ)
gp_ex_circ = example_circuit.copy()
graph_quito.place(gp_ex_circ)
np_ex_circ = example_circuit.copy()
noise_quito.place(np_ex_circ)

line_routed_circuit = route(lp_ex_circ, quito_characterisation["Architecture"])
graph_routed_circuit = route(gp_ex_circ, quito_characterisation["Architecture"])
noise_aware_routed_circuit = route(np_ex_circ, quito_characterisation["Architecture"])


for c in [line_routed_circuit, graph_routed_circuit, noise_aware_routed_circuit]:
    Transform.DecomposeBRIDGE().apply(c)
    Transform.DecomposeSWAPtoCX().apply(c)

print(
    "CX gates in line_routed_circuit: ", line_routed_circuit.n_gates_of_type(OpType.CX)
)
print(
    "CX gates in graph_routed_circuit: ",
    graph_routed_circuit.n_gates_of_type(OpType.CX),
)
print(
    "CX gates in noise_aware_routed_circuit: ",
    noise_aware_routed_circuit.n_gates_of_type(OpType.CX),
)

# In this example all of the placement methods perform equally, giving the same overall ```CX``` gate overhead.
#
# We can also provide routing with custom initial maps, partial or full. Lets define a partial custom map for only one of the qubits and see how routing performs. We can do this using an index mapping:

from pytket.routing import place_with_map
from pytket import Qubit

partial_initial_index_map = {0: 1}
partial_initial_map = {Qubit(i): Node(j) for i, j in partial_initial_index_map.items()}
print_qubit_mapping(partial_initial_map)

partial_ex_circ = example_circuit.copy()
place_with_map(partial_ex_circ, partial_initial_map)
partial_routed_circuit = route(partial_ex_circ, quito_characterisation["Architecture"])


Transform.DecomposeBRIDGE().apply(partial_routed_circuit)
Transform.DecomposeSWAPtoCX().apply(partial_routed_circuit)
Transform.RemoveRedundancies().apply(partial_routed_circuit)

print(
    "CX gates in partial_routed_circuit: ",
    partial_routed_circuit.n_gates_of_type(OpType.CX),
)

# ## Routing with Predicates

# While we've discussed methods that allow more control over the routing procedure used and allow for experimentation, circuits can easily be routed to a Device of choice using the ```pass``` system in ```pytket``` (further explanation of this system can be found in our compilation example notebook). In doing so we can use the ```ConnectivityPredicate``` to guarantee that our circuit obeys the connectivity constraints of the given Architecture.
#
# Let's import the ```CompilationUnit``` object and some useful passes along with our ```ConnectivityPredicate```.

from pytket.predicates import CompilationUnit, ConnectivityPredicate

from pytket.passes import SequencePass, RoutingPass, DecomposeSwapsToCXs

# Finally, lets demonstrate the pass system using other devices from  ```pytket-cirq```.
import cirq_google
import pytket.extensions.cirq as pc

foxtail_characterisation = pc.process_characterisation(cirq_google.Foxtail)
foxtail_arc = foxtail_characterisation["Architecture"]


bristlecone_characterisation = pc.process_characterisation(cirq_google.Bristlecone)
bristlecone_arc = bristlecone_characterisation["Architecture"]


def predicate_route_device(my_circuit, my_architecture):
    gp = GraphPlacement(my_architecture)
    gp.place(my_circuit)
    cu = CompilationUnit(my_circuit, [ConnectivityPredicate(my_architecture)])
    routing_passes = SequencePass(
        [RoutingPass(my_architecture), DecomposeSwapsToCXs(my_architecture, False)]
    )
    routing_passes.apply(cu)
    return cu.circuit, cu.check_all_predicates()


from pytket.qasm import circuit_from_qasm

comparison_circuit = circuit_from_qasm("qasm/routing_example_circuit.qasm")
foxtail_circuit, foxtail_valid = predicate_route_device(comparison_circuit, foxtail_arc)
bristlecone_circuit, bristlecone_valid = predicate_route_device(
    comparison_circuit, bristlecone_arc
)

print(
    "Foxtail circuit, number of CX gates:",
    foxtail_circuit.n_gates_of_type(OpType.CX),
    ", depth of CX gates:",
    foxtail_circuit.depth_by_type(OpType.CX),
    ", result valid:",
    foxtail_valid,
)
print(
    "Bristlecone circuit, number of CX gates:",
    bristlecone_circuit.n_gates_of_type(OpType.CX),
    ", depth of CX gates:",
    bristlecone_circuit.depth_by_type(OpType.CX),
    ", result valid:",
    bristlecone_valid,
)
