"""For each 537-base: Z = middle integers m in 539..1074 whose six base colours are all blocked by base pairs
(a + b = m, a, b <= 537, same colour). With 538 in colour 6 and its mirror N - 537 in colour 6, every z in Z must be
colour 6, so z + 538 = N - 537 (N = z + 1075) is impossible."""
import json, sys
bases = json.load(open('inputs/bases537.json'))
rows = []
for k, b in bases.items():
    pos = [[x for x in range(1, 538) if b[x - 1] == c] for c in range(6)]
    sets = [set(p) for p in pos]
    Z = []
    for m in range(539, 1075):
        if all(any((m - a) in sets[c] for a in pos[c] if m - a >= 1) for c in range(6)): Z.append(m)
    okN = [N for N in range(1690, 1711) if (N - 1075) not in Z]
    rows.append((k, len(Z), max(Z) if Z else None, okN))
for r in rows: print(*r)
