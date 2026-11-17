"""Long-call queue (core 2) for N >= 1699 after the push line's short calls came back UNSAT or TIMEOUT.
Each job: one CaDiCaL call with a long wall-clock limit on the least constrained structured instances, using the
base of the 1698 colouring (b1_0014). The first job is the matched calibration at N = 1698 (same structure, the
saved 1698 colouring satisfies it). Logs to logs/longq.jsonl. usage: longq.py DEADLINE SEED
"""
import json, os, random, sys, time
from schur import *
DEADLINE, SEED = float(sys.argv[1]), int(sys.argv[2]); rnd = random.Random(SEED)
LOG = open('logs/longq.jsonl', 'a')
def log(**kw):
    kw['utc'] = utc(); kw = {k: v for k, v in kw.items() if k != 'cols'}
    LOG.write(json.dumps(kw) + '\n'); LOG.flush(); print(json.dumps(kw), flush=True)
c1698 = load('best/N1698_b1_0014_sym.json'); base = c1698[:536]
def structural(N, F, m, W=40):
    fixed = {i + 1: base[i] for i in range(F)}
    forbid = {x: {6} for x in range(F + 1, m + 1)}
    skip = set(range((N + 1) // 3 - W, (N + 1) // 3 + W + 1)) if (N + 1) % 3 == 0 else set()
    mir = [(x, N + 1 - x) for x in range(1, (N + 1) // 2 + 1) if x != N + 1 - x and x not in skip and N + 1 - x not in skip]
    return Instance(N, 7, mirrors=mir, fixed=fixed, forbid=forbid)
jobs = [
    ('calib_sym1698_F150_m300', lambda: structural(1698, 150, 300), 600, 'SAT'),
    ('sym1699_F150_m300', lambda: structural(1699, 150, 300), 600, None),
    ('free1699_base536', lambda: Instance(1699, 7, fixed={i + 1: base[i] for i in range(536)}), 600, None),
    ('sym1699_F100_m300', lambda: structural(1699, 100, 300), 600, None),
    ('near1700_F150_m300', lambda: structural(1700, 150, 300), 600, None),
    ('sym1701_F150_m300', lambda: structural(1701, 150, 300), 600, None),
]
log(event='START', seed=SEED, jobs=[j[0] for j in jobs])
for name, mk, tl, expect in jobs:
    left = DEADLINE - time.time()
    if left < 60: break
    inst = mk()
    o = solve_bin(inst, min(tl, left - 10), seed=rnd.randrange(1 << 30), tag='longq')
    extra = {}
    if o['status'] == 'SAT':
        v = len(violations(o['cols'])); extra['violations'] = v
        save(f'push/longq_{name}.json', o['cols'])
        if v == 0 and len(o['cols']) > 1698: save(f'best/N{len(o["cols"])}_longq_{name}.json', o['cols'])
    log(event='JOB', job=name, N=inst.N, expect=expect, **o, **extra)
log(event='END')
