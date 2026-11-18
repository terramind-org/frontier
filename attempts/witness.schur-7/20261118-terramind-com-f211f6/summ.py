"""Summarise sweep logs: per (N, mode): bases done, final status counts, min F proved UNSAT per base (by core), SAT list."""
import json, sys, glob, collections
recs = []
for f in sorted(glob.glob('logs/sweep*_w*.jsonl')):
    for l in open(f):
        r = json.loads(l)
        if r.get('line'): r['_f'] = f; recs.append(r)
by = collections.defaultdict(list)
for r in recs: by[(r.get('line'), r.get('pivot', 538), r['N'], r['mode'], r['base'])].append(r)
agg = collections.defaultdict(lambda: dict(bases=0, end=collections.Counter(), unsatF=[], calls=0))
sats = []
for k, rs in by.items():
    a = agg[k[:4]]; a['bases'] += 1; a['calls'] += len(rs)
    last = rs[-1]; a['end'][last['status']] += 1
    u = [r['core_max'] for r in rs if r['status'] == 'UNSAT']
    if u: a['unsatF'].append(min(u))
    sats += [r for r in rs if r['status'] == 'SAT']
for k in sorted(agg):
    a = agg[k]; u = sorted(a['unsatF'])
    print(k, 'bases', a['bases'], 'calls', a['calls'], dict(a['end']), 'min-F-UNSAT: min', u[0] if u else None, 'median', u[len(u)//2] if u else None, 'max', u[-1] if u else None)
print('SAT:', [(r['base'], r['N'], r['mode'], r['F'], r.get('own_violations')) for r in sats])
