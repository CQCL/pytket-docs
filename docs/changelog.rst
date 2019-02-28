Changelog
==================================

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
* ``pytket.qiskit.TketPass`` allows pytket to be plugged in to the Qiskit compilation stack to take advantage of :math:`\mathrm{t|ket}\rangle`'s routing and optimisations
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