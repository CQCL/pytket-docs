Changelog
~~~~~~~~~

0.18.0 (September 2021)
-----------------------

* Qiskit version updated to 0.30.
* Updated pytket version requirement to 0.15.

0.17.0 (September 2021)
-----------------------

* Updated pytket version requirement to 0.14.

0.16.1 (July 2021)
------------------

* Fix slow/high memory use :py:meth:`AerBackend.get_operator_expectation_value`

0.16.0 (July 2021)
------------------

* Qiskit version updated to 0.28.
* Use provider API client to check job status without retrieving job in IBMQBackend.
* Updated pytket version requirement to 0.13.

0.15.1 (July 2021)
------------------

* Fixed bug in backends when n_shots argument was passed as list.

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
