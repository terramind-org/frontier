"""Program search around the FunSearch priority function, plus product starting points.

Part 1: the FunSearch greedy builder (add the highest-priority point that keeps the cap property) run with
parameterised variants of the published n=8 priority function and with other priority families; every
resulting cap is kept, the best few distinct ones are saved for the exchange search (lns.py).
Part 2: product caps (cap in F_3^a x cap in F_3^b) from caps found by CP-SAT in F_3^2..F_3^6, completed greedily.

usage: greedy.py outdir seed minutes_part1 minutes_part2
"""
import sys, os, time, random, itertools
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from capcore import *
from ortools.sat.python import cp_model

outdir, seed, m1, m2 = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
os.makedirs(outdir, exist_ok=True)
rng = random.Random(seed); nrng = np.random.default_rng(seed)
T = third_table()
t0 = time.time()
log = open(os.path.join(outdir, f"greedy_{seed}.log"), "a")


def say(*a):
    s = f"[{time.time()-t0:7.1f}s] " + " ".join(str(x) for x in a)
    print(s, flush=True); log.write(s + "\n"); log.flush()


def greedy(prio, start=()):
    """FunSearch builder: repeatedly add the max-priority unblocked point."""
    pr = np.array(prio, dtype=np.float64).copy()
    cap = []
    for p in start:
        pr[T[p, cap]] = -np.inf if cap else pr[T[p, cap]]
        pr[p] = -np.inf; cap.append(p)
    while True:
        i = int(np.argmax(pr))
        if pr[i] == -np.inf:
            break
        if cap:
            pr[T[i, cap]] = -np.inf
        pr[i] = -np.inf
        cap.append(i)
    return cap


def funsearch_priority(el, n, P):
    """The published FunSearch n=8 priority function with its constants exposed as P."""
    score = n
    in_el = 0
    el_count = el.count(0)
    if el_count == 0:
        score += n ** P["sq"]
        for d in (1, 2, 3):
            if el[d] == el[-d]:
                score *= P["r0"]
    else:
        if el[1] == el[-1]:
            score *= P["r1"]
        if el[2] == el[-2]:
            score *= P["r1"]
    for e in el:
        if e == 0:
            if in_el == 0:
                score *= n * P["z0"]
            elif in_el == el_count - 1:
                score *= P["zl"]
            else:
                score *= n * P["zm"] ** in_el
            in_el += 1
        else:
            score += P["nz"]
    if el[1] == el[-1]:
        score *= P["r2"]
    if el[2] == el[-2]:
        score *= P["r2"]
    return score


BASE = dict(sq=2.0, r0=1.5, r1=0.5, z0=0.5, zl=0.5, zm=0.5, nz=1.0, r2=1.5)
TUP = [tuple(int(x) for x in v) for v in VEC]


def fs_prio(P, perm=None):
    if perm is None:
        return np.array([funsearch_priority(t, N, P) for t in TUP])
    return np.array([funsearch_priority(tuple(t[j] for j in perm), N, P) for t in TUP])


results = {}  # frozenset -> (size, label)


def record(cap, label):
    key = frozenset(cap)
    if key not in results:
        results[key] = (len(cap), label)
    return len(cap)


# --- Part 1: priority variants ---
p0 = fs_prio(BASE)
c = greedy(p0); say("published priority ->", len(c), "cap ok", is_cap(c)); record(c, "published")
# tie-break noise on the published priority
for eps in (1e-9, 1e-3, 1e-2, 0.1, 0.5):
    for r in range(5):
        c = greedy(p0 + eps * np.abs(p0).max() * nrng.random(M)); record(c, f"published+noise{eps}")
    say(f"noise eps={eps}: sizes", sorted({v[0] for v in results.values()}, reverse=True)[:5])
# parameter perturbations
t1 = time.time()
it = 0
while time.time() - t1 < m1 * 60 * 0.6:
    it += 1
    P = dict(BASE)
    for kk in rng.sample(list(P), rng.randint(1, 3)):
        P[kk] = P[kk] * float(np.exp(nrng.normal(0, 0.4)))
    pr = fs_prio(P)
    c = greedy(pr + 1e-9 * nrng.random(M)); s = record(c, f"param {P}")
    if s >= 500:
        say("param variant", s, P)
say("after", it, "parameter variants: top sizes", sorted([v[0] for v in results.values()], reverse=True)[:10])
# other priority families: support/reflection based (from the structure of the 512 cap), random linear forms
wt = (VEC != 0).sum(axis=1)
refl = sum((VEC[:, i] == VEC[:, N - i]).astype(int) for i in range(1, N // 2))
fams = 0
while time.time() - t1 < m1 * 60:
    fams += 1
    a, b, cc, d = nrng.normal(0, 1, 4)
    pr = a * wt + b * refl + cc * (wt == 8) * refl + d * (VEC[:, 0] == 0)
    if rng.random() < 0.5:
        L = nrng.integers(0, 3, size=(2, N))
        pr = pr + nrng.normal(0, 1) * ((VEC.astype(int) @ L.T) % 3 == 0).sum(axis=1)
    c = greedy(pr + 1e-6 * nrng.random(M)); s = record(c, "family")
say("after", fams, "family variants: top sizes", sorted([v[0] for v in results.values()], reverse=True)[:10])
ranked = sorted(results.items(), key=lambda kv: -kv[1][0])
basecap = frozenset(int(x) for x in load_points(os.environ.get("BASELINE", "baseline.json")))
for i, (k, (s, lab)) in enumerate(ranked[:4]):
    fn = os.path.join(outdir, f"variant{i}_{s}.json"); save_points(fn, k)
    say("saved", fn, s, "same as baseline" if k == basecap else "different from baseline", lab[:120])
hist = {}
for s, _ in results.values():
    hist[s] = hist.get(s, 0) + 1
say("size histogram of distinct caps:", dict(sorted(hist.items(), reverse=True)[:15]))


# --- Part 2: product constructions ---
def max_cap(n, tl):
    vec = np.array(list(itertools.product((0, 1, 2), repeat=n)))
    pw = 3 ** np.arange(n - 1, -1, -1); m = 3 ** n
    mdl = cp_model.CpModel(); x = [mdl.NewBoolVar("") for _ in range(m)]
    for i in range(m):
        for j in range(i + 1, m):
            k = int(((-vec[i] - vec[j]) % 3) @ pw)
            if k > j:
                mdl.AddBoolOr([x[i].Not(), x[j].Not(), x[k].Not()])
    mdl.Add(x[0] == 1)
    mdl.Maximize(sum(x))
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = tl; s.parameters.num_workers = 1
    s.Solve(mdl)
    return [vec[i] for i in range(m) if s.Value(x[i])], s.BestObjectiveBound()


small = {}
for n, tl in ((2, 5), (3, 10), (4, 30), (5, m2 * 60 * 0.4), (6, m2 * 60 * 0.5)):
    caps, bound = max_cap(n, tl)
    small[n] = caps
    say(f"CP-SAT cap in F_3^{n}: {len(caps)} (bound {bound})")
prods = []
for a in range(2, 7):
    b = N - a
    if b < 2 or b > 6 or a > b:
        continue
    P = [int(np.concatenate([u, v]) @ POW) for u in small[a] for v in small[b]]
    assert is_cap(P)
    comp = greedy(np.where(np.isin(np.arange(M), P), -np.inf, 0.0) + nrng.random(M), start=P)
    say(f"product {len(small[a])} x {len(small[b])} = {len(P)}; greedy completion -> {len(comp)}")
    prods.append(comp)
for i, c in enumerate(sorted(prods, key=len, reverse=True)[:2]):
    fn = os.path.join(outdir, f"product{i}_{len(c)}.json"); save_points(fn, c); say("saved", fn)
say("done")
