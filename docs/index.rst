Getting Started
===============


.. jupyter-execute::

    from pytket import Circuit

    ghz_circ = Circuit(3)
    ghz_circ.H(0)
    ghz_circ.CX(0, 1)
    ghz_circ.CX(1, 2)
    ghz_circ.add_barrier(ghz_circ.qubits)
    ghz_circ.measure_all()



.. toctree::
    :caption: Manual
    :maxdepth: 2

    manual/manual_intro.rst
    manual/manual_circuit.rst
    manual/manual_backend.rst
    manual/manual_compiler.rst
    manual/manual_noise.rst
    manual/manual_assertion.rst
    manual/manual_zx.rst

.. toctree::
    :caption: Examples
    :maxdepth: 2

    examples/ansatz_sequence_example
    examples/circuit_analysis_example
    examples/circuit_generation_example
    examples/compilation_example
    examples/conditional_gate_example
    examples/contextual_optimization
    examples/creating_backends
    examples/measurement_reduction_example
    examples/mapping_example
    examples/symbolics_example
    examples/phase_estimation
    examples/pytket-qujax_qaoa
    examples/ucc_vqe



