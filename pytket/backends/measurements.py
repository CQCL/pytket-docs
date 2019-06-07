# Copyright 2019 Cambridge Quantum Computing
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np
from typing import Iterable, Tuple
from pytket import Circuit

def pauli_measurement(pauli_string:Iterable[Tuple[int,str]], circ:Circuit) :
    """
    Appends measurement instructions to a given circuit, measuring each qubit in a given basis
    """
    measured_qbs = []
    for qb_idx, p in pauli_string:
        measured_qbs.append(qb_idx)
        if p=='X':
            circ.H(qb_idx)
        elif p=='Y':
            circ.Sdg(qb_idx)
            circ.H(qb_idx)

    for idx in measured_qbs:
        circ.Measure(idx)


def bin_str_2_table(strings:Iterable[str]) -> np.ndarray:
    # infer number of qubits from first space separated bit string
    n_qubits = int((len(strings[0])-1)/2) + 1
    output = np.zeros((len(strings), n_qubits), dtype=int)

    for index, string in enumerate(strings):
        output[index] = np.fromstring(string, dtype=int, sep=' ')
    output = np.fliplr(output)
    return output