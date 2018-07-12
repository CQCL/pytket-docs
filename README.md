# pytket
Pytket is a python module for interfacing with CQC t|ket> a set of quantum programming tools. 
Currently implemented are methods to convert between cirq circuits and t|ket> QCommands, and an interface to the qubit routing algorithm. 

## Getting Started
[Pending upload to pypi]<br>
Requires python3.6, tested on macos 10.13.6 and Ubuntu 18.04. <br>
First install [cirq](https://www.github.com/quantumlib/cirq), then run <br>
```pip install pytket```

See [examples/routing_example.ipynb](https://github.com/CQCL/pytket/blob/master/examples/routing_example.ipynb)) a quick introduction. The currently supported cirq operations are: 

* `H`
* `X`
* `Y`
* `Z`
* `S`
* `T`
* `CNOT`
* `RotXGate`
* `RotYGate`
* `RotZGate`
* `measure`
