"""Line (b2): the Zenodo 1698 colouring as a repair seed. Keep it fixed except a freed window W, extend to N
(1699..1701) with N's new top positions free, no mirror; CaDiCaL 3.1.0 binary per call (status from rc).
Windows: pivot region [537, 537 + w), centred [537 - w/2, 537 + w/2), top [1699 - w, 1698], low [1, w), and
pivot plus top / low plus top halves. Usage: zenwin.py <timeout-s> <workers>"""
import json, sys, os
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from lib538 import Runner, from_colouring
TO, NW = int(sys.argv[1]), int(sys.argv[2])
zen = json.load(open(f'{H}/inputs/zenodo1698.json'))['colors']
wins = {}
for w in (200, 400, 600):
    wins[f'pivot{w}'] = range(537, 537 + w)
    wins[f'centre{w}'] = range(537 - w // 2, 537 + w // 2)
    wins[f'top{w}'] = range(1699 - w, 1699)
    wins[f'low{w}'] = range(1, w + 1)
    wins[f'pivtop{w}'] = list(range(537, 537 + w // 2)) + list(range(1699 - w // 2, 1699))
    wins[f'lowtop{w}'] = list(range(1, w // 2 + 1)) + list(range(1699 - w // 2, 1699))
jobs = []
for N in (1699, 1700, 1701):
    for name, W in wins.items():
        Wset = set(W)
        fix = [x for x in range(1, 1699) if x not in Wset]
        jobs.append(dict(spec=dict(tag=f'zenwin/{name}_N{N}', line='b2', seed_src='zenodo1698', window=name,
                                   freed=len(Wset), N=N, mode='none'),
                         build=lambda N=N, fix=fix: from_colouring(N, zen + [0] * (N - 1698), fix), timeout=TO, seed=N))
R = Runner(f'{H}/logs/zenwin.jsonl', f'{H}/out/sat', workers=NW)
R.run(jobs)
