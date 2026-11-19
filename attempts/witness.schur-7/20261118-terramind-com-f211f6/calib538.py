"""Calibration for schur7-538: small known answers, 1698 reconstructions from the repo and Zenodo prefixes,
planted middle refill, and the divisibility check at 1697."""
import json, sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib538 import Runner, template, from_colouring, bhash
from schur import Instance
H = os.path.dirname(os.path.abspath(__file__))
repo = json.load(open(f'{H}/inputs/repo1698.json'))['colors']
zen = json.load(open(f'{H}/inputs/zenodo1698.json'))['colors']
R = Runner(f'{H}/logs/calib.jsonl', f'{H}/out/calib')
jobs = []
for N in (13, 14):
    jobs.append(dict(spec=dict(tag=f'k3_N{N}', line='calib', N=N), build=lambda N=N: Instance(N, 3), timeout=60))
for name, c in (('repo', repo), ('zen', zen)):
    for F in (536, 400, 300):
        jobs.append(dict(spec=dict(tag=f'{name}_pivot537_F{F}_sym1698', line='calib', N=1698, F=F, mode='full'),
                         build=lambda c=c, F=F: template(1698, c[:536], F, 537, 'full'), timeout=120, seed=1))
rnd = random.Random(7)
win = list(range(700, 1000))  # planted: free 300 middle positions of the Zenodo colouring
jobs.append(dict(spec=dict(tag='zen_refill_700_999', line='calib', N=1698),
                 build=lambda: from_colouring(1698, zen, [x for x in range(1, 1699) if x not in set(win)]), timeout=120))
jobs.append(dict(spec=dict(tag='zen_pivot537_sym1697', line='calib', N=1697, F=536, mode='full', expect='UNSAT'),
                 build=lambda: template(1697, zen[:536], 536, 537, 'full'), timeout=60))
R.run(jobs)
