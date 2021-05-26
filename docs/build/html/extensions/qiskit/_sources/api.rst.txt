API documentation
~~~~~~~~~~~~~~~~~

.. autoclass:: pytket.extensions.qiskit.IBMQBackend
    :special-members:
    :members:

.. autoclass:: pytket.extensions.qiskit.IBMQEmulatorBackend
    :special-members: __init__
    :members:

.. autoclass:: pytket.extensions.qiskit.AerBackend
    :special-members: __init__
    :inherited-members:
    :members:
    :exclude-members: get_state, get_unitary

.. autoclass:: pytket.extensions.qiskit.AerStateBackend
    :special-members: __init__
    :inherited-members:
    :members:
    :exclude-members: get_counts, get_shots, get_unitary

.. autoclass:: pytket.extensions.qiskit.AerUnitaryBackend
    :special-members: __init__
    :inherited-members:
    :members:
    :exclude-members: get_counts, get_shots, get_state

.. automodule:: pytket.extensions.qiskit
    :members: qiskit_to_tk, tk_to_qiskit, process_characterisation

.. automodule:: pytket.extensions.qiskit.tket_backend
    :members:
    :special-members: __init__


.. automodule:: pytket.extensions.qiskit.tket_pass
    :special-members: __init__
    :members:

.. automodule:: pytket.extensions.qiskit.tket_job
    :special-members: __init__
    :members:

.. automodule:: pytket.extensions.qiskit.backends.config
    :members:
