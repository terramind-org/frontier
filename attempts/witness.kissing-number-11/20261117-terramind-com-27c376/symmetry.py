"""Signed coordinate permutations preserving the 604 (exact). Writes group.json: list of (perm, signs) where the
image of vector v has coordinate perm[k] = signs[k] * v[k]."""
import itertools, json, sys
sys.path.insert(0, 'src')
from common import load, D
V = load('baseline.json'); S = set(V)
def act(g, v):
    perm, sg = g
    out = [0] * 22
    for k in range(D):
        out[2*perm[k]] = sg[k] * v[2*k]; out[2*perm[k]+1] = sg[k] * v[2*k+1]
    return tuple(out)
# coordinate classes: A = coords carrying 6e_j, B = the rest; a symmetry maps A to A.
A = [k for k in range(D) if any(abs(v[2*k]) == 6 for v in V)]
B = [k for k in range(D) if k not in A]
supp = lambda v: frozenset(k for k in range(D) if v[2*k] or v[2*k+1])
supps = set(supp(v) for v in V)
G = []
for pa in itertools.permutations(A):
    for pb in itertools.permutations(B):
        perm = [0]*D
        for k, t in zip(A, pa): perm[k] = t
        for k, t in zip(B, pb): perm[k] = t
        if any(frozenset(perm[k] for k in s) not in supps for s in supps):
            continue
        for bits in range(1 << D):
            sg = [(-1 if bits >> k & 1 else 1) for k in range(D)]
            g = (perm, sg)
            if all(act(g, v) in S for v in V):
                G.append(g)
print('A', A, 'B', B, 'order', len(G))
json.dump(G, open('group.json', 'w'))
