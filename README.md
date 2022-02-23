# pytket

[![PyPI version](https://badge.fury.io/py/pytket.svg)](https://badge.fury.io/py/pytket)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/CQCL/pytket/main?filepath=examples)

Pytket is a python module for interfacing with CQC tket, a set of quantum programming tools.

This repository contains API documentation and example notebooks to get you started using pytket. It does not contain source code. The source code is maintained on the [tket repository](https://github.com/CQCL/tket).

## Getting started

Pytket is available for Python 3.8, 3.9 and 3.10, on Linux, MacOS and Windows.
To install, run:

``pip install pytket``

See the [Getting Started](https://cqcl.github.io/tket/pytket/api/getting_started.html) page for a quick introduction to using pytket.

API documentation can be found at [cqcl.github.io/tket/pytket](https://cqcl.github.io/tket/pytket/api).

To get more in depth on features, see the [manual](https://cqcl.github.io/pytket/manual/) and [examples](https://github.com/CQCL/pytket/tree/main/examples).

## Interfaces

It is easy to use pytket as a front-end for interacting with third-party devices
and software. We maintain a large and growing number of extensions on the
[pytket-extensions repository](https://github.com/CQCL/pytket-extensions). These are simple to install with `pip`.

## Maintenance and support

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

- ["On the qubit routing problem"](https://doi.org/10.4230/LIPIcs.TQC.2019.5) for qubit placement (a.k.a. allocation, mapping) and routing (a.k.a. swap network insertion, connectivity solving).
- ["Phase Gadget Synthesis for Shallow Circuits"](https://doi.org/10.4204/EPTCS.318.13) for representing exponentiated Pauli operators in the ZX calculus and their circuit decompositions.
- ["A Generic Compilation Strategy for the Unitary Coupled Cluster Ansatz"](https://arxiv.org/abs/2007.10515) for sequencing of terms in Trotterisation and Pauli diagonalisation.

We are also keen for others to benchmark their compilation techniques against us. We recommend checking our [benchmark repository](https://github.com/CQCL/tket_benchmarking) for examples on how to run basic benchmarks with the latest version of pytket. Please list the release version of pytket with any benchmarks you give, and feel free to get in touch for any assistance needed in setting up fair and representative tests.


## Telemetry

Pytket features a telemetry module which can be used to keep track of pyktet usage and will provide usage analytics and error reporting at a later date. Telemetry is disabled by default, but may be enabled either through function calls or in the pytket configuration file.

In order to opt in to telemetry, a helper function is provided in the `pytket.telemetry` module. This function need only be run once:

```python
from pytket import telemetry
telemetry.opt_in()
```

Similarly the `opt_out` function will allow a user to opt out.

Alternatively the configuration file located either at `$HOME/.config/pytket/config.json` or `$XDG_CONFIG_HOME/pytket/config.json` if `$XDG_CONFIG_HOME` is set can be edited manually.

Once a user has opted in to telemetry they will be assigned a telemetry ID by making an HTTP request to a CQC server with some information about their system.

### Data policy

Our telemetry data policy can be viewed [here](https://cqcl.github.io/tket/pytket/api/telemetry_data_policy.html).
