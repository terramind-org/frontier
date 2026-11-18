"""Line (b1, no symmetry): the Zenodo 1698 colouring's 1..F fixed, everything above free, no mirror, N = 1699..1701.
CaDiCaL 3.1.0 binary per call. Usage: zenpre.py <timeout-s> <workers>"""
import json, sys, os
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from lib538 import Runner, from_colouring
TO, NW = int(sys.argv[1]), int(sys.argv[2])
zen = json.load(open(f'{H}/inputs/zenodo1698.json'))['colors']
jobs = []
for F in (1300, 1100, 900, 700, 537):
    for N in (1699, 1700, 1701):
        jobs.append(dict(spec=dict(tag=f'zenpre/F{F}_N{N}', line='b1-free', seed_src='zenodo1698', F=F, N=N, mode='none'),
                         build=lambda N=N, F=F: from_colouring(N, zen + [0] * (N - 1698), range(1, F + 1)), timeout=TO, seed=F + N))
Runner(f'{H}/logs/zenpre.jsonl', f'{H}/out/sat', workers=NW).run(jobs)
