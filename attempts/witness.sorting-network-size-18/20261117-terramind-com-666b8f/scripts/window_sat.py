"""Window re-synthesis by SAT for the 18-input, 77-gate record network.

For a window [s, s+w) of the record's gate sequence: keep gates [0, s) as a prefix and gates [s+w, 77) as a suffix,
and ask CaDiCaL whether some sequence of w-1 gates in the window position makes prefix + window + suffix a sorter.
Counterexample-guided: the SAT instance only sees a growing subset of the distinct 0-1 vectors that leave the prefix;
after each SAT answer the candidate is run on all of them and failing vectors are added.
UNSAT is a real negative result ("no (w-1)-gate replacement of this window").

usage: window_sat.py baseline.json s w [timeout_s] -> prints a JSON line with the outcome.
"""
import json, sys, time, itertools, random
import numpy as np
from pysat.solvers import Cadical153

N = 18
PAIRS = [(i, j) for i in range(N) for j in range(i + 1, N)]


def apply(vec, gates):
    # vec: (m, N) uint8
    v = vec.copy()
    for i, j in gates:
        a, b = v[:, i].copy(), v[:, j].copy()
        v[:, i] = a & b
        v[:, j] = a | b
    return v


def all_inputs():
    x = np.arange(1 << N, dtype=np.uint32)
    return ((x[:, None] >> np.arange(N, dtype=np.uint32)) & 1).astype(np.uint8)


def unsorted(v):
    return (v[:, :-1] > v[:, 1:]).any(axis=1)


def solve_window(gates, s, w, timeout, seed=0, target=None):
    t0 = time.time()
    pre, win, suf = gates[:s], gates[s:s + w], gates[s + w:]
    T = (w - 1) if target is None else target
    P = np.unique(apply(all_inputs(), pre), axis=0)
    rng = random.Random(seed)
    solver = Cadical153()
    nv = [0]

    def new():
        nv[0] += 1
        return nv[0]

    g = [[new() for _ in PAIRS] for _ in range(T)]  # gate choice per step
    for t in range(T):
        solver.add_clause(g[t])
        for a, b in itertools.combinations(g[t], 2):
            solver.add_clause([-a, -b])
    # untouched[t][wire]: no chosen gate touches the wire at step t
    unt = [[new() for _ in range(N)] for _ in range(T)]
    for t in range(T):
        for wi in range(N):
            touching = [g[t][k] for k, (i, j) in enumerate(PAIRS) if i == wi or j == wi]
            solver.add_clause([unt[t][wi]] + touching)
            for x in touching:
                solver.add_clause([-unt[t][wi], -x])
    # a gate is useless right after the same gate (symmetry break)
    for t in range(T - 1):
        for k in range(len(PAIRS)):
            solver.add_clause([-g[t][k], -g[t + 1][k]])

    added = set()

    def add_vector(vec):
        key = vec.tobytes()
        if key in added:
            return
        added.add(key)
        cur = [new() for _ in range(N)]
        for wi in range(N):
            solver.add_clause([cur[wi] if vec[wi] else -cur[wi]])
        for t in range(T):
            nxt = [new() for _ in range(N)]
            for wi in range(N):
                solver.add_clause([-unt[t][wi], -cur[wi], nxt[wi]])
                solver.add_clause([-unt[t][wi], cur[wi], -nxt[wi]])
            for k, (i, j) in enumerate(PAIRS):
                gk = g[t][k]
                xi, xj, yi, yj = cur[i], cur[j], nxt[i], nxt[j]
                solver.add_clause([-gk, xi, -yi])
                solver.add_clause([-gk, xj, -yi])
                solver.add_clause([-gk, -xi, -xj, yi])
                solver.add_clause([-gk, -xi, yj])
                solver.add_clause([-gk, -xj, yj])
                solver.add_clause([-gk, xi, xj, -yj])
            cur = nxt
        for i, j in suf:
            a, b = cur[i], cur[j]
            lo, hi = new(), new()
            solver.add_clause([-lo, a]); solver.add_clause([-lo, b]); solver.add_clause([lo, -a, -b])
            solver.add_clause([-hi, a, b]); solver.add_clause([hi, -a]); solver.add_clause([hi, -b])
            cur[i], cur[j] = lo, hi
        for wi in range(N - 1):
            solver.add_clause([-cur[wi], cur[wi + 1]])

    idx = list(range(len(P)))
    rng.shuffle(idx)
    # seed set: vectors that the suffix alone does not sort after the window gates are removed
    bad0 = unsorted(apply(P, suf))
    seeds = [i for i in idx if bad0[i]][:60] + idx[:40]
    for i in seeds:
        add_vector(P[i])
    rounds = 0
    out = dict(s=s, w=w, T=T, prefix_vectors=int(len(P)))
    while True:
        rounds += 1
        if time.time() - t0 > timeout:
            out.update(result="timeout", rounds=rounds, vectors=len(added), secs=round(time.time() - t0, 1))
            return out, None
        r = solver.solve()  # hard wall-clock limit is enforced by the caller killing the process
        if r is False:
            out.update(result="UNSAT", rounds=rounds, vectors=len(added), secs=round(time.time() - t0, 1))
            return out, None
        model = set(l for l in solver.get_model() if l > 0)
        newwin = [PAIRS[k] for t in range(T) for k in range(len(PAIRS)) if g[t][k] in model]
        res = apply(P, newwin + suf)
        bad = np.nonzero(unsorted(res))[0]
        if len(bad) == 0:
            full = pre + newwin + suf
            out.update(result="SAT", rounds=rounds, vectors=len(added), secs=round(time.time() - t0, 1))
            return out, full
        pick = list(bad)
        rng.shuffle(pick)
        for i in pick[:30]:
            add_vector(P[i])


if __name__ == "__main__":
    base = json.load(open(sys.argv[1]))["comparators"]
    gates = [tuple(x) for x in base]
    s, w = int(sys.argv[2]), int(sys.argv[3])
    timeout = float(sys.argv[4]) if len(sys.argv) > 4 else 600
    out, full = solve_window(gates, s, w, timeout)
    print(json.dumps(out), flush=True)
    if full is not None:
        name = f"found_s{s}_w{w}.json"
        json.dump({"comparators": [list(x) for x in full]}, open(name, "w"))
        print("WROTE", name, len(full), flush=True)
