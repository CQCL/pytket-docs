Changelog
~~~~~~~~~

0.15.0 (June 2021)
------------------

* Updated pytket version requirement to 0.12.

0.14.0 (unreleased)
-------------------

* Qiskit version updated to 0.27.

0.13.0 (May 2021)
-----------------

* Updated pytket version requirement to 0.11.

0.12.0 (unreleased)
-------------------

* Qiskit version updated to 0.26.
* Code rewrites to avoid use of deprecated qiskit methods.
* Restriction to hermitian operators for expectation values in `AerBackend`.

0.11.0 (May 2021)
-----------------

* Contextual optimisation added to default compilation passes (except at optimisation level 0).
* Support for symbolic parameters in rebase pass.
* Correct phase when rebasing.
* Ability to preserve UUIDs of qiskit symbolic parameters when converting.
* Correction to error message.

0.10.0 (April 2021)
-------------------

* Support for symbolic phase in converters.
