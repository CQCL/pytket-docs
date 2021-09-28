Changelog
==================================

0.15.0 (September 2021)
-----------------------

Minor new features:

* Passes ``PauliSimp``, ``PauliSquash`` and ``GuidedPauliSimp`` can now
  decompose to three-qubit ``XXPhase3`` gates using the new
  ``CXConfigType.MultiQGate`` config type.
* New method ``compilation_pass_from_script`` to construct a compilation pass
  from a simple textual specification.
* New transform ``RebaseToTket`` and new pass ``SquashToTK1``.

API changes:

* The deprecated transform ``RebaseToQiskit`` and the deprecated passes
  ``DecomposeMultiQubitsIBM``, ``RebaseIBM``, ``SynthesiseIBM`` and
  ``USquashIBM`` are removed.
* The transform ``OptimisePostRouting`` transforms to TK1 instead of U gates.

0.14.0 (September 2021)
-----------------------

Major new features:

* New ``Circuit.add_assertion`` method for applying quantum assertions to circuits.
* Two new box types  ``StabiliserAssertionBox`` and ``ProjectorAssertionBox``.
* New ``BackendResult.get_debug_info`` method for summarising assertion results.
* New ``PauliStabiliser`` class.
* Native support for MacOS running on M1 (arm64) architecture (Python 3.8 and 3.9 only).
* New compilerpass for architecture aware synthesis of phase polynomials ``AASRouting``.

Minor new features:

* Update circuit display to include extra gate information and use ZX-style colours.
* `BackendInfo`, `Architecture` and `Node` are now JSON-serializable.
* `QubitPauliOperator` and `QubitPauliString` are now JSON-serializable.
* Equality checks on `Architecture` only consider node IDs and coupling.
* New pass `DecomposeMultiQubitsCX`, equivalent to `DecomposeMultiQubitsIBM` (which is deprecated).
* New pass `DecomposeSingleQubitsTK1`.
* New pass `SynthesiseTket`.
* New ``XXPhase3`` OpType.

API changes:

* The transforms `ReduceSingles`, `OptimisePauliGadgets` and `OptimisePhaseGadgets`, and the passes `CliffordSimp`, `PeepholeOptimise2Q`, `FullPeepholeOptimise` and `OptimisePhaseGadgets`, produce TK1 instead of U gates.
* The passes `O2Pass`, `O1Pass` and `DecomposeSingleQubitsIBM` are removed (use `FullPeepholeOptimise` and `SynthesiseTket` instead for the first two).
* `QubitPauliOperator.to_dict()` (deprecated) is replaced by the property `QubitPauliOperator.map`.

Deprecations:

* The passes`DecomposeMultiQubitsIBM` (equivalent to `DecomposeMultiQubitsCX`), `DecomposeSingleQubitsIBM`, `RebaseToQiskit`, `SynthesiseIBM`, `RebaseIBM` and `USquashIBM` are deprecated.


0.13.0 (July 2021)
------------------

Major new features:

* New circuit functions, e.g. ``get_unitary``, calculate numerical unitaries and statevectors from non-symbolic circuits.
* New serialization methods for compilation passes.

Minor new features:

* Additions to `BackendInfo`.
* More reliable handling of timeouts for placement.
* User-configurable placement timeout.

Fixes:

* Fixed occasional segfault in placement pass.
* Daggering or transposing circuits with CnX fixed to have valid operation arguments.

API changes:

* :py:meth:`Backend.compile_circuit` is deprecated,
  :py:meth:`Backend.get_compiled_circuit` and
  :py:meth:`Backend.get_compiled_circuits` (for a sequence of circuits) replace
  it, do not act in place, returning the compiled circuit(s). In place
  compilation can still be achieved with `backend.default_compilation_pass().apply(circ)`

0.12.0 (June 2021)
------------------

Major new features:

* New ``ThreeQubitSquash`` compilation pass to simplify long three-qubit subcircuits.
* Three-qubit squash included in ``FullPeepholeOptimise`` pass; new ``PeepholeOptimise2Q`` pass corresponds to former ``FullPeepholeOptimise``.

Minor new features:

* add_phase now returns the circuit
* Option for `process_circuits` to take a list of `n_shots`.
* `Device` class removed, replaced with :py:class:`BackendInfo`.
* ``QubitErrorContainer`` removed.
* ``RoutingMethod`` removed.

Bugfixes and improvements:

* Barriers no longer count towards circuit depth.
* Squashing of rotations with symbolic angles now performs more simplification, leading to much shorter expressions, and works around a bug in symengine that caused invalid simplification of some expressions.

0.11.0 (May 2021)
-----------------
Major new features:

* New ``pytket.utils.symbolic`` module to generate symbolic unitaries and statevectors from symbolic circuits.
* New box type ``Unitary3qBox`` implementing arbitrary 3-qubit unitaries.

Minor new features:

* New ``ECR`` OpType.
* New ``SynthesiseOQC`` pass.
* New ``RebaseOQC`` pass.
  
0.10.1 (May 2021)
-----------------

Minor new features:

* New ``PauliSquash`` pass combining ``PauliSimp`` with ``FullPeepholeOptimise``.
* New options for ``SimplifyInitial``.

0.10.0 (April 2021)
-------------------

Major new features:

* HTML rendering of Circuit in Jupyter notebooks, ``pytket.circuit.display.render_circuit_jupyter``.

Minor new features:

* EulerAngleReduction pass uses multi-qubit commutativity to reduce rotation triplets to pairs
* EulerAngleReduction takes additional strictness parameter
* RemoveBarriers pass added.

API changes:

* Remove architecture classes :py:class:`TriangularGrid`, :py:class:`HexagonalGrid` and :py:class:`CyclicButterfly`

Fixes:

* Several small bugfixes.

0.9.0 (March 2021)
------------------

Major new features:

* Contextual optimizations based on knowledge of state.

Minor new features:

* New box type ``PhasePolyBox``.
* Refactored PytketConfig. `pytket-qiskit`, `pytket-honeywell`, `pytket-aqt`, `pytket-ionq`, `pytket-qsharp` and `pytket-braket`
  now all have authentication or workspace parameters that can be set in config files.

Fixes:

* Several small bugfixes.

0.8.0 (March 2021)
------------------

API changes:

* All extension modules moved to `pytket.extensions` namespace.

Compatible extension versions:

* ``pytket-aqt``: 0.5.0
* ``pytket-braket``: 0.4.0
* ``pytket-cirq``: 0.8.0
* ``pytket-honeywell``: 0.7.0
* ``pytket-ionq``: 0.3.0
* ``pytket-projectq``: 0.7.0
* ``pytket-pyquil``: 0.8.0
* ``pytket-pyzx``: 0.7.0
* ``pytket-qiskit``: 0.8.0
* ``pytket-qsharp``: 0.9.0
* ``pytket-qulacs``: 0.5.0

0.7.2 (February 2021)
---------------------

Major new features:

* Support for Python 3.9, dropping 3.6.

Fixes:

* Fix memory corruption with symbolic circuits on Windows.

0.7.1 (February 2021)
--------------------------

Minor new features:

* Option to store encrypted Honeywell password (not recommended).
* Automatic retries for Honeywell result retrieval.

Fixes:

* Drop dependency on OpenFermion (conversions work with separate installation).
* Fix reset breaking ``AerBackend`` ``_process_model``.
* Fix ``IBMQEmulatorBackend`` not being initialised with noise model.


Compatible extension versions:

* ``pytket-aqt``: 0.4.0
* ``pytket-braket``: 0.3.0
* ``pytket-cirq``: 0.7.0
* ``pytket-honeywell``: 0.6.1
* ``pytket-ionq``: 0.2.0
* ``pytket-projectq``: 0.6.0
* ``pytket-pyquil``: 0.7.0
* ``pytket-pyzx``: 0.6.0
* ``pytket-qiskit``: 0.7.1
* ``pytket-qsharp``: 0.8.2
* ``pytket-qulacs``: 0.4.0


0.7.0 (February 2021)
--------------------------

Major new features:

* Subsitution of named operations with other operations, boxes or circuits.
* New ability to condition operations on compound (AND, OR, XOR) operations on ``Bit`` and ``BitRegister``,
  which can be compiled with ``DecomposeClassicalExp`` and executed with ``HoneywellBackend``.

Minor new features:

* Direct creation of operator from gate type and parameters (``Op.create``).
* New methods ``Circuit.ops_of_type`` and ``Circuit.commands_of_type``.
* ``KAKDecomposition`` now accepts the estimated CX gate fidelity as parameter
  and performs an approximate decomposition in that case.
* Significant optimisation of SPAM correction methods.
* New GraphColourMethod.Exhaustive added to gen_term_sequence_circuit
  for partitioning Pauli tensors.
* New OpTypes ``CRx`` and ``CRy``.
* New OpTypes ``SX``, ``SXdg``, ``CSX``, ``CSXdg``, ``CV`` and ``CVdg``.
* New ``BasePass.get_config()`` method, which returns the name and parameters
  for a pass.
* New ``SequencePass.get_sequence()`` method, which returns the sequence of passes.
* New ``get_pass()`` method for ``RepeatPass``, ``RepeatWithMetricPass``, ``RepeatUntilSatisfiedPass``.
* New ``get_predicate()`` method for ``RepeatUntilSatisfiedPass``.
* New ``get_metric()`` method for ``RepeatWithMetricPass``.
* New ``backend`` parameter to ``SpamCorrecter`` constructor.

New supported backends:

* Support for Azure Quantum backends in the ``pytket-qsharp`` extension.

New features in extensions:

* Conversion of ``Reset`` and custom gates in ``pytket-qiskit``.
* Support for mid-circuit measurements on IBMQ premium devices via ``pytket-qiskit``.

API changes:

* Removal of "minimise" method for SPAM correction

Compatible extension versions:

* ``pytket-aqt``: 0.4.0
* ``pytket-braket``: 0.3.0
* ``pytket-cirq``: 0.7.0
* ``pytket-honeywell``: 0.6.0
* ``pytket-ionq``: 0.2.0
* ``pytket-projectq``: 0.6.0
* ``pytket-pyquil``: 0.7.0
* ``pytket-pyzx``: 0.6.0
* ``pytket-qiskit``: 0.7.0
* ``pytket-qsharp``: 0.8.0
* ``pytket-qulacs``: 0.4.0

0.6.1 (October 2020)
--------------------

Minor New Features:

* New pass generator ``RenameQubitsPass``

New Supported Backends:

* Devices from IonQ (via separate ``pytket-ionq`` module)

0.6.0 (September 2020)
----------------------

Major New Features:

* Windows support
* Phase-aware circuits
* New box type for applying quantum controls to arbitrary quantum operations
* New ``tailoring`` module containing tools for noise tailoring
* Circuit transpose method
* Optimization levels for default backend compilation passes
* New serialization methods for circuits and results
* New online user manual

Minor New Features:

* New gate type ``OpType.PhasedISWAP``
* Expectations of non-Hermitian operators (when supported by backend)
* Greater control over graph-colouring algorithms
* Improved Clifford simplification
* Retrieval of gate set from ``GateSetPredicate``
* New ``Backend.cancel`` method
* New ``name`` attribute for circuits.
* Backends can be wrapped as Qiskit backends for use in Qiskit software.
* IBMQEmulatorBackend added to emulate IBMQBackend behaviour, with simulator execution.

New supported backends:

* Devices and simulators from Amazon Braket (via separate ``pytket-braket``
  module)
* Qulacs simulator (via separate ``pytket-qulacs`` module)

.. * IonQ devices (via separate ``pytket-ionq`` module)

API changes:

* Retrieval of shots, counts, state and unitary directly from ``ResultHandle``
  is no longer supported: either use ``Backend.get_shots(Circuit)`` or
  ``Backend.get_result(ResultHandle).get_shots()`` (etc).
* ``Backend.default_compilation_pass`` is no longer a property but a method.
* ``QubitMap`` is replaced by a Python dictionary.
* Bit ordering of `condition_value` for conditionals now follows QASM convention
  (opposite to before, now `[0, 1]` corresponds to value 2).

Bugfixes:

* Various small bug fixes

Known issues:

* There is an `issue <https://github.com/CQCL/pytket/issues/24>`_ with the use
  of symbolic circuits on Windows, causing memory access violations in some
  circumstances.

Compatible extension versions:

* ``pytket-aqt``: 0.3.0
* ``pytket-braket``: 0.2.0
* ``pytket-cirq``: 0.5.0
* ``pytket-honeywell``: 0.4.0
* ``pytket-projectq``: 0.5.0
* ``pytket-pyquil``: 0.6.0
* ``pytket-pyzx``: 0.5.0
* ``pytket-qiskit``: 0.6.0
* ``pytket-qsharp``: 0.6.0
* ``pytket-qulacs``: 0.3.0

.. * ``pytket-ionq``: 0.1.0

0.5.7 (August 2020)
-------------------
Number of bugs fixed including:


* ``OpType.Reset`` added to QASM conversion
* Bugfix for ``CnX`` with n=4, n=5
* Correct Node IDS for ``FullyConnected`` Architecture.


0.5.5 (June 2020)
-----------------
Major New Features:

* Redesigned algorithm for ``CliffordSimp``, improving speed and identifying more cases for optimisation

Minor New Features:

* New gates added: ``OpType.Sycamore`` and ``OpType.ISWAPMax``
* New class ``Graph`` for visualising circuit structure

Updates:

* First parameter of ``OpType.FSim`` gate corrected to have range :math:`[0, 2\pi)`
* New ``QubitPauliOperator`` and related classes replace use of OpenFermion's ``QubitOperator``
* Significant optimisation of ``pauli_tensor_matrix`` and ``operator_matrix``


0.5.4 (May 2020)
------------------
Minor New Features:

* Method to generate a circuit from a sequence of ``QubitOperator`` terms

Updates:

* Rename ``measurement`` module to ``partition``

Bugfixes:

* Fix invalid cancellation of certain controlled rotations


0.5.2 (April 2020)
------------------
Major New Features:

* Routing, gate decomposition, and basic optimisations can work around conditional gates and mid-circuit measurements
* New high-level optimisation routine for Trotterised Hamiltonians
* Measurement reduction via Pauli term diagonalisation
* Inspection of the status of circuit execution on asynchronous backends
* Error mitigation facilities via the SPAM method
* Introduction of the :py:class:`Program` class for specifying routines with classical control flow

Minor New Features:

* Improved error messages when circuits cannot be run on a backend
* Generalised :py:meth:`Circuit.depth_by_type` to allow sets of gate types
* A selection of optimisation passes are parameterised by pattern for decomposing into CXs
* New :py:class:`Architecture` subclass, :py:class:`FullyConnected`, added
* New gates added: `OpType.ESWAP` and `OpType.FSim`
* Additional utility methods for permuting qubits of statevectors
* Inspection of any implicit permutations within the :py:class:`Circuit` dag structure
* Inspection of free symbols in a circuit
* Inspection of detailed gate errors from a :py:class:`Device`
* Additional methods for parsing/producing QASM through strings and streams
* Ability to enable internal logs

Updates:

* Cleaner addition of conditions to gates via kwargs
* :py:class:`UnitID` objects are specialised into either :py:class:`Qubit` or :py:class:`Bit` objects, with more natural constructors
* Renamed many passes to give a uniform naming convention
* Getters on :py:class:`Architecture`, :py:class:`Device`, :py:class:`GateError`, and :py:class:`QubitErrorContainer` made into readonly properties
* Backend-specific runtime arguments (e.g. simulator seeds) are now passed in via kwargs
* Stability improvements and bug fixes
* Updated documentation and additional examples
* Stricter namespacing (most classes must be imported from submodules rather than top level)
* Python 3.8 support

Deprecations:

* Calling :py:meth:`get_counts`, :py:meth:`get_shots` or :py:meth:`get_state` on a :py:class:`Backend` object with a :py:class:`Circuit` argument is deprecated in favour of :py:class:`ResultHandle`.

New supported backends:

* AQT devices and simulators (via separate ``pytket_aqt`` module)
* Honeywell devices (via separate ``pytket_honeywell`` module)
* Q# simulators and resource estimator (via separate ``pytket_qsharp`` module)

0.4.1 (December 2019)
---------------------
New Features:

* New classes for placement of logical qubits from :py:class:`Circuit` to physical qubits from :py:class:`Device` or :py:class:`Architecture`
* Data from backends can be returned in either increasing lexicographical order of (qu)bit identifiers (the familiar ordering used in most textbooks) or decreasing order (popular with other quantum software platforms) using the :py:class:`BasisOrder` enum

Updates:

* Updated documentation and additional examples
* OptimiseCliffordsZX pass removed, FullPeepholeOptimise pass added
* New architectures added, including :py:class:`SquareGrid`, :py:class:`HexagonalGrid`, :py:class:`RingArch`, :py:class:`TriangularGrid` and :py:class:`CyclicButterfly`
* Device information from :py:class:`Device` can now be returned
* Stability improvements and bug fixes

0.4.0 (November 2019)
---------------------
New Features:

* Contractural compilation passes with guarantees on how they transform circuits that satisfy their preconditions. This provides a uniform interface for optimisations, routing, and other stages of compilation
* New "Box" gate types for encapsulating high-level structures (arbitrary subcircuits, parameterised composite gate definitions, unitaries, Pauli operators)
* Simpler and more flexible structure for registers and names of qubits/bits, allowing for non-contiguous and multi-dimensional indices (referring to individual units, linear registers, grids, etc.)
* Latex diagram output using Quantikz
* The :py:class:`Device` class to build on top of :py:class:`Architecture` with error and timing information
* Initial and final maps tracked throughout the entire compilation procedure using the :py:class:`CompilationUnit` wrapper
* Import circuits from Quipper source files
* Utility methods for processing data from Backends

Updates:

* All Backends refactored for more consistent interfaces, separation of data processing, and introducing batch circuit processing when possible
* Routing improved to use distributed CX (BRIDGE) gates in addition to SWAP insertion
* Cost function for noise-aware allocation of qubits improved to consider more sources of noise
* :py:class:`Architecture` objects can be specified with arbitrary node names, using the same :py:class:`UnitID` objects and qubits/bits
* Removed the :py:class:`PhysicalCircuit` class in preference of just using :py:class:`Circuit` objects
* Generalised and sped up the gate commutation pass
* Optimisation for redundant gate removal now removes diagonal gates before measurements
* Support for custom gate definitions in QASM input
* Support for a greater fragment of sympy expressions in gate parameters
* Stability improvements and bug fixes
* Updated documentation and additional examples

0.3.0 (August 2019)
-------------------
New Features:

* More options for circuit routing, including noise-aware allocation of qubits
* Basic support for generating circuits with classical conditions and multiple registers
* ForestBackend for running circuits on Rigett's QVM simulators and QCS
* AerUnitaryBackend for inspecting the full unitary of a circuit
* Chaining gate commands
* Primitive QASM<->Circuit (import and export)

Updates:

* Simplified conversions for pytket_qiskit, going straight to/from QuantumCircuit rather than DAGCircuit
* CSWAP gate added

0.2.3 (July 2019)
------------------
New Features:

* Decomposition `Transform` for controlled gates

Updates:

* Exposed additional gate types into Pytket
* Fixed bug in `add_circuit`
* Fixed routing bug
* Made `run` behaviour more sensible for backends

0.2.2 (June 2019)
------------------
Updates:

* Minor bug fixes, examples and documentation

0.2.1 (June 2019)
------------------
Updates:

* Extra support for appending Circuits from Matrices and Exponents
* More docs and examples
* Fixed bugs in backends

0.2.0 (June 2019)
------------------
New Features:

* Support for circuits and simulation using ProjectQ (0.4.2)
* Support for conversion to and from PyZX (https://github.com/Quantomatic/pyzx)
* Interface to many new optimisation passes, allowing for custom passes
* Circuit compilation using symbolic parameters
* New interface to routing
* Enabled noise modeling in the AerBackend module

Updates:

* Qiskit support updated for Qiskit 0.10.1 and Qiskit Chemistry 0.5
* Pytket Chemistry module has been removed, to be part of the separate Eumen package
* Bug fixes and performance improvements to routing

0.1.6 (April 2019)
------------------
Updates:

* Routing can return SWAP gates rather than decomposing to CNOTs
* Decomposition and routing bug fixes

0.1.5 (April 2019)
------------------
New Features:

* Enabled conversions from 4x4 unitary matrices to 2 qubit circuit

0.1.4 (April 2019)
------------------
Updates:

* Bug fix patch for routing and performance improvements

0.1.3 (March 2019)
------------------
Updates:

* Qiskit support updated for Terra 0.7.3, Aqua 0.4.1, and Chemistry 0.4.2
* Bug fixes in routing

0.1.2 (February 2019)
---------------------
New Features:

* Support for circuits from Rigetti pyQuil (2.3)
* New interface for constructing and analysing circuits in pytket directly
* Named classical registers for measurements

Updates:

* Documentation and tutorial improvements
* Bug fixes in routing and optimisations
* Minor API changes for notational consistency

0.1.0 (December 2018)
---------------------
New Features:

* Support for circuits and architectures from IBM Qiskit (0.7)
* ``pytket.qiskit.TketPass`` allows pytket to be plugged in to the Qiskit compilation stack to take advantage of tket's routing and optimisations
* New Chemistry package featuring an implementation of the Quantum Subspace Expansion to work within or alongside Qiskit Aqua (0.4)
* Optimisation passes introduced for powerful circuit rewriting before routing, and safe rewriting after routing

Updates:

* Cirq functionality supports Cirq 0.4
* Refactoring into modules

0.0.1 (July 2018)
-----------------
New Features:

* Support for circuits and architectures from Google Cirq (0.3)
* Routing and placement procedures available for manipulating circuits to satisfy device specifications
