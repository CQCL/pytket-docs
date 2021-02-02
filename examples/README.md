# pytket Examples

Here you can find notebooks showing features and example usage of `pytket`. We
recommend that you clone the repo and open the examples in Jupyter (and play
around with them) yourself.

You can also run all the examples below, and try out all pytket code (including extensions) in your
browser using Binder:  [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/CQCL/pytket/master?filepath=examples)

## Feature Examples

[circuit_analysis_example](https://github.com/CQCL/pytket/blob/master/examples/circuit_analysis_example.ipynb) -
Basic methods of analysis and visualisation of circuits.

[circuit_generation_example](https://github.com/CQCL/pytket/blob/master/examples/circuit_generation_example.ipynb) -
More advanced methods of circuit generation.

[symbolics_example](https://github.com/CQCL/pytket/blob/master/examples/symbolics_example.ipynb) -
Constructing and using circuits with symbolic parameters.

[compilation_example](https://github.com/CQCL/pytket/blob/master/examples/compilation_example.ipynb) -
Compilation passes and how to combine and apply them.

[backends_example](https://github.com/CQCL/pytket/blob/master/examples/backends_example.ipynb) -
How to run circuits on different backends.

[comparing_simulators](https://github.com/CQCL/pytket/blob/master/examples/comparing_simulators.ipynb) -
An overview of the differences between each of the simulators supported by `pytket`.

[routing_example](https://github.com/CQCL/pytket/blob/master/examples/routing_example.ipynb) -
An introduction to routing, using Cirq to construct examples.

[conditional_gate_example](https://github.com/CQCL/pytket/blob/master/examples/conditional_gate_example.ipynb) -
Mid-circuit measurements and classical control.

[expectation_value_example](https://github.com/CQCL/pytket/blob/master/examples/expectation_value_example.ipynb) -
Computing expectation values of Hamiltonians.

[measurement_reduction_example](https://github.com/CQCL/pytket/blob/master/examples/measurement_reduction_example.ipynb)
- Advanced methods for reducing the number of circuits required for
measurement.

[ansatz_sequence_example](https://github.com/CQCL/pytket/blob/master/examples/ansatz_sequence_example.ipynb) - Advanced methods for synthesising an ansatz circuit from Trotterised Hamiltonians.

[spam_example](https://github.com/CQCL/pytket/blob/master/examples/spam_example.ipynb) -
Calibration and correction of state preparation and measurement in the presence of noise.

[creating_backends](https://github.com/CQCL/pytket/blob/master/examples/creating_backends.ipynb) - How to write your own pytket backend.

## Use-case Examples

[ucc_vqe](https://github.com/CQCL/pytket/blob/master/examples/ucc_vqe.ipynb) -
Exploring features to help code an efficient implementation of the Variational Quantum Eigensolver using the Unitary Coupled Cluster method for electronic structure.

[entanglement_swapping](https://github.com/CQCL/pytket/blob/master/examples/entanglement_swapping.ipynb) -
Using tomography to analyse the effect of noise channels when iterating the Entanglement Swapping protocol.

[Forest_portability_example](https://github.com/CQCL/pytket/blob/master/examples/Forest_portability_example.ipynb) -
Examples illustrating portability between different backends.

[qiskit_integration](https://github.com/CQCL/pytket/blob/master/examples/qiskit_integration.ipynb) - Wrapping a pytket backend as a qiskit backend.
