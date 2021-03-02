pytket extensions
=================

.. image:: CQCLogo.png
   :width: 120px
   :align: right


``pytket extensions`` enables `CQC`_ ``pytket`` to be used in conjunction with other platforms.
Each one of these adds either some new
methods to the ``pytket`` package to convert between the circuit
representations, or some new backends to submit circuits to within ``pytket``.


For each extension module:

Qiskit: ``pip install pytket-qiskit``

Cirq: ``pip install pytket-cirq``

PyQuil: ``pip install pytket-pyquil``

ProjectQ: ``pip install pytket-projectq``

AQT: ``pip install pytket-aqt``

Honeywell: ``pip install pytket-honeywell``

Braket: ``pip install pytket-braket``

QSharp: ``pip install pytket-qsharp``

PyZX: ``pip install pytket-pyzx``

Qulacs: ``pip install pytket-qulacs``

IonQ: ``pip install pytket-ionq``

How to cite
~~~~~~~~~~~

If you wish to cite tket in any academic publications, we generally recommend citing our `software overview paper <https://doi.org/10.1088/2058-9565/ab8e92>`_ for most cases.

If your work is on the topic of specific compilation tasks, it may be more appropriate to cite one of our other papers:

- `"On the qubit routing problem" <https://doi.org/10.4230/LIPIcs.TQC.2019.5>`_ for qubit placement (aka allocation, mapping) and routing (aka swap network insertion, connectivity solving).
- `"Phase Gadget Synthesis for Shallow Circuits" <https://doi.org/10.4204/EPTCS.318.13>`_ for representing exponentiated Pauli operators in the ZX calculus and their circuit decompositions.
- `"A Generic Compilation Strategy for the Unitary Coupled Cluster Ansatz" <https://arxiv.org/abs/2007.10515>`_ for sequencing of terms in Trotterisation and Pauli diagonalisation.

We are also keen for others to benchmark their compilation techniques against us. We recommend checking our `benchmark repository <https://github.com/CQCL/tket_benchmarking>`_ for examples on how to run basic benchmarks with the latest version of ``pytket``. Please list the release version of ``pytket`` with any benchmarks you give, and feel free to get in touch for any assistance needed in setting up fair and representative tests.


.. _pytket documentation: https://cqcl.github.io/pytket/build/html/index.html
.. _CQC: https://cambridgequantum.com


.. toctree::
    :caption: API reference:
    :maxdepth: 2

    aqt.rst
    braket.rst
    cirq.rst
    honeywell.rst
    projectq.rst
    pyquil.rst
    pyzx.rst
    qiskit.rst
    qsharp.rst
    qulacs.rst
    ionq.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
