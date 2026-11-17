from pathlib import Path
from collections import Counter
import json

from campaign import STRUCTURED, BLOCKS
from summarize import search_log, events

results = Path('results')
sat = {x['case'][:-4]:x['status'] for x in events(results/'orbit-sat.log') if 'status' in x}
canonical = {}
for path in results.glob('canonical-*-b*.log'):
    outcomes = [row['status'] for row in events(path) if 'status' in row]
    canonical[path.stem.removeprefix('canonical-')] = outcomes[-1] if outcomes else 'time cap'

print('### Complete enumerations\n')
print('| Family | Assignments | Minimum total | K₄ and K₆ at saved minimum |')
print('| --- | ---: | ---: | --- |')
for name in STRUCTURED:
    path = results/f'{name}-enum.log'
    row = search_log(path)
    assert row['enumeration_complete']
    best = row['best']
    print(f"| `{name}` | {row['visited']:,} | {best['total']} | {best['zero']} + {best['one']} |")
print()

specs = {
    'n36-b2':'18 + 18', 'n36-b3':'12 + 12 + 12', 'n36-b4':'4 × 9', 'n36-b6':'6 × 6',
    'n37-b3':'18 + 18 + 1', 'n37-b4':'12 + 12 + 12 + 1', 'n37-b6':'4 × 8 + 4 + 1',
}
print('### Additional cyclic actions\n')
print('| Family | Vertex cycle sizes | Distinct fingerprints by batch | Best total found | Clique SAT | Strengthened SAT |')
print('| --- | --- | --- | ---: | --- | --- |')
for name in BLOCKS:
    jobs = [results/f'{name}-anneal.log',*sorted(results.glob(f'{name}-reheat-*.log'))]
    rows = [search_log(job) for job in jobs]
    counts = ', '.join(f"{r['distinct']:,}" for r in rows)
    best = min(r['best']['total'] for r in rows)
    print(f"| `{name}` | {specs[name]} | {counts} | {best} | {sat.get(name,'missing')} | {canonical.get(name[1:],'n/a')} |")
print()
