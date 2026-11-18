"""Line (a): pivot-538 sweep with one incremental CaDiCaL (PySAT Cadical195) per (N, mirror mode).
The template formula (7 colours, colour 6 off 1..537 and off the mirrored base, 538 in colour 6, mirror) is loaded
once; each (base, F) is solved under assumptions fixing 1..F to the base. On UNSAT the failed-assumption core gives
p = the largest fixed position the refutation used, so every F >= p is UNSAT too for that base, N and mode; the
descent then tries F = min(p - 1, F - step). Stops at SAT, conflict limit, or F < Fmin.
Usage: sweep.py <worker-index> <n-workers> <conflict-budget> <Fmin> [base ids...]
Status LIMIT = conflict budget exhausted (undecided)."""
import json, sys, os, time, threading, datetime, hashlib
from pysat.solvers import Cadical195
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from lib538 import template, bhash
from check import count_viol
def utc(): return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-4] + 'Z'
wi, nw, TO, FMIN = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])  # TO: conflict budget per call (PySAT's interrupt timer did not fire)
bases = json.load(open(os.environ.get('BASES', f'{H}/inputs/bases537.json')))  # dict id -> colours of 1..PIVOT-1
PIVOT = int(os.environ.get('PIVOT', '538')); LINE = os.environ.get('LINE', 'a'); TAG = os.environ.get('TAG', '')
ids = sys.argv[5:] or list(bases)
combos = [(N, 'full') for N in (1699, 1701, 1702)] + [(N, 'partial') for N in range(1699, 1705)]
if os.environ.get('COMBOS'):  # e.g. "1699full,1700partial": explicit order for this worker
    combos = [(int(c[:4]), c[4:]) for c in os.environ['COMBOS'].split(',')]
else:
    combos = combos[wi::nw]
log = open(f'{H}/logs/sweep{TAG}_w{wi}.jsonl', 'a', buffering=1)
os.makedirs(f'{H}/out/sat', exist_ok=True)
for N, mode in combos:
    dummy = [0] * (PIVOT - 1)  # bases may be shorter than PIVOT - 1 (then F starts at len(base))
    inst = template(N, dummy, 0, PIVOT, mode)
    s = Cadical195(); t0 = time.time(); ncl = 0
    for c in inst.clauses():
        s.add_clause(c); ncl += 1
    log.write(json.dumps(dict(event='formula', N=N, mode=mode, clauses=ncl, vars=inst.nvars,
                              build=round(time.time() - t0, 1), time=utc())) + '\n')
    for b in ids:
        base = bases[b]; F = min(PIVOT - 1, len(base), int(os.environ.get('FSTART', '100000'))); steps = 0
        while F >= FMIN:
            assum = [inst.v(x, base[x - 1]) for x in range(1, F + 1)]
            st0 = s.accum_stats() or {}
            s.conf_budget(TO); t1 = time.time()
            r = s.solve_limited(assumptions=assum)
            dt = time.time() - t1
            st1 = s.accum_stats() or {}
            rec = dict(line=LINE, pivot=PIVOT, base=b, bhash=bhash(base), N=N, mode=mode, F=F, time=utc(), seconds=round(dt, 3),
                       conflicts=st1.get('conflicts', 0) - st0.get('conflicts', 0),
                       status={True: 'SAT', False: 'UNSAT', None: 'LIMIT'}[r], conflict_budget=TO, clauses=ncl)
            if r is False:
                core = s.get_core() or []
                pos = [x for x in range(1, F + 1) if inst.v(x, base[x - 1]) in set(core)]
                p = max(pos) if pos else 0
                rec.update(core_size=len(pos), core_max=p, core_min=min(pos) if pos else 0)
                log.write(json.dumps(rec) + '\n')
                if p == 0:
                    rec2 = dict(rec, note='UNSAT without base assumptions: template itself infeasible'); log.write(json.dumps(rec2) + '\n'); break
                F = min(p - 1, F - 10)
            elif r is True:
                cols = inst.decode(s.get_model()); v = count_viol(cols, 7)
                fn = f'{H}/out/sat/{LINE}_{b}_p{PIVOT}_N{N}_{mode}_F{F}.json'; json.dump({'colors': cols}, open(fn, 'w'))
                rec.update(own_violations=v, file=os.path.relpath(fn, H)); log.write(json.dumps(rec) + '\n')
                print('SAT', rec, flush=True); break
            else:
                log.write(json.dumps(rec) + '\n'); break
    s.delete()
log.write(json.dumps(dict(event='done', time=utc())) + '\n')
