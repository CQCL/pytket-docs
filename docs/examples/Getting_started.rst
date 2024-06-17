Getting Started 
===============

.. toctree::
    :caption: Example Notebooks:
    :maxdepth: 2

    ansatz_sequence_example
    circuit_analysis_example
    circuit_generation_example
    compilation_example
    conditional_gate_example
    contextual_optimization
    creating_backends
    measurement_reduction_example
    mapping_example
    symbolics_example
    phase_estimation
    pytket-qujax_qaoa
    ucc_vqe
    CONTRIBUTING.md





.. jupyter-execute::

    from pytket import Circuit

    ghz_circ = Circuit(3)
    ghz_circ.H(0)
    ghz_circ.CX(0, 1)
    ghz_circ.CX(1, 2)
    ghz_circ.add_barrier(ghz_circ.qubits)
    ghz_circ.measure_all()