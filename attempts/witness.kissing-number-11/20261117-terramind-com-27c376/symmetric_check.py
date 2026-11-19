"""Orbit-symmetric exact models. S = the sign subgroup of G (order 512: every single A-coordinate flip and the
simultaneous flip of the three B coordinates). A configuration invariant under S can only use vectors x whose S-orbit
is pairwise compatible: x . (s x) = 36 - 2 sum_{k flipped} x_k^2 <= 18 forces every nonzero A coordinate to have
x_k^2 >= 9 and the B part to be 0 or |x_B|^2 >= 9. Variables are S-orbits (weight = orbit size); two orbits are
compatible iff max over s of x . (s y) = sum_A |x_k y_k| + |x_B . y_B| <= 18 (exact). Then for subgroups H = S x| P'
(P' a subgroup of the 48 coordinate permutations, each with its B-sign coset) variables are H-orbits.
Pool class: A coordinates pure (integer or q sqrt2), B coordinates any p + q sqrt2 (pure and mixed), norm 36 exactly.
Usage: symmetric.py <time limit per model s> <out json>"""
import sys, os, json, time, itertools, random
sys.path.insert(0, os.path.dirname(__file__))
from common import load, save, exact_valid, le18
import mis
D = 11
V604 = load('baseline.json')
G = json.load(open('group.json'))
def utc(): return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
log = open('logs/symmetric-check.log', 'a')
def P(s): print(f'{utc()} {s}', file=log, flush=True); print(s, flush=True)
# A values (nonnegative representatives, square >= 9): (p, q, square)
Avals = [(p, 0, p*p) for p in (3, 4, 5, 6)] + [(0, q, 2*q*q) for q in (3, 4)]
# B parts with sum pq = 0, rational norm r: enumerate all
Bvals = [(p, q) for p in range(-6, 7) for q in range(-4, 5) if p*p + 2*q*q <= 36]
Bparts = {}
for b in itertools.product(Bvals, repeat=3):
    r = sum(p*p + 2*q*q for p, q in b); t = sum(p*q for p, q in b)
    if r <= 36 and t == 0 and (r == 0 or r >= 9):
        Bparts.setdefault(r, []).append(b)
def canonB(b):
    nb = tuple((-p, -q) for p, q in b)
    return min(b, nb)
reps = set()
def recA(k, a, r):
    if k == 8:
        rest = 36 - r
        for b in Bparts.get(rest, []):
            reps.add(tuple(a) + canonB(b))
        return
    recA(k + 1, a + [(0, 0)], r)
    for p, q, s in Avals:
        if r + s <= 36: recA(k + 1, a + [(p, q)], r + s)
recA(0, [], 0)
reps = sorted(reps)
P(f'S-model pool: {len(reps)} S-orbits')
def flat(x): return tuple(c for pq in x for c in pq)
def orbit_size(x):
    return 2 ** sum(1 for k in range(8) if x[k] != (0, 0)) * (2 if any(x[k] != (0, 0) for k in range(8, 11)) else 1)
def mul_abs(u, v):
    # |u v| for pure coordinates u, v given as (p, q): returns (a, b) meaning a + b sqrt2
    (p1, q1), (p2, q2) = u, v
    return abs(p1*p2) + 2*abs(q1*q2), abs(p1*q2) + abs(q1*p2)
def compatible(x, y):
    a = b = 0
    for k in range(8):
        da, db = mul_abs(x[k], y[k]); a += da; b += db
    c = d = 0
    for k in range(8, 11):
        (p1, q1), (p2, q2) = x[k], y[k]
        c += p1*p2 + 2*q1*q2; d += p1*q2 + q1*p2
    # |c + d sqrt2|
    if not le18(-c, -d) or True:
        pass
    neg = not le18(c, d) and False
    # sign of c + d sqrt2: use le18 trick: c + d sqrt2 >= 0  <=>  -(c) - d sqrt2 <= 0  <=> le18(-c + 18, -d)
    nonneg = le18(18 - c, -d)
    if not nonneg: c, d = -c, -d
    return le18(a + c, b + d)
# canonical S-orbit key of an arbitrary vector given as list of (p, q)
def skey(x):
    x = [(abs(p), abs(q)) if k < 8 else (p, q) for k, (p, q) in enumerate(x)]
    return tuple(x[:8]) + canonB(tuple(x[8:]))
index = {x: i for i, x in enumerate(reps)}
# the 604 as S-orbits
V604pq = [[(v[2*k], v[2*k+1]) for k in range(D)] for v in V604]
base = sorted({index[skey(x)] for x in V604pq})
P(f'604 = {len(base)} S-orbits, total weight {sum(orbit_size(reps[i]) for i in base)}')
n = len(reps)
t0 = time.time()
# conflict graph among S-orbits (exact). n is small enough for O(n^2) pure Python? check
P(f'building edges for n={n}')
import numpy as np
# vectorised: represent coordinates of reps as (p,q) arrays; A part products |.|, B part signed
Pp = np.array([[c[0] for c in x] for x in reps], dtype=np.int64); Qq = np.array([[c[1] for c in x] for x in reps], dtype=np.int64)
edges = []
BR = max(16, int(2.5e6 // n))  # rows per block: each int64 temporary is BR x n x 8 entries (about 160 MB)
for i0 in range(0, n, BR):
    pa, qa = Pp[i0:i0+BR], Qq[i0:i0+BR]
    Aa = np.abs(pa[:, None, :8] * Pp[None, :, :8]).sum(-1) + 2 * np.abs(qa[:, None, :8] * Qq[None, :, :8]).sum(-1)
    Ab = np.abs(pa[:, None, :8] * Qq[None, :, :8]).sum(-1) + np.abs(qa[:, None, :8] * Pp[None, :, :8]).sum(-1)
    Bc = (pa[:, None, 8:] * Pp[None, :, 8:]).sum(-1) + 2 * (qa[:, None, 8:] * Qq[None, :, 8:]).sum(-1)
    Bd = (pa[:, None, 8:] * Qq[None, :, 8:]).sum(-1) + (qa[:, None, 8:] * Pp[None, :, 8:]).sum(-1)
    # sign of Bc + Bd sqrt2
    pos = np.where(Bd == 0, Bc >= 0, np.where((Bc >= 0) & (Bd >= 0), True, np.where((Bc <= 0) & (Bd <= 0), False,
          np.where(Bc > 0, Bc*Bc >= 2*Bd*Bd, 2*Bd*Bd >= Bc*Bc))))
    Bc = np.where(pos, Bc, -Bc); Bd = np.where(pos, Bd, -Bd)
    x = 18 - (Aa + Bc); y = -(Ab + Bd)
    ok = np.where(y == 0, x >= 0, np.where((x >= 0) & (y >= 0), True, np.where((x <= 0) & (y <= 0), False,
         np.where(x > 0, x*x >= 2*y*y, 2*y*y >= x*x))))
    ii, jj = np.nonzero(~ok)
    for i, j in zip(ii + i0, jj):
        if i < j: edges.append((int(i), int(j)))
P(f'S-model edges {len(edges)} ({time.time()-t0:.1f}s); spot-check vs scalar: ' +
  str(all(compatible(reps[i], reps[j]) == ((i, j) not in set(edges[:0])) for i, j in [(0, 0)])))
# scalar spot check on random pairs
E = set(edges); rng = random.Random(1); bad = 0
for _ in range(20000):
    i, j = sorted(rng.sample(range(n), 2))
    if compatible(reps[i], reps[j]) == ((i, j) in E): bad += 1
P(f'scalar/vector disagreements on 20000 random pairs: {bad}')
for i, j in [(a, b) for a in base for b in base if a < b]:
    assert (i, j) not in E
w = [orbit_size(x) for x in reps]
results = {}
tl = float(sys.argv[1])
def expand_S(chosen_reps):
    out = set()
    for x in chosen_reps:
        nzA = [k for k in range(8) if x[k] != (0, 0)]
        for bits in range(1 << len(nzA)):
            y = list(x)
            for t, k in enumerate(nzA):
                if bits >> t & 1: y[k] = (-x[k][0], -x[k][1])
            out.add(flat(y))
            if any(x[k] != (0, 0) for k in range(8, 11)):
                z = y[:8] + [(-p, -q) for p, q in y[8:]]
                out.add(flat(z))
    return sorted(out)
results = {}
# H = S x| P' models: P' generated by random subsets of the 48 permutations (with their B-sign cosets)
perms = {}
for p, s in G:
    perms.setdefault(tuple(p), s)
plist = list(perms.items())
def apply_perm(ps, x):
    p, s = ps
    y = [None] * D
    for k in range(D):
        sg = 1 if k < 8 else s[k]
        y[p[k]] = (sg * x[k][0], sg * x[k][1])
    return skey(y)
def gen_subgroup(gens):
    # closure of the permutation images acting on S-orbit keys; represent elements by their action on rep indices
    els = [tuple(range(n))]
    acts = [tuple(index[apply_perm(g, reps[i])] for i in range(n)) for g in gens]
    seen = {els[0]}; frontier = [els[0]]
    while frontier:
        nf = []
        for e in frontier:
            for a in acts:
                c = tuple(a[e[i]] for i in range(n))
                if c not in seen: seen.add(c); nf.append(c)
        frontier = nf
        if len(seen) > 48: break
    return list(seen)
rng = random.Random(7)
done_orders = set()
for trial in range(40):
    k = rng.choice([1, 1, 2])
    gens = rng.sample(plist[1:], k)
    els = gen_subgroup(gens)
    order = len(els)
    if order in done_orders or order > 48: continue
    done_orders.add(order)
    # H-orbits on S-orbits
    comp = [-1] * n; orbs = []
    for i in range(n):
        if comp[i] >= 0: continue
        o = sorted({e[i] for e in els})
        for j in o: comp[j] = len(orbs)
        orbs.append(o)
    # valid H-orbit: its S-orbits pairwise compatible
    valid = [all((min(a, b), max(a, b)) not in E for a in o for b in o if a < b) for o in orbs]
    vid = [t for t in range(len(orbs)) if valid[t]]
    pos = {t: u for u, t in enumerate(vid)}
    he = set()
    for i, j in edges:
        a, b = comp[i], comp[j]
        if a != b and valid[a] and valid[b]: he.add((min(pos[a], pos[b]), max(pos[a], pos[b])))
    hw = [sum(w[i] for i in orbs[t]) for t in vid]
    hint = {pos[comp[i]] for i in base}
    P(f'SUBGROUP |P\'|={order} generators (perm, B-signs) = {[(list(g[0]), g[1][8:]) for g in gens]}')
    if len(vid) > 600:
        P(f'  not re-solved (H-orbits={len(vid)})'); continue
    st, val, bnd, ch, ts = mis.solve(len(vid), sorted(he), weights=hw, time_limit=tl, hint=None, seed=3, workers=1, cover=len(he) < 300000)
    P(f'MODEL S x| P\' (|P\'|={order}, order {512*order}): H-orbits={len(vid)} edges={len(he)} status={st} incumbent={val} bound={bnd} time={ts:.1f}s')
    results[f'S_P{order}'] = dict(order=512*order, orbits=len(vid), edges=len(he), status=st, incumbent=val, bound=bnd, time=ts)
    if val and val > 604:
        X = expand_S([reps[i] for t in ch for i in orbs[vid[t]]]); ok = exact_valid(X); P(f'  expands to {len(X)} exact {ok}')
        if ok[0]: save(f'SP{order}-model-best.json', X, 'symmetric configuration')

