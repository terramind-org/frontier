"""Arithmetic unit propagation on a pivot template: repeatedly give each free integer with one allowed colour that
colour; report the integer that ends with none, and the forced chain (for explaining root UNSAT)."""
import json, sys
def allowed(m, col, N, pivot, mirror):
    al = set(range(6)) | ({6} if (m >= pivot and (mirror == 'none' or m <= N + 1 - pivot)) else set())
    for c in list(al):
        for a, ca in col.items():
            if ca != c: continue
            if (m - a >= 1 and col.get(m - a) == c) or (m + a <= N and col.get(m + a) == c) or \
               (a - m >= 1 and col.get(a - m) == c) or (2 * m <= N and False):
                al.discard(c); break
        if c in al and 2 * m <= N and col.get(2 * m) == c: al.discard(c)
        if c in al and m % 2 == 0 and col.get(m // 2) == c: al.discard(c)
    return al
def run(N, base, F, pivot, mirror):
    col = {x: base[x - 1] for x in range(1, F + 1)}; col[pivot] = 6
    if mirror in ('full', 'partial'):
        for x in list(col): col[N + 1 - x] = col[x]
    chain = []
    while True:
        changed = False
        for m in range(1, N + 1):
            if m in col: continue
            al = allowed(m, col, N, pivot, mirror)
            if mirror == 'full' and N + 1 - m != m:
                al &= allowed(N + 1 - m, col, N, pivot, mirror)
            if not al: return chain, m
            if len(al) == 1:
                c = al.pop(); col[m] = c; chain.append((m, c))
                if mirror == 'full': col[N + 1 - m] = c
                changed = True
        if not changed: return chain, None
if __name__ == '__main__':
    bases = json.load(open('inputs/bases537.json')); b = bases[sys.argv[1]]
    N = int(sys.argv[3]); mode = sys.argv[2]; F = int(sys.argv[4]) if len(sys.argv) > 4 else 537
    chain, dead = run(N, b, F, 538, mode)
    print('forced', len(chain), chain[:30], 'dead end at', dead)
