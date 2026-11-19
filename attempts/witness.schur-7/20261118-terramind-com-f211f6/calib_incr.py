"""Calibration of the incremental-assumption path used by sweep.py: pivot 537 template at N = 1698 (full mirror)
loaded once, then the repo and Zenodo 1..536 prefixes (F = 536, 300, 150) assumed: must be SAT with 0 violations.
Then Rowley-family negative at 1699 with the repo base (known UNSAT with 1..200 fixed from round 2): report core."""
import json, sys, os, time, threading
from pysat.solvers import Cadical195
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from lib538 import template
from check import count_viol
repo = json.load(open(f'{H}/inputs/repo1698.json'))['colors']; zen = json.load(open(f'{H}/inputs/zenodo1698.json'))['colors']
log = open(f'{H}/logs/calib_incr.jsonl', 'a', buffering=1)
for N in (1698, 1699):
    inst = template(N, [0] * 536, 0, 537, 'full'); s = Cadical195()
    for c in inst.clauses(): s.add_clause(c)
    for name, c in (('repo', repo), ('zen', zen)):
        for F in (536, 300, 150):
            assum = [inst.v(x, c[x - 1]) for x in range(1, F + 1)]
            tm = threading.Timer(60, s.interrupt); tm.start(); t = time.time()
            r = s.solve_limited(assumptions=assum, expect_interrupt=True); tm.cancel()
            rec = dict(N=N, src=name, F=F, pivot=537, status={True: 'SAT', False: 'UNSAT', None: 'TIMEOUT'}[r], seconds=round(time.time() - t, 2))
            if r: cols = inst.decode(s.get_model()); rec['own_violations'] = count_viol(cols, 7); json.dump({'colors': cols}, open(f'{H}/out/calib/incr_{name}_N{N}_F{F}.json', 'w'))
            if r is False:
                core = set(s.get_core() or []); pos = [x for x in range(1, F + 1) if inst.v(x, c[x - 1]) in core]; rec.update(core_max=max(pos) if pos else 0, core_size=len(pos))
            print(rec, flush=True); log.write(json.dumps(rec) + '\n')
    s.delete()
