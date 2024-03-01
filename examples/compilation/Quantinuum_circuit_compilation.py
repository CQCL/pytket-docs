r"""
Circuit Compilation
===================

Circuits submitted to Quantinuum H-Series quantum computers and emulators are automatically run
through TKET compilation passes for H-Series hardware. This enables circuits to be automatically
optimized for H-Series systems and run more efficiently.

More information on the specific compilation passes applied can be found on the
``pytket-quantinuum`` documentation, specifically the `Default
Compilation <https://tket.quantinuum.com/extensions/pytket-quantinuum/#default-compilation>`__
section.

In the H-Series software stack, the optimization level applied is set with the ``tket-opt-level``
parameter. **The default compilation setting for circuits submitted to H-Series sytems is
optimization level 2.** More information is found in the *Quantinuum API Specification*.


When using ``pytket`` before submitting to hardware, the ``get_compiled_circuit`` function performs
the same compilation passes run after submission to Quantinuum systems. The advantage of using the
function before submitting to H-Series hardware is to see exactly what circuit optimizations will be
performed when submitted to hardware and determine if a different optimization level is desired. The
``optimisation_level`` parameter in the ``get_compiled_circuit`` function corresponds directly to
the level of optimisation after submitting to the H-Series systems and to the ``tket-opt-level``
parameter in the H-Series API. The default compilation for the ``get_compiled_circuit`` function is
optimization level 2, the same as when submitting to the H-Series directly.



Options
-------

Since the TKET compilation passes have been integrated into the H-Series stack, performing circuit
optimizations is redundant before submitting to hardware, unless the user would like to see the
optimizations applied before submitting. Given this, users may take 1 of 3 approaches when
submitting jobs: 1. Use ``optimisation_level=0`` when running ``get_compiled_circuit``, then submit
the circuit using ``process_circuits`` knowing that the corresponding optimization level actually
run will be 2. 2. Use the ``get_compiled_circuit`` function with the desired optimization level to
observe the transformed circuit before submitting and then specify ``tket-opt-level=None`` in the
``process_circuits`` function when submitting, in order for the optimizations to be applied as
desired. 3. If the user desires to have no optimizations applied, use ``optimisation_level=0`` in
``get_compiled_circuit`` and ``tket-opt-level=None`` in ``process_circuits``. This should be
specified in both functions.


Example Setup
~~~~~~~~~~~~~
# Set up the quantum circuit.
"""

from pytket.circuit import Circuit
from pytket.extensions.quantinuum import QuantinuumBackend

######################################################################
# Set up Bell State
# 

circuit = Circuit(2, name="Bell State")
circuit.H(0)
circuit.CX(0, 1)
circuit.measure_all()
machine = "H1-1E"
backend = QuantinuumBackend(device_name=machine)
backend.login()

######################################################################
# Option 1
# ~~~~~~~~
# 

######################################################################
# Corresponds to option 1 above where the user wants optimization level 2 in the stack so uses minimal
# rebasing in before submitting. You may still experiment with the optimization levels beforehand, but
# if optimization level 2 is desirable, then specify the options as illustrated below.
# 

n_shots = 100
compiled_circuit = backend.get_compiled_circuit(circuit, optimisation_level=0)
handle = backend.process_circuit(compiled_circuit, n_shots=n_shots)

######################################################################
# Option 2
# ~~~~~~~~
# 

######################################################################
# For option 2, suppose a user explores the results of TKET compilation passes on a circuit and finds
# that ``optimisation_level=1`` is desirable. The submission below specifies this in the
# ``get_compiled_circuit`` function with optimization level 1. Because the circuit is optimized
# beforehand, the TKET optimization in the H-Series stack should be turned off. The value
# ``tket-opt-level:None`` turns off TKET optimization in the H-Series stack.
# 

compiled_circuit = backend.get_compiled_circuit(circuit, optimisation_level=1)

handle = backend.process_circuit(
    compiled_circuit, n_shots=n_shots, options={"tket-opt-level": None}
)
print(handle)

######################################################################
# Option 3
# ~~~~~~~~
# 

######################################################################
# For option 3, suppose a user wants to turn off all optimizations in the stack, even simple
# single-qubit combinations done by the H-Series compiler. This can be done by setting
# ``optimisation_level=0`` in ``get_compiled_circuit`` and setting ``tket-opt-level:None`` in the
# ``process_circuits`` function.
# 

compiled_circuit = backend.get_compiled_circuit(circuit, optimisation_level=0)

handle = backend.process_circuit(
    compiled_circuit, n_shots=n_shots, options={"tket-opt-level": None}
)
print(handle)

######################################################################
# .. container::
# 
#    © 2024 by Quantinuum. All Rights Reserved.
# 