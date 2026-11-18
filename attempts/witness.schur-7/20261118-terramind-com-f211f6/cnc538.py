"""Line (c): cube-and-conquer on undecided (base, F, N, mode) instances with one incremental PySAT CaDiCaL per
instance. After assuming 1..F from the base, unit propagation gives the allowed colours of the free base positions
F+1..PIVOT-1; the d positions with fewest allowed colours (ties: smallest x) are split into every combination of
their allowed colours (at most MAXC cubes, in a seeded shuffle order). Each cube gets a conflict budget.
Usage: cnc538.py <spec-json> ; spec: {"tag","base_file","base","pivot","F","N","mode","d","maxc","budget","seed"[,"known"]}"""
import json, sys, os, time, itertools, random, hashlib
from pysat.solvers import Cadical195
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from lib538 import template, bhash
from check import count_viol
from schur import utc
sp = json.loads(sys.argv[1])
base = json.load(open(f"{H}/{sp['base_file']}"))[sp['base']]
P, F, N, mode = sp['pivot'], sp['F'], sp['N'], sp['mode']
inst = template(N, [0] * (P - 1), 0, P, mode)
s = Cadical195()
for c in inst.clauses(): s.add_clause(c)
pre = [inst.v(x, base[x - 1]) for x in range(1, F + 1)]
ok, implied = s.propagate(assumptions=pre)
log = open(f"{H}/logs/cnc.jsonl", 'a', buffering=1)
head = dict(tag=sp['tag'], line='c', base=sp['base'], bhash=bhash(base), pivot=P, F=F, N=N, mode=mode, budget=sp['budget'], time=utc())
if not ok:
    log.write(json.dumps(dict(head, event='prefix-propagation-conflict')) + '\n'); sys.exit(0)
imp = set(implied)
allowed = {}
for x in range(F + 1, P):
    al = [c for c in range(6) if -inst.v(x, c) not in imp]
    if not any(inst.v(x, c) in imp for c in range(6)): allowed[x] = al
cand = sorted(allowed, key=lambda x: (len(allowed[x]), x))[: sp['d']]
cubes = list(itertools.product(*[allowed[x] for x in cand]))
random.Random(sp['seed']).shuffle(cubes)
cubes = cubes[: sp['maxc']]
if sp.get('known'):  # calibration: put the cube that agrees with a known solution first
    kc = json.load(open(f"{H}/{sp['known']}"))['colors']; kcube = tuple(kc[x - 1] for x in cand)
    cubes = [kcube] + [c for c in cubes if c != kcube][: sp['maxc'] - 1]
log.write(json.dumps(dict(head, event='split', positions=cand, allowed=[allowed[x] for x in cand], total_cubes=len(list(itertools.product(*[allowed[x] for x in cand]))), run_cubes=len(cubes))) + '\n')
for i, cube in enumerate(cubes):
    assum = pre + [inst.v(x, c) for x, c in zip(cand, cube)]
    st0 = s.accum_stats() or {}; s.conf_budget(sp['budget']); t = time.time()
    r = s.solve_limited(assumptions=assum)
    st1 = s.accum_stats() or {}
    rec = dict(head, event='cube', i=i, cube=list(cube), status={True: 'SAT', False: 'UNSAT', None: 'LIMIT'}[r],
               seconds=round(time.time() - t, 2), conflicts=st1.get('conflicts', 0) - st0.get('conflicts', 0), time=utc())
    if r:
        cols = inst.decode(s.get_model()); fn = f"{H}/out/sat/c_{sp['tag']}_N{N}.json"
        json.dump({'colors': cols}, open(fn, 'w')); rec.update(own_violations=count_viol(cols, 7), file=os.path.relpath(fn, H))
    log.write(json.dumps(rec) + '\n'); print(rec, flush=True)
    if r: break
