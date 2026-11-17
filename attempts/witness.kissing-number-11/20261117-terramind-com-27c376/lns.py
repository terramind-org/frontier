"""Free-backbone large-neighbourhood search and blocker-set exchanges over the exact G-orbit pool.
Current configuration X = (604 minus a set Gone of baseline indices) + E (extra pool vectors). A neighbourhood is a
set R of members of X; every pool vector compatible with X minus R is computed exactly by the freeset server, the
conflict graph among them is built exactly and a maximum independent set is solved with CP-SAT. Success needs an
independent set larger than |R|. Equal-size different sets are accepted as moves (solution exclusion)."""
import sys, os, json, time, subprocess, hashlib, random, argparse
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from common import load, save, exact_valid, conflicts_matrix, as_float
import mis

def clique(cand, lb, mode=0, excl=(), seed=0, tl=60.0):
    """exact max clique of the compatibility graph via ./mclq. Returns (status, size, chosen, nodes, compat_edges, secs)."""
    t0 = time.time()
    inp = [f'{len(cand)} {lb} {mode} {seed} {tl}'] + [' '.join(map(str, v)) for v in cand]
    if mode == 1:
        inp.append(f'{len(excl)} ' + ' '.join(map(str, sorted(excl))))
    r = subprocess.run(['./mclq'], input='\n'.join(inp) + '\n', capture_output=True, text=True)
    if r.returncode != 0:
        return f'ERROR rc={r.returncode}', None, [], 0, 0, time.time() - t0
    head, body = r.stdout.split('\n', 1)
    t = head.split()
    chosen = [int(x) for x in body.split()]
    return t[1], int(t[3]), chosen, int(t[5]), int(t[7]), time.time() - t0

V604 = load('baseline.json')
FREECAP = 30000
IDX = {v: i for i, v in enumerate(V604)}

def utc():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

class FreeSet:
    def __init__(self, reps):
        self.p = subprocess.Popen(['./freeset', reps, 'group.txt', 'act604.txt'], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, text=True, bufsize=1 << 20)
        line = self.p.stdout.readline()
        assert line.startswith('READY'), line
    def query(self, Rp, E):
        q = [f'Q {len(Rp)} ' + ' '.join(map(str, sorted(Rp))) + f' {len(E)}']
        q += [' '.join(map(str, v)) for v in E]
        self.p.stdin.write('\n'.join(q) + '\n'); self.p.stdin.flush()
        n = int(self.p.stdout.readline().split()[1])
        out = set()
        for _ in range(n):
            out.add(tuple(int(t) for t in self.p.stdout.readline().split()))
        assert self.p.stdout.readline().strip() == 'END'
        return sorted(out)
    def close(self):
        self.p.stdin.write('X\n'); self.p.stdin.flush(); self.p.wait()

def edges_exact(cand):
    n = len(cand); edges = []
    B = max(64, int(1.5e7 // max(n, 1)))  # rows per block: keeps each int64 temporary under ~120 MB
    for i0 in range(0, n, B):
        C = conflicts_matrix(cand[i0:i0 + B], cand)
        ii, jj = np.nonzero(C)
        for i, j in zip(ii + i0, jj):
            if i < j: edges.append((int(i), int(j)))
    return edges

class Search:
    def __init__(self, fs, log, outdir, gone=(), extra=()):
        self.fs = fs; self.log = log; self.outdir = outdir
        self.gone = set(gone); self.E = list(extra)
        self.visited = set(); self.best = None
        self.record_state()
    def X(self):
        return [v for i, v in enumerate(V604) if i not in self.gone] + self.E
    def key(self):
        return hashlib.sha1(json.dumps(sorted(self.X())).encode()).hexdigest()
    def record_state(self):
        X = self.X()
        k = self.key()
        new = k not in self.visited
        self.visited.add(k)
        if self.best is None or len(X) > self.best:
            ok, why = exact_valid(X)
            assert ok, why
            self.best = len(X)
            save(os.path.join(self.outdir, f'best-{len(X)}.json'), X, f'exact configuration of {len(X)} vectors (lns.py)')
            self.p(f'BEST {len(X)} saved best-{len(X)}.json')
        return new
    def p(self, s):
        print(f'{utc()} {s}', file=self.log, flush=True)
    def solve_nbhd(self, Rset, label, tl=60.0, move=True, seed=0):
        """Rset: list of vectors of X to free."""
        Rp = set(self.gone)
        Ekeep = []
        Rs = set(Rset)
        for v in Rset:
            if v in IDX: Rp.add(IDX[v])
        for v in self.E:
            if v not in Rs: Ekeep.append(v)
        t0 = time.time()
        cand = self.fs.query(Rp, Ekeep)
        tq = time.time() - t0
        m = len(Rset)
        cur = {i for i, v in enumerate(cand) if v in Rs}
        assert len(cur) == m, (len(cur), m)
        if len(cand) > FREECAP:
            # the bitset graph needs n^2/8 bytes: above FREECAP (about 112 MB) the solve is skipped, never attempted
            self.p(f'NBHD {label} m={m} free={len(cand)} query={tq:.1f}s status=SKIPPED_TOO_LARGE')
            return {'label': label, 'm': m, 'free': len(cand), 'status': 'SKIPPED_TOO_LARGE', 'value': None, 'query_s': round(tq, 2)}
        st, val, ch, nodes, ne, ts = clique(cand, m, 0, seed=seed, tl=tl)
        self.p(f'NBHD {label} m={m} free={len(cand)} compat_edges={ne} query={tq:.1f}s status={st} max_found={val} nodes={nodes} solve={ts:.1f}s')
        res = {'label': label, 'm': m, 'free': len(cand), 'status': st, 'value': val, 'query_s': round(tq, 2), 'solve_s': round(ts, 2), 'nodes': nodes}
        if val is not None and val > m and len(ch) == val:
            self.apply(Rset, [cand[i] for i in ch])
            self.p(f'IMPROVED to {len(self.X())}')
            res['improved'] = True
            return res
        if move and st == 'OPTIMAL' and len(cand) > m:
            st2, val2, ch2, nodes2, _, ts2 = clique(cand, m, 1, excl=cur, seed=seed, tl=tl)
            res['move_status'] = st2; res['move_value'] = val2 if ch2 else None
            if ch2 and len(ch2) >= m:
                self.apply(Rset, [cand[i] for i in ch2])
                self.p(f'MOVE {label} status={st2} size={len(ch2)} distinct_states={len(self.visited)} E={len(self.E)} gone={len(self.gone)} solve={ts2:.1f}s')
                res['moved'] = True
            else:
                self.p(f'NOMOVE {label} status={st2} (no other {m}-set) solve={ts2:.1f}s')
        return res
    def record_state_after(self):
        return self.record_state()
    def apply(self, Rset, newvecs):
        Rs = set(Rset)
        for v in Rset:
            if v in IDX: self.gone.add(IDX[v])
        self.E = [v for v in self.E if v not in Rs]
        for v in newvecs:
            if v in IDX: self.gone.discard(IDX[v])
            else: self.E.append(v)
        X = self.X()
        ok, why = exact_valid(X)
        assert ok, why
        self.record_state()

def cap(X, center, m):
    F = as_float(X)
    c = np.asarray(center, float); c = c / np.linalg.norm(c)
    cs = F @ c / 6.0
    order = np.argsort(-cs)
    return [X[i] for i in order[:m]]
