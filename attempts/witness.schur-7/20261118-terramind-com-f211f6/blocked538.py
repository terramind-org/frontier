"""Arithmetic explanation of root failures: for a template (fixed base, pivot, mirrored base), list the free
integers whose every colour is blocked by a pair of fixed integers of that colour (x + y = m, m + x = y)."""
import json, sys
def blocked(N, base, pivot, mirror, F=None):
    F = F or len(base)
    col = {x: base[x - 1] for x in range(1, F + 1)}; col[pivot] = 6
    allowed6 = lambda x: x >= pivot and (mirror == 'none' or x <= N + 1 - pivot)
    if mirror in ('full', 'partial'):
        for x in list(col): col[N + 1 - x] = col[x]
    out = []
    for m in range(1, N + 1):
        if m in col: continue
        bl = set() if allowed6(m) else {6}
        for c in range(7):
            for a, ca in col.items():
                if ca != c: continue
                b = m - a
                if b >= 1 and col.get(b) == c: bl.add(c); break
                b = m + a
                if b <= N and col.get(b) == c: bl.add(c); break
                if 2 * m == a or (a - m >= 1 and col.get(a - m) == c): bl.add(c); break
        if len(bl) == 7: out.append(m)
    return out
if __name__ == '__main__':
    bases = json.load(open('inputs/bases537.json'))
    b = bases[sys.argv[1]]; mode = sys.argv[2]
    for N in map(int, sys.argv[3:]):
        bl = blocked(N, b, 538, mode); print(N, mode, len(bl), bl[:12])
