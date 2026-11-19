"""Shared helpers for the F_3^8 cap set search: integer encoding, third-point table, completeness counts."""
import itertools, json
import numpy as np

N = 8
M = 3 ** N
VEC = np.array(list(itertools.product((0, 1, 2), repeat=N)), dtype=np.int8)  # index i <-> VEC[i]
POW = (3 ** np.arange(N - 1, -1, -1)).astype(np.int32)


def third_row(a):
    """For point a, the array t with t[b] = -(a+b) mod 3 (the point completing the line through a and b)."""
    return (((-VEC[a][None, :] - VEC) % 3).astype(np.int32) @ POW).astype(np.int32)


_T = None


def third_table():
    """Full 6561 x 6561 int16 table T[a, b] = -(a+b)."""
    global _T
    if _T is None:
        T = np.empty((M, M), dtype=np.int16)
        for a in range(M):
            T[a] = third_row(a)
        _T = T
    return _T


def load_points(path):
    pts = json.load(open(path))["points"]
    return np.array(pts, dtype=np.int32) @ POW


def save_points(path, idx):
    json.dump({"points": [VEC[i].tolist() for i in sorted(int(x) for x in idx)]}, open(path, "w"))


def is_cap(idx):
    T = third_table()
    idx = np.asarray(sorted(set(int(x) for x in idx)))
    inset = np.zeros(M, bool); inset[idx] = True
    sub = T[np.ix_(idx, idx)]
    hit = inset[sub]
    np.fill_diagonal(hit, False)
    return not hit.any()


def block_counts(idx):
    """For every point x, the number of pairs {a,b} in the set with a+b+x = 0 (0 for points of the set itself)."""
    T = third_table()
    idx = np.asarray(idx)
    inset = np.zeros(M, bool); inset[idx] = True
    cnt = np.zeros(M, np.int64)
    for a in idx:
        cnt += inset[T[a]]  # x with -(a+x) in set, i.e. a + b + x = 0 for b = T[a,x]
    cnt[idx] = 0
    # each pair counted from both ends; also a itself: T[a,a] = -2a = a, so x=a counts once -> already zeroed
    return cnt // 2
