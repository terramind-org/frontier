"""Convert a full-term GF(2) mask file (first line rank, then 'a b d' per term, trace form) to a C3SCHEME file.
Fails unless the scheme is invariant under (a,b,d)->(b,d,a)."""
import sys
lines = open(sys.argv[1]).read().split("\n")
terms = [tuple(map(int, l.split())) for l in lines[1:] if l.strip()]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 5
from collections import Counter
cnt = Counter(terms)
fixed = [t[0] for t in terms if t[0] == t[1] == t[2]]
rest = Counter(t for t in terms if not (t[0] == t[1] == t[2]))
orbits = []
while rest:
    t = next(iter(rest))
    rots = [t, (t[1], t[2], t[0]), (t[2], t[0], t[1])]
    for r in rots:
        if rest[r] <= 0:
            sys.exit(f"not C3-invariant: missing rotation of {t}")
        rest[r] -= 1
        if rest[r] == 0:
            del rest[r]
    orbits.append(t)
with open(sys.argv[2], "w") as fh:
    fh.write(f"C3SCHEME {n} {len(fixed) + 3 * len(orbits)} {len(orbits)} {len(fixed)}\n")
    for x in fixed:
        fh.write(f"{x}\n")
    for o in orbits:
        fh.write(" ".join(map(str, o)) + "\n")
print(f"terms={len(terms)} fixed={len(fixed)} orbits={len(orbits)}")
