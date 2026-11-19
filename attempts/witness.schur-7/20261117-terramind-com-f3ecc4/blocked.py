"""Which integers have every colour excluded by fixed colours alone (pairs of fixed integers), for the
Rowley-style constructions at several orders. Pure arithmetic, no solver."""
import sys, json
from schur import load
def fixed_colouring(base, S, N, mirror_upto):
    f = {i + 1: c for i, c in enumerate(base)}; m = len(base); f[m + 1] = 6
    for x in list(f):
        if x <= mirror_upto and 1 <= S - x <= N: f[S - x] = f[x]
    return f
def blocked(f, N, K=7):
    out = {}
    for z in range(1, N + 1):
        if z in f: continue
        bl = set()
        for x, c in f.items():
            y = z - x                      # x + y = z
            if 1 <= y <= N and f.get(y) == c: bl.add(c)
            y2 = z + x                     # z + x = y2
            if y2 <= N and f.get(y2) == c: bl.add(c)
        if len(bl) == K: out[z] = 'all'
    return out
base = load(sys.argv[1])[:536]
for N, S in [(1696, 1697), (1697, 1698), (1698, 1699), (1699, 1700), (1700, 1701)]:
    f = fixed_colouring(base, S, N, 537)
    # also check fixed-fixed conflicts
    conf = [(x, y) for x in f for y in f if x <= y and x + y <= N and f[x] == f[y] == f.get(x + y)]
    b = blocked(f, N)
    print(N, 'S', S, 'fixed conflicts', conf[:5], 'n', len(conf), 'all-blocked', sorted(b)[:12], len(b))
print('--- with x + x = 2x and the self-mirror triple (x, S - 2x, S - x)')
def blocked2(f, N, S, K=7, symmetric=True):
    res = {}
    for z in range(1, N + 1):
        if z in f: continue
        bl = set()
        for x, c in f.items():
            y = z - x
            if 1 <= y <= N and f.get(y) == c: bl.add(c)
            if z + x <= N and f.get(z + x) == c: bl.add(c)
        if 2 * z <= N and (2 * z) in f: bl.add(f[2 * z])
        if symmetric and 1 <= S - 2 * z <= N and (S - 2 * z) in f and S - z <= N: bl.add(f[S - 2 * z])
        if len(bl) == K: res[z] = 1
        elif len(bl) == K - 1: res.setdefault('forced', []).append(z)
    return res
for N, S, sym in [(1696, 1697, True), (1697, 1698, False), (1698, 1699, True), (1699, 1700, True)]:
    f = fixed_colouring(base, S, N, 537)
    b = blocked2(f, N, S, symmetric=sym)
    print(N, S, 'all-blocked', sorted(k for k in b if k != 'forced')[:10], 'forced', len(b.get('forced', [])))
