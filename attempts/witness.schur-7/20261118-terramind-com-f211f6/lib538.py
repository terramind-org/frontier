"""Pivot-538 (and pivot-537 seed) instance builders plus a logged two-worker job runner for schur7-538.
Uses schur.py (Instance, solve_bin: CaDiCaL 3.1.0 binary, status from return code 10/20/0)."""
import hashlib, json, os, sys, time, random
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schur import Instance, solve_bin, utc
from check import count_viol

HERE = os.path.dirname(os.path.abspath(__file__))

def bhash(cols):
    return hashlib.sha256(''.join(map(str, cols)).encode()).hexdigest()[:12]

def template(N, base, F, pivot, mirror, K=7, extra_fixed=None, forbid_top=None, free_window=None):
    """base: colours (0..5) of 1..len(base); integers 1..pivot-1 get colours 0..5 only, 1..F fixed to base,
    pivot gets colour 6. mirror: 'full' (c(x)=c(N+1-x) all x), 'partial' (only x in 1..pivot), 'none'."""
    fixed = {x: base[x - 1] for x in range(1, F + 1)}
    fixed[pivot] = 6
    if extra_fixed: fixed.update(extra_fixed)
    forbid = {x: {6} for x in range(1, pivot)}
    if forbid_top:
        for x, cs in forbid_top.items(): forbid.setdefault(x, set()).update(cs)
    mirrors = []
    if mirror == 'full':
        mirrors = [(x, N + 1 - x) for x in range(1, (N + 1) // 2 + 1) if x != N + 1 - x]
    elif mirror == 'partial':
        mirrors = [(x, N + 1 - x) for x in range(1, pivot + 1) if N + 1 - x > pivot]
    # mirror-implied forbids: colour 6 off the mirrored base
    if mirror in ('full', 'partial'):
        for x in range(1, pivot):
            forbid.setdefault(N + 1 - x, set()).add(6)
    return Instance(N, K, mirrors=mirrors, fixed=fixed, forbid=forbid)

def from_colouring(N, cols, fix_positions, mirror_S=None, mirror_xs=None, K=7):
    """Fix the given positions to cols, optional mirror c(x)=c(S-x) for x in mirror_xs."""
    fixed = {x: cols[x - 1] for x in fix_positions}
    mirrors = []
    if mirror_S:
        for x in (mirror_xs or range(1, N + 1)):
            y = mirror_S - x
            if 1 <= y <= N and x < y: mirrors.append((x, y))
    return Instance(N, K, mirrors=mirrors, fixed=fixed)

class Runner:
    def __init__(self, log, outdir, workers=2):
        self.log = open(log, 'a', buffering=1); self.outdir = outdir; self.workers = workers
        os.makedirs(outdir, exist_ok=True)
        self.n = 0
    def one(self, job):
        spec, build, timeout, seed = job['spec'], job['build'], job['timeout'], job.get('seed', 0)
        t0 = time.time(); start = utc()
        try:
            inst = build()
            r = solve_bin(inst, timeout, seed=seed, tag=spec['tag'].replace('/', '_'),
                          proof=job.get('proof'), keep_cnf=job.get('keep_cnf'))
        except Exception as e:
            r = dict(status='ERROR', rc=None, error=repr(e))
        rec = dict(spec, start=start, end=utc(), wall=round(time.time() - t0, 2), timeout=timeout,
                   **{k: v for k, v in r.items() if k != 'cols'})
        if r.get('status') == 'SAT':
            cols = r['cols']; v = count_viol(cols, 7)
            p = os.path.join(self.outdir, f"{spec['tag'].replace('/', '_')}_N{len(cols)}.json")
            json.dump({'colors': cols}, open(p, 'w'))
            rec.update(own_violations=v, file=os.path.relpath(p, HERE), N_out=len(cols))
        self.log.write(json.dumps(rec) + '\n')
        print(rec['end'], spec['tag'], rec.get('status'), rec.get('rc'), rec.get('seconds'), rec.get('conflicts'),
              rec.get('own_violations', ''), flush=True)
        return rec
    def run(self, jobs, deadline=None):
        out = []
        with ThreadPoolExecutor(self.workers) as ex:
            futs = []
            for j in jobs:
                futs.append(ex.submit(self._guard, j, deadline))
            for f in futs:
                r = f.result()
                if r: out.append(r)
        return out
    def _guard(self, job, deadline):
        if deadline and time.time() > deadline: return None
        return self.one(job)
