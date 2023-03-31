# pip install pytket~=1.13

# # WASM function calls with pytket
# The WASM module in python allows you to add external classical functions from a compiled web assembly (WASM) to the circuit.

# In the first step you need to read in the wasm file. You can do this when creating the wasm file handler by giving the path to the file. The wasmfilehandler now knows all available functions and the corresponding signatures. If you are not sure about the signatures of the functions of your file you can get a list of them from the wasmfilehandler like shown below. The parameters and result types of the supported functions must be i32. All functions that contain other types will be listed when printing the wasmfilehandler as well, but you can't add them to a circuit.

from pytket import wasm, Circuit, Bit

wfh = wasm.WasmFileHandler("testfile.wasm")
print("wasm file uid:")
print(wfh)

print("\n\nwasm file repr:")
print(repr(wfh))

# In the next step we want to add some of the classical function calls to a circuit. We will start with adding the function "add_one" to read in for the first parameter from Bit(0) and write the result to Bit(1). The length of the two list giving the number of bits needs to be the number of parameters and the number of results.

c = Circuit(0, 8)

c.add_wasm(
    "add_one",  # name of the function
    wfh,  # wasm file handler
    [1],  # number of bits in each of the parameter i32
    [1],  # number of bits in each of the result i32
    [Bit(0), Bit(1)],
)  # list of bits where the wasm op will be added to

# If you want to have more than one bit per parameter, you can add that in the following way. This will add the function "add_one" to read in for the first parameter from Bit(0) and Bit(1) and write the result to Bit(2), Bit(3) and Bit(4).

c.add_wasm(
    "add_one",  # name of the function
    wfh,  # wasm file handler
    [2],  # number of bits in each of the parameter i32
    [3],  # number of bits in each of the result i32
    [Bit(0), Bit(1), Bit(2), Bit(3), Bit(4)],
)  # list of bits where the wasm op will be added to

# When adding functions with multiple parameters this can be done in the same way:

c.add_wasm(
    "multi",  # name of the function
    wfh,  # wasm file handler
    [2, 1],  # number of bits in each of the parameter i32
    [3],  # number of bits in each of the result i32
    [Bit(0), Bit(1), Bit(5), Bit(2), Bit(3), Bit(4)],
)  # list of bits where the wasm op will be added to

# If you want to add two parameters with the same bits, that is fine, too.

c.add_wasm(
    "multi",  # name of the function
    wfh,  # wasm file handler
    [2, 2],  # number of bits in each of the parameter i32
    [3],  # number of bits in each of the result i32
    [Bit(0), Bit(1), Bit(0), Bit(1), Bit(2), Bit(3), Bit(4)],
)  # list of bits where the wasm op will be added to

# If you are working with registers in your circuit to organise the classical bits you can add wasm to your circuit using given registers for each parameter and the return value.

# add registers to circuit

c0 = c.add_c_register("c0", 3)
c1 = c.add_c_register("c1", 4)
c2 = c.add_c_register("c2", 5)

c.add_wasm_to_reg(
    "multi",  # function name
    wfh,  # wasm file handler
    [c0, c1],  # register for each input parameter
    [c2],
)  # register for the result
c.add_wasm_to_reg(
    "add_one",  # function name
    wfh,  # wasm file handler
    [c2],  # register for each input parameter
    [c2],
)  # register for the result

# The WASM might have some global data stored. To make sure this data is not messed up by function calls in the wrong order pytket will make sure that the order of the wasm calls within a circuit is not restructured. For this purpose pytket will add all wasm operation to a wasm_wire by default. If you are not worried about a possible restructure of the wasm calls in your circuit you have the option to not add the wasm_wire to your wasm operations. If you only want to stop some special reordering for some of your wasm operations you can add some the wasm operations to multiple wasm_wire to allow the restructuring in the intended way. Even if there are not wasm_wire given, pytket will only restructure the the wasm operations if there are no dependencies to in parameters or the results.

# Here you can see that all operations we have created above are conected to the default wasm_wire:

for g in c:
    print(g)

# We will now create a new circuit and add four operations. The two add_one operations should be allowed to commute, but we want to make sure that "multi" is executed after the two other functions. The last add_two operation can commute with all others.

c = Circuit(0, 5)

c.add_wasm("add_one", wfh, [1], [1], [Bit(0), Bit(0)], [0])
c.add_wasm("add_one", wfh, [1], [1], [Bit(1), Bit(1)], [1])
c.add_wasm("multi", wfh, [1, 1], [1], [Bit(2), Bit(3), Bit(2)], [0, 1])
c.add_wasm("add_two", wfh, [1], [1], [Bit(4), Bit(4)], [])

for g in c:
    print(g)

# One helpful feature might be to plot the DAG of the circuit to get an overview of the different components of the circuit

from pytket.utils import Graph

g = Graph(c)
g.view_DAG()

# ## Send WASM to the Backend
# In the last step we want to send the circuit with the wasm to a backend. First we create the backend. For this step you will need Quantinuum credentials.

from pytket.extensions.quantinuum import QuantinuumBackend

machine = "H1-1E"
b = QuantinuumBackend(device_name=machine)
b.login()

# When processing the circuit you need to add the wasmfilehandler you created as parameter to the `process_circuits` in the shown way

from pytket.extensions.quantinuum import QuantinuumBackend

c = Circuit(1)
c.name = "test_wasm"
a = c.add_c_register("a", 8)
c.add_wasm_to_reg("add_one", wfh, [a], [a])
c = b.get_compiled_circuit(c)
h = b.process_circuits([c], n_shots=10, wasm_file_handler=wfh)[0]

status = b.circuit_status(h)
print(status)

status = b.circuit_status(h)
print(status)

result = b.get_result(h)
print(result)

for shot in result.get_shots():
    print(shot)
