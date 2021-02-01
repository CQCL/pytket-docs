pytket.circuit.OpType
==================================
Enum for available operations compatible with the tket :py:class:`Circuit` class.

.. warning::
    All parametrised OpTypes which take angles (e.g. Rz, CPhase, FSim) expect parameters in multiples of pi (half-turns). 
    This may differ from other quantum programming tools you have used, which have specified angles in radians, or perhaps even degrees.
    Therefore, for instance `circuit.add_gate(OpType.Rx, 1, [0])` is equivalent in terms of the unitary to `circuit.add_gate(OpType.X, [0])`

.. currentmodule:: pytket._tket.circuit.OpType
.. autoclass:: pytket._tket.circuit.OpType
    :members:
