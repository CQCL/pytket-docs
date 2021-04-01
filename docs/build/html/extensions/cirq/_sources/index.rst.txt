pytket-cirq
==================================

.. image:: CQCLogo.png
   :width: 120px
   :align: right

`Cirq <https://www.github.com/quantumlib/cirq>`_ is a python library for producing
quantum circuits and running them on simulators and physical quantum devices.

``pytket-cirq`` is an extension to ``pytket`` that allows conversion to and from
Cirq representations.

``pytket-cirq`` is available for Python 3.7, 3.8 and 3.9, on Linux, MacOS and Windows.
To install, run:

``pip install pytket-cirq``

pytket.extensions.cirq
~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: pytket.extensions.cirq
    :members: cirq_to_tk, tk_to_cirq, process_characterisation

.. autoclass:: pytket.extensions.cirq.CirqStateSampleBackend
    :inherited-members:
    :members:

.. autoclass:: pytket.extensions.cirq.CirqDensityMatrixSampleBackend
    :inherited-members:
    :members:

.. autoclass:: pytket.extensions.cirq.CirqCliffordSampleBackend
    :inherited-members:
    :members:

.. autoclass:: pytket.extensions.cirq.CirqStateSimBackend
    :inherited-members:
    :members:

.. autoclass:: pytket.extensions.cirq.CirqDensityMatrixSimBackend
    :inherited-members:
    :members:

.. autoclass:: pytket.extensions.cirq.CirqCliffordSimBackend
    :inherited-members:
    :members:
