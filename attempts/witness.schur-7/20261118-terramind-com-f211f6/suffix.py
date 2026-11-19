"""Line (d'): new bases by freeing the LOW part. Almost every pivot-538 refutation in the sweep used base positions starting
at 1 (core_min = 1 in 1,214 of 1,244), so here the base is fixed only on S..537 (S in a list), 1..S-1 are free with colours 0..5,
538 in colour 6, mirror as given. One incremental PySAT CaDiCaL per (N, mode), conflict budget per call.
Usage: suffix.py <conflict-budget> <combos e.g. 1699full,1701full> <S list e.g. 141,200,300> [bases...]"""
import json, sys, os, time, datetime
from pysat.solvers import Cadical195
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from lib538 import template, bhash
from check import count_viol
def utc(): return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-4] + 'Z'
B = int(sys.argv[1]); combos = [(int(c[:4]), c[4:]) for c in sys.argv[2].split(',')]; Ss = [int(x) for x in sys.argv[3].split(',')]
bases = json.load(open(f'{H}/inputs/bases537.json')); ids = sys.argv[4:] or list(bases)
log = open(f'{H}/logs/suffix.jsonl', 'a', buffering=1)
for N, mode in combos:
    inst = template(N, [0] * 537, 0, 538, mode); s = Cadical195()
    for c in inst.clauses(): s.add_clause(c)
    for b in ids:
        base = bases[b]
        for S in Ss:
            assum = [inst.v(x, base[x - 1]) for x in range(S, 538)]
            st0 = s.accum_stats() or {}; s.conf_budget(B); t = time.time()
            r = s.solve_limited(assumptions=assum); st1 = s.accum_stats() or {}
            rec = dict(line='d-suffix', base=b, bhash=bhash(base), N=N, mode=mode, S=S, status={True: 'SAT', False: 'UNSAT', None: 'LIMIT'}[r],
                       seconds=round(time.time() - t, 2), conflicts=st1.get('conflicts', 0) - st0.get('conflicts', 0), budget=B, time=utc())
            if r is False:
                core = set(s.get_core() or []); pos = [x for x in range(S, 538) if inst.v(x, base[x - 1]) in core]
                rec.update(core_size=len(pos), core_min=min(pos) if pos else 0, core_max=max(pos) if pos else 0)
            if r:
                cols = inst.decode(s.get_model()); fn = f'{H}/out/sat/d_{b}_S{S}_N{N}_{mode}.json'
                json.dump({'colors': cols}, open(fn, 'w')); rec.update(own_violations=count_viol(cols, 7), file=os.path.relpath(fn, H))
            log.write(json.dumps(rec) + '\n'); print(rec, flush=True)
            if r is not False: break   # LIMIT or SAT: larger S (fewer fixed) would not be more informative this round
log.write(json.dumps(dict(event='done', time=utc())) + '\n')
