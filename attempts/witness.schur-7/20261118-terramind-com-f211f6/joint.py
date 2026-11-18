"""Line (d): new 537-bases generated jointly with the target. The pivot-538 template at N with the WHOLE base free
(1..537 any of colours 0..5, 538 in colour 6, mirror), solver phases set to a known base so the search starts near
it; a SAT answer is a new 6-colour base together with its extension. Conflict budget per call.
Usage: joint.py <conflict-budget> <combo e.g. 1699full> <phase base ids...>"""
import json, sys, os, time, datetime
from pysat.solvers import Cadical195
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from lib538 import template, bhash
from check import count_viol
def utc(): return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-4] + 'Z'
B = int(sys.argv[1]); N, mode = int(sys.argv[2][:4]), sys.argv[2][4:]
bases = json.load(open(f'{H}/inputs/bases537.json'))
log = open(f'{H}/logs/joint.jsonl', 'a', buffering=1)
for b in sys.argv[3:]:
    inst = template(N, [0] * 537, 0, 538, mode); s = Cadical195()
    for c in inst.clauses(): s.add_clause(c)
    base = bases[b]
    s.set_phases([inst.v(x, base[x - 1]) for x in range(1, 538)])
    s.conf_budget(B); t = time.time(); r = s.solve_limited(); st = s.accum_stats() or {}
    rec = dict(line='d-joint', phase_base=b, bhash=bhash(base), N=N, mode=mode, F=0, status={True: 'SAT', False: 'UNSAT', None: 'LIMIT'}[r],
               seconds=round(time.time() - t, 2), conflicts=st.get('conflicts'), budget=B, time=utc())
    if r:
        cols = inst.decode(s.get_model()); fn = f'{H}/out/sat/d_joint_{b}_N{N}_{mode}.json'
        json.dump({'colors': cols}, open(fn, 'w')); rec.update(own_violations=count_viol(cols, 7), file=os.path.relpath(fn, H))
    log.write(json.dumps(rec) + '\n'); print(rec, flush=True); s.delete()
    if r is False: break  # base-free template refuted: phases cannot matter
