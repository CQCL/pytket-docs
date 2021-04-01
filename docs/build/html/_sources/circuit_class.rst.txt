pytket.circuit.Circuit
==================================
:py:class:`Circuit` objects provide an abstraction of quantum circuits. They consist of a set of qubits/quantum wires and a collection of operations applied to them in a given order. These wires have open inputs and outputs, rather than assuming any fixed input state.

See the
`Pytket User Manual <https://cqcl.github.io/pytket/build/html/manual/index.html>`_
for a step-by-step tutorial on constructing circuits.

Many of the :py:class:`Circuit` methods described below append a gate or box to
the end of the circuit. Where ``kwargs`` are indicated in these methods, the
following keyword arguments are supported:

- ``opgroup`` (:py:class:`str`): name of the associated operation group, if any
- ``condition`` (:py:class:`Bit`, :py:class:`BitLogicExp` or :py:class:`ConstPredicate`): classical condition for applying operation
- ``condition_bits`` (list of :py:class:`Bit`): classical bits on which to condition operation
- ``condition_value`` (:py:class:`int`): required value of condition bits (little-endian), defaulting to all-1s if not specified

(Thus there are two ways to express classical conditions: either using a general
``condition``, or using the pair ``condition_bits`` and ``condition_value`` to
condition on a specified set of bit values.)

.. currentmodule:: pytket._tket.circuit.Circuit
.. autoclass:: pytket._tket.circuit.Circuit
   :special-members:
   :members:
