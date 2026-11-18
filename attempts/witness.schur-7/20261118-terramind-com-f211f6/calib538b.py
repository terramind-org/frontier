"""Calibration part 2: how short a prefix of the Zenodo / repo 1698 colourings still lets the pivot-537 symmetric
1698 instance be solved quickly (positive controls for short-prefix runs)."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib538 import Runner, template
H = os.path.dirname(os.path.abspath(__file__))
repo = json.load(open(f'{H}/inputs/repo1698.json'))['colors']
zen = json.load(open(f'{H}/inputs/zenodo1698.json'))['colors']
R = Runner(f'{H}/logs/calib.jsonl', f'{H}/out/calib')
jobs = []
for F in (200, 150, 100, 50):
    for name, c in (('zen', zen), ('repo', repo)):
        jobs.append(dict(spec=dict(tag=f'{name}_pivot537_F{F}_sym1698', line='calib', N=1698, F=F, mode='full'),
                         build=lambda c=c, F=F: template(1698, c[:536], F, 537, 'full'), timeout=90, seed=1))
R.run(jobs)
