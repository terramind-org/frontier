"""Independent brute-force check of a Schur witness: every pair x <= y with x + y <= N, colours in 0..6."""
import json, sys
cols = json.load(open(sys.argv[1]))['colors']
N = len(cols)
assert all(isinstance(c, int) and 0 <= c <= 6 for c in cols)
bad = [(x, y) for x in range(1, N + 1) for y in range(x, N + 1 - x) if cols[x-1] == cols[y-1] == cols[x+y-1]]
classes = [sum(1 for c in cols if c == k) for k in range(7)]
sym = sum(cols[x-1] != cols[N - x] for x in range(1, N + 1))
print(sys.argv[1], 'N', N, 'monochromatic', len(bad), 'class sizes', classes, 'asymmetric positions (x vs N+1-x)', sym)
