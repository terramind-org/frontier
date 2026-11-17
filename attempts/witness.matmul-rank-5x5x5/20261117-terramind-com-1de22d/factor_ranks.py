"""Multiset of GF(2) ranks of all factor matrices of a C3SCHEME (orbits expanded). Invariant under the
matrix-multiplication symmetry group, so different multisets mean inequivalent schemes (equal ones prove nothing)."""
import sys, collections
def rank2(m, n=5):
    rows = [(m >> (5 * i)) & 31 for i in range(n)]; r = 0
    for b in range(n):
        piv = next((i for i in range(r, n) if rows[i] >> b & 1), None)
        if piv is None: continue
        rows[r], rows[piv] = rows[piv], rows[r]
        for i in range(n):
            if i != r and rows[i] >> b & 1: rows[i] ^= rows[r]
        r += 1
    return r
for path in sys.argv[1:]:
    L = open(path).read().split("\n"); _, n, rk, no, nf = L[0].split(); no, nf = int(no), int(nf)
    fx = [int(x) for x in L[1:1 + nf]]; orb = [list(map(int, l.split())) for l in L[1 + nf:1 + nf + no]]
    c = collections.Counter(rank2(x) for x in fx for _ in range(3))
    for o in orb: c.update(rank2(x) * 1 for x in o for _ in range(3))
    print(path, "rank", rk, "factor-rank multiset", dict(sorted(c.items())))
