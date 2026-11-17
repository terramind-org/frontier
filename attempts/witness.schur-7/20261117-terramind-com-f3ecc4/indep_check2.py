"""Second independent check, class by class: each class as a set; no x, y in the class (x <= y, x = y allowed)
with x + y in the class; every integer 1..N coloured once in 0..6; reports pairs x, 2x explicitly."""
import json, sys
cols = json.load(open(sys.argv[1]))['colors']; N = len(cols)
ok_range = all(type(c) is int and 0 <= c <= 6 for c in cols)
classes = {k: {i + 1 for i, c in enumerate(cols) if c == k} for k in range(7)}
assert sum(len(s) for s in classes.values()) == N and set().union(*classes.values()) == set(range(1, N + 1))
bad = sum(1 for s in classes.values() for x in s for y in s if x <= y and x + y in s)
doubles = sum(1 for s in classes.values() for x in s if 2 * x in s)
print(sys.argv[1], 'N', N, 'colours in 0..6:', ok_range, 'monochromatic x+y=z (x<=y):', bad, 'of which x=y:', doubles)
