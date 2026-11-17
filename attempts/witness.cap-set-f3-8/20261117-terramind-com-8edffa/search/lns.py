"""Exchange / large-neighbourhood search on a cap set in F_3^8.

Each step removes a set R of cap points, computes the freed set F (R plus every outside point whose blocking pairs
all touch R), and solves max |S|, S subset of F, (kept points + S) a cap, exactly with OR-Tools CP-SAT
(hint: S = R). Net gain = |S| - |R|. Gain > 0 is an improvement; gain 0 with a different S is a plateau move,
accepted with probability --plateau to walk between caps of equal size.

Neighbourhoods (chosen at random each step):
  targeted : pick 1..3 outside points of low blocking count, remove one endpoint of each blocking pair
             (a vertex cover of their pair-matchings), biased to endpoints that block many low-count points
  random   : k points, k growing over time, sampled with weight ~ how many low-count outside points they block
  subspace : the cap points of a random affine subspace of codimension c (c in 1..3)
  hyperplanes : the cap points in a union of 1..4 random affine hyperplanes (up to KMAX points)
Environment: FMAX (skip larger freed sets), KMIN, KMAX (random-k range, k grows over the run), TMAX (CP-SAT seconds cap), PLATEAU.

usage: lns.py start.json outdir seed minutes
"""
import sys, os, time, random, json, itertools
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from capcore import *
from ortools.sat.python import cp_model

start, outdir, seed, minutes = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4])
plateau = float(os.environ.get("PLATEAU", "0.5"))
KMIN = int(os.environ.get("KMIN", "40")); KMAX = int(os.environ.get("KMAX", "470"))
TMAX = float(os.environ.get("TMAX", "60"))
FMAX = int(os.environ.get("FMAX", "1400"))  # skip neighbourhoods whose model would take minutes to build
skipped = 0
os.makedirs(outdir, exist_ok=True)
rng = random.Random(seed); nrng = np.random.default_rng(seed)
T = third_table()
cap = set(int(x) for x in load_points(start))
assert is_cap(cap)
base = len(cap)
t0 = time.time()
log = open(os.path.join(outdir, f"lns_{seed}.log"), "a")


def say(*a):
    s = f"[{time.time()-t0:7.1f}s] " + " ".join(str(x) for x in a)
    print(s, flush=True); log.write(s + "\n"); log.flush()


def freed(capl, R):
    Rs = set(R)
    K = np.array([p for p in capl if p not in Rs], dtype=np.int64)
    inK = np.zeros(M, bool); inK[K] = True
    blocked = inK[T[K]].any(axis=0)  # x blocked by some pair inside K (or x in K: T[a,a]=a)
    blocked |= inK
    F = np.nonzero(~blocked)[0]
    return K, inK, F


def solve(K, inK, F, R, tlim):
    F = np.asarray(F)
    nF = len(F)
    pos = {int(f): i for i, f in enumerate(F)}
    sub = T[np.ix_(F, F)].astype(np.int64)
    m = cp_model.CpModel()
    x = [m.NewBoolVar(f"x{i}") for i in range(nF)]
    inF = np.zeros(M, bool); inF[F] = True
    iu, ju = np.triu_indices(nF, 1)
    z = sub[iu, ju]
    pm = inK[z]
    for i, j in zip(iu[pm], ju[pm]):
        m.AddBoolOr([x[i].Not(), x[j].Not()])
    tm = inF[z]
    ntri = 0
    for i, j, zz in zip(iu[tm], ju[tm], z[tm]):
        k = pos[int(zz)]
        if k > j:
            m.AddBoolOr([x[i].Not(), x[j].Not(), x[k].Not()]); ntri += 1
    m.Maximize(sum(x))
    Rs = set(R)
    for i, f in enumerate(F):
        m.AddHint(x[i], 1 if int(f) in Rs else 0)
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = tlim
    s.parameters.num_workers = 1
    s.parameters.random_seed = rng.randrange(1 << 30)
    st = s.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None, st, int(pm.sum()), ntri
    S = [int(F[i]) for i in range(nF) if s.Value(x[i])]
    return S, st, int(pm.sum()), ntri


def blockinfo(capl):
    inC = np.zeros(M, bool); inC[capl] = True
    C = np.array(capl)
    rows = T[C]  # rows[i, x] = partner b of a=C[i] for line through x
    hit = inC[rows]  # hit[i,x]: (C[i], rows[i,x]) is a blocking pair of x
    cnt = hit.sum(axis=0) // 2
    cnt[C] = 0
    return C, rows, hit, cnt, inC


steps = 0; stats = {k: [0, 0, 0, 0] for k in ("targeted", "random", "subspace", "hyperplanes")}
maxR_opt = {}
best_gain = {}
last_report = 0
while time.time() - t0 < minutes * 60:
    steps += 1
    capl = sorted(cap)
    C, rows, hit, cnt, inC = blockinfo(capl)
    outside = np.nonzero(~inC)[0]
    elapsed = (time.time() - t0) / (minutes * 60)
    kind = rng.choices(["targeted", "random", "subspace", "hyperplanes"], [0.15, 0.4, 0.15, 0.3])[0]
    # weight of cap points: how many low-count outside points they help block
    w_out = np.zeros(M); w_out[outside] = 1.0 / np.maximum(cnt[outside], 1) ** 2
    wcap = (hit * w_out[None, :]).sum(axis=1)
    if kind == "targeted":
        lowc = outside[np.argsort(cnt[outside] + nrng.random(len(outside)) * 6)][:60]
        m_t = rng.choice([1, 1, 2, 2, 3])
        targets = rng.sample(list(lowc), m_t)
        R = set()
        for xo in targets:
            ii = np.nonzero(hit[:, xo])[0]
            for i in ii:
                a, b = int(C[i]), int(rows[i, xo])
                if a > b or a in R or b in R:
                    continue
                # pick endpoint with larger weight (mostly)
                ia = i; ib = int(np.searchsorted(C, b))
                if rng.random() < 0.75:
                    R.add(a if wcap[ia] >= wcap[ib] else b)
                else:
                    R.add(rng.choice([a, b]))
        R = sorted(R)
        if len(R) > 40:
            continue
    elif kind == "random":
        kmax = int(KMIN + elapsed * (KMAX - KMIN))
        k = rng.randint(max(1, kmax // 3), max(1, kmax))
        p = wcap + 1e-3; p = p / p.sum()
        R = sorted(int(v) for v in nrng.choice(C, size=k, replace=False, p=p))
    elif kind == "subspace":
        c = rng.choice([1, 2, 2, 3])
        while True:
            A = nrng.integers(0, 3, size=(c, N))
            # rank over F_3: check by enumerating combinations
            ok = True
            for coef in itertools.product((0, 1, 2), repeat=c):
                if any(coef) and not ((np.array(coef) @ A) % 3).any():
                    ok = False; break
            if ok:
                break
        v = nrng.integers(0, 3, size=c)
        insub = (((VEC.astype(np.int64) @ A.T) % 3) == v).all(axis=1)
        R = [p for p in capl if insub[p]]
        if not R:
            continue
    elif kind == "hyperplanes":
        h = rng.choice([1, 2, 2, 3, 3, 4])
        insub = np.zeros(M, bool)
        for _ in range(h):
            a = nrng.integers(0, 3, size=N)
            while not a.any():
                a = nrng.integers(0, 3, size=N)
            insub |= ((VEC.astype(np.int64) @ a) % 3) == rng.randrange(3)
        R = [p for p in capl if insub[p]]
        if not R or len(R) > KMAX:
            continue
    K, inK, F = freed(capl, R)
    if len(F) > FMAX:
        skipped += 1
        continue
    tlim = 2.0 + TMAX * min(1.0, len(F) / 1000.0)
    S, st, npair, ntri = solve(K, inK, F, R, tlim)
    if S is None:
        continue
    gain = len(S) - len(R)
    stats[kind][0] += 1
    best_gain[kind] = max(best_gain.get(kind, -999), gain)
    if st == cp_model.OPTIMAL:
        maxR_opt[kind] = max(maxR_opt.get(kind, 0), len(R))
    else:
        stats[kind][3] += 1
    newcap = set(K.tolist()) | set(S)
    if gain > 0:
        assert is_cap(newcap)
        cap = newcap
        stats[kind][1] += 1
        fn = os.path.join(outdir, f"improved_{len(cap)}_seed{seed}.json")
        save_points(fn, cap)
        say(f"IMPROVED to {len(cap)} via {kind} |R|={len(R)} |F|={len(F)} -> {fn}")
    elif gain == 0 and set(S) != set(R) and rng.random() < plateau:
        assert is_cap(newcap)
        cap = newcap
        stats[kind][2] += 1
    if time.time() - last_report > 60:
        last_report = time.time()
        say(f"step {steps} size {len(cap)} (start {base}) stats(solves,improve,plateau,not_optimal) {stats} best_gain {best_gain} largest_R_proved_optimal {maxR_opt} skipped(|F|>FMAX) {skipped} "
            f"last {kind} |R|={len(R)} |F|={len(F)} pairs={npair} tri={ntri} status={st} gain={gain} mincnt={cnt[outside].min()}")
save_points(os.path.join(outdir, f"final_seed{seed}.json"), cap)
say(f"done: steps {steps} final size {len(cap)} start {base} stats {stats} best_gain {best_gain} largest_R_proved_optimal {maxR_opt} skipped(|F|>FMAX) {skipped}")
