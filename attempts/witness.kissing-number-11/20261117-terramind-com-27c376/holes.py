"""Numerical deep holes of the 604: local minima of max_w cos(x, w) over unit x (random starts, smooth-max descent,
then an epigraph LP polish on the active set). Holes are grouped into G-classes by the sorted multiset of their
cosines to the 604 (rounded to 1e-6). Output holes.json: one representative per class with its max cosine and the
indices of the 604 at cosine >= maxcos - 1e-7 (the exact-tie blockers, numerically)."""
import sys, os, json, time
import numpy as np
from scipy.optimize import linprog
sys.path.insert(0, os.path.dirname(__file__))
from common import load, as_float
V = load('baseline.json'); W = as_float(V) / 6.0
rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
ntr = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
def descend(x):
    for beta in (20, 50, 150, 500, 2000):
        for _ in range(200):
            c = W @ x
            e = np.exp(beta * (c - c.max())); p = e / e.sum()
            g = W.T @ p
            g -= (g @ x) * x
            x = x - 0.5 / beta * g; x /= np.linalg.norm(x)
    return x
def polish(x):
    for _ in range(30):
        c = W @ x; act = np.argsort(-c)[:80]
        # minimise t s.t. W_a (x + d) <= t, d orthogonal to x, |d_i| <= 0.02
        n = 11
        A = np.hstack([W[act], -np.ones((len(act), 1))]); b = -(W[act] @ x)
        Aeq = np.hstack([x[None, :], np.zeros((1, 1))]); beq = [0.0]
        r = linprog(np.r_[np.zeros(n), 1.0], A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq,
                    bounds=[(-0.02, 0.02)] * n + [(None, None)], method='highs')
        if r.status != 0: break
        x2 = x + r.x[:n]; x2 /= np.linalg.norm(x2)
        if (W @ x2).max() >= c.max() - 1e-13: break
        x = x2
    return x
classes = {}
t0 = time.time()
for t in range(ntr):
    x = rng.normal(size=11); x /= np.linalg.norm(x)
    x = polish(descend(x))
    c = W @ x; mc = c.max()
    key = tuple(np.round(np.sort(c)[-60:], 5))
    if key not in classes:
        classes[key] = dict(x=x.tolist(), maxcos=float(mc), count=0,
                            blockers=[int(i) for i in np.nonzero(c >= mc - 1e-7)[0]],
                            shell=[int(i) for i in np.argsort(-c)[:120]])
    classes[key]['count'] += 1
out = sorted(classes.values(), key=lambda h: h['maxcos'])
print(f'{ntr} starts, {len(out)} hole classes, {time.time()-t0:.0f}s')
for h in out[:25]:
    print(f"maxcos {h['maxcos']:.6f} blockers {len(h['blockers'])} hits {h['count']}")
json.dump(out, open('holes.json', 'w'))
