"""Line (a), step 1: where does pivot 538 land? Bases fully fixed (F = 537), 538 in colour 6, full mirror
x -> N+1-x for N with 3 not dividing N+1, partial mirror (base and pivot only) for all N, on 6 bases."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib538 import Runner, template, bhash
H = os.path.dirname(os.path.abspath(__file__))
bases = json.load(open(f'{H}/inputs/bases537.json'))
pick = ['F1.001', 'F1.050', 'F2.001', 'F3.001', 'F4.001', 'F5.001']
R = Runner(f'{H}/logs/search.jsonl', f'{H}/out/sat')
jobs = []
for b in pick:
    base = bases[b]
    for N in range(1690, 1705):
        modes = (['full'] if (N + 1) % 3 else []) + ['partial']
        for m in modes:
            jobs.append(dict(spec=dict(tag=f'ladder/{b}_F537_N{N}_{m}', line='a-ladder', base=b, bhash=bhash(base),
                                       F=537, N=N, mode=m, pivot=538),
                             build=lambda base=base, N=N, m=m: template(N, base, 537, 538, m), timeout=30, seed=N))
R.run(jobs)
