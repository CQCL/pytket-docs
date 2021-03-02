pytket-qiskit
==================================

IBM's `Qiskit <https://qiskit.org>`_ is an open-source framework for quantum
computation, ranging from high-level algorithms to low-level circuit
representations, simulation and access to the `IBMQ <https://www.research.ibm.com/ibm-q/>`_ Experience devices.

``pytket-qiskit`` is an extension to ``pytket`` that allows ``pytket`` circuits to be
run on IBM backends and simulators, as well as conversion to and from Qiskit
representations.

``pytket-qiskit`` is available for Python 3.7, 3.8 and 3.9, on Linux, MacOS and Windows. To
install, run:

``pip install pytket-qiskit``

pytket.extensions.qiskit
~~~~~~~~~~~~~~~~~~~~~~~~

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
