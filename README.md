# pytket-docs

[![Slack](https://img.shields.io/badge/Slack-4A154B?style=for-the-badge&logo=slack&logoColor=white)](https://tketusers.slack.com/join/shared_invite/zt-18qmsamj9-UqQFVdkRzxnXCcKtcarLRA#/shared-invite/email)
[![PyPI version](https://badge.fury.io/py/pytket.svg)](https://badge.fury.io/py/pytket)

Pytket is a python module for interfacing with tket, a quantum computing toolkit and optimising compiler developed by Quantinuum.

This repository contains the pytket user manual and example notebooks content in the `docs` directory. It does not contain source code for pytket itself. The source code is maintained on the [tket repository](https://github.com/CQCL/tket).

The manual and examples are built and deployed as html pages using the [myst-nb](https://myst-nb.readthedocs.io/en/latest/) library. Instructions on building the docs locally can be found [here](https://github.com/CQCL/pytket-docs/blob/main/docs/README.md).

Note that the TKET website is not deployed from this repository. This repository just contains the content for the documentation.
 

## Getting started

Pytket is available for Python 3.10, 3.11 and 3.12 on Linux, MacOS and Windows.
To install, run:

```shell
pip install pytket
```

API documentation can be found at https://docs.quantinuum.com/tket/api-docs.


## Maintenance and support

If you think you've found a bug or have an idea for a feature then please raise an issue [here](https://github.com/CQCL/tket/issues).

There is also a slack channel for discussion and support. click [here](https://tketusers.slack.com/join/shared_invite/zt-18qmsamj9-UqQFVdkRzxnXCcKtcarLRA#/shared-invite/email) to join.

### Pytket 0.x.y

Pytket underwent rapid development from 2018 to 2022, with frequent changes of
API. Our policy has been to maintain only the latest 0.x relase, and not to port
bugfixes to older releases. Since version 0.7 (February 2021) we have been
releasing new versions (0.x.0) on a 4-week cycle, with occasional patch releases
(0.x.y) for important hotfixes.

### Pytket 1.x.y

With the release of pytket 1.0 in early 2022, we are moving to a different
process, to facilitate long-term stability. Following the [semver](https://semver.org/)
conventions, we will not introduce incompatible API changes in the 1.x.y series;
the minor version (x) will be incremented whenever new functionality is
introduced; and the patch version (y) will be incremented for bug fixes.

Pytket 1 will be maintained according to this policy for at least a year
following the release of pytket 2.0. There will be no further maintenance of
0.x.y versions.

### Pytket 2.x.y

Development work on pytket 2 will begin soon after the release of pytket 1.0.
This will have a different API. Only pre-release versions will be uploaded to
pypi until the API has stabilized enough to make a 2.0 release. Thereafter we
will continue according to the same policy as for pytket 1.x.y.

## How to cite

If you wish to cite tket in any academic publications, we generally recommend citing our [software overview paper](https://doi.org/10.1088/2058-9565/ab8e92) for most cases.

If your work is on the topic of specific compilation tasks, it may be more appropriate to cite one of our other papers:

- ["On the qubit routing problem"](https://doi.org/10.4230/LIPIcs.TQC.2019.5) for qubit placement (a.k.a. allocation) and routing (a.k.a. swap network insertion, connectivity solving).
- ["Phase Gadget Synthesis for Shallow Circuits"](https://doi.org/10.4204/EPTCS.318.13) for representing exponentiated Pauli operators in the ZX calculus and their circuit decompositions.
- ["A Generic Compilation Strategy for the Unitary Coupled Cluster Ansatz"](https://arxiv.org/abs/2007.10515) for sequencing of terms in Trotterisation and Pauli diagonalisation.

We are also keen for others to benchmark their compilation techniques against us. We recommend checking our [benchmark repository](https://github.com/CQCL/tket_benchmarking) for examples on how to run basic benchmarks with the latest version of pytket. Please list the release version of pytket with any benchmarks you give, and feel free to get in touch for any assistance needed in setting up fair and representative tests.
