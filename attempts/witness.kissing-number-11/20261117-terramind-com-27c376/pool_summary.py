"""Pool size by pattern from the orbit-representative files: pattern = sorted multiset of coordinate types, where a
coordinate is written p (integer), q*r2 (pure sqrt2 multiple) or p+q*r2 (mixed). Counts are vectors (sum of orbit
sizes |G|/|Stab|) and orbits. Also: vectors with at most k conflicts against the 604 (k = 1 means the 604 itself)."""
import sys, collections, json
out = {}
for name in sys.argv[1:]:
    pat = collections.Counter(); orb = collections.Counter(); low = collections.Counter(); tot = 0
    with open(name) as f:
        for line in f:
            t = line.split()
            v = list(map(int, t[:22])); st = int(t[22]); nc = int(t[23])
            size = 24576 // st
            parts = []
            for k in range(11):
                p, q = abs(v[2*k]), abs(v[2*k+1])
                if p == 0 and q == 0: continue
                parts.append(f'{p}' if q == 0 else f'{q}r2' if p == 0 else f'{p}+-{q}r2')
            key = ','.join(sorted(parts, key=lambda s: (-len(s), s)))
            pat[key] += size; orb[key] += 1; tot += size
            low[min(nc, 20)] += size
    out[name] = {'total_vectors': tot, 'orbits': sum(orb.values()), 'patterns': len(pat),
                 'by_pattern': {k: [pat[k], orb[k]] for k in sorted(pat, key=lambda k: -pat[k])},
                 'conflicts_with_604_hist_capped20': dict(sorted(low.items()))}
    print(name, tot, sum(orb.values()), len(pat))
json.dump(out, open('logs/pool-summary.json', 'w'), indent=0)
