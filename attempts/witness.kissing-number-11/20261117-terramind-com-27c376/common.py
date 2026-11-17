"""Shared exact helpers. A vector is a tuple of 22 ints (p0,q0,...,p10,q10): coordinate k = p_k + q_k*sqrt2.
Scale of the published file: every vector has norm 36; compatible iff inner product a + b*sqrt2 <= 18 exactly."""
import json, numpy as np
D = 11
SQ2 = 2 ** 0.5

def load(path):
    d = json.load(open(path))
    return [tuple(v) for v in d['vectors']]

def save(path, vecs, desc):
    json.dump({'n': len(vecs), 'dim': D, 'description': desc, 'vectors': [list(map(int, v)) for v in vecs]}, open(path, 'w'))

def dot(u, v):
    a = b = 0
    for k in range(D):
        pu, qu, pv, qv = u[2*k], u[2*k+1], v[2*k], v[2*k+1]
        a += pu*pv + 2*qu*qv
        b += pu*qv + qu*pv
    return a, b

def le18(a, b):
    """exact a + b*sqrt2 <= 18"""
    x = 18 - a; y = -b  # need x + y sqrt2 >= 0
    if y == 0: return x >= 0
    if x >= 0 and y >= 0: return True
    if x <= 0 and y <= 0: return False
    if x > 0: return x*x >= 2*y*y   # y < 0
    return 2*y*y >= x*x             # x < 0 < y

def norm(v):
    return dot(v, v)

def as_float(vecs):
    a = np.array(vecs, dtype=np.int64)
    return a[:, 0::2] + SQ2 * a[:, 1::2]

def as_pq(vecs):
    a = np.array(vecs, dtype=np.int64)
    return a[:, 0::2].copy(), a[:, 1::2].copy()

def exact_valid(vecs):
    """Full exact check of a norm-36 configuration (all norms 36, distinct, pairwise dot <= 18). Vectorised:
    integer arrays a (rational part) and b (sqrt2 part) of the Gram matrix, then exact sign test."""
    P, Q = as_pq(vecs)
    n = len(vecs)
    A = P @ P.T + 2 * (Q @ Q.T)
    B = P @ Q.T + Q @ P.T
    if not (np.all(np.diag(A) == 36) and np.all(np.diag(B) == 0)):
        return False, 'norm'
    x = 18 - A; y = -B
    ok = np.where(y == 0, x >= 0,
         np.where((x >= 0) & (y >= 0), True,
         np.where((x <= 0) & (y <= 0), False,
         np.where(x > 0, x*x >= 2*y*y, 2*y*y >= x*x))))
    np.fill_diagonal(ok, True)
    bad = int((~ok).sum() // 2)
    if len(set(vecs)) != n: return False, 'dup'
    return bad == 0, f'{bad} bad pairs'

def conflicts_matrix(X, Y):
    """exact boolean matrix: X[i] conflicts with Y[j] (dot > 18). X, Y lists of 22-tuples."""
    Px, Qx = as_pq(X); Py, Qy = as_pq(Y)
    A = Px @ Py.T + 2 * (Qx @ Qy.T)
    B = Px @ Qy.T + Qx @ Py.T
    x = 18 - A; y = -B
    ok = np.where(y == 0, x >= 0,
         np.where((x >= 0) & (y >= 0), True,
         np.where((x <= 0) & (y <= 0), False,
         np.where(x > 0, x*x >= 2*y*y, 2*y*y >= x*x))))
    return ~ok
