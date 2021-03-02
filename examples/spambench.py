### Script for benchmarking different SPAM correction methods.

from collections import Counter
from random import seed, random, randrange
from time import perf_counter
from pytket.circuit import Node
from pytket.utils.spam import SpamCorrecter


def fake_counts(n_qbs, n_shots):
    """ Uniformly random results """
    counts = Counter()
    for i in range(n_shots):
        readout = tuple(randrange(2) for _ in range(n_qbs))
        counts[readout] += 1
    return dict(counts)


def prep_state_to_readout(n_qbs, prep_state):
    l = [0] * n_qbs
    for nodes, vals in prep_state.items():
        assert len(nodes) == len(vals)
        for i, node in enumerate(nodes):
            l[node.index[0]] = vals[i]
    return tuple(l)


def maybe_flipped(x, p):
    if random() < p:
        return x
    else:
        return 1 - x


def fake_cal_counts(n_qbs, ideal_readout, p, n_shots):
    counts = Counter()
    for _ in range(n_shots):
        readout = tuple(maybe_flipped(ideal_readout[i], p) for i in range(n_qbs))
        counts[readout] += 1
    return dict(counts)


def fake_calib_results(part, prep_states, p=0.9, n_shots=1000):
    print("Generating fake calibration results...")
    n_qbs = sum(part)
    ideal_readouts = [
        prep_state_to_readout(n_qbs, prep_state) for prep_state in prep_states
    ]
    results = [
        fake_cal_counts(n_qbs, ideal_readout, p, n_shots)
        for ideal_readout in ideal_readouts
    ]
    print("Generated fake calibration results.")
    return results


def benchmark(part, methods, p=0.9, n_shots=1000, randseed=None):
    """
    Benchmark different count-correction methods with qubits partitioned into groups.

    part: list of positive integers, representing partition of qubits
    p: probability of any bit having its expected value when generating fake calibration results
    """
    print(
        f"Benchmarking with partition {part}, simulation fidelity {p}, {n_shots} shots, random seed = {randseed}"
    )
    seed(randseed)
    n_qbs = sum(part)
    subs = []
    i = 0
    for x in part:
        subs.append([Node("x", j) for j in range(i, i + x)])
        i += x
    spam = SpamCorrecter(subs)
    calib_circs = spam.calibration_circuits()
    calib_results = fake_calib_results(part, spam._prepared_states, p, n_shots)
    spam.calculate_matrices(calib_results)
    my_result = fake_counts(n_qbs, n_shots)
    res_map = {Node("x", i): i for i in range(n_qbs)}
    for method in methods:
        print(f"Method '{method}'...")
        t0 = perf_counter()
        spam.correct_counts(my_result, res_map, method=method)
        t1 = perf_counter()
        print(f"Time: {t1-t0} s")
        print()
    print()


benchmark(
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ["invert", "bayesian"],
    randseed=0,
)
benchmark(
    [2, 2, 2, 2, 2, 1],
    ["invert", "bayesian"],
    randseed=0,
)
benchmark(
    [3, 3, 3, 2],
    ["invert", "bayesian"],
    randseed=0,
)
benchmark(
    [4, 4, 3],
    ["invert", "bayesian"],
    randseed=0,
)
benchmark(
    [5, 5, 1],
    ["invert", "bayesian"],
    randseed=0,
)
benchmark(
    [6, 5],
    ["invert", "bayesian"],
    randseed=0,
)
benchmark(
    [7, 4],
    ["invert", "bayesian"],
    randseed=0,
)
benchmark(
    [8, 3],
    ["invert", "bayesian"],
    randseed=0,
)
benchmark(
    [9, 2],
    ["invert", "bayesian"],
    randseed=0,
)
benchmark(
    [10, 1],
    ["invert", "bayesian"],
    randseed=0,
)
benchmark(
    [11],
    ["invert", "bayesian"],
    randseed=0,
)
