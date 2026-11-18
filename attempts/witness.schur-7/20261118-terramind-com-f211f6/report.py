"""Aggregate every search log of schur7-538 into the tables of the writeup (prints Markdown)."""
import json, glob, collections, os
H = os.path.dirname(os.path.abspath(__file__))
def rows(pat):
    out = []
    for f in sorted(glob.glob(f'{H}/logs/{pat}')):
        for l in open(f):
            r = json.loads(l); r['_file'] = os.path.basename(f); out.append(r)
    return out
tot = collections.Counter(); secs = 0.0
# line a and its variants (sweep logs)
sw = [r for r in rows('sweep*_w*.jsonl') if r.get('line') and not r.get('note')]
for r in sw: tot[r['status']] += 1; secs += r.get('seconds', 0)
print('## sweep (core-guided descent)')
g = collections.defaultdict(list)
for r in sw: g[(r.get('line', 'a'), r.get('pivot', 538), r['N'], r['mode'])].append(r)
print('| line | pivot | N | mirror | bases | calls | SAT | min F proved UNSAT (min/median/max over bases) | F where limit hit (min/max) |')
print('|---|---|---|---|---|---|---|---|---|')
for k in sorted(g):
    rs = g[k]; per = collections.defaultdict(list)
    for r in rs: per[r['base']].append(r)
    mins = []; lims = []; sat = 0
    for b, xs in per.items():
        u = [x['core_max'] for x in xs if x['status'] == 'UNSAT' and x.get('core_max')]
        if u: mins.append(min(u))
        lims += [x['F'] for x in xs if x['status'] == 'LIMIT']; sat += sum(x['status'] == 'SAT' for x in xs)
    mins.sort()
    ms = f'{mins[0]}/{mins[len(mins)//2]}/{mins[-1]}' if mins else '-'
    ls = f'{min(lims)}/{max(lims)}' if lims else '-'
    print(f'| {k[0]} | {k[1]} | {k[2]} | {k[3]} | {len(per)} | {len(rs)} | {sat} | {ms} | {ls} |')
for name, pat in (('binary runs (ladder, zenwin, zenpre)', 'ladder.out'),):
    pass
bins = rows('search.jsonl') + rows('zenwin.jsonl') + rows('zenpre.jsonl')
print('\n## binary CaDiCaL runs')
c = collections.Counter((r['line'], r['N'], r['status'], r.get('rc')) for r in bins)
for k in sorted(c): print('|', ' | '.join(map(str, k)), '|', c[k], '|')
for r in bins: tot[r['status']] += 1; secs += r.get('seconds', 0) or 0
cn = [r for r in rows('cnc.jsonl') if r.get('event') == 'cube']
print('\n## cubes')
c = collections.Counter((r['tag'], r['status']) for r in cn)
for k in sorted(c): print(k, c[k])
for r in cn:
    if not r['tag'].startswith('calib'): tot[r['status']] += 1; secs += r['seconds']
sf = [r for r in rows('suffix.jsonl') if r.get('line')]
print('\n## suffix')
c = collections.Counter((r['N'], r['mode'], r['S'], r['status']) for r in sf)
for k in sorted(c): print(k, c[k])
for r in sf: tot[r['status']] += 1; secs += r['seconds']
jt = [r for r in rows('joint.jsonl')]
print('\n## joint'); [print(r) for r in jt]
for r in jt: tot[r['status']] += 1; secs += r['seconds']
print('\n## totals (search calls, calibration excluded)', dict(tot), 'solver seconds', round(secs))
print('SAT files with N >= 1699:', [f for f in glob.glob(f'{H}/out/sat/*.json') if len(json.load(open(f))['colors']) >= 1699])
